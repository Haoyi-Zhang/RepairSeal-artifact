"""Compare exact-point signed-C repair decisions using an external archive.

The normalized corpus is produced by codeflaws_staged_study.py. This driver
independently rechecks its raw source/test hashes, reconstructs a signed circuit,
and compares concrete AST observations, full vector checking, a demand direct
decision, and direct production of the identical complete record. Only R=true
is used here: the upstream reference supplies the expected behavior everywhere.
No upstream source or complete vector packet is redistributed by this driver.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import platform
import sys
import tarfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]
import proof_dag_checker as core
import codeflaws_int32_bridge as bridge
import int32_circuit as symbolic
from scientific_driver import new_output_directory, require_assertions

SOURCES = [ROOT / p for p in (
    "src/proof_dag_checker.py", "src/demand_evaluator.py", "src/int32_circuit.py",
    "src/codeflaws_int32_bridge.py", "tests/scientific_driver.py",
    "tests/int32_contract_study.py")]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def same(a, b, context):
    if not core.exact_equal(a, b):
        raise AssertionError((context, a, b))


def decision(result):
    return {key: result[key] for key in ("status", "witness")}


def bindings():
    return {p.relative_to(ROOT).as_posix(): file_hash(p) for p in SOURCES}


def load_inputs(corpus_path, archive_path):
    raw_corpus = corpus_path.read_bytes()
    corpus = core.load_json_strict(raw_corpus.decode("utf-8"))
    same(corpus["schema"], "repairseal-codeflaws-int32-corpus-v1", "corpus schema")
    same(corpus["profile_id"], bridge.PROFILE_ID, "corpus profile")
    same(file_hash(archive_path), corpus["archive_sha256"], "whole archive hash")
    raw_sources, admitted = {}, {}
    needed, payloads = {}, {}

    def need(name, expected, limit):
        if name in needed:
            same(needed[name], (expected, limit), "consistent archive descriptor")
        needed[name] = (expected, limit)

    for source_hash, row in corpus["sources"].items():
        need(row["member"], source_hash, bridge.MAX_SOURCE_BYTES)
    for subject in corpus["subjects"]:
        for test in subject["tests"]:
            need(test["input_member"], test["input_sha256"], 4096)
            need(test["output_member"], test["output_sha256"], 1024)
    # A streaming pass avoids repeatedly decompressing the same gzip prefix.
    # No archive path is extracted onto the filesystem.
    with tarfile.open(archive_path, "r|gz") as archive:
        for member in archive:
            if member.name not in needed:
                continue
            expected, limit = needed[member.name]
            if member.name in payloads or not member.isfile() or not 0 <= member.size <= limit:
                raise ValueError(("duplicate, nonregular or oversized member", member.name))
            stream = archive.extractfile(member)
            if stream is None:
                raise ValueError(("missing archive member", member.name))
            raw = stream.read(limit + 1)
            same(digest(raw), expected, (member.name, "member hash"))
            payloads[member.name] = raw
    same(sorted(payloads), sorted(needed), "complete selected archive members")
    for source_hash, row in corpus["sources"].items():
        raw = payloads[row["member"]]
        program = bridge.admit_source(raw, filename=row["member"])
        same(program.source_sha256, source_hash, "admitted hash")
        same(program.input_arity, row["input_arity"], "input arity")
        same(program.output_kind, row["output_kind"], "output codec")
        raw_sources[source_hash] = raw
        admitted[source_hash] = program
    for subject in corpus["subjects"]:
        for test in subject["tests"]:
            raw = payloads[test["input_member"]]
            same(list(bridge.parse_input(raw, subject["input_arity"])), test["input"], "input vector")
            out = payloads[test["output_member"]]
            same(bridge.canonical_output(out, subject["output_kind"]), test["expected"], "oracle token")
    return corpus, raw_sources, admitted, digest(raw_corpus)


def populations(corpus):
    eligible = [row for row in corpus["subjects"] if row["eligible"]]
    candidates = defaultdict(set)
    needed = defaultdict(set)
    for subject in corpus["subjects"]:
        points = {tuple(row["input"]) for row in subject["tests"]}
        for role in ("original_sha", "reference_sha"):
            needed[subject[role]].update(points)
        if subject["eligible"]:
            candidates[subject["problem"]].update((subject["original_sha"], subject["reference_sha"]))
    cases = []
    for subject in eligible:
        expected = {}
        for test in subject["tests"]:
            point = tuple(test["input"])
            if point in expected:
                same(expected[point], test["expected"], "consistent test oracle")
            expected[point] = test["expected"]
        for source_hash in sorted(candidates[subject["problem"]]):
            metadata = corpus["sources"][source_hash]
            if metadata["input_arity"] != subject["input_arity"] or metadata["output_kind"] != subject["output_kind"]:
                continue
            needed[source_hash].update(expected)
            cases.append((subject, source_hash))
    return eligible, cases, needed


def observations(admitted, needed, output):
    rows, indexed = [], {}
    for source_hash, points_set in sorted(needed.items()):
        program = admitted[source_hash]
        circuit = core.Circuit()
        labels = {value: i for i, value in enumerate(program.output_labels)}
        compiled = symbolic.SignedCompiler(circuit, program, labels).compile()
        points = sorted(points_set)
        vectors = symbolic._vectors(circuit, program.input_names, points)
        for i, point in enumerate(points):
            actual = bridge.evaluate(program, point)
            defined = vectors[compiled.defined][i]
            value = symbolic.decode(vectors[compiled.output][i], program.output_kind, labels) if defined else None
            trace = [[site, int(bool(vectors[guard][i]))] for site, reachable, guard in compiled.events
                     if vectors[reachable][i]]
            got = {"defined": defined, "value": value, "trace": trace}
            wanted = {"defined": actual.defined, "value": actual.value, "trace": [list(x) for x in actual.trace]}
            same(got, wanted, (source_hash, point, "independent observation"))
            row = {"source_sha256": source_hash, "input": list(point), **got,
                   "undefined_reason": actual.undefined_reason, "interpreter_steps": actual.steps,
                   "dag_nodes": len(circuit.nodes)}
            indexed[source_hash, point] = row
            rows.append(row)
    save(output / "source-observations.json", rows)
    return indexed, rows


def concrete_decision(subject, candidate_hash, points, observed):
    candidate = [observed[candidate_hash, tuple(point)] for point in points]
    reference = [observed[subject["reference_sha"], tuple(point)] for point in points]
    for obligation in ("defined", "repair"):
        failures = []
        for point, q, ref in zip(points, candidate, reference):
            if ((not q["defined"]) if obligation == "defined"
                else (not q["defined"] or not ref["defined"] or q["value"] != ref["value"])):
                failures.append((q["trace"], point))
        if failures:
            trace, point = min(failures)
            return {"status": "REFUTED", "witness": {"obligation": obligation, "trace": trace, "input": point}}
    return {"status": "ACCEPT", "witness": None}


def audit_upstream_oracles(corpus, observed, output):
    """Recheck declared eligibility and reference observations without selection.

    Oracle agreement is a reported property, not a filter. A mismatch aborts
    the current study instead of removing an inconvenient subject or point.
    """
    rows = []
    for subject in corpus["subjects"]:
        per_role = {}
        for role in ("original", "reference"):
            counts = Counter()
            for test in subject["tests"]:
                result = observed[subject[role+"_sha"], tuple(test["input"])]
                counts["undefined" if not result["defined"] else
                       "match" if result["value"] == test["expected"] else "mismatch"] += 1
            per_role[role] = dict(counts)
        all_defined = all(not result.get("undefined", 0) for result in per_role.values())
        same(subject["eligible"], all_defined, (subject["id"], "definedness eligibility"))
        if subject["eligible"]:
            same(per_role["reference"].get("match", 0), len(subject["tests"]),
                 (subject["id"], "upstream reference versus raw oracle"))
        rows.append({"subject": subject["id"], "eligible": subject["eligible"],
                     "test_occurrences": len(subject["tests"]), **per_role})
    save(output / "oracle-audit.json", rows)
    return rows


def run(corpus_path, archive_path, output):
    before = bindings()
    corpus, raw_sources, admitted, corpus_sha = load_inputs(corpus_path, archive_path)
    eligible, cases, needed = populations(corpus)
    observed, observation_rows = observations(admitted, needed, output)
    oracle_audit = audit_upstream_oracles(corpus, observed, output)
    requests, stages = [], []
    work = {stage: Counter() for stage in ("repair", "union")}
    for sequence, (subject, candidate_hash) in enumerate(cases):
        source_hashes = {"original": subject["original_sha"], "candidate": candidate_hash,
                         "reference": subject["reference_sha"]}
        stage_results = {}
        for stage in ("repair", "union"):
            points = sorted({tuple(test["input"]) for test in subject["tests"]
                             if stage == "union" or test["split"] == "repair"})
            points = [list(point) for point in points]
            task = {"kind": symbolic.PROFILE, "id": f"{subject['id']}-{candidate_hash[:12]}-{stage}",
                    "policy": "reference-everywhere", "points": points,
                    "sources": {role: raw_sources[sha].decode("utf-8") for role, sha in source_hashes.items()}}
            expected = concrete_decision(subject, candidate_hash, points, observed)
            start = time.perf_counter(); packet = symbolic.make_evidence(task)
            produced = time.perf_counter(); encoded = symbolic._canonical(packet)
            decoded = core.load_json_strict(encoded.decode("utf-8")); decoded_at = time.perf_counter()
            full = symbolic.verify_evidence(task, decoded); checked_at = time.perf_counter()
            direct = symbolic.evaluate_direct(task); direct_at = time.perf_counter()
            recorded, direct_record = symbolic.evaluate_with_record(task); recorded_at = time.perf_counter()
            for name, result in (("full", full), ("demand", direct), ("direct-record", recorded)):
                same(decision(result), expected, (task["id"], name))
            same(packet, direct_record, (task["id"], "identical complete record"))
            same(full["semantic_cells"], recorded["semantic_cells"], "materialization work")
            if direct["semantic_cells"] > full["semantic_cells"]:
                raise AssertionError("demand computes more distinct values than full")
            totals = work[stage]
            totals.update(requests=1, points=len(points), full_cells=full["semantic_cells"],
                          demand_cells=direct["semantic_cells"], direct_record_cells=recorded["semantic_cells"],
                          packet_bytes=len(encoded), **{expected["status"]: 1})
            row = {"id": task["id"], "subject": subject["id"], "problem": subject["problem"],
                   "stage": stage, "sources": source_hashes, "points": points,
                   "task_sha256": symbolic.task_identity(task), "packet_sha256": packet["sha256"],
                   "packet_bytes": len(encoded), **expected, "full": full, "demand": direct,
                   "direct_record": recorded,
                   "timing_ms": {"packet_production": (produced-start)*1000,
                                 "encode_decode": (decoded_at-produced)*1000,
                                 "full_receiving": (checked_at-decoded_at)*1000,
                                 "demand_receiving": (direct_at-checked_at)*1000,
                                 "direct_record_receiving": (recorded_at-direct_at)*1000}}
            requests.append(row); stage_results[stage] = row
        first, second = stage_results["repair"], stage_results["union"]
        stages.append({"subject": subject["id"], "problem": subject["problem"],
                       "candidate_sha256": candidate_hash, "repair": first["status"],
                       "union": second["status"], "union_witness": second["witness"],
                       "repair_points": len(first["points"]), "union_points": len(second["points"])})
        if (sequence+1) % 100 == 0:
            print(json.dumps({"completed_candidate_subjects": sequence+1, "total": len(cases)}), flush=True)
    save(output / "requests.json", requests); save(output / "stages.json", stages)
    same(bindings(), before, "executed sources unchanged")
    same(file_hash(corpus_path), corpus_sha, "normalized corpus unchanged")
    changed = [row for row in stages if row["repair"] == "ACCEPT" and row["union"] == "REFUTED"]
    summary = {"schema": "repairseal-int32-contract-study-v1", "outcome": "PASS",
               "profile": symbolic.PROFILE, "policy": "reference-everywhere",
               "source_bindings": before, "corpus_sha256": corpus_sha,
               "archive_sha256": corpus["archive_sha256"], "eligible_subjects": len(eligible),
               "eligible_problems": len({row["problem"] for row in eligible}),
               "candidate_subject_combinations": len(cases), "requests": len(requests),
               "source_input_observations": len(observation_rows),
               "undefined_source_input_observations": sum(not row["defined"] for row in observation_rows),
               "work": {stage: dict(counts) for stage, counts in work.items()},
               "repair_accept_union_refute": len(changed),
               "changed_subjects": len({row["subject"] for row in changed}),
               "changed_problems": len({row["problem"] for row in changed}),
               "identical_full_and_direct_records": len(requests),
               "eligible_references_match_raw_oracles": sum(row["eligible"] and not row["reference"].get("mismatch", 0)
                                                              and not row["reference"].get("undefined", 0) for row in oracle_audit),
               "eligible_originals_with_oracle_mismatch": sum(row["eligible"] and bool(row["original"].get("mismatch", 0)) for row in oracle_audit),
               "environment": {"python": sys.version, "platform": platform.platform(),
                               "pycparser": __import__("pycparser").__version__},
               "timing_scope": "one ordered observation per arm; no speedup estimate; includes fresh admission/reconstruction, excludes archive and oracle preparation",
               "records": {name: file_hash(output/name) for name in ("requests.json", "stages.json", "source-observations.json", "oracle-audit.json")}}
    save(output / "summary.json", summary)
    return summary


def main():
    require_assertions()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = new_output_directory(args.output)
    try:
        result = run(args.corpus.resolve(), args.archive.resolve(), output)
    except BaseException as exc:
        save(output/"summary.json", {"outcome": "FAILED", "error_type": type(exc).__name__, "error": str(exc)})
        raise
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

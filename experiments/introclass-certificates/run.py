"""Certificates and native translation validation for released test-passing patches.

The cases are an explicitly exploratory selection from the separate published-
patch campaign. Their population frequency must come from that campaign, not
from this mechanism-focused subset. Every raw and normalized source is compiled
and run under both GCC and Clang on every declared input.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PATCHES = ROOT / "experiments/real-patches"
sys.path[:0] = [str(HERE), str(ROOT / "src"), str(ROOT / "tests")]
import normalize as adapter
import codeflaws_int32_bridge as bridge
import int32_circuit as symbolic
import int32_refutation as compact
import proof_dag_checker as core

_spec = importlib.util.spec_from_file_location("repairseal_intro_native_runner", ROOT / "experiments/natural-expansion/run.py")
native_helper = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(native_helper)

SELECTED = ("apr-043", "apr-046", "apr-069", "apr-070", "apr-072", "apr-073")
BOUND = ("experiments/introclass-certificates/normalize.py", "experiments/introclass-certificates/run.py",
         "experiments/natural-expansion/run.py", "experiments/natural-expansion/domains.py",
         "tests/codeflaws_staged_study.py", "src/int32_circuit.py", "src/int32_refutation.py",
         "src/codeflaws_int32_bridge.py", "src/proof_dag_checker.py", "src/demand_evaluator.py",
         "experiments/real-patches/corpus.json", "experiments/real-patches/points.json",
         "experiments/real-patches/given-tests.json")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def file_hash(path):
    return native_helper.file_hash(path)


def save(path, value):
    native_helper.save(path, value)


def read_lines(path):
    return native_helper.read_lines(path)


def declaration():
    corpus = json.loads((PATCHES / "corpus.json").read_text())
    indexed = {c["case_id"]: c for c in corpus}
    cases = [indexed[key] for key in SELECTED]
    points = json.loads((PATCHES / "points.json").read_text())
    tests = json.loads((PATCHES / "given-tests.json").read_text())
    families = sorted({c["family"] for c in cases})
    return {"schema": "repairseal-introclass-certificate-protocol-v1",
            "selection": "Exploratory six-patch subset identified after the separate fixed-sample study found test-passing incorrect behavior and fully initialized scalar control flow. Selection is outcome-directed; no prevalence estimate uses these six cases.",
            "selected_case_ids": list(SELECTED), "cases": cases,
            "points": {family: sorted([p["values"] for p in points if p["family"] == family]) for family in families},
            "given_tests": {family: [t for t in tests if t["family"] == family] for family in families},
            "policy": "reference-everywhere", "profile": symbolic.PROFILE,
            "source_bindings": {name: file_hash(ROOT / name) for name in BOUND},
            "normalization": "Exact identity macro expansion; atoi(argv[k]) replaced in order by scanf of the same int variable; identity int casts removed; fixed teacher prompt/suffix reduced to its numeric observation. Original computation, if structure, declaration types and assignment order retained.",
            "native_validation": "Original raw bytes and normalized bytes separately compiled and executed with GCC and Clang on every declared point; original teacher output matched against its complete fixed prompt/suffix codec; all original candidate outputs on given tests matched byte-for-byte.",
            "independent_math_oracle": "median: sorted triple middle element; smallest: minimum of the quadruple. Used only to validate the supplied teacher reference on the finite domain.",
            "limits": "No global equivalence proof, no human-rater agreement, no signed preservation-root claim, no inference that a supplied certificate searches for a witness."}


def mathematical(family, point):
    return str(sorted(point)[1] if family == "median" else min(point))


def prepare(protocol, output):
    source_specs = {}
    for case in protocol["cases"]:
        for role in ("original", "candidate", "reference"):
            sha = case[role + "_sha256"]
            spec = {"raw_sha256": sha, "family": case["family"], "reference": role == "reference"}
            if sha in source_specs and source_specs[sha] != spec:
                raise ValueError("inconsistent source role")
            source_specs[sha] = spec
    mappings = {}; observed = {}; observations = []
    for sha, spec in sorted(source_specs.items()):
        raw = (PATCHES / "sources" / (sha + ".c")).read_bytes()
        if digest(raw) != sha:
            raise ValueError("published source identity")
        normalized, mapping = adapter.normalize(raw, spec["family"], spec["reference"])
        mapping["reference"] = spec["reference"]
        mapping["normalized_path"] = "normalized/" + sha + ".c"
        target = output / mapping["normalized_path"]
        target.parent.mkdir(parents=True, exist_ok=True); target.write_text(normalized)
        mappings[sha] = mapping
        admitted = bridge.admit_source(normalized.encode())
        circuit = core.Circuit(); compiled = symbolic.SignedCompiler(circuit, admitted, {}).compile()
        points = protocol["points"][spec["family"]]
        vectors = symbolic._vectors(circuit, admitted.input_names, points)
        for ordinal, point in enumerate(points):
            concrete = bridge.evaluate(admitted, point)
            defined = vectors[compiled.defined][ordinal]
            calculated = {"defined": defined,
                          "value": symbolic.decode(vectors[compiled.output][ordinal], "numeric", {}) if defined else None,
                          "trace": [[site, int(bool(vectors[guard][ordinal]))] for site, reach, guard in compiled.events if vectors[reach][ordinal]]}
            expected = {"defined": concrete.defined, "value": concrete.value, "trace": [list(t) for t in concrete.trace]}
            if not concrete.defined or not core.exact_equal(calculated, expected):
                raise ValueError((sha, point, "defined concrete/symbolic agreement"))
            if spec["reference"] and concrete.value != mathematical(spec["family"], point):
                raise ValueError("supplied teacher reference differs from mathematical oracle")
            row = {"raw_source_sha256": sha, "normalized_source_sha256": mapping["normalized_sha256"],
                   "family": spec["family"], "input": point, **expected, "symbolic": calculated,
                   "reference_math_agreement": True if spec["reference"] else None}
            observations.append(row); observed[sha, tuple(point)] = row
    save(output / "mappings.json", mappings)
    native_helper.save_lines(output / "semantic-observations.jsonl", observations)
    requests = []
    for case in protocol["cases"]:
        task = {"kind": symbolic.PROFILE, "id": "introclass-" + case["case_id"],
                "policy": "reference-everywhere", "points": protocol["points"][case["family"]],
                "sources": {role: (output / mappings[case[role + "_sha256"]]["normalized_path"]).read_text()
                            for role in ("original", "candidate", "reference")}}
        bad = [(observed[case["candidate_sha256"], tuple(p)]["trace"], p) for p in task["points"]
               if observed[case["candidate_sha256"], tuple(p)]["value"] != observed[case["reference_sha256"], tuple(p)]["value"]]
        if not bad:
            raise ValueError("selected repair has no semantic counterexample")
        trace, point = min(bad)
        expected = {"status": "REFUTED", "witness": {"obligation": "repair", "trace": trace, "input": point}}
        packet = symbolic.make_evidence(task)
        full = symbolic.verify_evidence(task, packet); direct = symbolic.evaluate_direct(task)
        record_result, record_packet = symbolic.evaluate_with_record(task)
        if not core.exact_equal(packet, record_packet):
            raise ValueError("complete record difference")
        certificate = compact.produce(task, expected["witness"]); confirmation = compact.check(task, certificate)
        for arm in (full, direct, record_result, confirmation):
            if {k: arm[k] for k in ("status", "witness")} != expected:
                raise ValueError("receiver disagreement")
        base = "cases/" + case["case_id"]
        save(output / base / "request.json", task); save(output / base / "full.json", packet)
        save(output / base / "compact.json", certificate)
        requests.append({"case_id": case["case_id"], "family": case["family"], "subject": case["subject"],
                         "candidate_sha256": case["candidate_sha256"], "task_sha256": symbolic.task_identity(task),
                         "domain_points": len(task["points"]), "mismatch_points": len(bad), **expected,
                         "full": full, "direct": direct, "direct_record": record_result, "compact": confirmation,
                         "request_path": base + "/request.json", "full_path": base + "/full.json", "compact_path": base + "/compact.json",
                         "candidate_at_witness": observed[case["candidate_sha256"], tuple(point)]["value"],
                         "reference_at_witness": observed[case["reference_sha256"], tuple(point)]["value"],
                         "original_at_witness": observed[case["original_sha256"], tuple(point)]["value"]})
    save(output / "requests.json", requests)
    return mappings, observed


def native_validation(protocol, mappings, observed, output, work, compilers):
    if work.exists() or ROOT == work or ROOT in work.parents:
        raise ValueError("native work must be a new external directory")
    work.mkdir(parents=True)
    identities = []; compile_records = []; native_records = []; seen = set()
    for path in compilers:
        path = path.resolve()
        directory = work / str(len(seen)); directory.mkdir()
        version_record, version_raw, _ = native_helper.bounded_process([str(path), "--version"], b"", directory, compiling=True)
        version = version_raw.decode("ascii")
        compiler = "clang" if "clang" in version.lower() else "gcc" if "gcc" in version.lower() else None
        if version_record["outcome"] != "ok" or compiler is None or compiler in seen:
            raise ValueError("require two compiler families")
        seen.add(compiler)
        flags = ["-std=c99", "-O1", "-include", "stdlib.h", "-Werror=implicit-function-declaration", "-Werror=format"]
        identities.append({"family": compiler, "path": str(path), "sha256": file_hash(path), "version": version,
                           "flags": flags, "forced_header_reason": "Released instrumented median sources call atoi without stdlib.h; its real declaration is supplied by a recorded compiler flag without changing their bytes."})
        with (output / ("native-" + compiler + ".jsonl")).open("w") as stream:
            for source_index, (sha, mapping) in enumerate(sorted(mappings.items()), 1):
                binaries = {}
                for variant in ("original", "normalized"):
                    raw = ((PATCHES / "sources" / (sha + ".c")).read_bytes() if variant == "original"
                           else (output / mapping["normalized_path"]).read_bytes())
                    expected_hash = sha if variant == "original" else mapping["normalized_sha256"]
                    if digest(raw) != expected_hash:
                        raise ValueError("compiled source hash mismatch")
                    source_path = directory / (sha + "-" + variant + ".c"); source_path.write_bytes(raw)
                    binary = directory / (sha + "-" + variant)
                    receipt, _stdout, _stderr = native_helper.bounded_process([str(path), *flags, str(source_path), "-o", str(binary)], b"", directory, compiling=True)
                    if receipt["outcome"] != "ok":
                        raise ValueError((compiler, sha, variant, receipt["stderr"]))
                    compile_records.append({"compiler": compiler, "raw_source_sha256": sha, "variant": variant,
                                            "compiled_source_sha256": expected_hash, "binary_sha256": file_hash(binary),
                                            "process": native_helper.normalize_paths(receipt, work)})
                    binaries[variant] = binary
                for point in protocol["points"][mapping["family"]]:
                    for variant in ("original", "normalized"):
                        command = [str(binaries[variant])]
                        stdin = (" ".join(map(str, point)) + "\n").encode()
                        if variant == "original" and mapping["original_input_channel"] == "argv":
                            command += list(map(str, point)); stdin = b""
                        receipt, stdout, stderr = native_helper.bounded_process(command, stdin, directory)
                        if receipt["outcome"] != "ok" or stderr:
                            raise ValueError((compiler, sha, variant, point, "native process failure", receipt))
                        value = adapter.decode_original(stdout, mapping) if variant == "original" else bridge.canonical_output(stdout, "numeric")
                        expected = observed[sha, tuple(point)]["value"]
                        if value != expected:
                            raise ValueError((compiler, sha, variant, point, "native correspondence", value, expected))
                        row = {"compiler": compiler, "raw_source_sha256": sha, "variant": variant,
                               "family": mapping["family"], "input": point, "stdin_sha256": digest(stdin),
                               "value": value, "expected_value": expected, "agrees": True,
                               "process": native_helper.normalize_paths(receipt, work)}
                        native_records.append(row); stream.write(json.dumps(row, separators=(",", ":")) + "\n")
                stream.flush()
                print(json.dumps({"compiler": compiler, "complete_source": source_index, "sources": len(mappings)}), flush=True)
    save(output / "compilers.json", identities); save(output / "compilations.json", compile_records)


def recompute(output):
    protocol = json.loads((output / "protocol.json").read_text())
    mappings = json.loads((output / "mappings.json").read_text())
    observations = read_lines(output / "semantic-observations.jsonl")
    requests = json.loads((output / "requests.json").read_text())
    native = read_lines(output / "native-gcc.jsonl") + read_lines(output / "native-clang.jsonl")
    index = {(r["compiler"], r["raw_source_sha256"], r["variant"], tuple(r["input"])): r for r in native}
    cases = []; given_checks = 0
    for case, request in zip(protocol["cases"], requests):
        checks = []
        for test in protocol["given_tests"][case["family"]]:
            for compiler in ("gcc", "clang"):
                row = index[compiler, case["candidate_sha256"], "original", tuple(test["input_values"])]
                checks.append(row["process"]["outcome"] == "ok" and row["process"]["stdout"] == test["expected_stdout"])
        given_checks += len(checks)
        all_pass = bool(checks) and all(checks)
        cases.append({"case_id": case["case_id"], "family": case["family"], "subject": case["subject"],
                      "candidate_sha256": case["candidate_sha256"], "domain_points": request["domain_points"],
                      "all_given_tests_pass_both_compilers": all_pass, "given_test_compiler_checks": len(checks),
                      "tests_pass_but_wrong": all_pass and request["status"] == "REFUTED", "status": request["status"],
                      "witness": request["witness"], "mismatch_points": request["mismatch_points"],
                      "candidate_at_witness": request["candidate_at_witness"], "reference_at_witness": request["reference_at_witness"],
                      "original_at_witness": request["original_at_witness"]})
    return {"schema": "repairseal-introclass-certificate-summary-v1", "outcome": "PASS",
            "patches": len(cases), "original_subjects": len({c["subject"] for c in cases}),
            "families": len({c["family"] for c in cases}), "normalized_sources": len(mappings),
            "source_input_observations": len(observations), "native_process_executions": len(native),
            "native_correspondence_agreements": sum(r["agrees"] for r in native),
            "native_correspondence_disagreements": sum(not r["agrees"] for r in native),
            "compilations": len(json.loads((output / "compilations.json").read_text())),
            "complete_receiver_agreements": len(requests), "compact_confirmations": len(requests),
            "given_test_compiler_checks": given_checks,
            "tests_pass_but_wrong": sum(c["tests_pass_but_wrong"] for c in cases),
            "reference_math_agreements": sum(r["reference_math_agreement"] is True for r in observations),
            "cases": cases, "human_annotators": 0,
            "scope": "Six deliberately selected real published repairs, five original subjects, two IntroClass families. All claims are finite-domain and source-bound. The I/O adaptation has executable correspondence evidence; it is not an independently signed human derivation or an unrestricted C equivalence proof."}


def run(args):
    output = args.output.resolve()
    if output.exists(): raise ValueError("choose a new output directory")
    output.mkdir(parents=True)
    protocol = declaration(); save(output / "protocol.json", protocol)
    save(output / "execution.json", {"started_at_utc": datetime.now(timezone.utc).isoformat(),
                                     "python": sys.version, "platform": platform.platform(),
                                     "compiler_paths": [str(args.gcc), str(args.clang)]})
    mappings, observed = prepare(protocol, output)
    native_validation(protocol, mappings, observed, output, args.native_work.resolve(), [args.gcc, args.clang])
    if protocol["source_bindings"] != {name: file_hash(ROOT / name) for name in BOUND}:
        raise ValueError("executed source bindings changed")
    summary = recompute(output)
    if summary["tests_pass_but_wrong"] != len(SELECTED):
        raise ValueError("selected case did not pass every published test on both compilers")
    save(output / "summary.json", summary)
    save(output / "manifest.json", {"files": {str(p.relative_to(output)): file_hash(p)
                                             for p in sorted(output.rglob("*")) if p.is_file() and p.name != "manifest.json"}})
    print(json.dumps(summary, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--native-work", type=Path, required=True)
    parser.add_argument("--gcc", type=Path, default=Path(shutil.which("gcc") or "/usr/bin/gcc"))
    parser.add_argument("--clang", type=Path, default=Path(shutil.which("clang") or "/usr/bin/clang"))
    args = parser.parse_args(); run(args); return 0


if __name__ == "__main__": raise SystemExit(main())

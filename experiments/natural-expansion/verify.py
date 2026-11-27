"""Offline arithmetic, receipt-binding, coverage, and summary verification.

This checks retained evidence, not a fresh compiler execution. Exact-source
reconstruction still requires the externally acquired pinned Codeflaws archive.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
_spec = importlib.util.spec_from_file_location("repairseal_natural_expansion_run", HERE / "run.py")
study = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(study)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify_packet(packet, points):
    body = {k: v for k, v in packet.items() if k != "sha256"}
    require(packet["sha256"] == hashlib.sha256(study.symbolic._canonical(body)).hexdigest(), "packet digest")
    vectors = []
    names = ["i" + str(i) for i in range(len(points[0]))]
    positions = {name: i for i, name in enumerate(names)}
    for ordinal, node in enumerate(packet["nodes"]):
        require(node["id"] == ordinal, "node order")
        op = node["op"]
        if op in {"b", "u"}:
            vector = [node["data"] for _ in points]
        elif op == "input":
            require(node["data"] in positions, "input binding")
            vector = [point[positions[node["data"]]] & study.core.MASK for point in points]
        else:
            children = node["children"]
            require(all(type(ch) is int and 0 <= ch < ordinal for ch in children), "topological children")
            vector = [study.core.local_value(op, tuple(vectors[ch][column] for ch in children))
                      for column in range(len(points))]
        require(study.core.exact_equal(vector, packet["vectors"][ordinal]), "packet local-value mismatch")
        vectors.append(vector)
    require(len(vectors) == len(packet["vectors"]), "packet vector cardinality")
    return study.core.classify_vectors(points, packet["roots"], packet["events"], vectors)


def verify_receipt_streams(process):
    # All admitted programs emit ASCII scalar tokens; UBSan diagnostics and
    # compiler paths in this study are also ASCII. The raw stream is retained.
    for name in ("stdout", "stderr"):
        raw = process[name].encode("ascii")
        require(hashlib.sha256(raw).hexdigest() == process[name + "_sha256"], name + " receipt digest")
        require(len(raw) == process[name + "_bytes"], name + " receipt length")
    require(not process["truncated"], "truncated process receipt")


def verify(root: Path | None = None, records: Path | None = None):
    root = ROOT if root is None else Path(root)
    output = root / "experiments/natural-expansion/records" if records is None else Path(records)
    errors = []; recomputed = None; checks = 0
    try:
        inventory = json.loads((output / "manifest.json").read_text())["files"]
        actual_files = {str(p.relative_to(output)) for p in output.rglob("*") if p.is_file() and p.name != "manifest.json"}
        require(set(inventory) == actual_files, "record inventory completeness")
        for name, sha in inventory.items():
            require(study.file_hash(output / name) == sha, "record digest: " + name)
            checks += 1
        protocol = json.loads((output / "protocol.json").read_text())
        require(protocol == study.make_protocol(), "frozen protocol reconstruction from bound census and rules")
        for name, sha in protocol["source_bindings"].items():
            require(study.file_hash(root / name) == sha, "executed implementation binding: " + name)
        require(study.file_hash(root / "data/source-programs/normalized-corpus.json") == protocol["corpus_sha256"], "input census binding")
        cases = {c["subject"]: c for c in protocol["cases"]}
        for case in cases.values():
            require(case["points"] == sorted(case["points"]) and len(case["points"]) == len({tuple(p) for p in case["points"]}), "domain order or duplicate")
            require(0 < len(case["points"]) <= 4096, "domain admission bound")
            require(all(study.legal(case["problem"], p) for p in case["points"]), "illegal task input")
            require(all(t["input"] in case["points"] for t in case["given_tests"]), "provided test omitted from declared domain")
        observations = study.read_lines(output / "semantic-observations.jsonl")
        observed = {(r["source_sha256"], tuple(r["input"])): r for r in observations}
        require(len(observed) == len(observations), "duplicate semantic observation")
        expected_keys = {(c[role + "_sha256"], tuple(p)) for c in cases.values()
                         for role in ("original", "reference") for p in c["points"]}
        require(set(observed) == expected_keys, "semantic observation coverage")
        for row in observations:
            require(row["agrees"] is True and study.core.exact_equal({k: row[k] for k in ("defined", "value", "trace")}, row["symbolic"]), "concrete-symbolic disagreement")
        requests = json.loads((output / "requests.json").read_text())
        require({(r["subject"], r["candidate_role"]) for r in requests} == {(s, role) for s in cases for role in ("original", "reference")}, "request coverage")
        require(len(requests) == 2*len(cases), "request duplicate")
        for req in requests:
            case = cases[req["subject"]]
            expected = study.concrete_decision(case, req["candidate_role"], observed)
            require({k: req[k] for k in ("status", "witness")} == expected, "concrete canonical diagnostic")
            require(req["domain_points"] == len(case["points"]), "request domain count")
            for arm in ("full", "direct", "direct_record"):
                require({k: req[arm][k] for k in ("status", "witness")} == expected, arm + " result")
            require(req["complete_records_identical"] is True, "complete-record identity")
            packet_path = output / req["packet_path"]
            require(study.file_hash(packet_path) == req["packet_sha256"], "request packet file binding")
            packet = json.loads(packet_path.read_text())
            require(packet["task_sha256"] == req["task_sha256"], "request packet task binding")
            require(verify_packet(packet, case["points"]) == expected, "offline packet arithmetic verdict")
            cells = len(packet["nodes"]) * len(case["points"])
            require(req["full"]["semantic_cells"] == cells and req["direct_record"]["semantic_cells"] == cells, "complete-record cell count")
            if expected["status"] == "REFUTED":
                cert = req["compact_certificate"]
                body = {k: v for k, v in cert.items() if k != "certificate_sha256"}
                require(hashlib.sha256(study.symbolic._canonical(body)).hexdigest() == cert["certificate_sha256"], "compact digest")
                require(cert["task_sha256"] == req["task_sha256"], "compact task binding")
                require({k: cert[k] for k in ("obligation", "input", "trace")} == expected["witness"], "compact witness")
                require({k: req["compact"][k] for k in ("status", "witness")} == expected and req["compact"]["checked_points"] == 1, "compact confirmation")
                require(req["compact"]["checked_cells"] == len(packet["nodes"]), "compact point-local cell count")
            else:
                require(req["compact"] is None and req["compact_certificate"] is None, "accepted task has refutation")
            checks += 1
        native = study.read_lines(output / "native-gcc.jsonl") + study.read_lines(output / "native-clang.jsonl")
        native_keys = {(r["compiler"], r["mode"], r["native_case_id"]) for r in native}
        require(len(native_keys) == len(native), "duplicate native observation")
        plan = json.loads((output / "native-plan.json").read_text())
        expected_occurrences = []
        expected_plan = {}
        for case in protocol["cases"]:
            for role in ("original", "reference"):
                sha = case[role + "_sha256"]
                for test in case["given_tests"]:
                    case_id = sha + ":" + test["input_sha256"]
                    expected_occurrences.append({"subject": case["subject"], "candidate_role": role,
                                                 "source_sha256": sha, "native_case_id": case_id,
                                                 "input": test["input"], "expected": test["expected"],
                                                 "split": test["split"], "input_member": test["input_member"],
                                                 "input_sha256": test["input_sha256"], "output_sha256": test["output_sha256"]})
                    expected_plan[case_id] = {"id": case_id, "source_sha256": sha,
                                              "input": test["input"], "input_sha256": test["input_sha256"]}
                for point in case["points"]:
                    input_sha = hashlib.sha256((" ".join(map(str, point)) + "\n").encode()).hexdigest()
                    case_id = sha + ":" + input_sha
                    expected_plan.setdefault(case_id, {"id": case_id, "source_sha256": sha,
                                                       "input": point, "input_sha256": input_sha})
        require(json.loads((output / "test-occurrences.json").read_text()) == expected_occurrences,
                "all provided logical tests and exact input hashes retained")
        require({c["id"]: c for c in plan} == expected_plan and len(plan) == len(expected_plan),
                "native execution plan covers every given test and declared point")
        for compiler in ("gcc", "clang"):
            for case in plan:
                require((compiler, "ordinary", case["id"]) in native_keys, "ordinary native coverage")
                if not observed[case["source_sha256"], tuple(case["input"])]["defined"]:
                    require((compiler, "ubsan", case["id"]) in native_keys, "UBSan coverage")
        source_output_kind = {c[role + "_sha256"]: c["output_kind"] for c in cases.values() for role in ("original", "reference")}
        for row in native:
            verify_receipt_streams(row["process"])
            planned = expected_plan[row["native_case_id"]]
            require(all(row[k] == planned[k] for k in ("source_sha256", "input", "input_sha256")), "native receipt planned input binding")
            obs = observed[row["source_sha256"], tuple(row["input"])]
            require(row["model_defined"] == obs["defined"] and row["model_value"] == obs["value"], "native semantic binding")
            process = row["process"]
            value = None
            if process["outcome"] == "ok" and not process["stderr"]:
                value = study.bridge.canonical_output(process["stdout"].encode(), source_output_kind[row["source_sha256"]])
            require(value == row["native_value"], "native stdout decoding")
            if obs["defined"]:
                require(row["semantic_agrees"] is True and process["outcome"] == "ok" and not process["stderr"] and value == obs["value"], "defined native agreement")
            else:
                require(row["semantic_agrees"] is None, "undefined native run treated as defined")
            if row["mode"] == "ubsan":
                require(row["ubsan_detected"] and process["outcome"] == "nonzero" and "runtime error:" in process["stderr"], "UBSan diagnostic")
        for row in json.loads((output / "native-controls.json").read_text()):
            verify_receipt_streams(row)
            if row["control"] == "ubsan-run":
                require(row["outcome"] == "nonzero" and "runtime error:" in row["stderr"], "UBSan positive control")
            else:
                require(row["outcome"] == "ok", "native target or compiler control")
        for row in json.loads((output / "compilations.json").read_text()):
            verify_receipt_streams(row)
            require(row["outcome"] == "ok" and bool(row["binary_sha256"]), "native compilation")
        recomputed = study.recompute(output)
        require(recomputed == json.loads((output / "summary.json").read_text()), "recomputed summary mismatch")
    except (AssertionError, KeyError, ValueError, TypeError, OSError, IndexError) as exc:
        errors.append(type(exc).__name__ + ": " + str(exc))
    return {"status": "PASS" if not errors else "FAIL", "errors": errors,
            "checks": checks, "recomputed": recomputed,
            "scope": "Offline retained-evidence consistency and arithmetic replay; fresh original-source reconstruction requires the pinned archive."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--records", type=Path)
    args = parser.parse_args()
    result = verify(records=args.records)
    if args.output:
        study.save(args.output, result)
    print(json.dumps({k: v for k, v in result.items() if k != "recomputed"}, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

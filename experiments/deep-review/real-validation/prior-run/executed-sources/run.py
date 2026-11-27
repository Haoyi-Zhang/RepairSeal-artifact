#!/usr/bin/env python3
"""Freeze, execute, and verify the comparison/copy weak-order study.

`run --output NEW_DIR` launches fresh GCC processes; `verify --data DIR`
recomputes the quotient and validates retained native receipts without executing
them. Existing output directories are never overwritten.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ARTIFACT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from order_types import Program, patterns, rank_pattern, embed, EMBEDDINGS

SELECTED = ("apr-043", "apr-046", "apr-069", "apr-070", "apr-072", "apr-073")
MODES = {"O0": ["-O0"], "O2": ["-O2"],
         "ubsan-O1": ["-O1", "-fsanitize=undefined", "-fno-sanitize-recover=all"]}
FLAGS = ["-std=c11", "-include", "stdlib.h", "-Werror=implicit-function-declaration", "-Werror=format"]
DEPENDENCIES = ("experiments/deep-review/real-validation/order_types.py",
                "experiments/deep-review/real-validation/run.py",
                "experiments/introclass-certificates/independent_review.py",
                "experiments/real-patches/corpus.json", "experiments/real-patches/given-tests.json")


def require(ok, why):
    if not ok: raise ValueError(why)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def load(path):
    def pairs(items):
        out = {}
        for k, v in items:
            require(k not in out, "duplicate JSON member")
            out[k] = v
        return out
    return json.loads(path.read_text(), object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def utc():
    return datetime.now(timezone.utc).isoformat()


def independent_review():
    spec = importlib.util.spec_from_file_location("weak_order_source_review",
        ARTIFACT / "experiments/introclass-certificates/independent_review.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def declaration():
    corpus = load(ARTIFACT / "experiments/real-patches/corpus.json")
    cases = [next(c for c in corpus if c["case_id"] == name) for name in SELECTED]
    tests = load(ARTIFACT / "experiments/real-patches/given-tests.json")
    sources = {}
    for case in cases:
        for role in ("original", "candidate", "reference"):
            ident = case[role + "_sha256"]
            spec = {"family": case["family"], "reference": role == "reference"}
            require(ident not in sources or sources[ident] == spec, "source roles conflict")
            sources[ident] = spec
    for ident, spec in sources.items():
        raw = ARTIFACT / "experiments/real-patches/sources" / (ident + ".c")
        normalized = ARTIFACT / "experiments/introclass-certificates/records/normalized" / (ident + ".c")
        require(digest(raw.read_bytes()) == ident, "raw source identity")
        spec.update(raw_sha256=ident, normalized_sha256=digest(normalized.read_bytes()))
    points = {}
    for family, arity in (("median", 3), ("smallest", 4)):
        mapped = defaultdict(list)
        for pattern in patterns(arity):
            for embedding in EMBEDDINGS:
                mapped[embed(pattern, embedding)].append({"pattern": pattern, "embedding": embedding})
        for test in tests:
            if test["family"] == family:
                mapped[tuple(test["input_values"])].append({"given_test": test["suite"] + "/" + test["name"]})
        points[family] = [{"input": point, "reasons": reasons} for point, reasons in sorted(mapped.items())]
    return {
        "schema": "repairseal-order-type-protocol-v1", "created_utc": utc(),
        "selection": "Exploratory six previously known test-passing incorrect Angelix patches; five subjects and two families. Selection is outcome-directed and no prevalence estimate follows.",
        "exact_case_ids": SELECTED, "cases": cases, "sources": sources, "given_tests": tests,
        "order_types": {"median": patterns(3), "smallest": patterns(4)},
        "native_points": points, "embeddings": EMBEDDINGS,
        "native_modes": MODES, "compiler_flags": FLAGS,
        "compiler_scope": "One available GCC compiler, three optimization/sanitizer modes. No fresh Clang or external-verifier run is claimed.",
        "dependencies": {name: digest((ARTIFACT/name).read_bytes()) for name in DEPENDENCIES},
        "proof_scope": "All signed-int32 tuples for the admitted normalized comparison/copy computational fragment, under complete successful in-range decimal input and ordinary successful numeric output. This is an additional quotient analysis, not an expansion of RepairSeal's finite-domain acceptance contract. Raw/normalized computational AST correspondence and fresh boundary runs support the I/O adaptation; arbitrary C, arithmetic, malformed input, resource/environment failures and library implementations are excluded.",
    }


def compute(protocol, data):
    review = independent_review()
    classes = []; structural = []; index = {}
    for ident, spec in sorted(protocol["sources"].items()):
        raw = (data / "sources/raw" / (ident + ".c")).read_bytes()
        norm = (data / "sources/normalized" / (ident + ".c")).read_bytes()
        require(digest(raw) == ident and digest(norm) == spec["normalized_sha256"], "source binding")
        old, _ = review.parse_for_review(raw)
        new, _ = review.parse_for_review(norm, normalized=True)
        old_shape, old_stats = review.structural_signature(old, spec["family"], True, spec["reference"])
        new_shape, new_stats = review.structural_signature(new, spec["family"], False, spec["reference"])
        require(canonical(old_shape) == canonical(new_shape), "computational AST correspondence")
        program = Program(norm)
        require(program.arity == (3 if spec["family"] == "median" else 4), "declared arity")
        structural.append({"source": ident, "normalized_sha256": spec["normalized_sha256"],
                           "computational_ast_sha256": digest(canonical(old_shape)),
                           "raw": old_stats, "normalized": new_stats, "profile_admitted": True})
        for pattern in patterns(program.arity):
            result = program.evaluate(pattern)
            require(result["defined"], "uninitialized read or invalid path in admitted source")
            independent_value, independent_trace = review.model(ident, list(pattern))
            require(str(result["output_rank"]) == independent_value
                    and result["trace"] == independent_trace, "independent branch model disagreement")
            oracle = sorted(pattern)[1] if spec["family"] == "median" else min(pattern)
            if spec["reference"]: require(result["output_rank"] == oracle, "teacher differs from mathematics")
            row = {"source": ident, "family": spec["family"], "pattern": pattern,
                   **result, "oracle_rank": oracle, "matches_oracle": result["output_rank"] == oracle}
            classes.append(row); index[ident, pattern] = row
    cases = []
    for case in protocol["cases"]:
        family = case["family"]
        arity = 3 if family == "median" else 4
        provided = {rank_pattern(t["input_values"]) for t in protocol["given_tests"] if t["family"] == family}
        outcomes = []; signature = []
        for pattern in patterns(arity):
            original = index[case["original_sha256"], pattern]
            candidate = index[case["candidate_sha256"], pattern]
            kind = ("correct-preserved" if original["matches_oracle"] and candidate["matches_oracle"] else
                    "fixed" if candidate["matches_oracle"] else
                    "regressed" if original["matches_oracle"] else "still-wrong")
            outcomes.append({"pattern": pattern, "original_rank": original["output_rank"],
                             "candidate_rank": candidate["output_rank"], "oracle_rank": candidate["oracle_rank"],
                             "transition": kind, "covered_by_given_tests": pattern in provided,
                             "candidate_trace": candidate["trace"]})
            signature.append(candidate["output_rank"])
        counts = dict(sorted(Counter(r["transition"] for r in outcomes).items()))
        wrong = [r for r in outcomes if r["candidate_rank"] != r["oracle_rank"]]
        cases.append({"case_id": case["case_id"], "family": family, "subject": case["subject"],
                      "order_types": len(outcomes), "given_test_order_types": len(provided),
                      "wrong_order_types": len(wrong), "covered_wrong_order_types": sum(r["covered_by_given_tests"] for r in wrong),
                      "transitions": counts, "output_behavior_sha256": digest(canonical(signature)),
                      "outcomes": outcomes})
    return {"sources": structural, "order_classes": classes, "cases": cases}


def process(command, stdin=b"", timeout=15):
    began = time.perf_counter()
    result = subprocess.run(command, input=stdin, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    require(len(result.stdout) < 16384 and len(result.stderr) < 65536, "bounded process output")
    return {"command": list(map(str, command)), "returncode": result.returncode,
            "elapsed_seconds": time.perf_counter()-began,
            "stdin_sha256": digest(stdin),
            "stdout": result.stdout.decode("ascii"), "stderr": result.stderr.decode("ascii"),
            "stdout_sha256": digest(result.stdout), "stderr_sha256": digest(result.stderr)}


def expected_stdout(spec, variant, point, row):
    value = point[row["selected_input"]]
    if spec["reference"] and variant == "raw":
        return f"Please enter {len(point)} numbers separated by spaces > {value} is the {spec['family']}\n"
    return str(value) + "\n"


def fresh(args):
    output = args.output.resolve()
    require(not output.exists(), "output directory already exists")
    compiler = Path(shutil.which(args.gcc) or args.gcc).resolve()
    require(compiler.is_file(), "GCC executable unavailable")
    protocol = declaration()
    started = utc()
    compiler_version = process([str(compiler), "--version"])
    require(compiler_version["returncode"] == 0 and "gcc" in compiler_version["stdout"].lower(), "GCC identity")
    protocol["compiler"] = {"path": str(compiler), "sha256": digest(compiler.read_bytes()), "version": compiler_version}
    # Write all selection/domain/code identities before any source compilation.
    save(output / "protocol.json", protocol)
    for ident in protocol["sources"]:
        for variant, directory in (("raw", "experiments/real-patches/sources"),
                                   ("normalized", "experiments/introclass-certificates/records/normalized")):
            destination = output / "sources" / variant / (ident + ".c")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((ARTIFACT / directory / (ident + ".c")).read_bytes())
    abstract = compute(protocol, output)
    save(output / "abstract.json", abstract)
    index = {(r["source"], tuple(r["pattern"])): r for r in abstract["order_classes"]}
    compilations = []; executions = 0
    # Temporary binaries stay outside the data directory and are removed after
    # execution. Their complete compilation receipts and hashes are retained.
    with tempfile.TemporaryDirectory(prefix="weak-order-native-", dir=output.parent) as work_name:
        work = Path(work_name)
        with (output / "native.jsonl").open("w") as stream:
            for number, (ident, spec) in enumerate(sorted(protocol["sources"].items()), 1):
                binaries = {}
                for variant in ("raw", "normalized"):
                    source = output / "sources" / variant / (ident + ".c")
                    for mode, flags in MODES.items():
                        binary = work / (ident + "-" + variant + "-" + mode)
                        receipt = process([str(compiler), *FLAGS, *flags, str(source), "-o", str(binary)], timeout=60)
                        require(receipt["returncode"] == 0, "native compilation failed: " + receipt["stderr"])
                        binary_hash = digest(binary.read_bytes())
                        binaries[variant, mode] = (binary, binary_hash)
                        receipt["command"] = [x.replace(str(work), "$NATIVE_WORK").replace(str(output), "$DATA") for x in receipt["command"]]
                        compilations.append({"source": ident, "variant": variant, "mode": mode,
                                             "compiled_source_sha256": digest(source.read_bytes()),
                                             "binary_sha256": binary_hash, "process": receipt})
                jobs = [(entry["input"], variant, mode) for entry in protocol["native_points"][spec["family"]]
                        for variant in ("raw", "normalized") for mode in MODES]
                def execute(job):
                    point, variant, mode = job
                    binary, binary_hash = binaries[variant, mode]
                    argv = variant == "raw" and not spec["reference"]
                    stdin = b"" if argv else (" ".join(map(str, point)) + "\n").encode()
                    command = [str(binary)] + (list(map(str, point)) if argv else [])
                    receipt = process(command, stdin)
                    row = index[ident, rank_pattern(point)]
                    expected = expected_stdout(spec, variant, point, row)
                    require(receipt["returncode"] == 0 and not receipt["stderr"] and receipt["stdout"] == expected,
                            "native correspondence failure: " + repr((ident, point, variant, mode, receipt)))
                    receipt["command"][0] = receipt["command"][0].replace(str(work), "$NATIVE_WORK")
                    return {"source": ident, "variant": variant, "mode": mode, "input": point,
                            "pattern": rank_pattern(point), "binary_sha256": binary_hash,
                            "expected_stdout": expected, "process": receipt}
                with ThreadPoolExecutor(max_workers=4) as pool:
                    for row in pool.map(execute, jobs):
                        stream.write(json.dumps(row, separators=(",", ":")) + "\n"); executions += 1
                stream.flush()
                print(json.dumps({"source_completed": number, "sources": len(protocol["sources"]), "native_executions": executions}), flush=True)
    save(output / "compilations.json", compilations)
    require(protocol["dependencies"] == {name: digest((ARTIFACT/name).read_bytes()) for name in DEPENDENCIES}, "study source changed during run")
    save(output / "execution.json", {"started_utc": started, "finished_utc": utc(),
         "python": platform.python_version(), "platform": platform.platform(), "fresh_native_execution": True,
         "protocol_sha256": digest((output / "protocol.json").read_bytes()),
         "dependency_hashes_unchanged": True, "human_annotators": 0})
    summary = verify(output, compare_summary=False)
    save(output / "summary.json", summary)
    print(json.dumps(summary, indent=2), flush=True)


def verify(data, compare_summary=True):
    protocol = load(data / "protocol.json")
    require(protocol["schema"] == "repairseal-order-type-protocol-v1", "protocol schema")
    current = declaration()
    require(canonical({k: v for k, v in protocol.items() if k not in ("created_utc", "compiler")})
            == canonical({k: v for k, v in current.items() if k != "created_utc"}),
            "frozen selection, source, tests, domain and method declaration")
    require(protocol["exact_case_ids"] == list(SELECTED), "case population")
    require(protocol["native_modes"] == MODES and protocol["compiler_flags"] == FLAGS, "native treatment closure")
    require(protocol["dependencies"] == {name: digest((ARTIFACT/name).read_bytes()) for name in DEPENDENCIES}, "executed code binding")
    for family, arity in (("median", 3), ("smallest", 4)):
        require(protocol["order_types"][family] == [list(p) for p in patterns(arity)], "complete weak-order enumeration")
        expected = {embed(p, e) for p in patterns(arity) for e in EMBEDDINGS}
        expected |= {tuple(t["input_values"]) for t in protocol["given_tests"] if t["family"] == family}
        require([r["input"] for r in protocol["native_points"][family]] == [list(p) for p in sorted(expected)], "native domain closure")
    abstract = compute(protocol, data)
    require(canonical(abstract) == canonical(load(data / "abstract.json")), "abstract outcomes recomputation")
    index = {(r["source"], tuple(r["pattern"])): r for r in abstract["order_classes"]}
    compilations = load(data / "compilations.json")
    compile_index = {}
    for row in compilations:
        key = row["source"], row["variant"], row["mode"]
        require(key not in compile_index, "duplicate compilation")
        require(row["source"] in protocol["sources"] and row["variant"] in ("raw", "normalized") and row["mode"] in MODES, "unknown compilation")
        expected_hash = row["source"] if row["variant"] == "raw" else protocol["sources"][row["source"]]["normalized_sha256"]
        require(row["compiled_source_sha256"] == expected_hash, "compiled source identity")
        check_process(row["process"])
        require(row["process"]["returncode"] == 0, "failed compilation receipt")
        expected_command = [protocol["compiler"]["path"], *FLAGS, *MODES[row["mode"]],
                            "$DATA/sources/" + row["variant"] + "/" + row["source"] + ".c", "-o",
                            "$NATIVE_WORK/" + row["source"] + "-" + row["variant"] + "-" + row["mode"]]
        require(row["process"]["command"] == expected_command, "compilation command treatment")
        require(len(row["binary_sha256"]) == 64, "binary identity")
        compile_index[key] = row
    expected_compilations = {(ident, variant, mode) for ident in protocol["sources"] for variant in ("raw", "normalized") for mode in MODES}
    require(set(compile_index) == expected_compilations, "compilation closure")
    expected_keys = {(ident, variant, mode, tuple(point["input"]))
                     for ident, spec in protocol["sources"].items()
                     for point in protocol["native_points"][spec["family"]]
                     for variant in ("raw", "normalized") for mode in MODES}
    seen = set()
    supplied = {(case["candidate_sha256"], tuple(test["input_values"])): test["expected_stdout"]
                for case in protocol["cases"] for test in protocol["given_tests"] if case["family"] == test["family"]}
    with (data / "native.jsonl").open() as stream:
        for line in stream:
            row = json.loads(line)
            key = row["source"], row["variant"], row["mode"], tuple(row["input"])
            require(key in expected_keys and key not in seen, "native process coverage or duplicate")
            seen.add(key); spec = protocol["sources"][row["source"]]
            pattern = rank_pattern(row["input"])
            require(row["pattern"] == list(pattern), "native input weak order")
            record = index[row["source"], pattern]
            expected = expected_stdout(spec, row["variant"], row["input"], record)
            proc = row["process"]; check_process(proc)
            require(proc["returncode"] == 0 and proc["stderr"] == "" and proc["stdout"] == expected
                    and row["expected_stdout"] == expected, "native semantic/codec correspondence")
            if row["variant"] == "raw" and (row["source"], tuple(row["input"])) in supplied:
                require(proc["stdout"] == supplied[row["source"], tuple(row["input"])], "published test output oracle")
            compilation = compile_index[key[:3]]
            require(row["binary_sha256"] == compilation["binary_sha256"], "execution binary binding")
            argv = row["variant"] == "raw" and not spec["reference"]
            require(proc["command"] == [compilation["process"]["command"][-1]] + (list(map(str, row["input"])) if argv else []), "exact native argv")
            stdin = b"" if argv else (" ".join(map(str, row["input"])) + "\n").encode()
            require(proc["stdin_sha256"] == digest(stdin), "exact native stdin")
    require(seen == expected_keys, "complete native execution closure")
    groups = defaultdict(list)
    compact_cases = []
    for case in abstract["cases"]:
        groups[case["family"], case["output_behavior_sha256"]].append(case["case_id"])
        compact_cases.append({key: value for key, value in case.items() if key != "outcomes"})
    # Given tests can repeat the same vector; count the named suite entries,
    # while fresh execution is deduplicated by actual source/input/mode/form.
    given_test_checks = sum(sum(t["family"] == c["family"] for t in protocol["given_tests"]) * len(MODES)
                            for c in protocol["cases"])
    summary = {"schema": "repairseal-order-type-summary-v1", "status": "PASS",
               "patches": len(protocol["cases"]), "original_subjects": len({c["subject"] for c in protocol["cases"]}),
               "families": 2, "admitted_source_identities": len(protocol["sources"]),
               "order_type_counts": {"median": len(patterns(3)), "smallest": len(patterns(4))},
               "source_order_class_observations": len(abstract["order_classes"]),
               "defined_classes": sum(r["defined"] for r in abstract["order_classes"]),
               "independent_branch_model_agreements": len(abstract["order_classes"]),
               "computational_ast_correspondences": len(abstract["sources"]),
               "distinct_candidate_output_behaviors": len(groups),
               "candidate_behavior_groups": sorted(groups.values()),
               "native_unique_points_per_family": {f: len(p) for f, p in protocol["native_points"].items()},
               "native_source_input_pairs": len(expected_keys) // (2*len(MODES)),
               "native_compilations": len(compilations), "native_process_executions": len(seen),
               "native_correspondence_agreements": len(seen), "native_correspondence_disagreements": 0,
               "compiler_families": ["gcc"], "compiler_modes": list(MODES),
               "named_given_test_candidate_mode_checks": given_test_checks,
               "provided_tests_native_pass": all(c["covered_wrong_order_types"] == 0 for c in abstract["cases"]),
               "cases": compact_cases, "human_annotators": 0,
               "limits": protocol["proof_scope"]}
    execution = load(data / "execution.json")
    require(execution["protocol_sha256"] == digest((data / "protocol.json").read_bytes())
            and execution["fresh_native_execution"] is True and execution["dependency_hashes_unchanged"] is True,
            "fresh-run protocol binding")
    if compare_summary:
        require(canonical(summary) == canonical(load(data / "summary.json")), "summary recomputation")
    return summary


def check_process(receipt):
    require(type(receipt["returncode"]) is int, "process return code")
    for name in ("stdout", "stderr"):
        require(type(receipt[name]) is str and digest(receipt[name].encode("ascii")) == receipt[name + "_sha256"], "process stream hash")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    run = sub.add_parser("run"); run.add_argument("--output", type=Path, required=True); run.add_argument("--gcc", default="gcc")
    check = sub.add_parser("verify"); check.add_argument("--data", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "run": fresh(args)
    else: print(json.dumps(verify(args.data.resolve()), indent=2))


if __name__ == "__main__":
    main()

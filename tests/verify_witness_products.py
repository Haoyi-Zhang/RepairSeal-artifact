#!/usr/bin/env python3
"""Compare the executed and current C emitters on every retained witness input.

Each emitter runs in a separate isolated Python process.  Both must reproduce
the exact retained program bytes; this is an equality check on the complete
recorded population, not a claim about unmeasured guard expressions.  The
executed snapshot is checked literally against the original protocol.  Current
source identities are recorded separately and are never substituted into it.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

if not __debug__:
    raise SystemExit("Witness product verification requires assertions enabled; -O and -OO are rejected.")

ROOT = Path(__file__).resolve().parents[1]
BOUND_SOURCES = (
    "src/proof_dag_checker.py", "src/demand_evaluator.py",
    "tests/cbmc_comparison.py", "tests/scientific_driver.py",
    "tests/witness_interoperability.py",
)
POPULATION = {"core": 380, "grammar": 400, "natural": 24}
REQUESTS = sum(POPULATION.values())
CONTINUITY_FIELDS = (
    "original_source_bindings_unchanged", "original_input_bindings_unchanged",
    "original_tool_bindings_unchanged", "inherited_observations_unchanged",
    "interruption_records_unchanged", "continuation_source_unchanged",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON object key: " + key)
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("nonfinite JSON value: " + value)


def decode(data):
    return json.loads(data, object_pairs_hook=unique_object, parse_constant=reject_constant)


def read(path):
    return decode(path.read_bytes())


def identity(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_bindings(root):
    return {name: identity(root / name) for name in BOUND_SOURCES}


def check_snapshot(root, expected):
    require(set(expected) == set(BOUND_SOURCES), "the executed source inventory differs from the declared five files")
    actual = source_bindings(root)
    require(actual == expected, "executed source bytes differ from the original protocol")
    return actual


def completed_study(study):
    """Check completeness without replacing the independent raw-record audit."""
    filenames = ["protocol.json", "summary.json", "cases.json", "controls.json"]
    protocol, summary, rows, controls = [read(study / name) for name in filenames]
    require(protocol["pilot_limit"] is None and protocol["planned_requests"] == REQUESTS,
            "a complete registered population is required; pilots are not certified")
    require(protocol["population"] == POPULATION and len(protocol["requests"]) == REQUESTS,
            "the original population does not contain the registered 804 requests")
    require(summary["outcome"] == "COMPLETE_WITH_RECORDED_EXTERNAL_OUTCOMES",
            "the primary campaign is incomplete")
    require(summary["source_inputs_and_tools_unchanged"] is True,
            "the completed campaign did not establish execution continuity")
    require(summary["producer_disagreements"] == summary["direct_cpa_disagreements"] == [],
            "the primary campaign contains a definitive semantic disagreement")
    require(len(rows) == REQUESTS and [row["index"] for row in rows] == list(range(REQUESTS)),
            "the retained cases do not contain each registered original index exactly once")
    require(Counter(row["population"] for row in rows) == POPULATION,
            "the completed case population differs from the protocol")
    require(summary["groups"]["all"]["requests"] == REQUESTS and
            len(controls) == summary["control_runs"] == 18,
            "the complete subjects and study controls are required")
    # Every retained invocation is counted once by its concrete path. Preserved
    # failures and inherited-policy rechecks are attempts in their own right.
    # A failed directory creation has no invocation receipt and is not inferred
    # to have launched a compiler or any external verifier.
    native_receipts = sorted(study.rglob("native-compile.invocation.json"))
    amendment_path = study / "continuation-protocol.json"
    if amendment_path.exists():
        amendment = read(amendment_path)
        execution = summary["execution"]
        initial, pending = amendment["initial_completed_indices"], amendment["pending_original_indices"]
        require(len(initial) == len(set(initial)) and len(pending) == len(set(pending)) and
                not set(initial) & set(pending) and sorted(initial + pending) == list(range(REQUESTS)),
                "the continuation does not partition the original requested population")
        require(amendment["original_protocol_identity"] == identity(study / "protocol.json") and
                amendment["source_files"] == protocol["source_files"],
                "the continuation is not bound to the exact original protocol and sources")
        require(all(execution[field] is True for field in CONTINUITY_FIELDS),
                "continuation source/input/observation continuity failed")
        require(execution["complete_subjects"] == REQUESTS and
                execution["initial_completed_subjects"] == len(initial) and
                execution["continuation_completed_subjects"] == len(pending) and
                execution["initial_failed_native_attempts"] == len(amendment["failed_native_indices"]) and
                execution["actual_native_compilation_attempts"] == len(native_receipts) and
                execution["successful_corrected_policy_native_compilations"] == REQUESTS,
                "continuation attempt accounting is inconsistent")
        continuation_source = amendment["continuation_source"]
        snapshot = study / continuation_source["snapshot"]
        require(snapshot.resolve().is_relative_to(study.resolve()) and
                identity(snapshot) == continuation_source["identity"],
                "the continuation source snapshot changed")
        native = read(study / "native-reconciliation/summary.json")
        native_rows = read(study / "native-reconciliation/records.json")
        require(native["outcome"] == "PASS_UNIFORM_NATIVE_POLICY" and
                native["requests"] == native["actual_corrected_policy_compilations"] == REQUESTS and
                native["native_mismatches"] == 0 and
                native["compiler_policy"] == amendment["native_policy_after"] and
                [row["index"] for row in native_rows] == list(range(REQUESTS)),
                "the amended compiler policy was not reconciled across all original subjects")
        filenames += ["continuation-protocol.json", "native-reconciliation/summary.json",
                      "native-reconciliation/records.json", continuation_source["snapshot"]]
        resume_path = study / "resource-resume-protocol.json"
        if resume_path.exists():
            resume = read(resume_path)
            checkpoint, remaining = resume["inherited_complete_indices"], resume["pending_original_indices"]
            require(len(checkpoint) == len(set(checkpoint)) and len(remaining) == len(set(remaining)) and
                    set(initial) < set(checkpoint) and not set(checkpoint) & set(remaining) and
                    sorted(checkpoint + remaining) == list(range(REQUESTS)) and
                    resume["partial_case_directories"] == [],
                    "the resource-resume checkpoint is not a complete partition of original subjects")
            require(resume["original_protocol_identity"] == identity(study / "protocol.json") and
                    resume["continuation_protocol_identity"] == identity(amendment_path) and
                    resume["initial_source_files"] == protocol["source_files"] and
                    resume["continuation_source"] == continuation_source and
                    resume["native_policy"] == amendment["native_policy_after"],
                    "the resource-resume segment changed a registered scientific binding or policy")
            require(execution["resource_checkpoint_unchanged"] is True and
                    execution["resource_resume_source_unchanged"] is True and
                    execution["first_continuation_completed_subjects"] == len(checkpoint) - len(initial) and
                    execution["resource_resume_completed_subjects"] == len(remaining) and
                    execution["resource_resume_protocol"] == "resource-resume-protocol.json" and
                    execution["resource_interruptions"] == 1,
                    "the resource-resume execution accounting or continuity failed")
            resumed_source = resume["resume_source"]
            resumed_snapshot = study / resumed_source["snapshot"]
            require(resumed_snapshot.resolve().is_relative_to(study) and
                    identity(resumed_snapshot) == resumed_source["identity"],
                    "the resource-resume source snapshot changed")
            termination = read(study / "resource-interruption/termination.json")
            require(termination["complete_case_records"] == len(checkpoint) and
                    termination["partial_case_directories"] == [] and
                    termination["native_compiler_attempts_added_by_this_resource_failure"] == 0,
                    "the retained resource interruption differs from the declared complete checkpoint")
            filenames += ["resource-resume-protocol.json", resumed_source["snapshot"],
                          "resource-interruption/termination.json"]
        else:
            require("resource_resume_protocol" not in execution,
                    "a resource-resume execution must retain its explicit segment protocol")
    else:
        require("execution" not in summary,
                "an amended execution must retain its explicit continuation protocol")
        require(len(native_receipts) == REQUESTS, "a fresh unamended campaign must retain every native invocation")
    filenames += [str(path.relative_to(study)) for path in native_receipts]
    return protocol, rows, {name: identity(study / name) for name in filenames}


def input_bindings(study, protocol, rows):
    bindings = []
    paths = []
    for row in rows:
        index = row["index"]
        declared = protocol["requests"][index]
        require((declared["population"], declared["path"]) == (row["population"], row["input_file"]),
                f"request {index} has a different original population or input path")
        directory = study / "cases" / f"{index:04d}"
        require(read(directory / "case-summary.json") == row,
                f"request {index} has inconsistent per-case and aggregate records")
        request_path, program_path = directory / "request.json", directory / "program.c"
        request_identity = identity(request_path)
        require(request_identity == declared["identity"],
                f"request {index} differs from the original registered input bytes")
        bindings.append({"index": index, "request_sha256": request_identity,
                         "program_sha256": identity(program_path)})
        paths.append(request_path)
    return bindings, paths


def worker(root, paths):
    # A fresh interpreter has no imported receiver or emitter from either root.
    module_path = root / "tests/witness_interoperability.py"
    spec = importlib.util.spec_from_file_location("repairseal_isolated_product_driver", module_path)
    require(spec is not None and spec.loader is not None, "the emitter module could not be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return [module.emit_product(read(Path(path))) for path in paths]


def emit_isolated(root, paths):
    command = [sys.executable, "-I", "-B", str(Path(__file__).resolve()), "--_emit-root", str(root.resolve())]
    result = subprocess.run(command, input=json.dumps([str(path.resolve()) for path in paths]).encode(),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=600, check=False)
    require(result.returncode == 0,
            "isolated emitter failed: " + result.stderr.decode("utf-8", errors="replace"))
    values = decode(result.stdout)
    require(isinstance(values, list) and len(values) == len(paths) and all(isinstance(value, str) for value in values),
            "isolated emitter returned an invalid product sequence")
    return values


def compare_products(study, rows, executed, current):
    require(len(executed) == len(current) == len(rows), "product sequence lengths differ")
    total = 0
    for row, old, new in zip(rows, executed, current):
        index = row["index"]
        actual = (study / "cases" / f"{index:04d}" / "program.c").read_bytes()
        require(old.encode("utf-8") == actual, f"executed emitter differs from retained C product {index}")
        require(new.encode("utf-8") == actual, f"current emitter differs from retained C product {index}")
        total += len(actual)
    return total


def verify(study, current_root=ROOT):
    study = study.resolve()
    protocol, rows, study_before = completed_study(study)
    executed_root = study / "executed-sources"
    executed_before = check_snapshot(executed_root, protocol["source_files"])
    current_before = source_bindings(current_root)
    cases_before, paths = input_bindings(study, protocol, rows)
    checker_before = identity(Path(__file__))
    executed = emit_isolated(executed_root, paths)
    current = emit_isolated(current_root, paths)
    compared = compare_products(study, rows, executed, current)
    require(source_bindings(current_root) == current_before and
            check_snapshot(executed_root, protocol["source_files"]) == executed_before and
            input_bindings(study, protocol, rows)[0] == cases_before and
            {name: identity(study / name) for name in study_before} == study_before and
            identity(Path(__file__)) == checker_before,
            "a source, input, product or completion record changed during product verification")
    return {
        "outcome": "PASS_IDENTICAL_WITNESS_PRODUCTS", "requests": len(rows),
        "protocol_sha256": study_before["protocol.json"],
        "executed_source_bindings": executed_before, "current_source_bindings": current_before,
        "checker_source_sha256": checker_before, "completion_record_bindings": study_before,
        "case_bindings": cases_before, "identical_products": len(rows),
        "compared_source_bytes": compared, "isolated_emitter_processes": 2,
        "retained_native_compile_receipts": sum(name.endswith("native-compile.invocation.json") for name in study_before),
        "native_attempt_accounting_basis": "Distinct retained invocation receipts, including preserved failed compilations and corrected-policy rechecks; directory-creation attempts are not inferred.",
        "unchanged_during_check": True,
        "scope": "Exact UTF-8 C product equality for every retained registered input. Current-source changes are bound separately; this does not extend the recorded external-tool results to additional guard expressions.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--_emit-root", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args._emit_root is not None:
        require(args.study is None and args.output is None, "internal emitter mode takes only an emitter root")
        paths = decode(sys.stdin.buffer.read())
        require(isinstance(paths, list) and all(isinstance(path, str) for path in paths),
                "invalid internal request path sequence")
        print(json.dumps(worker(args._emit_root.resolve(), paths), allow_nan=False))
        return
    if args.study is None or args.output is None:
        parser.error("--study and --output are required")
    if args.output.exists():
        parser.error("output must be a new file; retained evidence is never overwritten")
    result = verify(args.study)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({key: result[key] for key in ("outcome", "requests", "identical_products", "compared_source_bytes")}))


if __name__ == "__main__":
    main()

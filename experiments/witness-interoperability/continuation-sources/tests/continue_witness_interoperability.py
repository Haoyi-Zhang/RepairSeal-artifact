#!/usr/bin/env python3
"""Complete an interrupted witness study under an explicit compiler amendment.

The original protocol and completed records remain immutable. A corrected
native C11 diagnostic policy is checked on every original subject, while
already reconciled producer/consumer observations are retained. This command
never represents the interrupted invocation as a complete execution.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import time

if not __debug__:
    raise SystemExit("Witness continuation requires assertions enabled; -O and -OO are rejected.")

import witness_interoperability as study


def read(path):
    return json.loads(path.read_text())


def identity(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def manifest(directory, base):
    return {str(path.relative_to(base)): identity(path)
            for path in sorted(directory.rglob("*")) if path.is_file()}


def unchanged(bindings, base):
    return all((base / path).is_file() and identity(base / path) == value for path, value in bindings.items())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", type=Path, required=True)
    parser.add_argument("--failure-stdout", type=Path, required=True)
    parser.add_argument("--failure-stderr", type=Path, required=True)
    parser.add_argument("--initial-exit-code", type=int, required=True)
    args = parser.parse_args()
    root = args.study.resolve()
    if (root / "continuation-protocol.json").exists() or (root / "summary.json").exists():
        parser.error("continuation protocol and completion summary must not already exist")
    if args.initial_exit_code != 1:
        parser.error("this amendment requires the recorded native-compile failure exit code")
    protocol = read(root / "protocol.json")
    assert protocol["pilot_limit"] is None and protocol["planned_requests"] == 804
    assert len(protocol["requests"]) == 804
    interrupted = root / "interruption"
    audit = read(interrupted / "inherited-verification.json")
    audit_binding = read(interrupted / "audit-binding.json")
    assert audit["outcome"] == "PASS_INTERRUPTED_WITNESS_RECORDS"
    assert identity(interrupted / audit_binding["source"]) == audit_binding["source_identity"]
    assert identity(interrupted / audit_binding["report"]) == audit_binding["report_identity"]
    rows = sorted((read(path) for path in (root / "cases").glob("*/case-summary.json")), key=lambda row: row["index"])
    inherited = [row["index"] for row in rows]
    assert inherited == audit["completed_indices"] and len(rows) == audit["requests"]
    assert len(inherited) == len(set(inherited))
    pending = [index for index in range(804) if index not in set(inherited)]
    assert pending
    failed = []
    for directory in sorted((root / "cases").iterdir()):
        if int(directory.name) in inherited:
            continue
        invocation = read(directory / "native-compile.invocation.json")
        error = (directory / "native-compile.stderr.txt").read_text()
        assert invocation["exit_code"] != 0 and invocation["timed_out"] is False
        assert "-Werror=xor-used-as-pow" in error
        assert not (directory / "producer.invocation.json").exists()
        failed.append(int(directory.name))
    assert failed == [526], "the declared amendment covers exactly the observed compiler diagnostic"
    assert "-Werror=xor-used-as-pow" in args.failure_stderr.read_text()
    assert "native product compilation failed" in args.failure_stderr.read_text()
    sources = {name: identity(study.ROOT / name) for name in protocol["source_files"]}
    assert sources == protocol["source_files"]
    for name, bound in sources.items():
        assert identity(root / "executed-sources" / name) == bound
    input_bindings = {row["path"]: row["identity"] for row in protocol["requests"]}
    assert unchanged(input_bindings, study.ROOT)
    tools = protocol["external_tool_files"]
    assert unchanged(tools, Path("/"))
    for tool in ("cbmc", "cpachecker", "gcc"):
        invocation = read(root / (tool + "-environment.invocation.json"))
        setattr(args, tool, Path(invocation["argv"][0]))
        assert identity(getattr(args, tool)) == tools[str(getattr(args, tool))]
    args.jobs = protocol["jobs"]
    args.timeout = protocol["timeout_seconds"]
    args.cpu_limit = protocol["cpu_limit_seconds"]
    inherited_files = {}
    for index in inherited:
        inherited_files.update(manifest(root / "cases" / f"{index:04d}", root))
    for name in ("protocol.json", "completed-before-failure.json"):
        inherited_files[name] = identity(root / name)
    for name in ("inherited-verification.json", "audit-source.py", "audit-binding.json"):
        inherited_files["interruption/" + name] = identity(interrupted / name)
    for origin, name in ((args.failure_stdout, "driver.stdout.txt"), (args.failure_stderr, "driver.stderr.txt")):
        destination = interrupted / name
        if destination.exists():
            parser.error(f"interruption log already exists: {name}")
        shutil.copy2(origin, destination)
        assert identity(origin) == identity(destination)
    for index in failed:
        target = interrupted / "cases" / f"{index:04d}"
        target.parent.mkdir(parents=True, exist_ok=True)
        assert not target.exists()
        (root / "cases" / f"{index:04d}").rename(target)
    study.dump(interrupted / "termination.json", {
        "observed_process_exit_code": args.initial_exit_code,
        "reason": "GCC promoted its XOR-as-power intent warning to an error; no native executable or external decision was produced for that attempt.",
        "failed_native_indices": failed,
        "complete_case_records": len(inherited),
        "rows_returned_to_initial_collector": len(read(root / "completed-before-failure.json")),
        "completed_during_thread_pool_shutdown": sorted(set(inherited) - {row["index"] for row in read(root / "completed-before-failure.json")}),
    })
    interruption_files = manifest(interrupted, root)
    source_snapshot = root / "continuation-sources" / "tests" / Path(__file__).name
    source_snapshot.parent.mkdir(parents=True)
    with source_snapshot.open("xb") as stream:
        stream.write(Path(__file__).read_bytes())
    continuation_source = identity(Path(__file__))
    assert identity(source_snapshot) == continuation_source
    uniform = root / "native-reconciliation"
    uniform.mkdir()
    amendment = {
        "type": "Explicit continuation after a native compiler diagnostic",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "original_protocol": "protocol.json", "original_protocol_identity": identity(root / "protocol.json"),
        "initial_exit_code": args.initial_exit_code,
        "initial_completed_indices": inherited, "pending_original_indices": pending,
        "failed_native_indices": failed,
        "selection": "Every original planned index absent from a complete, independently reconciled case record; no selection by tool result or effect direction.",
        "native_policy_before": ["-std=c11", "-O0", "-fPIC", "-shared", "-Werror"],
        "native_policy_after": ["-std=c11", "-O0", "-fPIC", "-shared", "-pedantic-errors"],
        "native_policy_reason": "Enforce C11 constraints while retaining nonfatal programmer-intent warnings for admitted bitwise XOR expressions.",
        "uniform_native_population": "All804 original subjects: repeat native correspondence for inherited subjects in native-reconciliation/cases; pending subjects receive the corrected policy in their ordinary case directory.",
        "producer_consumer_policy": "Original executables, commands, four-case concurrency, wall limits, CPU limits, program/property relation and arm rotation are unchanged.",
        "source_files": sources,
        "continuation_source": {"path": "tests/" + Path(__file__).name, "identity": continuation_source,
                                "snapshot": str(source_snapshot.relative_to(root))},
        "inherited_file_bindings": inherited_files,
        "interruption_file_bindings": interruption_files,
        "native_attempt_accounting": {"initial_successful": len(inherited), "initial_failed": len(failed),
                                      "planned_corrected_policy": 804},
    }
    study.dump(root / "continuation-protocol.json", amendment)
    original_run = study.run_process

    def corrected_process(argv, cwd, prefix, timeout, env=None):
        command = list(argv)
        if prefix == "native-compile":
            assert command.count("-Werror") == 1
            command[command.index("-Werror")] = "-pedantic-errors"
        return original_run(command, cwd, prefix, timeout, env)

    study.run_process = corrected_process
    started = time.perf_counter()
    uniform_rows = []

    def recheck(row):
        index = row["index"]
        original = root / "cases" / f"{index:04d}"
        directory = uniform / "cases" / f"{index:04d}"
        directory.mkdir(parents=True)
        for name in ("program.c", "request.json"):
            shutil.copy2(original / name, directory / name)
            assert identity(original / name) == identity(directory / name)
        native = study.native_correspondence(read(directory / "request.json"), directory, args.gcc)
        old = read(original / "native-correspondence.json")
        new = read(directory / "native-correspondence.json")
        assert old == new, "diagnostic policy must not change any native semantic outcome"
        return {"index": index, "record_directory": str(directory.relative_to(root)),
                "phase": "native_reconciliation", **native}

    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        for future in as_completed([executor.submit(recheck, row) for row in rows]):
            uniform_rows.append(future.result())
    study.dump(uniform / "inherited.json", sorted(uniform_rows, key=lambda row: row["index"]))
    print(json.dumps({"corrected_policy_native_rechecks": len(uniform_rows), "pending_external_subjects": len(pending)}), flush=True)
    environment = dict(os.environ)
    completed_new = 0
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = [executor.submit(study.check_case, index, protocol["requests"][index]["population"],
                                   study.ROOT / protocol["requests"][index]["path"], args, root, environment)
                   for index in pending]
        for future in as_completed(futures):
            try:
                row = future.result()
                rows.append(row)
                completed_new += 1
                uniform_rows.append({"index": row["index"], "record_directory": f"cases/{row['index']:04d}",
                                     "phase": "continuation", **row["native_correspondence"]})
            except BaseException:
                for remaining in futures:
                    remaining.cancel()
                study.dump(root / "continuation-completed-before-failure.json", sorted(rows, key=lambda row: row["index"]))
                raise
            if completed_new % 20 == 0 or len(rows) == 804:
                study.dump(root / "continuation-progress.json", {"completed_indices": sorted(row["index"] for row in rows),
                                                                  "completed_continuation_subjects": completed_new, "planned_requests": 804})
                print(json.dumps({"complete_subjects": len(rows), "continuation_subjects": completed_new, "planned_requests": 804}), flush=True)
    rows.sort(key=lambda row: row["index"])
    assert [row["index"] for row in rows] == list(range(804))
    study.dump(root / "cases.json", rows)
    controls = study.run_controls(rows, args, root)
    uniform_rows.sort(key=lambda row: row["index"])
    assert [row["index"] for row in uniform_rows] == list(range(804))
    study.dump(uniform / "records.json", uniform_rows)
    study.dump(uniform / "summary.json", {"outcome": "PASS_UNIFORM_NATIVE_POLICY", "requests": 804,
                                         "actual_corrected_policy_compilations": 804,
                                         "native_points": sum(row["points"] for row in uniform_rows),
                                         "native_mismatches": 0,
                                         "compiler_policy": amendment["native_policy_after"]})
    summary = study.summarize(rows, controls)
    original_sources_unchanged = unchanged(sources, study.ROOT)
    inputs_unchanged = unchanged(input_bindings, study.ROOT)
    tools_unchanged = unchanged(tools, Path("/"))
    inherited_unchanged = unchanged(inherited_files, root)
    failure_records_unchanged = unchanged(interruption_files, root)
    continuation_unchanged = identity(Path(__file__)) == continuation_source == identity(source_snapshot)
    summary["source_inputs_and_tools_unchanged"] = all((original_sources_unchanged, inputs_unchanged, tools_unchanged,
                                                       inherited_unchanged, failure_records_unchanged, continuation_unchanged))
    summary["execution"] = {
        "mode": "Interrupted invocation followed by an explicitly registered continuation",
        "complete_subjects": 804, "initial_completed_subjects": len(inherited),
        "continuation_completed_subjects": len(pending), "initial_failed_native_attempts": len(failed),
        "actual_native_compilation_attempts": len(inherited) + len(failed) + 804,
        "successful_corrected_policy_native_compilations": 804,
        "native_reconciliation": "native-reconciliation/summary.json",
        "continuation_protocol": "continuation-protocol.json", "interruption": "interruption/termination.json",
        "original_source_bindings_unchanged": original_sources_unchanged,
        "original_input_bindings_unchanged": inputs_unchanged,
        "original_tool_bindings_unchanged": tools_unchanged,
        "inherited_observations_unchanged": inherited_unchanged,
        "interruption_records_unchanged": failure_records_unchanged,
        "continuation_source_unchanged": continuation_unchanged,
        "continuation_wall_seconds": time.perf_counter() - started,
        "completed_utc": datetime.now(timezone.utc).isoformat(),
    }
    if not summary["source_inputs_and_tools_unchanged"]:
        summary["outcome"] = "FAILED_CHANGED_EXECUTION_INPUT"
    study.dump(root / "summary.json", summary)
    print(json.dumps(summary, indent=2), flush=True)
    if summary["producer_disagreements"] or summary["direct_cpa_disagreements"] or not summary["source_inputs_and_tools_unchanged"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

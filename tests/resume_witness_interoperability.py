#!/usr/bin/env python3
"""Resume the registered compiler-policy continuation after a resource failure.

This segment changes no scientific setting. It retains the complete checkpoint,
the resource exception and both earlier source/protocol bindings, then executes
the complement of the reconciled original subject indices.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import time

if not __debug__:
    raise SystemExit("Witness resource resume requires assertions enabled; -O and -OO are rejected.")

import continue_witness_interoperability as previous

study = previous.study
read, identity, manifest, unchanged = previous.read, previous.identity, previous.manifest, previous.unchanged


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", type=Path, required=True)
    parser.add_argument("--failure-stdout", type=Path, required=True)
    parser.add_argument("--failure-stderr", type=Path, required=True)
    args = parser.parse_args()
    root = args.study.resolve()
    if any((root / name).exists() for name in ("resource-resume-protocol.json", "summary.json", "cases.json", "controls.json")):
        parser.error("this resource-resume segment must not overwrite another segment or complete output")
    protocol, amendment = read(root / "protocol.json"), read(root / "continuation-protocol.json")
    interrupted = root / "resource-interruption"
    audit = read(interrupted / "inherited-verification.json")
    assert audit["outcome"] == "PASS_INTERRUPTED_WITNESS_RECORDS"
    rows = sorted((read(path) for path in (root / "cases").glob("*/case-summary.json")), key=lambda row: row["index"])
    inherited = [row["index"] for row in rows]
    assert inherited == audit["completed_indices"] == list(range(572))
    assert {int(path.name) for path in (root / "cases").iterdir()} == set(inherited), "any incomplete directory must be separately preserved and reviewed"
    pending = [index for index in range(804) if index not in set(inherited)]
    initial = set(amendment["initial_completed_indices"])
    assert initial < set(inherited) and sorted(initial | set(amendment["pending_original_indices"])) == list(range(804))
    assert "No space left on device" in args.failure_stderr.read_text()
    assert "directory.mkdir(parents=True)" in args.failure_stderr.read_text()
    assert "cases/0572" in args.failure_stderr.read_text()
    assert unchanged(amendment["inherited_file_bindings"], root)
    assert unchanged(amendment["interruption_file_bindings"], root)
    assert identity(root / "protocol.json") == amendment["original_protocol_identity"]
    assert unchanged(protocol["source_files"], study.ROOT)
    assert identity(Path(previous.__file__)) == amendment["continuation_source"]["identity"]
    assert identity(root / amendment["continuation_source"]["snapshot"]) == amendment["continuation_source"]["identity"]
    inputs = {item["path"]: item["identity"] for item in protocol["requests"]}
    assert unchanged(inputs, study.ROOT)
    assert unchanged(protocol["external_tool_files"], Path("/"))
    for tool in ("cbmc", "cpachecker", "gcc"):
        setattr(args, tool, Path(read(root / (tool + "-environment.invocation.json"))["argv"][0]))
    args.jobs, args.timeout, args.cpu_limit = protocol["jobs"], protocol["timeout_seconds"], protocol["cpu_limit_seconds"]
    for origin, name in ((args.failure_stdout, "driver.stdout.txt"), (args.failure_stderr, "driver.stderr.txt")):
        destination = interrupted / name
        assert not destination.exists()
        shutil.copy2(origin, destination)
        assert identity(destination) == identity(origin)
    source = study.ROOT / "tests/verify_witness_interoperability.py"
    with (interrupted / "audit-source.py").open("xb") as stream:
        stream.write(source.read_bytes())
    study.dump(interrupted / "audit-binding.json", {"source": "audit-source.py", "source_identity": identity(source),
                                                    "report": "inherited-verification.json", "report_identity": identity(interrupted / "inherited-verification.json")})
    collected = read(root / "continuation-completed-before-failure.json")
    study.dump(interrupted / "termination.json", {
        "observed_process_exit_code": 1,
        "observed_exception": "ENOSPC during directory creation for original index572, before its native/compiler/validator calls.",
        "complete_case_records": len(inherited), "partial_case_directories": [],
        "rows_returned_to_collector": len(collected),
        "completed_during_thread_pool_shutdown": sorted(set(inherited) - {row["index"] for row in collected}),
        "native_compiler_attempts_added_by_this_resource_failure": 0,
        "directory_creation_attempt_count": "Not separately instrumented; no exact attempt count is inferred from the propagated exception.",
    })
    bound = {}
    for name in ("cases", "native-reconciliation", "resource-interruption"):
        bound.update(manifest(root / name, root))
    for name in ("protocol.json", "continuation-protocol.json", "continuation-completed-before-failure.json"):
        bound[name] = identity(root / name)
    snapshot = root / "resource-resume-sources" / "tests" / Path(__file__).name
    snapshot.parent.mkdir(parents=True)
    with snapshot.open("xb") as stream:
        stream.write(Path(__file__).read_bytes())
    source_identity = identity(Path(__file__))
    assert identity(snapshot) == source_identity
    phase = {
        "type": "Same-policy resume after resource interruption",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "original_protocol_identity": identity(root / "protocol.json"),
        "continuation_protocol_identity": identity(root / "continuation-protocol.json"),
        "initial_source_files": protocol["source_files"],
        "continuation_source": amendment["continuation_source"],
        "resume_source": {"path": "tests/" + Path(__file__).name, "identity": source_identity,
                          "snapshot": str(snapshot.relative_to(root))},
        "inherited_complete_indices": inherited, "pending_original_indices": pending,
        "partial_case_directories": [], "checkpoint_file_bindings": bound,
        "scientific_policy": "The compiler diagnostic policy, original inputs, emitted products, external executables/commands, arm rotation, concurrency and resource limits are unchanged from the registered continuation.",
        "native_policy": amendment["native_policy_after"],
    }
    study.dump(root / "resource-resume-protocol.json", phase)
    original_process = study.run_process

    def corrected_process(argv, cwd, prefix, timeout, env=None):
        command = list(argv)
        if prefix == "native-compile":
            assert command.count("-Werror") == 1
            command[command.index("-Werror")] = "-pedantic-errors"
        return original_process(command, cwd, prefix, timeout, env)

    study.run_process = corrected_process
    started = time.perf_counter()
    uniform_rows = read(root / "native-reconciliation/inherited.json")
    assert {row["index"] for row in uniform_rows} == initial
    for row in rows:
        if row["index"] not in initial:
            uniform_rows.append({"index": row["index"], "record_directory": f"cases/{row['index']:04d}",
                                 "phase": "continuation", **row["native_correspondence"]})
    environment = dict(os.environ)
    completed_new = 0
    print(json.dumps({"inherited_complete_subjects": len(inherited), "pending_subjects": len(pending)}), flush=True)
    with ThreadPoolExecutor(max_workers=args.jobs) as executor:
        futures = [executor.submit(study.check_case, index, protocol["requests"][index]["population"],
                                   study.ROOT / protocol["requests"][index]["path"], args, root, environment) for index in pending]
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
                study.dump(root / "resource-resume-completed-before-failure.json", sorted(rows, key=lambda row: row["index"]))
                raise
            if completed_new % 20 == 0 or len(rows) == 804:
                study.dump(root / "resource-resume-progress.json", {"completed_indices": sorted(row["index"] for row in rows),
                                                                    "completed_new_subjects": completed_new, "planned_requests": 804})
                print(json.dumps({"complete_subjects": len(rows), "resumed_subjects": completed_new, "planned_requests": 804}), flush=True)
    rows.sort(key=lambda row: row["index"])
    assert [row["index"] for row in rows] == list(range(804))
    study.dump(root / "cases.json", rows)
    controls = study.run_controls(rows, args, root)
    uniform_rows.sort(key=lambda row: row["index"])
    assert [row["index"] for row in uniform_rows] == list(range(804))
    study.dump(root / "native-reconciliation/records.json", uniform_rows)
    study.dump(root / "native-reconciliation/summary.json", {"outcome": "PASS_UNIFORM_NATIVE_POLICY", "requests": 804,
               "actual_corrected_policy_compilations": 804, "native_points": sum(row["points"] for row in uniform_rows),
               "native_mismatches": 0, "compiler_policy": amendment["native_policy_after"]})
    summary = study.summarize(rows, controls)
    flags = {
        "original_source_bindings_unchanged": unchanged(protocol["source_files"], study.ROOT),
        "original_input_bindings_unchanged": unchanged(inputs, study.ROOT),
        "original_tool_bindings_unchanged": unchanged(protocol["external_tool_files"], Path("/")),
        "inherited_observations_unchanged": unchanged(amendment["inherited_file_bindings"], root),
        "interruption_records_unchanged": unchanged(amendment["interruption_file_bindings"], root),
        "continuation_source_unchanged": identity(Path(previous.__file__)) == identity(root / amendment["continuation_source"]["snapshot"]) == amendment["continuation_source"]["identity"],
        "resource_checkpoint_unchanged": unchanged(bound, root),
        "resource_resume_source_unchanged": identity(Path(__file__)) == identity(snapshot) == source_identity,
    }
    summary["source_inputs_and_tools_unchanged"] = all(flags.values())
    native_receipts = [path for name in ("cases", "native-reconciliation/cases", "interruption/cases", "resource-interruption/cases")
                       for path in (root / name).rglob("native-compile.invocation.json")]
    summary["execution"] = {
        "mode": "Interrupted invocation followed by an explicitly registered continuation",
        "complete_subjects": 804, "initial_completed_subjects": len(initial),
        "continuation_completed_subjects": 804 - len(initial),
        "first_continuation_completed_subjects": len(inherited) - len(initial),
        "resource_resume_completed_subjects": len(pending),
        "initial_failed_native_attempts": len(amendment["failed_native_indices"]),
        "actual_native_compilation_attempts": len(native_receipts),
        "native_attempt_accounting_basis": "Distinct retained native-compile.invocation.json receipts; the observed directory-creation failure reached no compiler call.",
        "successful_corrected_policy_native_compilations": 804,
        "compiler_diagnostic_interruptions": 1, "resource_interruptions": 1,
        "native_reconciliation": "native-reconciliation/summary.json",
        "continuation_protocol": "continuation-protocol.json", "resource_resume_protocol": "resource-resume-protocol.json",
        "interruption": "interruption/termination.json", "resource_interruption": "resource-interruption/termination.json",
        **flags, "completion_segment_wall_seconds": time.perf_counter() - started,
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

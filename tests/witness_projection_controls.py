#!/usr/bin/env python3
"""Test that a projected witness cannot bypass the product's input domain.

The first refuted request of each population is chosen by the study's original
order.  Its first input constraint is replaced by a value outside the domain.
The remaining input constraints, source and property are retained.  Native
execution checks the resulting early return; the external validator receives
the altered standard witness.
"""
from __future__ import annotations

import argparse
import ctypes
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

if not __debug__:
    raise SystemExit("Witness projection controls require assertions enabled; -O and -OO are rejected.")

import witness_interoperability as study


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--cpachecker", type=Path, required=True)
    parser.add_argument("--gcc", type=Path, default=Path("/usr/bin/gcc"))
    parser.add_argument("--cpu-limit", type=int, default=30)
    parser.add_argument("--timeout", type=float, default=45)
    args = parser.parse_args()
    for name in ("study", "output", "cpachecker", "gcc"):
        setattr(args, name, getattr(args, name).resolve())
    if args.output.exists():
        parser.error("output must be new")
    summary = json.loads((args.study / "summary.json").read_text())
    assert summary["outcome"] == "COMPLETE_WITH_RECORDED_EXTERNAL_OUTCOMES"
    assert summary["source_inputs_and_tools_unchanged"] is True
    assert summary["control_runs"] == 18
    cases = json.loads((args.study / "cases.json").read_text())
    assert len(cases) == 804
    assert [case["index"] for case in cases] == list(range(804))
    selected = {}
    for case in cases:
        if case["receiver_status"] == "REFUTED":
            selected.setdefault(case["population"], case)
    assert set(selected) == {"core", "grammar", "natural"}
    registered = json.loads((args.study / "protocol.json").read_text())
    external_bindings = registered["external_tool_files"]
    assert all(study.content_identity(Path(name)) == binding for name, binding in external_bindings.items())
    expected_input_command = [str(args.cpachecker), "--heap", "768M", "--32", "--stats", "--no-output-files",
                              "--timelimit", f"{args.cpu_limit}s", "--output-path", "input-output",
                              "--spec", "property.prp", "--witnessValidation", "--witness", "input.graphml", "program.c"]
    original_invocations = {}
    for population, case in selected.items():
        result = case["arms"].get("input", {})
        if "argv" in result:
            assert result["argv"] == expected_input_command, "the control must use the preselected input arm's receiver configuration"
            assert result["wall_limit_seconds"] == args.timeout
            original_invocations[population] = result
    files = [Path(__file__).resolve(), Path(study.__file__).resolve(), args.cpachecker, args.gcc]
    names = ("program.c", "native-wrapper.c", "property.prp", "request.json", "input-projection.json", "input.graphml")
    for case in selected.values():
        source = args.study / "cases" / f"{case['index']:04d}"
        files += [source / name for name in names if (source / name).is_file()]
        files += [source / name for name in ("input.invocation.json", "input-result.json") if (source / name).is_file()]
    bound = {str(path): study.content_identity(path) for path in files}
    bound.update(external_bindings)
    args.output.mkdir(parents=True)
    study.dump(args.output / "protocol.json", {
        "analysis": "Secondary input-constraint consumption controls",
        "selection": "First receiver-refuted request in each original population, without filtering by validator outcome.",
        "planned_controls": 3,
        "mutation": "Replace only the first projected input value with the smallest nonnegative value outside that input domain.",
        "expected_native_result": "No error: the product returns at its first input-membership check.",
        "expected_validator_result": "TRUE under the constrained violation-validation task, hence UNCONFIRMED witness; this is not an unrestricted safety proof.",
        "selected": {population: case["index"] for population, case in selected.items()},
        "source_input_and_executable_files": bound,
        "registered_external_tool_files": external_bindings,
        "receiving_configuration_basis": "The same preselected input-arm command and wall cutoff; only output directory and witness filename differ.",
        "preselected_input_invocations": original_invocations,
        "timeout_seconds": args.timeout,
        "cpu_limit_seconds": args.cpu_limit,
    })
    rows = []
    for population, case in selected.items():
        source = args.study / "cases" / f"{case['index']:04d}"
        directory = args.output / population
        directory.mkdir()
        if not (source / "input.graphml").is_file():
            rows.append({"population": population, "case": case["index"], "outcome": "NOT_RUN",
                         "reason": "the preselected case has no producer input projection"})
            continue
        for name in names:
            shutil.copy2(source / name, directory / name)
            assert study.content_identity(directory / name) == bound[str(source / name)]
        request = json.loads((directory / "request.json").read_text())
        projection = json.loads((directory / "input-projection.json").read_text())
        point = list(projection["values"])
        name = projection["input_order"][0]
        excluded = 0
        while excluded in request["inputs"][name]:
            excluded += 1
        original = point[0]
        point[0] = excluded
        tree = ET.parse(directory / "input.graphml")
        first = tree.getroot().find("g:graph/g:edge", study.NS)
        value = first.find("g:data[@key='assumption']", study.NS)
        assert value.text == f"\\result == {original}u;"
        value.text = f"\\result == {excluded}u;"
        study.save_tree(tree, directory / "excluded-input.graphml")
        record, output = study.run_process([args.gcc, "-std=c11", "-O0", "-fPIC", "-shared", "-pedantic-errors",
                                            "native-wrapper.c", "-o", "native-control.so"],
                                           directory, "native-compile", 30)
        if record["exit_code"] != 0:
            raise RuntimeError(output)
        library = ctypes.CDLL(str(directory / "native-control.so"))
        function = library.repairseal_point
        function.argtypes = [ctypes.POINTER(ctypes.c_uint), ctypes.c_uint]
        function.restype = ctypes.c_int
        observed = function((ctypes.c_uint * len(point))(*point), len(point))
        (directory / "native-control.so").unlink()
        if observed != 0:
            raise AssertionError("native product did not reject the out-of-domain input before the error")
        result = study.cpa_run(args, directory, "excluded-input", "violation_witness", "excluded-input.graphml")
        expected_control_command = list(expected_input_command)
        expected_control_command[expected_control_command.index("--output-path") + 1] = "excluded-input-output"
        expected_control_command[expected_control_command.index("--witness") + 1] = "excluded-input.graphml"
        assert result["argv"] == expected_control_command and result["wall_limit_seconds"] == original_invocations[population]["wall_limit_seconds"]
        row = {"population": population, "case": case["index"], "request_id": case["request_id"],
               "changed_input": name, "before": original, "after": excluded,
               "full_input": point, "first_initializer_line": projection["source_lines"][0],
               "native_error_flag": observed, "validator": result,
               "outcome": "EXPECTED_UNCONFIRMED" if result["outcome"] == "UNCONFIRMED" else "OTHER_OBSERVED_OUTCOME"}
        study.dump(directory / "control-summary.json", row)
        rows.append(row)
    result = {"planned_controls": 3, "actual_native_executions": sum("native_error_flag" in row for row in rows),
              "actual_validator_runs": sum("validator" in row for row in rows),
              "expected_unconfirmed": sum(row["outcome"] == "EXPECTED_UNCONFIRMED" for row in rows),
              "source_inputs_and_executables_unchanged": all(study.content_identity(Path(name)) == binding for name, binding in bound.items()),
              "controls": rows}
    result["outcome"] = ("PASS_INPUT_CONSTRAINT_CONTROLS"
                         if result["expected_unconfirmed"] == 3 and result["source_inputs_and_executables_unchanged"]
                         else "INCOMPLETE_OR_UNEXPECTED_CONTROL_OUTCOME")
    study.dump(args.output / "summary.json", result)
    print(json.dumps(result, indent=2))
    if result["outcome"] != "PASS_INPUT_CONSTRAINT_CONTROLS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()

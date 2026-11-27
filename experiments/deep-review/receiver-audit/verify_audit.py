#!/usr/bin/env python3
"""Verify and recompute the retained admission audit without a compiler or ZIP.

Fresh work covers source admission, concrete interpretations and receiver
decisions. Native subprocess outputs and the original-archive source census
are hash-bound retained observations, not freshly rerun external experiments.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def sha_file(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def read(path):
    return json.loads(path.read_text())


def require(condition, reason):
    if not condition:
        raise AssertionError(reason)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def verify(audit_dir=HERE):
    """Return a truthful PASS receipt or raise on any binding/result mismatch."""
    audit_dir = Path(audit_dir).resolve()
    root = audit_dir.parents[2]
    manifest = read(audit_dir / "audit-manifest.json")
    require(manifest["schema"] == "repairseal-source-attribute-audit-manifest-v1", "manifest schema")
    require(len(manifest["files"]) == len(set(manifest["files"])), "manifest duplicate path")
    for name, expected in manifest["files"].items():
        target = (root / name).resolve()
        require(target.is_relative_to(root), "manifest path escapes artifact")
        require(sha_file(target) == expected, "changed audit file: " + name)
    versions = read(audit_dir / "source-versions.json")
    names = [row["module"] for row in versions["modules"]]
    require(len(names) == len(set(names)), "duplicate source module")
    require(set(names) == {p.name for p in (root / "src").glob("*.py")}
            == {p.name for p in (root / "current/src").glob("*.py")}, "source inventory changed")
    for row in versions["modules"]:
        old_hash = sha_file(root / "src" / row["module"])
        current_hash = sha_file(root / "current/src" / row["module"])
        require(old_hash == row["historical_sha256"] == row["original_archive_sha256"], "historical source changed")
        require(current_hash == row["current_sha256"], "current source changed")
        require(row["historical_byte_exact"] is True and row["changed"] == (old_hash != current_hash), "source version flags")
    require(versions["all_historical_modules_byte_exact"] is True
            and versions["changed_modules"] == ["codeflaws_int32_bridge.py"], "source version summary")
    environment = read(audit_dir / "run/environment.json")
    paths = {"current_bridge": root / "current/src/codeflaws_int32_bridge.py",
             "legacy_bridge": audit_dir / "preimage/codeflaws_int32_bridge.py",
             "audit_driver": audit_dir / "run_audit.py",
             "control_tests": root / "tests/test_source_attribute_admission.py",
             "int32_circuit": root / "src/int32_circuit.py",
             "int32_refutation": root / "src/int32_refutation.py"}
    require(environment["source_bindings"] == {k: sha_file(p) for k, p in paths.items()}, "run source bindings")
    require(sha_file(paths["legacy_bridge"]) == sha_file(root / "src/codeflaws_int32_bridge.py"), "preimage differs from historical source")
    sys.path[:0] = [str(root / "src"), str(root / "tests")]
    driver = load("repairseal_attribute_audit_recompute", audit_dir / "run_audit.py")
    old = load("repairseal_attribute_audit_legacy", paths["legacy_bridge"])
    current = load("repairseal_attribute_audit_current", paths["current_bridge"])
    controls = load("repairseal_attribute_audit_controls", paths["control_tests"])
    import int32_circuit as signed
    rows = read(audit_dir / "run/controls.json")
    summary = read(audit_dir / "run/summary.json")
    require([row["id"] for row in rows] == list(controls.CASES), "control selection/order changed")
    fresh_old_decisions = fresh_current_decisions = fresh_current_rejections = fresh_output_checks = 0
    for row in rows:
        name = row["id"]
        control = controls.CASES[name]
        raw = control["source"]
        require(row["source"].encode() == raw and row["source_sha256"] == driver.digest(raw), "control source identity")
        require(row["expected_admitted"] is control["admitted"], "control expectation changed")
        before, admitted = driver.admission(old, raw, name)
        after, current_admitted = driver.admission(current, raw, name)
        recorded_before = {k: v for k, v in row["before"].items()
                           if k not in ("concrete_at_seven", "direct_status", "full_status")}
        require(before == recorded_before and after == row["after"], "admission replay changed: " + name)
        require(row["expectation_met"] is True and after["admitted"] is control["admitted"], "admission expectation")
        if not control["admitted"]:
            require(after["code"] == control["code"], "rejection diagnostic")
        require(admitted is not None, "audit precondition: historically admitted control")
        require(old.evaluate(admitted, [7]).as_dict() == row["before"]["concrete_at_seven"], "legacy concrete observation")
        request = {"kind": signed.PROFILE, "id": "old-source-attribute-" + name,
                   "policy": "reference-everywhere", "points": [[7]],
                   "sources": dict.fromkeys(("original", "candidate", "reference"), raw.decode())}
        with patch.dict(sys.modules, {"codeflaws_int32_bridge": old}):
            packet = signed.make_evidence(request)
            for kind, result in (("direct_status", signed.evaluate_direct(request)),
                                 ("full_status", signed.verify_evidence(request, packet))):
                require(result["status"] == row["before"][kind] == "ACCEPT", "legacy semantic decision")
                fresh_old_decisions += 1
        with patch.dict(sys.modules, {"codeflaws_int32_bridge": current}):
            for invoke in (lambda: signed.evaluate_direct(request), lambda: signed.verify_evidence(request, packet)):
                if current_admitted is not None:
                    require(invoke()["status"] == "ACCEPT", "current positive decision")
                    fresh_current_decisions += 1
                else:
                    try:
                        invoke()
                    except current.UnsupportedSource as exc:
                        require(exc.code == control["code"], "current receiver rejection diagnostic")
                        fresh_current_rejections += 1
                    else:
                        raise AssertionError("unsupported source reached current semantic decision")
        syntax = row["syntax_check"]
        require(syntax["command"] == [environment["compiler"]["path"], "-std=c11", "-fsyntax-only", "-x", "c", "-"]
                and syntax["input_utf8"] == raw.decode() and type(syntax["returncode"]) is int, "retained compiler input/command")
        if control["admitted"]:
            require(row["native_compilation"]["returncode"] == 0 and syntax["returncode"] == 0, "positive compilation receipt")
            observations = row["native_observations"]
            require([o["point"] for o in observations] == [[v] for v in (current.INT_MIN, -1, 0, 1, current.INT_MAX)], "native control points")
            for observation in observations:
                concrete = current.evaluate(current_admitted, observation["point"])
                symbolic = signed.evaluate_program(current_admitted, observation["point"])
                process = observation["process"]
                require(process["returncode"] == 0 and observation["matches_identity"] is True, "native observation result")
                require(concrete.defined and symbolic["defined"] and concrete.value == symbolic["value"]
                        == process["stdout"].strip() == str(observation["point"][0]), "fresh model / retained native agreement")
                fresh_output_checks += 1
    negative = [r for r in rows if not r["expected_admitted"]]
    derived = {"controls": len(rows), "negative_controls": len(negative),
               "preimage_admitted_negative_controls": sum(r["before"]["admitted"] for r in negative),
               "native_rejected_negative_controls": sum(r["syntax_check"]["returncode"] != 0 for r in negative),
               "preimage_false_acceptances_for_native_rejected_controls": sum(
                   r["syntax_check"]["returncode"] != 0 and r["before"]["direct_status"] == "ACCEPT"
                   and r["before"]["full_status"] == "ACCEPT" for r in negative),
               "current_rejected_negative_controls": sum(not r["after"]["admitted"] for r in negative),
               "positive_controls": sum(r["expected_admitted"] for r in rows),
               "native_positive_observations": sum(len(r.get("native_observations", [])) for r in rows),
               "all_control_expectations_met": all(r["expectation_met"] for r in rows),
               "all_native_positive_observations_match": all(o["matches_identity"] for r in rows for o in r.get("native_observations", []))}
    require(all(summary[k] == v for k, v in derived.items()) and summary["status"] == "PASS", "audit summary counts/status")
    census = read(audit_dir / "run/retained-source-census.json")
    census_rows = census["rows"]
    require(len(census_rows) == census["unique_sources"] == len({r["source_sha256"] for r in census_rows}), "census denominator")
    require(sum(r["occurrences"] for r in census_rows) == census["source_occurrences"], "census occurrences")
    require(sum(r["before"]["admitted"] for r in census_rows) == census["admitted_unique_sources"], "census admitted sources")
    require(all(r["identical"] is True and r["before"] == r["after"] for r in census_rows)
            and census["same_admission_and_ast"] == len(census_rows) and not census["changed_sources"], "retained census results")
    require(summary["retained_source_census"] == {k: v for k, v in census.items() if k != "rows"}, "census summary")
    return {"status": "PASS_SOURCE_ATTRIBUTE_AUDIT_OFFLINE", "bound_files": len(manifest["files"]),
            "historical_modules_preserved": len(names), "changed_current_modules": versions["changed_modules"],
            "control_sources_recomputed": len(rows), "fresh_legacy_receiver_decisions": fresh_old_decisions,
            "fresh_current_positive_decisions": fresh_current_decisions,
            "fresh_current_unsupported_rejections": fresh_current_rejections,
            "fresh_model_to_retained_native_output_checks": fresh_output_checks,
            "counts": derived,
            "retained_census_unique_sources": len(census_rows),
            "native_executions_rerun": 0, "archive_census_rerun": False,
            "scope": "Fresh source admission and model/receiver computation; native receipts and original ZIP census verified as retained evidence only."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit-dir", type=Path, default=HERE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify(args.audit_dir)
    text = json.dumps(result, sort_keys=True, indent=2) + "\n"
    if args.output:
        with args.output.open("x") as stream:
            stream.write(text)
    print(text, end="")


if __name__ == "__main__":
    main()

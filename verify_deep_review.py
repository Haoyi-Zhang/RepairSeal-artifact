#!/usr/bin/env python3
"""Verify the new review studies with isolated, version-explicit processes.

Native receipts are checked, not re-executed. --historical also reruns the
unchanged 203-check historical gate. Every output directory must be new.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
REVIEW = ROOT / "experiments/deep-review"


def read(path):
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("duplicate JSON field: " + key)
            value[key] = item
        return value
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def require(value, message):
    if not value:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--historical", action="store_true")
    parser.add_argument("--checks-only", action="store_true", help="Skip unit-test processes; recheck all new study evidence.")
    args = parser.parse_args()
    if not __debug__:
        parser.error("run with assertions enabled, without -O")
    output = args.output.resolve()
    if output.exists():
        parser.error("choose a new output directory; prior records are never overwritten")
    output.mkdir(parents=True)
    records = []
    result = {"schema": "repairseal-deep-review-gate-v1", "status": "FAIL",
              "started_utc": datetime.now(timezone.utc).isoformat(),
              "python": sys.version, "historical_requested": args.historical,
              "unit_tests_requested": not args.checks_only, "phases": records,
              "fresh_native_executions": 0,
              "scope": "Fresh local semantic/reduction and optional unit checks; native compiler outputs remain retained receipts."}

    def run(name, command, timeout=300, tests=None):
        started = datetime.now(timezone.utc).isoformat()
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                                   timeout=timeout, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        (output / (name + ".stdout.log")).write_text(completed.stdout)
        (output / (name + ".stderr.log")).write_text(completed.stderr)
        row = {"name": name, "command": command, "returncode": completed.returncode,
               "started_utc": started, "status": "PASS" if completed.returncode == 0 else "FAIL"}
        if tests is not None:
            count = re.search(r"Ran (\d+) tests? in", completed.stderr)
            row["test_count"] = int(count.group(1)) if count else None
            row["expected_test_count"] = tests
            row["status"] = "PASS" if row["status"] == "PASS" and row["test_count"] == tests else "FAIL"
        records.append(row)
        require(row["status"] == "PASS", "failed phase: " + name)
        return completed

    try:
        expected = read(REVIEW / "expected.json")
        require(expected["schema"] == "repairseal-deep-review-expectations-v1", "expectation schema")
        for name, sha in expected["files"].items():
            target = (ROOT / name).resolve()
            require(target.is_relative_to(ROOT) and not target.is_symlink(), "unsafe binding")
            require(digest(target) == sha, "changed review input: " + name)
        records.append({"name": "exact-source-and-evidence-bindings", "status": "PASS",
                        "files": len(expected["files"])})
        py = [sys.executable, "-B"]
        native_audit = output / "admission.json"
        run("admission", py + [str(REVIEW / "receiver-audit/verify_audit.py"), "--output", str(native_audit)])
        require(read(native_audit)["status"] == "PASS_SOURCE_ATTRIBUTE_AUDIT_OFFLINE", "admission audit status")
        order = run("order-classes", py + [str(REVIEW / "real-validation/run.py"), "verify", "--data", str(REVIEW / "real-validation/records")])
        summary = json.loads(order.stdout)
        require(summary["status"] == "PASS", "order study status")
        for key, value in expected["order_fields"].items():
            require(type(summary[key]) is type(value) and summary[key] == value, "order field: " + key)
        independent = output / "independent-order.json"
        run("independent-order", py + [str(REVIEW / "research-audit/review_order_reduction.py"), "--output", str(independent)])
        reviewed = read(independent)
        require(reviewed == read(REVIEW / "research-audit/independent-order-review.json"), "independent order review replay")
        traces = output / "trace-order"
        run("trace-order", py + [str(REVIEW / "research-audit/trace_order_counterexample.py"), "--output", str(traces)])
        old = read(REVIEW / "research-audit/trace-order-results/summary.json")
        fresh = read(traces / "summary.json")
        require({k: v for k, v in old.items() if k != "environment"}
                == {k: v for k, v in fresh.items() if k != "environment"}, "trace-order semantic replay")
        if not args.checks_only:
            for name, pattern, count in (("admission-tests", "test_source_attribute_admission.py", 6),
                                         ("order-tests", "test_weak_order_validation.py", 17)):
                run(name, py + ["-m", "unittest", "discover", "-s", "tests", "-p", pattern, "-v"], tests=count)
            run("current-cli-tests", py + ["-m", "unittest", "discover", "-s", "current/tests", "-p", "test_*.py", "-v"], tests=4)
            code = ("import sys,unittest\n"
                    "sys.path[:0]=['current/src','tests']\n"
                    "import codeflaws_int32_bridge,int32_circuit,int32_refutation,proof_dag_checker\n"
                    "s=unittest.defaultTestLoader.loadTestsFromNames(['test_codeflaws_int32_bridge','test_int32_circuit',"
                    "'test_int32_refutation','test_codeflaws_header_admission','test_codeflaws_diagnostic_determinism'])\n"
                    "r=unittest.TextTestRunner(verbosity=2).run(s)\nraise SystemExit(not r.wasSuccessful())\n")
            run("current-compatibility-tests", py + ["-c", code], tests=43)
        if args.historical:
            directory = output / "historical-203"
            run("historical-203", py + [str(ROOT / "verify_expected_results.py"), "--output", str(directory)], timeout=900)
            historical = read(directory / "result.json")
            require(historical["status"] == "PASS_KEY_RESULT_SOURCE_TRACE" and historical["checks"] == 203
                    and not historical["failures"], "historical named result checks")
        result["status"] = "PASS_DEEP_REVIEW"
    except (AssertionError, ValueError, KeyError, TypeError, OSError, subprocess.TimeoutExpired) as exc:
        result["error"] = type(exc).__name__ + ": " + str(exc)
    result["completed_utc"] = datetime.now(timezone.utc).isoformat()
    result["unit_tests_run"] = sum(row.get("test_count") or 0 for row in records)
    (output / "result.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"status": result["status"], "phases": len(records), "unit_tests": result["unit_tests_run"],
                      "error": result.get("error"), "output": str(output)}))
    return 0 if result["status"] == "PASS_DEEP_REVIEW" else 1


if __name__ == "__main__":
    raise SystemExit(main())

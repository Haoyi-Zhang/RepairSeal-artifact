#!/usr/bin/env python3
"""Run the revised signed receiver without changing historical evidence.

This entry point imports only current/src. The legacy artifact/src is retained
for the exact, hash-bound historical studies, not silently substituted here.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "src"))
import codeflaws_int32_bridge as bridge
import int32_circuit as signed
import int32_refutation as compact
import proof_dag_checker as core

REVISION = "repairseal-reviewed-admission-20261127"
SCHEMA = "repairseal-current-execution-v1"


def implementation_identity():
    paths = [Path(__file__), *sorted((HERE / "src").glob("*.py"))]
    return {p.relative_to(HERE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths}


def read_evidence(path):
    value = core.load_json_file(path)
    if type(value) is dict and value.get("schema") == SCHEMA:
        if "evidence" not in value:
            raise core.Invalid("execution envelope contains no evidence")
        return value["evidence"]
    return value


def execute(operation, request, evidence=None, algorithm="demand"):
    if operation == "decide":
        result = (signed.evaluate_direct(request) if algorithm == "demand"
                  else signed.evaluate_with_record(request)[0])
        return {"result": result}
    if operation == "produce-record":
        result, packet = signed.evaluate_with_record(request)
        return {"result": result, "evidence": packet}
    if operation == "check-record":
        return {"result": signed.verify_evidence(request, evidence)}
    if operation == "produce-refutation":
        certificate = compact.produce(request)
        return {"result": compact.check(request, certificate), "evidence": certificate}
    if operation == "check-refutation":
        return {"result": compact.check(request, evidence)}
    raise core.Invalid("unknown operation")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["decide", "produce-record", "check-record",
                                              "produce-refutation", "check-refutation"])
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--algorithm", choices=["demand", "materialized"], default="demand")
    parser.add_argument("--output", type=Path, help="New output file; existing files are never overwritten.")
    args = parser.parse_args(argv)
    checking = args.operation.startswith("check-")
    if checking != (args.evidence is not None):
        parser.error("--evidence is required exactly for check-record and check-refutation")
    if args.algorithm != "demand" and args.operation != "decide":
        parser.error("--algorithm applies only to decide")
    envelope = {"schema": SCHEMA, "revision": REVISION,
                "implementation": implementation_identity(), "operation": args.operation}
    code = 0
    try:
        request = core.load_json_file(args.request)
        evidence = read_evidence(args.evidence) if checking else None
        envelope.update(execute(args.operation, request, evidence, args.algorithm))
        envelope["request_sha256"] = signed.task_identity(request)
    except (bridge.UnsupportedSource, core.Unsupported) as exc:
        envelope["result"] = {"status": "UNSUPPORTED", "reason": str(exc)}
        code = 3
    except (core.Invalid, bridge.InvalidInput, OSError, UnicodeError, ValueError,
            RecursionError) as exc:
        envelope["result"] = {"status": "INVALID", "reason": str(exc)}
        code = 2
    payload = json.dumps(envelope, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        try:
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(payload)
        except OSError as exc:
            print(json.dumps({"status": "OUTPUT_ERROR", "reason": str(exc)}), file=sys.stderr)
            return 2
    else:
        sys.stdout.write(payload)
    return code


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Reproduce the source-attribute admission audit without rewriting old records.

Only the owned controls in test_source_attribute_admission.py are compiled.
An optional original delivery ZIP supplies a parser-only compatibility census:
its retained .c members are read, deduplicated and never compiled or executed.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
from unittest.mock import patch
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      separators=(",", ":"), allow_nan=False).encode()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def admission(module, raw, name):
    try:
        admitted = module.admit_source(raw, name)
    except module.UnsupportedSource as exc:
        return {"admitted": False, "code": exc.code}, None
    tree = io.StringIO()
    admitted.tree.show(buf=tree, showcoord=False)
    return {"admitted": True, "source_sha256": admitted.source_sha256,
            "ast_sha256": digest(tree.getvalue().encode()),
            "input_names": list(admitted.input_names),
            "input_targets": list(admitted.input_targets),
            "output_kind": admitted.output_kind,
            "output_labels": list(admitted.output_labels),
            "ast_nodes": admitted.ast_nodes}, admitted


def execute(command, stdin=b"", timeout=10):
    completed = subprocess.run(command, input=stdin, capture_output=True,
                               timeout=timeout, check=False)
    return {"command": command, "input_utf8": stdin.decode(),
            "returncode": completed.returncode,
            "stdout": completed.stdout.decode(errors="replace"),
            "stderr": completed.stderr.decode(errors="replace")}


def archive_census(path, old, current):
    sources = {}
    source_occurrences = 0
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            if not info.filename.startswith("RepairSeal_TOSEM/artifact/") or not info.filename.endswith(".c"):
                continue
            raw = archive.read(info)
            source_occurrences += 1
            sha = digest(raw)
            if sha not in sources:
                sources[sha] = {"raw": raw, "member": info.filename, "occurrences": 0}
            sources[sha]["occurrences"] += 1
    rows = []
    for sha, source in sorted(sources.items()):
        before, _ = admission(old, source["raw"], source["member"])
        after, _ = admission(current, source["raw"], source["member"])
        rows.append({"source_sha256": sha, "representative_member": source["member"],
                     "occurrences": source["occurrences"],
                     "before": before, "after": after, "identical": before == after})
    return {"schema": "repairseal-retained-c-admission-census-v1",
            "selection": "Every .c member below RepairSeal_TOSEM/artifact/ in the supplied original ZIP; byte-deduplicated; parser-only, no compilation or execution",
            "archive_sha256": digest(path.read_bytes()),
            "source_occurrences": source_occurrences, "unique_sources": len(sources),
            "admitted_unique_sources": sum(r["before"]["admitted"] for r in rows),
            "same_admission_and_ast": sum(r["identical"] for r in rows),
            "changed_sources": [r["source_sha256"] for r in rows if not r["identical"]],
            "scope_limit": "External Codeflaws originals absent from the delivery are not covered. Equality of admission/AST is not a fresh native execution or full experiment rerun.",
            "rows": rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--bridge", type=Path, default=ROOT / "current/src/codeflaws_int32_bridge.py")
    parser.add_argument("--preimage", type=Path, default=HERE / "preimage/codeflaws_int32_bridge.py")
    parser.add_argument("--compiler", default="gcc")
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        raise ValueError("output must be a new directory; historical receipts are not overwritten")
    output.mkdir(parents=True)
    current = load("codeflaws_int32_bridge", args.bridge.resolve())
    old = load("repairseal_bridge_preimage", args.preimage.resolve())
    import int32_circuit as signed
    import int32_refutation as compact
    import test_source_attribute_admission as controls
    compiler = shutil.which(args.compiler)
    if compiler is None:
        raise ValueError("compiler is unavailable: " + args.compiler)
    compiler = str(Path(compiler).resolve())
    environment = {"started_at_utc": datetime.now(timezone.utc).isoformat(),
                   "python": sys.version, "platform": platform.platform(),
                   "pycparser": __import__("pycparser").__version__,
                   "compiler": {"path": compiler, "sha256": digest(Path(compiler).read_bytes()),
                                "version": execute([compiler, "--version"])},
                   "source_bindings": {"current_bridge": digest(args.bridge.read_bytes()),
                                       "legacy_bridge": digest(args.preimage.read_bytes()),
                                       "audit_driver": digest(Path(__file__).read_bytes()),
                                       "control_tests": digest((ROOT / "tests/test_source_attribute_admission.py").read_bytes()),
                                       "int32_circuit": digest((ROOT / "src/int32_circuit.py").read_bytes()),
                                       "int32_refutation": digest((ROOT / "src/int32_refutation.py").read_bytes())}}
    rows = []
    for name, control in controls.CASES.items():
        raw = control["source"]
        before, admitted = admission(old, raw, name)
        after, _ = admission(current, raw, name)
        row = {"id": name, "source": raw.decode(), "source_sha256": digest(raw),
               "expected_admitted": control["admitted"], "before": before, "after": after}
        row["syntax_check"] = execute([compiler, "-std=c11", "-fsyntax-only", "-x", "c", "-"], raw)
        if admitted is not None:
            row["before"]["concrete_at_seven"] = old.evaluate(admitted, [7]).as_dict()
            request = {"kind": signed.PROFILE, "id": "old-source-attribute-" + name,
                       "policy": "reference-everywhere", "points": [[7]],
                       "sources": dict.fromkeys(("original", "candidate", "reference"), raw.decode())}
            # The symbolic module obtains admission through this named module.
            with patch.dict(sys.modules, {"codeflaws_int32_bridge": old}):
                packet = signed.make_evidence(request)
                row["before"]["direct_status"] = signed.evaluate_direct(request)["status"]
                row["before"]["full_status"] = signed.verify_evidence(request, packet)["status"]
        row["expectation_met"] = after["admitted"] == control["admitted"] and (
            control["admitted"] or after["code"] == control["code"])
        if control["admitted"]:
            row["native_observations"] = []
            with tempfile.TemporaryDirectory(prefix="repairseal-attribute-control-") as directory:
                source_path, binary_path = Path(directory) / "control.c", Path(directory) / "control"
                source_path.write_bytes(raw)
                compilation = execute([compiler, "-std=c11", "-O2", str(source_path), "-o", str(binary_path)])
                row["native_compilation"] = compilation
                if compilation["returncode"] != 0:
                    raise AssertionError("positive control failed native compilation")
                for value in (current.INT_MIN, -1, 0, 1, current.INT_MAX):
                    process = execute([str(binary_path)], (str(value) + "\n").encode())
                    native = process["returncode"] == 0 and process["stdout"].strip() == str(value)
                    row["native_observations"].append({"point": [value], "process": process,
                                                       "matches_identity": native})
        rows.append(row)
    census = archive_census(args.archive, old, current) if args.archive else None
    if census:
        (output / "retained-source-census.json").write_bytes(canonical(census) + b"\n")
    negatives = [row for row in rows if not row["expected_admitted"]]
    summary = {"schema": "repairseal-source-attribute-audit-v1", "status": "PASS",
               "controls": len(rows), "negative_controls": len(negatives),
               "preimage_admitted_negative_controls": sum(r["before"]["admitted"] for r in negatives),
               "native_rejected_negative_controls": sum(r["syntax_check"]["returncode"] != 0 for r in negatives),
               "preimage_false_acceptances_for_native_rejected_controls": sum(
                   r["syntax_check"]["returncode"] != 0 and r["before"].get("direct_status") == "ACCEPT"
                   and r["before"].get("full_status") == "ACCEPT" for r in negatives),
               "current_rejected_negative_controls": sum(not r["after"]["admitted"] for r in negatives),
               "positive_controls": sum(r["expected_admitted"] for r in rows),
               "native_positive_observations": sum(len(r.get("native_observations", [])) for r in rows),
               "all_control_expectations_met": all(r["expectation_met"] for r in rows),
               "all_native_positive_observations_match": all(o["matches_identity"] for r in rows for o in r.get("native_observations", [])),
               "retained_source_census": {k: v for k, v in census.items() if k != "rows"} if census else None,
               "interpretation": "The old signed frontend could admit C constraint violations by ignoring declaration/signature attributes. The fixed profile rejects all alignment specifiers and qualified void signatures before any receiver decision. Valid alignment remains unsupported, not refuted.",
               "limits": ["One available native compiler; no Clang or external verifiers were run.",
                          "Owned adversarial controls are not real benchmark bug prevalence.",
                          "Original retained scientific receipts remain historical and are not rewritten."]}
    if not (summary["all_control_expectations_met"] and summary["all_native_positive_observations_match"]
            and (census is None or not census["changed_sources"])):
        summary["status"] = "FAIL"
    for name, content in (("environment.json", environment), ("controls.json", rows), ("summary.json", summary)):
        (output / name).write_bytes(canonical(content) + b"\n")
    print(json.dumps(summary, sort_keys=True))
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

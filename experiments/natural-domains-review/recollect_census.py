"""Recollect the entire fixed Codeflaws source/test census, without native runs.

The external source archive is checked in full and is not redistributed. This
fresh collection checks the data underlying the scope analysis independently of
the retained delivery files; the frontend implementation is intentionally the
same version. Native source correspondence is a separate experiment.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path[:0] = [str(ROOT / "tests"), str(ROOT / "src")]
import codeflaws_staged_study as study

COMPARED = ("archive-provenance.json", "source-admission.json", "test-admission.json",
            "normalized-corpus.json", "concrete-observations.json", "staged-requests.json")


def run(archive, output):
    if output.exists() or ROOT == output or ROOT in output.parents:
        raise ValueError("choose a new collection directory outside artifact")
    output.mkdir(parents=True)
    start = datetime.now(timezone.utc).isoformat()
    before = {name: study.file_sha256(ROOT / name) for name in (
        "src/codeflaws_int32_bridge.py", "tests/codeflaws_staged_study.py",
        "experiments/natural-domains-review/recollect_census.py")}
    *_rest, summary = study.run_inspection(archive, output)
    comparisons = []
    for name in COMPARED:
        fresh = output / name
        retained = ROOT / "data/source-programs" / name
        equal = json.loads(fresh.read_text()) == json.loads(retained.read_text())
        comparisons.append({"file": name, "json_equal": equal,
                            "fresh_sha256": study.file_sha256(fresh),
                            "retained_sha256": study.file_sha256(retained)})
    record = {"schema": "repairseal-fresh-census-recollection-v1",
              "status": "PASS" if all(r["json_equal"] for r in comparisons) else "FAIL",
              "started_at_utc": start, "completed_at_utc": datetime.now(timezone.utc).isoformat(),
              "python": sys.version, "platform": platform.platform(),
              "archive_sha256": study.ARCHIVE_SHA256, "archive_bytes": study.ARCHIVE_BYTES,
              "source_bindings": before, "comparisons": comparisons,
              "indexed_subjects": summary["indexed_subjects"],
              "indexed_source_occurrences": summary["indexed_source_occurrences"],
              "syntactically_admitted_source_occurrences": summary["syntactically_admitted_source_occurrences"],
              "compatible_syntactic_pairs": summary["compatible_syntactic_pairs"],
              "complete_io_subjects": summary["complete_io_subjects"],
              "all_defined_subjects": summary["all_defined_subjects"],
              "fresh_native_executions": 0,
              "scope": "Fresh whole-archive identity, source admission, test parsing and concrete interpretation. Same frontend version; no fresh native compilation or independent C semantics proof."}
    if before != {name: study.file_sha256(ROOT / name) for name in before}:
        raise ValueError("collector implementation changed during execution")
    study.save(output / "recollection.json", record)
    inventory = {p.name: study.file_sha256(p) for p in sorted(output.iterdir()) if p.is_file()}
    study.save(output / "manifest.json", {"files": inventory})
    print(json.dumps(record, indent=2))
    return 0 if record["status"] == "PASS" else 1


def verify(root=None, records=None):
    root = ROOT if root is None else Path(root)
    records = HERE / "fresh-census" if records is None else Path(records)
    errors = []; result = None
    try:
        inventory = json.loads((records / "manifest.json").read_text())["files"]
        actual = {p.name for p in records.iterdir() if p.is_file() and p.name != "manifest.json"}
        if actual != set(inventory):
            raise ValueError("census inventory completeness")
        for name, expected in inventory.items():
            if study.file_sha256(records / name) != expected:
                raise ValueError("census record hash: " + name)
        result = json.loads((records / "recollection.json").read_text())
        for name, expected in result["source_bindings"].items():
            if study.file_sha256(root / name) != expected:
                raise ValueError("census source hash: " + name)
        for comparison in result["comparisons"]:
            fresh = records / comparison["file"]
            retained = root / "data/source-programs" / comparison["file"]
            if (study.file_sha256(fresh) != comparison["fresh_sha256"]
                    or study.file_sha256(retained) != comparison["retained_sha256"]
                    or not comparison["json_equal"]
                    or json.loads(fresh.read_text()) != json.loads(retained.read_text())):
                raise ValueError("fresh versus retained census: " + comparison["file"])
        admission = json.loads((records / "source-admission.json").read_text())
        corpus = json.loads((records / "normalized-corpus.json").read_text())
        counts = {"indexed_subjects": len({r["subject"] for r in admission["rows"]}),
                  "indexed_source_occurrences": len(admission["rows"]),
                  "syntactically_admitted_source_occurrences": sum(r["admitted"] for r in admission["rows"]),
                  "compatible_syntactic_pairs": len(admission["compatible_pairs"]),
                  "complete_io_subjects": len(corpus["subjects"]),
                  "all_defined_subjects": sum(s["eligible"] for s in corpus["subjects"])}
        if any(result[key] != value for key, value in counts.items()) or result["status"] != "PASS":
            raise ValueError("census recollection count or outcome")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(str(exc))
    return {"status": "PASS" if not errors else "FAIL", "errors": errors, "recomputed": result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if args.verify:
        result = verify()
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            study.save(args.output, result)
        print(json.dumps({k: v for k, v in result.items() if k != "recomputed"}))
        return 0 if result["status"] == "PASS" else 1
    if args.archive is None or args.output is None:
        parser.error("--archive and --output are required for fresh collection")
    return run(args.archive.resolve(), args.output.resolve())


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Cross-check the revised signed frontend on every indexed Codeflaws source occurrence.

The retained-source compatibility census of this audit covers the C members shipped with
the package, but not the external Codeflaws originals behind the paper's admission funnel
(7,806 occurrences, 223 admitted). This driver reads every recorded member from the pinned
archive, runs the historical frontend (`src/`) and the revised frontend (`current/src/`) on the
exact bytes, and compares both with the retained `data/source-programs/source-admission.json`.

    run    --archive codeflaws.tar.gz --output NEW.json   (needs the pinned archive)
    verify [--record codeflaws-admission-crosscheck.json] (offline consistency of the record)

No source bytes are written; the record holds hashes, decisions, and AST fingerprints only.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys
import tarfile

HERE = Path(__file__).resolve().parent
ARTIFACT = HERE.parents[2]
RETAINED = ARTIFACT / "data/source-programs/source-admission.json"
HISTORICAL = ARTIFACT / "src/codeflaws_int32_bridge.py"
CURRENT = ARTIFACT / "current/src/codeflaws_int32_bridge.py"
RECORD = HERE / "codeflaws-admission-crosscheck.json"
ARCHIVE_SHA256 = "2673fc16fa05590c5c1171f5b633594713ae9207346a3d0ba4c4d8b2eea82b11"
ARCHIVE_BYTES = 265695532


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def file_digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_bridge(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def decision(bridge, raw: bytes, member: str) -> dict:
    try:
        admitted = bridge.admit_source(raw, member)
    except bridge.UnsupportedSource as exc:
        return {"admitted": False, "code": exc.code}
    shape = repr((admitted.input_names, admitted.input_targets, admitted.output_kind,
                  admitted.output_labels, admitted.headers, admitted.ast_nodes, admitted.tree))
    return {"admitted": True, "input_arity": admitted.input_arity, "output_kind": admitted.output_kind,
            "ast_nodes": admitted.ast_nodes, "admission_fingerprint": hashlib.sha256(shape.encode()).hexdigest()}


def summarize(rows: list[dict]) -> dict:
    occ = len(rows)
    hist = sum(r["historical"]["admitted"] for r in rows)
    cur = sum(r["current"]["admitted"] for r in rows)
    retained_match = sum(r["historical_matches_retained"] for r in rows)
    same = sum(r["historical"] == r["current"] for r in rows)
    changed = [r for r in rows if r["historical"] != r["current"]]
    return {"source_occurrences": occ, "distinct_source_sha256": len({r["sha256"] for r in rows}),
            "historical_admitted_occurrences": hist, "current_admitted_occurrences": cur,
            "historical_decisions_matching_retained_record": retained_match,
            "identical_historical_and_current_decisions": same,
            "changed_decisions": [{"member": r["member"], "historical": r["historical"], "current": r["current"]}
                                  for r in changed],
            "current_rejection_codes": dict(sorted(Counter(r["current"].get("code", "admitted")
                                                           for r in rows).items()))}


def run(archive: Path, output: Path) -> int:
    if output.exists():
        raise SystemExit("output exists; choose a new path")
    if archive.stat().st_size != ARCHIVE_BYTES or file_digest(archive) != ARCHIVE_SHA256:
        raise SystemExit("archive identity mismatch")
    historical, current = load_bridge("historical_bridge", HISTORICAL), load_bridge("current_bridge", CURRENT)
    retained = json.loads(RETAINED.read_text())["rows"]
    wanted = {r["member"] for r in retained}
    payloads = {}
    with tarfile.open(archive, "r:gz") as tar:
        for member in tar:
            if member.isfile() and member.name in wanted:
                payloads[member.name] = tar.extractfile(member).read()
    cache: dict[str, tuple[dict, dict]] = {}
    rows = []
    for r in retained:
        raw = payloads[r["member"]]
        sha = digest(raw)
        if sha not in cache:
            cache[sha] = (decision(historical, raw, r["member"]), decision(current, raw, r["member"]))
        hist, cur = cache[sha]
        expect = {"admitted": r["admitted"]}
        if r["admitted"]:
            expect.update(input_arity=r["input_arity"], output_kind=r["output_kind"], ast_nodes=r["ast_nodes"])
            got = {k: hist.get(k) for k in expect}
        else:
            expect["code"] = r["rejection"]["code"]
            got = {k: hist.get(k) for k in expect}
        rows.append({"member": r["member"], "role": r["role"], "sha256": sha,
                     "sha256_matches_retained": sha == r["sha256"], "historical": hist, "current": cur,
                     "historical_matches_retained": got == expect})
    summary = summarize(rows)
    ok = (summary["historical_decisions_matching_retained_record"] == len(rows)
          and all(r["sha256_matches_retained"] for r in rows)
          and summary["identical_historical_and_current_decisions"] == len(rows))
    record = {"schema": "repairseal-codeflaws-admission-crosscheck-v1",
              "status": "PASS_UNCHANGED_ADMISSION" if ok else "CHANGED_OR_MISMATCHED",
              "archive": {"sha256": ARCHIVE_SHA256, "bytes": ARCHIVE_BYTES, "redistributed": False},
              "implementations": {"historical": {"path": "src/codeflaws_int32_bridge.py", "sha256": file_digest(HISTORICAL)},
                                  "current": {"path": "current/src/codeflaws_int32_bridge.py", "sha256": file_digest(CURRENT)}},
              "retained_record": {"path": "data/source-programs/source-admission.json", "sha256": file_digest(RETAINED)},
              "driver_sha256": file_digest(Path(__file__)),
              "python": platform.python_version(),
              "summary": summary, "rows": rows,
              "scope": ("Source admission only, on the exact archived bytes of every indexed original and reference "
                        "occurrence; no compilation, execution, or request evaluation.")}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=1, sort_keys=False) + "\n")
    print(json.dumps({"status": record["status"], **{k: v for k, v in summary.items() if k != "changed_decisions"},
                      "changed": len(summary["changed_decisions"])}))
    return 0 if ok else 1


def verify(path: Path) -> int:
    record = json.loads(path.read_text())
    errors = []
    retained = json.loads(RETAINED.read_text())["rows"]
    if record["retained_record"]["sha256"] != file_digest(RETAINED):
        errors.append("retained admission record changed")
    for role, p in (("historical", HISTORICAL), ("current", CURRENT)):
        if record["implementations"][role]["sha256"] != file_digest(p):
            errors.append(role + " frontend changed since the cross-check")
    rows = record["rows"]
    if [(r["member"], r["role"]) for r in rows] != [(r["member"], r["role"]) for r in retained]:
        errors.append("row set differs from the retained admission record")
    if summarize(rows) != record["summary"]:
        errors.append("summary does not recompute from rows")
    for r, k in zip(rows, retained):
        if r["sha256"] != k["sha256"] or r["historical"]["admitted"] != k["admitted"]:
            errors.append("row disagrees with retained record: " + r["member"]); break
    expected_status = ("PASS_UNCHANGED_ADMISSION" if record["summary"]["identical_historical_and_current_decisions"]
                       == len(rows) and record["summary"]["historical_decisions_matching_retained_record"] == len(rows)
                       else "CHANGED_OR_MISMATCHED")
    if record["status"] != expected_status:
        errors.append("status does not follow from rows")
    result = {"status": "PASS_CROSSCHECK_RECORD" if not errors else "FAIL_CROSSCHECK_RECORD",
              "record_status": record["status"], "errors": errors}
    print(json.dumps(result))
    return 0 if not errors and record["status"] == "PASS_UNCHANGED_ADMISSION" else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="mode", required=True)
    r = sub.add_parser("run"); r.add_argument("--archive", type=Path, required=True); r.add_argument("--output", type=Path, required=True)
    v = sub.add_parser("verify"); v.add_argument("--record", type=Path, default=RECORD)
    args = parser.parse_args()
    return run(args.archive, args.output) if args.mode == "run" else verify(args.record)


if __name__ == "__main__":
    raise SystemExit(main())

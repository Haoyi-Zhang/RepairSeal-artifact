#!/usr/bin/env python3
"""Move completed final-gate evidence into the artifact and summarize exact logs.

This collector does not run or override a scientific check. It requires the
last run to have passed every requested gate, verifies its code bindings, and
checks the delivery paper directly against the originally supplied ZIP.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--attempt", type=Path, action="append", required=True,
                        help="Completed reports directory, in execution order")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source, archive, output = args.source.resolve(), args.archive.resolve(), args.output.resolve()
    attempts = [p.resolve() for p in args.attempt]
    if output.exists():
        raise SystemExit("Output already exists; previous evidence is preserved")
    runs = [read(p / "run.json") for p in attempts]
    final = runs[-1]
    gates = {s["name"]: s for s in final["steps"]}
    required = {"preflight", "smoke", "expected-results", "core", "paper", "audit-data-integrity"}
    if len(gates) != len(final["steps"]) or set(gates) != required:
        raise SystemExit("Final run does not contain exactly the six requested gates")
    if final["status"] != "PASS" or any(s["returncode"] != 0 or s["status"] != "PASS" for s in gates.values()):
        raise SystemExit("Final run is not successful; all failed run evidence is preserved")
    changes = [p for p, h in final["scientific_code_bindings"].items()
               if not (source / p).is_file() or digest(source / p) != h]
    if changes or digest(source / "artifact/expected-results.json") != final["expected_results_sha256"]:
        raise SystemExit("Source or expected-result bindings changed after final validation: " + repr(changes))

    old_paper = {}
    with zipfile.ZipFile(archive) as z:
        for info in z.infolist():
            parts = Path(info.filename).parts
            if not info.is_dir() and len(parts) > 2 and parts[:2] == ("RepairSeal_TOSEM", "paper"):
                old_paper[Path(*parts[2:]).as_posix()] = hashlib.sha256(z.read(info)).hexdigest()
    current_paper = {p.relative_to(source / "paper").as_posix(): digest(p)
                     for p in sorted((source / "paper").rglob("*")) if p.is_file()}
    if not old_paper or old_paper != current_paper or not final["source_paper_unchanged"]:
        raise SystemExit("Delivery paper does not exactly match the supplied original ZIP")

    reports = attempts[-1]
    evaluations = {mode: read(reports / mode / "evaluation.json") for mode in ("preflight", "smoke", "core", "paper")}
    smoke = next(s["test_summary"] for s in evaluations["smoke"]["steps"] if s["name"] == "smoke-tests")
    unit = next(s["test_summary"] for s in evaluations["core"]["steps"] if s["name"] == "complete-unit-suite")
    packaged = read(reports / "expected-results/result.json")
    fresh = read(reports / "core/fresh-key-result-trace/result.json")
    reproduction = read(reports / "core/fresh-core/reproduction.json")
    data_audit = read(reports / "audit-data-integrity.stdout.log")
    if packaged["failures"] or fresh["failures"] or data_audit["errors"]:
        raise SystemExit("A retained success conflicts with detailed check failures")
    paper_log = (reports / "paper/logs/paper-build.stdout.log").read_text(encoding="utf-8")
    paper_pages = {
        "main.pdf": int(re.findall(r"built main manuscript: (\d+) pages", paper_log)[-1]),
        "supplementary.pdf": int(re.findall(r"built supplementary material: (\d+) pages", paper_log)[-1]),
        "figure-atlas.pdf": int(re.findall(r'"pages": (\d+)', paper_log)[-1]),
    }
    inspection_path = reports / "paper/rebuilt-output-inspection.json"
    if inspection_path.is_file():
        inspection = read(inspection_path)
        expected_outputs = {name: {**row, "pages": paper_pages[name]}
                            for name, row in evaluations["paper"]["paper_outputs"].items()}
        if inspection["status"] != "PASS" or inspection["outputs"] != expected_outputs:
            raise SystemExit("Direct built-PDF inspection disagrees with the paper gate")
    final_folder = "attempt-" + str(len(attempts))
    summary = {
        "schema": "repairseal-final-validation-summary-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS",
        "interpretation": "The final complete run passes all six gates. Earlier failed attempts remain failures and are retained in full. This is not a fresh full external CBMC/CPAchecker campaign.",
        "final_attempt": final_folder,
        "final_run": final_folder + "/run.json",
        "attempts": [{"directory": "attempt-" + str(i), "status": r["status"],
                      "started_at_utc": r["started_at_utc"], "ended_at_utc": r["ended_at_utc"],
                      "gates": {s["name"]: {"status": s["status"], "returncode": s["returncode"]} for s in r["steps"]}}
                     for i, r in enumerate(runs, 1)],
        "gates": {name: {"status": row["status"], "returncode": row["returncode"],
                          "command": row["command"], "cwd": row["cwd"],
                          "elapsed_seconds": row["elapsed_seconds"],
                          "stdout": final_folder + "/" + row["stdout"],
                          "stderr": final_folder + "/" + row["stderr"]}
                  for name, row in gates.items()},
        "packaged_results": {"checks": packaged["checks"], "failures": packaged["failures"],
                             "status": packaged["status"], "receipt": final_folder + "/expected-results/result.json"},
        "fresh_core_results": {"checks": fresh["checks"], "failures": fresh["failures"],
                               "status": fresh["status"], "receipt": final_folder + "/core/fresh-key-result-trace/result.json"},
        "smoke_tests": smoke,
        "complete_unit_suite": unit,
        "core_steps": [{k: s[k] for k in ("name", "status", "returncode")}
                       for s in evaluations["core"]["steps"]],
        "fresh_scientific_stages": {s["name"]: {k: s[k] for k in ("status", "returncode", "elapsed_seconds") if k in s}
                                    for s in reproduction["steps"]
                                    if s["name"] in ("analysis", "functional", "demand", "headers")},
        "fresh_reproduction_outcome": reproduction["outcome"],
        "paper": {"build_isolation": final["paper_build_isolation"],
                  "delivery_files": len(old_paper), "delivery_matches_original_zip": True,
                  "unchanged_during_final_run": True, "integrity_receipt": "paper-original-integrity.json",
                  "rebuilt_outputs": {name: {**row, "pages": paper_pages[name]}
                                      for name, row in evaluations["paper"]["paper_outputs"].items()},
                  "direct_pdf_inspection": final_folder + "/paper/rebuilt-output-inspection.json" if inspection_path.is_file() else None,
                  "note": "Rebuilt PDFs are outputs in disposable copies, not replacements for the supplied paper."},
        "data_audit": data_audit,
        "scientific_code_unchanged_since_final_run": True,
        "expected_results_sha256": final["expected_results_sha256"],
        "retention": "Attempt directories preserve original report and log bytes. Disposable full project copies may be removed after completion; original command cwd strings record where execution took place.",
    }
    paper_integrity = {"schema": "repairseal-original-paper-byte-check-v1", "status": "PASS",
                       "archive_name": archive.name, "archive_bytes": archive.stat().st_size,
                       "archive_sha256": digest(archive), "paper_files": len(old_paper),
                       "original_paper_sha256": old_paper, "current_paper_sha256": current_paper,
                       "missing": [], "added": [], "changed": []}
    output.mkdir(parents=True)
    for i, path in enumerate(attempts, 1):
        shutil.move(str(path), output / ("attempt-" + str(i)))
    for name, record in (("summary.json", summary), ("paper-original-integrity.json", paper_integrity)):
        (output / name).write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for name in ("run_final_validation.py", "collect_final_validation.py"):
        shutil.copy2(Path(__file__).with_name(name), output / name)
    lines = [
        "# Final validation of the review update", "",
        "`summary.json` is the fixed entry point. It is derived from completed execution records; "
        "the last attempt passes all six requested gates. Previous attempts retain their original "
        "status, stdout, stderr, commands, timestamps, exit codes, generated receipts and source bindings.", "",
        "## Final gate results", "",
        "| Gate | Status | Exit code | Elapsed seconds |", "| --- | --- | ---: | ---: |",
    ]
    for name in ("preflight", "smoke", "expected-results", "core", "paper", "audit-data-integrity"):
        row = gates[name]
        lines.append(f"| {name} | {row['status']} | {row['returncode']} | {row['elapsed_seconds']:.2f} |")
    lines.extend([
        "", f"The packaged result check passes **{packaged['checks']}/{packaged['checks']}** checks. "
        f"The fresh core result check passes **{fresh['checks']}/{fresh['checks']}** checks. "
        f"The smoke suite executes **{smoke['tests']} tests, {smoke['skipped']} skipped**; "
        f"the formal complete suite executes **{unit['tests']} tests, {unit['skipped']} skipped**.", "",
        f"The complete suite record is in `{final_folder}/core/evaluation.json` and its named logs. "
        "An earlier separately run unit precheck is not substituted for this formal suite.", "",
        "## Preserved unsuccessful attempt", "",
        "Attempt 1 failed in the functional stage of the core gate. "
        "`round2 reproduction failed: 4` identifies command index 4, not four failed tests: "
        "one of eight original driver-contract tests failed because the exact declared source-addition "
        "inventory did not yet include the new `src/int32_refutation.py` module. "
        "The other five top-level gates passed. `attempt-1/diagnosis.json` identifies the failed test "
        "and preserves its source preimages. No failure has been rewritten as a success.", "",
        "The integration fix declares the one new path and pins its exact SHA-256. Historical source "
        "hashes, scientific fields, the existing three source additions, and receiver identity checks "
        "remain exact. Negative controls reject unknown modules and changes to the declared module. "
        "The successful attempt reruns all six gates from new full project copies.", "",
        "## Paper preservation and build isolation", "",
        f"All **{len(old_paper)}** delivery paper files match the originally supplied ZIP byte for byte. "
        "`paper-original-integrity.json` records the input ZIP hash and every original/current paper "
        "file hash. No paper build command ran inside the delivery tree.", "",
        "Core and standalone paper evaluation use two separate full project copies. "
        f"The standalone rebuilt outputs have {paper_pages['main.pdf']} main pages, "
        f"{paper_pages['supplementary.pdf']} supplementary pages, and "
        f"{paper_pages['figure-atlas.pdf']} atlas pages. Their hashes and byte counts are retained in "
        f"`{final_folder}/paper/evaluation.json`; the separate direct PDF inspection is recorded beside it. "
        "These generated PDFs do not replace the original paper. Disposable project copies may be "
        "removed after successful capture; original absolute execution paths remain in the logs.", "",
        "## Environment and rerun", "",
        "The evaluator reports record Python package versions and GCC/Clang executable identities. "
        "The complete run used the pinned dependencies, a writable temporary directory outside the "
        "project, and the locally provisioned TeX/font environment. Tool binaries and fonts are not "
        "redistributed in this record bundle. CBMC 6.6.0 was available for the unit semantic controls; "
        "these gates do not claim a fresh full CBMC/CPAchecker external campaign.", "",
        "With the required environment configured, run:", "", "```sh",
        "python3 -B artifact/results/review-update/final-validation/run_final_validation.py \\",
        "  --source /absolute/path/to/RepairSeal_TOSEM \\",
        "  --work /absolute/path/to/a/new-disposable-directory", "```", "",
        "The work directory must be new and outside the source project. The runner executes each "
        "gate with a new output directory and never overwrites earlier evidence. "
        "`collect_final_validation.py` checks the completed results and original ZIP before moving "
        "attempt report directories into a new archive directory; its `--help` lists the arguments.", "",
    ])
    (output / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": "PASS", "output": str(output), "attempts": len(attempts),
                      "packaged_checks": packaged["checks"], "fresh_checks": fresh["checks"],
                      "unit_tests": unit, "paper_files_unchanged": len(old_paper)}, indent=2))


if __name__ == "__main__":
    main()

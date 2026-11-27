#!/usr/bin/env python3
"""Run the unchanged evaluator gates in independent full project copies.

Run with the required pinned tool environment already configured. --work must
be a new directory outside --source. Complete command stdout/stderr and exact
exit codes are retained, including unsuccessful attempts if any. The original
source paper is byte-checked before and after all validation commands.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import threading
import time


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(root):
    return {str(path.relative_to(root)): sha(path) for path in sorted(root.rglob("*")) if path.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    args = parser.parse_args()
    source, work = args.source.resolve(), args.work.resolve()
    if work.exists() or work == source or source in work.parents:
        raise SystemExit("--work must be a new directory outside the source project")
    work.mkdir(parents=True)
    original_paper = inventory(source / "paper")
    record = {
        "schema": "repairseal-final-update-validation-v1",
        "source_project": str(source), "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "driver_sha256": sha(Path(__file__)), "source_paper_files": len(original_paper),
        "source_paper_before": original_paper,
        "scientific_code_bindings": {str(path.relative_to(source)): sha(path)
                                     for path in sorted((source / "artifact").rglob("*.py"))},
        "expected_results_sha256": sha(source / "artifact/expected-results.json"),
        "status": "RUNNING", "steps": [],
        "paper_build_isolation": "core and paper use separate complete copies; no build command runs in the source project",
    }
    reports = work / "reports"
    reports.mkdir()
    lock = threading.Lock()
    def save():
        temp = reports / "run.json.writing"
        temp.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        temp.replace(reports / "run.json")
    save()
    for name in ("core-project", "paper-project"):
        start = time.monotonic()
        shutil.copytree(source, work / name)
        print(json.dumps({"snapshot": name, "status": "READY", "elapsed_seconds": time.monotonic()-start}), flush=True)
    environment = dict(os.environ)
    environment.update(PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    def run(name, command, project):
        started = time.time()
        row = {"name": name, "command": command, "cwd": str(project / "artifact"),
               "started_at_utc": datetime.fromtimestamp(started, timezone.utc).isoformat(),
               "stdout": name + ".stdout.log", "stderr": name + ".stderr.log"}
        print(json.dumps({"gate": name, "status": "RUNNING"}), flush=True)
        with (reports / row["stdout"]).open("wb") as stdout, (reports / row["stderr"]).open("wb") as stderr:
            completed = subprocess.run(command, cwd=project / "artifact", env=environment,
                                       stdout=stdout, stderr=stderr, check=False)
        row.update(returncode=completed.returncode, status="PASS" if completed.returncode == 0 else "FAIL",
                   elapsed_seconds=time.time()-started, ended_at_utc=datetime.now(timezone.utc).isoformat())
        with lock:
            record["steps"].append(row)
            save()
        print(json.dumps(row), flush=True)
        return row
    core_project = work / "core-project"
    paper_project = work / "paper-project"
    for name in ("preflight", "smoke"):
        run(name, ["sh", "evaluate.sh", name, "--output", str(reports / name)], core_project)
    run("expected-results", [sys.executable, "-B", "verify_expected_results.py", "--output",
                             str(reports / "expected-results")], core_project)
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(run, name, ["sh", "evaluate.sh", name, "--output", str(reports / name)], project)
                   for name, project in (("core", core_project), ("paper", paper_project))]
        for future in futures:
            future.result()
    run("audit-data-integrity", [sys.executable, "-B", "audit_data_integrity.py"], core_project)
    record["source_paper_after"] = inventory(source / "paper")
    record["source_paper_unchanged"] = record["source_paper_after"] == original_paper
    record["ended_at_utc"] = datetime.now(timezone.utc).isoformat()
    record["status"] = "PASS" if record["source_paper_unchanged"] and all(
        row["returncode"] == 0 for row in record["steps"]) else "FAIL"
    save()
    print(json.dumps({"status": record["status"], "gates": len(record["steps"]),
                      "source_paper_unchanged": record["source_paper_unchanged"],
                      "report": str(reports / "run.json")}), flush=True)
    return int(record["status"] != "PASS")


if __name__ == "__main__":
    raise SystemExit(main())

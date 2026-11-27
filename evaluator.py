#!/usr/bin/env python3
"""Evaluator-facing entry point for the RepairSeal artifact.

Modes intentionally separate local executable evidence from retained-output
recomputation and from external campaigns that need pinned tools/data.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time
from typing import Any

ARTIFACT = Path(__file__).resolve().parent
ROOT = ARTIFACT.parent
PAPER = ROOT / "paper"
EXPECTED = ARTIFACT / "expected-results.json"
EXIT_FAILED = 1
EXIT_PRECONDITION = 3
PAPER_ABSENT = ("companion paper/ directory not found next to the artifact; "
                "paper-build steps are skipped (the artifact is standalone)")


def has_paper() -> bool:
    """The manuscript sources are an optional sibling directory, not part of the artifact."""
    return (PAPER / "main.tex").is_file() and (PAPER / "build.sh").is_file()


def scan_root() -> Path:
    return ROOT if has_paper() else ARTIFACT


def display(path: Path) -> str:
    base = scan_root()
    return str(path.relative_to(base)) if path.is_relative_to(base) else str(path)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def save(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".writing")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=True,
                                    allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def reserve(path: Path) -> Path:
    path = path.resolve()
    if path.exists():
        raise ValueError("--output must name a new path; existing evidence is preserved")
    if path.is_relative_to(ARTIFACT.resolve()):
        raise ValueError("--output must be outside artifact/ so scientific source snapshots stay stable")
    path.mkdir(parents=True)
    return path


def command_record(name: str, command: list[str], cwd: Path, output: Path,
                   timeout: float, env: dict[str, str] | None = None,
                   accepted: tuple[int, ...] = (0,)) -> dict[str, Any]:
    logs = output / "logs"
    logs.mkdir(exist_ok=True)
    stdout_path = logs / f"{name}.stdout.log"
    stderr_path = logs / f"{name}.stderr.log"
    started = time.monotonic()
    record: dict[str, Any] = {
        "name": name,
        "command": command,
        "cwd": str(cwd),
        "stdout": str(stdout_path.relative_to(output)),
        "stderr": str(stderr_path.relative_to(output)),
        "started_utc": utc_now(),
        "timeout_seconds": timeout,
        "status": "RUNNING",
    }
    try:
        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            completed = subprocess.run(command, cwd=cwd, env=env, stdout=stdout,
                                       stderr=stderr, timeout=timeout, check=False)
        record["returncode"] = completed.returncode
        record["status"] = "PASS" if completed.returncode in accepted else "FAIL"
    except subprocess.TimeoutExpired:
        record.update(status="TIMEOUT", returncode=None)
    except BaseException as exc:
        record.update(status="FAIL", returncode=None,
                      error_type=type(exc).__name__, error=str(exc))
    record["ended_utc"] = utc_now()
    record["elapsed_seconds"] = time.monotonic() - started
    return record


def package_versions() -> dict[str, Any]:
    expected = {
        "pycparser": "3.0",
        "matplotlib": "3.10.8",
        "numpy": "2.3.5",
        "PyMuPDF": "1.26.7",
        "pillow": "12.3.0",
    }
    rows = {}
    for distribution, wanted in expected.items():
        try:
            actual = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            actual = None
        rows[distribution] = {
            "expected": wanted,
            "actual": actual,
            "status": "PASS" if actual == wanted else "FAIL",
        }
    return rows


def executable_identity(path: Path | None, version_args: tuple[str, ...] = ("--version",)) -> dict[str, Any]:
    if path is None:
        return {"status": "MISSING"}
    path = path.expanduser().resolve()
    if not path.is_file() or not os.access(path, os.X_OK):
        return {"status": "UNUSABLE", "path": str(path)}
    try:
        completed = subprocess.run([str(path), *version_args], capture_output=True,
                                   text=True, timeout=30, check=False)
    except BaseException as exc:
        return {"status": "UNUSABLE", "path": str(path), "error": str(exc)}
    return {
        "status": "READY" if completed.returncode == 0 else "UNUSABLE",
        "path": str(path),
        "sha256": sha256(path),
        "returncode": completed.returncode,
        "version_output": (completed.stdout + completed.stderr).strip(),
    }


def external_preconditions(args: argparse.Namespace) -> dict[str, Any]:
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))["external_only"]
    rows: dict[str, Any] = {}

    python_row = executable_identity(args.python312, ("--version",))
    if python_row.get("status") == "READY":
        text = python_row.get("version_output", "")
        python_row["expected_version"] = expected["historical_python"]["version"]
        python_row["version_match"] = "3.12.14" in text
        if not python_row["version_match"]:
            python_row["status"] = "WRONG_VERSION"
    rows["historical_python"] = python_row

    for key, path, token in (
        ("boolean_cbmc", args.cbmc66, "6.6.0"),
        ("witness_cbmc", args.cbmc611, "6.11.0"),
        ("cpachecker", args.cpachecker, "4.3"),
    ):
        row = executable_identity(path)
        if row.get("status") == "READY":
            row["expected_version"] = token
            row["version_match"] = token in row.get("version_output", "")
            if not row["version_match"]:
                row["status"] = "WRONG_VERSION"
        rows[key] = row

    archive = args.archive.expanduser().resolve() if args.archive else None
    if archive is None:
        rows["codeflaws_archive"] = {"status": "MISSING"}
    elif not archive.is_file():
        rows["codeflaws_archive"] = {"status": "UNUSABLE", "path": str(archive)}
    else:
        actual_hash = sha256(archive)
        actual_bytes = archive.stat().st_size
        required = expected["codeflaws_archive"]
        rows["codeflaws_archive"] = {
            "status": "READY" if (actual_hash == required["sha256"] and
                                     actual_bytes == required["bytes"]) else "WRONG_IDENTITY",
            "path": str(archive), "sha256": actual_hash, "bytes": actual_bytes,
            "expected_sha256": required["sha256"], "expected_bytes": required["bytes"],
        }

    upstream = args.upstream.expanduser().resolve() if args.upstream else None
    rows["upstream_vulkan"] = {
        "status": "READY" if upstream and upstream.is_dir() else "MISSING",
        **({"path": str(upstream)} if upstream else {}),
        "note": "A source checkout alone is not proof of application-level execution; the external mode records the command separately.",
    }
    required_for_campaigns = ("historical_python", "boolean_cbmc", "witness_cbmc",
                              "cpachecker", "codeflaws_archive")
    ready = all(rows[name]["status"] == "READY" for name in required_for_campaigns)
    return {
        "status": "READY" if ready else "FAILED_PRECONDITION",
        "scientific_studies_started": 0,
        "requirements": rows,
    }


def path_hygiene() -> dict[str, Any]:
    forbidden = re.compile(r"/(?:mnt/data|home/oai|root/\.cache|tmp)/")
    paths = [ARTIFACT / "README.md", ARTIFACT / "docs/reproduction.md"]
    if has_paper():
        paths += [ROOT / "README.md", PAPER / "README.md"]
    hits = []
    for path in paths:
        if not path.is_file():
            hits.append({"path": display(path), "problem": "missing"})
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if forbidden.search(line):
                hits.append({"path": display(path), "line": number,
                             "problem": "private absolute path"})
    caches = []
    base = scan_root()
    # Only the delivered trees are scanned; sibling venvs and output folders
    # (e.g. ../rs-out next to artifact/ and paper/) are not part of the delivery.
    roots = [ARTIFACT, PAPER] if has_paper() else [ARTIFACT]
    for path in (p for root in roots for p in root.rglob("*")):
        parts = path.relative_to(base).parts
        if {"evaluation-output", ".git", ".venv", "venv"} & set(parts):
            continue
        if path.name == "__pycache__" or path.suffix in {".pyc", ".pyo"}:
            caches.append(display(path))
    return {"status": "PASS" if not hits and not caches else "FAIL",
            "documentation_hits": hits, "cache_files": caches}


def preflight(args: argparse.Namespace, output: Path, report: dict[str, Any]) -> bool:
    required = [
        ARTIFACT / "LICENSE", ARTIFACT / "README.md", ARTIFACT / "reproduce.py",
        ARTIFACT / "verify_expected_results.py", EXPECTED,
    ]
    if has_paper():
        required += [ROOT / "README.md", PAPER / "main.tex", PAPER / "supplementary.tex",
                     PAPER / "build.sh"]
    files = [{"path": display(path), "status": "PASS" if path.is_file() else "MISSING"}
             for path in required]
    report["paper_companion"] = ("PRESENT" if has_paper() else "ABSENT: " + PAPER_ABSENT)
    report["environment"] = {
        "python": sys.version,
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_count": os.cpu_count(),
        "packages": package_versions(),
        "gcc": executable_identity(Path(shutil.which("gcc"))) if shutil.which("gcc") else {"status": "MISSING"},
        "clang": executable_identity(Path(shutil.which("clang"))) if shutil.which("clang") else {"status": "MISSING"},
        "java": executable_identity(Path(shutil.which("java")), ("--version",)) if shutil.which("java") else {"status": "MISSING"},
    }
    report["required_files"] = files
    report["path_hygiene"] = path_hygiene()
    report["external_preconditions"] = external_preconditions(args)
    command = [sys.executable, "-B", str(ARTIFACT / "verify_expected_results.py"),
               "--output", str(output / "key-result-trace")]
    step = command_record("verify-packaged-results", command, ROOT, output,
                          timeout=args.step_timeout, env=base_env())
    report.setdefault("steps", []).append(step)
    delivery = command_record("audit-delivery",
        [sys.executable, "-B", str(ARTIFACT / "audit_delivery.py"),
         "--output", str(output / "delivery-audit.json")],
        ROOT, output, timeout=args.step_timeout, env=base_env())
    report["steps"].append(delivery)
    package_ok = all(row["status"] == "PASS" for row in report["environment"]["packages"].values())
    files_ok = all(row["status"] == "PASS" for row in files)
    return (package_ok and files_ok and report["path_hygiene"]["status"] == "PASS" and
            step["status"] == "PASS" and delivery["status"] == "PASS")


def base_env() -> dict[str, str]:
    existing = os.environ.get("PYTHONPATH", "")
    local = os.pathsep.join((str(ARTIFACT / "tests"), str(ARTIFACT / "src")))
    pythonpath = local + (os.pathsep + existing if existing else "")
    return {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0",
            "PYTHONPATH": pythonpath,
            "SOURCE_DATE_EPOCH": os.environ.get("SOURCE_DATE_EPOCH", "1795046400"),
            "FORCE_SOURCE_DATE": "1", "TZ": "UTC"}


def parse_unittest(step: dict[str, Any], output: Path) -> dict[str, Any]:
    text = ""
    for key in ("stdout", "stderr"):
        path = output / step[key]
        if path.exists():
            text += path.read_text(encoding="utf-8", errors="replace") + "\n"
    match = re.search(r"Ran (\d+) tests? in [^\n]+", text)
    skipped = re.search(r"OK \(skipped=(\d+)\)", text)
    ok = bool(re.search(r"^OK(?: \(skipped=\d+\))?\s*$", text, re.M))
    return {"tests": int(match.group(1)) if match else None,
            "skipped": int(skipped.group(1)) if skipped else 0,
            "ok": ok,
            "skip_reasons": sorted(set(re.findall(r"skipped '([^']+)'", text)))}


def run_smoke(args: argparse.Namespace, output: Path, report: dict[str, Any]) -> bool:
    tests = [
        "tests.test_receiving_boundaries",
        "tests.test_domain_transport",
        "tests.test_codeflaws_header_admission",
        "tests.test_current_admission_report",
        "tests.test_claim_ledger",
        "tests.test_int32_refutation",
        "tests.test_introclass_normalization",
        "tests.test_update_result_types",
    ]
    step = command_record("smoke-tests",
                          [sys.executable, "-B", "-m", "unittest", "-v", *tests],
                          ARTIFACT, output, args.step_timeout, base_env())
    step["test_summary"] = parse_unittest(step, output)
    report.setdefault("steps", []).append(step)
    return step["status"] == "PASS" and step["test_summary"]["ok"]


def run_paper(args: argparse.Namespace, output: Path, report: dict[str, Any]) -> bool | None:
    """Build the companion paper; return None (skipped) when it is not present."""
    if not has_paper():
        report.setdefault("steps", []).append(
            {"name": "paper-build", "status": "SKIPPED", "reason": PAPER_ABSENT})
        print("paper-build skipped: " + PAPER_ABSENT, file=sys.stderr)
        return None
    step = command_record("paper-build", ["sh", "build.sh"], PAPER, output,
                          args.paper_timeout, base_env())
    report.setdefault("steps", []).append(step)
    if step["status"] != "PASS":
        return False
    pdfs = {}
    for name in ("main.pdf", "supplementary.pdf", "figure-atlas.pdf"):
        path = PAPER / name
        pdfs[name] = {"status": "PASS" if path.is_file() else "MISSING",
                      **({"bytes": path.stat().st_size, "sha256": sha256(path)} if path.is_file() else {})}
    report["paper_outputs"] = pdfs
    return all(row["status"] == "PASS" for row in pdfs.values())


def run_core(args: argparse.Namespace, output: Path, report: dict[str, Any]) -> bool:
    reproduction = output / "fresh-core"
    command = [sys.executable, "-B", str(ARTIFACT / "reproduce.py"),
               "--checks", "analysis", "functional", "demand", "headers",
               "--output", str(reproduction), "--step-timeout", str(args.science_timeout)]
    if args.gcc:
        command += ["--gcc", str(args.gcc)]
    if args.clang:
        command += ["--clang", str(args.clang)]
    step = command_record("fresh-core-reproduction", command, ARTIFACT, output,
                          args.core_timeout, base_env())
    report.setdefault("steps", []).append(step)
    if step["status"] != "PASS":
        return False

    tests = command_record("complete-unit-suite",
                           [sys.executable, "-B", "-m", "unittest", "discover",
                            "-s", "tests", "-p", "test_*.py", "-v"],
                           ARTIFACT, output, args.test_timeout, base_env())
    tests["test_summary"] = parse_unittest(tests, output)
    report["steps"].append(tests)
    summary = tests["test_summary"]
    tests_ok = (tests["status"] == "PASS" and summary["ok"] and
                summary["tests"] is not None and summary["tests"] >= 360 and
                summary["skipped"] <= 2)

    verify = command_record(
        "verify-fresh-results",
        [sys.executable, "-B", str(ARTIFACT / "verify_expected_results.py"),
         "--output", str(output / "fresh-key-result-trace"),
         "--fresh-demand", str(reproduction / "unsigned-demand"),
         "--fresh-functional", str(reproduction / "functional"),
         "--fresh-headers", str(reproduction / "header-admission")],
        ROOT, output, args.step_timeout, base_env())
    report["steps"].append(verify)
    paper_ok = run_paper(args, output, report) is not False  # None = skipped (no paper/)
    return tests_ok and verify["status"] == "PASS" and paper_ok


def run_external(args: argparse.Namespace, output: Path, report: dict[str, Any]) -> int:
    preconditions = external_preconditions(args)
    report["external_preconditions"] = preconditions
    save(output / "external-preconditions.json", preconditions)
    if preconditions["status"] != "READY":
        return EXIT_PRECONDITION

    # Exact historical receipt compatibility.
    history = command_record(
        "historical-receipt-replay",
        [str(args.python312), "-B", "-m", "unittest", "-v",
         "tests.test_current_admission_report.HistoricalAdmissionReceiptCompatibility"],
        ARTIFACT, output, args.step_timeout, base_env())
    report.setdefault("steps", []).append(history)
    if history["status"] != "PASS":
        return EXIT_FAILED

    campaigns = [
        ("external-cbmc66", ["cbmc"], ["--cbmc", str(args.cbmc66)]),
        ("external-witness", ["witness"], ["--cbmc", str(args.cbmc611),
          "--witness-cbmc", str(args.cbmc611), "--cpachecker", str(args.cpachecker)]),
        ("external-codeflaws", ["native", "signed", "coverage", "timing",
          "point-timing", "counter-overhead"], ["--archive", str(args.archive)]),
    ]
    for name, checks, options in campaigns:
        destination = output / name
        command = [sys.executable, "-B", str(ARTIFACT / "reproduce.py"),
                   "--checks", *checks, "--output", str(destination),
                   "--gcc", str(args.gcc), "--clang", str(args.clang),
                   "--jobs", str(args.jobs), "--step-timeout", str(args.science_timeout),
                   *options]
        step = command_record(name, command, ARTIFACT, output,
                              args.external_timeout, base_env())
        report.setdefault("steps", []).append(step)
        if step["status"] != "PASS":
            return EXIT_FAILED
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("preflight", "smoke", "paper", "core", "external", "all"))
    p.add_argument("--output", type=Path)
    p.add_argument("--archive", type=Path)
    p.add_argument("--cbmc66", type=Path)
    p.add_argument("--cbmc611", type=Path)
    p.add_argument("--cpachecker", type=Path)
    p.add_argument("--python312", type=Path)
    p.add_argument("--upstream", type=Path)
    p.add_argument("--gcc", type=Path, default=Path(shutil.which("gcc")) if shutil.which("gcc") else None)
    p.add_argument("--clang", type=Path, default=Path(shutil.which("clang")) if shutil.which("clang") else None)
    p.add_argument("--jobs", type=int, default=4)
    p.add_argument("--step-timeout", type=float, default=600)
    p.add_argument("--science-timeout", type=float, default=21600)
    p.add_argument("--test-timeout", type=float, default=7200)
    p.add_argument("--paper-timeout", type=float, default=3600)
    p.add_argument("--core-timeout", type=float, default=28800)
    p.add_argument("--external-timeout", type=float, default=86400)
    return p


def main() -> int:
    args = parser().parse_args()
    if not 1 <= args.jobs <= 4:
        raise SystemExit("--jobs must be 1..4")
    if args.output is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        args.output = ROOT / "evaluation-output" / f"{stamp}-{args.mode}"
    output = reserve(args.output)
    report: dict[str, Any] = {
        "schema": "repairseal-artifact-evaluation-v1",
        "mode": args.mode,
        "started_utc": utc_now(),
        "project_root": str(ROOT),
        "status": "RUNNING",
        "steps": [],
        "interpretation": (
            "Local fresh execution, retained-output recomputation, and external-only campaigns are distinct states. "
            "A missing external prerequisite starts zero scientific studies and is not a negative result."
        ),
    }
    save(output / "evaluation.json", report)
    exit_code = EXIT_FAILED
    try:
        local_ok = preflight(args, output, report)
        if not local_ok:
            exit_code = EXIT_FAILED
        elif args.mode == "preflight":
            exit_code = 0
        elif args.mode == "smoke":
            exit_code = 0 if run_smoke(args, output, report) else EXIT_FAILED
        elif args.mode == "paper":
            built = run_paper(args, output, report)
            exit_code = EXIT_PRECONDITION if built is None else (0 if built else EXIT_FAILED)
        elif args.mode == "core":
            exit_code = 0 if run_core(args, output, report) else EXIT_FAILED
        elif args.mode == "external":
            exit_code = run_external(args, output, report)
        else:
            local_complete = run_core(args, output, report)
            exit_code = run_external(args, output, report) if local_complete else EXIT_FAILED
    except BaseException as exc:
        report.update(error_type=type(exc).__name__, error=str(exc))
        exit_code = EXIT_FAILED
    report["ended_utc"] = utc_now()
    report["exit_code"] = exit_code
    report["status"] = ({0: "PASS", EXIT_PRECONDITION: "FAILED_PRECONDITION"}.get(exit_code, "FAIL"))
    save(output / "evaluation.json", report)
    print(json.dumps({"status": report["status"], "mode": args.mode,
                      "output": str(output), "exit_code": exit_code}))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

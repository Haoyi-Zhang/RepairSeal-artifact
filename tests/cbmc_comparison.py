#!/usr/bin/env python3
"""Independent raw-C CBMC decisions for receiver-owned finite repair requests.

No network access or tool installation is performed by this script.  Only
requests admitted by the existing unsigned scalar frontend are submitted to
CBMC.  The submitted functions are the original request strings, not a C
translation of RepairSeal's DAG.  CBMC checks the decision predicate; it does
not produce RepairSeal's canonical obligation/trace/input minimum.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import shutil
import signal
import subprocess
import sys
import time
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]
import proof_dag_checker as core
from demand_evaluator import evaluate_demand
from scientific_driver import new_output_directory, require_assertions

CBMC_FLAGS = (
    "--32", "--c11", "--gcc", "--no-standard-checks",
    "--div-by-zero-check", "--undefined-shift-check",
    "--retain-trivial-checks", "--json-ui", "--trace",
)
EXPECTED_COUNTS = {"core": 380, "grammar": 400, "natural": 24}
BOUND_FILES = (
    "tests/cbmc_comparison.py", "tests/scientific_driver.py",
    "src/proof_dag_checker.py", "src/demand_evaluator.py",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def source_fingerprints() -> dict[str, str]:
    return {name: sha256(ROOT / name) for name in BOUND_FILES}


def emit_harness(request: dict, directory: Path) -> Path:
    """Admit first; preserve each function's original bytes in a separate file."""
    domains, names = core.validate_request_fields(request)
    core.build_expected(request)
    if directory.exists():
        raise FileExistsError(f"harness destination already exists: {directory}")
    directory.mkdir(parents=True)
    write_json(directory / "request.json", request)
    for role in core.ROLES:
        (directory / f"{role}.c").write_bytes(request[role].encode("utf-8"))
    (directory / "repair_guard.txt").write_bytes(request["repair_guard"].encode("utf-8"))
    # Reserved implementation names cannot be introduced by admitted input
    # identifiers.  The f macro also consistently renames a local parameter f.
    lines = [
        "/* Generated wrapper. Included receiver-owned functions are unchanged. */",
        '_Static_assert(sizeof(unsigned) == 4, "unsigned must occupy four bytes");',
        '_Static_assert(~0u == 4294967295u, "unsigned must have 32 value bits");',
        "extern unsigned __VERIFIER_nondet_uint(void);",
        "extern void __CPROVER_assume(_Bool);",
        "extern void __CPROVER_assert(_Bool, const char *);",
    ]
    for role in core.ROLES:
        lines += [f"#define f __repairseal_{role}", f'#include "{role}.c"', "#undef f"]
    lines += ["int main(void)", "{"]
    for name in names:
        lines.append(f"  unsigned {name} = __VERIFIER_nondet_uint();")
        membership = " || ".join(f"{name} == {value}u" for value in domains[name])
        lines.append(f"  __CPROVER_assume({membership});")
    arguments = ", ".join(names)
    lines += [
        f"  unsigned __repairseal_q = __repairseal_candidate({arguments});",
        "  if (",
        request["repair_guard"],
        "  ) {",
        f"    unsigned __repairseal_t = __repairseal_reference({arguments});",
        '    __CPROVER_assert(__repairseal_q == __repairseal_t, "repairseal.repair");',
        "  } else {",
        f"    unsigned __repairseal_p = __repairseal_original({arguments});",
        '    __CPROVER_assert(__repairseal_q == __repairseal_p, "repairseal.preserve");',
        "  }",
        "  return 0;",
        "}",
    ]
    path = directory / "harness.c"
    path.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
    return path


def property_category(prop: dict) -> str:
    description = prop.get("description", "")
    if description == "repairseal.repair":
        return "repair-equality"
    if description == "repairseal.preserve":
        return "preservation-equality"
    identity = prop.get("property", "")
    combined = f"{identity} {description}".lower()
    if "division-by-zero" in combined or "division by zero" in combined:
        base = "division-definedness"
    elif "undefined-shift" in combined or "shift distance" in combined:
        base = "shift-definedness"
    else:
        return "unclassified"
    location = prop.get("sourceLocation", {})
    source = location.get("file", "")
    for role in core.ROLES:
        if f"__repairseal_{role}" in identity or Path(source).name == f"{role}.c":
            return f"{role}-{base}"
    return f"wrapper-{base}"


def parse_cbmc_result(stdout: str, exit_code: int) -> dict:
    """Require mutually consistent JSON, exit code and property outcomes."""
    try:
        raw = core.load_json_strict(stdout)
    except (core.Invalid, ValueError) as exc:
        return {"status": "ERROR", "reason": f"invalid CBMC JSON: {exc}", "properties": []}
    if type(raw) is not list or any(type(item) is not dict for item in raw):
        return {"status": "ERROR", "reason": "CBMC JSON is not a list of objects", "properties": []}
    terminal = [item["cProverStatus"] for item in raw if "cProverStatus" in item]
    blocks = [item["result"] for item in raw if "result" in item]
    properties = []
    for block in blocks:
        if type(block) is not list or any(type(p) is not dict for p in block):
            return {"status": "ERROR", "reason": "invalid property block", "properties": []}
        for prop in block:
            properties.append({
                "property": prop.get("property"),
                "description": prop.get("description"),
                "status": prop.get("status"),
                "sourceLocation": prop.get("sourceLocation"),
                "category": property_category(prop),
            })
    errors = [item.get("messageText", "") for item in raw if item.get("messageType") == "ERROR"]
    failed = [p for p in properties if p["status"] == "FAILURE"]
    unknown = [p for p in properties if p["status"] == "UNKNOWN"]
    malformed = [p for p in properties if p["status"] not in {"SUCCESS", "FAILURE", "UNKNOWN"}]
    common = {"properties": properties, "terminal_statuses": terminal, "error_messages": errors,
              "failed_property_count": len(failed), "unknown_property_count": len(unknown)}
    if errors or malformed or any(p["category"] == "unclassified" for p in properties):
        return {"status": "ERROR", "reason": "error, malformed or unclassified property", **common}
    if terminal == ["success"] and exit_code == 0 and not failed and not unknown and blocks:
        return {"status": "ACCEPT", "reason": "all generated properties established", **common}
    # Refuting a conjunction needs one reachable violation. CBMC may leave
    # later checks UNKNOWN after that violation, especially after undefined
    # behavior. Such checks cannot invalidate the already found counterexample;
    # they would prevent ACCEPT. No canonicality is inferred from this result.
    if terminal == ["failure"] and exit_code == 10 and failed:
        return {"status": "REFUTED", "reason": "at least one reachable failed property", **common}
    return {"status": "ERROR", "reason": "inconsistent or incomplete terminal result", **common}


class Engine:
    def __init__(self, binary: Path, library_dirs=(), timeout=30.0, memory_mib=2048):
        self.binary = binary.resolve(strict=True)
        self.timeout = float(timeout)
        self.memory_mib = int(memory_mib)
        if not self.binary.is_file() or not os.access(self.binary, os.X_OK):
            raise ValueError("CBMC binary must be an executable regular file")
        if self.timeout <= 0 or not math.isfinite(self.timeout) or self.memory_mib < 128:
            raise ValueError("positive finite timeout and at least 128 MiB required")
        self.environment = dict(os.environ)
        self.library_dirs = [str(Path(p).resolve(strict=True)) for p in library_dirs]
        if self.library_dirs:
            inherited = self.environment.get("LD_LIBRARY_PATH")
            self.environment["LD_LIBRARY_PATH"] = os.pathsep.join(
                self.library_dirs + ([inherited] if inherited else []))
        # prlimit also applies to compiler-preprocessor descendants.  It does
        # not require a global installation or a change of process privileges.
        self.prlimit = shutil.which("prlimit")
        if self.prlimit is None or os.name != "posix":
            raise RuntimeError("this controlled runner requires POSIX prlimit")
        self.profile = self._profile()

    def _probe(self, command):
        result = subprocess.run(command, env=self.environment, capture_output=True, timeout=15)
        return {"command": command, "exit_code": result.returncode,
                "stdout": result.stdout.decode("utf-8", errors="replace"),
                "stderr": result.stderr.decode("utf-8", errors="replace")}

    def _profile(self):
        version = self._probe([str(self.binary), "--version"])
        if version["exit_code"] != 0 or not version["stdout"].strip():
            raise RuntimeError(f"CBMC version probe failed: {version}")
        gcc = shutil.which("gcc")
        if gcc is None:
            raise RuntimeError("GCC preprocessor not found")
        dependencies = self._probe(["ldd", str(self.binary)])
        library_hashes = {}
        for line in dependencies["stdout"].splitlines():
            match = re.search(r"(?:=>\s+)?(/\S+)\s+\(", line)
            if match:
                path = Path(match.group(1)).resolve(strict=True)
                library_hashes[str(path)] = sha256(path)
        return {
            "binary": str(self.binary), "binary_sha256": sha256(self.binary),
            "version_probe": version, "flags": list(CBMC_FLAGS),
            "library_directories": self.library_dirs,
            "dynamic_dependencies": dependencies, "dynamic_library_sha256": library_hashes,
            "gcc": str(Path(gcc).resolve()), "gcc_sha256": sha256(Path(gcc)),
            "gcc_version": self._probe([gcc, "--version"]),
            "prlimit": self.prlimit, "prlimit_sha256": sha256(Path(self.prlimit)),
            "timeout_seconds": self.timeout, "address_space_limit_mib": self.memory_mib,
            "platform": platform.platform(), "python": sys.version,
        }

    def run(self, directory: Path) -> dict:
        command = [self.prlimit, f"--as={self.memory_mib * 1024 * 1024}",
                   f"--cpu={math.ceil(self.timeout) + 2}", "--", str(self.binary),
                   *CBMC_FLAGS, "harness.c"]
        write_json(directory / "invocation.json", {"argv": command, "cwd": ".",
                   "timeout_seconds": self.timeout, "memory_mib": self.memory_mib})
        started = time.perf_counter()
        process = subprocess.Popen(command, cwd=directory, env=self.environment,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   start_new_session=True)
        timed_out = False
        try:
            stdout, stderr = process.communicate(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            stdout, stderr = process.communicate()
        seconds = time.perf_counter() - started
        (directory / "cbmc.stdout.json").write_bytes(stdout)
        (directory / "cbmc.stderr.txt").write_bytes(stderr)
        parsed = parse_cbmc_result(stdout.decode("utf-8", errors="replace"), process.returncode)
        if timed_out:
            parsed = {"status": "TIMEOUT", "reason": "wall-clock limit; complete result not claimed",
                      "partial_parse": parsed, "properties": parsed.get("properties", [])}
        parsed.update({"exit_code": process.returncode, "wall_seconds": seconds,
                       "timed_out": timed_out,
                       "stdout_sha256": hashlib.sha256(stdout).hexdigest(),
                       "stderr_sha256": hashlib.sha256(stderr).hexdigest(),
                       "counterexample_contract": "any property failure; not canonical leastness"})
        write_json(directory / "cbmc-result.json", parsed)
        return parsed


def population_files(populations, proof_data: Path, natural_data: Path):
    rows = []
    for population in populations:
        if population == "core":
            files = sorted((proof_data / "fixture-inputs").glob("*.json"))
            files += sorted((proof_data / "stress-inputs").glob("*.json"))
        elif population == "grammar":
            files = sorted((proof_data / "holdout-differential/inputs").glob("*.json"))
        else:
            files = sorted(natural_data.glob("*/request.json"))
        if len(files) != EXPECTED_COUNTS[population]:
            raise ValueError(f"{population}: expected {EXPECTED_COUNTS[population]} requests, found {len(files)}")
        rows.extend((population, path) for path in files)
    return rows


def check_case(index: int, population: str, path: Path, output: Path, engine: Engine):
    request = core.load_json_file(path)
    case_dir = output / f"{index:04d}"
    harness = emit_harness(request, case_dir)
    start = time.perf_counter()
    direct = evaluate_demand(request)
    direct_seconds = time.perf_counter() - start
    write_json(case_dir / "direct-result.json", direct)
    cbmc = engine.run(case_dir)
    agreement = None
    if cbmc["status"] in {"ACCEPT", "REFUTED"}:
        agreement = cbmc["status"] == direct["status"]
    row = {
        "index": index, "population": population, "request_id": request["id"],
        "input_file": str(path.resolve()), "input_file_sha256": sha256(path),
        "input_order": list(request["inputs"]),
        "domain_size": math.prod(map(len, request["inputs"].values())),
        "case_directory": str(case_dir.relative_to(output)),
        "source_sha256": {role: core.digest(request[role]) for role in (*core.ROLES, "repair_guard")},
        "harness_sha256": sha256(harness),
        "direct_status": direct["status"], "direct_checked_cells": direct["checked_cells"],
        "direct_wall_seconds": direct_seconds,
        "cbmc_status": cbmc["status"], "cbmc_exit_code": cbmc["exit_code"],
        "cbmc_wall_seconds": cbmc["wall_seconds"],
        "status_agreement": agreement,
        "failed_property_categories": dict(Counter(p["category"] for p in cbmc["properties"]
                                                    if p["status"] == "FAILURE")),
    }
    write_json(case_dir / "case-summary.json", row)
    return row


def main() -> None:
    require_assertions()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cbmc", type=Path, default=shutil.which("cbmc"))
    parser.add_argument("--library-dir", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--proof-data", type=Path, default=ROOT / "proof-data")
    parser.add_argument("--natural-data", type=Path,
                        default=ROOT / "data/natural-domains")
    parser.add_argument("--population", nargs="+", choices=tuple(EXPECTED_COUNTS),
                        default=list(EXPECTED_COUNTS))
    parser.add_argument("--limit", type=int, help="explicit pilot prefix, never presented as the full population")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--memory-mib", type=int, default=2048)
    parser.add_argument("--jobs", type=int, default=1)
    args = parser.parse_args()
    if args.cbmc is None:
        parser.error("CBMC is not installed; pass --cbmc PATH (this script never downloads tools)")
    if args.jobs < 1 or args.jobs > 16 or args.limit is not None and args.limit < 1:
        parser.error("jobs must be 1..16 and an explicit pilot limit must be positive")
    populations = list(dict.fromkeys(args.population))
    cases = population_files(populations, args.proof_data.resolve(), args.natural_data.resolve())
    if args.limit is not None:
        cases = cases[:args.limit]
    engine = Engine(args.cbmc, args.library_dir, args.timeout, args.memory_mib)
    before = source_fingerprints()
    input_before = {str(path.resolve()): sha256(path) for _, path in cases}
    output = new_output_directory(args.output)
    write_json(output / "tool-profile.json", engine.profile)
    write_json(output / "protocol.json", {
        "schema": "repairseal-cbmc-comparison-v1", "populations": populations,
        "pilot_limit": args.limit, "planned_requests": len(cases), "jobs": args.jobs,
        "source_sha256": before, "input_sha256": input_before,
        "refutation_rule": "one classified FAILURE with final failure/exit 10 suffices even if other properties remain UNKNOWN",
        "semantic_target": "finite universal definedness and guarded equality",
        "cbmc_output": "decision with possibly noncanonical property counterexamples",
        "direct_output": "same decision plus canonical obligation/trace/input witness",
        "timing_scope": "CBMC process wall time versus direct API wall time; not a matched performance claim",
        "timing_caveat": "parallel jobs contend for resources; measurements are descriptive execution logs",
        "unsigned_overflow": "permitted modular arithmetic; overflow checks not enabled",
        "source_translation": "raw admitted C included under an f-renaming macro; no receiver DAG emission",
    })
    rows = []
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(check_case, index, population, path, output, engine): index
                   for index, (population, path) in enumerate(cases)}
        for future in as_completed(futures):
            rows.append(future.result())
            if len(rows) % 25 == 0 or len(rows) == len(cases):
                print(json.dumps({"completed": len(rows), "planned": len(cases),
                                  "cbmc_statuses": dict(Counter(row["cbmc_status"] for row in rows))}), flush=True)
    rows.sort(key=lambda row: row["index"])
    write_json(output / "cases.json", rows)
    stable = before == source_fingerprints()
    stable = stable and input_before == {str(path.resolve()): sha256(path) for _, path in cases}
    groups = {}
    for population in populations:
        selected = [row for row in rows if row["population"] == population]
        groups[population] = {
            "requests": len(selected),
            "direct_statuses": dict(Counter(row["direct_status"] for row in selected)),
            "cbmc_statuses": dict(Counter(row["cbmc_status"] for row in selected)),
            "status_agreements": sum(row["status_agreement"] is True for row in selected),
            "status_disagreements": sum(row["status_agreement"] is False for row in selected),
            "unresolved": sum(row["status_agreement"] is None for row in selected),
        }
    disagreements = [row["index"] for row in rows if row["status_agreement"] is False]
    summary = {
        "schema": "repairseal-cbmc-comparison-summary-v1", "requests": len(rows),
        "populations": groups, "source_and_inputs_stable": stable,
        "disagreement_indices": disagreements,
        "complete_decisions": sum(row["status_agreement"] is not None for row in rows),
        "status_agreements": sum(row["status_agreement"] is True for row in rows),
        "unresolved_indices": [row["index"] for row in rows if row["status_agreement"] is None],
        "interpretation": "Only ACCEPT/REFUTED are compared. No CBMC canonical diagnostic or standard witness validation is claimed.",
        "protocol_sha256": sha256(output / "protocol.json"),
        "tool_profile_sha256": sha256(output / "tool-profile.json"),
    }
    write_json(output / "summary.json", summary)
    print(json.dumps(summary, indent=2))
    if not stable or disagreements:
        raise SystemExit(1)
    if summary["unresolved_indices"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()

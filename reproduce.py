#!/usr/bin/env python3
"""Execute RepairSeal studies or independently recheck the retained observations.

The default selection runs every listed study, including standard-witness
interoperability. Use --checks to select an explicit subset. Retained-record
analysis does not count as a fresh execution of source programs or measurements.
All outputs go to a new directory and every selected stage has an explicit
state. Missing prerequisites prevent all selected studies from starting.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import random
import re
import shutil
import signal
import statistics
import subprocess
import sys
import time
import traceback

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent
CHECKS = ("analysis", "units", "functional", "demand", "cbmc", "native", "signed", "coverage",
          "timing", "point-timing", "counter-overhead", "headers", "witness")
DESTINATIONS = {"analysis": "retained-analysis", "units": "unit-tests", "functional": "functional",
                "demand": "unsigned-demand", "cbmc": "c-verification", "native": "source-programs",
                "signed": "signed-contract", "coverage": "signed-coverage",
                "timing": "receiving-time", "point-timing": "point-demand",
                "counter-overhead": "counter-overhead",
                "headers": "header-admission", "witness": "witness-interoperability"}
SCRIPTS = {"functional": "reproduce_all.py", "demand": "demand_comparison.py", "cbmc": "cbmc_comparison.py",
           "native": "codeflaws_staged_study.py", "signed": "int32_contract_study.py",
           "coverage": "signed_coverage_study.py",
           "timing": "int32_evaluator_study.py", "point-timing": "int32_point_demand_study.py",
           "counter-overhead": "counter_overhead_study.py",
           "headers": "test_codeflaws_header_admission.py", "witness": "witness_interoperability.py"}
NEEDS = {"analysis": set(), "units": {"cbmc", "gcc", "clang"}, "functional": {"gcc", "clang"},
         "demand": set(), "cbmc": {"cbmc", "gcc"}, "native": {"archive", "gcc", "clang"},
         "signed": {"archive"}, "coverage": {"archive"}, "timing": {"archive"}, "point-timing": {"archive"},
         "counter-overhead": {"archive"},
         "headers": {"gcc", "clang"}, "witness": {"witness_cbmc", "cpachecker", "gcc"}}
WITNESS_FOLLOWUP_SCRIPTS = ("verify_witness_interoperability.py", "verify_witness_products.py", "analyze_witness_search.py",
                            "witness_projection_controls.py")


class PreconditionFailure(RuntimeError):
    """A configured external tool could not start before the studies."""


class Incomplete(RuntimeError):
    """A selected stage ran, but its declared checks were not all executed."""


class ExecutionFailure(RuntimeError):
    def __init__(self, message, returncode=None, timed_out=False):
        super().__init__(message)
        self.returncode = returncode
        self.timed_out = timed_out


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False)


def same(actual, expected, message):
    require(canonical(actual) == canonical(expected), message)


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key: " + key)
        result[key] = value
    return result


def load(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_object,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError("nonfinite JSON number")))


def save(path, value):
    temporary = path.with_name(path.name + ".writing")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def file_identity(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def snapshot_sources(root=ROOT):
    paths = [root / "reproduce.py"]
    for directory in (root / "src", root / "tests"):
        paths.extend(sorted(directory.rglob("*.py")))
    return {str(path.relative_to(root)): path.read_bytes() for path in paths if path.is_file()}


def reserve_output(path, root=ROOT):
    require(not path.is_symlink() and not path.exists(), "output must be a new directory; existing evidence is preserved")
    path = path.resolve()
    require(not path.is_relative_to(root.resolve()), "output must be outside artifact/")
    path.mkdir(parents=True)
    return path


def selected_checks(values):
    selected = CHECKS if values is None else tuple(name for name in CHECKS if name in values)
    require(bool(selected), "select at least one check")
    if values is not None:
        require(set(values) <= set(CHECKS), "unknown check selected")
    return selected


def study_data(data, name, root=ROOT):
    """Use current descriptive data names; the experiment folder is also supported."""
    path = data / name
    if path.exists():
        return path
    alternative = root / "experiments" / name
    return alternative if alternative.exists() else path


def point_measurements(data, root=ROOT):
    directory = study_data(data, "point-demand", root)
    return directory / "measurements" if (directory / "measurements").exists() else directory


def tool_path(args, name):
    if name == "witness_cbmc":
        return getattr(args, "witness_cbmc", None) or args.cbmc
    return getattr(args, name)


def preconditions(args, selected, root=ROOT):
    """Collect every missing prerequisite before any scientific child starts."""
    failures = []
    if not __debug__:
        failures.append("scientific reproduction requires enabled assertions; run without -O or -OO")
    requirements = set().union(*(NEEDS[name] for name in selected))
    if requirements and os.name != "posix":
        failures.append("the external C studies require a POSIX host")
    if set(selected) != {"analysis"}:
        try:
            if importlib.metadata.version("pycparser") != "3.0":
                failures.append("the supplied scientific environment requires pycparser 3.0")
        except importlib.metadata.PackageNotFoundError:
            failures.append("pycparser is not installed; use the supplied requirements file")
    for name in sorted(requirements):
        path = tool_path(args, name)
        option = "--witness-cbmc or --cbmc" if name == "witness_cbmc" else "--" + name
        if path is None:
            failures.append(option + " is required for the selected checks")
        elif not path.is_file() or (name != "archive" and not os.access(path, os.X_OK)):
            failures.append(option + " does not name a usable " + ("archive" if name == "archive" else "executable"))
    if {"gcc", "clang"} <= requirements and args.gcc is not None and args.clang is not None:
        if args.gcc.resolve() == args.clang.resolve():
            failures.append("GCC and Clang must be distinct executable files")
    for path in args.library_dir:
        if not path.is_dir():
            failures.append("library directory does not exist: " + str(path))
    if args.cpu is not None and (not hasattr(os, "sched_getaffinity") or args.cpu not in os.sched_getaffinity(0)):
        failures.append("--cpu must belong to this process's allowed affinity")
    if {"units", "cbmc"} & set(selected) and shutil.which("prlimit") is None:
        failures.append("prlimit is required by the CBMC runner")
    if "witness" in selected and shutil.which("java") is None:
        failures.append("Java is required by CPAchecker")
    for name in selected:
        if name in SCRIPTS and not (root / "tests" / SCRIPTS[name]).is_file():
            failures.append("missing study entry point: tests/" + SCRIPTS[name])
    if "witness" in selected:
        for name in WITNESS_FOLLOWUP_SCRIPTS:
            if not (root / "tests" / name).is_file():
                failures.append("missing witness completion check: tests/" + name)
    if "units" in selected and not any((root / "tests").glob("test_*.py")):
        failures.append("unit discovery has no test files")
    required_data = []
    if set(selected) & {"functional", "demand"}:
        required_data.append(args.data / "contract-study" / "transport.json")
    if set(selected) & {"functional", "cbmc", "witness"}:
        required_data.append(args.data / "natural-domains" / "requests.json")
    if set(selected) & {"signed", "coverage", "timing", "point-timing", "counter-overhead"} and "native" not in selected:
        required_data.append(args.data / "source-programs" / "normalized-corpus.json")
    if "signed" in selected:
        required_data.append(args.data / "signed-contract" / "requests.json")
    if set(selected) & {"coverage", "timing", "point-timing", "counter-overhead"} and "signed" not in selected:
        required_data.append(args.data / "signed-contract" / "summary.json")
        if set(selected) & {"coverage", "counter-overhead"}:
            required_data.append(args.data / "signed-contract" / "requests.json")
    if set(selected) & {"analysis", "coverage"}:
        required_data.append(root / "tests" / "verify_signed_coverage_study.py")
    if set(selected) & {"analysis", "counter-overhead"}:
        required_data.append(root / "tests" / "verify_counter_overhead_study.py")
    if "counter-overhead" in selected and "point-timing" not in selected:
        required_data.extend(point_measurements(args.data, root) / name for name in ("summary.json", "work.json"))
    counter_references = []
    if "counter-overhead" in selected:
        if "signed" not in selected:
            counter_references.append(args.data / "signed-contract")
        if "point-timing" not in selected:
            counter_references.append(point_measurements(args.data, root))
    if "analysis" in selected:
        counter_references.append(study_data(args.data, "counter-overhead", root))
    for folder in counter_references:
        summary_file = folder / "summary.json"
        if summary_file.is_file():
            try:
                declared = load(summary_file)["records"]
                require(type(declared) is dict, "record inventory must be an object")
                for name in declared:
                    path = (folder / name).resolve()
                    require(path.is_relative_to(folder.resolve()), "reference record escapes its study")
                    required_data.append(path)
            except (ValueError, OSError, KeyError, TypeError) as exc:
                failures.append("invalid counter-overhead reference inventory: " + str(summary_file) + ": " + str(exc))
    if "analysis" in selected:
        required_data.extend(args.data / "receiving-time" / name for name in
                             ("summary.json", "protocol.json", "work.json", "timings.jsonl", "analysis.json", "request-timing-summary.json"))
        required_data.extend(point_measurements(args.data, root) / name for name in
                             ("summary.json", "protocol.json", "work.json", "timings.jsonl", "analysis.json", "request-timing-summary.json"))
        required_data.append(args.data / "signed-contract" / "requests.json")
        required_data.append(args.data / "signed-contract" / "summary.json")
        required_data.append(root / "tests" / "verify_point_demand_study.py")
        required_data.extend(study_data(args.data, "signed-coverage", root) / name for name in
                             ("protocol.json", "coverage-before-union.json", "coverage-before-union-summary.json",
                              "coverage-with-union-outcomes.json", "summary.json"))
        required_data.extend(study_data(args.data, "counter-overhead", root) / name for name in
                             ("summary.json", "protocol.json", "work.json", "timings.jsonl", "analysis.json",
                              "request-timing-summary.json", "derived/receivers.py", "derived/manifest.json"))
    for path in dict.fromkeys(required_data):
        if not path.is_file():
            failures.append("missing input record: " + str(path))
    if "archive" in requirements and args.archive is not None and args.archive.is_file():
        corpus_file = args.data / "source-programs" / "normalized-corpus.json"
        if corpus_file.is_file():
            try:
                expected = load(corpus_file)["archive_sha256"]
                if file_identity(args.archive) != expected:
                    failures.append("the external archive differs from the recorded input corpus")
            except (ValueError, OSError, KeyError) as exc:
                failures.append("could not validate the external archive: " + str(exc))
    return failures


def make_environment(args, output, selected):
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for name in ("CBMC_BINARY", "CBMC_CONTROL_OUTPUT", "CBMC_LIBRARY_DIR"):
        env.pop(name, None)
    if args.library_dir:
        inherited = env.get("LD_LIBRARY_PATH")
        env["LD_LIBRARY_PATH"] = os.pathsep.join([str(p) for p in args.library_dir] + ([inherited] if inherited else []))
        env["CBMC_LIBRARY_DIR"] = str(args.library_dir[0])
    tools = output / "tool-bin"
    available = [(name, getattr(args, name)) for name in ("gcc", "clang") if getattr(args, name) is not None]
    if available:
        tools.mkdir()
        for name, path in available:
            (tools / name).symlink_to(path)
        env["PATH"] = str(tools) + os.pathsep + env.get("PATH", "")
    if args.cbmc is not None:
        env["CBMC_BINARY"] = str(args.cbmc)
        env["CBMC_CONTROL_OUTPUT"] = str(output / DESTINATIONS["units"] / "cbmc-controls")
    return env


def stop_process(process):
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=3)


def run_command(command, cwd, env, stdout, stderr, timeout):
    process = None
    with stdout.open("wb") as out, stderr.open("wb") as err:
        try:
            process = subprocess.Popen([str(value) for value in command], cwd=cwd, env=env,
                                       stdout=out, stderr=err, start_new_session=True)
            try:
                code = process.wait(timeout=timeout)
            except subprocess.TimeoutExpired as exc:
                stop_process(process)
                raise ExecutionFailure("study exceeded the configured timeout", process.returncode, True) from exc
            if code != 0:
                raise ExecutionFailure("study process exited with code " + str(code), code)
            return code
        except BaseException:
            if process is not None:
                stop_process(process)
            raise


def command_for(name, args, selected, output, root=ROOT):
    invoke = [sys.executable, "-B"]
    destination = output / DESTINATIONS[name]
    corpus = ((output / DESTINATIONS["native"]) if "native" in selected else args.data / "source-programs") / "normalized-corpus.json"
    prior = output / DESTINATIONS["signed"] if "signed" in selected else args.data / "signed-contract"
    transport = output / DESTINATIONS["functional"] / "contract-comparison" if "functional" in selected else args.data / "contract-study"
    natural = output / DESTINATIONS["functional"] / "natural-domains" if "functional" in selected else args.data / "natural-domains"
    if name == "units":
        return [*invoke, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"]
    if name == "analysis":
        return None
    command = [*invoke, root / "tests" / SCRIPTS[name]]
    if name == "headers":
        return [*command, "--native-audit", destination, "--gcc", args.gcc, "--clang", args.clang]
    command += ["--output", destination]
    if name == "functional":
        command += ["--child-timeout", str(args.step_timeout)]
    elif name == "demand":
        command += ["--transport-source", transport]
    elif name == "cbmc":
        command += ["--cbmc", args.cbmc, "--natural-data", natural, "--jobs", str(args.jobs)]
    elif name == "native":
        command += ["--archive", args.archive, "--execute-admitted", "--native-work", output / "native-work",
                    "--compiler", args.gcc, "--compiler", args.clang]
    elif name in {"signed", "coverage", "timing", "point-timing", "counter-overhead"}:
        command += ["--corpus", corpus, "--archive", args.archive]
        if name == "coverage":
            command += ["--reference", prior]
        elif name != "signed":
            command += ["--prior", prior]
            if args.cpu is not None:
                command += ["--cpu", str(args.cpu)]
        if name == "counter-overhead":
            point_prior = output / DESTINATIONS["point-timing"] if "point-timing" in selected else point_measurements(args.data, root)
            command += ["--point-prior", point_prior]
    elif name == "witness":
        command += ["--cbmc", tool_path(args, "witness_cbmc"), "--cpachecker", args.cpachecker, "--gcc", args.gcc,
                    "--jobs", str(min(args.jobs, 4))]
    if name in {"cbmc", "witness"}:
        for directory in args.library_dir:
            command += ["--library-dir", directory]
    return command


def witness_followup_commands(args, output, root=ROOT):
    study = output / DESTINATIONS["witness"]
    invoke = [sys.executable, "-B"]
    records = study / "verification.json"
    products = study / "product-equivalence.json"
    statistics = study / "search-statistics.json"
    controls = output / "witness-input-controls"
    return [
        ("record-verification", [*invoke, root / "tests/verify_witness_interoperability.py",
                                 "--study", study, "--output", records], records,
         "independent analysis of the newly executed witness campaign"),
        ("product-equivalence", [*invoke, root / "tests/verify_witness_products.py",
                                 "--study", study, "--output", products], products,
         "isolated executed/current emission and exact retained C-product equality"),
        ("search-statistics", [*invoke, root / "tests/analyze_witness_search.py",
                               "--study", study, "--output", statistics], statistics,
         "descriptive analysis of the newly recorded search counters"),
        ("input-controls", [*invoke, root / "tests/witness_projection_controls.py",
                             "--study", study, "--output", controls,
                             "--cpachecker", args.cpachecker, "--gcc", args.gcc,
                             "--timeout", "45", "--cpu-limit", "30"], controls / "summary.json",
         "three new native and external-validator control executions"),
    ]


def validate_witness_followup(name, result_file):
    result = load(result_file)
    expected = {"record-verification": "PASS_RETAINED_WITNESS_RECORDS",
                "product-equivalence": "PASS_IDENTICAL_WITNESS_PRODUCTS",
                "search-statistics": "PASS_MATCHED_STATISTICS_RECONCILIATION",
                "input-controls": "PASS_INPUT_CONSTRAINT_CONTROLS"}
    same(result["outcome"], expected[name], "witness completion check: " + name)
    if name == "record-verification":
        same(result["requests"], 804, "independently reconciled witness population")
        same(result["checked"]["control_processes"], 18, "independently reconciled negative controls")
        return {"outcome": result["outcome"], "requests": 804, "negative_controls": 18}
    if name == "search-statistics":
        same(len(result["requests"]), 594, "all planned refutations in search analysis")
        same(result["groups"]["all"]["planned_refutations"], 594, "search-analysis population")
        return {"outcome": result["outcome"], "planned_refutations": 594}
    if name == "product-equivalence":
        for field, expected in (("requests", 804), ("identical_products", 804),
                                ("isolated_emitter_processes", 2), ("unchanged_during_check", True)):
            same(result[field], expected, "witness product equality: " + field)
        return {"outcome": result["outcome"], "requests": 804, "identical_products": 804}
    for field in ("planned_controls", "actual_native_executions", "actual_validator_runs", "expected_unconfirmed"):
        same(result[field], 3, "witness input-control completion: " + field)
    return {"outcome": result["outcome"], "native_executions": 3, "external_validator_runs": 3}


def run_witness_followups(args, output, row, env, report, report_path, source_start, root=ROOT):
    commands = witness_followup_commands(args, output, root)
    row["followups"] = [{"name": name, "status": "NOT_RUN", "command": [str(v) for v in command],
                         "output": str(result_file.relative_to(output)), "execution_kind": kind,
                         "returncode": None}
                        for name, command, result_file, kind in commands]
    save(report_path, report)
    for state, (name, command, result_file, _kind) in zip(row["followups"], commands):
        require(snapshot_sources(root) == source_start, "source files changed before witness " + name)
        stdout = output / "logs" / ("witness-" + name + ".stdout.log")
        stderr = output / "logs" / ("witness-" + name + ".stderr.log")
        state.update(status="RUNNING", started_utc=utc_now(), stdout=str(stdout.relative_to(output)),
                     stderr=str(stderr.relative_to(output)))
        save(report_path, report)
        started = time.monotonic()
        try:
            state["returncode"] = run_command(command, root, env, stdout, stderr, args.step_timeout)
            state["validation"] = validate_witness_followup(name, result_file)
            require(snapshot_sources(root) == source_start, "source files changed during witness " + name)
            state["status"] = "PASS"
        except BaseException as exc:
            state.update(status="FAILED", error_type=type(exc).__name__, error=str(exc))
            row["failed_followup"] = name
            if isinstance(exc, ExecutionFailure):
                state.update(returncode=exc.returncode, timed_out=exc.timed_out)
            for pending in row["followups"]:
                if pending["status"] == "NOT_RUN":
                    pending["reason"] = "not reached after an earlier witness completion check failed"
            raise
        finally:
            state.update(ended_utc=utc_now(), elapsed_seconds=time.monotonic() - started)
            save(report_path, report)


def _ratio_quantiles(values):
    values = sorted(values)
    return {key: values[math.ceil(fraction * len(values)) - 1]
            for key, fraction in (("p10", .1), ("p25", .25), ("p50", .5), ("p75", .75), ("p90", .9))}


def verify_five_arm(directory, reference):
    """Recompute existing five-arm medians and clusters without the writer's analyzer."""
    protocol, summary, analysis = (load(directory / name) for name in ("protocol.json", "summary.json", "analysis.json"))
    work, recorded = load(directory / "work.json"), load(directory / "request-timing-summary.json")
    oracle = {row["id"]: row for row in load(reference)}
    arms = ("full", "live", "projected_live", "demand", "direct_record")
    same(protocol["arms"], list(arms), "five-arm inventory")
    same(protocol["repetitions_per_request"], 10, "five-arm repetitions")
    same(summary["outcome"], "PASS", "five-arm study did not finish")
    require(len(work) == len({row["id"] for row in work}) == len(oracle) == 1478, "five-arm request population")
    same(set_as_list(oracle), sorted(row["id"] for row in work), "five-arm reference identities")
    base = (0, 1, 4, 2, 3)
    forward = [tuple(arms[(value + offset) % 5] for value in base) for offset in range(5)]
    orders = forward + [tuple(reversed(order)) for order in forward]
    same(protocol["orders"], [list(order) for order in orders], "five-arm Williams orders")
    times = {row["id"]: {arm: [] for arm in arms} for row in work}
    lines = (directory / "timings.jsonl").read_text().splitlines()
    require(len(lines) == len(work) * 10, "five-arm measured call groups")
    offset = 0
    for repetition in range(10):
        schedule = list(range(len(work)))
        random.Random(protocol["seed"] + repetition).shuffle(schedule)
        for position, index in enumerate(schedule):
            row = json.loads(lines[offset], object_pairs_hook=_object)
            same(row["id"], work[index]["id"], "five-arm shuffled request")
            same(row["repetition"], repetition, "five-arm repetition")
            same(row["schedule_position"], position, "five-arm schedule position")
            same(row["order"], list(orders[(repetition + index) % 10]), "five-arm measured order")
            same(sorted(row["nanoseconds"]), sorted(arms), "five-arm measured durations")
            for arm, value in row["nanoseconds"].items():
                require(type(value) is int and value > 0, "duration must be a positive actual nanosecond count")
                times[row["id"]][arm].append(value)
            offset += 1
    rebuilt = []
    for row in work:
        old = oracle[row["id"]]
        for key in ("id", "subject", "problem", "stage", "sources", "points", "status", "witness"):
            same(row[key], old[key], "five-arm canonical reference: " + key)
        for arm in arms:
            same({k: row["results"][arm][k] for k in ("status", "witness")},
                 {k: old[k] for k in ("status", "witness")}, "five-arm result agreement")
        medians = {arm: statistics.median(times[row["id"]][arm]) for arm in arms}
        rebuilt.append({key: row[key] for key in ("id", "subject", "problem", "stage", "status", "role")} |
                       {"median_ns": medians, "demand_over_full": medians["demand"] / medians["full"],
                        "demand_over_live": medians["demand"] / medians["live"]})
    same(rebuilt, recorded, "five-arm per-request statistics from raw measurements")
    for stage in ("repair", "union"):
        rows = [row for row in work if row["stage"] == stage]
        stats = [row for row in rebuilt if row["stage"] == stage]
        current = analysis[stage]
        same(current["requests"], len(rows), "five-arm stage size")
        same(len(rows), 739, "five-arm complete stage")
        same(current["cells"], {arm: sum(row["results"][arm]["semantic_cells"] for row in rows) for arm in arms}, "five-arm cell totals")
        same(current["problems"], len({row["problem"] for row in rows}), "five-arm problem count")
        same(current["status"], dict(Counter(row["status"] for row in rows)), "five-arm status counts")
        same(current["role"], dict(Counter(row["role"] for row in rows)), "five-arm candidate classes")
        same(current["sum_request_median_ns"], {arm: sum(row["median_ns"][arm] for row in stats) for arm in arms}, "five-arm aggregate request medians")
        same(current["demand_slower_than_full"], sum(row["demand_over_full"] > 1 for row in stats), "five-arm slower-than-full count")
        same(current["demand_slower_than_live"], sum(row["demand_over_live"] > 1 for row in stats), "five-arm slower-than-live count")
        for ratio in ("demand_over_full", "demand_over_live"):
            same(current[ratio], _ratio_quantiles([row[ratio] for row in stats]), "five-arm ratio quantiles")
        groups = {}
        for row in stats:
            group = groups.setdefault(row["problem"], {arm: 0 for arm in arms})
            for arm, value in row["median_ns"].items():
                group[arm] += value
        same(sorted(groups), sorted(row["problem"] for row in current["problem_ratios"]), "five-arm problem inventory")
        for row in current["problem_ratios"]:
            total = groups[row["problem"]]
            same(row["sum_request_median_ns"], total, "five-arm problem request totals")
            same(row["demand_over_live"], total["demand"] / total["live"], "five-arm problem ratio")
            same(row["demand_over_full"], total["demand"] / total["full"], "five-arm problem ratio")
            same(row["requests"], sum(item["problem"] == row["problem"] for item in stats), "five-arm problem size")
        for baseline in ("full", "live"):
            ratios = [total["demand"] / total[baseline] for total in groups.values()]
            same(current["problem_demand_slower_than_" + baseline], sum(value > 1 for value in ratios), "five-arm problem direction")
            same(current["problem_median_demand_over_" + baseline], statistics.median(ratios), "five-arm problem median ratio")
    same(summary["timed_receiving_calls"], 73900, "five-arm actual timed call count")
    same(summary["preflight_receiving_calls"], 7390, "five-arm preflight calls")
    same(summary["work"], analysis, "five-arm summary/analysis consistency")
    return {"requests": 1478, "timed_receiving_calls": 73900,
            "outcome": "PASS_RETAINED_FIVE_ARM_ANALYSIS", "fresh_receiving_calls": 0}


def set_as_list(mapping):
    return sorted(mapping)


def run_record_verifier(command, destination, prefix, root, timeout):
    stdout, stderr = destination / (prefix + ".stdout.log"), destination / (prefix + ".stderr.log")
    try:
        return run_command(command, root, dict(os.environ), stdout, stderr, timeout)
    except ExecutionFailure as exc:
        # The scientific writer may already have exited successfully. Preserve
        # that return code and identify the failing verification child instead.
        exc.validation_process = {"command": [str(value) for value in command],
                                  "returncode": exc.returncode, "timed_out": exc.timed_out,
                                  "stdout": str(stdout), "stderr": str(stderr)}
        raise


def verify_coverage_records(study, reference, destination, root=ROOT, timeout=21600):
    """Run the archive-free verifier, retaining its actual process outcome."""
    target = destination / "coverage-verification.json"
    command = [sys.executable, "-B", root / "tests/verify_signed_coverage_study.py",
               "--study", study, "--reference", reference, "--output", target]
    code = run_record_verifier(command, destination, "coverage-verification", root, timeout)
    result = load(target)
    same(result["outcome"], "PASS_INDEPENDENT_SIGNED_COVERAGE_RECOMPUTATION", "independent signed coverage audit")
    same(result["combinations"], 739, "complete signed support-coverage population")
    require(result["local_values"] > 0, "signed coverage must evaluate retained local rules")
    return {**result, "command": [str(value) for value in command], "returncode": code}


def verify_counter_records(study, reference, point_reference, destination, root=ROOT, timeout=21600,
                           filename="independent-verification.json"):
    target = destination / filename
    command = [sys.executable, "-B", root / "tests/verify_counter_overhead_study.py", study,
               "--reference", reference, "--point-reference", point_reference, "--output", target]
    code = run_record_verifier(command, destination, "counter-overhead-verification", root, timeout)
    result = load(target)
    same(result["outcome"], "PASS_INDEPENDENT_COUNTER_OVERHEAD_RECOMPUTATION", "independent measurement-overhead audit")
    for field, expected in (("requests", 1478), ("preflight_receiving_calls", 7390), ("timed_receiving_calls", 73900)):
        same(result[field], expected, "counter-overhead verification: " + field)
    return {**result, "command": [str(value) for value in command], "returncode": code}


def analyze_retained(data, destination, root=ROOT, *, timeout=21600):
    destination.mkdir()
    reference = data / "signed-contract" / "requests.json"
    five = verify_five_arm(data / "receiving-time", reference)
    # The point-study verifier is a separate implementation from its writer.
    sys.path.insert(0, str(root / "tests"))
    from verify_point_demand_study import verify
    point = verify(point_measurements(data, root), reference)
    coverage = verify_coverage_records(study_data(data, "signed-coverage", root), data / "signed-contract",
                                       destination, root, timeout)
    counter = verify_counter_records(study_data(data, "counter-overhead", root), reference,
                                     point_measurements(data, root) / "work.json", destination, root, timeout,
                                     "counter-overhead-verification.json")
    result = {"outcome": "PASS_RETAINED_ANALYSIS", "five_arm": five, "point_demand": point,
              "signed_coverage": coverage,
              "counter_overhead": counter,
              "scope": "Recomputed raw recorded observations; no new receiving measurement, native program run or external verification process."}
    save(destination / "analysis.json", result)
    return result


def check_units(stdout, stderr, destination):
    text = stdout.read_text(errors="replace") + stderr.read_text(errors="replace")
    matches = re.findall(r"^Ran (\d+) tests? in ", text, re.M)
    require(len(matches) == 1 and int(matches[0]) > 0, "unit runner did not report one nonempty discovery")
    require(re.search(r"^OK(?: \([^\n]*\))?\s*$", text, re.M) is not None, "unit discovery did not succeed")
    skipped = sum(map(int, re.findall(r"skipped=(\d+)", text)))
    if skipped:
        raise Incomplete(str(skipped) + " unit-test methods were skipped")
    controls = load(destination / "cbmc-controls" / "controls.json")
    require(len(controls) == 22, "all 22 external CBMC controls must run")
    require(all(row["expected"] == row["direct"] == row["cbmc"] for row in controls), "external unit control disagreement")
    return {"tests": int(matches[0]), "skipped": 0, "external_cbmc_controls": len(controls)}


def validate_step(name, directory, stdout, stderr, args, selected, output, root=ROOT):
    if name == "units":
        return check_units(stdout, stderr, directory)
    if name == "functional":
        result = load(directory / "complete-reproduction.json")
        same(result["outcome"], "PASS_COMPLETE_REPRODUCTION", "functional reproduction incomplete")
        same(result["implementation_unchanged_during_reproduction"], True, "functional source changed")
        same(result["structured_requests"], 380, "complete structured population")
        return {"outcome": result["outcome"], "structured_requests": result["structured_requests"],
                "scope": "Functional campaigns and their internal native controls; separate source/timing/witness stages remain separate."}
    if name == "headers":
        result = load(directory / "report.json")
        same(result["case_count"], 30, "header case count")
        same(result["compiler_count"], 2, "header compiler count")
        same(result["native_compilations"], 60, "header compilation attempts")
        same(result["native_executions"], 42, "header executions")
        require(all(row["current"]["admitted"] == row["admitted"] for row in result["records"]), "header admission expectation")
        return {key: result[key] for key in ("case_count", "compiler_count", "native_compilations", "native_executions")}
    result = load(directory / "summary.json")
    if name == "demand":
        same(result["outcome"], "PASS", "demand study incomplete")
        same({k: v["requests"] for k, v in result["corpora"].items()}, {"core": 380, "grammar": 400}, "unsigned populations")
        return {"outcome": result["outcome"], "canonical_requests": 780}
    if name == "cbmc":
        for key, expected in (("requests", 804), ("status_agreements", 804), ("unresolved_indices", []),
                              ("disagreement_indices", []), ("source_and_inputs_stable", True)):
            same(result[key], expected, "external C verification: " + key)
        return {"requests": 804, "status_agreements": 804}
    if name == "native":
        same(result["native_executed"], True, "original sources were not executed")
        native = load(directory / "native-summary.json")
        for key, expected in (("compilers", 2), ("compiled_external_source_units", 352),
                              ("actual_external_program_executions", 15368), ("native_interpreter_agreements", 15368),
                              ("failures", []), ("source_bytes_rewritten", False), ("raw_input_bytes_preserved", True)):
            same(native[key], expected, "native execution: " + key)
        return {key: native[key] for key in ("compilers", "compiled_external_source_units", "actual_external_program_executions", "native_interpreter_agreements")}
    if name == "signed":
        same(result["outcome"], "PASS", "signed study incomplete")
        same(result["requests"], 1478, "signed request population")
        same(result["identical_full_and_direct_records"], 1478, "signed record agreement")
        reference = load(args.data / "signed-contract" / "requests.json")
        current = load(directory / "requests.json")
        same([{k: v for k, v in row.items() if k != "timing_ms"} for row in current],
             [{k: v for k, v in row.items() if k != "timing_ms"} for row in reference], "current signed scientific observations versus retained reference")
        return {"requests": 1478, "identical_full_and_direct_records": 1478, "canonical_reference_agreement": True}
    if name == "coverage":
        same(result["outcome"], "PASS_SIGNED_COVERAGE_AUDIT", "signed support-coverage study incomplete")
        same(result["source_inputs_unchanged"], True, "signed support-coverage inputs changed")
        same(result["groups"]["all"]["combinations"], 739, "signed support-coverage population")
        reference = output / DESTINATIONS["signed"] if "signed" in selected else args.data / "signed-contract"
        return verify_coverage_records(directory, reference, directory, root, args.step_timeout)
    if name in {"timing", "point-timing"}:
        reference = (output / DESTINATIONS["signed"] if "signed" in selected else args.data / "signed-contract") / "requests.json"
        if name == "timing":
            verified = verify_five_arm(directory, reference)
            verified["outcome"] = "PASS_NEW_FIVE_ARM_MEASUREMENTS"
            verified["fresh_receiving_calls"] = 73900
        else:
            sys.path.insert(0, str(root / "tests"))
            from verify_point_demand_study import verify
            verified = verify(directory, reference)
            verified["fresh_receiving_calls"] = 70944
        return verified
    if name == "counter-overhead":
        for field, expected in (("outcome", "PASS_COUNTER_OVERHEAD_STUDY"), ("requests", 1478),
                                ("preflight_receiving_calls", 7390), ("timed_receiving_calls", 73900),
                                ("source_inputs_unchanged", True), ("canonical_disagreements", 0),
                                ("value_trace_disagreements", 0)):
            same(result[field], expected, "counter-overhead execution: " + field)
        reference = (output / DESTINATIONS["signed"] if "signed" in selected else args.data / "signed-contract") / "requests.json"
        point_prior = output / DESTINATIONS["point-timing"] if "point-timing" in selected else point_measurements(args.data, root)
        verified = verify_counter_records(directory, reference, point_prior / "work.json", directory, root, args.step_timeout)
        return verified
    if name == "witness":
        same(result["outcome"], "COMPLETE_WITH_RECORDED_EXTERNAL_OUTCOMES", "witness campaign incomplete")
        same(result["source_inputs_and_tools_unchanged"], True, "witness execution inputs changed")
        same(result["producer_disagreements"], [], "witness producer disagreement")
        same(result["direct_cpa_disagreements"], [], "independent verifier disagreement")
        same(result["control_runs"], 18, "witness negative control population")
        protocol = load(directory / "protocol.json")
        same(protocol["planned_requests"], 804, "witness planned population")
        same(protocol["pilot_limit"], None, "witness pilot cannot pass full reproduction")
        cases = load(directory / "cases.json")
        same(sorted(row["index"] for row in cases), list(range(804)), "complete unique witness cases")
        return {"requests": len(cases), "outcome": result["outcome"],
                "groups": result["groups"], "control_runs": result["control_runs"],
                "scope": "Complete external campaign with every tool outcome retained; completion is not universal witness confirmation."}
    raise ValueError(name)


def run(args, root=ROOT):
    selected = selected_checks(args.checks)
    output = reserve_output(args.output, root)
    report_path = output / "reproduction.json"
    report = {"outcome": "PRECONDITION_CHECK", "started_utc": utc_now(), "selected_checks": list(selected),
              "complete_selection": tuple(selected) == CHECKS, "python": sys.version,
              "artifact": str(root), "data": str(args.data), "steps": [
                  {"name": name, "status": "NOT_RUN" if name in selected else "NOT_REQUESTED"} for name in CHECKS],
              "interpretation": "Each PASS stage executed and checked its named work. Retained-data analysis never replaces an execution stage."}
    save(report_path, report)
    try:
        problems = preconditions(args, selected, root)
    except BaseException as exc:
        problems = [type(exc).__name__ + ": " + str(exc)]
    if problems:
        for row in report["steps"]:
            if row["status"] == "NOT_RUN":
                row["reason"] = "prerequisite check failed; no study started"
        report.update(outcome="FAILED_PRECONDITION", problems=problems, scientific_studies_started=0, ended_utc=utc_now(), exit_code=2)
        save(report_path, report)
        print(json.dumps({"outcome": report["outcome"], "problems": problems}), flush=True)
        return 2
    source_start = snapshot_sources(root)
    exit_code = 1
    try:
        env = make_environment(args, output, selected)
        logs = output / "logs"
        logs.mkdir()
        requirements = set().union(*(NEEDS[name] for name in selected)) - {"archive"}
        report["tool_probes"] = []
        probed = {}
        for tool in sorted(requirements):
            stdout, stderr = logs / ("tool-" + tool + ".stdout.log"), logs / ("tool-" + tool + ".stderr.log")
            executable = tool_path(args, tool)
            family = "cbmc" if tool == "witness_cbmc" else tool
            key = (family, str(executable.resolve()))
            command = [executable, "--version"]
            probe = {"tool": tool.replace("_", "-"), "command": [str(value) for value in command], "status": "RUNNING"}
            report["tool_probes"].append(probe)
            if key in probed:
                probe.update(status="READY", shared_startup_probe=probed[key])
                continue
            try:
                probe["returncode"] = run_command(command, root, env, stdout, stderr, 30)
                text = (stdout.read_text(errors="replace") + stderr.read_text(errors="replace")).lower()
                token = {"gcc": "gcc", "clang": "clang", "cpachecker": "cpachecker"}.get(family)
                if token is not None:
                    require(token in text or (family == "gcc" and "free software foundation" in text),
                            "configured " + tool + " did not identify its expected tool family")
                else:
                    require(bool(text.strip()), "configured tool returned no identity information")
                probe["status"] = "READY"
                probed[key] = probe["tool"]
            except BaseException as exc:
                probe.update(status="FAILED", error=str(exc))
                raise PreconditionFailure(tool + " startup probe failed: " + str(exc)) from exc
        save(report_path, report)
        for name in selected:
            row = next(row for row in report["steps"] if row["name"] == name)
            destination = output / DESTINATIONS[name]
            stdout, stderr = logs / (name + ".stdout.log"), logs / (name + ".stderr.log")
            require(snapshot_sources(root) == source_start, "source files changed before " + name)
            row.update(status="RUNNING", started_utc=utc_now(), output=DESTINATIONS[name],
                       stdout=str(stdout.relative_to(output)), stderr=str(stderr.relative_to(output)), returncode=None)
            report["outcome"], report["active_step"] = "RUNNING", name
            save(report_path, report)
            print(json.dumps({"step": name, "status": "RUNNING"}), flush=True)
            started = time.monotonic()
            try:
                if name == "analysis":
                    row["validation"] = analyze_retained(args.data, destination, root, timeout=args.step_timeout)
                    stdout.write_text("Retained raw observations independently recomputed.\n")
                    stderr.write_text("")
                    row["returncode"] = None
                    row["execution_kind"] = "retained-record analysis"
                else:
                    if name == "units":
                        destination.mkdir()
                    command = command_for(name, args, selected, output, root)
                    row["command"] = [str(value) for value in command]
                    row["execution_kind"] = "new study execution"
                    save(report_path, report)
                    row["returncode"] = run_command(command, root, env, stdout, stderr, args.step_timeout)
                    row["validation"] = validate_step(name, destination, stdout, stderr, args, selected, output, root)
                    if name == "witness":
                        run_witness_followups(args, output, row, env, report, report_path, source_start, root)
                require(snapshot_sources(root) == source_start, "source files changed during " + name)
                row["status"] = "PASS"
            except Incomplete as exc:
                row.update(status="INCOMPLETE", error=str(exc))
                raise
            except BaseException as exc:
                row.update(status="FAILED", error_type=type(exc).__name__, error=str(exc))
                if isinstance(exc, ExecutionFailure):
                    if hasattr(exc, "validation_process"):
                        row["failed_validation_process"] = exc.validation_process
                    elif "failed_followup" not in row:
                        row.update(returncode=exc.returncode, timed_out=exc.timed_out)
                raise
            finally:
                row.update(ended_utc=utc_now(), elapsed_seconds=time.monotonic() - started)
                save(report_path, report)
                print(json.dumps({"step": name, "status": row["status"]}), flush=True)
        report["outcome"] = "PASS_COMPLETE" if tuple(selected) == CHECKS else "PASS_SELECTED_CHECKS"
        exit_code = 0
    except PreconditionFailure as exc:
        report.update(outcome="FAILED_PRECONDITION", problems=[str(exc)], scientific_studies_started=0)
        exit_code = 2
    except Incomplete as exc:
        report.update(outcome="INCOMPLETE", error=str(exc))
        exit_code = 2
    except BaseException as exc:
        report.update(outcome="FAILED", error_type=type(exc).__name__, error=str(exc))
        (output / "failure.log").write_text(traceback.format_exc())
        exit_code = 1
    finally:
        try:
            require(snapshot_sources(root) == source_start, "scientific implementation changed during reproduction")
            report["source_unchanged_during_run"] = True
        except BaseException as exc:
            report.update(outcome="FAILED", source_unchanged_during_run=False, final_error=str(exc))
            exit_code = 1
        for row in report["steps"]:
            if row["status"] == "NOT_RUN":
                row["reason"] = "not reached after an earlier failure"
            elif row["status"] == "NOT_REQUESTED":
                row["reason"] = "outside the explicit --checks selection"
        report.update(active_step=None, ended_utc=utc_now(), exit_code=exit_code)
        save(report_path, report)
    print(json.dumps({"outcome": report["outcome"], "report": str(report_path)}), flush=True)
    return exit_code


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--output", type=Path, required=True, help="new directory outside artifact/")
    result.add_argument("--checks", nargs="+", choices=CHECKS, help="explicit subset; default executes every study")
    result.add_argument("--data", type=Path, default=ROOT / "data", help="descriptively named retained data directories")
    result.add_argument("--archive", type=Path)
    result.add_argument("--cbmc", type=Path)
    result.add_argument("--witness-cbmc", type=Path,
                        help="optional distinct producer executable for the witness study; defaults to --cbmc")
    result.add_argument("--cpachecker", type=Path)
    result.add_argument("--gcc", type=Path, default=Path(shutil.which("gcc")) if shutil.which("gcc") else None)
    result.add_argument("--clang", type=Path, default=Path(shutil.which("clang")) if shutil.which("clang") else None)
    result.add_argument("--library-dir", type=Path, action="append", default=[])
    result.add_argument("--cpu", type=int, help="optional allowed CPU for each repeated timing child")
    result.add_argument("--jobs", type=int, default=1, help="external verifier workers, 1 to 4; timing remains serial")
    result.add_argument("--step-timeout", type=float, default=21600.0,
                        help="finite positive wall limit per study command in seconds (default: %(default)s)")
    return result


def main():
    if not __debug__:
        raise SystemExit("scientific reproduction requires enabled assertions; run without -O or -OO")
    arguments = parser()
    args = arguments.parse_args()
    if not 1 <= args.jobs <= 4 or not math.isfinite(args.step_timeout) or args.step_timeout <= 0:
        arguments.error("jobs must be 1..4 and step-timeout finite and positive")
    for name in ("data", "archive", "cbmc", "witness_cbmc", "cpachecker", "gcc", "clang"):
        value = getattr(args, name)
        if value is not None:
            setattr(args, name, value.resolve())
    args.library_dir = [path.resolve() for path in args.library_dir]
    return run(args)


if __name__ == "__main__":
    def interrupted(signum, _frame):
        raise InterruptedError("received signal " + str(signum))
    signal.signal(signal.SIGTERM, interrupted)
    raise SystemExit(main())

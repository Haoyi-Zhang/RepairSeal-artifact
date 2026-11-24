"""Recheck signed exact-point work and measure balanced repeated receiving time.

All five arms reconstruct the same source request on every call. Timed full
receiving starts from a decoded packet; its production and transport decoding
are outside the interval. The direct-record arm additionally returns a complete
record. Its output contract is kept separate from decision-only direct arms.

Ten Williams orders balance each arm's position and its immediate predecessor
within each request. Request order is independently shuffled in every block
using a recorded seed. Every timed result is compared outside the timed region
with the retained concrete-oracle decision and deterministic cell count.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gc
import hashlib
import json
import os
from pathlib import Path
import platform
import random
import statistics
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]
import proof_dag_checker as core
import int32_circuit as signed
import int32_baselines as baselines
import int32_contract_study as retained
from scientific_driver import new_output_directory, require_assertions

ARMS = ("full", "live", "projected_live", "demand", "direct_record")
SOURCE_NAMES = (
    "src/proof_dag_checker.py", "src/demand_evaluator.py",
    "src/int32_circuit.py", "src/codeflaws_int32_bridge.py",
    "tests/int32_baselines.py", "tests/scientific_driver.py",
    "tests/int32_contract_study.py", "tests/int32_evaluator_study.py")


def sha(path):
    return retained.file_hash(path)


def save(path, value):
    retained.save(path, value)


def same(left, right, context):
    retained.same(left, right, context)


def source_bindings():
    return {name: sha(ROOT / name) for name in SOURCE_NAMES}


def orders():
    base = (0, 1, 4, 2, 3)
    forward = [tuple(ARMS[(value + offset) % 5] for value in base) for offset in range(5)]
    result = forward + [tuple(reversed(row)) for row in forward]
    positions = Counter((arm, i) for row in result for i, arm in enumerate(row))
    preceding = Counter(pair for row in result for pair in zip(row, row[1:]))
    same(dict(positions), {(arm, i): 2 for arm in ARMS for i in range(5)}, "position balance")
    same(dict(preceding), {(a, b): 2 for a in ARMS for b in ARMS if a != b}, "predecessor balance")
    return result


def invoke(arm, task, packet):
    if arm == "full": return signed.verify_evidence(task, packet)
    if arm == "live": return baselines.evaluate_live(task)
    if arm == "projected_live": return baselines.evaluate_projected_live(task)
    if arm == "demand": return signed.evaluate_direct(task)
    if arm == "direct_record": return signed.evaluate_with_record(task)
    raise ValueError(arm)


def unpack(arm, result):
    return result[0] if arm == "direct_record" else result


def quantiles(values):
    values = sorted(values)
    # Empirical inverse CDF: position ceil(p*n), with no interpolation.
    import math
    return {name: values[max(0, math.ceil(fraction * len(values)) - 1)]
            for name, fraction in (("p10", .1), ("p25", .25), ("p50", .5), ("p75", .75), ("p90", .9))}


def environment():
    cpu = None
    path = Path("/proc/cpuinfo")
    if path.exists():
        for line in path.read_text().splitlines():
            if line.startswith("model name"):
                cpu = line.split(":", 1)[1].strip()
                break
    return {"python": sys.version, "platform": platform.platform(),
            "pycparser": __import__("pycparser").__version__, "processor": cpu,
            "affinity": sorted(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else None,
            "clock": vars(time.get_clock_info("perf_counter")),
            "gc_enabled": gc.isenabled(), "gc_threshold": list(gc.get_threshold()),
            "process_workers": 1}


def analyze(work, timings, output):
    by_id = {row["id"]: row for row in work}
    same(len(by_id), len(work), "unique work request identities")
    durations = {key: {arm: [] for arm in ARMS} for key in by_id}
    visits = {key: [] for key in by_id}
    for row in timings:
        same(sorted(row["nanoseconds"]), sorted(ARMS), "complete measured arms")
        same(sorted(row["order"]), sorted(ARMS), "measured order permutation")
        if any(type(value) is not int or value <= 0 for value in row["nanoseconds"].values()):
            raise ValueError("receiving duration must be a positive integer nanosecond count")
        visits[row["id"]].append((row["repetition"], tuple(row["order"])))
        for arm in ARMS:
            durations[row["id"]][arm].append(row["nanoseconds"][arm])
    for key, rows in visits.items():
        same(sorted(row[0] for row in rows), list(range(10)), (key, "one measurement per block"))
        same(sorted(row[1] for row in rows), sorted(orders()), (key, "all balanced orders"))
    request_stats = []
    for key, row in by_id.items():
        medians = {arm: statistics.median(durations[key][arm]) for arm in ARMS}
        request_stats.append({"id": key, "subject": row["subject"], "problem": row["problem"],
                              "stage": row["stage"], "status": row["status"], "role": row["role"],
                              "median_ns": medians,
                              "demand_over_full": medians["demand"] / medians["full"],
                              "demand_over_live": medians["demand"] / medians["live"]})
    summaries = {}
    for stage in ("repair", "union"):
        rows = [row for row in work if row["stage"] == stage]
        stats = [row for row in request_stats if row["stage"] == stage]
        aggregate = {"requests": len(rows), "problems": len({r["problem"] for r in rows}),
                     "cells": {arm: sum(r["results"][arm]["semantic_cells"] for r in rows) for arm in ARMS},
                     "sum_request_median_ns": {arm: sum(r["median_ns"][arm] for r in stats) for arm in ARMS},
                     "status": dict(Counter(r["status"] for r in rows)),
                     "role": dict(Counter(r["role"] for r in rows)),
                     "demand_slower_than_full": sum(r["demand_over_full"] > 1 for r in stats),
                     "demand_slower_than_live": sum(r["demand_over_live"] > 1 for r in stats),
                     "demand_over_full": quantiles([r["demand_over_full"] for r in stats]),
                     "demand_over_live": quantiles([r["demand_over_live"] for r in stats])}
        per_problem = []
        for problem in sorted({r["problem"] for r in stats}):
            subset = [r for r in stats if r["problem"] == problem]
            summed = {arm: sum(r["median_ns"][arm] for r in subset) for arm in ARMS}
            per_problem.append({"problem": problem, "requests": len(subset), "sum_request_median_ns": summed,
                                "demand_over_full": summed["demand"] / summed["full"],
                                "demand_over_live": summed["demand"] / summed["live"]})
        aggregate["problem_ratios"] = per_problem
        aggregate["problem_demand_slower_than_full"] = sum(r["demand_over_full"] > 1 for r in per_problem)
        aggregate["problem_demand_slower_than_live"] = sum(r["demand_over_live"] > 1 for r in per_problem)
        aggregate["problem_median_demand_over_full"] = statistics.median(r["demand_over_full"] for r in per_problem)
        aggregate["problem_median_demand_over_live"] = statistics.median(r["demand_over_live"] for r in per_problem)
        summaries[stage] = aggregate
    save(output / "request-timing-summary.json", request_stats)
    save(output / "analysis.json", summaries)
    return summaries


def run(args, output):
    before = source_bindings()
    prior = json.loads((args.prior / "summary.json").read_text())
    same(prior["outcome"], "PASS", "retained oracle run")
    for name, expected in prior["source_bindings"].items():
        same(sha(ROOT / name), expected, (name, "retained implementation"))
    for name, expected in prior["records"].items():
        same(sha(args.prior / name), expected, (name, "retained record"))
    corpus, raw, _admitted, corpus_sha = retained.load_inputs(args.corpus, args.archive)
    same(corpus_sha, prior["corpus_sha256"], "shared corpus")
    _eligible, cases, _needed = retained.populations(corpus)
    previous = json.loads((args.prior / "requests.json").read_text())
    indexed = {row["id"]: row for row in previous}
    task_rows = []
    for subject, candidate_hash in cases:
        sources = {"original": subject["original_sha"], "candidate": candidate_hash,
                   "reference": subject["reference_sha"]}
        role = ("own_reference" if candidate_hash == subject["reference_sha"] else
                "own_original" if candidate_hash == subject["original_sha"] else "cross_source")
        for stage in ("repair", "union"):
            points = sorted({tuple(test["input"]) for test in subject["tests"]
                             if stage == "union" or test["split"] == "repair"})
            task = {"kind": signed.PROFILE, "id": f"{subject['id']}-{candidate_hash[:12]}-{stage}",
                    "policy": "reference-everywhere", "points": [list(p) for p in points],
                    "sources": {key: raw[value].decode("utf-8") for key, value in sources.items()}}
            old = indexed[task["id"]]
            same(signed.task_identity(task), old["task_sha256"], "exact retained request")
            task_rows.append((task, old, role))
    same(len(task_rows), len(previous), "complete request population")
    design = orders()
    protocol = {"schema": "repairseal-signed-evaluator-protocol-v1", "source_bindings": before,
                "corpus_sha256": corpus_sha, "archive_sha256": corpus["archive_sha256"],
                "prior_summary_sha256": sha(args.prior / "summary.json"),
                "prior_records": prior["records"], "requests": len(task_rows),
                "arms": list(ARMS), "repetitions_per_request": 10, "seed": args.seed,
                "orders": design, "environment": environment(),
                "measurement": "perf_counter_ns around complete receiving API call; verification outside interval",
                "included": ["fresh admission and source reconstruction", "semantic evaluation", "all enabled counters", "full packet identity and local comparisons", "direct-record canonical encoding and digest", "normal Python garbage collection"],
                "excluded": ["archive preparation", "full packet production", "transport decoding", "cross-arm result comparisons"],
                "initialization": "one untimed call to each arm for every request before measured blocks",
                "unit": "paired repeated request, clustered descriptively by problem; no independent-defect inference",
                "host_scope": "single recorded Python process and host; no deployment performance inference"}
    protocol["instrumentation"] = "released prototype counters retained: demand/projected maintain per-event counters; full/live use aggregate cell counts; timing describes these implementations, not an intrinsic algorithmic time bound"
    save(output / "protocol.json", protocol)
    work, packets = [], []
    for index, (task, old, role) in enumerate(task_rows):
        packet = signed.make_evidence(task)
        same(packet["sha256"], old["packet_sha256"], "retained full packet")
        results = {}
        for arm in ARMS:
            got = invoke(arm, task, packet)
            result = unpack(arm, got)
            same(retained.decision(result), retained.decision(old), (task["id"], arm, "preflight decision"))
            if arm in {"full", "demand", "direct_record"}:
                same(result, old[arm], (task["id"], arm, "retained deterministic result"))
            if arm == "direct_record": same(got[1], packet, "identical complete record")
            results[arm] = result
        cells = {arm: result["semantic_cells"] for arm, result in results.items()}
        if not cells["demand"] <= cells["projected_live"] <= cells["live"] <= cells["full"] == cells["direct_record"]:
            raise AssertionError((task["id"], "work nesting", cells))
        work.append({"id": task["id"], "subject": old["subject"], "problem": old["problem"],
                     "stage": old["stage"], "role": role, "sources": old["sources"],
                     "points": old["points"], "task_sha256": old["task_sha256"],
                     "packet_sha256": old["packet_sha256"], **retained.decision(old), "results": results,
                     "avoided_cells": {"static_pruning": cells["full"] - cells["live"],
                                       "support_projection": cells["live"] - cells["projected_live"],
                                       "conditional_and_diagnostic_demand": cells["projected_live"] - cells["demand"]}})
        packets.append(packet)
        if (index + 1) % 100 == 0:
            print(json.dumps({"phase": "preflight", "completed": index + 1, "total": len(task_rows)}), flush=True)
    save(output / "work.json", work)
    timings, blocks = [], []
    with (output / "timings.jsonl").open("x", encoding="utf-8") as stream:
        for repetition in range(10):
            rng = random.Random(args.seed + repetition)
            schedule = list(range(len(task_rows)))
            rng.shuffle(schedule)
            started = time.monotonic()
            for position, index in enumerate(schedule):
                task, old, _role = task_rows[index]
                order = design[(repetition + index) % len(design)]
                measured = {}
                for arm in order:
                    begin = time.perf_counter_ns()
                    got = invoke(arm, task, packets[index])
                    end = time.perf_counter_ns()
                    measured[arm] = end - begin
                    result = unpack(arm, got)
                    same(result, work[index]["results"][arm], (task["id"], repetition, arm, "timed deterministic result"))
                    if arm == "direct_record": same(got[1], packets[index], "timed identical complete record")
                    del got, result
                row = {"id": task["id"], "repetition": repetition, "schedule_position": position,
                       "order": list(order), "nanoseconds": measured}
                stream.write(json.dumps(row, separators=(",", ":")) + "\n")
                timings.append(row)
                if (position + 1) % 100 == 0:
                    stream.flush()
                    print(json.dumps({"phase": "timing", "block": repetition + 1,
                                      "completed": position + 1, "total": len(task_rows)}), flush=True)
            blocks.append({"block": repetition, "wall_seconds": time.monotonic() - started,
                           "load_average": list(os.getloadavg()) if hasattr(os, "getloadavg") else None})
    analysis = analyze(work, timings, output)
    same(source_bindings(), before, "executed sources unchanged")
    same(sha(args.corpus), corpus_sha, "corpus unchanged")
    same(sha(args.prior / "summary.json"), protocol["prior_summary_sha256"], "prior summary unchanged")
    for name, expected in protocol["prior_records"].items():
        same(sha(args.prior / name), expected, (name, "prior record unchanged"))
    summary = {"schema": "repairseal-signed-evaluator-study-v1", "outcome": "PASS",
               "source_bindings": before, "protocol_sha256": sha(output / "protocol.json"),
               "requests": len(work), "preflight_receiving_calls": len(work) * 5,
               "timed_receiving_calls": len(timings) * 5, "repetitions_per_request": 10,
               "canonical_disagreements": 0, "work": analysis, "blocks": blocks,
               "records": {name: sha(output / name) for name in
                           ("work.json", "timings.jsonl", "request-timing-summary.json", "analysis.json")}}
    save(output / "summary.json", summary)
    return summary


def main():
    require_assertions()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--prior", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20261119)
    parser.add_argument("--cpu", type=int)
    args = parser.parse_args()
    output = new_output_directory(args.output)
    if args.cpu is not None:
        os.sched_setaffinity(0, {args.cpu})
    try:
        result = run(args, output)
    except BaseException as exc:
        save(output / "summary.json", {"outcome": "FAILED", "error_type": type(exc).__name__, "error": str(exc)})
        raise
    print(json.dumps({"outcome": result["outcome"], "requests": result["requests"],
                      "timed_receiving_calls": result["timed_receiving_calls"]}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

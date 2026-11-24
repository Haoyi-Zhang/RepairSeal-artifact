"""Balanced matched study of support sharing versus per-point demand.

The original signed requests are reconstructed from the recorded corpus and
unchanged external source archive. Full, live-node, support-demand and
point-demand receivers all perform fresh source admission and reconstruction.
Twelve four-arm Williams orders balance both positions and immediate
predecessors three times per request. A canonical-result and deterministic
work check follows every measured call, outside the timed interval.

This is an implementation comparison. The point-demand ablation removes both
global-support analysis and support-keyed storage; its timing difference is
not a measurement of either phase in isolation.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
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
from int32_point_demand import evaluate_point_demand
from int32_evaluator_study import environment, quantiles
from scientific_driver import new_output_directory, require_assertions

ARMS = ("full", "live", "support_demand", "point_demand")
REPETITIONS = 12
SOURCE_NAMES = ("src/proof_dag_checker.py", "src/demand_evaluator.py", "src/int32_circuit.py",
    "src/codeflaws_int32_bridge.py", "tests/int32_baselines.py", "tests/int32_contract_study.py",
    "tests/int32_evaluator_study.py", "tests/int32_point_demand.py", "tests/int32_point_demand_study.py",
    "tests/scientific_driver.py")


def source_bindings():
    return {name: retained.file_hash(ROOT / name) for name in SOURCE_NAMES}


def orders():
    base = (0, 1, 3, 2)
    result = [tuple(ARMS[(value + offset) % 4] for value in base) for offset in range(4)]
    position = Counter((arm, i) for row in result for i, arm in enumerate(row))
    preceding = Counter(pair for row in result for pair in zip(row, row[1:]))
    retained.same(dict(position), {(arm, i): 1 for arm in ARMS for i in range(4)}, "position balance")
    retained.same(dict(preceding), {(a, b): 1 for a in ARMS for b in ARMS if a != b}, "predecessor balance")
    return result


def invoke(arm, task, packet):
    if arm == "full": return signed.verify_evidence(task, packet)
    if arm == "live": return baselines.evaluate_live(task)
    if arm == "support_demand": return signed.evaluate_direct(task)
    if arm == "point_demand": return evaluate_point_demand(task)
    raise ValueError(arm)


def load_requests(args):
    prior = json.loads((args.prior / "summary.json").read_text())
    retained.same(prior["outcome"], "PASS", "prior oracle study")
    for name, expected in prior["source_bindings"].items():
        retained.same(retained.file_hash(ROOT / name), expected, ("prior source", name))
    for name, expected in prior["records"].items():
        retained.same(retained.file_hash(args.prior / name), expected, ("prior record", name))
    corpus, raw, _admitted, corpus_digest = retained.load_inputs(args.corpus, args.archive)
    retained.same(corpus_digest, prior["corpus_sha256"], "shared corpus")
    _eligible, cases, _needed = retained.populations(corpus)
    previous = json.loads((args.prior / "requests.json").read_text())
    indexed = {row["id"]: row for row in previous}
    tasks = []
    for subject, candidate in cases:
        sources = {"original": subject["original_sha"], "candidate": candidate,
                   "reference": subject["reference_sha"]}
        role = ("own_reference" if candidate == sources["reference"] else
                "own_original" if candidate == sources["original"] else "cross_source")
        for stage in ("repair", "union"):
            points = sorted({tuple(test["input"]) for test in subject["tests"]
                             if stage == "union" or test["split"] == "repair"})
            task = {"kind": signed.PROFILE, "id": f"{subject['id']}-{candidate[:12]}-{stage}",
                    "policy": "reference-everywhere", "points": [list(p) for p in points],
                    "sources": {key: raw[value].decode("utf-8") for key, value in sources.items()}}
            old = indexed[task["id"]]
            retained.same(signed.task_identity(task), old["task_sha256"], "unaltered request")
            tasks.append((task, old, role))
    retained.same(len(tasks), len(previous), "complete prior population")
    return tasks, prior, corpus_digest


def analyze(work, timing_rows, output):
    index = {row["id"]: row for row in work}
    durations = {key: {arm: [] for arm in ARMS} for key in index}
    visits = {key: [] for key in index}
    for row in timing_rows:
        retained.same(sorted(row["nanoseconds"]), sorted(ARMS), "all measured arms")
        retained.same(sorted(row["order"]), sorted(ARMS), "order permutation")
        if any(type(v) is not int or v <= 0 for v in row["nanoseconds"].values()):
            raise ValueError("nonpositive measured duration")
        visits[row["id"]].append((row["repetition"], tuple(row["order"])))
        for arm in ARMS:
            durations[row["id"]][arm].append(row["nanoseconds"][arm])
    request_stats = []
    for key, row in index.items():
        retained.same(sorted(rep for rep, _order in visits[key]), list(range(REPETITIONS)), "one call per block")
        retained.same(dict(Counter(order for _rep, order in visits[key])),
                      {order: REPETITIONS // len(orders()) for order in orders()}, "balanced complete design")
        medians = {arm: statistics.median(durations[key][arm]) for arm in ARMS}
        request_stats.append({key_: row[key_] for key_ in ("id", "subject", "problem", "stage", "role", "points", "status")} |
                             {"median_ns": medians,
                              "ratios": {"point_over_live": medians["point_demand"] / medians["live"],
                                         "point_over_support": medians["point_demand"] / medians["support_demand"],
                                         "support_over_live": medians["support_demand"] / medians["live"],
                                         "point_over_full": medians["point_demand"] / medians["full"]}})
    result = {}
    for stage in ("repair", "union"):
        rows = [row for row in work if row["stage"] == stage]
        stats = [row for row in request_stats if row["stage"] == stage]
        result[stage] = {"requests": len(rows), "problems": len({r["problem"] for r in rows}),
            "cells": {arm: sum(r["results"][arm]["semantic_cells"] for r in rows) for arm in ARMS},
            "status": dict(Counter(r["status"] for r in rows)),
            "ratios": {name: quantiles([r["ratios"][name] for r in stats]) for name in stats[0]["ratios"]},
            "sum_request_median_ns": {arm: sum(r["median_ns"][arm] for r in stats) for arm in ARMS},
            "point_faster_than_live": sum(r["ratios"]["point_over_live"] < 1 for r in stats),
            "point_faster_than_support": sum(r["ratios"]["point_over_support"] < 1 for r in stats),
            "support_faster_than_live": sum(r["ratios"]["support_over_live"] < 1 for r in stats)}
        problem_stats = []
        for problem in sorted({r["problem"] for r in rows}):
            subset = [r for r in stats if r["problem"] == problem]
            totals = {arm: sum(r["median_ns"][arm] for r in subset) for arm in ARMS}
            problem_stats.append({"problem": problem, "requests": len(subset),
                "sum_request_median_ns": totals,
                "point_over_live": totals["point_demand"] / totals["live"],
                "point_over_support": totals["point_demand"] / totals["support_demand"]})
        result[stage]["problem_ratios"] = problem_stats
        result[stage]["problem_point_faster_than_live"] = sum(r["point_over_live"] < 1 for r in problem_stats)
        result[stage]["problem_point_faster_than_support"] = sum(r["point_over_support"] < 1 for r in problem_stats)
        result[stage]["problem_median_point_over_live"] = statistics.median(r["point_over_live"] for r in problem_stats)
        result[stage]["problem_median_point_over_support"] = statistics.median(r["point_over_support"] for r in problem_stats)
        cross = [r for r in stats if r["role"] == "cross_source"]
        result[stage]["cross_source"] = {"requests": len(cross), "problems": len({r["problem"] for r in cross}),
            "point_over_live": quantiles([r["ratios"]["point_over_live"] for r in cross]),
            "point_over_support": quantiles([r["ratios"]["point_over_support"] for r in cross]),
            "point_faster_than_live": sum(r["ratios"]["point_over_live"] < 1 for r in cross),
            "point_faster_than_support": sum(r["ratios"]["point_over_support"] < 1 for r in cross)}
    retained.save(output / "request-timing-summary.json", request_stats)
    retained.save(output / "analysis.json", result)
    return result


def run(args, output):
    before = source_bindings()
    tasks, prior, corpus_digest = load_requests(args)
    protocol = {"schema": "repairseal-point-demand-study", "source_bindings": before,
        "corpus_identity": corpus_digest, "prior_summary_identity": retained.file_hash(args.prior / "summary.json"),
        "prior_records": prior["records"], "requests": len(tasks), "arms": list(ARMS),
        "repetitions_per_request": REPETITIONS, "seed": args.seed, "orders": orders(), "environment": environment(),
        "measurement": "perf_counter_ns around complete receiving call; canonical and work checks outside interval",
        "included": ["fresh admission and lowering", "semantic evaluation", "released traversal counters", "full packet integrity checks", "normal garbage collection"],
        "excluded": ["packet creation", "transport decoding", "cross-arm comparisons"],
        "design": "Four-arm Williams design repeated three times per request; independent shuffled request order in each repetition",
        "counter_scope": "Support and point demand share counter categories and conditional traversal; live/full retain aggregate counters",
        "comparison_scope": "Removing support sharing also changes analysis, projection and memo addressing; whole-call ratios cannot assign separate elapsed contributions",
        "population": "Complete original-source request set used in the previous signed study; no selection by speed or new candidate generation"}
    retained.save(output / "protocol.json", protocol)
    work, packets = [], []
    for position, (task, old, role) in enumerate(tasks):
        packet = signed.make_evidence(task)
        retained.same(packet["sha256"], old["packet_sha256"], "same full packet")
        results = {}
        for arm in ARMS:
            got = invoke(arm, task, packet)
            retained.same(retained.decision(got), retained.decision(old), (task["id"], arm, "canonical preflight"))
            if arm in {"full", "support_demand"}:
                retained.same(got, old["demand" if arm == "support_demand" else "full"], "unchanged deterministic arm")
            results[arm] = got
        cells = {arm: result["semantic_cells"] for arm, result in results.items()}
        if not cells["support_demand"] <= cells["point_demand"] <= cells["live"] <= cells["full"]:
            raise AssertionError((task["id"], "observed nesting", cells))
        work.append({"id": task["id"], "subject": old["subject"], "problem": old["problem"],
            "stage": old["stage"], "role": role, "points": old["points"], **retained.decision(old), "results": results,
            "avoided_cells": {"static_pruning": cells["full"] - cells["live"],
                "conditional_and_diagnostic_demand_without_sharing": cells["live"] - cells["point_demand"],
                "support_sharing_after_demand": cells["point_demand"] - cells["support_demand"]}})
        packets.append(packet)
        if (position + 1) % 100 == 0:
            print(json.dumps({"phase": "preflight", "completed": position + 1, "total": len(tasks)}), flush=True)
    retained.save(output / "work.json", work)
    times, blocks = [], []
    design = orders()
    with (output / "timings.jsonl").open("x", encoding="utf-8") as stream:
        for repetition in range(REPETITIONS):
            schedule = list(range(len(tasks)))
            random.Random(args.seed + repetition).shuffle(schedule)
            start = time.monotonic()
            for position, index in enumerate(schedule):
                task, _old, _role = tasks[index]
                order = design[(repetition + index) % len(design)]
                measured = {}
                for arm in order:
                    begin = time.perf_counter_ns()
                    got = invoke(arm, task, packets[index])
                    end = time.perf_counter_ns()
                    measured[arm] = end - begin
                    retained.same(got, work[index]["results"][arm], (task["id"], arm, repetition, "timed deterministic result"))
                    del got
                row = {"id": task["id"], "repetition": repetition, "schedule_position": position,
                       "order": list(order), "nanoseconds": measured}
                stream.write(json.dumps(row, separators=(",", ":")) + "\n")
                times.append(row)
                if (position + 1) % 100 == 0:
                    stream.flush()
                    print(json.dumps({"phase": "timing", "block": repetition + 1, "completed": position + 1, "total": len(tasks)}), flush=True)
            blocks.append({"repetition": repetition, "wall_seconds": time.monotonic() - start,
                           "load_average": list(os.getloadavg()) if hasattr(os, "getloadavg") else None})
    analysis = analyze(work, times, output)
    retained.same(source_bindings(), before, "executed source unchanged")
    retained.same(retained.file_hash(args.corpus), corpus_digest, "input corpus unchanged")
    retained.same(retained.file_hash(args.prior / "summary.json"), protocol["prior_summary_identity"], "prior summary unchanged")
    for name, expected in protocol["prior_records"].items():
        retained.same(retained.file_hash(args.prior / name), expected, (name, "prior record unchanged"))
    summary = {"outcome": "PASS", "source_bindings": before, "requests": len(work),
        "preflight_receiving_calls": len(work) * len(ARMS), "timed_receiving_calls": len(times) * len(ARMS),
        "repetitions_per_request": REPETITIONS, "canonical_disagreements": 0, "analysis": analysis, "blocks": blocks,
        "records": {name: retained.file_hash(output / name) for name in
                    ("protocol.json", "work.json", "timings.jsonl", "request-timing-summary.json", "analysis.json")}}
    retained.save(output / "summary.json", summary)
    return summary


def main():
    require_assertions()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--prior", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20261120)
    parser.add_argument("--cpu", type=int)
    args = parser.parse_args()
    if args.cpu is not None:
        os.sched_setaffinity(0, {args.cpu})
    output = new_output_directory(args.output)
    try:
        result = run(args, output)
    except BaseException as exc:
        retained.save(output / "summary.json", {"outcome": "FAILED", "error_type": type(exc).__name__, "error": str(exc)})
        raise
    print(json.dumps({key: result[key] for key in ("outcome", "requests", "timed_receiving_calls")}), flush=True)


if __name__ == "__main__":
    main()

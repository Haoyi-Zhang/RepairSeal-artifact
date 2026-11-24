"""Independently recompute the paired study's published aggregates from raw calls.

This verifier does not import the study writer or reuse its analysis routines.
It checks balanced measured schedules, complete repetitions, arm-specific work
bounds, canonical agreement, and request/problem aggregation. It can validate
an already unpacked result directory without the external C source archive.
"""
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import json
import math
import statistics

ARMS = {"full", "live", "support_demand", "point_demand"}


def check(condition, message):
    if not condition:
        raise ValueError(message)


def verify(directory, reference):
    protocol = json.loads((directory / "protocol.json").read_text())
    summary = json.loads((directory / "summary.json").read_text())
    work = json.loads((directory / "work.json").read_text())
    reported = json.loads((directory / "analysis.json").read_text())
    stats = json.loads((directory / "request-timing-summary.json").read_text())
    check(summary["outcome"] == "PASS", "completed study required")
    repetitions = protocol["repetitions_per_request"]
    check(repetitions == 12 and set(protocol["arms"]) == ARMS, "declared study design")
    check(len(work) == len({r["id"] for r in work}) == 1478, "complete unique request population")
    expected = {r["id"]: r for r in work}
    oracle_rows = json.loads(reference.read_text())
    oracle = {r["id"]: r for r in oracle_rows}
    check(len(oracle) == len(oracle_rows) and set(oracle) == set(expected), "complete retained canonical reference")
    for key, row in expected.items():
        check(all(row[k] == oracle[key][k] for k in ("status", "witness", "subject", "problem", "stage", "points")), "retained canonical reference and request labels")
        sources = oracle[key]["sources"]
        role = ("own_reference" if sources["candidate"] == sources["reference"] else
                "own_original" if sources["candidate"] == sources["original"] else "cross_source")
        check(row["role"] == role, "candidate class from retained source identities")
    times = defaultdict(lambda: defaultdict(list))
    visit = defaultdict(list)
    raw_rows = 0
    for line in (directory / "timings.jsonl").read_text().splitlines():
        row = json.loads(line)
        key = row["id"]
        check(key in expected, "unknown timed request")
        check(set(row["order"]) == ARMS and len(row["order"]) == len(ARMS), "complete measured order")
        check(set(row["nanoseconds"]) == ARMS, "complete measured duration map")
        visit[key].append((row["repetition"], row["order"]))
        for arm, value in row["nanoseconds"].items():
            check(type(value) is int and value > 0, "positive actual duration")
            times[key][arm].append(value)
        raw_rows += 1
    check(raw_rows == len(work) * repetitions, "complete timed call groups")
    medians = {}
    for key, visits in visit.items():
        check(sorted(rep for rep, _order in visits) == list(range(repetitions)), "each repetition exactly once")
        position = Counter((arm, index) for _rep, order in visits for index, arm in enumerate(order))
        adjacent = Counter(pair for _rep, order in visits for pair in zip(order, order[1:]))
        check(dict(position) == {(arm, index): 3 for arm in ARMS for index in range(4)}, "per-request position balance")
        check(dict(adjacent) == {(a, b): 3 for a in ARMS for b in ARMS if a != b}, "per-request predecessor balance")
        medians[key] = {arm: statistics.median(values) for arm, values in times[key].items()}
    check(set(visit) == set(expected), "all requests measured")
    check(len(stats) == len(expected) == len({r["id"] for r in stats}), "complete unique per-request summary")
    for row in stats:
        key = row["id"]
        check(row["median_ns"] == medians[key], "per-request median from raw calls")
        m = medians[key]
        ratios = {"point_over_live": m["point_demand"] / m["live"],
                  "point_over_support": m["point_demand"] / m["support_demand"],
                  "support_over_live": m["support_demand"] / m["live"],
                  "point_over_full": m["point_demand"] / m["full"]}
        check(row["ratios"] == ratios, "paired ratios from same request medians")
        original = expected[key]
        check(all(row[k] == original[k] for k in ("subject", "problem", "stage", "role", "points", "status")), "summary labels")
    for row in work:
        results = row["results"]
        target = {k: row[k] for k in ("status", "witness")}
        check(set(results) == ARMS, "all preflight arms")
        check(all({k: result[k] for k in target} == target for result in results.values()), "canonical agreement")
        c = {arm: r["semantic_cells"] for arm, r in results.items()}
        check(c["support_demand"] <= c["point_demand"] <= c["live"] <= c["full"], "observed work nesting")
        check(c["full"] == results["full"]["nodes"] * len(row["points"]), "full N*M bound")
        check(c["live"] == results["live"]["live_nodes"] * len(row["points"]), "live L*M bound")
        counters = results["point_demand"]["counters"]
        check(counters["semantic_cells"] == counters["cache_writes"] == c["point_demand"], "point one-store accounting")
        check(counters["cache_queries"] == counters["cache_hits"] + c["point_demand"], "point cache-query accounting")
        check(counters["key_coordinates"] == counters["support_nodes"] == 0, "point memo removes support work")
    regenerated = {}
    for stage in ("repair", "union"):
        rows = [row for row in work if row["stage"] == stage]
        subset = [row for row in stats if row["stage"] == stage]
        check(len(rows) == 739, "complete stage")
        check(len({row["problem"] for row in rows}) == 35, "complete problem clusters")
        cells = {arm: sum(row["results"][arm]["semantic_cells"] for row in rows) for arm in ARMS}
        check(cells == reported[stage]["cells"], "aggregate cells")
        quantiles = {}
        for name in subset[0]["ratios"]:
            values = sorted(row["ratios"][name] for row in subset)
            quantiles[name] = {label: values[math.ceil(fraction * len(values)) - 1]
                              for label, fraction in (("p10", .1), ("p25", .25), ("p50", .5), ("p75", .75), ("p90", .9))}
        check(quantiles == reported[stage]["ratios"], "empirical paired-ratio quantiles")
        check(reported[stage]["requests"] == len(rows) and reported[stage]["problems"] == 35,
              "aggregate population labels")
        check(reported[stage]["status"] == dict(Counter(row["status"] for row in rows)),
              "aggregate decision counts")
        for name, numerator, denominator in (("point_faster_than_live", "point_demand", "live"),
                                            ("point_faster_than_support", "point_demand", "support_demand"),
                                            ("support_faster_than_live", "support_demand", "live")):
            check(reported[stage][name] == sum(row["median_ns"][numerator] < row["median_ns"][denominator]
                                             for row in subset), "request-level faster counts")
        check(reported[stage]["sum_request_median_ns"] ==
              {arm: sum(row["median_ns"][arm] for row in subset) for arm in ARMS},
              "sum of request median durations")
        problems = {}
        for row in subset:
            bucket = problems.setdefault(row["problem"], {arm: 0 for arm in ARMS})
            for arm, value in row["median_ns"].items():
                bucket[arm] += value
        check({r["problem"] for r in reported[stage]["problem_ratios"]} == set(problems), "reported problem identities")
        for row in reported[stage]["problem_ratios"]:
            total = problems[row["problem"]]
            check(row["sum_request_median_ns"] == total, "cluster summed request medians")
            check(row["point_over_live"] == total["point_demand"] / total["live"], "problem paired live ratio")
            check(row["point_over_support"] == total["point_demand"] / total["support_demand"], "problem paired support ratio")
        check(len(reported[stage]["problem_ratios"]) == 35, "complete reported problem ratios")
        for denominator, arm in (("live", "live"), ("support", "support_demand")):
            values = [total["point_demand"] / total[arm] for total in problems.values()]
            check(reported[stage]["problem_point_faster_than_" + denominator] == sum(value < 1 for value in values),
                  "problem-level faster counts")
            check(reported[stage]["problem_median_point_over_" + denominator] == statistics.median(values),
                  "median of problem-level paired ratios")
        cross = [row for row in subset if row["role"] == "cross_source"]
        cross_report = reported[stage]["cross_source"]
        check(cross_report["requests"] == len(cross) == 549 and
              cross_report["problems"] == len({row["problem"] for row in cross}) == 23,
              "cross-source population")
        for name, denominator in (("point_over_live", "live"), ("point_over_support", "support_demand")):
            values = sorted(row["median_ns"]["point_demand"] / row["median_ns"][denominator] for row in cross)
            quantile = {label: values[math.ceil(fraction * len(values)) - 1]
                        for label, fraction in (("p10", .1), ("p25", .25), ("p50", .5), ("p75", .75), ("p90", .9))}
            check(cross_report[name] == quantile, "cross-source paired-ratio quantiles")
            check(cross_report[name.replace("over", "faster_than")] == sum(value < 1 for value in values),
                  "cross-source faster counts")
        regenerated[stage] = {"requests": len(rows), "problems": len(problems), "cells": cells, "paired_ratio_quantiles": quantiles}
    check(summary["timed_receiving_calls"] == raw_rows * 4 == 70944, "actual timed call count")
    check(summary["preflight_receiving_calls"] == len(work) * 4 == 5912, "actual preflight call count")
    return {"outcome": "PASS_INDEPENDENT_POINT_DEMAND_RECOMPUTATION", "requests": len(work),
            "measured_call_groups": raw_rows, "timed_receiving_calls": raw_rows * 4,
            "schedule_checks": "all arms occupy every position and each directed neighboring pair occurs three times per request",
            "regenerated": regenerated}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    args = parser.parse_args()
    result = verify(args.directory, args.reference)
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(result["outcome"])


if __name__ == "__main__":
    main()

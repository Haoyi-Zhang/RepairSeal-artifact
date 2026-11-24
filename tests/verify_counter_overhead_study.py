"""Recompute the instrumentation experiment from individual recorded calls.

This checker imports neither the study writer nor either receiving evaluator.
It checks the complete request population, original canonical and measured-work
references, declared and actually used balanced schedules, each request median,
and the paired request/problem comparisons. It needs no external source archive.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parents[1]
ARMS = ("support", "point", "support_uninstrumented", "point_uninstrumented", "live")
RATIOS = {
    "support_over_live": ("support", "live"),
    "point_over_live": ("point", "live"),
    "support_uninstrumented_over_live": ("support_uninstrumented", "live"),
    "point_uninstrumented_over_live": ("point_uninstrumented", "live"),
    "point_uninstrumented_over_support_uninstrumented": ("point_uninstrumented", "support_uninstrumented"),
    "support_over_uninstrumented": ("support", "support_uninstrumented"),
    "point_over_uninstrumented": ("point", "point_uninstrumented"),
    "point_over_support": ("point", "support"),
}
INSTRUMENTED = {"support": "support_demand", "point": "point_demand", "live": "live"}
LABELS = ("id", "subject", "problem", "stage", "role", "points", "status")


def require(value, message):
    if not value:
        raise ValueError(message)


def same(actual, expected, message):
    """JSON equality with exact scalar types, including Boolean/integer types."""
    require(type(actual) is type(expected), message + ": scalar/container type")
    if isinstance(expected, dict):
        require(set(actual) == set(expected), message + ": object keys")
        for key in expected:
            same(actual[key], expected[key], message + "/" + str(key))
    elif isinstance(expected, list):
        require(len(actual) == len(expected), message + ": sequence length")
        for index, (a, b) in enumerate(zip(actual, expected)):
            same(a, b, message + "/" + str(index))
    else:
        require(actual == expected, message + ": value")


def decode(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON field: " + key)
            result[key] = value
        return result

    def number(text):
        value = float(text)
        require(math.isfinite(value), "nonfinite JSON number")
        return value

    def bad(text):
        raise ValueError("nonfinite JSON constant: " + text)

    return json.loads(text, object_pairs_hook=unique, parse_float=number, parse_constant=bad)


def load(path):
    return decode(path.read_text())


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def bindings(root, entries):
    require(isinstance(entries, dict) and entries, "nonempty binding inventory")
    for name, identity in entries.items():
        path = (root / name).resolve()
        require(path.is_relative_to(root.resolve()), "binding escapes its root")
        require(digest(path) == identity, "changed bound file: " + name)


def quantiles(values):
    values = sorted(values)
    require(bool(values), "nonempty ratio population")
    return {name: values[math.ceil(fraction * len(values)) - 1]
            for name, fraction in (("p10", .1), ("p25", .25), ("p50", .5), ("p75", .75), ("p90", .9))}


def ratios(medians):
    return {name: medians[a] / medians[b] for name, (a, b) in RATIOS.items()}


def comparisons(values):
    return {"lower": sum(value < 1 for value in values),
            "equal": sum(value == 1 for value in values),
            "higher": sum(value > 1 for value in values)}


def aggregate(rows):
    """Aggregate actual request medians; never pool calls from unlike tasks."""
    problems = []
    for problem in sorted({row["problem"] for row in rows}):
        selected = [row for row in rows if row["problem"] == problem]
        totals = {arm: sum(row["median_ns"][arm] for row in selected) for arm in ARMS}
        problems.append({"problem": problem, "requests": len(selected),
                         "sum_request_median_ns": totals, "ratios": ratios(totals)})
    return {
        "requests": len(rows), "problems": len(problems),
        "status": dict(Counter(row["status"] for row in rows)),
        "roles": dict(Counter(row["role"] for row in rows)),
        "ratios": {name: quantiles([row["ratios"][name] for row in rows]) for name in RATIOS},
        "request_comparisons": {name: comparisons([row["ratios"][name] for row in rows]) for name in RATIOS},
        "sum_request_median_ns": {arm: sum(row["median_ns"][arm] for row in rows) for arm in ARMS},
        "problem_ratios": problems,
        "problem_median_ratios": {name: statistics.median(row["ratios"][name] for row in problems) for name in RATIOS},
        "problem_comparisons": {name: comparisons([row["ratios"][name] for row in problems]) for name in RATIOS},
    }


def verify(directory, reference, point_reference):
    directory, reference, point_reference = directory.resolve(), reference.resolve(), point_reference.resolve()
    protocol = load(directory / "protocol.json")
    summary = load(directory / "summary.json")
    work = load(directory / "work.json")
    reported = load(directory / "analysis.json")
    reported_stats = load(directory / "request-timing-summary.json")
    require(summary["outcome"] == "PASS_COUNTER_OVERHEAD_STUDY", "complete measured study required")
    require(summary["source_inputs_unchanged"] is True, "source and input continuity")
    require(summary["canonical_disagreements"] == summary["value_trace_disagreements"] == 0,
            "canonical and untimed value-trace agreement")
    same(protocol["arms"], list(ARMS), "declared methods")
    same(protocol["ratio_specs"], {key: list(value) for key, value in RATIOS.items()}, "paired ratio definitions")
    require(protocol["requests"] == 1478 and protocol["repetitions_per_request"] == 10,
            "complete population and ten repetitions")
    bindings(directory, summary["records"])
    bindings(ROOT, protocol["source_bindings"])
    bindings(directory, protocol["source_snapshots"])
    bindings(directory, protocol["derivation_files"])
    same(protocol["source_snapshots"],
         {"executed-sources/" + name: identity for name, identity in protocol["source_bindings"].items()},
         "every executed source has a literal snapshot")
    if "source_bindings" in summary:
        same(summary["source_bindings"], protocol["source_bindings"], "same source inventory at completion")
    require(digest(reference) == protocol["prior_records"]["requests.json"], "canonical-reference binding")
    require(digest(reference.parent / "summary.json") == protocol["prior_summary_identity"], "canonical-summary binding")
    bindings(reference.parent, protocol["prior_records"])
    require(digest(point_reference) == protocol["point_prior_records"]["work.json"], "point-work binding")
    require(digest(point_reference.parent / "summary.json") == protocol["point_prior_summary_identity"],
            "point-study summary binding")
    bindings(point_reference.parent, protocol["point_prior_records"])
    same(protocol["reference_identities"], {"signed_requests": digest(reference), "point_work": digest(point_reference)},
         "independent reference identities")
    derivation = load(directory / "derived/manifest.json")
    require(derivation["derived_source_identity"] == digest(directory / "derived/receivers.py"),
            "retained derived kernel identity")
    require(derivation["canonical_return_fields"] == ["status", "witness"], "derived semantic output")
    for name, identity in derivation["source_bindings"].items():
        require(protocol["source_bindings"][name] == identity, "derivation uses executed original sources")
    require(len(work) == 1478 and len({row["id"] for row in work}) == 1478, "each request once in preflight")
    oracle_rows, old_point_rows = load(reference), load(point_reference)
    oracle = {row["id"]: row for row in oracle_rows}
    old_point = {row["id"]: row for row in old_point_rows}
    expected = {row["id"]: row for row in work}
    require(len(oracle_rows) == len(oracle) == len(old_point_rows) == len(old_point) == 1478 and
            set(oracle) == set(old_point) == set(expected), "complete independent reference populations")
    for key, row in expected.items():
        original, measured = oracle[key], old_point[key]
        for field in ("subject", "problem", "stage", "points", "sources", "task_sha256", "status", "witness"):
            same(row[field], original[field], "canonical reference " + key + "/" + field)
        sources = original["sources"]
        role = ("own_reference" if sources["candidate"] == sources["reference"] else
                "own_original" if sources["candidate"] == sources["original"] else "cross_source")
        same(row["role"], role, "candidate origin")
        same(set(row["results"]), set(ARMS), "complete preflight arms")
        decision = {field: row[field] for field in ("status", "witness")}
        for arm, result in row["results"].items():
            same({field: result[field] for field in decision}, decision, "complete canonical preflight")
            if arm in INSTRUMENTED:
                same(result, measured["results"][INSTRUMENTED[arm]], "unchanged instrumented result")
            else:
                same(result, decision, "uninstrumented result contains only the requested decision")
        cells = {arm: row["results"][arm]["semantic_cells"] for arm in INSTRUMENTED}
        same(row["semantic_work"], cells, "actual instrumented preflight semantic values")
        require(cells["support"] <= cells["point"] <= cells["live"], "semantic-work nesting")
        same(set(row["value_traces"]), {"support", "point", "support_uninstrumented", "point_uninstrumented"},
             "all untimed value traces")
        same(row["exact_trace_match"], {"support": True, "point": True}, "typed sequence comparison completed")
        for arm in ("support", "point"):
            trace, off_trace = row["value_traces"][arm], row["value_traces"][arm + "_uninstrumented"]
            same(trace, off_trace, "equal recorded store sequence identity")
            require(trace["stored_values"] == cells[arm], "one trace event per computed semantic value")
            require(isinstance(trace["identity"], str) and len(trace["identity"]) == 64 and
                    all(c in "0123456789abcdef" for c in trace["identity"]), "typed store-trace binding")
    design = protocol["orders"]
    require(len(design) == 10 and len({tuple(order) for order in design}) == 10, "ten distinct declared orders")
    position = Counter((arm, index) for order in design for index, arm in enumerate(order))
    adjacent = Counter(pair for order in design for pair in zip(order, order[1:]))
    require(all(len(order) == 5 and set(order) == set(ARMS) for order in design), "declared order permutations")
    same(dict(position), {(arm, index): 2 for arm in ARMS for index in range(5)}, "declared position balance")
    same(dict(adjacent), {(a, b): 2 for a in ARMS for b in ARMS if a != b}, "declared predecessor balance")
    times = defaultdict(lambda: defaultdict(list))
    visits = defaultdict(list)
    schedules = defaultdict(list)
    request_position = {row["id"]: index for index, row in enumerate(work)}
    raw_count = 0
    with (directory / "timings.jsonl").open() as stream:
        for line in stream:
            row = decode(line)
            key, rep, order = row["id"], row["repetition"], row["order"]
            require(key in expected and type(rep) is int and 0 <= rep < 10, "declared timed request and repetition")
            require(row["all_results_exactly_matched_preflight"] is True, "every timed result checked against preflight")
            same(order, design[(rep + request_position[key]) % 10], "actual registered receiving order")
            require(set(row["nanoseconds"]) == set(ARMS), "every duration present")
            require(type(row["schedule_position"]) is int and 0 <= row["schedule_position"] < 1478,
                    "request schedule position")
            schedules[rep].append((row["schedule_position"], key))
            visits[key].append((rep, tuple(order)))
            for arm, value in row["nanoseconds"].items():
                require(type(value) is int and value > 0, "positive integer measured nanoseconds")
                times[key][arm].append(value)
            raw_count += 1
    require(raw_count == 14780 and set(visits) == set(expected), "all recorded timed call groups")
    for rep in range(10):
        require(len(schedules[rep]) == 1478 and {key for _index, key in schedules[rep]} == set(expected),
                "complete request inventory in every repetition")
        same([index for index, _key in schedules[rep]], list(range(1478)), "actual sequential schedule positions")
    medians = {}
    for key, group in visits.items():
        same(sorted(rep for rep, _order in group), list(range(10)), "each request measured once per repetition")
        same(dict(Counter(order for _rep, order in group)), {tuple(order): 1 for order in design},
             "each request receives the complete balanced design")
        medians[key] = {arm: statistics.median(times[key][arm]) for arm in ARMS}
    stats = [{field: row[field] for field in LABELS} |
             {"median_ns": medians[row["id"]], "ratios": ratios(medians[row["id"]])} for row in work]
    same(reported_stats, stats, "every per-request summary from actual raw calls")
    regenerated = {}
    for stage in ("repair", "union"):
        selected = [row for row in stats if row["stage"] == stage]
        require(len(selected) == 739 and len({row["problem"] for row in selected}) == 35, "complete stage")
        result = aggregate(selected)
        same(result["roles"], {"own_reference": 95, "own_original": 95, "cross_source": 549}, "complete candidate classes")
        result["semantic_cells"] = {arm: sum(row["semantic_work"][arm] for row in work if row["stage"] == stage)
                                     for arm in INSTRUMENTED}
        cross = [row for row in selected if row["role"] == "cross_source"]
        require(len(cross) == 549 and len({row["problem"] for row in cross}) == 23, "cross-source clusters")
        result["cross_source"] = aggregate(cross)
        regenerated[stage] = result
    same(reported, regenerated, "complete request/problem/cross-source analysis")
    same(summary["analysis"], regenerated, "completion summary analysis")
    require(summary["preflight_receiving_calls"] == 7390 and summary["timed_receiving_calls"] == 73900,
            "actual receiving-call counts")
    require(summary["repetitions_per_request"] == 10, "summary repetition count")
    return {"outcome": "PASS_INDEPENDENT_COUNTER_OVERHEAD_RECOMPUTATION", "requests": 1478,
            "preflight_receiving_calls": 7390, "timed_receiving_calls": 73900,
            "measured_call_groups": raw_count, "canonical_reference": digest(reference),
            "point_work_reference": digest(point_reference),
            "schedule_checks": "Each arm occurs twice in each position and each directed adjacent pair occurs twice for every request.",
            "trace_scope": "Untimed corresponding receivers recorded the same typed store-sequence identity and reported an exact element-by-element comparison; these are not new native-C observations.",
            "regenerated": regenerated}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--point-reference", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output must be a new file; retained observations are never replaced")
    result = verify(args.directory, args.reference, args.point_reference)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        stream.write(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(result["outcome"])


if __name__ == "__main__":
    main()

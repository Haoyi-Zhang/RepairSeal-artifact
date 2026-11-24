"""Measure the effect of demand-receiver instrumentation in a balanced study.

All five arms receive the complete original signed request population. The
instrumented and counter-elided demand implementations are co-measured with
the live-node baseline. Each call includes fresh source admission,
reconstruction and canonical receiving. Traces used to establish identical
local value/store sequences are collected only in untimed preflight calls.
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
import int32_point_demand as point
import counter_free_receivers as elided
from int32_point_demand_study import load_requests
from int32_evaluator_study import environment, quantiles
from scientific_driver import new_output_directory, require_assertions

ARMS = ("support", "point", "support_uninstrumented", "point_uninstrumented", "live")
REPETITIONS = 10
RATIO_SPECS = {
    "support_over_live": ("support", "live"),
    "point_over_live": ("point", "live"),
    "support_uninstrumented_over_live": ("support_uninstrumented", "live"),
    "point_uninstrumented_over_live": ("point_uninstrumented", "live"),
    "point_uninstrumented_over_support_uninstrumented": ("point_uninstrumented", "support_uninstrumented"),
    "support_over_uninstrumented": ("support", "support_uninstrumented"),
    "point_over_uninstrumented": ("point", "point_uninstrumented"),
    "point_over_support": ("point", "support"),
}
SOURCE_NAMES = (
    "src/proof_dag_checker.py", "src/demand_evaluator.py",
    "src/int32_circuit.py", "src/codeflaws_int32_bridge.py",
    "tests/int32_baselines.py", "tests/int32_contract_study.py",
    "tests/int32_evaluator_study.py", "tests/int32_point_demand.py",
    "tests/int32_point_demand_study.py", "tests/scientific_driver.py",
    "tests/counter_free_receivers.py", "tests/counter_overhead_study.py",
)


def check(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    def unique(items):
        result = {}
        for key, value in items:
            check(key not in result, "duplicate JSON field")
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))


def bindings():
    return {name: retained.file_hash(ROOT / name) for name in SOURCE_NAMES}


def orders():
    base = (0, 1, 4, 2, 3)
    forward = [tuple(ARMS[(value + offset) % 5] for value in base) for offset in range(5)]
    design = forward + [tuple(reversed(order)) for order in forward]
    positions = Counter((arm, position) for order in design for position, arm in enumerate(order))
    neighbors = Counter(pair for order in design for pair in zip(order, order[1:]))
    check(dict(positions) == {(arm, position): 2 for arm in ARMS for position in range(5)},
          "balanced method positions")
    check(dict(neighbors) == {(a, b): 2 for a in ARMS for b in ARMS if a != b},
          "balanced directed neighbors")
    return design


def receivers():
    kernel = elided.initialize()
    return {
        "support": signed.evaluate_direct, "point": point.evaluate_point_demand,
        "support_uninstrumented": kernel.evaluate_support,
        "point_uninstrumented": kernel.evaluate_point,
        "live": baselines.evaluate_live,
    }


def ratios(values):
    return {name: values[a] / values[b] for name, (a, b) in RATIO_SPECS.items()}


def comparisons(rows):
    return {name: {"lower": sum(row["ratios"][name] < 1 for row in rows),
                   "equal": sum(row["ratios"][name] == 1 for row in rows),
                   "higher": sum(row["ratios"][name] > 1 for row in rows)}
            for name in RATIO_SPECS}


def summarize(stats):
    problem_rows = []
    for problem in sorted({row["problem"] for row in stats}):
        selected = [row for row in stats if row["problem"] == problem]
        totals = {arm: sum(row["median_ns"][arm] for row in selected) for arm in ARMS}
        problem_rows.append({"problem": problem, "requests": len(selected),
                             "sum_request_median_ns": totals, "ratios": ratios(totals)})
    return {
        "requests": len(stats), "problems": len(problem_rows),
        "status": dict(Counter(row["status"] for row in stats)),
        "roles": dict(Counter(row["role"] for row in stats)),
        "ratios": {name: quantiles([row["ratios"][name] for row in stats]) for name in RATIO_SPECS},
        "request_comparisons": comparisons(stats),
        "sum_request_median_ns": {arm: sum(row["median_ns"][arm] for row in stats) for arm in ARMS},
        "problem_ratios": problem_rows,
        "problem_median_ratios": {name: statistics.median(row["ratios"][name] for row in problem_rows)
                                 for name in RATIO_SPECS},
        "problem_comparisons": comparisons(problem_rows),
    }


def analyze(work, timing, output):
    indexed = {row["id"]: row for row in work}
    check(len(indexed) == len(work), "unique observed request identities")
    durations = {key: {arm: [] for arm in ARMS} for key in indexed}
    visits = {key: [] for key in indexed}
    for row in timing:
        check(row["id"] in indexed and set(row["nanoseconds"]) == set(ARMS), "complete measured arms")
        check(sorted(row["order"]) == sorted(ARMS), "measured order permutation")
        check(row["all_results_exactly_matched_preflight"] is True, "timed result checks")
        visits[row["id"]].append((row["repetition"], tuple(row["order"])))
        for arm, value in row["nanoseconds"].items():
            check(type(value) is int and value > 0, "positive measured nanoseconds")
            durations[row["id"]][arm].append(value)
    request_stats = []
    for key, row in indexed.items():
        check(sorted(rep for rep, _order in visits[key]) == list(range(REPETITIONS)),
              "exactly one request measurement in each repetition")
        check(sorted(order for _rep, order in visits[key]) == sorted(orders()),
              "complete balanced orders")
        medians = {arm: statistics.median(durations[key][arm]) for arm in ARMS}
        request_stats.append({name: row[name] for name in
                              ("id", "subject", "problem", "stage", "role", "points", "status")} |
                             {"median_ns": medians, "ratios": ratios(medians)})
    analysis = {}
    for stage in ("repair", "union"):
        selected = [row for row in request_stats if row["stage"] == stage]
        raw = [row for row in work if row["stage"] == stage]
        check(len(selected) == 739 and len({row["problem"] for row in selected}) == 35,
              "complete stage and problem population")
        stage_result = summarize(selected)
        stage_result["semantic_cells"] = {
            arm: sum(row["semantic_work"][arm] for row in raw) for arm in ("support", "point", "live")}
        cross = [row for row in selected if row["role"] == "cross_source"]
        check(len(cross) == 549 and len({row["problem"] for row in cross}) == 23,
              "complete cross-source population")
        stage_result["cross_source"] = summarize(cross)
        analysis[stage] = stage_result
    retained.save(output / "request-timing-summary.json", request_stats)
    retained.save(output / "analysis.json", analysis)
    return analysis


def point_reference(args):
    summary = read(args.point_prior / "summary.json")
    check(summary["outcome"] == "PASS" and summary["requests"] == 1478,
          "complete retained point-demand campaign")
    for name, value in summary["source_bindings"].items():
        check(retained.file_hash(ROOT / name) == value, "changed point reference source: " + name)
    for name, value in summary["records"].items():
        check(retained.file_hash(args.point_prior / name) == value, "changed point reference record: " + name)
    rows = read(args.point_prior / "work.json")
    result = {row["id"]: row for row in rows}
    check(len(result) == len(rows) == 1478, "complete unique point reference")
    return result, summary


def run(args, output):
    before = bindings()
    task_rows, prior, corpus_identity = load_requests(args)
    old_point, point_summary = point_reference(args)
    check(len(task_rows) == len(old_point) == 1478, "complete unselected natural population")
    check({task["id"] for task, _old, _role in task_rows} == set(old_point), "paired point reference population")
    selected_receivers = receivers()
    code, derivation = elided.derivation()
    derived = output / "derived"
    derived.mkdir()
    (derived / "receivers.py").write_text(code, encoding="utf-8")
    retained.save(derived / "manifest.json", derivation)
    snapshots = {}
    for name, expected in before.items():
        path = output / "executed-sources" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        content = (ROOT / name).read_bytes()
        check(elided.identity(content) == expected, "source changed while snapshotting")
        path.write_bytes(content)
        snapshots[path.relative_to(output).as_posix()] = expected
    derived_files = {name: retained.file_hash(output / name) for name in
                     ("derived/receivers.py", "derived/manifest.json")}
    protocol = {
        "study": "Paired removal of measurement bookkeeping from demand receiving",
        "source_bindings": before, "source_snapshots": snapshots, "derivation_files": derived_files,
        "corpus_identity": corpus_identity, "archive_identity": retained.file_hash(args.archive),
        "prior_summary_identity": retained.file_hash(args.prior / "summary.json"),
        "prior_records": prior["records"],
        "point_prior_summary_identity": retained.file_hash(args.point_prior / "summary.json"),
        "point_prior_records": point_summary["records"],
        "reference_identities": {"signed_requests": retained.file_hash(args.prior / "requests.json"),
                                 "point_work": retained.file_hash(args.point_prior / "work.json")},
        "requests": 1478, "arms": list(ARMS), "repetitions_per_request": REPETITIONS,
        "seed": args.seed, "orders": orders(), "ratio_specs": RATIO_SPECS,
        "environment": environment(),
        "measurement": "perf_counter_ns immediately around the same complete receiving dispatch for every arm; result validation and logging follow the timer",
        "included": ["fresh source admission and reconstruction", "semantic evaluation",
                     "unchanged type and local-rule checks", "canonical diagnostics",
                     "normal Python garbage collection",
                     "original measurement bookkeeping only in instrumented demand arms"],
        "removed": ["per-event Counter.add calls and counter object",
                    "maximum-stack-depth measurement", "projection measurement updates",
                    "measurement-only returned metadata", "measurement-only accounting self-check"],
        "preserved": derivation["preserved"],
        "preflight": "One untimed call per arm and request. Temporary store hooks compare the exact typed local-value sequence between each demand implementation and its counter-elided derivative. These are the 7390 preflight calls, not additional calls.",
        "trace_scope": "Untimed execution correspondence under an exact AST derivation, not an independent C-semantics proof. A digest and number of stores are retained after exact sequence equality is checked.",
        "timing_hooks": "Every temporary method hook is restored and identity-checked before the first timed call and after measurement.",
        "reference_scope": "Canonical decisions match the retained independent signed study. Original support/point/live preflight results also match their complete prior point-study records.",
        "semantic_work_scope": "Actual counters from the three original preflight arms. Counter-elided results contain status and witness only; no zero work counts are invented.",
        "unit": "Paired repeated requests, described per request, per problem and for all compatible cross-source combinations",
        "population": "All 739 original natural candidate-subject combinations on repair and union domains; no selection by cost or effect direction",
        "campaign_scope": "All reported timing contrasts use this campaign's co-measured arms; previous measured nanoseconds are not reused.",
    }
    retained.save(output / "protocol.json", protocol)
    protocol_identity = retained.file_hash(output / "protocol.json")
    work = []
    old_names = {"support": "support_demand", "point": "point_demand", "live": "live"}
    for index, (task, old, role) in enumerate(task_rows):
        results, traces = {}, {}
        for arm in ARMS:
            if arm == "live":
                got = selected_receivers[arm](task)
            else:
                with elided.capture_stores(arm) as observed:
                    got = selected_receivers[arm](task)
                traces[arm] = observed
            retained.same(retained.decision(got), retained.decision(old), (task["id"], arm, "canonical preflight"))
            if arm in old_names:
                retained.same(got, old_point[task["id"]]["results"][old_names[arm]],
                              (task["id"], arm, "complete prior point-study result"))
            else:
                check(set(got) == {"status", "witness"}, "counter-elided output has no invented metrics")
            results[arm] = got
        for arm in ("support", "point"):
            retained.same(traces[arm], traces[arm + "_uninstrumented"],
                          (task["id"], arm, "exact typed local value/store sequence"))
            check(len(traces[arm]) == results[arm]["semantic_cells"], "one trace event per local store")
        semantic_work = {arm: results[arm]["semantic_cells"] for arm in ("support", "point", "live")}
        check(semantic_work["support"] <= semantic_work["point"] <= semantic_work["live"], "semantic work nesting")
        work.append({
            "id": task["id"], "subject": old["subject"], "problem": old["problem"],
            "stage": old["stage"], "role": role, "sources": old["sources"],
            "points": old["points"], "task_sha256": old["task_sha256"],
            **retained.decision(old), "results": results, "semantic_work": semantic_work,
            "value_traces": {arm: elided.trace_record(values) for arm, values in traces.items()},
            "exact_trace_match": {"support": True, "point": True},
        })
        if (index + 1) % 100 == 0:
            print(json.dumps({"phase": "preflight", "completed": index + 1, "total": len(task_rows)}), flush=True)
    retained.save(output / "work.json", work)
    check(elided.hooks_restored(), "all preflight hooks must be absent before timing")
    check(bindings() == before, "sources unchanged before timing")
    check(retained.file_hash(output / "protocol.json") == protocol_identity, "protocol unchanged before timing")
    timing, blocks = [], []
    design = orders()
    with (output / "timings.jsonl").open("x", encoding="utf-8") as stream:
        for repetition in range(REPETITIONS):
            schedule = list(range(len(task_rows)))
            random.Random(args.seed + repetition).shuffle(schedule)
            started = time.monotonic()
            for position, index in enumerate(schedule):
                task, _old, _role = task_rows[index]
                order = design[(repetition + index) % len(design)]
                measured = {}
                for arm in order:
                    begin = time.perf_counter_ns()
                    got = selected_receivers[arm](task)
                    end = time.perf_counter_ns()
                    measured[arm] = end - begin
                    retained.same(got, work[index]["results"][arm],
                                  (task["id"], arm, repetition, "exact timed preflight result"))
                    del got
                row = {"id": task["id"], "repetition": repetition, "schedule_position": position,
                       "order": list(order), "nanoseconds": measured,
                       "all_results_exactly_matched_preflight": True}
                stream.write(json.dumps(row, separators=(",", ":")) + "\n")
                timing.append(row)
                if (position + 1) % 100 == 0:
                    stream.flush()
                    print(json.dumps({"phase": "timing", "block": repetition + 1,
                                      "completed": position + 1, "total": len(task_rows)}), flush=True)
            blocks.append({"repetition": repetition, "wall_seconds": time.monotonic() - started,
                           "load_average": list(os.getloadavg()) if hasattr(os, "getloadavg") else None})
    analysis = analyze(work, timing, output)
    check(elided.hooks_restored(), "measurement ran without outstanding trace hooks")
    check(bindings() == before, "scientific sources unchanged during execution")
    check(retained.file_hash(args.corpus) == corpus_identity, "input corpus unchanged")
    check(retained.file_hash(args.archive) == protocol["archive_identity"], "external source archive unchanged")
    check(retained.file_hash(output / "protocol.json") == protocol_identity, "protocol unchanged during execution")
    for folder, summary_key, record_key in (
        (args.prior, "prior_summary_identity", "prior_records"),
        (args.point_prior, "point_prior_summary_identity", "point_prior_records"),
    ):
        check(retained.file_hash(folder / "summary.json") == protocol[summary_key], "prior summary unchanged")
        for name, expected in protocol[record_key].items():
            check(retained.file_hash(folder / name) == expected, "prior observation unchanged: " + name)
    for name, expected in {**derived_files, **snapshots}.items():
        check(retained.file_hash(output / name) == expected, "executed source/derivation record changed")
    files = ("protocol.json", "work.json", "timings.jsonl", "request-timing-summary.json", "analysis.json")
    summary = {
        "outcome": "PASS_COUNTER_OVERHEAD_STUDY", "requests": len(work),
        "preflight_receiving_calls": len(work) * 5,
        "timed_receiving_calls": len(timing) * 5, "repetitions_per_request": REPETITIONS,
        "canonical_disagreements": 0, "value_trace_disagreements": 0,
        "source_inputs_unchanged": True, "source_bindings": before,
        "analysis": analysis, "blocks": blocks,
        "records": {name: retained.file_hash(output / name) for name in
                    (*files, *derived_files, *snapshots)},
    }
    retained.save(output / "summary.json", summary)
    return summary


def main():
    require_assertions()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--prior", type=Path, required=True)
    parser.add_argument("--point-prior", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seed", type=int, default=20261121)
    parser.add_argument("--cpu", type=int)
    args = parser.parse_args()
    for name in ("corpus", "archive", "prior", "point_prior", "output"):
        setattr(args, name, getattr(args, name).resolve())
    if args.cpu is not None:
        os.sched_setaffinity(0, {args.cpu})
    output = new_output_directory(args.output)
    try:
        result = run(args, output)
    except BaseException as exc:
        retained.save(output / "summary.json",
                      {"outcome": "FAILED", "error_type": type(exc).__name__, "error": str(exc)})
        raise
    print(json.dumps({key: result[key] for key in
                      ("outcome", "requests", "preflight_receiving_calls", "timed_receiving_calls")}), flush=True)


if __name__ == "__main__":
    main()

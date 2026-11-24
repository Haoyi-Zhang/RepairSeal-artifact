#!/usr/bin/env python3
"""Descriptive, dependency-aware analysis of the retained natural-source replay.

Every statistic derives from the two supplied immutable JSON records.
Per-request observations, candidate--subject combinations, subjects, sources and
problems are different units. No confidence interval or population estimate is
computed from the dependent cross-product workload.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import statistics
from scientific_driver import new_output_directory, require_assertions


def require(condition, context):
    if not condition:
        raise ValueError(context)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True, allow_nan=False) + "\n", encoding="utf-8")


def quantile(values, fraction):
    values = sorted(values)
    position = (len(values) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)
    return values[lower] + (values[upper] - values[lower]) * (position - lower)


def distribution(values):
    if not values:
        return {"n": 0}
    return {"n": len(values), "min": min(values), "q25": quantile(values, .25),
            "median": statistics.median(values), "q75": quantile(values, .75),
            "max": max(values)}


def candidate_class(row):
    src = row["sources"]
    require(src["original"] != src["reference"], (row["id"], "equal own original/reference"))
    if src["candidate"] == src["reference"]:
        return "own_reference"
    if src["candidate"] == src["original"]:
        return "own_original"
    return "cross_source"


def summarize_requests(rows):
    if not rows:
        return {"requests": 0}
    full = sum(row["full_cells"] for row in rows)
    demand = sum(row["demand_cells"] for row in rows)
    by_problem = defaultdict(list)
    for row in rows:
        by_problem[row["problem"]].append(row)
    problem_reductions = [1 - sum(r["demand_cells"] for r in rs) / sum(r["full_cells"] for r in rs)
                          for rs in by_problem.values()]
    result = {
        "requests": len(rows), "problems": len(by_problem),
        "subjects": len({row["subject"] for row in rows}),
        "candidate_sources": len({row["candidate_sha256"] for row in rows}),
        "statuses": dict(sorted(Counter(row["status"] for row in rows).items())),
        "candidate_classes": dict(sorted(Counter(row["candidate_class"] for row in rows).items())),
        "full_cells": full, "demand_cells": demand,
        "pooled_cell_reduction_fraction": 1 - demand / full,
        "request_cell_reduction_fraction": distribution([row["reduction_fraction"] for row in rows]),
        "equal_problem_aggregate_cell_reduction_fraction": distribution(problem_reductions),
        "domain_points": distribution([row["points"] for row in rows]),
        "constructed_nodes": distribution([row["nodes"] for row in rows]),
        "memo_queries_per_semantic_value": distribution([row["memo_queries"] / row["demand_cells"] for row in rows]),
        "existing_one_order_timing_only": {
            "scope": "One retained ordered observation per arm; descriptive only, not a stable speedup estimate.",
            "demand_over_full_ratio": distribution([row["old_timing_demand_ms"] / row["old_timing_full_ms"] for row in rows]),
            "demand_slower_than_full_requests": sum(row["old_timing_demand_ms"] > row["old_timing_full_ms"] for row in rows),
            "full_total_ms": sum(row["old_timing_full_ms"] for row in rows),
            "demand_total_ms": sum(row["old_timing_demand_ms"] for row in rows),
            "direct_record_total_ms": sum(row["old_timing_direct_record_ms"] for row in rows),
        },
    }
    return result


def summarize_combinations(rows):
    accepted = sum(row["repair"] == "ACCEPT" for row in rows)
    reversed_rows = [row for row in rows if row["reversed"]]
    return {
        "combinations": len(rows),
        "subjects": len({row["subject"] for row in rows}),
        "problems": len({row["problem"] for row in rows}),
        "candidate_sources": len({row["candidate_sha256"] for row in rows}),
        "repair_accept": accepted,
        "union_accept": sum(row["union"] == "ACCEPT" for row in rows),
        "repair_accept_union_refute": len(reversed_rows),
        "reversal_fraction_of_repair_acceptances": len(reversed_rows) / accepted if accepted else None,
        "reversal_subjects": len({row["subject"] for row in reversed_rows}),
        "reversal_candidate_sources": len({row["candidate_sha256"] for row in reversed_rows}),
        "reversal_problems": len({row["problem"] for row in reversed_rows}),
        "joint_decisions": dict(sorted(Counter(row["repair"] + "/" + row["union"] for row in rows).items())),
    }


def main():
    require_assertions()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    project, output = args.project.resolve(), new_output_directory(args.output)
    base = args.input.resolve()
    request_path, stage_path = base / "requests.json", base / "stages.json"
    summary = read(base / "summary.json")
    require(summary["outcome"] == "PASS", "source study did not complete")
    input_hashes = {path.name: sha(path) for path in (request_path, stage_path)}
    for name, digest in input_hashes.items():
        require(summary["records"][name] == digest, "source record hash mismatch: " + name)
    requests, combinations = read(request_path), read(stage_path)
    require(type(requests) is list and type(combinations) is list, "records must be lists")
    require(len(requests) == 1478 and len(combinations) == 739, "retained round3 populations changed")
    require(len({row["id"] for row in requests}) == len(requests), "duplicate request id")

    derived, pairs = [], defaultdict(dict)
    for row in requests:
        require(row["stage"] in {"repair", "union"}, "unknown stage")
        require(row["status"] in {"ACCEPT", "REFUTED"}, "unknown decision")
        require(row["full"]["semantic_cells"] == row["full"]["nodes"] * len(row["points"]), "full cell accounting")
        require(row["direct_record"]["semantic_cells"] == row["full"]["semantic_cells"], "direct record accounting")
        for arm in ("full", "demand", "direct_record"):
            require(row[arm]["status"] == row["status"] and row[arm]["witness"] == row["witness"], (row["id"], arm, "canonical disagreement"))
        require(0 < row["demand"]["semantic_cells"] <= row["full"]["semantic_cells"], "demand bounds")
        key = (row["subject"], row["sources"]["candidate"])
        require(row["stage"] not in pairs[key], "duplicate candidate-subject stage")
        pairs[key][row["stage"]] = row
        counters = row["demand"]["counters"]
        derived.append({
            "id": row["id"], "subject": row["subject"], "problem": row["problem"],
            "candidate_sha256": row["sources"]["candidate"], "candidate_class": candidate_class(row),
            "stage": row["stage"], "status": row["status"], "points": len(row["points"]),
            "input_arity": len(row["points"][0]), "nodes": row["full"]["nodes"],
            "full_cells": row["full"]["semantic_cells"], "demand_cells": row["demand"]["semantic_cells"],
            "reduction_fraction": 1 - row["demand"]["semantic_cells"] / row["full"]["semantic_cells"],
            "memo_queries": counters["cache_queries"], "memo_hits": counters["cache_hits"],
            "memo_key_coordinates": counters["key_coordinates"],
            "root_predicate_tests": counters["root_predicate_tests"],
            "diagnostic_points": counters["diagnostic_points"],
            "trace_events_examined": counters["trace_events_examined"],
            "conditional_choices": counters["conditional_choices"],
            "old_timing_full_ms": row["timing_ms"]["full_receiving"],
            "old_timing_demand_ms": row["timing_ms"]["demand_receiving"],
            "old_timing_direct_record_ms": row["timing_ms"]["direct_record_receiving"],
        })

    stages = []
    require(len(pairs) == len(combinations), "combination join count")
    seen_combinations = set()
    for row in combinations:
        key = (row["subject"], row["candidate_sha256"])
        require(key in pairs and key not in seen_combinations, "missing/duplicate stage join")
        seen_combinations.add(key)
        pair = pairs[key]
        require(set(pair) == {"repair", "union"}, "incomplete stage pair")
        for stage in pair:
            require(row[stage] == pair[stage]["status"], "stage decision mismatch")
            require(row[stage + "_points"] == len(pair[stage]["points"]), "stage domain mismatch")
        require(set(map(tuple, pair["repair"]["points"])) <= set(map(tuple, pair["union"]["points"])), "domain union is not an extension")
        require(not (row["repair"] == "REFUTED" and row["union"] == "ACCEPT"), "acceptance monotonicity failure")
        stages.append({**row, "candidate_class": candidate_class(pair["repair"]),
                       "reversed": row["repair"] == "ACCEPT" and row["union"] == "REFUTED"})

    grouped_requests = {}
    for stage in ("repair", "union", "combined"):
        subset = [row for row in derived if stage == "combined" or row["stage"] == stage]
        grouped_requests[stage] = {
            "all": summarize_requests(subset),
            "by_status": {status: summarize_requests([row for row in subset if row["status"] == status]) for status in ("ACCEPT", "REFUTED")},
            "by_candidate_class": {kind: summarize_requests([row for row in subset if row["candidate_class"] == kind]) for kind in ("own_reference", "own_original", "cross_source")},
        }
    per_problem = []
    for problem in sorted({row["problem"] for row in derived}):
        subset = [row for row in stages if row["problem"] == problem]
        per_problem.append({
            "problem": problem,
            "combinations": summarize_combinations(subset),
            "candidate_classes": dict(sorted(Counter(row["candidate_class"] for row in subset).items())),
            "requests": {stage: summarize_requests([row for row in derived if row["problem"] == problem and row["stage"] == stage]) for stage in ("repair", "union")},
        })
    overall_combinations = summarize_combinations(stages)
    combination_groups = {kind: summarize_combinations([row for row in stages if row["candidate_class"] == kind]) for kind in ("own_reference", "own_original", "cross_source")}
    analysis = {
        "schema": "repairseal-round4-natural-descriptive-audit-v1",
        "source_records": {str(path.relative_to(project)): {"sha256": sha(path), "bytes": path.stat().st_size} for path in (request_path, stage_path)},
        "analysis_script_sha256": sha(Path(__file__)),
        "units": {
            "request": "One candidate/subject/stage finite decision; repair and union stages are paired, not independent.",
            "combination": "One candidate source paired with one subject of the same problem, evaluated on both stages.",
            "problem": "One benchmark problem; candidates, references and tests can be shared by its combinations.",
            "pooled_cell_reduction": "1 - sum(demand semantic cells) / sum(full semantic cells); weights requests by their full cells.",
            "request_distribution": "Distribution of 1 - demand/full within the named requests; each request contributes once.",
            "equal_problem_distribution": "For each included problem first sum cells over its included requests, then summarize its ratio; each problem contributes once.",
            "quantiles": "Empirical linear interpolation at (n-1)*p, including endpoints; median agrees with statistics.median.",
            "candidate_classes": "own_reference and own_original mean exact source-content hash equality with that subject; cross_source is every other admitted same-problem candidate.",
            "reversal_fraction": "A descriptive fraction of repair-stage acceptances in this constructed replay; not an APR success rate, prevalence estimate or independent-sample estimate.",
        },
        "request_statistics": grouped_requests,
        "combination_statistics": {"all": overall_combinations, "by_candidate_class": combination_groups},
        "concentration": {
            "reversal_problems": sum(row["combinations"]["repair_accept_union_refute"] > 0 for row in per_problem),
            "no_reversal_problems": sum(row["combinations"]["repair_accept_union_refute"] == 0 for row in per_problem),
            "problems_with_no_cross_source_combinations": [row["problem"] for row in per_problem if row["candidate_classes"].get("cross_source", 0) == 0],
            "largest_reversal_contributors": [{"problem": row["problem"], "reversals": row["combinations"]["repair_accept_union_refute"], "fraction_of_all_reversals": row["combinations"]["repair_accept_union_refute"] / overall_combinations["repair_accept_union_refute"]} for row in sorted(per_problem, key=lambda row: (-row["combinations"]["repair_accept_union_refute"], row["problem"]))[:5]],
        },
        "mechanism_identifiability": {
            "directly_recorded": ["full and demand total semantic values", "memo query/hit counts and key-coordinate work", "support construction counts", "root predicate tests", "diagnostic point and trace-event visits", "conditional choices", "exact-point representative construction"],
            "not_separately_identified": ["full-DAG versus live-node saving", "live-node versus support-projected saving", "conditional short circuit versus first-failed-obligation stopping versus delayed trace work"],
            "reason": "The retained signed study has no live-vector/projected-live arm and no per-phase semantic counts. Conditional-choice counts are not counts of saved values. Shared DAG and memo keys make counterfactual savings non-additive without a fixed decomposition order.",
            "needed_comparison": "On identical requests and canonical outputs, measure full -> live-vector -> projected-live -> demand; report the final difference jointly unless new controlled evaluator variants isolate individual mechanisms.",
            "all_axes_note": "All input axes can occur in an obligation while individual internal nodes depend on fewer coordinates. Root relevance alone does not rule out internal-node projection reuse, constant reuse, unused reconstructed terms or conditional evaluation.",
        },
        "inference_limits": ["No sampling inference or confidence intervals are produced from the dependent workload.", "Existing one-order timing values are reported only as observations; a balanced repeated paired protocol is needed for runtime conclusions.", "Semantic-cell savings do not by themselves establish lower wall time or memory consumption.", "95 own-reference combinations and 95 own-original combinations are natural source sanity controls; report the 549 cross-source combinations separately."],
    }
    for name, digest in input_hashes.items():
        require(sha(base / name) == digest, "source record changed during analysis: " + name)
    save(output / "analysis.json", analysis)
    save(output / "request-derived.json", derived)
    save(output / "combination-derived.json", stages)
    save(output / "problem-derived.json", per_problem)
    with (output / "request-derived.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(derived[0]))
        writer.writeheader(); writer.writerows(derived)
    print(json.dumps({"output": str(output), "requests": len(derived), "combinations": overall_combinations, "classes": combination_groups, "concentration": analysis["concentration"]}, indent=2))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Secondary descriptive analysis of retained CPAchecker search statistics.

Input-projection and trivial violation witnesses use the same receiver
configuration and Boolean task.  No elapsed-time inference is made here.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import statistics

if not __debug__:
    raise SystemExit("Witness-search analysis requires assertions enabled; -O and -OO are rejected.")

METRICS = {
    "iterations": "Number of iterations",
    "cegar_refinements": "Number of CEGAR refinements",
    "abstraction_computations": "Number of abstraction computations",
    "reached_states": "Size of reached set",
}
METRIC_OWNERS = {
    "iterations": "CPA algorithm",
    "cegar_refinements": "CEGAR algorithm",
    "abstraction_computations": "ValueAnalysisPrecisionAdjustment",
    "reached_states": "CPAchecker general",
}


def extract(text):
    values, issues = {}, {}
    for name, label in METRICS.items():
        found = re.findall(r"^" + re.escape(label) + r":\s+(\d+)\b", text, re.M)
        if len(found) == 1:
            values[name] = int(found[0])
        else:
            issues[name] = "missing" if not found else "multiple statistics blocks"
    return values, issues


def extract_owned(text):
    values, issues = extract(text)
    owners = {name: [] for name in METRICS}
    section = None
    for line in text.splitlines():
        if line.endswith(" statistics"):
            section = line[:-len(" statistics")]
        for name, label in METRICS.items():
            if re.match(r"^" + re.escape(label) + r":\s+\d+\b", line):
                owners[name].append(section)
    for name in list(values):
        if owners[name] != [METRIC_OWNERS[name]]:
            del values[name]
            issues[name] = "missing or unexpected statistics owner"
    return values, issues, owners


def started_analyses(stderr):
    loaded = {}
    sequence, issues = [], []
    for line in stderr.splitlines():
        load = re.match(r"^Loading analysis ([0-9]+) from file (.+?) \.\.\.", line)
        if load:
            number = int(load[1])
            loaded.setdefault(number, []).append(load[2])
            if len(loaded[number]) != 1:
                issues.append(f"analysis {number} loaded more than once")
        start = re.match(r"^Starting analysis ([0-9]+) \.\.\.", line)
        if start:
            number = int(start[1])
            configurations = loaded.get(number, [])
            if len(configurations) != 1:
                issues.append(f"analysis {number} has no unique preceding configuration load")
            sequence.append({"analysis": number, "configuration": configurations[0] if len(configurations) == 1 else None})
    if len(sequence) != 1:
        issues.append("exactly one started analysis is required for a matched statistics block")
    return sequence, issues


def command_profile(argv, arm):
    # Commands differ in output directory and witness filename.  All semantic
    # options, receiver executable, memory limits and property remain equal.
    result = []
    i = 0
    while i < len(argv):
        if argv[i] == "--output-path":
            result += [argv[i], "<output>"]
            i += 2
        elif argv[i] == "--witness":
            assert argv[i + 1] == arm + ".graphml"
            result += [argv[i], "<witness>"]
            i += 2
        else:
            result.append(argv[i])
            i += 1
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output must be a new file; completed evidence is never overwritten")
    study = args.study.resolve()
    protocol = json.loads((study / "protocol.json").read_text())
    summary = json.loads((study / "summary.json").read_text())
    assert summary["outcome"] == "COMPLETE_WITH_RECORDED_EXTERNAL_OUTCOMES"
    assert summary["source_inputs_and_tools_unchanged"] is True
    assert summary["control_runs"] == 18
    cases = json.loads((study / "cases.json").read_text())
    assert len(cases) == 804
    assert [case["index"] for case in cases] == list(range(804))
    assert Counter(case["population"] for case in cases) == {"core": 380, "grammar": 400, "natural": 24}
    for case in cases:
        if case["producer"]["status"] in {"ACCEPT", "REFUTED"}:
            assert set(case["arms"]) == {"direct", "raw", "context", "standard", "located", "input", "trivial"}
        else:
            assert not case["arms"]
    violations = [row for row in cases if row["receiver_status"] == "REFUTED"]
    assert len(violations) == 594
    rows = []
    for case in violations:
        row = {"index": case["index"], "population": case["population"], "request_id": case["request_id"],
               "input": {}, "trivial": {}}
        directory = study / "cases" / f"{case['index']:04d}"
        for arm in ("input", "trivial"):
            result = case["arms"].get(arm)
            if result is None:
                row[arm] = {"outcome": "NOT_RUN", "metrics": {}, "issues": {"run": "producer unresolved"},
                            "ignored_annotation_warning_count": 0, "statistic_owners": {},
                            "started_analysis_sequence": [], "analysis_log_issues": ["no receiving invocation"]}
                continue
            metrics, issues = {}, {}
            owners, sequence, analysis_issues = {}, [], ["no receiving invocation"]
            if "argv" in result:
                metrics, issues, owners = extract_owned((directory / (arm + ".stdout.txt")).read_text())
                sequence, analysis_issues = started_analyses((directory / (arm + ".stderr.txt")).read_text())
                if any(event["configuration"] not in protocol["external_tool_files"] for event in sequence):
                    analysis_issues.append("started configuration is absent from the bound validator files")
            row[arm] = {"outcome": result["outcome"], "metrics": metrics, "issues": issues,
                        "ignored_annotation_warning_count": len(result["ignored_semantic_annotations"]),
                        "statistic_owners": owners, "started_analysis_sequence": sequence,
                        "analysis_log_issues": analysis_issues}
        if all("argv" in case["arms"].get(arm, {}) for arm in ("input", "trivial")):
            assert command_profile(case["arms"]["input"]["argv"], "input") == command_profile(case["arms"]["trivial"]["argv"], "trivial")
            row["matched_receiver_configuration"] = (
                not row["input"]["analysis_log_issues"] and not row["trivial"]["analysis_log_issues"] and
                row["input"]["started_analysis_sequence"] == row["trivial"]["started_analysis_sequence"])
        else:
            row["matched_receiver_configuration"] = False
        rows.append(row)
    groups = {}
    for population in ("core", "grammar", "natural", "all"):
        selected = rows if population == "all" else [row for row in rows if row["population"] == population]
        matched = [row for row in selected if row["matched_receiver_configuration"] and
                   all(row[arm]["outcome"] == "CONFIRMED" for arm in ("input", "trivial"))]
        both_confirmed = [row for row in selected if all(row[arm]["outcome"] == "CONFIRMED" for arm in ("input", "trivial"))]
        group = {"planned_refutations": len(selected), "both_confirmed": len(both_confirmed),
                 "both_confirmed_with_single_matching_analysis": len(matched),
                 "both_confirmed_but_unmatched_or_ambiguous_analysis": len(both_confirmed) - len(matched),
                 "input_outcomes": dict(Counter(row["input"]["outcome"] for row in selected)),
                 "trivial_outcomes": dict(Counter(row["trivial"]["outcome"] for row in selected)),
                 "input_runs_with_ignored_annotation_warning": sum(row["input"]["ignored_annotation_warning_count"] > 0 for row in selected),
                 "trivial_runs_with_ignored_annotation_warning": sum(row["trivial"]["ignored_annotation_warning_count"] > 0 for row in selected),
                 "metrics": {}}
        for name in METRICS:
            pairs = [(row["input"]["metrics"][name], row["trivial"]["metrics"][name])
                     for row in matched if all(name in row[arm]["metrics"] for arm in ("input", "trivial"))]
            ratios = [a / b for a, b in pairs if b > 0]
            group["metrics"][name] = {
                "matched_complete_statistics": len(pairs),
                "both_confirmed_but_missing_or_ambiguous_statistics": len(matched) - len(pairs),
                "input_total": sum(a for a, _ in pairs), "trivial_total": sum(b for _, b in pairs),
                "input_lower": sum(a < b for a, b in pairs), "equal": sum(a == b for a, b in pairs),
                "input_higher": sum(a > b for a, b in pairs),
                "positive_denominator_ratios": len(ratios), "zero_trivial_denominators": sum(b == 0 for _, b in pairs),
                "zero_input_numerators": sum(a == 0 for a, _ in pairs),
                "both_zero": sum(a == 0 and b == 0 for a, b in pairs),
                "median_input_to_trivial_ratio": statistics.median(ratios) if ratios else None,
                "minimum_ratio": min(ratios) if ratios else None,
                "maximum_ratio": max(ratios) if ratios else None,
            }
        groups[population] = group
    result = {"analysis": "Secondary descriptive analysis of retained search statistics",
              "selection": "All 594 planned refutations; no selection by effect direction. Counter comparisons require both arms confirmed, the same unique started analysis configuration in stderr, and exactly one correctly owned statistics block per metric.",
              "measures": METRICS, "statistic_owners": METRIC_OWNERS, "groups": groups, "requests": rows,
              "configuration_basis": "Actual Loading analysis N / Starting analysis N events in stderr; stdout's restart summary and Last algorithm field do not identify the started engine.",
              "interpretation": "Iterations, CEGAR refinements, value-analysis abstraction computations and reached states are distinct receiver-specific units. ValueAnalysisPrecisionAdjustment's computation counter is not PredicateCPA's Number of abstractions. Ratios describe dependent workloads, not independent defect rates. One process timing per arm under concurrent execution does not support a speed claim.",
              "outcome": "PASS_MATCHED_STATISTICS_RECONCILIATION"}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"outcome": result["outcome"], "groups": groups}, indent=2))


if __name__ == "__main__":
    main()

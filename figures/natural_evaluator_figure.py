"""Render the signed natural-source evaluator study after its final PASS record.

The first panel shows per-request semantic-cell ratios; the second shows
per-request ratios of ten-repetition median receiving-call durations. Both
panels are descriptive ECDFs against the live-node direct evaluator.
No figure is produced for an incomplete study. Timing medians and aggregate
work are recomputed from the bound raw files before rendering.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import statistics

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter

ARMS = ("full", "live", "projected_live", "demand", "direct_record")
STAGES = ("repair", "union")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate data key: " + key)
            result[key] = value
        return result
    def bad(value):
        raise ValueError("nonfinite number: " + value)
    return json.loads(path.read_text(), object_pairs_hook=pairs, parse_constant=bad)


def checked_study(directory):
    summary = load(directory / "summary.json")
    if summary.get("outcome") != "PASS":
        raise ValueError("a complete passing evaluator study is required")
    for name, expected in summary["records"].items():
        if sha(directory / name) != expected:
            raise ValueError("study record binding: " + name)
    if sha(directory / "protocol.json") != summary["protocol_sha256"]:
        raise ValueError("study protocol binding")
    protocol = load(directory / "protocol.json")
    repetitions = protocol["repetitions_per_request"]
    if repetitions != 10 or summary["repetitions_per_request"] != repetitions:
        raise ValueError("the figure requires the ten-repetition protocol")
    if protocol["arms"] != list(ARMS):
        raise ValueError("evaluator arms")
    work = load(directory / "work.json")
    statistics_rows = load(directory / "request-timing-summary.json")
    analysis = load(directory / "analysis.json")
    by_id = {row["id"]: row for row in work}
    stats = {row["id"]: row for row in statistics_rows}
    if len(by_id) != len(work) or len(stats) != len(statistics_rows) or set(by_id) != set(stats):
        raise ValueError("request identities")
    if len(work) != summary["requests"] or len(work) != protocol["requests"]:
        raise ValueError("request population")
    measured = defaultdict(lambda: defaultdict(list))
    visits = defaultdict(list)
    for line in (directory / "timings.jsonl").read_text().splitlines():
        row = json.loads(line)
        if row["id"] not in by_id or sorted(row["order"]) != sorted(ARMS):
            raise ValueError("unknown timed request or arm order")
        if sorted(row["nanoseconds"]) != sorted(ARMS):
            raise ValueError("incomplete measured arms")
        visits[row["id"]].append((row["repetition"], tuple(row["order"])))
        for arm, value in row["nanoseconds"].items():
            if type(value) is not int or value <= 0:
                raise ValueError("duration must be positive integer nanoseconds")
            measured[row["id"]][arm].append(value)
    groups = {stage: [] for stage in STAGES}
    for key, row in by_id.items():
        if row["stage"] not in STAGES:
            raise ValueError("unknown stage")
        if sorted(rep for rep, _ in visits[key]) != list(range(repetitions)):
            raise ValueError("one measurement per request per repetition")
        if Counter(order for _, order in visits[key]) != Counter(map(tuple, protocol["orders"])):
            raise ValueError("balanced evaluator orders")
        medians = {arm: statistics.median(measured[key][arm]) for arm in ARMS}
        if medians != stats[key]["median_ns"] or row["stage"] != stats[key]["stage"]:
            raise ValueError("timing median or stage mismatch")
        ratio = medians["demand"] / medians["live"]
        if ratio != stats[key]["demand_over_live"]:
            raise ValueError("timing-ratio denominator")
        cells = {arm: row["results"][arm]["semantic_cells"] for arm in ARMS}
        if any(type(value) is not int or value < 0 for value in cells.values()):
            raise ValueError("semantic-cell counter type")
        if not cells["demand"] <= cells["projected_live"] <= cells["live"] <= cells["full"] == cells["direct_record"]:
            raise ValueError("nested semantic work")
        groups[row["stage"]].append({"id": key, "cells": cells, "time_ratio": ratio})
    if summary["timed_receiving_calls"] != len(work) * repetitions * len(ARMS):
        raise ValueError("measured-call count")
    for stage, rows in groups.items():
        totals = {arm: sum(row["cells"][arm] for row in rows) for arm in ARMS}
        if not rows or len(rows) != analysis[stage]["requests"] or totals != analysis[stage]["cells"]:
            raise ValueError("stage totals: " + stage)
        if analysis[stage] != summary["work"][stage]:
            raise ValueError("analysis summary binding: " + stage)
    return groups, analysis, protocol


def figure(groups, analysis, protocol, out, r3):
    fig, (left, right) = plt.subplots(1, 2, figsize=(428.42 / 72, 263 / 72))
    fig.subplots_adjust(left=.10, right=.985, bottom=.27, top=.79, wspace=.31)
    colors = {"repair": "#66747c", "union": "#24596e"}
    for stage in STAGES:
        if any(row["cells"]["live"] <= 0 for row in groups[stage]):
            raise ValueError("the live-node cell denominator must be positive")
        frequencies = Counter(row["cells"]["demand"] / row["cells"]["live"] for row in groups[stage])
        xs, ys, cumulative = [0], [0], 0
        for ratio, count in sorted(frequencies.items()):
            cumulative += count
            xs.append(ratio); ys.append(cumulative/len(groups[stage]))
        xs.append(1.05); ys.append(1)
        left.step(xs, ys, where="post", color=colors[stage], linewidth=1.05,
                  linestyle=(0, (4, 2)) if stage == "repair" else "-", zorder=3)
    left.axvline(1, color=r3.GRAY, linewidth=.75, linestyle=(0, (2, 2)), zorder=1)
    left.set_xlim(0, 1.05); left.set_ylim(0, 1.025)
    left.set_xticks([0, .25, .5, .75, 1], ["0", "0.25", "0.5", "0.75", "1"])
    left.set_yticks([0, .25, .5, .75, 1], ["0", "25", "50", "75", "100"])
    left.set_ylabel("Requests (%)", fontsize=9.3, labelpad=4)
    left.set_xlabel("Demand / live-node cells", fontsize=9.3, labelpad=6)
    left.set_title("(a) Semantic-cell ratios", fontsize=10, pad=9)
    left.grid(axis="y", color=r3.RULE, linewidth=.55)
    left.set_axisbelow(True)

    all_ratios = [row["time_ratio"] for rows in groups.values() for row in rows]
    xmin, xmax = min(min(all_ratios), 1) / 1.12, max(max(all_ratios), 1) * 1.12
    for stage in STAGES:
        frequencies = Counter(row["time_ratio"] for row in groups[stage])
        xs, ys, cumulative = [xmin], [0], 0
        for ratio, count in sorted(frequencies.items()):
            cumulative += count
            xs.append(ratio); ys.append(cumulative/len(groups[stage]))
        xs.append(xmax); ys.append(1)
        right.step(xs, ys, where="post", color=colors[stage], linewidth=1.05,
                   linestyle=(0, (4, 2)) if stage == "repair" else "-", zorder=3)
    right.axvline(1, color=r3.GRAY, linewidth=.75, linestyle=(0, (2, 2)), zorder=1)
    right.set_xscale("log")
    right.set_xlim(xmin, xmax); right.set_ylim(0, 1.025)
    powers = list(range(math.floor(math.log2(xmin)), math.ceil(math.log2(xmax))+1))
    ticks = [2**power for power in powers if xmin <= 2**power <= xmax]
    if len(ticks) > 6:
        ticks = [tick for tick in ticks if round(math.log2(tick)) % 2 == 0 or tick == 1]
    right.xaxis.set_major_locator(FixedLocator(ticks))
    right.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}"))
    right.xaxis.set_minor_formatter(NullFormatter())
    right.set_yticks([0, .25, .5, .75, 1], ["0", "25", "50", "75", "100"])
    right.set_xlabel("Demand / live-node time", fontsize=9.3, labelpad=6)
    right.set_title("(b) Instrumented time ratios", fontsize=10, pad=9)
    right.grid(axis="y", color=r3.RULE, linewidth=.55)
    right.set_axisbelow(True)
    handles = [Line2D([], [], color=colors[stage], linestyle=(0, (4, 2)) if stage == "repair" else "-",
                      label=stage.capitalize()+f" ({len(groups[stage])} requests)") for stage in STAGES]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(.53,.99), ncol=2,
               frameon=False, fontsize=9.4, handlelength=2.2, columnspacing=2.0)
    fig.text(.5, .105, "Below 1: fewer cells in (a) or shorter receiving time in (b).",
             ha="center", va="center", fontsize=9.1)
    fig.text(.5, .045, f"Timing uses each request's median over {protocol['repetitions_per_request']} receiving calls per method.",
             ha="center", va="center", fontsize=9.1)
    r3.save_figure(fig, out, "natural-evaluator-comparison")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    groups, analysis, protocol = checked_study(args.input)
    source = args.project_root / "artifact/figures/figure_style.py"
    spec = importlib.util.spec_from_file_location("round3_figures", source)
    r3 = importlib.util.module_from_spec(spec); spec.loader.exec_module(r3)
    r3.style()
    figure(groups, analysis, protocol, args.output, r3)
    manifest = {"schema": "repairseal-natural-evaluator-figure-v1", "script_sha256": sha(Path(__file__)),
                "helper_sha256": sha(source),
                "data_inputs": {name: sha(args.input/name) for name in (
                    "summary.json", "protocol.json", "work.json", "timings.jsonl",
                    "request-timing-summary.json", "analysis.json")},
                "populations": {stage: len(rows) for stage, rows in groups.items()},
                "work": {stage: analysis[stage]["cells"] for stage in STAGES},
                "work_plot": "per-request demand/live-node semantic-cell ratio ECDF; linear x axis 0 to 1.05",
                "timing_unit": "ratio of per-request medians of ten complete receiving-call durations",
                "timing_denominator": "live-node direct evaluator",
                "ecdf_unit": "request; both panels include every request in each measured stage; descriptive distribution, no independence or population inference",
                "outputs": {name: sha(args.output/name) for name in (
                    "natural-evaluator-comparison.pdf", "natural-evaluator-comparison.svg")}}
    (args.output/"natural-evaluator-figure-manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps({"output": str(args.output), "populations": manifest["populations"]}))


if __name__ == "__main__":
    main()

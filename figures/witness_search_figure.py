"""Plot matched external-receiver search work from the completed witness study.

Every planned refutation remains in the input inventory. A ratio requires both
arms to confirm the property result, the same single started analysis, and
both raw logs to contain one correctly owned counter.
The plot uses recorded algorithm counters, not elapsed time.
"""
from __future__ import annotations

import argparse
from collections import Counter
import importlib.util
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter

METRICS = (("iterations", "Number of iterations", "(a) CPA algorithm\niterations"),
           ("abstraction_computations", "Number of abstraction computations", "(b) Value-analysis\nabstraction computations"))
POPULATIONS = ("core", "grammar", "natural")


def require(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def checked_inputs(directory):
    summary = read(directory / "summary.json")
    protocol = read(directory / "protocol.json")
    report = read(directory / "search-statistics.json")
    cases = read(directory / "cases.json")
    require(summary["outcome"] == "COMPLETE_WITH_RECORDED_EXTERNAL_OUTCOMES", "complete external campaign")
    require(summary["source_inputs_and_tools_unchanged"], "fixed source, input and tools")
    require(len(cases) == len({r["index"] for r in cases}) == 804, "complete unique request population")
    require(report["outcome"] == "PASS_MATCHED_STATISTICS_RECONCILIATION", "completed counter analysis")
    planned = {r["index"]: r for r in cases if r["receiver_status"] == "REFUTED"}
    rows = report["requests"]
    require(len(planned) == len(rows) == len({r["index"] for r in rows}) == 594,
            "all planned refutations retained")
    require({r["index"] for r in rows} == set(planned), "complete refutation identities")
    analyzer_path = Path(__file__).resolve().parents[1] / "tests/analyze_witness_search.py"
    spec = importlib.util.spec_from_file_location("witness_search_analysis", analyzer_path)
    analyzer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(analyzer)
    groups = {metric: {population: [] for population in POPULATIONS} for metric, _, _ in METRICS}
    excluded = {metric: Counter() for metric, _, _ in METRICS}
    for row in rows:
        case = planned[row["index"]]
        require(row["population"] == case["population"] and row["request_id"] == case["request_id"],
                "counter-to-case correspondence")
        raw = {}
        for arm in ("input", "trivial"):
            if "argv" not in case["arms"].get(arm, {}):
                continue
            folder = directory / "cases" / f"{row['index']:04d}"
            metrics, issues, owners = analyzer.extract_owned((folder / (arm + ".stdout.txt")).read_text())
            sequence, analysis_issues = analyzer.started_analyses((folder / (arm + ".stderr.txt")).read_text())
            if any(event["configuration"] not in protocol["external_tool_files"] for event in sequence):
                analysis_issues.append("started configuration is absent from the bound validator files")
            require(row[arm]["metrics"] == metrics and row[arm]["issues"] == issues and
                    row[arm]["statistic_owners"] == owners and
                    row[arm]["started_analysis_sequence"] == sequence and
                    row[arm]["analysis_log_issues"] == analysis_issues,
                    "raw counter ownership and started-analysis agreement")
            raw[arm] = {"metrics": metrics, "sequence": sequence, "issues": analysis_issues}
        if set(raw) == {"input", "trivial"}:
            matched = (not raw["input"]["issues"] and not raw["trivial"]["issues"] and
                       raw["input"]["sequence"] == raw["trivial"]["sequence"] and
                       analyzer.command_profile(case["arms"]["input"]["argv"], "input") ==
                       analyzer.command_profile(case["arms"]["trivial"]["argv"], "trivial"))
            require(row["matched_receiver_configuration"] == matched, "actual matched receiving configuration")
        for metric, label, _ in METRICS:
            counts = []
            reason = None
            for arm in ("input", "trivial"):
                outcome = case["arms"][arm]["outcome"]
                require(row[arm]["outcome"] == outcome, "counter receiving outcome")
                if outcome != "CONFIRMED":
                    reason = "unconfirmed_or_unresolved"
                    break
                if metric not in raw.get(arm, {}).get("metrics", {}):
                    reason = "missing_or_ambiguous_counter"
                    break
                count = raw[arm]["metrics"][metric]
                require(row[arm]["metrics"].get(metric) == count, "raw search-counter agreement")
                counts.append(count)
            if reason:
                excluded[metric][reason] += 1
                continue
            if not row["matched_receiver_configuration"]:
                excluded[metric]["unmatched_or_ambiguous_started_analysis"] += 1
                continue
            if counts[1] == 0:
                excluded[metric]["zero_baseline"] += 1
                continue
            require(counts[0] > 0, "zero numerator requires an explicit non-logarithmic display")
            groups[metric][row["population"]].append({"input": counts[0], "trivial": counts[1]})
    for metric, _, _ in METRICS:
        require(sum(map(len, groups[metric].values())) + sum(excluded[metric].values()) == 594,
                "plotted and excluded denominator")
        for population in POPULATIONS:
            expected = report["groups"][population]["metrics"][metric]["positive_denominator_ratios"]
            require(len(groups[metric][population]) == expected, "plotted metric denominator")
            require(groups[metric][population], "each population needs a recorded comparison")
    return groups, excluded


def plot(groups, excluded, output, style, variant=4, name="witness-search-work"):
    """Pairwise counter scatter plots; below equality means less search with the supplied input."""
    fig, axes = plt.subplots(1, 2, figsize=(428.42/72, 238/72))
    fig.subplots_adjust(left=.108, right=.985, bottom=.235, top=.79, wspace=.28)
    colors={"core":style.GRAY,"grammar":style.BLUE,"natural":style.INK}
    markers={"core":"s","grammar":"o","natural":"^"}
    faces={"core":"white","grammar":style.BLUE,"natural":"white"}
    titles={"iterations":"(a) CPA iterations","abstraction_computations":"(b) Value abstractions"}
    for axis,(metric,_label,_old_title) in zip(axes,METRICS):
        all_rows=[row for population in POPULATIONS for row in groups[metric][population]]
        all_values=[v for row in all_rows for v in (row["input"],row["trivial"])]
        lo=max(.8,min(all_values)/1.35); hi=max(all_values)*1.35
        axis.plot([lo,hi],[lo,hi],color=style.INK,lw=.8,linestyle=(0,(4,3)),zorder=1)
        for pop in POPULATIONS:
            rows=groups[metric][pop]
            axis.scatter([r["trivial"] for r in rows],[r["input"] for r in rows],
                         s=11 if pop!="natural" else 24,marker=markers[pop],
                         facecolors=faces[pop],edgecolors=colors[pop],linewidths=.7,
                         alpha=.42 if pop!="natural" else .95,zorder=3)
        axis.set_xscale("log"); axis.set_yscale("log")
        axis.set_xlim(lo,hi); axis.set_ylim(lo,hi)
        axis.set_aspect("equal",adjustable="box")
        axis.set_title(titles[metric],fontsize=9.7,pad=7)
        axis.set_xlabel("trivial-witness counter",fontsize=8.6,labelpad=5)
        axis.grid(which="major",color=style.RULE,lw=.45)
        axis.set_axisbelow(True)
    axes[0].set_ylabel("supplied-input counter",fontsize=8.8,labelpad=4)
    handles=[]
    denoms={p:len(groups["iterations"][p]) for p in POPULATIONS}
    for pop in POPULATIONS:
        handles.append(Line2D([],[],marker=markers[pop],linestyle="none",
                              markerfacecolor=faces[pop],markeredgecolor=colors[pop],
                              markeredgewidth=.8,markersize=4.5,
                              label=f"{pop.capitalize()} ({denoms[pop]})"))
    fig.legend(handles=handles,loc="upper center",bbox_to_anchor=(.53,.975),ncol=3,
               frameon=False,fontsize=8.6,columnspacing=1.1,handletextpad=.45)
    style.save_figure(fig, output, name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.project_root.resolve()
    helper = root / "artifact/figures/figure_style.py"
    if not helper.exists():
        helper = root / "artifact/figures/figure_style.py"
    spec = importlib.util.spec_from_file_location("figure_style", helper)
    style = importlib.util.module_from_spec(spec); spec.loader.exec_module(style); style.style()
    args.output.mkdir(parents=True, exist_ok=True)
    groups, excluded = checked_inputs(args.input.resolve())
    plot(groups, excluded, args.output.resolve(), style)
    print(json.dumps({"outcome": "PLOTTED_RECONCILED_SEARCH_COUNTERS", "excluded": excluded}))

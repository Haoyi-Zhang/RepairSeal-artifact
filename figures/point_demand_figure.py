"""Plot the completed paired demand ablation from individual measured calls."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import importlib.util
import json
from pathlib import Path
import statistics
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator


def read(path):
    return json.loads(path.read_text())


def inputs(root, directory):
    sys.path.insert(0, str(root/"artifact/tests"))
    from verify_point_demand_study import verify
    reference = root/"artifact/data/signed-contract/requests.json"
    if not reference.exists():
        reference = root/"artifact/data/signed-contract/requests.json"
    verify(directory, reference)
    work = read(directory/"work.json")
    times = defaultdict(lambda: defaultdict(list))
    for line in (directory/"timings.jsonl").read_text().splitlines():
        row = json.loads(line)
        for arm, value in row["nanoseconds"].items():
            times[row["id"]][arm].append(value)
    groups = {stage: [] for stage in ("repair", "union")}
    for row in work:
        point = row["results"]["point_demand"]["semantic_cells"]
        support = row["results"]["support_demand"]["semantic_cells"]
        median = {arm: statistics.median(values) for arm, values in times[row["id"]].items()}
        groups[row["stage"]].append({"cells": point/support,
                                    "time": median["point_demand"]/median["support_demand"]})
    return groups


def plot(groups, output, style, variant=4, name="point-demand-comparison"):
    """Compact paired ECDFs with direct median annotations."""
    fig, axes = plt.subplots(1, 2, figsize=(428.42/72, 205/72))
    fig.subplots_adjust(left=.102, right=.985, bottom=.245, top=.83, wspace=.28)
    colors = {"repair": style.GRAY, "union": style.BLUE}
    lines = {"repair": (0, (4, 2)), "union": "-"}
    titles = ("(a) Semantic cells", "(b) Recorded receiving time")
    for axis, metric, title in zip(axes, ("cells", "time"), titles):
        values = [row[metric] for rows in groups.values() for row in rows]
        span=max(values)-min(values)
        low=min(1,min(values))-max(.025,span*.04)
        high=max(1,max(values))+max(.035,span*.05)
        medians={}
        for stage in ("repair","union"):
            rows=groups[stage]
            frequencies=Counter(row[metric] for row in rows)
            xs=[low]; ys=[0]; total=0
            for value,count in sorted(frequencies.items()):
                total += count
                xs.append(value); ys.append(total/len(rows))
            xs.append(high); ys.append(1)
            axis.step(xs,ys,where="post",color=colors[stage],lw=1.25,
                      linestyle=lines[stage],zorder=3)
            medians[stage]=statistics.median(row[metric] for row in rows)
            axis.plot([medians[stage]],[.5],marker="o",markersize=4.2,
                      markerfacecolor="white" if stage=="repair" else colors[stage],
                      markeredgecolor=colors[stage],markeredgewidth=.9,zorder=4)
        axis.axvline(1,color=style.INK,lw=.8,linestyle=(0,(2,2)),zorder=2)
        axis.set_xlim(low,high); axis.set_ylim(0,1.01)
        axis.set_yticks([0,.25,.5,.75,1],["0","25","50","75","100"])
        if metric=="cells":
            axis.set_xticks([1,1.25,1.5,1.75,2,2.25],["1","1.25","1.5","1.75","2","2.25"])
        else:
            axis.xaxis.set_major_locator(MaxNLocator(nbins=5,min_n_ticks=4))
        axis.set_title(title,fontsize=9.7,pad=7)
        axis.set_xlabel("point-local / support-keyed",fontsize=8.8,labelpad=5)
        axis.grid(axis="y",color=style.RULE,lw=.5)
        axis.set_axisbelow(True)
    axes[0].set_ylabel("Requests (%)",fontsize=9.0,labelpad=4)
    handles=[Line2D([],[],color=colors[s],lw=1.25,linestyle=lines[s],label=f"{s.capitalize()} (739)")
             for s in ("repair","union")]
    fig.legend(handles=handles,loc="upper center",bbox_to_anchor=(.53,.995),ncol=2,
               frameon=False,fontsize=8.8,handlelength=2.0,columnspacing=1.8)
    style.save_figure(fig, output, name)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root",type=Path,required=True)
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    root=args.project_root.resolve(); args.output.mkdir(parents=True,exist_ok=True)
    helper=root/"artifact/figures/figure_style.py"
    if not helper.exists(): helper=root/"artifact/figures/figure_style.py"
    spec=importlib.util.spec_from_file_location("figure_style",helper)
    style=importlib.util.module_from_spec(spec);spec.loader.exec_module(style);style.style()
    groups=inputs(root,args.input)
    plot(groups,args.output,style)

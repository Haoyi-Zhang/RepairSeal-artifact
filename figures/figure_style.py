"""Render matched demand costs and an exact worked support-cache example.

Measured coordinates come only from the frozen demand study. The mechanism
example is explicitly illustrative and exhaustively checked by the small
mathematical model below; it is not an additional benchmark observation.
Existing figure generators and outputs are not modified.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Rectangle
from matplotlib.ticker import FixedLocator, FuncFormatter, LogLocator, NullFormatter
from matplotlib.text import Text


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data/unsigned-demand"
DEFAULT_OUTPUT = ROOT.parent / "paper/figures"
INK, BLUE, GRAY, RULE, PALE = "#192b36", "#24596e", "#66747c", "#cbd3d7", "#eef3f5"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    def object_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate figure-data key")
            result[key] = value
        return result
    def nonfinite(_value):
        raise ValueError("nonfinite figure data")
    return json.loads(path.read_text(), object_pairs_hook=object_pairs, parse_constant=nonfinite)


def frozen_records(directory):
    status, summary = load(directory / "status.json"), load(directory / "summary.json")
    if status.get("outcome") != "PASS" or summary.get("outcome") != "PASS":
        raise ValueError("a complete passing demand study is required")
    if status["summary_sha256"] != sha(directory / "summary.json"):
        raise ValueError("demand summary binding")
    for filename, expected in summary["records"].items():
        if sha(directory / filename) != expected:
            raise ValueError("demand record binding: " + filename)
    records = load(directory / "decisions.json")
    if len({row["id"] for row in records}) != len(records):
        raise ValueError("duplicate scientific request")
    for row in records:
        values = [row["full_cells"], *(row["cells"][name] for name in ("pruned", "projected_live", "demand"))]
        if any(type(value) is not int or value <= 0 for value in values):
            raise ValueError("nonpositive or untyped cell count")
        if values != sorted(values, reverse=True):
            raise ValueError("cell-order invariant")
        if row["full_cells"] != row["full_nodes"] * row["input_points"] or row["cells"]["pruned"] != row["live_nodes"] * row["input_points"]:
            raise ValueError("full-product count invariant")
    groups = {name: [row for row in records if row["corpus"].startswith(name)] for name in ("core", "grammar")}
    for name, rows in groups.items():
        expected = summary["corpora"][name]
        if len(rows) != expected["requests"] or sum(row["full_cells"] for row in rows) != expected["full_cells"]:
            raise ValueError("population or full-cell summary mismatch")
        for mode in ("pruned", "projected_live", "demand"):
            if sum(row["cells"][mode] for row in rows) != expected["cells"][mode]:
                raise ValueError("direct-cell summary mismatch")
    if sum(map(len, groups.values())) != len(records):
        raise ValueError("unclassified scientific requests")
    return groups, summary


def publication_font_family():
    """Use the manuscript's Times New Roman face for diagrams; font binaries are not distributed.

    Liberation Serif is metric-compatible with Times New Roman and is the first fallback.
    """
    for candidate in ("Times New Roman", "Liberation Serif", "DejaVu Serif"):
        try:
            path = font_manager.findfont(candidate, fallback_to_default=False)
        except ValueError:
            continue
        return font_manager.FontProperties(fname=path).get_name()
    return "DejaVu Serif"


def style():
    family = publication_font_family()
    plt.rcParams.update({"font.family": "serif", "font.serif": [family], "font.size": 9.7,
        "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "path",
        "svg.hashsalt": "repairseal-tosem-v2",
        "mathtext.fontset": "stix", "axes.unicode_minus": False,
        "axes.linewidth": .7, "axes.edgecolor": GRAY, "axes.labelcolor": INK,
        "text.color": INK, "xtick.color": GRAY, "ytick.color": GRAY,
        "xtick.labelsize": 9, "ytick.labelsize": 9, "axes.labelsize": 10,
        "legend.fontsize": 9.5, "axes.spines.top": False, "axes.spines.right": False,
        "savefig.facecolor": "white", "figure.facecolor": "white"})


def save_figure(figure, output, name):
    output.mkdir(parents=True, exist_ok=True)
    figure.canvas.draw()
    renderer, bounds = figure.canvas.get_renderer(), figure.bbox
    outside_ticks = set()
    for axis in figure.axes:
        for coordinate_axis in (axis.xaxis, axis.yaxis):
            lower, upper = sorted(coordinate_axis.get_view_interval())
            for tick in (*coordinate_axis.get_major_ticks(), *coordinate_axis.get_minor_ticks()):
                if not lower <= tick.get_loc() <= upper:
                    outside_ticks.update((tick.label1, tick.label2))
    for artist in figure.findobj(Text):
        if artist in outside_ticks or not artist.get_visible() or not artist.get_text().strip():
            continue
        box = artist.get_window_extent(renderer)
        if (box.x0 < bounds.x0 - 1 or box.y0 < bounds.y0 - 1 or
                box.x1 > bounds.x1 + 1 or box.y1 > bounds.y1 + 1):
            raise ValueError(name + ": clipped text: " + artist.get_text())
    figure.savefig(output / (name + ".pdf"), metadata={"Creator": "RepairSeal figure_style.py",
        "CreationDate": None, "ModDate": None, "Producer": None})
    figure.savefig(output / (name + ".svg"), metadata={"Date": None,
        "Creator": "RepairSeal figure_style.py"})
    plt.close(figure)


def compact_number(value, _position):
    if value >= 1000000: return f"{value / 1000000:g}M"
    if value >= 1000: return f"{value / 1000:g}k"
    return f"{value:g}"


def demand_work(groups, output):
    figure, axes = plt.subplots(1, 2, figsize=(7.05, 3.35))
    figure.subplots_adjust(left=.09, right=.985, bottom=.215, top=.80, wspace=.26)
    series = (("pruned", "s", GRAY, "Live-node", "none"),
              ("projected_live", "^", BLUE, "Projected live", "none"),
              ("demand", "o", INK, "Demand", INK))
    for axis, (name, rows) in zip(axes, groups.items()):
        full = [row["full_cells"] for row in rows]
        for mode, marker, color, _label, face in series:
            axis.scatter(full, [row["cells"][mode] for row in rows], marker=marker,
                         s=15 if mode != "demand" else 12, facecolors=face,
                         edgecolors=color, linewidths=.6, alpha=.45, zorder=3)
        minimum, maximum = min(full), max(full)
        axis.set_xscale("log"); axis.set_yscale("log")
        axis.set_xlim(minimum / 1.10, maximum * 1.12)
        ymin = min(row["cells"]["demand"] for row in rows)
        axis.set_ylim(ymin / 1.35, maximum * 1.35)
        axis.plot([minimum / 1.10, maximum * 1.12], [minimum / 1.10, maximum * 1.12],
                  color=GRAY, lw=.85, linestyle=(0, (3, 2)), zorder=2)
        axis.set_title(("(a) Core" if name == "core" else "(b) Grammar") +
                       f"  ({len(rows)} requests)", fontsize=10.6, pad=9)
        axis.set_xlabel("Full-vector cells", labelpad=5)
        axis.grid(axis="y", which="major", color=RULE, linewidth=.6, zorder=0)
        axis.set_axisbelow(True)
        axis.xaxis.set_major_formatter(FuncFormatter(compact_number))
        axis.yaxis.set_major_formatter(FuncFormatter(compact_number))
        axis.xaxis.set_minor_formatter(NullFormatter()); axis.yaxis.set_minor_formatter(NullFormatter())
        axis.tick_params(which="minor", length=2, width=.45)
        if name == "core":
            axis.xaxis.set_major_locator(FixedLocator([2000, 3000, 4000]))
            axis.xaxis.set_minor_locator(FixedLocator([]))
        else:
            axis.xaxis.set_major_locator(LogLocator(base=10, numticks=4))
        axis.yaxis.set_major_locator(LogLocator(base=10, numticks=6))
    axes[0].set_ylabel("Direct semantic cells", labelpad=5)
    handles = [Line2D([], [], color=GRAY, lw=.85, linestyle=(0, (3, 2)), label="Full (equal cells)")]
    handles.extend(Line2D([], [], marker=marker, linestyle="none", markerfacecolor=face,
                          markeredgecolor=color, markeredgewidth=.7, markersize=4.2,
                          label=label_) for _mode, marker, color, label_, face in series)
    figure.legend(handles=handles, loc="upper center", bbox_to_anchor=(.52, .995),
                  ncol=4, frameon=False, handlelength=1.4, columnspacing=1.4, handletextpad=.55)
    figure.text(.5, .045, "One mark per evaluator and request; coincident marks overlap. Both axes are logarithmic.",
                ha="center", va="center", fontsize=9.5)
    save_figure(figure, output, "demand-work")


def worked_example():
    """Compute the diagram's values rather than hand-fill its result table."""
    axes = ((0, 1), (0, 1), (0, 1), (5, 9))
    points = list(itertools.product(*axes))
    cache = {"g": {}, "e": {}, "repair": {}, "h": {}}
    def g(x):
        cache["g"].setdefault((x,), x != 0)
        return cache["g"][(x,)]
    def e(x, y):
        cache["e"].setdefault((x, y), x == y)
        return cache["e"][(x, y)]
    def repair(x, y):
        if (x, y) not in cache["repair"]:
            cache["repair"][(x, y)] = not g(x) or e(x, y)
        return cache["repair"][(x, y)]
    for x, y in itertools.product(*axes[:2]):
        if not repair(x, y):
            first_failure = (x, y)
            break
    candidates = []
    for x, y, z in itertools.product(*axes[:3]):
        if repair(x, y):
            continue
        cache["h"].setdefault((z,), z == 0)
        trace = ((0, int(cache["h"][(z,)])),)
        candidates.append((trace, (x, y, z, axes[3][0])))
    witness = min(candidates)
    direct = min((((0, int(z == 0)),), (x, y, z, t)) for x, y, z, t in points
                 if not ((x == 0) or (x == y)))
    if witness != direct or first_failure != (1, 0):
        raise ValueError("worked example diagnostic")
    if set(cache["e"]) != {(1, 0), (1, 1)}:
        raise ValueError("worked example short circuit")
    return {"axes": [list(axis) for axis in axes], "points": len(points),
            "first_failure": list(first_failure), "witness": [list(map(list, witness[0])), list(witness[1])],
            "cache": {name: [{"key": list(key), "value": value} for key, value in values.items()]
                      for name, values in cache.items()},
            "diagnostic_candidates": [{"trace": [list(event) for event in trace], "input": list(point)}
                                      for trace, point in sorted(candidates, key=lambda item: item[1])],
            "description": "Illustrative unsigned Cartesian case: original=reference=y, candidate=x, selector=(x!=0); candidate first branches on z==0 without changing its returned value. t is wholly unused."}


class Plate:
    def __init__(self, width=507.6, height=370):
        self.figure = plt.figure(figsize=(width / 72, height / 72))
        self.axis = self.figure.add_axes([0, 0, 1, 1], xlim=(0, width), ylim=(0, height))
        self.axis.set_axis_off()

    def text(self, x, y, value, size=9.5, *, ha="center", color=INK, weight="normal", **kwargs):
        return self.axis.text(x, y, value, ha=ha, va="center", fontsize=size,
                              color=color, weight=weight, linespacing=1.13, zorder=4, **kwargs)

    def line(self, x0, y0, x1, y1, color=RULE, width=.7, dashed=False):
        self.axis.plot([x0, x1], [y0, y1], color=color, linewidth=width,
                       linestyle=(0, (3, 2)) if dashed else "-", zorder=1)

    def rect(self, x, y, width, height, face="white", edge=RULE, dashed=False):
        self.axis.add_patch(Rectangle((x, y), width, height, facecolor=face,
                                     edgecolor=edge, linewidth=.8,
                                     linestyle=(0, (3, 2)) if dashed else "-", zorder=2))

    def node(self, x, y, width, height, value, inactive=False, size=9.5):
        self.rect(x - width / 2, y - height / 2, width, height,
                  face="white" if inactive else PALE, edge=GRAY if inactive else INK, dashed=inactive)
        self.text(x, y, value, size=size, color=GRAY if inactive else INK)

    def arrow(self, *points, inactive=False, color=INK):
        for start, end in zip(points[:-2], points[1:-1]):
            self.line(*start, *end, color=color, width=.8, dashed=inactive)
        self.axis.add_patch(FancyArrowPatch(points[-2], points[-1], arrowstyle="-|>",
            mutation_scale=7, shrinkA=0, shrinkB=0, linewidth=.8, color=color,
            linestyle=(0, (3, 2)) if inactive else "-", zorder=1))


def support_overview(output):
    example = worked_example()
    plate = Plate()
    plate.text(253.8, 356, r"Worked example:  $P=T=y$,  $Q=x$,  $R=(x\ne0)$", size=11)
    plate.text(253.8, 338, r"$D=\{0,1\}_x\times\{0,1\}_y\times\{0,1\}_z\times\{5,9\}_t$  (16 inputs)", size=10.1)
    plate.text(9, 314, "(a) Shared truth terms", size=10.3, ha="left", weight="bold")
    plate.text(269, 314, "(b) Values keyed by global support", size=10.3, ha="left", weight="bold")
    plate.text(498, 301, "cache after diagnosis", size=9.0, ha="right", color=GRAY)

    # A real shared equality term feeds both obligations. The inactive
    # preservation dependencies are drawn but not demanded in this case.
    plate.node(40, 289, 24, 18, r"$x$")
    plate.node(179, 289, 24, 18, r"$y$")
    plate.node(40, 253, 72, 24, r"$g=(x\ne0)$")
    plate.node(179, 253, 78, 24, r"$e=(x=y)$")
    plate.node(40, 216, 42, 20, r"$\neg g$")
    plate.node(105, 176, 100, 28, r"$O_R=\neg g\vee e$")
    plate.node(218, 176, 90, 28, r"$O_P=g\vee e$", inactive=True)
    plate.arrow((40, 280), (40, 265))
    plate.arrow((50, 280), (146, 265))
    plate.arrow((179, 280), (179, 265))
    plate.arrow((40, 241), (40, 226))
    plate.arrow((49, 206), (79, 190))
    plate.arrow((164, 241), (118, 190))
    plate.arrow((195, 241), (214, 190), inactive=True, color=GRAY)
    plate.arrow((76, 253), (109, 253), (109, 206), (195, 190), inactive=True, color=GRAY)
    plate.text(204, 151, "dashed: not requested", size=9.1, color=GRAY)

    # Table entries are read from the mathematical memo execution above.
    cache = {name: {tuple(item["key"]): item["value"] for item in items}
             for name, items in example["cache"].items()}
    truth = lambda value: "T" if value else "F"
    plate.text(273, 289, r"$g$: key $x$", ha="left")
    plate.text(397, 289, "0", size=9.5); plate.text(467, 289, "1", size=9.5)
    plate.line(271, 280, 498, 280)
    plate.text(273, 269, "cached value", ha="left")
    plate.text(397, 269, truth(cache["g"][(0,)]))
    plate.text(467, 269, truth(cache["g"][(1,)]))
    plate.line(271, 258, 498, 258)

    columns = (358, 399, 440, 481)
    xy = ((0, 0), (0, 1), (1, 0), (1, 1))
    plate.text(273, 239, "key (x, y)", ha="left")
    for x, key in zip(columns, xy):
        plate.text(x, 239, f"{key[0]},{key[1]}", size=9.3)
    plate.line(271, 229, 499, 229)
    plate.text(273, 216, r"$e[x,y]$", ha="left")
    plate.text(273, 193, r"$O_R[x,y]$", ha="left")
    for x, key in zip(columns, xy):
        value = cache["e"].get(key)
        plate.text(x, 216, "-" if value is None else truth(value), color=GRAY if value is None else INK)
        plate.text(x, 193, truth(cache["repair"][key]), weight="bold" if not cache["repair"][key] else "normal")
    plate.line(271, 181, 499, 181)
    plate.text(384, 165, r"$x=0$: $\neg g$ is true; $e$ is not requested.", size=9.4)
    plate.text(384, 150, "The same keys serve every z and t.", size=9.4)

    plate.line(9, 137, 499, 137)
    plate.text(9, 120, "(c) Obligation priority", size=10.3, ha="left", weight="bold")
    plate.text(269, 120, "(d) Diagnose only the first failure", size=10.3, ha="left", weight="bold")
    plate.text(12, 99, "1   defined", ha="left")
    plate.text(125, 99, "true", ha="left")
    plate.text(12, 78, "2   repair", ha="left")
    plate.text(125, 78, "false at (x,y)=(1,0)", ha="left")
    plate.text(12, 57, "3   preserve", ha="left", color=GRAY)
    plate.text(125, 57, "not requested", ha="left", color=GRAY)
    plate.text(11, 36, "If all hold: ACCEPT; no trace queries.", ha="left", size=9.2)

    plate.text(280, 99, "z")
    plate.text(344, 99, "trace")
    plate.text(443, 99, "least full input")
    plate.line(271, 89, 499, 89)
    for y, row in zip((76, 54), example["diagnostic_candidates"]):
        selected = row["input"] == example["witness"][1]
        if selected:
            plate.rect(271, y - 10, 228, 20, face=PALE, edge="none")
        plate.text(280, y, str(row["input"][2]), weight="bold" if selected else "normal")
        plate.text(344, y, "[(0," + str(row["trace"][0][1]) + ")]", weight="bold" if selected else "normal")
        plate.text(443, y, "(" + ",".join(map(str, row["input"])) + ")", weight="bold" if selected else "normal")
    plate.text(384, 34, r"Event 0: $h(z)=(z=0)$; trace precedes input.", size=9.2)
    plate.text(253.8, 13, "Cartesian: fill omitted t with 5. For a listed point set, keep the least actual representative.", size=9.0)
    save_figure(plate.figure, output, "support-demand-overview")
    return example


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    groups, summary = frozen_records(args.input)
    style()
    demand_work(groups, args.output)
    example = support_overview(args.output)
    files = [name + extension for name in ("demand-work", "support-demand-overview") for extension in (".pdf", ".svg")]
    manifest = {"schema": "repairseal-round3-figures-v1", "script_sha256": sha(Path(__file__)),
                "study_summary_sha256": sha(args.input / "summary.json"),
                "study_decisions_sha256": summary["records"]["decisions.json"],
                "populations": {name: len(rows) for name, rows in groups.items()},
                "cost_totals": {name: summary["corpora"][name]["cells"] for name in groups},
                "plot_contract": "one unjittered mark per request per direct evaluator; full-vector counts on x; no elapsed-time measurement",
                "worked_example": example, "outputs": {name: sha(args.output / name) for name in files}}
    destination = Path(__file__).with_name("round3-figure-manifest.json")
    destination.write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"manifest": str(destination), "outputs": [str(args.output / name) for name in files]}, indent=2))


if __name__ == "__main__":
    main()

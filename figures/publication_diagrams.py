"""Round-4 publication diagrams for the RepairSeal manuscript.

Every label and relation is generated as vector content.  The functions accept
an optional variant number so the iteration audit can regenerate reviewed
candidates without touching retained evidence records.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Polygon, Rectangle
from matplotlib.lines import Line2D


INK = "#192b36"
BLUE = "#24596e"
GRAY = "#66747c"
RULE = "#cbd3d7"
PALE = "#eef3f5"
PALE2 = "#f7f9fa"
RUST = "#8b4a3a"


def _rbox(p, x, y, w, h, *, face="white", edge=RULE, radius=5, lw=.8, dashed=False):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.0,rounding_size={radius}",
        facecolor=face, edgecolor=edge, linewidth=lw,
        linestyle=(0, (3, 2)) if dashed else "-", zorder=2,
    )
    p.axis.add_patch(patch)
    return patch


def _document(p, x, y, w, h, label, *, edge=GRAY, face="white", size=8.8, dashed=False):
    fold = min(8, w * .22, h * .28)
    points = [(x, y), (x+w, y), (x+w, y+h-fold), (x+w-fold, y+h), (x, y+h)]
    p.axis.add_patch(Polygon(points, closed=True, facecolor=face, edgecolor=edge,
                             linewidth=.8, linestyle=(0, (3, 2)) if dashed else "-", zorder=2))
    p.line(x+w-fold, y+h, x+w-fold, y+h-fold, color=edge, width=.65)
    p.line(x+w-fold, y+h-fold, x+w, y+h-fold, color=edge, width=.65)
    p.text(x+w/2, y+h/2-1, label, size=size, color=edge)


def _arrow(p, start, end, *, color=INK, dashed=False, label=None, label_xy=None):
    p.arrow(start, end, color=color, inactive=dashed)
    if label:
        lx, ly = label_xy if label_xy else ((start[0]+end[0])/2, (start[1]+end[1])/2+7)
        p.text(lx, ly, label, size=8.3, color=color,
               bbox={"facecolor": "white", "edgecolor": "none", "pad": .8})


def _lane_label(p, x, y, number, title, subtitle=None):
    p.axis.add_patch(Circle((x, y), 8.5, facecolor=INK, edgecolor=INK, linewidth=.7, zorder=3))
    p.text(x, y, str(number), size=8.4, color="white", weight="bold")
    p.text(x+14, y+5 if subtitle else y, title, size=9.3, weight="bold", ha="left")
    if subtitle:
        p.text(x+14, y-8, subtitle, size=8.1, color=GRAY, ha="left")


def overview(style, output: Path, variant: int = 24, name: str = "repairseal-overview"):
    """Three evidence roles under one receiver-owned request.

    Variants 1--8 retain a comparison-table construction, 9--16 use a shared
    spine, and 17--24 use the selected worked-example lane construction.
    """
    variant = max(1, min(24, int(variant)))
    if variant <= 8:
        p = style.Plate(width=428.42, height=292)
        p.text(214.21, 280, "Receiver-owned request", size=10.7, weight="bold")
        p.text(214.21, 264, r"$P,Q,T,R,D$; source semantics; diagnostic order; required result", size=9.1)
        p.rect(5, 224, 418.42, 26, face=PALE, edge=BLUE)
        p.text(214.21, 237, r"Reconstruct source and obligations $O_0,O_1,O_2$", size=9.5, weight="bold")
        headers = ("Evidence role", "Receiver work", "Result")
        for x, text in zip((10, 154, 318), headers):
            p.text(x, 207, text, size=9.2, weight="bold", ha="left")
        p.line(6, 197, 422, 197)
        rows = [
            (166, "Complete rows", "Recompute and compare every cell", "complete decision + record"),
            (116, "Supplied failure", "Check one declared point", "confirmed refutation"),
            (66, "Accepted history", "Check support coverage", "fresh result or fallback"),
        ]
        for y, a, b, c in rows:
            p.text(10, y, a, size=9.1, weight="bold", ha="left")
            p.text(154, y, b, size=8.9, ha="left")
            p.text(318, y, c, size=8.9, ha="left")
            p.line(6, y-24, 422, y-24)
        p.text(214.21, 18, "Invalid or interrupted work yields no semantic result.", size=8.8, color=GRAY)
    elif variant <= 16:
        p = style.Plate(width=428.42, height=300)
        _rbox(p, 7, 247, 414.42, 46, face=PALE, edge=BLUE)
        p.text(18, 278, "Receiver-owned task", size=10.0, weight="bold", ha="left")
        p.text(18, 260, r"Same $P,Q,T,R,D$, source interpretation and diagnostic order", size=9.0, ha="left")
        p.arrow((214, 247), (214, 233))
        _rbox(p, 95, 205, 238, 28, face="white", edge=INK)
        p.text(214, 219, r"Reconstruct $O_0$ definedness, $O_1$ repair, $O_2$ preservation", size=9.0, weight="bold")
        yvals = (158, 103, 48)
        labels = ((1, "Complete record"), (2, "Supplied violation"), (3, "Accepted history"))
        for y, (n, label) in zip(yvals, labels):
            _lane_label(p, 18, y, n, label)
            p.line(104, y, 410, y, color=RULE, width=.7)
        _document(p, 112, 143, 55, 30, "full rows", edge=GRAY)
        _rbox(p, 185, 140, 112, 36, face=PALE2, edge=BLUE)
        p.text(241, 158, "recompute + compare", size=8.6)
        _arrow(p, (167, 158), (185, 158))
        _rbox(p, 318, 140, 94, 36, face="white", edge=BLUE)
        p.text(365, 158, "complete result", size=8.6, weight="bold")
        _arrow(p, (297, 158), (318, 158))
        _document(p, 112, 88, 55, 30, r"$(j,u,\tau)$", edge=GRAY)
        _rbox(p, 185, 85, 112, 36, face=PALE2, edge=BLUE)
        p.text(241, 103, "verify named failure", size=8.6)
        _arrow(p, (167, 103), (185, 103))
        _rbox(p, 318, 85, 94, 36, face="white", edge=RUST)
        p.text(365, 103, "REFUTED at u", size=8.6, weight="bold", color=RUST)
        _arrow(p, (297, 103), (318, 103), color=RUST)
        _document(p, 112, 33, 55, 30, "ACCEPT D", edge=BLUE)
        _rbox(p, 185, 30, 112, 36, face=PALE2, edge=BLUE)
        p.text(241, 48, "coverage for E", size=8.6)
        _arrow(p, (167, 48), (185, 48))
        _rbox(p, 318, 30, 94, 36, face="white", edge=BLUE)
        p.text(365, 52, "covered: ACCEPT E", size=8.2, weight="bold")
        p.text(365, 39, "else: ordinary check", size=7.9, color=GRAY)
        _arrow(p, (297, 48), (318, 48))
        p.text(214, 10, "Invalid or interrupted work: no semantic result", size=8.5, color=GRAY)
    else:
        p = style.Plate(width=428.42, height=306)
        # Worked-example request: enough detail to make the lanes concrete without
        # duplicating the running-example figure.
        _rbox(p, 6, 259, 416.42, 41, face=PALE, edge=BLUE, radius=6)
        p.text(17, 286, "Running request", size=9.5, weight="bold", ha="left")
        p.text(113, 286, r"CEIL_DIV scalar model:  $|D|=42$  (12 repair, 30 preserve),  $n>0$", size=9.0, ha="left")
        p.text(17, 270, r"Receiver owns $P,Q,T,R,D$, source semantics, prior state and the required result", size=8.8, ha="left")
        p.arrow((214.21, 259), (214.21, 246))
        _rbox(p, 92, 218, 244.42, 28, face="white", edge=INK, radius=5)
        p.text(214.21, 232, r"Reconstruct $O_0$ definedness, $O_1$ repair, $O_2$ preservation", size=9.0, weight="bold")

        # Lane 1: two matched complete paths share a result but not a record.
        _lane_label(p, 18, 177, 1, "Complete decision", "same output obligation on D")
        _document(p, 111, 179, 48, 26, "full rows", edge=GRAY)
        _rbox(p, 171, 177, 103, 30, face=PALE2, edge=GRAY, radius=4)
        p.text(222.5, 192, r"recompute $N\times M$", size=8.4)
        p.text(222.5, 181, "compare every cell", size=7.9, color=GRAY)
        _arrow(p, (159, 192), (171, 192), color=GRAY)
        p.text(136, 164, "or", size=7.8, color=GRAY)
        _document(p, 111, 137, 48, 26, "no packet", edge=BLUE)
        _rbox(p, 171, 135, 103, 30, face=PALE, edge=BLUE, radius=4)
        p.text(222.5, 150, "support-keyed demand", size=8.2)
        _arrow(p, (159, 150), (171, 150), color=BLUE)
        # Bracket two complete paths into the same semantic result.
        p.line(274, 192, 288, 192, color=GRAY, width=.8)
        p.line(274, 150, 288, 150, color=BLUE, width=.8)
        p.line(288, 150, 288, 192, color=INK, width=.8)
        _arrow(p, (288, 171), (304, 171))
        _rbox(p, 304, 151, 112, 40, face="white", edge=BLUE, radius=5)
        p.text(360, 177, "ACCEPT or least", size=8.4, weight="bold")
        p.text(360, 164, "canonical REFUTED", size=8.4, weight="bold")
        p.text(360, 146, "full path alone returns the record", size=7.4, color=GRAY)

        # Lane 2: actual boundary input from the running example.
        p.line(8, 126, 420, 126, color=RULE, width=.65)
        _lane_label(p, 18, 104, 2, "Supplied violation", r"boundary input $u^*=(2,U)$")
        _document(p, 126, 89, 58, 30, r"$(O_1,u^*,\tau)$", edge=GRAY)
        _arrow(p, (184, 104), (205, 104), color=GRAY)
        _rbox(p, 205, 87, 96, 34, face=PALE2, edge=BLUE, radius=4)
        p.text(253, 108, r"evaluate $O_1(u^*)$", size=8.2)
        p.text(253, 96, "recompute trace", size=7.8, color=GRAY)
        _arrow(p, (301, 104), (321, 104), color=RUST)
        _rbox(p, 321, 87, 95, 34, face="white", edge=RUST, radius=5)
        p.text(368.5, 108, r"REFUTED at $u^*$", size=8.3, weight="bold", color=RUST)
        p.text(368.5, 96, "does not decide all D", size=7.6, color=GRAY)

        # Lane 3: accepted history is receiver-owned and branches neutrally.
        p.line(8, 77, 420, 77, color=RULE, width=.65)
        _lane_label(p, 18, 53, 3, "Accepted history", "receiver-owned ACCEPT on D; later E")
        _document(p, 141, 38, 52, 30, "receipt D", edge=BLUE)
        _arrow(p, (193, 53), (214, 53), color=BLUE)
        _rbox(p, 214, 36, 92, 34, face=PALE, edge=BLUE, radius=4)
        p.text(260, 57, "support coverage", size=8.2)
        p.text(260, 45, r"for every $O_j$", size=7.8, color=GRAY)
        _arrow(p, (306, 58), (327, 64), color=BLUE, label="yes", label_xy=(317, 72))
        _arrow(p, (306, 48), (327, 39), color=GRAY, label="no", label_xy=(318, 34))
        _rbox(p, 327, 51, 89, 28, face="white", edge=BLUE, radius=5)
        p.text(371.5, 65, "fresh ACCEPT E", size=8.1, weight="bold")
        _rbox(p, 327, 18, 89, 28, face="white", edge=GRAY, radius=5)
        p.text(371.5, 32, "ordinary complete check", size=7.7, color=GRAY)
        p.text(214.21, 7, "invalid / interrupted  →  no semantic result", size=8.0, color=GRAY)
    style.save_figure(p.figure, output, name)


def _domain_data(root: Path):
    path = root / "artifact/data/domain-study/summary.json"
    data = json.loads(path.read_text())
    if data.get("outcome") != "PASS":
        raise ValueError("domain study is not complete")
    row = next(r for r in data["domains"] if r["name"] == "retained42")
    return row


def ceil_obligations(style, root: Path, output: Path, variant: int = 6, name: str = "ceil-obligations"):
    """Exact 42-point domain at its final .88-linewidth display size."""
    variant = max(1, min(6, int(variant)))
    row = _domain_data(root)
    ms, ns = row["axes"]["m"], row["axes"]["n"]
    U = (1 << 32) - 1
    repair = {(i, j) for i, m in enumerate(ms) for j, n in enumerate(ns) if m > U - (n - 1)}
    if len(ms) * len(ns) != 42 or len(repair) != 12:
        raise ValueError("running-domain count mismatch")

    width, height = 377.01, 186
    fig = plt.figure(figsize=(width/72, height/72))
    # Explicit margins preserve actual-size typography and room for the semantic legend.
    ax = fig.add_axes([.105, .255, .875, .61])
    for i, _m in enumerate(ms):
        for j, _n in enumerate(ns):
            bad = (i, j) in repair
            if variant >= 2:
                ax.add_patch(Rectangle((j-.47, i-.47), .94, .94,
                    facecolor=PALE if bad else "white", edgecolor=RULE, linewidth=.55,
                    hatch="////" if bad and variant >= 5 else None))
            marker = "x" if bad else "o"
            ax.plot(j, i, marker=marker, markersize=6.0 if variant < 4 else 6.5,
                    markeredgewidth=1.15, markerfacecolor="white", color=BLUE, linestyle="none")
    label = lambda x: "U" if x == U else ("U - 1" if x == U-1 else str(x))
    ax.set_xticks(range(len(ns)), [label(n) for n in ns])
    ax.set_yticks(range(len(ms)), [label(m) for m in ms])
    ax.set_xlim(-.5, len(ns)-.5); ax.set_ylim(len(ms)-.5, -.5)
    ax.xaxis.tick_top(); ax.xaxis.set_label_position("top")
    xlabel = r"Divisor $n$" if variant < 3 else r"Divisor $n$  (caller premise: $n>0$)"
    ax.set_xlabel(xlabel, labelpad=6, fontsize=9.2)
    ax.set_ylabel(r"Numerator $m$", fontsize=9.2, labelpad=6)
    ax.tick_params(length=0, pad=3, labelsize=8.5)
    for spine in ax.spines.values(): spine.set_visible(False)
    if variant >= 4:
        fig.text(.98, .94, r"$U=2^{32}-1$", ha="right", va="center", fontsize=8.2, color=GRAY)
        fig.text(.105, .205, "Source-linked unsigned scalar model", ha="left", va="center", fontsize=8.1, color=GRAY)
    handles = [
        Line2D([], [], marker="x", color=BLUE, linestyle="none", markersize=6.2,
               markeredgewidth=1.2, label=r"Repair: compare $Q$ with $T$ (12)"),
        Line2D([], [], marker="o", markerfacecolor="white", color=BLUE, linestyle="none",
               markersize=6.2, markeredgewidth=1.2, label=r"Preserve: compare $Q$ with $P$ (30)"),
        Line2D([], [], color=INK, linewidth=0, marker="$O_0$", markersize=10,
               label=r"$Q$ defined at all 42 points"),
    ]
    ncol = 2 if variant < 6 else 3
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.54, .02), ncol=ncol,
               frameon=False, fontsize=8.0, handlelength=1.0, columnspacing=1.15, handletextpad=.45)
    style.save_figure(fig, output, name)


def _support_example():
    axes = ((0, 1), (0, 1), (0, 1), (5, 9))
    points = list(itertools.product(*axes))
    g = {(x,): x != 0 for x in axes[0]}
    e = {(1, y): 1 == y for y in axes[1]}
    o1 = {(x, y): ((not g[(x,)]) or (x == y)) for x, y in itertools.product(*axes[:2])}
    failed = next(k for k in itertools.product(*axes[:2]) if not o1[k])
    candidates = []
    for z in axes[2]:
        trace = ((0, int(z == 0)),)
        candidates.append((trace, (failed[0], failed[1], z, axes[3][0])))
    witness = min(candidates)
    return {"axes": axes, "points": points, "g": g, "e": e, "o1": o1,
            "failed": failed, "candidates": candidates, "witness": witness}


def support_demand(style, output: Path, variant: int = 12, name: str = "support-demand-overview"):
    """Support projection, priority and diagnostic selection at exact linewidth."""
    variant = max(1, min(12, int(variant)))
    ex = _support_example()
    if variant <= 4:
        # Four-panel candidate retained in the audit for comparison with the selected construction.
        p = style.Plate(width=428.42, height=306)
        p.text(214, 291, r"$P=T=y$, $Q=x$, $R=(x\ne0)$; 16 inputs", size=10.1)
        p.text(8, 270, "(a) Shared terms", size=9.7, ha="left", weight="bold")
        p.text(218, 270, "(b) Support-keyed values", size=9.7, ha="left", weight="bold")
        p.node(45, 232, 44, 22, r"$g(x)$")
        p.node(130, 232, 54, 22, r"$e(x,y)$")
        p.node(88, 190, 96, 27, r"$O_1=\neg g\vee e$")
        p.arrow((45, 221), (70, 204)); p.arrow((130, 221), (106, 204))
        p.text(8, 153, "(c) Priority", size=9.7, ha="left", weight="bold")
        p.text(18, 126, r"$O_0$: pass", size=9.1, ha="left")
        p.text(18, 104, r"$O_1$: fail at $(1,0)$", size=9.1, ha="left")
        p.text(18, 82, r"$O_2$: not requested", size=9.1, ha="left", color=GRAY)
        p.text(218, 153, "(d) Diagnostic", size=9.7, ha="left", weight="bold")
        p.text(230, 124, r"$z=0$: trace 1", size=9.0, ha="left")
        p.text(230, 101, r"$z=1$: trace 0  ← least", size=9.0, ha="left", weight="bold")
        p.text(214, 26, "Complete decision; no complete value table is materialized.", size=8.8, color=GRAY)
    elif variant <= 8:
        p = style.Plate(width=428.42, height=290)
        p.text(214, 278, r"16 inputs: $\{0,1\}_x\times\{0,1\}_y\times\{0,1\}_z\times\{5,9\}_t$", size=9.6)
        p.text(12, 254, "Support graph", size=9.5, weight="bold", ha="left")
        p.text(160, 254, "Memo keys", size=9.5, weight="bold", ha="left")
        p.text(300, 254, "Ordered decision", size=9.5, weight="bold", ha="left")
        # graph
        p.node(38, 220, 32, 20, r"$x$"); p.node(100, 220, 32, 20, r"$y$")
        p.node(38, 184, 68, 22, r"$g(x)$"); p.node(100, 184, 76, 22, r"$e(x,y)$")
        p.node(69, 144, 108, 26, r"$O_1=\neg g\vee e$")
        p.arrow((38, 210), (38, 195)); p.arrow((52, 210), (83, 195)); p.arrow((100, 210), (100, 195))
        p.arrow((38, 173), (52, 157)); p.arrow((100, 173), (86, 157))
        p.text(12, 119, r"supports: $\{x\}$ and $\{x,y\}$", size=8.5, ha="left", color=GRAY)
        # keys
        _rbox(p, 158, 188, 124, 52, face=PALE2, edge=RULE, radius=3)
        p.text(168, 226, r"$g[x]$", size=8.8, weight="bold", ha="left")
        p.text(168, 210, "0→F     1→T", size=8.7, ha="left")
        p.text(168, 195, "two keys serve all z,t", size=8.0, color=GRAY, ha="left")
        _rbox(p, 158, 126, 124, 52, face=PALE2, edge=RULE, radius=3)
        p.text(168, 164, r"$e[x,y]$ after short-circuit", size=8.4, weight="bold", ha="left")
        p.text(168, 148, "(1,0)→F   (1,1)→T", size=8.5, ha="left")
        p.text(168, 133, "x=0 does not request e", size=8.0, color=GRAY, ha="left")
        # priority
        y0 = 220
        for label, status, color in ((r"$O_0$", "pass", BLUE), (r"$O_1$", "fail at (1,0)", RUST), (r"$O_2$", "not requested", GRAY)):
            _rbox(p, 306, y0-12, 104, 24, face="white", edge=color, radius=3)
            p.text(318, y0, label, size=8.7, weight="bold", ha="left", color=color)
            p.text(402, y0, status, size=8.0, ha="right", color=color)
            y0 -= 36
        p.arrow((358, 136), (358, 118), color=RUST)
        p.text(358, 106, "diagnose this failure only", size=8.2, color=RUST)
        _rbox(p, 298, 51, 120, 42, face=PALE, edge=BLUE, radius=3)
        p.text(358, 78, r"trace 0, input $(1,0,1,5)$", size=8.1, weight="bold")
        p.text(358, 63, "least actual representative", size=7.8, color=GRAY)
        p.text(214, 22, "Complete decision without a complete materialized value record.", size=8.7, color=GRAY)
    else:
        p = style.Plate(width=428.42, height=282)
        p.text(8, 269, r"Worked request: $P=T=y$, $Q=x$, $R=(x\ne0)$", size=9.4, weight="bold", ha="left")
        p.text(420, 269, r"$D=\{0,1\}_x\times\{0,1\}_y\times\{0,1\}_z\times\{5,9\}_t$  (16)", size=8.7, ha="right")
        # panel titles and separators
        p.text(8, 246, "(a) Support follows dependence", size=9.2, weight="bold", ha="left")
        p.text(151, 246, "(b) Memo by projected key", size=9.2, weight="bold", ha="left")
        p.text(294, 246, "(c) Stop, then diagnose", size=9.2, weight="bold", ha="left")
        p.line(142, 36, 142, 238, color=RULE, width=.7)
        p.line(285, 36, 285, 238, color=RULE, width=.7)

        # (a) shared nodes with support labels.
        p.node(34, 211, 30, 19, r"$x$")
        p.node(103, 211, 30, 19, r"$y$")
        p.node(34, 174, 62, 22, r"$g=(x\ne0)$")
        p.node(103, 174, 68, 22, r"$e=(x=y)$")
        p.node(69, 128, 112, 26, r"$O_1=\neg g\vee e$")
        p.arrow((34, 201), (34, 185)); p.arrow((48, 201), (88, 185)); p.arrow((103, 201), (103, 185))
        p.arrow((34, 163), (52, 141)); p.arrow((103, 163), (86, 141))
        p.text(34, 190, r"$\{x\}$", size=7.6, color=GRAY)
        p.text(103, 190, r"$\{x,y\}$", size=7.6, color=GRAY)
        _rbox(p, 11, 72, 116, 32, face=PALE2, edge=GRAY, radius=3, dashed=True)
        p.text(69, 92, r"$O_2=g\vee e$", size=8.4, color=GRAY)
        p.text(69, 79, "not requested after O1 fails", size=7.4, color=GRAY)
        p.text(69, 48, "z and t are irrelevant to O1", size=8.0, color=GRAY)

        # (b) compact memo table.
        _rbox(p, 153, 177, 122, 54, face=PALE2, edge=RULE, radius=3)
        p.text(162, 217, r"$g[x]$", size=8.6, weight="bold", ha="left")
        p.text(266, 217, "2 keys", size=7.8, color=GRAY, ha="right")
        p.text(162, 197, "x", size=7.8, color=GRAY, ha="left")
        p.text(205, 197, "0", size=8.0); p.text(247, 197, "1", size=8.0)
        p.text(162, 184, "value", size=7.8, color=GRAY, ha="left")
        p.text(205, 184, "F", size=8.2); p.text(247, 184, "T", size=8.2)
        _rbox(p, 153, 103, 122, 62, face=PALE2, edge=RULE, radius=3)
        p.text(162, 151, r"$e[x,y]$", size=8.6, weight="bold", ha="left")
        p.text(266, 151, "2 demanded keys", size=7.6, color=GRAY, ha="right")
        p.text(162, 132, "key", size=7.8, color=GRAY, ha="left")
        p.text(205, 132, "(1,0)", size=7.8); p.text(249, 132, "(1,1)", size=7.8)
        p.text(162, 116, "value", size=7.8, color=GRAY, ha="left")
        p.text(205, 116, "F", size=8.2, weight="bold", color=RUST); p.text(249, 116, "T", size=8.2)
        p.text(214, 83, "same keys serve every z and t", size=8.0, color=GRAY)
        p.text(214, 62, "listed domains use actual points", size=8.0, color=GRAY)
        p.text(214, 49, "as representatives", size=8.0, color=GRAY)

        # (c) priority and only then trace selection.
        steps = [(217, r"$O_0$", "pass", BLUE), (183, r"$O_1$", "fail at (1,0)", RUST), (149, r"$O_2$", "not requested", GRAY)]
        for y, lab, status, color in steps:
            _rbox(p, 300, y-12, 118, 24, face="white", edge=color, radius=3,
                  dashed=(color == GRAY))
            p.text(310, y, lab, size=8.4, weight="bold", ha="left", color=color)
            p.text(409, y, status, size=7.7, ha="right", color=color)
        p.arrow((359, 137), (359, 121), color=RUST)
        p.text(359, 111, "diagnose O1 only", size=8.0, color=RUST, weight="bold")
        # two candidates; selected by trace then full input.
        rows = [(86, 0, 1, (1,0,0,5), False), (58, 1, 0, (1,0,1,5), True)]
        p.text(304, 96, "z", size=7.6, color=GRAY)
        p.text(338, 96, "trace", size=7.6, color=GRAY)
        p.text(393, 96, "full input", size=7.6, color=GRAY)
        for y, z, tr, u, selected in rows:
            if selected:
                _rbox(p, 297, y-11, 123, 22, face=PALE, edge=BLUE, radius=3)
            p.text(304, y, str(z), size=8.0, weight="bold" if selected else "normal")
            p.text(338, y, str(tr), size=8.0, weight="bold" if selected else "normal")
            p.text(393, y, "("+",".join(map(str,u))+")", size=7.7,
                   weight="bold" if selected else "normal")
        p.text(359, 34, "least (trace, input)", size=8.0, color=BLUE, weight="bold")
    style.save_figure(p.figure, output, name)
    return ex


def acceptance_transport(style, output: Path, variant: int = 12, name: str = "acceptance-transport"):
    """Coverage as a sufficient authorization rule, with neutral fallback."""
    variant = max(1, min(12, int(variant)))
    p = style.Plate(width=402.715, height=232)
    _rbox(p, 5, 198, 392.715, 29, face=PALE, edge=BLUE, radius=5)
    p.text(201.35, 215, r"Receiver-established ACCEPT on $D$", size=9.8, weight="bold")
    p.text(201.35, 204, "same sources, policy, semantics and identity", size=8.1, color=GRAY)
    p.text(8, 184, "(a) Different points, same relevant projection", size=8.9, weight="bold", ha="left")
    p.text(212, 184, "(b) Authorization for the new request E", size=8.9, weight="bold", ha="left")

    # Left: disjoint domains whose x projections coincide.
    xs = (62, 108, 154)
    yD = 91
    yE = (126, 146, 166)
    p.text(10, 91, r"$D$: $z=0$", size=8.1, ha="left")
    p.text(10, 166, r"$E$: $z\in\{1,2,3\}$", size=8.1, ha="left")
    for x in xs:
        p.axis.add_patch(Circle((x, yD), 4.3, facecolor=INK, edgecolor=INK, zorder=3))
        for y in yE:
            p.rect(x-4.4, y-4.4, 8.8, 8.8, face="white", edge=BLUE)
        p.arrow((x, 82), (x, 61), inactive=True, color=GRAY)
        p.rect(x-6.2, 43, 12.4, 12.4, face="white", edge=BLUE)
        p.axis.add_patch(Circle((x, 49.2), 3.0, facecolor=INK, edgecolor=INK, zorder=4))
    p.line(48, 80, 168, 80, color=RULE, width=.7)
    p.text(62, 33, "0", size=8.2); p.text(108, 33, "1", size=8.2); p.text(154, 33, "2", size=8.2)
    p.text(108, 17, r"$\pi_x(D)=\pi_x(E)=\{0,1,2\}$", size=8.7, weight="bold")
    p.text(108, 4, r"$D\cap E=\varnothing$", size=8.0, color=GRAY)

    # Right: sufficient rule, explicit no-conclusion branch.
    p.text(303, 162, r"supports $B_0,B_1,B_2$", size=8.4, color=GRAY)
    _rbox(p, 228, 123, 150, 31, face="white", edge=BLUE, radius=4)
    p.text(303, 142, r"for every $j$:  $\pi_{B_j}(E)\subseteq\pi_{B_j}(D)$", size=8.7, weight="bold")
    p.text(303, 129, "sufficient, not necessary", size=7.9, color=GRAY)
    # yes branch
    _arrow(p, (262, 123), (249, 103), color=BLUE, label="yes", label_xy=(250, 112))
    _rbox(p, 210, 65, 110, 38, face=PALE, edge=BLUE, radius=5)
    p.text(265, 90, r"fresh ACCEPT on $E$", size=8.7, weight="bold")
    p.text(265, 76, "0 new semantic cells", size=7.9, color=BLUE)
    # no branch: no conclusion, then ordinary check, neutral semantics.
    _arrow(p, (344, 123), (356, 103), color=GRAY, label="no", label_xy=(356, 112))
    _rbox(p, 318, 82, 79, 21, face="white", edge=GRAY, radius=4)
    p.text(357.5, 92.5, "no conclusion", size=7.8, color=GRAY)
    p.arrow((357.5, 82), (357.5, 69), color=GRAY)
    _rbox(p, 318, 25, 79, 44, face="white", edge=GRAY, radius=4)
    p.text(357.5, 57, "ordinary complete", size=7.4, color=GRAY)
    p.text(357.5, 46, r"check on $E$", size=7.4, color=GRAY)
    p.text(357.5, 34, "then ACCEPT / REFUTED", size=6.9, color=GRAY)
    p.text(257, 41, r"old packet remains bound to $D$", size=8.2, color=INK)
    p.text(257, 27, "no packet rebinding", size=7.8, color=GRAY)
    style.save_figure(p.figure, output, name)


def trust_boundary(style, output: Path, variant: int = 10, name: str = "trust-boundary"):
    """Matched replay/direct control with shared source interpretation."""
    variant = max(1, min(10, int(variant)))
    p = style.Plate(width=428.42, height=184)
    _rbox(p, 6, 145, 416.42, 34, face=PALE, edge=BLUE, radius=5)
    p.text(214.21, 167, "Receiver reconstructs the same request and source semantics", size=9.6, weight="bold")
    p.text(214.21, 154, "same obligations, domain and canonical diagnostic order", size=8.2, color=GRAY)
    # Shared interpretation fans out to the two matched paths.
    p.line(214.21, 145, 214.21, 137, color=INK, width=.8)
    p.line(108, 137, 320.42, 137, color=INK, width=.8)
    p.arrow((108, 137), (108, 126)); p.arrow((320.42, 137), (320.42, 126))

    p.text(108, 117, "Certificate replay", size=9.2, weight="bold")
    p.text(320.42, 117, "Certificate-free control", size=9.2, weight="bold")
    # Extra untrusted input enters only the replay path.
    _document(p, 9, 85, 48, 29, "rows", edge=GRAY, dashed=True)
    p.arrow((57, 99), (72, 99), inactive=True, color=GRAY)
    _rbox(p, 72, 72, 118, 37, face=PALE2, edge=GRAY, radius=4)
    p.text(131, 98, "admit schema + coverage", size=8.0)
    p.text(131, 86, "recompute and compare rows", size=7.8, color=GRAY)
    _rbox(p, 238, 72, 164, 37, face=PALE2, edge=BLUE, radius=4)
    p.text(320, 98, "derive supports + evaluate obligations", size=8.0)
    p.text(320, 86, "no producer assertions", size=7.8, color=GRAY)
    for x in (131, 320): p.arrow((x, 72), (x, 59))
    _rbox(p, 72, 34, 118, 25, face="white", edge=BLUE, radius=4)
    _rbox(p, 238, 34, 164, 25, face="white", edge=BLUE, radius=4)
    p.text(131, 46.5, "ACCEPT / canonical REFUTED", size=7.9, weight="bold")
    p.text(320, 46.5, "ACCEPT / canonical REFUTED", size=7.9, weight="bold")
    # Replay-admission failures are validation outcomes, not source verdicts.
    p.arrow((105, 72), (105, 22), inactive=True, color=GRAY)
    p.text(105, 13, "UNCOVERED / INVALID → no repair verdict", size=7.8, color=GRAY)
    p.text(320, 13, "both paths interpret the source", size=7.8, color=GRAY)
    style.save_figure(p.figure, output, name)

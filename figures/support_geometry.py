"""Regenerate the seven manuscript figures without changing evidence records.

The request/receiver overview and replay diagram state matched contracts. The
support diagram reroutes one inactive dependency to avoid an ambiguous crossing.
All plotted measurements and the remaining diagrams use the existing generators.
Only the selected output directory is written.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def panel(plate, x, y, w, h, title, lines=(), *, size=9.4, face=None, edge=None):
    plate.rect(x, y, w, h, face=face or "#eef3f5", edge=edge or "#24596e")
    if lines:
        plate.text(x+w/2, y+h-11, title, size=size, weight="bold")
        gap = 12
        first = y+(h-22)/2+(len(lines)-1)*gap/2
        for i, line in enumerate(lines):
            plate.text(x+w/2, first-i*gap, line, size=size-.2)
    else:
        plate.text(x+w/2, y+h/2, title, size=size, weight="bold")


def overview(r3, out):
    p = r3.Plate(width=428.42, height=306)
    panel(p, 3, 253, 422.42, 50, "Receiver-owned task",
          ["Original P; candidate Q; reference T; repair guard R",
           "Ordered domain D (M inputs); source profile; diagnostic order"], size=10.0)
    panel(p, 3, 207, 422.42, 33, "Receiver reconstruction",
          ["N-node typed DAG; definedness, repair, preservation and trace roots"], size=9.6)
    p.arrow((214.21, 253), (214.21, 240))
    for x, title, subtitle in ((3, "Complete finite decision", "Every input in D"),
                               (220.42, "Supplied-point refutation", "Unsigned profile; same supplied j and u")):
        p.rect(x, 31, 205, 164, face="none", edge="#9baab2")
        p.text(x+102.5, 182, title, size=10.0, weight="bold")
        p.text(x+102.5, 167, subtitle, size=9.1)
        p.arrow((x+102.5, 207), (x+102.5, 195))
    # Evidence-bearing and evidence-free algorithms receive the same task.
    panel(p, 11, 80, 90, 73, "Full vectors",
          ["Bind the packet", "Compute N × M", "Compare every cell"], size=9.5)
    panel(p, 110, 80, 90, 73, "Direct demand",
          ["No packet", "Support-keyed values", "Lazy local rules", "Trace if refuted"], size=9.5)
    panel(p, 228.42, 80, 90, 73, "Compact packet",
          ["Bind (j, u, trace)", r"Check false $O_j$", "and claimed trace"], size=9.2)
    panel(p, 327.42, 80, 90, 73, "Direct at u",
          ["No packet", r"Check false $O_j$", "Recompute trace"], size=9.5)
    for x in (56, 155, 273.42, 372.42):
        p.arrow((x, 80), (x, 65))
    panel(p, 11, 38, 189, 27, "ACCEPT or canonical REFUTED", size=9.3, face="white")
    panel(p, 228.42, 38, 189, 27, "REFUTED at supplied (j, trace, u)", size=9.1, face="white")
    p.text(214.21, 14, "Invalid evidence or interrupted work yields no semantic decision.", size=9.4)
    r3.save_figure(p.figure, out, "repairseal-overview")


def support(r3, out):
    original = r3.Plate

    class UncrossedPlate(original):
        def node(self, x, y, width, height, value, **kwargs):
            if (x, y, width, height) == (40, 253, 72, 24):
                width = 60
            value = value.replace("O_R", "O_1").replace("O_P", "O_2")
            return super().node(x, y, width, height, value, **kwargs)

        def arrow(self, *points, **kwargs):
            if points == ((76, 253), (109, 253), (109, 206), (195, 190)):
                points = ((10, 253), (4, 253), (4, 141), (218, 141), (218, 162))
            return super().arrow(*points, **kwargs)

        def text(self, x, y, value, *args, **kwargs):
            if value == "dashed: not requested":
                x, y = 106, 151
            value = {"1   defined": r"$O_0$   defined", "2   repair": r"$O_1$   repair", "3   preserve": r"$O_2$   preserve"}.get(value, value)
            value = value.replace("O_R", "O_1").replace("O_P", "O_2")
            return super().text(x, y, value, *args, **kwargs)

        def line(self, x0, y0, x1, y1, **kwargs):
            if (x0, y0, x1, y1) == (9, 137, 499, 137):
                y0 = y1 = 130
            return super().line(x0, y0, x1, y1, **kwargs)

    r3.Plate = UncrossedPlate
    try:
        return r3.support_overview(out)
    finally:
        r3.Plate = original


def replay(r3, out):
    p = r3.Plate(width=428.42, height=191)
    panel(p, 3, 154, 422.42, 34, "Same receiver-owned request and source interpretation",
          ["Obligations, domain and canonical diagnostic order stay fixed"], size=9.8)
    for x, title in ((16, "Certificate replay"), (225.42, "Certificate-free control")):
        p.rect(x, 34, 191, 107, face="none", edge="#9baab2")
        p.text(x+95.5, 133, title, size=10.0, weight="bold")
        p.arrow((x+95.5, 154), (x+95.5, 141))
    panel(p, 24, 77, 175, 49, "Untrusted rows: admit and replay",
          ["Check schema and complete coverage", "Recompute and compare every row"], size=9.1)
    panel(p, 233.42, 77, 175, 49, "Evaluate obligations directly",
          ["No producer assertions to compare", "Use receiver-derived support keys"], size=9.1)
    for x in (111.5, 320.92):
        p.arrow((x, 77), (x, 66))
    panel(p, 24, 41, 175, 25, "ACCEPT / canonical REFUTED", size=9.1, face="white")
    panel(p, 233.42, 41, 175, 25, "ACCEPT / canonical REFUTED", size=9.1, face="white")
    p.arrow((24, 96), (5, 96), (5, 15), (129, 15), color="#66747c")
    p.text(66, 15, "replay failure", size=9.0, color="#66747c",
           bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.5})
    panel(p, 129, 4, 287.42, 22, "UNCOVERED / INVALID: no repair verdict", size=9.2,
          face="white", edge="#66747c")
    r3.save_figure(p.figure, out, "trust-boundary")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--only", choices=("all", "overview"), default="all")
    args = parser.parse_args()
    root, out = args.project_root.resolve(), args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    rev = module("revision_figures", root/"artifact/figures/mechanism_geometry.py")
    r3 = module("round3_figures", root/"artifact/figures/figure_style.py")
    if args.only != "overview":
        rev.ceiling(out)
        rev.definedness(out)
        rev.acceptance_transport(out)
    r3.style()
    overview(r3, out)
    if args.only == "overview":
        return
    groups, summary = r3.frozen_records(root/"artifact/data/unsigned-demand")
    r3.style()
    r3.demand_work(groups, out)
    example = support(r3, out)
    replay(r3, out)
    stems = ("repairseal-overview", "ceil-obligations", "value-definedness",
             "support-demand-overview", "acceptance-transport", "demand-work", "trust-boundary")
    files = sorted(out / (stem + suffix) for stem in stems for suffix in (".pdf", ".svg")
                   if (out / (stem + suffix)).exists())
    manifest = {
        "schema": "repairseal-round4-figure-regeneration-v1",
        "script_sha256": sha(Path(__file__)),
        "source_generators": {str(p.relative_to(root)): sha(p) for p in (
            root/"artifact/figures/mechanism_geometry.py", root/"artifact/figures/figure_style.py")},
        "worked_example": example,
        "demand_data": {
            "description": "Semantic-work measurements from actual executions of the retained generated core and grammar requests; not elapsed time or natural-source workload data.",
            "summary_sha256": sha(root/"artifact/data/unsigned-demand/summary.json"),
            "decisions_sha256": summary["records"]["decisions.json"],
            "populations": {k: len(v) for k,v in groups.items()},
            "full_cells": {k: summary["corpora"][k]["full_cells"] for k in groups},
            "direct_cells": {k: summary["corpora"][k]["cells"] for k in groups}},
        "outputs": {p.name: sha(p) for p in files},
    }
    (out/"regeneration-manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps({"pdfs_generated": len(stems), "output": str(out)}))


if __name__ == "__main__":
    main()

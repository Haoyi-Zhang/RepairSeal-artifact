"""Generate the manuscript's vector mechanism figures.

Scientific labels, relations, conditions, coordinates, and plotted points are
placed by code.  Publication figures share the manuscript line width and the
receiver-owned color/shape semantics defined in :mod:`figure_style`.
"""
from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path

import matplotlib
matplotlib.use("Agg")


def module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(value)
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root, output = args.project_root.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    style = module("figure_style", root / "artifact/figures/figure_style.py")
    diagrams = module("tosem_diagrams", root / "artifact/figures/tosem_diagrams.py")
    style.style()

    # Current manuscript figures.  The selected variant numbers are recorded in
    # the retained figure-selection record and regenerated from the same editable source.
    diagrams.overview(style, output)
    diagrams.ceil_obligations(style, root, output)
    diagrams.support_demand(style, output)
    diagrams.acceptance_transport(style, output)
    diagrams.trust_boundary(style, output)

    # Retained artifact-only figures used by the supplementary checks but not
    # consumed by the current manuscript.  Keeping them generated prevents the
    # publication build from silently breaking their documented commands.
    diagrams.definedness_example(style, output)
    groups, _ = style.frozen_records(root / "artifact/data/unsigned-demand")
    style.demand_work(groups, output)


if __name__ == "__main__":
    main()

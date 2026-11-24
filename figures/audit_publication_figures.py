#!/usr/bin/env python3
"""Audit generated publication and artifact figures for geometry and vector integrity.

The audit is deliberately conservative. It checks page bounds, pairwise text
collisions, line/curve intersections with the interior of text spans, raster
image use, and embedded fonts reported by ``pdffonts``. It does not replace
visual inspection at manuscript scale or in grayscale.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path

import fitz

FORMAL_FIGURES = (
    "repairseal-overview.pdf",
    "ceil-obligations.pdf",
    "support-demand-overview.pdf",
    "acceptance-transport.pdf",
    "point-demand-comparison.pdf",
    "witness-search-work.pdf",
    "trust-boundary.pdf",
)

ARTIFACT_ONLY_FIGURES = (
    "value-definedness.pdf",
    "demand-work.pdf",
    "natural-evaluator-comparison.pdf",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def segment_intersects_rect(a: fitz.Point, b: fitz.Point, r: fitz.Rect) -> bool:
    """Liang--Barsky segment/rectangle intersection."""
    x0, y0, x1, y1 = a.x, a.y, b.x, b.y
    dx, dy = x1 - x0, y1 - y0
    p = (-dx, dx, -dy, dy)
    q = (x0 - r.x0, r.x1 - x0, y0 - r.y0, r.y1 - y0)
    u0, u1 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if abs(pi) < 1e-12:
            if qi < 0:
                return False
            continue
        t = qi / pi
        if pi < 0:
            if t > u1:
                return False
            u0 = max(u0, t)
        else:
            if t < u0:
                return False
            u1 = min(u1, t)
    return u0 <= u1


def curve_points(p0, p1, p2, p3, count: int = 20):
    for index in range(count + 1):
        t = index / count
        u = 1 - t
        yield fitz.Point(
            u**3 * p0.x + 3 * u * u * t * p1.x + 3 * u * t * t * p2.x + t**3 * p3.x,
            u**3 * p0.y + 3 * u * u * t * p1.y + 3 * u * t * t * p2.y + t**3 * p3.y,
        )


def drawing_segments(page):
    result = []
    for drawing in page.get_drawings():
        for item in drawing["items"]:
            kind = item[0]
            if kind == "l":
                result.append((item[1], item[2]))
            elif kind == "re":
                rect = item[1]
                points = (
                    fitz.Point(rect.x0, rect.y0),
                    fitz.Point(rect.x1, rect.y0),
                    fitz.Point(rect.x1, rect.y1),
                    fitz.Point(rect.x0, rect.y1),
                )
                result.extend((points[i], points[(i + 1) % 4]) for i in range(4))
            elif kind == "qu":
                quad = item[1]
                points = (quad.ul, quad.ur, quad.lr, quad.ll)
                result.extend((points[i], points[(i + 1) % 4]) for i in range(4))
            elif kind == "c":
                points = list(curve_points(item[1], item[2], item[3], item[4]))
                result.extend(zip(points, points[1:]))
    return result


def embedded_fonts(path: Path):
    process = subprocess.run(
        ["pdffonts", str(path)], capture_output=True, text=True, check=False
    )
    lines = process.stdout.splitlines()[2:]
    rows = []
    for line in lines:
        # The three yes/no fields precede the final two object-id columns.
        match = re.search(r"\s(yes|no)\s+(yes|no)\s+(yes|no)\s+\d+\s+\d+\s*$", line)
        if match:
            rows.append({"embedded": match.group(1) == "yes", "line": line.strip()})
    return {
        "tool_exit": process.returncode,
        "font_count": len(rows),
        "nonembedded": [row["line"] for row in rows if not row["embedded"]],
    }


def inspect(path: Path):
    document = fitz.open(path)
    if document.page_count != 1:
        raise ValueError(f"{path.name}: expected one page")
    page = document[0]
    spans = []
    outside = []
    for block_index, block in enumerate(page.get_text("dict")["blocks"]):
        for line_index, line in enumerate(block.get("lines", [])):
            for span_index, span in enumerate(line.get("spans", [])):
                if not span["text"].strip():
                    continue
                rect = fitz.Rect(span["bbox"])
                item = {
                    "block": block_index,
                    "line": line_index,
                    "span": span_index,
                    "text": span["text"],
                    "size": span["size"],
                    "rect": rect,
                }
                spans.append(item)
                if not page.rect.contains(rect):
                    outside.append(span["text"])

    text_overlaps = []
    for index, first in enumerate(spans):
        for second in spans[index + 1 :]:
            if (first["block"], first["line"]) == (second["block"], second["line"]):
                continue
            intersection = first["rect"] & second["rect"]
            if intersection.is_empty or intersection.get_area() <= 0.1:
                continue
            first_ratio = intersection.get_area() / max(1, first["rect"].get_area())
            second_ratio = intersection.get_area() / max(1, second["rect"].get_area())
            if max(first_ratio, second_ratio) > 0.08:
                text_overlaps.append([first["text"], second["text"]])

    segments = drawing_segments(page)
    line_overlaps = []
    for span in spans:
        rect = span["rect"]
        inset = min(0.75, max(0.1, (rect.y1 - rect.y0) * 0.08))
        core = fitz.Rect(rect.x0 + 0.4, rect.y0 + inset, rect.x1 - 0.4, rect.y1 - inset)
        for start, end in segments:
            if math.hypot(end.x - start.x, end.y - start.y) <= 0.5:
                continue
            if segment_intersects_rect(start, end, core):
                line_overlaps.append(span["text"])
                break

    fonts = embedded_fonts(path)
    issues = []
    if outside:
        issues.append("text_outside_page")
    if text_overlaps:
        issues.append("text_text_overlap")
    if line_overlaps:
        issues.append("line_text_overlap")
    if page.get_images(full=True):
        issues.append("raster_image_present")
    if fonts["tool_exit"] != 0 or fonts["nonembedded"]:
        issues.append("font_embedding")

    return {
        "file": path.name,
        "sha256": sha256(path),
        "page_points": [page.rect.width, page.rect.height],
        "text_span_count": len(spans),
        "minimum_span_size_points": min(span["size"] for span in spans),
        "raster_image_count": len(page.get_images(full=True)),
        "text_outside_page": outside,
        "text_text_overlaps": text_overlaps,
        "line_text_overlaps": sorted(set(line_overlaps)),
        "fonts": fonts,
        "issues": issues,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--figures", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--include-artifact-only",
        action="store_true",
        help="also audit figures generated for artifact documentation but not included in the current paper",
    )
    args = parser.parse_args()
    names = list(FORMAL_FIGURES)
    if args.include_artifact_only:
        names.extend(ARTIFACT_ONLY_FIGURES)
    records = []
    for name in names:
        record = inspect(args.figures / name)
        record["scope"] = "formal" if name in FORMAL_FIGURES else "artifact_only"
        records.append(record)
    outcome = "PASS" if all(not record["issues"] for record in records) else "FAIL"
    result = {
        "outcome": outcome,
        "figure_count": len(records),
        "formal_figure_count": len(FORMAL_FIGURES),
        "artifact_only_figure_count": len(records) - len(FORMAL_FIGURES),
        "figures": records,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(outcome)
    if outcome != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()

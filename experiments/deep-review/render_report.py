#!/usr/bin/env python3
"""Render the complete Chinese HTML report to a paginated PDF.

Tested with PyMuPDF 1.26.6 and fontTools. The renderer uses PyMuPDF's bundled
Droid Sans Fallback TrueType font; no separate font file is redistributed.
The original HTML remains the content source; PDF text is not substituted.
"""
from pathlib import Path
import argparse
import json
import re
import html as html_module
import tempfile
import io
import fitz
from fontTools.ttLib import TTFont
from fontTools import subset


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[3])
    args = parser.parse_args()
    root = args.root.resolve()
    html = (root / "DEEP_REVIEW.html").read_text(encoding="utf-8")
    mediabox = fitz.paper_rect("a4")
    content = fitz.Rect(48, 47, mediabox.width - 48, mediabox.height - 48)
    def rectfn(rect_num, filled):
        if rect_num > 40:
            raise RuntimeError("Unexpected pagination; inspect HTML layout")
        return mediabox, content, None
    # Use a TrueType CJK face and subset before layout. CID-keyed CFF fonts
    # can have incompatible glyph maps in some Story/renderer combinations.
    # Keep section boundaries explicit: Story does not implement every CSS
    # page-break property across all supported versions.
    with tempfile.TemporaryDirectory(prefix="report-fonts-", dir=root.parent) as temp:
        font_root = Path(temp)
        visible_text = html_module.unescape(re.sub(r"<[^>]*>", " ", html))
        for weight in ("Regular", "Bold"):
            font = TTFont(io.BytesIO(fitz.Font("cjk").buffer))
            options = subset.Options()
            subsetter = subset.Subsetter(options=options)
            subsetter.populate(text=visible_text)
            subsetter.subset(font)
            font.save(str(font_root / f"ReportCJK-{weight}.ttf"))
            font.close()
            html = html.replace(f"NotoSansCJK-{weight}.ttc", f"ReportCJK-{weight}.ttf")
        head = html.split("<body>", 1)[0] + "<body>"
        sections = re.findall(r"<section\b.*?</section>", html, flags=re.S)
        if len(sections) != 9:
            raise RuntimeError(f"Unexpected report section count: {len(sections)}")
        doc = fitz.open()
        for section in sections:
            story = fitz.Story(html=head + section + "</body></html>", archive=fitz.Archive(str(font_root)))
            part = story.write_with_links(rectfn)
            doc.insert_pdf(part)
            part.close()
    for i, page in enumerate(doc):
        page.draw_line((48, 28), (mediabox.width - 48, 28), color=(0.73, 0.81, 0.85), width=0.5)
        page.insert_text((48, 23), "REPAIRSEAL  /  DEEP REVIEW  /  2026-11-27", fontsize=7, color=(0.28, 0.40, 0.47))
        page.insert_text((48, mediabox.height - 27), "Research scope, source evidence, and reproducibility", fontsize=7, color=(0.38, 0.44, 0.49))
        page.insert_text((mediabox.width - 85, mediabox.height - 27), f"{i+1} / {len(doc)}", fontsize=7, color=(0.38, 0.44, 0.49))
    doc.set_metadata({"title": "RepairSeal 深度复核与完成报告", "subject": "实际实现、真实补丁分析、论证修正与可复核交付", "author": "RepairSeal project review", "creator": f"PyMuPDF {fitz.VersionBind}"})
    out = root / "DEEP_REVIEW.pdf"
    doc.save(out, garbage=4, deflate=True)
    print(json.dumps({"output": str(out), "pages": len(doc), "bytes": out.stat().st_size, "renderer": fitz.VersionBind}, ensure_ascii=False))


if __name__ == "__main__":
    main()

"""Check vector artwork and render print-scale previews inside the paper workspace.

Text bounding-box checks are useful diagnostics, not a substitute for visual review.
"""
import json
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[1]
PRINT_WIDTH_PT = 5.5 * 72


def main():
    with fitz.open(ROOT / "figures/overview.pdf") as document:
        page = document[0]
        spans = [
            span
            for block in page.get_text("dict")["blocks"]
            for line in block.get("lines", [])
            for span in line["spans"]
            if span["text"].strip()
        ]
        overlaps = []
        overflow = []
        for i, span in enumerate(spans):
            bounds = fitz.Rect(span["bbox"])
            if not page.rect.contains(bounds):
                overflow.append(span["text"])
            for other in spans[i + 1:]:
                intersection = bounds & fitz.Rect(other["bbox"])
                if not intersection.is_empty and intersection.width > .5 and intersection.height > .5:
                    overlaps.append([span["text"], other["text"]])
        scale = PRINT_WIDTH_PT / page.rect.width
        # 144 dpi: a 5.5-inch figure is 792 pixels wide in this diagnostic preview.
        page.get_pixmap(matrix=fitz.Matrix(scale * 2, scale * 2)).save(
            ROOT / "build/figure_print_scale.png"
        )
        page.get_pixmap(matrix=fitz.Matrix(2, 2), colorspace=fitz.csGRAY).save(
            ROOT / "build/figure_grayscale.png"
        )
        report = {
            "figure_size_pt": [page.rect.width, page.rect.height],
            "paper_width_inches": PRINT_WIDTH_PT / 72,
            "smallest_text_at_paper_width_pt": min(span["size"] for span in spans) * scale,
            "embedded_raster_images": len(page.get_images()),
            "text_span_overlaps": overlaps,
            "text_artboard_overflow": overflow,
        }
    with fitz.open(ROOT / "build/main.pdf") as manuscript:
        texts = [page.get_text() for page in manuscript]
        report["manuscript_pages"] = len(manuscript)
        report["figure_pages"] = [i + 1 for i, text in enumerate(texts) if "Figure 1:" in text]
    (ROOT / "build/figure_check.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()

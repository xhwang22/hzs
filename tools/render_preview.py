"""Render the compiled manuscript for visual review; no source-project imports."""
import json
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build"


def main():
    with fitz.open(OUT / "main.pdf") as pdf:
        texts = [page.get_text() for page in pdf]
        (OUT / "main.txt").write_text("\n\n".join("===== PAGE %d =====\n%s" % (i+1,t) for i,t in enumerate(texts)))
        cols, width, height = 4, 170, 235
        sheet = fitz.open()
        canvas = sheet.new_page(width=cols*width, height=((len(pdf)+cols-1)//cols)*height)
        for i, page in enumerate(pdf):
            row, col = divmod(i, cols)
            rect = fitz.Rect(col*width+3, row*height+3, (col+1)*width-3, (row+1)*height-15)
            canvas.insert_image(rect, pixmap=page.get_pixmap(matrix=fitz.Matrix(.55,.55)))
            canvas.insert_text((col*width+6, (row+1)*height-4), "Page %d" % (i+1), fontsize=7)
        canvas.get_pixmap(matrix=fitz.Matrix(2,2)).save(OUT / "contact_sheet.png")
        preview_pages = set(range(min(len(pdf), 3))) | {i for i, t in enumerate(texts)
            if any(mark in t for mark in ("Figure 2:", "Figure 3:", "Table 1:", "Frozen study identities"))}
        for i in sorted(preview_pages):
            pdf[i].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(OUT / ("page_%02d.png" % (i+1)))
        report = {"pages": len(pdf), "references_pages": [i+1 for i,t in enumerate(texts) if "REFERENCES" in t],
                  "ai_statement_pages": [i+1 for i,t in enumerate(texts) if "AI USE STATEMENT" in t],
                  "figure_pages": [i+1 for i,t in enumerate(texts) if "Figure 1:" in t],
                  "evolution_pages": [i+1 for i,t in enumerate(texts) if "Figure 2:" in t],
                  "main_table_pages": [i+1 for i,t in enumerate(texts) if "Table 1:" in t],
                  "todo_occurrences": sum(t.count("TODO:") for t in texts)}
        (OUT / "document_check.json").write_text(json.dumps(report, indent=2))
        print(json.dumps(report))
    with fitz.open(ROOT / "figures/overview.pdf") as pdf:
        pdf[0].get_pixmap(matrix=fitz.Matrix(3,3)).save(ROOT / "figures/overview.png")
        # overview.svg is editable source artwork, not a derivative of the PDF.


if __name__ == "__main__":
    main()

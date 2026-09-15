"""Read-only source inspection; all derived artifacts stay in this paper directory."""
import hashlib
import json
from pathlib import Path

import fitz
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "OpenAgentScaler"
OUT = ROOT / "sources"


def main():
    (OUT / "paper_text").mkdir(parents=True, exist_ok=True)
    metadata = []
    for path in sorted((SOURCE / "paper/pdfs").glob("*.pdf")):
        with fitz.open(path) as pdf:
            text = "\n\n".join("===== PAGE %d =====\n%s" % (i + 1, page.get_text()) for i, page in enumerate(pdf))
            metadata.append({"file": str(path.relative_to(SOURCE)), "pages": len(pdf), "metadata": pdf.metadata})
        (OUT / "paper_text" / (path.stem + ".txt")).write_text(text)
    (OUT / "html_text").mkdir(exist_ok=True)
    for base in [SOURCE / "paper/paper_report", SOURCE / "report/2026-09-01-goal"]:
        for path in sorted(base.glob("*.html")):
            soup = BeautifulSoup(path.read_text(), "html.parser")
            for node in soup(["script", "style"]):
                node.decompose()
            (OUT / "html_text" / (path.stem + ".txt")).write_text(soup.get_text("\n", strip=True))
    (OUT / "pdf_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2))
    snapshot = {}
    for base in [SOURCE / "envopt", SOURCE / "report", SOURCE / "paper"]:
        for path in sorted(base.rglob("*")):
            rel = path.relative_to(SOURCE)
            if any(part in ("runs", ".git", "__pycache__", ".pytest_cache") for part in rel.parts):
                continue
            if path.is_file() and path.suffix in (".py", ".md", ".yaml", ".txt", ".html"):
                snapshot[str(rel)] = hashlib.sha256(path.read_bytes()).hexdigest()
    (OUT / "source_sha256.json").write_text(json.dumps(snapshot, indent=2))
    print("Extracted %d PDFs; fingerprinted %d source documents." % (len(metadata), len(snapshot)))


if __name__ == "__main__":
    main()

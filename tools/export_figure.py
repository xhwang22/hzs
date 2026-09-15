"""Export the editable SVG artwork as vector PDF and a high-resolution preview."""
from pathlib import Path
import argparse

import cairosvg

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name", nargs="?", default="overview", choices=["overview", "design_extensions"])
    name = parser.parse_args().name
    source = FIGURES / (name + ".svg")
    cairosvg.svg2pdf(url=str(source), write_to=str(FIGURES / (name + ".pdf")))
    cairosvg.svg2png(url=str(source), write_to=str(FIGURES / (name + ".png")), output_width=2400)
    print("Exported %s.svg → vector PDF and PNG" % name)

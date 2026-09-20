# Seeing the Patterns, Closing the Loop

Evolving Environments for Agent Training — anonymous ICLR 2027 manuscript.

- LaTeX entry point: [`main.tex`](main.tex)
- Compiled paper: [`build/main.pdf`](build/main.pdf)

## Repository contents

This repository contains only the manuscript and its rendering dependencies:
section sources, BibTeX, the PDF figures and table fragments used by the paper,
and the unmodified ICLR 2027 style dependencies.

Research logs, analysis reports, raw experimental artifacts, draft figures,
generation scripts, and preview images are not part of this rendering bundle.

In the local workspace, `build/` contains only the published `main.pdf`.
Compiler intermediates and verification reports go in `.tmp/build/`; page and
figure PNG previews go in `.tmp/previews/`. Historical drafts live under `.tmp/`.
Final figure PDFs and editable SVG masters remain in `figures/`, and author-supplied
reference images remain in `reference_fig/`.

## Compile

On Overleaf, set the main document to `main.tex` and the compiler to **XeLaTeX**.
The included `latexmkrc` locates the vendored style files.

Locally, install [Tectonic](https://tectonic-typesetting.github.io/) and Python 3,
then run:

```sh
make
```

The output is `build/main.pdf`. A custom executable can be selected with
`make TECTONIC=/path/to/tectonic PYTHON=/path/to/python3`. Figure PDFs are already
supplied; no third-party Python packages, experimental data, or model APIs are needed.

The publisher preserves the existing PDF's original document ID and updates the
file in place, allowing PDF.js viewers to reuse page, zoom, and scroll history
across recompiles. The new version ID and page content remain unchanged. On a
first build the compiler's document ID is used. Incompatible or incomplete PDFs
are rejected before the existing preview is overwritten. Direct Overleaf builds
do not use this local preview-publishing step.

When adding a new figure or table dependency, include it in `.gitignore`'s
publication allowlist as well.

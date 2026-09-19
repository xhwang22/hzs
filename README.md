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

## Compile

On Overleaf, set the main document to `main.tex` and the compiler to **XeLaTeX**.
The included `latexmkrc` locates the vendored style files.

Locally, install [Tectonic](https://tectonic-typesetting.github.io/) and run:

```sh
make
```

The output is `build/main.pdf`. A custom executable can be selected with
`make TECTONIC=/path/to/tectonic`. Figure PDFs are already supplied; compilation
does not require Python, experimental data, or external model APIs.

When adding a new figure or table dependency, include it in `.gitignore`'s
publication allowlist as well.

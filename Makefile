SHELL := /bin/sh
ROOT := $(CURDIR)
TECTONIC := $(ROOT)/tools/tectonic
export XDG_CACHE_HOME := $(ROOT)/.cache
export TMPDIR := $(ROOT)/.tmp
export TEXINPUTS := $(ROOT)/vendor/iclr2027:
export BSTINPUTS := $(ROOT)/vendor/iclr2027:

.PHONY: all paper figure
all: paper

figure: figures/overview.pdf figures/design_extensions.pdf

figures/overview.pdf: figures/overview.svg tools/export_figure.py
	$(ROOT)/.venv/bin/python tools/export_figure.py

figures/design_extensions.pdf: figures/design_extensions.svg tools/export_figure.py
	$(ROOT)/.venv/bin/python tools/export_figure.py design_extensions

figures/evolution.pdf: data/results_20260915.json data/appworld_user_20260915.csv data/appworld_user_20260915.meta.json tools/plot_results.py
	$(ROOT)/.venv/bin/python tools/plot_results.py

paper: figures/overview.pdf figures/evolution.pdf
	$(TECTONIC) -X compile -Z search-path=$(ROOT)/vendor/iclr2027 --keep-logs --keep-intermediates --outdir build main.tex

SHELL := /bin/sh
ROOT := $(CURDIR)
TECTONIC ?= $(if $(wildcard $(ROOT)/tools/tectonic),$(ROOT)/tools/tectonic,tectonic)
PYTHON ?= python3
export XDG_CACHE_HOME := $(ROOT)/.cache
export TMPDIR := $(ROOT)/.tmp
export TEXINPUTS := $(ROOT)/vendor/iclr2027:
export BSTINPUTS := $(ROOT)/vendor/iclr2027:

.PHONY: all paper
all: paper

# Figure PDFs and table fragments are committed rendering inputs. Normal builds
# never regenerate them or require local research data and plotting scripts.
# Compile off to the side so failed builds leave the published PDF intact.
# Publish in place to retain the file watcher, preserving the original document
# ID used by PDF.js reading history. The newly compiled version ID is unchanged.
paper:
	mkdir -p build .cache .tmp/build/compile
	"$(TECTONIC)" -X compile -Z search-path=$(ROOT)/vendor/iclr2027 --keep-logs --keep-intermediates --outdir .tmp/build/compile main.tex
	$(PYTHON) tools/publish_pdf.py .tmp/build/compile/main.pdf build/main.pdf

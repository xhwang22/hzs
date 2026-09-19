SHELL := /bin/sh
ROOT := $(CURDIR)
TECTONIC ?= $(if $(wildcard $(ROOT)/tools/tectonic),$(ROOT)/tools/tectonic,tectonic)
export XDG_CACHE_HOME := $(ROOT)/.cache
export TMPDIR := $(ROOT)/.tmp
export TEXINPUTS := $(ROOT)/vendor/iclr2027:
export BSTINPUTS := $(ROOT)/vendor/iclr2027:

.PHONY: all paper
all: paper

# Figure PDFs and table fragments are committed rendering inputs. Normal builds
# never regenerate them or require local research data and plotting scripts.
paper:
	mkdir -p build .cache .tmp
	"$(TECTONIC)" -X compile -Z search-path=$(ROOT)/vendor/iclr2027 --keep-logs --keep-intermediates --outdir build main.tex

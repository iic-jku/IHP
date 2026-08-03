# =============================================================================
# IHP SG13G2 RF evaluation pipeline
# =============================================================================
# Three stages, each with its own set of targets:
#
#   generate  ->  sim  ->  plot
#   (Python)     (Palace)   (Python)
#
#   1. generate-*  build GDS layouts of test structures into gds/<sweep>/
#   2. sim-*       mesh each GDS and run the Palace FEM solver, then convert the
#                  raw output to Touchstone (.sNp) via combine_snp.py
#   3. plot-*      extract the figures of merit from the .sNp files and write
#                  PNGs + CSVs into images/
#
# The sweeps:
#   blc            branch-line coupler, one per design frequency  (4-port)
#   wpd            Wilkinson power divider, one per design freq    (3-port)
#   tline-z0       characteristic impedance Z0 vs signal width    (2-port, 1 freq)
#   tline-loss     loss per mm vs width, two-length de-embedded    (2-port, freq band)
#   tline-sparams  fixed-50-ohm lines across lengths, for eyeballing raw S-params
#
# Typical use:
#   make generate-tline-z0 && make sim-tline-z0 && make plot-tline-z0
#   make help                 # list every target
#
# WARNING: the sim-* targets each launch many Palace runs (the full tline sweeps
# are thousands of runs, hours of compute). Generate and simulate one sweep at a
# time rather than running `make all` unattended.
#
# Directory layout produced:
#   gds/<sweep>/*.gds                              layouts (from generate-*)
#   gds/<sweep>/<model>/<model>_data/...   mesh, config, Palace output, .sNp
#   images/*.png, *.csv                            results (from plot-* and img-*)
# =============================================================================

# absolute path to this Makefile's directory, so targets work from any cwd
MAKEFILE_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

PYTHON   := python3
# NOTE: keep these as plain assignments with NO trailing inline comment - make folds
# the whitespace before a `#` into the value and would corrupt the paths.
# GDS_DIR    = root of all generated layouts + sim data
# IMAGES_DIR = output PNGs and CSVs (plot results + layout previews)
GDS_DIR    := $(MAKEFILE_DIR)/gds
IMAGES_DIR := $(MAKEFILE_DIR)/images

.DEFAULT_GOAL := help

# Auto-documenting help: prints every target that has a `## comment` after it.
help: ## Show this help message
	@echo 'Usage: make <target>'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-24s %s\n", $$1, $$2}'
.PHONY: help

# -----------------------------------------------------------------------------
# 1. GENERATE - build GDS layouts (fast, no solver involved)
# -----------------------------------------------------------------------------
generate-blc: ## Generate the branch-line-coupler GDS sweep (gds/blc)
	cd $(MAKEFILE_DIR) && $(PYTHON) generate_blc.py
.PHONY: generate-blc

generate-wpd: ## Generate the Wilkinson-power-divider GDS sweep (gds/wpd)
	cd $(MAKEFILE_DIR) && $(PYTHON) generate_wpd.py
.PHONY: generate-wpd

generate-tline-sparams: ## Generate the tline S-parameter verification sweep (gds/tline_sparams)
	cd $(MAKEFILE_DIR) && $(PYTHON) generate_tline_sparams.py
.PHONY: generate-tline-sparams

generate-tline-z0: ## Generate the tline Z0(w) sweep (gds/tline_z0)
	cd $(MAKEFILE_DIR) && $(PYTHON) generate_tline_z0.py
.PHONY: generate-tline-z0

generate-tline-loss: ## Generate the tline loss(w)/mm sweep (gds/tline_loss)
	cd $(MAKEFILE_DIR) && $(PYTHON) generate_tline_loss.py
.PHONY: generate-tline-loss

generate-tline: generate-tline-sparams generate-tline-z0 generate-tline-loss ## Generate all tline GDS sweeps
.PHONY: generate-tline

generate: generate-blc generate-wpd generate-tline ## Generate all GDS sweeps
.PHONY: generate

# -----------------------------------------------------------------------------
# 2. SIM - mesh + solve each GDS with Palace (SLOW; many runs per sweep)
# -----------------------------------------------------------------------------
# run_more_sims.sh loops over every .gds in the given folder, calling run_sim.sh
# (which runs palace_sim.py to build the mesh/config, then Palace), and
# finally runs combine_snp.py once to turn all raw port-S.csv output into .sNp
# Touchstone files. The stackup is set by XML_filename in palace_sim.py
# (currently SG13G2_200um.xml).
sim-blc: ## Run Palace simulations on all generated BLC GDS files
	cd $(MAKEFILE_DIR) && ./run_more_sims.sh $(GDS_DIR)/blc
.PHONY: sim-blc

sim-wpd: ## Run Palace simulations on all generated WPD GDS files
	cd $(MAKEFILE_DIR) && ./run_more_sims.sh $(GDS_DIR)/wpd
.PHONY: sim-wpd

sim-tline-sparams: ## Run Palace simulations on the tline S-parameter verification sweep
	cd $(MAKEFILE_DIR) && ./run_more_sims.sh $(GDS_DIR)/tline_sparams
.PHONY: sim-tline-sparams

sim-tline-z0: ## Run Palace simulations on the tline Z0(w) sweep
	cd $(MAKEFILE_DIR) && ./run_more_sims.sh $(GDS_DIR)/tline_z0
.PHONY: sim-tline-z0

sim-tline-loss: ## Run Palace simulations on the tline loss(w)/mm sweep
	cd $(MAKEFILE_DIR) && ./run_more_sims.sh $(GDS_DIR)/tline_loss
.PHONY: sim-tline-loss

sim-tline: sim-tline-sparams sim-tline-z0 sim-tline-loss ## Run Palace simulations on all tline GDS sweeps
.PHONY: sim-tline

# The overall sim target finishes with clean-intermediates (cleanup section at the
# end of this file): the .sNp Touchstone results are kept, but meshes, raw Palace
# output and the .gds layouts are deleted to save disk.
# The per-sweep sim-* targets do NOT clean, so partial reruns keep their raw data.
sim: sim-blc sim-wpd sim-tline ## Run all Palace simulations, then drop intermediates (keeps .sNp)
	$(MAKE) clean-intermediates
.PHONY: sim

# -----------------------------------------------------------------------------
# 3. PLOT - extract figures of merit from the .sNp files into images/
# -----------------------------------------------------------------------------
# The z0/loss targets loop over every design frequency found in the sweep's model
# directory names (the *_<N>GHz tag) and emit one faceted plot + CSV per frequency.
# (Directory names, not .gds filenames: layouts are deleted by clean-intermediates.)

# plot-tline-z0 opens the interactive window by default (Z0 is a single-frequency
# sweep -> one window; click a point to read its value). The aggregate targets below
# override Z0_SHOW to empty so batch runs don't block. To force batch here too (e.g.
# on a headless machine): make plot-tline-z0 Z0_SHOW=
#
# By default one plot is made per design-frequency tag found in the model dir names.
#   FREQ=<GHz>       restrict to a single design tag instead of looping all of them
#   EVAL_FREQ=<GHz>  read Zc at this in-band frequency instead of at the tag itself
#                    (each sim spans 0.5-1.5x its tag), e.g.
#                    make plot-tline-z0 EVAL_FREQ=150   # Zc @ 150GHz from the 200GHz sweep
Z0_SHOW ?= --show
FREQ ?=
EVAL_FREQ ?=
plot-tline-z0: ## Plot Z0(w) by ground layer (FREQ=/EVAL_FREQ= to pick frequencies, Z0_SHOW= for batch)
	cd $(MAKEFILE_DIR) && for f in $(if $(FREQ),$(FREQ),$$(ls -d $(GDS_DIR)/tline_z0/*GHz 2>/dev/null | sed -E 's/.*_([0-9.]+)GHz$$/\1/' | sort -n -u)); do \
		$(PYTHON) plot_tline.py z0 $(GDS_DIR)/tline_z0 --freq $$f $(if $(EVAL_FREQ),--eval-freq $(EVAL_FREQ)) --length-um 1000 $(Z0_SHOW); \
	done
.PHONY: plot-tline-z0

# Zc vs frequency across the whole simulated band (per stack, curve per width) - shows
# the impedance dispersion the single-point z0 plot can't. Interactive by default too;
# Z0_SHOW is shared with plot-tline-z0 (aggregates below set it empty for batch runs).
plot-tline-z0-freq: ## Plot Zc vs frequency (dispersion) per stack + open interactive window
	cd $(MAKEFILE_DIR) && $(PYTHON) plot_tline.py z0-freq $(GDS_DIR)/tline_z0 $(Z0_SHOW)
.PHONY: plot-tline-z0-freq

# 3D surface Zc(frequency, width) for ONE stack (a surface can only show one).
# Defaults to TopMetal2/Metal5; override per invocation, e.g.
#   make plot-tline-z0-3d SIGNAL=topmetal1 GROUND=metal3
SIGNAL ?= topmetal2
GROUND ?= metal5
plot-tline-z0-3d: ## 3D surface of Zc over (freq, width) for one stack (SIGNAL=/GROUND= to pick)
	cd $(MAKEFILE_DIR) && $(PYTHON) plot_tline.py z0-3d $(GDS_DIR)/tline_z0 --signal $(SIGNAL) --ground $(GROUND) $(Z0_SHOW)
.PHONY: plot-tline-z0-3d

plot-tline-loss: ## Plot loss(w)/mm faceted by ground layer, for every simulated frequency (two-length de-embedded)
	cd $(MAKEFILE_DIR) && for f in $$(ls -d $(GDS_DIR)/tline_loss/*GHz 2>/dev/null | sed -E 's/.*_([0-9.]+)GHz$$/\1/' | sort -n -u); do \
		$(PYTHON) plot_tline.py loss $(GDS_DIR)/tline_loss --freq $$f --length1-um 500 --length2-um 1000; \
	done
.PHONY: plot-tline-loss

# Z0-vs-loss design chart: joins the z0 sweep (Zc) with the loss sweep (two-length
# de-embedded loss) on (stack, width) - needs sim results from BOTH sweeps. One plot
# per design frequency present in the loss sweep (or a single one via FREQ=).
plot-tline-design: ## Z0-vs-loss design chart, one point per stack+width (needs z0 AND loss sims)
	cd $(MAKEFILE_DIR) && for f in $(if $(FREQ),$(FREQ),$$(ls -d $(GDS_DIR)/tline_loss/*GHz 2>/dev/null | sed -E 's/.*_([0-9.]+)GHz$$/\1/' | sort -n -u)); do \
		$(PYTHON) plot_tline.py design $(GDS_DIR)/tline_z0 $(GDS_DIR)/tline_loss --freq $$f $(Z0_SHOW); \
	done
.PHONY: plot-tline-design

# sparams overlays raw S21/S11 vs frequency for a HAND-PICKED set of files on one
# axis (it warns past ~8 files), so there's no all-files target - pass the files
# explicitly, e.g.:
#   make plot-tline-sparams FILES="gds/tline_sparams/foo gds/tline_sparams/bar"
plot-tline-sparams: ## Overlay raw S21/S11 vs freq for hand-picked files (set FILES="...")
	@test -n "$(FILES)" || { echo 'set FILES, e.g. make plot-tline-sparams FILES="gds/tline_sparams/a gds/tline_sparams/b"'; exit 1; }
	cd $(MAKEFILE_DIR) && $(PYTHON) plot_tline.py sparams $(FILES)
.PHONY: plot-tline-sparams

# aggregate/batch targets must not block on an interactive window; Z0_SHOW:= (empty)
# is inherited by plot-tline-z0 when it's built as a prerequisite of these.
plot-tline: Z0_SHOW :=
plot-tline: plot-tline-z0 plot-tline-z0-freq plot-tline-z0-3d plot-tline-loss plot-tline-design ## Generate all tline plots into images/
.PHONY: plot-tline

plot-blc: ## Plot branch-line-coupler S-params, imbalance, phase + summary (images/)
	cd $(MAKEFILE_DIR) && $(PYTHON) plot_blc.py $(GDS_DIR)/blc
.PHONY: plot-blc

plot-wpd: ## Plot Wilkinson-divider S-params, imbalance, phase + summary (images/)
	cd $(MAKEFILE_DIR) && $(PYTHON) plot_wpd.py $(GDS_DIR)/wpd
.PHONY: plot-wpd

plot: plot-tline plot-blc plot-wpd ## Generate every plot (tline + blc + wpd)
.PHONY: plot

# -----------------------------------------------------------------------------
# IMG - render layout preview PNGs (fast, no solver; needs a generated GDS)
# -----------------------------------------------------------------------------
# lay2img.py renders a GDS into a PNG under images/ so you can eyeball a layout
# without opening KLayout. It uses the PDK layer properties, so PDK_ROOT/PDK must
# point at the IHP PDK (defaults: PDK_ROOT=IHP-Open-PDK, PDK=ihp-sg13g2 - override
# in the environment if elsewhere). Previews land in images/ alongside the plot
# results, so `make clean-images` removes them too.
#
# Scope: only the TopMetal2/Metal5 stackup at 160 GHz (--background black -> one
# PNG per layout, <name>_black.png). blc/wpd are TM2/M5 at every frequency, so they
# are picked by frequency alone; the tline sweep is filtered to *topmetal2_over_metal5*.
#   IMG_FREQ=<GHz>   pick another design frequency (default 160)
# Render arbitrary files with `make img FILES="a.gds b.gds ..."` (also black only).
IMG_DIR          := $(IMAGES_DIR)
IMG_OVERSAMPLING ?= 4
IMG_FREQ         ?= 200
IMG_BG           ?= black

img-blc: ## Render the TM2/M5 branch-line-coupler at IMG_FREQ GHz, black (images/)
	mkdir -p $(IMG_DIR)
	cd $(MAKEFILE_DIR) && f=$(GDS_DIR)/blc/blc_$(IMG_FREQ)GHz.gds; \
		test -f "$$f" || { echo "no such layout: $$f (run make generate-blc)"; exit 1; }; \
		$(PYTHON) lay2img.py "$$f" $(IMG_DIR)/$$(basename "$$f" .gds).png --oversampling $(IMG_OVERSAMPLING) --background $(IMG_BG)
.PHONY: img-blc

img-wpd: ## Render the TM2/M5 Wilkinson-power-divider at IMG_FREQ GHz, black (images/)
	mkdir -p $(IMG_DIR)
	cd $(MAKEFILE_DIR) && f=$(GDS_DIR)/wpd/wpd_$(IMG_FREQ)GHz.gds; \
		test -f "$$f" || { echo "no such layout: $$f (run make generate-wpd)"; exit 1; }; \
		$(PYTHON) lay2img.py "$$f" $(IMG_DIR)/$$(basename "$$f" .gds).png --oversampling $(IMG_OVERSAMPLING) --background $(IMG_BG)
.PHONY: img-wpd

img-tline: ## Render the TM2/M5 w20um l500um loss tline at IMG_FREQ GHz, black (images/)
	mkdir -p $(IMG_DIR)
	cd $(MAKEFILE_DIR) && f=$(GDS_DIR)/tline_loss/tline_topmetal2_over_metal5_w20um_l500um_$(IMG_FREQ)GHz.gds; \
		test -f "$$f" || { echo "no such layout: $$f (run make generate-tline-loss)"; exit 1; }; \
		$(PYTHON) lay2img.py "$$f" $(IMG_DIR)/$$(basename "$$f" .gds).png --oversampling $(IMG_OVERSAMPLING) --background $(IMG_BG)
.PHONY: img-tline

img: ## Render layout PNGs for hand-picked GDS files, black (set FILES="a.gds b.gds ...")
	@test -n "$(FILES)" || { echo 'set FILES, e.g. make img FILES="gds/blc/blc_160GHz.gds gds/wpd/wpd_160GHz.gds"'; exit 1; }
	mkdir -p $(IMG_DIR)
	cd $(MAKEFILE_DIR) && for f in $(FILES); do \
		$(PYTHON) lay2img.py "$$f" $(IMG_DIR)/$$(basename "$$f" .gds).png --oversampling $(IMG_OVERSAMPLING) --background $(IMG_BG); \
	done
.PHONY: img

img-all: img-blc img-wpd img-tline ## Render TM2/M5 blc + wpd + tline at IMG_FREQ GHz, black (images/)
.PHONY: img-all

# -----------------------------------------------------------------------------
# End-to-end
# -----------------------------------------------------------------------------
all: generate sim plot ## Generate every GDS sweep, simulate, and plot all of it (very slow)
.PHONY: all

# -----------------------------------------------------------------------------
# Cleanup
# -----------------------------------------------------------------------------
# Two tiers:
#   safe (results kept)   clean-sim-raw, clean-layouts, clean-intermediates
#                         - drop regenerable intermediates, KEEP the .sNp results
#   destructive           clean, clean-images, clean-all
#                         - delete the results themselves

# --- safe tier: keeps the .sNp results (what plot-* reads, tracked in git) ---

# Deletes the bulky per-model intermediates: Gmsh meshes, ParaView field dumps,
# Palace/gds2palace JSON (config.json, port_information.json) and the raw Palace
# CSVs that combine_snp.py has already folded into the .sNp.
# NOTE: re-running combine_snp.py needs those raw CSVs and port_information.json,
# so only clean once the .sNp files exist.
clean-sim-raw: ## Delete meshes + raw Palace output, keep .sNp results (saves most disk)
	find $(GDS_DIR) -type f -name '*.msh' -delete 2>/dev/null || true
	find $(GDS_DIR) -type d -name 'paraview' -prune -exec rm -rf {} + 2>/dev/null || true
	find $(GDS_DIR) -type f \( -name 'port-*.csv' -o -name 'domain-E.csv' -o -name 'error-indicators.csv' \) -delete 2>/dev/null || true
	find $(GDS_DIR) -type f -name '*.json' -delete 2>/dev/null || true
.PHONY: clean-sim-raw

# The .gds layouts are inputs, regenerated by `make generate` - once simulated they
# are no longer needed (plot targets read frequencies from the model DIRECTORY names,
# which stay). Kept separate from clean-sim-raw so layouts survive partial sim runs.
clean-layouts: ## Delete the generated .gds layout files (regenerate with `make generate`)
	find $(GDS_DIR) -type f -name '*.gds' -delete 2>/dev/null || true
.PHONY: clean-layouts

# Everything under gds/ that isn't a .sNp result: what `sim` runs when all sweeps
# are done. (Unlike `clean`, this KEEPS the .sNp results.)
clean-intermediates: clean-sim-raw clean-layouts ## Delete all sim intermediates + layouts, keep only .sNp results
.PHONY: clean-intermediates

# --- destructive tier: deletes the results too ---

# DESTRUCTIVE + LOCAL: `clean` deletes gds/ from disk - layouts, Palace meshes,
# configs and .sNp results under gds/<sweep>/<model>/, all expensive to regenerate.
# Use clean-intermediates to keep the .sNp results, or clean-images to only redo plots.
clean: ## DELETE all generated GDS + sim data incl. .sNp results (destructive, local only)
	rm -rf $(GDS_DIR)
.PHONY: clean

clean-images: ## Remove generated plots, CSVs + layout previews (images/)
	rm -rf $(IMAGES_DIR)
.PHONY: clean-images

clean-all: clean clean-images ## Remove everything generated (gds/ + images/)
.PHONY: clean-all

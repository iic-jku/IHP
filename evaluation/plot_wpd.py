"""Plot Wilkinson-power-divider (WPD) EM results from Touchstone (.s3p) files.

A Wilkinson divider is a 3-port equal-split divider: power fed into the input port
splits equally (-3 dB) between the two output ports, which are IN PHASE (unlike the
90-degree branch-line hybrid). The figures of merit are therefore:

    * coupling / insertion loss - are the two outputs really near -3 dB?
    * return loss  - is the input port well matched (|S11| low)?
    * isolation    - how dead is the output-output path (|S32| low)?
    * phase balance - is the phase difference between the outputs ~0 degrees?

NOTE on isolation: the IHP PDK cell does not place the isolation resistor (its
placement is commented out in the cell source), so the simulated structure is the
resistor-less divider. |S32| and the output match will look poor - that is physical
for a Wilkinson without its resistor, not a simulation error. Insertion loss, input
match and output balance are the meaningful metrics here.

Port roles are fixed by generate_wpd.py: port 1 = e1 input, ports 2/3 = e2/e3 outputs,
so no data-driven port classification is needed (unlike the BLC).

Two kinds of output are written to ./images/:
    * wpd_<N>GHz.png  - per divider: |S| vs f, amplitude imbalance vs f, phase-diff vs f
    * wpd_summary.png / .csv - the key metrics for every divider, at its design frequency

Usage:
    python plot_wpd.py gds/wpd                 # every .s3p found under gds/wpd
    python plot_wpd.py a.s3p b.s3p             # specific files
    python plot_wpd.py gds/wpd --rl-spec 15    # change the return-loss guide line

Paths may be individual Touchstone files or directories (searched recursively).
"""

import argparse
import csv
import os
import re
import sys
from glob import glob

import matplotlib
import numpy as np
import skrf as rf

# This script only writes PNGs. Letting matplotlib pick a backend makes it probe the
# X display, which blocks indefinitely on headless/VNC setups (DISPLAY set but no
# usable GUI), so pin the non-interactive backend before pyplot is imported.
matplotlib.use("Agg")

from matplotlib import pyplot as plt

# ---------------------------------------------------------------------------
# style: shared with plot_blc.py - validated CVD-safe palette, recessive grid
# ---------------------------------------------------------------------------
PALETTE = ["#2a78d6", "#1baf7a", "#eda100", "#008300",
           "#4a3aa7", "#e34948", "#e87ba4", "#eb6834"]
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e5e5e2", "#fcfcfb"

# fixed colours for the four roles, so every plot reads the same way
C_RETURN, C_OUT_A, C_OUT_B, C_ISO = PALETTE[5], PALETTE[0], PALETTE[1], PALETTE[2]

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE, "font.size": 11,
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.axisbelow": True, "lines.linewidth": 2, "lines.markersize": 6,
    "legend.frameon": False,
})

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")

# matches a design frequency anywhere in a path, e.g. '.../wpd_100GHz/.../x.s3p'
FREQ_RE = re.compile(r"wpd[_-]?(\d+(?:\.\d+)?)\s*GHz", re.IGNORECASE)


def design_freq_ghz(path: str) -> float | None:
    """Pull the divider's design frequency (GHz) out of a file path.

    The frequency is encoded in the directory name (wpd_<N>GHz) rather than the leaf
    filename, since Palace names every run's output file the same, so we search the
    whole path. Returns the number in GHz, or None if no wpd_<N>GHz tag is present.
    """
    m = FREQ_RE.search(path)
    return float(m.group(1)) if m else None


def find_wpd_touchstone(paths, prefer_deembedded=True):
    """Collect one .s3p per divider from the given files/directories.

    combine_snp.py can emit raw, `_dc` and `_deembedded` variants side by side; the
    de-embedded one best represents the divider itself, so it's preferred, then the
    raw file, and the DC-extrapolation helper is dropped. Dividers are keyed by their
    design frequency (from the path) so same-named files in different run directories
    don't collide. Returns a list of (design_freq_ghz, filepath), sorted by frequency.
    """
    files = []
    for p in paths:
        if os.path.isdir(p):
            files += glob(os.path.join(p, "**", "*.s3p"), recursive=True)
        elif os.path.isfile(p):
            files.append(p)
        else:
            print(f"skipping {p!r} (not a file or directory)")

    # rank each candidate; keep the best-ranked file per design frequency
    best: dict[float, tuple[int, str]] = {}
    for f in files:
        fghz = design_freq_ghz(f)
        if fghz is None:
            print(f"skipping {f!r} (no wpd_<N>GHz tag in path)")
            continue
        base = os.path.basename(f)[: -len(".s3p")]
        variant = "raw"
        if base.endswith("_deembedded"):
            variant = "deembedded"
        elif base.endswith("_dc"):
            variant = "dc"
        rank = {"deembedded": 2 if prefer_deembedded else 0, "raw": 1, "dc": 0}[variant]
        if fghz not in best or rank > best[fghz][0]:
            best[fghz] = (rank, f)
    return sorted((fghz, f) for fghz, (_, f) in best.items())


def _freq_index(ntwk: rf.Network, fghz: float | None) -> int:
    """Index of the frequency sample nearest fghz (or the middle sample if None)."""
    if fghz is None:
        return ntwk.frequency.npoints // 2
    return int(np.argmin(np.abs(ntwk.frequency.f - fghz * 1e9)))


def _sdb(ntwk, a, b):
    """|S[a][b]| in dB over frequency (0-based port indices)."""
    return 20 * np.log10(np.abs(ntwk.s[:, a, b]))


def _wrap180(deg):
    """Wrap an angle (or array of angles) in degrees to the range (-180, 180]."""
    return (deg + 180) % 360 - 180


def metrics_at_design(ntwk, fghz):
    """Compute the headline WPD figures of merit at the design frequency.

    Port roles are fixed: 1 = input, 2/3 = outputs. Returns a dict with (all in dB
    unless noted):
        return_loss  - |S11|, lower is better
        isolation    - |S32|, output-output isolation, lower is better (poor without
                       the isolation resistor - see module docstring)
        excess_loss  - -10*log10(|S21|^2 + |S31|^2); 0 dB is a perfect lossless split
        imbalance    - |S21|dB - |S31|dB; 0 dB is a perfectly equal split
        phase_err    - arg(S21) - arg(S31) in degrees, wrapped; the outputs of a
                       Wilkinson are ideally in phase, so 0 is perfect
    """
    i = _freq_index(ntwk, fghz)
    a = ntwk.s[i, 1, 0]  # S21
    b = ntwk.s[i, 2, 0]  # S31
    a_db, b_db = 20 * np.log10(np.abs(a)), 20 * np.log10(np.abs(b))
    phase = _wrap180(np.degrees(np.angle(a) - np.angle(b)))
    return {
        "return_loss": float(_sdb(ntwk, 0, 0)[i]),
        "isolation": float(_sdb(ntwk, 2, 1)[i]),
        "excess_loss": float(-10 * np.log10(np.abs(a) ** 2 + np.abs(b) ** 2)),
        "imbalance": float(a_db - b_db),
        "phase_err": float(phase),
    }


# ---------------------------------------------------------------------------
# per-divider detail plot
# ---------------------------------------------------------------------------
def plot_one(ntwk, fghz, rl_spec):
    """Draw the 3-panel detail figure for one divider and save it to images/.

    Panel 1: |S11|, the two outputs and the output-output isolation vs frequency, with
             -3 dB and -rl_spec dB guide lines and a marker at the design frequency.
    Panel 2: amplitude imbalance (|S21|-|S31|, dB) vs frequency - flatness of the split.
    Panel 3: output phase difference vs frequency against the ideal 0-degree line.
    """
    fg = ntwk.frequency.f / 1e9

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(7.5, 9), sharex=True)

    # --- panel 1: all four magnitudes ---
    ax1.plot(fg, _sdb(ntwk, 0, 0), color=C_RETURN, label="return loss  S11")
    ax1.plot(fg, _sdb(ntwk, 1, 0), color=C_OUT_A, label="output  S21")
    ax1.plot(fg, _sdb(ntwk, 2, 0), color=C_OUT_B, label="output  S31")
    ax1.plot(fg, _sdb(ntwk, 2, 1), color=C_ISO, label="isolation  S32")
    ax1.axhline(-3.01, color=MUTED, ls=":", lw=1)            # ideal 3 dB split
    ax1.axhline(-rl_spec, color=MUTED, ls="--", lw=1)        # match/isolation spec
    ax1.text(fg[0], -3.01, " -3 dB", va="bottom", ha="left", color=MUTED, fontsize=9)
    ax1.set_ylabel("magnitude  (dB)")
    ax1.set_ylim(bottom=max(-40, ax1.get_ylim()[0]))
    ax1.legend(ncol=2, fontsize=9)

    # --- panel 2: amplitude imbalance between the two outputs ---
    imb = _sdb(ntwk, 1, 0) - _sdb(ntwk, 2, 0)
    ax2.plot(fg, imb, color=C_OUT_A)
    ax2.axhline(0, color=MUTED, ls=":", lw=1)
    ax2.set_ylabel("imbalance  |S21|-|S31|  (dB)")

    # --- panel 3: output phase difference (ideally 0 - the outputs are in phase) ---
    dphi = _wrap180(np.degrees(np.angle(ntwk.s[:, 1, 0])
                               - np.angle(ntwk.s[:, 2, 0])))
    ax3.plot(fg, dphi, color=C_OUT_B)
    ax3.axhline(0, color=MUTED, ls="--", lw=1)
    ax3.text(fg[0], 0, " ideal 0 deg", va="bottom", ha="left", color=MUTED, fontsize=9)
    ax3.set_ylabel("phase diff  (deg)")
    ax3.set_xlabel("frequency  (GHz)")

    # mark the design frequency on every panel
    if fghz is not None:
        for ax in (ax1, ax2, ax3):
            ax.axvline(fghz, color=INK, ls="-", lw=0.8, alpha=0.35)
        ax1.text(fghz, ax1.get_ylim()[1], f" design {fghz:g} GHz",
                 va="top", ha="left", color=INK, fontsize=9)

    tag = f"{fghz:g}GHz" if fghz is not None else "unknown"
    fig.suptitle(f"Wilkinson power divider  @ design {tag}", fontsize=14, color=INK)
    fig.tight_layout()
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, f"wpd_{tag}.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


# ---------------------------------------------------------------------------
# summary across all dividers
# ---------------------------------------------------------------------------
def plot_summary(rows, rl_spec):
    """Draw the across-dividers summary (each metric at its own design frequency).

    Left axis gathers the dB metrics (return loss, isolation, excess loss, imbalance)
    vs design frequency; right axis shows the output phase error in degrees, which
    has different units. `rows` is the list of per-divider metric dicts built in main().
    """
    rows = sorted(rows, key=lambda r: r["design_ghz"])
    f = [r["design_ghz"] for r in rows]

    fig, (axl, axr) = plt.subplots(1, 2, figsize=(12, 4.5))

    axl.plot(f, [r["return_loss"] for r in rows], "-o", color=C_RETURN, label="return loss")
    axl.plot(f, [r["isolation"] for r in rows], "-o", color=C_ISO, label="isolation")
    axl.plot(f, [r["excess_loss"] for r in rows], "-o", color=C_OUT_A, label="excess loss")
    axl.plot(f, [r["imbalance"] for r in rows], "-o", color=C_OUT_B, label="amp imbalance")
    axl.axhline(-rl_spec, color=MUTED, ls="--", lw=1)
    axl.set_xlabel("design frequency  (GHz)")
    axl.set_ylabel("(dB)")
    axl.set_title("power metrics at design frequency", fontsize=12, color=INK)
    axl.legend(fontsize=9)

    axr.plot(f, [r["phase_err"] for r in rows], "-o", color=C_OUT_B)
    axr.axhline(0, color=MUTED, ls=":", lw=1)
    axr.set_xlabel("design frequency  (GHz)")
    axr.set_ylabel("phase error from 0 deg  (deg)")
    axr.set_title("output phase balance at design frequency", fontsize=12, color=INK)

    fig.suptitle("Wilkinson power divider performance vs design frequency", fontsize=14, color=INK)
    fig.tight_layout()
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "wpd_summary.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


def dump_summary_csv(rows):
    """Write the per-divider summary metrics to images/wpd_summary.csv."""
    rows = sorted(rows, key=lambda r: r["design_ghz"])
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "wpd_summary.csv")
    cols = ["design_ghz", "return_loss", "isolation", "excess_loss",
            "imbalance", "phase_err"]
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            w.writerow([f"{r[c]:.4f}" for c in cols])
    print(f"wrote {out}")


def main():
    """CLI entry point: discover WPD .s3p files, draw a detail figure per divider,
    and a summary figure + CSV across all of them."""
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    # positional: .s3p files, or directories searched recursively for them
    p.add_argument("paths", nargs="+", help="Touchstone .s3p files or directories")
    # guide line (dB, given as a positive number) drawn for return loss / isolation;
    # purely cosmetic - it doesn't filter anything.
    p.add_argument("--rl-spec", type=float, default=15.0,
                   help="return-loss / isolation guide line in dB (default 15)")
    args = p.parse_args()

    found = find_wpd_touchstone(args.paths)
    if not found:
        sys.exit("no WPD .s3p files found")

    rows = []
    for fghz, path in found:
        ntwk = rf.Network(path)
        if ntwk.nports != 3:
            print(f"skipping {path!r}: expected 3 ports, got {ntwk.nports}")
            continue
        plot_one(ntwk, fghz, args.rl_spec)                  # per-divider detail figure
        m = metrics_at_design(ntwk, fghz)
        rows.append({"design_ghz": fghz if fghz is not None else 0.0, **m})

    if rows:
        plot_summary(rows, args.rl_spec)                    # across-dividers overview
        dump_summary_csv(rows)


if __name__ == "__main__":
    main()

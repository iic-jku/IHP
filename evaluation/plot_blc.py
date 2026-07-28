"""Plot branch-line-coupler (BLC) EM results from Touchstone (.s4p) files.

A branch-line coupler is a 4-port 90-degree hybrid: power fed into the input port
splits equally (-3 dB) between two output ports that are 90 degrees apart in phase,
while the fourth (diagonal) port stays isolated. The four things that tell you whether
a BLC actually works are therefore:

    * coupling / insertion loss - are the two outputs really near -3 dB?
    * return loss  - is the input port well matched (|S11| low)?
    * isolation    - is the isolated port really dead (its |Sx1| low)?
    * quadrature   - is the phase difference between the two outputs ~90 degrees?

This script reads the simulated 4x4 S-parameters (input assumed to be port 1, matching
the port-1 = e1 feed in generate_blc.py) and, rather than hard-coding which physical
port is through / coupled / isolated, classifies them FROM THE DATA at each coupler's
design frequency: of ports 2/3/4, the two with the largest |Sx1| are the outputs and
the smallest is the isolated port. That makes the labelling robust to port-ordering
conventions.

Two kinds of output are written to ./images/:
    * blc_<N>GHz.png  - per coupler: |S| vs f, amplitude imbalance vs f, phase-diff vs f
    * blc_summary.png / .csv - the key metrics for every coupler, at its design frequency

Usage:
    python plot_blc.py gds/blc                 # every .s4p found under gds/blc
    python plot_blc.py a.s4p b.s4p             # specific files
    python plot_blc.py gds/blc --rl-spec 15    # change the return-loss/isolation guide line

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
# style: shared with plot_tline.py - validated CVD-safe palette, recessive grid
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

# matches a design frequency anywhere in a path, e.g. '.../blc_100GHz/.../x.s4p'
FREQ_RE = re.compile(r"blc[_-]?(\d+(?:\.\d+)?)\s*GHz", re.IGNORECASE)


def design_freq_ghz(path: str) -> float | None:
    """Pull the coupler's design frequency (GHz) out of a file path.

    The frequency is encoded in the directory name (blc_<N>GHz) rather than the leaf
    filename, since Palace names every run's output file the same, so we search the
    whole path. Returns the number in GHz, or None if no blc_<N>GHz tag is present.
    """
    m = FREQ_RE.search(path)
    return float(m.group(1)) if m else None


def find_blc_touchstone(paths, prefer_deembedded=True):
    """Collect one .s4p per coupler from the given files/directories.

    combine_snp.py can emit raw, `_dc` and `_deembedded` variants side by side; the
    de-embedded one best represents the coupler itself, so it's preferred, then the
    raw file, and the DC-extrapolation helper is dropped. Couplers are keyed by their
    design frequency (from the path) so same-named files in different run directories
    don't collide. Returns a list of (design_freq_ghz, filepath), sorted by frequency.
    """
    files = []
    for p in paths:
        if os.path.isdir(p):
            files += glob(os.path.join(p, "**", "*.s4p"), recursive=True)
        elif os.path.isfile(p):
            files.append(p)
        else:
            print(f"skipping {p!r} (not a file or directory)")

    # rank each candidate; keep the best-ranked file per design frequency
    best: dict[float, tuple[int, str]] = {}
    for f in files:
        fghz = design_freq_ghz(f)
        if fghz is None:
            print(f"skipping {f!r} (no blc_<N>GHz tag in path)")
            continue
        base = os.path.basename(f)[: -len(".s4p")]
        variant = "raw"
        if base.endswith("_deembedded"):
            variant = "deembedded"
        elif base.endswith("_dc"):
            variant = "dc"
        rank = {"deembedded": 2 if prefer_deembedded else 0, "raw": 1, "dc": 0}[variant]
        if fghz not in best or rank > best[fghz][0]:
            best[fghz] = (rank, f)
    return sorted((fghz, f) for fghz, (_, f) in best.items())


def classify_ports(ntwk: rf.Network, fghz: float | None):
    """Work out which ports are the two outputs and which is isolated.

    Input is assumed to be port 1 (index 0). Looking at |Sx1| for x in {2,3,4} at the
    design frequency (or the band centre if fghz is None), the two largest are the
    output arms and the smallest is the isolated port. Returns
    (out_a_idx, out_b_idx, iso_idx) as 0-based port indices, with the outputs ordered
    by port number for a stable phase-difference sign.
    """
    i = _freq_index(ntwk, fghz)
    trans = {x: np.abs(ntwk.s[i, x, 0]) for x in (1, 2, 3)}  # |S21|,|S31|,|S41|
    iso_idx = min(trans, key=trans.get)                      # weakest -> isolated
    outs = sorted(x for x in (1, 2, 3) if x != iso_idx)      # the other two -> outputs
    return outs[0], outs[1], iso_idx


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


def metrics_at_design(ntwk, fghz, out_a, out_b, iso):
    """Compute the headline BLC figures of merit at the design frequency.

    Returns a dict with (all in dB unless noted):
        return_loss  - |S11|, lower is better
        isolation    - |S(iso)1|, lower is better
        excess_loss  - -10*log10(|Sa1|^2 + |Sb1|^2); 0 dB is a perfect lossless split
        imbalance    - |Sa1|dB - |Sb1|dB; 0 dB is a perfectly equal split
        phase_diff   - |arg(Sa1) - arg(Sb1)| in degrees (should be ~90). The magnitude
                       is used because the sign depends only on which output we call A
                       vs B (arbitrary), whereas |Sa1 - Sb1 phase| = 90 is the real spec.
        phase_err    - phase_diff - 90 in degrees (deviation from ideal quadrature)
    """
    i = _freq_index(ntwk, fghz)
    a = ntwk.s[i, out_a, 0]
    b = ntwk.s[i, out_b, 0]
    a_db, b_db = 20 * np.log10(np.abs(a)), 20 * np.log10(np.abs(b))
    phase = abs(_wrap180(np.degrees(np.angle(a) - np.angle(b))))
    return {
        "return_loss": float(_sdb(ntwk, 0, 0)[i]),
        "isolation": float(_sdb(ntwk, iso, 0)[i]),
        "excess_loss": float(-10 * np.log10(np.abs(a) ** 2 + np.abs(b) ** 2)),
        "imbalance": float(a_db - b_db),
        "phase_diff": float(phase),
        "phase_err": float(phase - 90),
    }


# ---------------------------------------------------------------------------
# per-coupler detail plot
# ---------------------------------------------------------------------------
def plot_one(ntwk, fghz, rl_spec):
    """Draw the 3-panel detail figure for one coupler and save it to images/.

    Panel 1: |S11|, the two outputs and the isolated port vs frequency, with -3 dB and
             -rl_spec dB guide lines and a marker at the design frequency.
    Panel 2: amplitude imbalance (|outA|-|outB|, dB) vs frequency - flatness of the split.
    Panel 3: output phase difference vs frequency against the ideal 90-degree line.
    """
    out_a, out_b, iso = classify_ports(ntwk, fghz)
    fg = ntwk.frequency.f / 1e9

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(7.5, 9), sharex=True)

    # --- panel 1: all four magnitudes ---
    ax1.plot(fg, _sdb(ntwk, 0, 0), color=C_RETURN, label="return loss  S11")
    ax1.plot(fg, _sdb(ntwk, out_a, 0), color=C_OUT_A, label=f"output  S{out_a + 1}1")
    ax1.plot(fg, _sdb(ntwk, out_b, 0), color=C_OUT_B, label=f"output  S{out_b + 1}1")
    ax1.plot(fg, _sdb(ntwk, iso, 0), color=C_ISO, label=f"isolation  S{iso + 1}1")
    ax1.axhline(-3.01, color=MUTED, ls=":", lw=1)            # ideal 3 dB split
    ax1.axhline(-rl_spec, color=MUTED, ls="--", lw=1)        # match/isolation spec
    ax1.text(fg[0], -3.01, " -3 dB", va="bottom", ha="left", color=MUTED, fontsize=9)
    ax1.set_ylabel("magnitude  (dB)")
    ax1.set_ylim(bottom=max(-40, ax1.get_ylim()[0]))
    ax1.legend(ncol=2, fontsize=9)

    # --- panel 2: amplitude imbalance between the two outputs ---
    imb = _sdb(ntwk, out_a, 0) - _sdb(ntwk, out_b, 0)
    ax2.plot(fg, imb, color=C_OUT_A)
    ax2.axhline(0, color=MUTED, ls=":", lw=1)
    ax2.set_ylabel(f"imbalance  |S{out_a + 1}1|-|S{out_b + 1}1|  (dB)")

    # --- panel 3: quadrature phase difference (magnitude; sign is arbitrary, see metrics) ---
    dphi = np.abs(_wrap180(np.degrees(np.angle(ntwk.s[:, out_a, 0])
                                      - np.angle(ntwk.s[:, out_b, 0]))))
    ax3.plot(fg, dphi, color=C_OUT_B)
    ax3.axhline(90, color=MUTED, ls="--", lw=1)
    ax3.text(fg[0], 90, " ideal 90 deg", va="bottom", ha="left", color=MUTED, fontsize=9)
    ax3.set_ylabel("|phase diff|  (deg)")
    ax3.set_xlabel("frequency  (GHz)")

    # mark the design frequency on every panel
    if fghz is not None:
        for ax in (ax1, ax2, ax3):
            ax.axvline(fghz, color=INK, ls="-", lw=0.8, alpha=0.35)
        ax1.text(fghz, ax1.get_ylim()[1], f" design {fghz:g} GHz",
                 va="top", ha="left", color=INK, fontsize=9)

    tag = f"{fghz:g}GHz" if fghz is not None else "unknown"
    fig.suptitle(f"Branch-line coupler  @ design {tag}", fontsize=14, color=INK)
    fig.tight_layout()
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, f"blc_{tag}.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


# ---------------------------------------------------------------------------
# summary across all couplers
# ---------------------------------------------------------------------------
def plot_summary(rows, rl_spec):
    """Draw the across-couplers summary (each metric at its own design frequency).

    Left axis gathers the dB metrics (return loss, isolation, excess loss, imbalance)
    vs design frequency; right axis shows the quadrature phase error in degrees, which
    has different units. `rows` is the list of per-coupler metric dicts built in main().
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
    axr.set_ylabel("phase error from 90 deg  (deg)")
    axr.set_title("quadrature error at design frequency", fontsize=12, color=INK)

    fig.suptitle("Branch-line coupler performance vs design frequency", fontsize=14, color=INK)
    fig.tight_layout()
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "blc_summary.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")


def dump_summary_csv(rows):
    """Write the per-coupler summary metrics to images/blc_summary.csv."""
    rows = sorted(rows, key=lambda r: r["design_ghz"])
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "blc_summary.csv")
    cols = ["design_ghz", "return_loss", "isolation", "excess_loss",
            "imbalance", "phase_diff", "phase_err"]
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            w.writerow([f"{r[c]:.4f}" for c in cols])
    print(f"wrote {out}")


def main():
    """CLI entry point: discover BLC .s4p files, draw a detail figure per coupler,
    and a summary figure + CSV across all of them."""
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    # positional: .s4p files, or directories searched recursively for them
    p.add_argument("paths", nargs="+", help="Touchstone .s4p files or directories")
    # guide line (dB, given as a positive number) drawn for return loss / isolation;
    # a common hybrid spec is 15-20 dB. Purely cosmetic - it doesn't filter anything.
    p.add_argument("--rl-spec", type=float, default=15.0,
                   help="return-loss / isolation guide line in dB (default 15)")
    args = p.parse_args()

    found = find_blc_touchstone(args.paths)
    if not found:
        sys.exit("no BLC .s4p files found")

    rows = []
    for fghz, path in found:
        ntwk = rf.Network(path)
        if ntwk.nports != 4:
            print(f"skipping {path!r}: expected 4 ports, got {ntwk.nports}")
            continue
        plot_one(ntwk, fghz, args.rl_spec)                  # per-coupler detail figure
        out_a, out_b, iso = classify_ports(ntwk, fghz)
        m = metrics_at_design(ntwk, fghz, out_a, out_b, iso)
        rows.append({"design_ghz": fghz if fghz is not None else 0.0, **m})

    if rows:
        plot_summary(rows, args.rl_spec)                    # across-couplers overview
        dump_summary_csv(rows)


if __name__ == "__main__":
    main()

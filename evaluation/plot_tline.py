"""Plot transmission-line EM results from Touchstone (.s2p) files.

Two different extraction methods are used, depending on how many line lengths
are available per (stack, width, frequency) point:

Zc(w): single-line extraction (Eul-Schiek / Bianco)
    The Palace ports are lumped ports referenced to 50 ohm, so the simulator
    returns S-parameters normalised to 50 ohm - not the line's characteristic
    impedance. Because every tline structure is a uniform, symmetric, reciprocal
    2-port, the true characteristic impedance Zc and propagation constant gamma
    are extracted analytically from a single line's 50-ohm S-parameters:

        K  = (S11^2 - S21^2 + 1) / (2*S11)
        G  = K +/- sqrt(K^2 - 1)            # reflection coeff, pick root with |G| <= 1
        Zc = Zref * (1 + G) / (1 - G)       # Zref = 50 ohm

        e^(-gamma*L) = (S11 + S21 - G) / (1 - (S11 + S21)*G)
        loss[dB/mm]  = -20*log10|e^(-gamma*L)| / L_mm

    This removes the 50-ohm reference mismatch, so it is correct even though the
    lines are not 50 ohm. It does NOT remove any parasitic effect of the port
    launch itself (only what combine_snp.py's analytic port de-embedding catches).

loss(w): two-length (multiline) extraction
    Two lines of identical width/stack/frequency but different length (length1,
    length2) are simulated with identical port launches. Converting each to its
    ABCD matrix, T2 . inv(T1) is a similarity transform of the pure line segment
    of length dL = length2 - length1 - so its eigenvalues are e^(+-gamma*dL)
    regardless of whatever the (identical) port launch does. This cancels port
    effects exactly rather than relying on an assumed port model.
    Only the real part (loss) is used from this; the imaginary part (phase/beta)
    wraps every 2*pi*dL and isn't recovered here.

Usage:
    python plot_tline.py z0      gds/tline_z0    [--freq 200] [--eval-freq 150]
    python plot_tline.py z0-freq gds/tline_z0
    python plot_tline.py z0-3d   gds/tline_z0    [--signal topmetal2 --ground metal5]
    python plot_tline.py loss    gds/tline_loss  --freq 200  [--eval-freq 160] [--length1-um 500] [--length2-um 1000]
    python plot_tline.py design  gds/tline_z0 gds/tline_loss  [--freq 200]
    python plot_tline.py sparams file1.s2p file2.s2p ...

Paths may be individual Touchstone files or directories (searched recursively).
Plots (PNG) and the extracted values (CSV, for z0/loss) are written to ./images/.
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

# Backend must be chosen before pyplot is imported. Every subcommand writes its PNG
# regardless of --show, so batch runs take the non-interactive backend and never touch
# the display. When a window IS wanted, pick Tk explicitly: matplotlib's automatic
# search probes GTK/Qt first, and with those bindings half-installed (as they are in
# the IIC-OSIC-TOOLS image) the probe blocks forever instead of failing over.
# Set MPLBACKEND to override either choice.
if "--show" not in sys.argv:
    matplotlib.use("Agg")
elif not os.environ.get("MPLBACKEND"):
    try:
        matplotlib.use("TkAgg")
    except ImportError:
        pass  # no Tk: fall back to matplotlib's own search

from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (registers the '3d' projection)

# ---------------------------------------------------------------------------
# style: recessive grid, thin marks; metal layers coloured with the IHP scheme
# ---------------------------------------------------------------------------
PALETTE = [
    "#2a78d6",
    "#1baf7a",
    "#eda100",
    "#008300",
    "#4a3aa7",
    "#e34948",
    "#e87ba4",
    "#eb6834",
]  # used by the sparams overlay
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e5e5e2", "#fcfcfb"

# stack order (bottom -> top); fixes legend ordering everywhere
LAYER_ORDER = [
    "metal1",
    "metal2",
    "metal3",
    "metal4",
    "metal5",
    "topmetal1",
    "topmetal2",
]

# IHP SG13G2 layer colours, taken from the PDK's KLayout layer properties
# (ihp/klayout/tech/layers.lyp, drawing purpose). Several PDK colours are tuned for
# filled shapes on KLayout's dark canvas and are too pale to read as thin lines on the
# light plot background, so those are darkened here while keeping the same hue.
IHP_LAYER_COLOR = {
    "metal1": "#39bfff",  # PDK #39bfff  blue
    "metal2": "#8a8a99",  # PDK #ccccd9  grey   (darkened)
    "metal3": "#d80000",  # PDK #d80000  red
    "metal4": "#5faa1e",  # PDK #93e837  green  (darkened)
    "metal5": "#b09a1e",  # PDK #dcd146  yellow (darkened)
    "topmetal1": "#9c6b2f",  # PDK #ffe6bf  cream  (darkened to brown, distinct from metal5 gold)
    "topmetal2": "#ff8000",  # PDK #ff8000  orange
}

# how each signal (top) layer is drawn, so ground=colour and signal=line style are
# two independent visual dimensions on the combined plot
SIGNAL_STYLE = {
    "topmetal2": ("-", "o"),  # thick top metal -> solid
    "topmetal1": ("--", "s"),  # thinner top metal -> dashed
}

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "font.size": 11,
        "axes.edgecolor": MUTED,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "axes.axisbelow": True,
        "lines.linewidth": 2,
        "lines.markersize": 6,
        "legend.frameon": False,
    }
)

ZREF = 50.0
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")

MODEL_RE = re.compile(
    r"tline_(?P<sig>[a-z0-9]+)_over_(?P<gnd>[a-z0-9]+)_"
    r"(?:w(?P<w>[0-9.]+)um_)?(?:l(?P<l>[0-9.]+)um_)?(?P<f>[0-9.]+)GHz",
    re.IGNORECASE,
)


def _layer_rank(layer: str) -> int:
    """Sort key placing metal layers in stack order (bottom -> top), unknowns last."""
    return LAYER_ORDER.index(layer) if layer in LAYER_ORDER else 99


def color_for(layer: str) -> str:
    """IHP PDK colour for a metal layer (metal1 blue, metal2 grey, ...); grey fallback."""
    return IHP_LAYER_COLOR.get(layer, MUTED)


def parse_model(name: str) -> dict | None:
    """Pull the stack/width/length/frequency out of a model filename.

    Returns a dict with signal, ground, width (um or None), length (um or None) and
    freq_ghz, or None if the name doesn't match the expected tline_* convention.
    width and length are each optional in the filename, so either may come back None.
    """
    m = MODEL_RE.search(name)
    if not m:
        return None
    d = m.groupdict()
    return {
        "signal": d["sig"].lower(),
        "ground": d["gnd"].lower(),
        "width": float(d["w"]) if d["w"] else None,
        "length": float(d["l"]) if d["l"] else None,
        "freq_ghz": float(d["f"]),
    }


def model_key(path: str) -> str | None:
    """The model identity (the tline_..._GHz tag) from anywhere in a path, or None.

    Runs before the model_basename fix all wrote the same leaf name
    (palace_auto_sim.sNp), so the model's stack/width/length/frequency lives in the
    *directory* path - this pulls the tag out of the full path. Newer runs name the leaf
    after the GDS too, but keying on the path still reads both old and new results.
    """
    m = MODEL_RE.search(path)
    return m.group(0) if m else None


def find_touchstone(paths, suffix, prefer_deembedded=True):
    """Collect .sNp files under the given paths, one variant per model.

    Models are keyed by their path tag (see model_key), not the leaf filename, because
    every Palace run writes the same leaf name into a different model directory. Each
    model can have raw / `_dc` / `_deembedded` variants (that suffix IS on the leaf
    name); the de-embedded file best represents the line itself, so it's preferred,
    then raw, and the DC-extrapolation helper is dropped.
    """
    files = []
    for p in paths:
        if os.path.isdir(p):
            files += glob(os.path.join(p, "**", f"*{suffix}"), recursive=True)
        elif os.path.isfile(p):
            files.append(p)
        else:
            print(f"skipping {p!r} (not a file or directory)")

    by_model: dict[str, tuple[int, str]] = {}
    for f in files:
        key = model_key(f)
        if key is None:
            print(f"skipping {f!r} (no tline_..._GHz tag in path)")
            continue
        leaf = os.path.basename(f)[: -len(suffix)]
        variant = "raw"
        if leaf.endswith("_deembedded"):
            variant = "deembedded"
        elif leaf.endswith("_dc"):
            variant = "dc"
        rank = {"deembedded": 2 if prefer_deembedded else 0, "raw": 1, "dc": 0}[variant]
        if key not in by_model or rank > by_model[key][0]:
            by_model[key] = (rank, f)
    return [f for _, f in sorted(by_model.values(), key=lambda t: t[1])]


def extract_line(ntwk: rf.Network, zref: float = ZREF):
    """Return (Zc, e^{-gamma L}) arrays over frequency from a 2-port line network."""
    n = ntwk.copy()
    n.renormalize(zref)
    S11 = 0.5 * (n.s[:, 0, 0] + n.s[:, 1, 1])  # symmetrise
    S21 = 0.5 * (n.s[:, 1, 0] + n.s[:, 0, 1])  # reciprocity
    with np.errstate(all="ignore"):
        K = (S11**2 - S21**2 + 1) / (2 * S11)
        root = np.sqrt(K**2 - 1)
        G = K + root
        bad = np.abs(G) > 1
        G = np.where(bad, K - root, G)
        z = (S11 + S21 - G) / (1 - (S11 + S21) * G)
        Zc = zref * (1 + G) / (1 - G)
    # near-perfect match (S11 -> 0): formula is singular, but Zc == zref and z == S21
    matched = np.abs(S11) < 1e-6
    Zc = np.where(matched, zref, Zc)
    z = np.where(matched, S21, z)
    return Zc, z


def value_at(ntwk, freq_ghz, length_um):
    """Extract (Zc, loss dB/mm) at the frequency point nearest freq_ghz."""
    Zc, z = extract_line(ntwk)
    i = int(np.argmin(np.abs(ntwk.frequency.f - freq_ghz * 1e9)))
    loss_dbmm = -20 * np.log10(np.abs(z[i])) / (length_um / 1000.0)
    return float(Zc[i].real), float(loss_dbmm)


NP_TO_DB = 20 / np.log(10)  # 8.6859...; converts Np (natural-log amplitude ratio) to dB


def extract_gamma_two_length(n1: rf.Network, n2: rf.Network, dL_um: float):
    """Return gamma [Np/um + j*rad/um] over frequency from two lines differing by dL_um.

    n1, n2 must share the same width/stack/frequency band and differ only in length
    (same port launch on both). Eigenvalues of T2 . inv(T1) (ABCD-matrix ratio) are a
    similarity transform of the pure dL segment, so they equal e^{+-gamma*dL}
    regardless of whatever the (identical) port launch does - this cancels port
    effects exactly, unlike extract_line() above which only removes the 50-ohm
    reference mismatch. Only the real part (loss) is trustworthy here: the
    imaginary part (phase) wraps every 2*pi*dL and isn't recovered.
    """
    M = n2.a @ np.linalg.inv(n1.a)
    eigs = np.linalg.eigvals(M)
    # physical root decays over dL (propagation direction 1 -> 2)
    lam = np.where(np.abs(eigs[:, 0]) < np.abs(eigs[:, 1]), eigs[:, 0], eigs[:, 1])
    return -np.log(lam) / dL_um


def loss_at_two_length(n1, n2, dL_um, freq_ghz):
    """Extract loss (dB/mm) at the frequency point nearest freq_ghz via two-length de-embedding."""
    gamma = extract_gamma_two_length(n1, n2, dL_um)
    i = int(np.argmin(np.abs(n1.frequency.f - freq_ghz * 1e9)))
    loss_dbmm = gamma[i].real * NP_TO_DB * 1000.0  # Np/um -> dB/um -> dB/mm
    return float(loss_dbmm)


# ---------------------------------------------------------------------------
# plots
# ---------------------------------------------------------------------------
def _attach_click_readout(fig, ax, points, unit, xlabel="w", xunit="um"):
    """Click near a data point in the interactive window to label its exact value.

    points: list of (x, y, description) tuples. Nearest-point is found in pixel space
    (so the very different x [um] and y [ohm / dB] scales don't distort 'nearest'),
    and clicking empty space clears the label. xlabel/xunit name the x quantity in
    the readout (default width in um). Only useful with --show; harmless
    otherwise since nothing fires without a live canvas.
    """
    ann = ax.annotate(
        "",
        xy=(0, 0),
        xytext=(12, 12),
        textcoords="offset points",
        bbox=dict(boxstyle="round", fc="#ffffe0", ec=MUTED, alpha=0.95),
        arrowprops=dict(arrowstyle="->", color=MUTED),
        fontsize=9,
        zorder=10,
    )
    ann.set_visible(False)

    def on_click(event):
        if event.inaxes is not ax or event.x is None:
            return
        best = None
        for x, y, desc in points:
            px, py = ax.transData.transform((x, y))
            d2 = (px - event.x) ** 2 + (py - event.y) ** 2
            if best is None or d2 < best[0]:
                best = (d2, x, y, desc)
        if best is None or best[0] > 40**2:  # click too far from any point -> clear
            ann.set_visible(False)
        else:
            _, x, y, desc = best
            ann.xy = (x, y)
            ann.set_text(f"{desc}\n{xlabel} = {x:g} {xunit}\n{y:.3f} {unit}")
            ann.set_visible(True)
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect("button_press_event", on_click)


def _plot_vs_width(entries, ykey, ylabel, title, fname, unit="", show=False):
    """Single-axis plot of <ykey> vs signal width for every stack, on one figure.

    Two independent visual dimensions:
        colour     = ground layer, using the IHP PDK colours (metal1 blue, metal2
                     grey, metal3 red, ...); see IHP_LAYER_COLOR.
        line style = signal layer (TopMetal2 solid, TopMetal1 dashed); see SIGNAL_STYLE.

    So e.g. an orange dashed curve is TopMetal1-signal over ... no - colour is the
    ground, so a blue solid curve is TopMetal2 over Metal1. Two legends spell this out.
    entries: list of dicts with keys signal, ground, width, <ykey>.
    The PNG is always written; when show=True an interactive window also opens with a
    click-to-read readout (unit labels the value in that readout).
    """
    grounds = sorted({e["ground"] for e in entries}, key=_layer_rank)
    signals = sorted({e["signal"] for e in entries}, key=_layer_rank)

    fig, ax = plt.subplots(figsize=(9, 6))
    readout_points = []  # (width, value, "signal / ground") for the interactive readout
    for ground in grounds:
        for signal in signals:
            pts = sorted(
                (e for e in entries if e["ground"] == ground and e["signal"] == signal),
                key=lambda e: e["width"],
            )
            if not pts:
                continue
            ls, mk = SIGNAL_STYLE.get(signal, ("-", "o"))
            xs = [e["width"] for e in pts]
            ys = [e[ykey] for e in pts]
            ax.plot(xs, ys, ls=ls, marker=mk, color=color_for(ground))
            readout_points += [(x, y, f"{signal} / {ground}") for x, y in zip(xs, ys)]

    ax.set_xlabel("signal width  w  (um)")
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=14, color=INK)

    # two legends outside the axes: ground = colour, signal = line style
    ground_handles = [Line2D([], [], color=color_for(g), lw=2, label=g) for g in grounds]
    signal_handles = [
        Line2D(
            [],
            [],
            color=INK,
            lw=2,
            ls=SIGNAL_STYLE.get(s, ("-", "o"))[0],
            marker=SIGNAL_STYLE.get(s, ("-", "o"))[1],
            label=s,
        )
        for s in signals
    ]
    leg_ground = ax.legend(
        handles=ground_handles,
        title="ground (colour)",
        loc="upper left",
        bbox_to_anchor=(1.02, 1.0),
        fontsize=9,
        title_fontsize=9,
    )
    ax.add_artist(leg_ground)
    ax.legend(
        handles=signal_handles,
        title="signal (style)",
        loc="upper left",
        bbox_to_anchor=(1.02, 0.42),
        fontsize=9,
        title_fontsize=9,
    )

    fig.tight_layout()
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, fname)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"wrote {out}")

    if show:
        _attach_click_readout(fig, ax, readout_points, unit)
        print("opening interactive window - click a point to read its value, close to continue")
        plt.show()
    plt.close(fig)
    return out


def _plot_z0_vs_freq(curves, fname, show=False):
    """Plot Zc versus frequency across the whole simulated band, faceted by stack.

    Each .s2p already spans the full band each Palace run swept (e.g. 100-300 GHz), so
    this shows how much Zc drifts with frequency - the dispersion the single-point z0
    plot can't reveal. One subplot per (signal/ground) stack; within a subplot, one
    curve per signal width, coloured on a sequential scale (narrow -> wide). y-axes are
    per-facet (each stack sits at a different impedance level).

    curves: list of dicts with keys signal, ground, width, f_ghz (array), zc (array).
    """
    grounds = sorted({c["ground"] for c in curves}, key=_layer_rank)
    signals = sorted({c["signal"] for c in curves}, key=_layer_rank)
    stacks = [(g, s) for g in grounds for s in signals if any(c["ground"] == g and c["signal"] == s for c in curves)]
    widths = sorted({c["width"] for c in curves})

    # sequential colour per width (narrow = dark, wide = bright)
    cmap = plt.cm.viridis
    wcolor = {w: cmap(i / max(len(widths) - 1, 1)) for i, w in enumerate(widths)}

    ncol = min(3, len(stacks))
    nrow = -(-len(stacks) // ncol)
    fig, axes = plt.subplots(nrow, ncol, figsize=(5.0 * ncol, 3.4 * nrow), squeeze=False, sharex=True)
    for ax, (ground, signal) in zip(axes.flat, stacks):
        sub = sorted(
            (c for c in curves if c["ground"] == ground and c["signal"] == signal),
            key=lambda c: c["width"],
        )
        for c in sub:
            ax.plot(c["f_ghz"], c["zc"], color=wcolor[c["width"]], lw=1.4)
        ax.set_title(f"{signal} / {ground}", fontsize=10, color=INK)
        ax.set_ylabel("Zc  (ohm)")
    for ax in axes.flat[len(stacks) :]:
        ax.set_visible(False)

    fig.suptitle(
        "Characteristic impedance vs frequency (per stack, curve = width)",
        fontsize=14,
        color=INK,
        y=1.0,
    )
    fig.tight_layout(rect=(0, 0.11, 1, 0.99))  # bottom band for x-label + width legend
    fig.text(0.5, 0.065, "frequency  (GHz)", ha="center", color=INK, fontsize=11)
    handles = [Line2D([], [], color=wcolor[w], lw=2, label=f"{w:g}") for w in widths]
    fig.legend(
        handles=handles,
        title="signal width (um)",
        loc="lower center",
        ncol=min(len(widths), 8),
        bbox_to_anchor=(0.5, 0.0),
        fontsize=9,
        title_fontsize=9,
    )

    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, fname)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"wrote {out}")
    if show:
        print("opening interactive window - zoom/pan to inspect, close to continue")
        plt.show()
    plt.close(fig)
    return out


def _plot_z0_surface(curves, signal, ground, fname, show=False):
    """3D surface of Zc over (frequency, width) for one stack.

    Axes follow the requested mapping: x = frequency, y = Zc (impedance), z = width.
    The surface is coloured by Zc so iso-impedance bands are readable independently of
    the viewing angle. Each width's .s2p already spans the full simulated band; the
    widths are interpolated onto a common frequency grid so the (width x frequency)
    mesh is regular.

    curves: list of dicts with keys signal, ground, width, f_ghz (array), zc (array)
    (as produced by _collect_z0_vs_freq); only the requested stack is used.
    """
    sub = [c for c in curves if c["signal"] == signal and c["ground"] == ground]
    if not sub:
        sys.exit(
            f"no z0 data for stack {signal}/{ground} "
            f"(available: {sorted({(c['signal'], c['ground']) for c in curves})})"
        )
    by_w = {}
    for c in sorted(sub, key=lambda c: c["width"]):
        by_w.setdefault(c["width"], c)  # one curve per width (keep first if duplicated)
    widths = sorted(by_w)
    if len(widths) < 2:
        sys.exit(f"need >= 2 widths for a surface, found {len(widths)} for {signal}/{ground}")

    # common frequency grid = overlap of every width's band, then interpolate onto it
    fmin = max(by_w[w]["f_ghz"].min() for w in widths)
    fmax = min(by_w[w]["f_ghz"].max() for w in widths)
    npts = max(len(by_w[w]["f_ghz"]) for w in widths)
    fgrid = np.linspace(fmin, fmax, npts)
    Zc = np.array([np.interp(fgrid, by_w[w]["f_ghz"], by_w[w]["zc"]) for w in widths])  # (M, N)
    F, W = np.meshgrid(fgrid, widths)  # (M, N) each: freq varies along cols, width along rows

    fig = plt.figure(figsize=(9, 7))
    ax = fig.add_subplot(projection="3d")
    norm = plt.Normalize(float(np.nanmin(Zc)), float(np.nanmax(Zc)))
    ax.plot_surface(
        F,
        Zc,
        W,
        facecolors=plt.cm.viridis(norm(Zc)),
        rstride=1,
        cstride=1,
        linewidth=0,
        antialiased=True,
        shade=False,
    )
    ax.set_xlabel("frequency  (GHz)", labelpad=10)
    ax.set_ylabel("Zc  (ohm)", labelpad=10)
    ax.set_zlabel("signal width  w  (um)", labelpad=10)
    ax.set_title(
        f"Characteristic impedance surface  -  {signal} / {ground}",
        fontsize=13,
        color=INK,
    )
    for pane in (ax.xaxis, ax.yaxis, ax.zaxis):
        pane.pane.set_facecolor(SURFACE)
        pane.pane.set_edgecolor(GRID)
    ax.view_init(elev=22, azim=-58)

    m = plt.cm.ScalarMappable(cmap=plt.cm.viridis, norm=norm)
    m.set_array([])
    cb = fig.colorbar(m, ax=ax, shrink=0.6, pad=0.12)
    cb.set_label("Zc  (ohm)")

    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, fname)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"wrote {out}")
    if show:
        print("opening interactive window - drag to rotate, close to continue")
        plt.show()
    plt.close(fig)
    return out


def _plot_design_chart(entries, title, fname, show=False):
    """Zc-vs-loss scatter: one point per (stack, width), the designer's synthesis view.

    x = Zc, y = loss, so 'I need 70 ohm, what's the cheapest way to get it?' is a
    vertical slice: find 70 on the x-axis, take the lowest point. Points of one stack
    are connected in width order (narrow = right/high-Zc end, wide = left/low-Zc end)
    with the endpoint widths labelled; colour = ground layer, marker/line style =
    signal layer, same encoding as the 2D width plots. A dotted grey staircase marks
    the lowest loss achievable per Zc bin (the Pareto envelope).

    entries: list of dicts with keys signal, ground, width, Zc, loss.
    """
    grounds = sorted({e["ground"] for e in entries}, key=_layer_rank)
    signals = sorted({e["signal"] for e in entries}, key=_layer_rank)

    fig, ax = plt.subplots(figsize=(9.5, 6.5))
    readout_points = []
    for ground in grounds:
        for signal in signals:
            pts = sorted(
                (e for e in entries if e["ground"] == ground and e["signal"] == signal),
                key=lambda e: e["width"],
            )
            if not pts:
                continue
            ls, mk = SIGNAL_STYLE.get(signal, ("-", "o"))
            xs = [e["Zc"] for e in pts]
            ys = [e["loss"] for e in pts]
            ax.plot(
                xs,
                ys,
                ls=ls,
                marker=mk,
                color=color_for(ground),
                lw=1.1,
                alpha=0.85,
                markersize=6,
            )
            # label the two ends of the width trajectory (widest first: low-Zc end)
            for e in (pts[0], pts[-1]) if len(pts) > 1 else (pts[0],):
                ax.annotate(
                    f"{e['width']:g}",
                    (e["Zc"], e["loss"]),
                    textcoords="offset points",
                    xytext=(5, 5),
                    fontsize=7,
                    color=MUTED,
                )
            readout_points += [(x, y, f"{signal} / {ground}  w={e['width']:g}um") for x, y, e in zip(xs, ys, pts)]

    # Pareto envelope: lowest loss achievable per Zc bin
    zc_all = np.array([e["Zc"] for e in entries])
    loss_all = np.array([e["loss"] for e in entries])
    bins = np.linspace(zc_all.min(), zc_all.max(), 16)
    idx = np.digitize(zc_all, bins)
    env_x, env_y = [], []
    for b in np.unique(idx):
        sel = idx == b
        i = np.argmin(loss_all[sel])
        env_x.append(zc_all[sel][i])
        env_y.append(loss_all[sel][i])
    order = np.argsort(env_x)
    ax.plot(
        np.array(env_x)[order],
        np.array(env_y)[order],
        ":",
        color=MUTED,
        lw=1.2,
        zorder=1,
        label="lowest loss per Zc",
    )

    ax.set_xlabel("characteristic impedance  Zc  (ohm)")
    ax.set_ylabel("loss  (dB/mm)")
    ax.set_title(title, fontsize=13, color=INK)

    ground_handles = [Line2D([], [], color=color_for(g), lw=2, label=g) for g in grounds]
    signal_handles = [
        Line2D(
            [],
            [],
            color=INK,
            lw=2,
            ls=SIGNAL_STYLE.get(s, ("-", "o"))[0],
            marker=SIGNAL_STYLE.get(s, ("-", "o"))[1],
            label=s,
        )
        for s in signals
    ]
    envelope_handle = [Line2D([], [], color=MUTED, ls=":", lw=1.2, label="lowest loss per Zc")]
    leg_ground = ax.legend(
        handles=ground_handles,
        title="ground (colour)",
        loc="upper left",
        bbox_to_anchor=(1.02, 1.0),
        fontsize=9,
        title_fontsize=9,
    )
    ax.add_artist(leg_ground)
    leg_signal = ax.legend(
        handles=signal_handles,
        title="signal (style)",
        loc="upper left",
        bbox_to_anchor=(1.02, 0.55),
        fontsize=9,
        title_fontsize=9,
    )
    ax.add_artist(leg_signal)
    ax.legend(
        handles=envelope_handle,
        loc="upper left",
        bbox_to_anchor=(1.02, 0.32),
        fontsize=9,
    )

    fig.tight_layout()
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, fname)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"wrote {out}")
    if show:
        _attach_click_readout(fig, ax, readout_points, "dB/mm", xlabel="Zc", xunit="ohm")
        print("opening interactive window - click a point to read its value, close to continue")
        plt.show()
    plt.close(fig)
    return out


def _dump_csv(entries, ykey, fname):
    """Write the extracted values to images/<fname> as CSV (one row per entry),
    sorted by ground/signal/width. ykey is one value column name ('Zc', 'loss')
    or a list of several."""
    ykeys = [ykey] if isinstance(ykey, str) else list(ykey)
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, fname)
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["signal", "ground", "width_um", *ykeys])
        for e in sorted(entries, key=lambda e: (e["ground"], e["signal"], e["width"])):
            w.writerow([e["signal"], e["ground"], e["width"], *(f"{e[k]:.4f}" for k in ykeys)])
    print(f"wrote {out}")


def _collect_width_sweep(paths, freq_ghz, length_um, eval_freq_ghz=None):
    """Build the per-line entry list for the single-line (Z0) sweep.

    Finds every .s2p under paths, keeps those tagged with a width at the requested
    design frequency (freq_ghz, the filename tag), and runs single-line extraction on
    each to get Zc (and loss, though only Zc is used downstream). Returns a list of
    dicts, or exits if nothing matches.

    freq_ghz selects WHICH files (by their _<N>GHz design tag); eval_freq_ghz selects
    WHERE in the simulated band to read the value (each .s2p spans 0.5-1.5x its tag).
    When eval_freq_ghz is None, the value is read at the tag frequency itself. A value
    outside a file's band is clamped to the nearest simulated point, with a warning.

    Uses the RAW (non-de-embedded) files. combine_snp.py's port de-embedding is only
    clean for lossy, non-resonant lines; for the low-loss (TopMetal2) lines the
    resonance instability bleeds into nearby frequencies, so the de-embedded Zc is a
    few ohms erratic even at the design frequency. Raw leaves a small, smooth
    port-inductance offset instead, which is consistent across every stack and matches
    the z0-freq plot. (See _collect_z0_vs_freq for the same reasoning across the band.)
    """
    files = find_touchstone(paths, ".s2p", prefer_deembedded=False)
    if not files:
        sys.exit("no .s2p files found")
    entries = []
    warned_outside_band = False
    for f in files:
        meta = parse_model(f)
        if meta is None or meta["width"] is None:
            continue
        if freq_ghz is not None and abs(meta["freq_ghz"] - freq_ghz) > 1e-6:
            continue
        ntwk = rf.Network(f)
        fghz = eval_freq_ghz if eval_freq_ghz is not None else (freq_ghz if freq_ghz is not None else meta["freq_ghz"])
        band = ntwk.frequency.f / 1e9
        if not warned_outside_band and not (band.min() <= fghz <= band.max()):
            print(
                f"warning: eval frequency {fghz:g} GHz is outside the simulated band "
                f"({band.min():g}-{band.max():g} GHz); using the nearest band edge"
            )
            warned_outside_band = True
        zc, loss = value_at(ntwk, fghz, length_um)
        entries.append({**meta, "Zc": zc, "loss": loss})
    if not entries:
        sys.exit("no files matched the requested frequency")
    return entries


def _collect_z0_vs_freq(paths):
    """Extract Zc across the whole simulated band for every z0 line (not one point).

    Same single-line extraction as _collect_width_sweep, but keeps the full Zc(f) array
    from each file rather than sampling one frequency - that's what lets the vs-freq plot
    show the dispersion. Returns a list of dicts: signal, ground, width, f_ghz, zc.

    Uses the RAW (non-de-embedded) files: combine_snp.py's port de-embedding cascades a
    negative series inductance whose reactance (omega*L) grows with frequency and blows
    up at the low-loss lines' half-wave resonances, adding a large sawtooth artifact
    across a wide band. De-embedding is a narrowband correction - fine for the
    single-point z0(w) plot, wrong for this 3:1 sweep - so it's disabled here."""
    files = find_touchstone(paths, ".s2p", prefer_deembedded=False)
    if not files:
        sys.exit("no .s2p files found")
    curves = []
    for f in files:
        meta = parse_model(f)
        if meta is None or meta["width"] is None:
            continue
        ntwk = rf.Network(f)
        Zc, _ = extract_line(ntwk)
        curves.append(
            {
                "signal": meta["signal"],
                "ground": meta["ground"],
                "width": meta["width"],
                "f_ghz": ntwk.frequency.f / 1e9,
                "zc": Zc.real,
            }
        )
    if not curves:
        sys.exit("no z0 curves extracted (no width-tagged .s2p found)")
    return curves


def _collect_loss_two_length(paths, freq_ghz, length1_um, length2_um, eval_freq_ghz=None):
    """Group .s2p files by (signal, ground, width, freq) and extract loss from the
    length1/length2 pair via two-length de-embedding (see module docstring)."""
    files = find_touchstone(paths, ".s2p")
    if not files:
        sys.exit("no .s2p files found")

    by_key: dict[tuple, dict[float, str]] = {}
    for f in files:
        meta = parse_model(f)
        if meta is None or meta["width"] is None or meta["length"] is None:
            continue
        if freq_ghz is not None and abs(meta["freq_ghz"] - freq_ghz) > 1e-6:
            continue
        key = (meta["signal"], meta["ground"], meta["width"], meta["freq_ghz"])
        by_key.setdefault(key, {})[meta["length"]] = f

    entries = []
    missing = 0
    warned_outside_band = False
    for (signal, ground, width, tag_fghz), lengths in by_key.items():
        if length1_um not in lengths or length2_um not in lengths:
            missing += 1
            continue
        n1 = rf.Network(lengths[length1_um])
        n2 = rf.Network(lengths[length2_um])
        fghz = eval_freq_ghz if eval_freq_ghz is not None else tag_fghz
        band = n1.frequency.f / 1e9
        if not warned_outside_band and not (band.min() <= fghz <= band.max()):
            print(
                f"warning: eval frequency {fghz:g} GHz is outside the simulated band "
                f"({band.min():g}-{band.max():g} GHz); using the nearest band edge"
            )
            warned_outside_band = True
        loss = loss_at_two_length(n1, n2, length2_um - length1_um, fghz)
        entries.append(
            {
                "signal": signal,
                "ground": ground,
                "width": width,
                "freq_ghz": fghz,
                "loss": loss,
            }
        )
    if missing:
        print(
            f"warning: {missing} (stack, width, freq) points missing one of "
            f"length1={length1_um}um / length2={length2_um}um, skipped"
        )
    if not entries:
        sys.exit(f"no files matched both length1={length1_um}um and length2={length2_um}um at the requested frequency")
    return entries


def _collect_design_chart(paths, freq_ghz, length_um, length1_um, length2_um):
    """Join the z0 and loss sweeps into one entry list for the design chart.

    Zc comes from the single-length z0 sweep (files WITHOUT an _l<N>um tag, single-line
    extraction on raw files - see _collect_width_sweep for why raw); loss comes from
    the two-length pairs in the loss sweep (see _collect_loss_two_length). The two are
    joined on (signal, ground, width); pairs present in only one sweep are dropped
    with a note. Pass BOTH sweep directories in paths, e.g.
    `design gds/tline_z0 gds/tline_loss`.
    """
    files = find_touchstone(paths, ".s2p", prefer_deembedded=False)
    if not files:
        sys.exit("no .s2p files found")
    zc_by_key = {}
    for f in files:
        meta = parse_model(f)
        if meta is None or meta["width"] is None or meta["length"] is not None:
            continue  # z0 side: only the single-length (untagged-length) sweep
        if freq_ghz is not None and abs(meta["freq_ghz"] - freq_ghz) > 1e-6:
            continue
        fghz = freq_ghz if freq_ghz is not None else meta["freq_ghz"]
        zc, _ = value_at(rf.Network(f), fghz, length_um)
        zc_by_key[(meta["signal"], meta["ground"], meta["width"])] = zc
    if not zc_by_key:
        sys.exit(
            "no z0-sweep files matched (need width-tagged .s2p WITHOUT a length tag "
            "- did you pass the tline_z0 directory?)"
        )

    loss_entries = _collect_loss_two_length(paths, freq_ghz, length1_um, length2_um)

    entries, unmatched = [], 0
    for e in loss_entries:
        key = (e["signal"], e["ground"], e["width"])
        if key in zc_by_key:
            entries.append({**e, "Zc": zc_by_key[key]})
        else:
            unmatched += 1
    if unmatched:
        print(f"note: {unmatched} loss points had no matching z0 point (skipped)")
    only_z0 = len(zc_by_key) - len(entries)
    if only_z0:
        print(f"note: {only_z0} z0 points had no matching loss pair (skipped)")
    if not entries:
        sys.exit("no (stack, width) points exist in BOTH sweeps - pass both gds/tline_z0 and gds/tline_loss")
    return entries


def cmd_design(args):
    """`design` subcommand: Zc-vs-loss scatter, one point per (stack, width) - the
    synthesis view for picking a stack/width to hit a target impedance at least loss."""
    e = _collect_design_chart(args.paths, args.freq, args.length_um, args.length1_um, args.length2_um)
    tag = f"{args.freq:g}GHz" if args.freq else "designfreq"
    _plot_design_chart(
        e,
        f"Zc vs loss  @ {tag}   (point = stack + width, labels = w in um)",
        f"tline_design_{tag}.png",
        show=args.show,
    )
    _dump_csv(e, ["Zc", "loss"], f"tline_design_{tag}.csv")


def cmd_z0(args):
    """`z0` subcommand: extract Zc(w) via single-line extraction and write the
    PNG + CSV for the requested frequency (and open an interactive window if --show).

    --freq picks the files (design tag); --eval-freq optionally reads the value at a
    different in-band frequency. When they differ, the output name/title carry the
    eval frequency plus a '_from<tag>' marker so a genuine <eval>GHz sweep's plot
    isn't clobbered."""
    e = _collect_width_sweep(args.paths, args.freq, args.length_um, eval_freq_ghz=args.eval_freq)
    eval_f = args.eval_freq if args.eval_freq is not None else args.freq
    tag = f"{eval_f:g}GHz" if eval_f else "designfreq"
    title = f"Characteristic impedance vs width  @ {tag}"
    if args.eval_freq is not None and args.freq and abs(args.eval_freq - args.freq) > 1e-6:
        tag += f"_from{args.freq:g}GHz"
        title += f"  (read from the {args.freq:g}GHz sweep)"
    _plot_vs_width(
        e,
        "Zc",
        "characteristic impedance  Zc  (ohm)",
        title,
        f"tline_z0_{tag}.png",
        unit="ohm",
        show=args.show,
    )
    _dump_csv(e, "Zc", f"tline_z0_{tag}.csv")


def cmd_z0_freq(args):
    """`z0-freq` subcommand: plot Zc across the whole simulated band (per stack, one
    curve per width) to show its frequency dependence; interactive window if --show."""
    curves = _collect_z0_vs_freq(args.paths)
    _plot_z0_vs_freq(curves, "tline_z0_vs_freq.png", show=args.show)


def cmd_z0_3d(args):
    """`z0-3d` subcommand: 3D surface of Zc over (frequency, width) for one stack
    (default TopMetal2 / Metal5); interactive rotatable window if --show."""
    curves = _collect_z0_vs_freq(args.paths)
    _plot_z0_surface(
        curves,
        args.signal,
        args.ground,
        f"tline_z0_3d_{args.signal}_over_{args.ground}.png",
        show=args.show,
    )


def cmd_loss(args):
    """`loss` subcommand: extract loss(w)/mm via two-length de-embedding and write
    the faceted PNG + CSV for the requested frequency."""
    e = _collect_loss_two_length(
        args.paths, args.freq, args.length1_um, args.length2_um, eval_freq_ghz=args.eval_freq
    )
    eval_f = args.eval_freq if args.eval_freq is not None else args.freq
    tag = f"{eval_f:g}GHz" if eval_f else "designfreq"
    title = f"Conductor+dielectric loss vs width  @ {tag}  (two-length de-embedded)"
    if args.eval_freq is not None and args.freq and abs(args.eval_freq - args.freq) > 1e-6:
        tag += f"_from{args.freq:g}GHz"
        title += f"  (read from the {args.freq:g}GHz sweep)"
    _plot_vs_width(
        e,
        "loss",
        "loss  (dB/mm)",
        title,
        f"tline_loss_{tag}.png",
        unit="dB/mm",
        show=args.show,
    )
    _dump_csv(e, "loss", f"tline_loss_{tag}.csv")


def cmd_sparams(args):
    """`sparams` subcommand: overlay raw S21 (solid) and S11 (dashed) magnitude vs
    frequency for every given file on one axis, and write tline_sparams.png.

    Unlike z0/loss this does no extraction - it just plots the S-parameters directly,
    for eyeballing/verification. One colour per file, so keep the file count small.
    """
    files = find_touchstone(args.paths, ".s2p")
    if not files:
        sys.exit("no .s2p files found")
    fig, ax = plt.subplots(figsize=(8, 5))
    for i, f in enumerate(files):
        ntwk = rf.Network(f)
        fghz = ntwk.frequency.f / 1e9
        c = PALETTE[i % len(PALETTE)]
        label = (model_key(f) or os.path.basename(f)[: -len(".s2p")]).replace("tline_", "")
        ax.plot(
            fghz,
            20 * np.log10(np.abs(ntwk.s[:, 1, 0])),
            "-",
            color=c,
            label=f"{label}  S21",
        )
        ax.plot(
            fghz,
            20 * np.log10(np.abs(ntwk.s[:, 0, 0])),
            "--",
            color=c,
            alpha=0.7,
            label=f"{label}  S11",
        )
    ax.set_xlabel("frequency  (GHz)")
    ax.set_ylabel("magnitude  (dB)")
    ax.set_title("S-parameters", fontsize=14, color=INK)
    ax.legend(fontsize=8, ncol=1)
    if len(files) > len(PALETTE):
        print(
            f"warning: {len(files)} files but only {len(PALETTE)} distinct colours; "
            "pass fewer files for a readable plot"
        )
    fig.tight_layout()
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "tline_sparams.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"wrote {out}")


def main():
    """CLI entry point: define the z0/loss/sparams subcommands and dispatch to the
    matching cmd_* handler (see module docstring for the extraction methods)."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    # one subcommand per plot type; `dest="cmd"` records which was chosen, required=True
    # forces the user to pick one instead of running with no command.
    sub = p.add_subparsers(dest="cmd", required=True)

    # --- z0: characteristic impedance Zc vs width, one line per point ---
    sp = sub.add_parser("z0", help="plot Zc(w) faceted by ground layer")
    # positional: one or more .s2p files, or directories that are searched recursively
    # for them. `nargs="+"` means at least one path is required.
    sp.add_argument("paths", nargs="+", help="Touchstone files or directories")
    # which frequency point to read from each swept .s2p file, in GHz. Files carry a
    # whole band; this picks the nearest sample. Must match a frequency you simulated.
    sp.add_argument(
        "--freq",
        type=float,
        default=200.0,
        help="design frequency (GHz): selects files by their _<N>GHz tag; "
        "required if the input mixes frequencies (default 200)",
    )
    # each .s2p spans 0.5-1.5x its design tag, so the value can be read anywhere in
    # that band, not just at the tag itself. Defaults to the tag (--freq).
    sp.add_argument(
        "--eval-freq",
        type=float,
        default=None,
        help="in-band frequency (GHz) to read Zc at; defaults to --freq. "
        "Lets you plot e.g. Zc @ 150 GHz from the 200 GHz sweep",
    )
    # physical length of the simulated line in um; only used to normalise per-mm
    # figures, so it MUST equal the `length` used in generate_tline_z0.py (1000).
    sp.add_argument(
        "--length-um",
        type=float,
        default=1000.0,
        help="line length in um (must match the generator; default 1000)",
    )
    # open an interactive matplotlib window (in addition to writing the PNG) so you can
    # zoom/pan and click points to read exact values. Needs a display/GUI backend.
    sp.add_argument(
        "--show",
        action="store_true",
        help="also open the interactive plot window (click points to read values)",
    )
    sp.set_defaults(func=cmd_z0)  # cmd_z0 runs when this subcommand is selected

    # --- z0-freq: Zc vs FREQUENCY across the whole band, to see its dispersion ---
    sp = sub.add_parser("z0-freq", help="plot Zc vs frequency (per stack, curve per width)")
    sp.add_argument("paths", nargs="+", help="Touchstone files or directories")
    # no --freq here: this uses the entire band each file was simulated over.
    sp.add_argument("--show", action="store_true", help="also open the interactive plot window")
    sp.set_defaults(func=cmd_z0_freq)

    # --- z0-3d: 3D surface Zc(frequency, width) for a single stack ---
    sp = sub.add_parser("z0-3d", help="3D surface of Zc over (frequency, width) for one stack")
    sp.add_argument("paths", nargs="+", help="Touchstone files or directories")
    # which stack to render the surface for (only one stack fits on a 3D surface).
    # defaults to the TopMetal2/Metal5 microstrip.
    sp.add_argument("--signal", default="topmetal2", help="signal (top) layer, default topmetal2")
    sp.add_argument("--ground", default="metal5", help="ground (bottom) layer, default metal5")
    sp.add_argument(
        "--show",
        action="store_true",
        help="also open the interactive plot window (drag to rotate)",
    )
    sp.set_defaults(func=cmd_z0_3d)

    # --- loss: loss(w)/mm via two-length de-embedding (needs two lengths per point) ---
    sp = sub.add_parser(
        "loss",
        help="plot loss(w)/mm faceted by ground layer, via two-length de-embedding",
    )
    sp.add_argument("paths", nargs="+", help="Touchstone files or directories")
    sp.add_argument(
        "--freq",
        type=float,
        default=200.0,
        help="design frequency (GHz) to select/evaluate; required if the input mixes frequencies (default 200)",
    )
    sp.add_argument(
        "--eval-freq",
        type=float,
        default=None,
        help="in-band frequency (GHz) to read loss at; defaults to --freq. "
        "Lets you plot e.g. loss @ 160 GHz from the 200 GHz sweep",
    )
    # the two line lengths (um) that form each de-embedding pair. The method subtracts
    # the shorter from the longer, so both MUST match length1/length2 in
    # generate_tline_loss.py, and dL = length2 - length1 is the segment loss is read over.
    sp.add_argument(
        "--length1-um",
        type=float,
        default=500.0,
        help="shorter line length in um (must match the generator; default 500)",
    )
    sp.add_argument(
        "--length2-um",
        type=float,
        default=1000.0,
        help="longer line length in um (must match the generator; default 1000)",
    )
    sp.add_argument(
        "--show",
        action="store_true",
        help="also open the interactive plot window (click points to read values)",
    )
    sp.set_defaults(func=cmd_loss)  # cmd_loss runs when this subcommand is selected

    # --- design: Zc-vs-loss scatter joining the z0 and loss sweeps ---
    sp = sub.add_parser("design", help="Zc-vs-loss design chart, one point per (stack, width)")
    # needs BOTH sweep directories: Zc comes from tline_z0, loss from tline_loss.
    sp.add_argument("paths", nargs="+", help="both sweep dirs, e.g. gds/tline_z0 gds/tline_loss")
    sp.add_argument(
        "--freq",
        type=float,
        default=200.0,
        help="design frequency (GHz): selects files by their _<N>GHz tag (default 200)",
    )
    sp.add_argument(
        "--length-um",
        type=float,
        default=1000.0,
        help="z0-sweep line length in um (must match generate_tline_z0.py; default 1000)",
    )
    sp.add_argument(
        "--length1-um",
        type=float,
        default=500.0,
        help="shorter loss line length in um (must match generate_tline_loss.py; default 500)",
    )
    sp.add_argument(
        "--length2-um",
        type=float,
        default=1000.0,
        help="longer loss line length in um (must match generate_tline_loss.py; default 1000)",
    )
    sp.add_argument(
        "--show",
        action="store_true",
        help="also open the interactive plot window (click points to read values)",
    )
    sp.set_defaults(func=cmd_design)

    # --- sparams: raw S21/S11 vs frequency, no extraction ---
    sp = sub.add_parser("sparams", help="overlay S21/S11 vs frequency for the given files")
    # here paths are usually a handful of specific files (one colour each), not a
    # whole directory - there's no --freq/--length because nothing is extracted.
    sp.add_argument("paths", nargs="+", help="Touchstone files or directories")
    sp.set_defaults(func=cmd_sparams)  # cmd_sparams runs when this subcommand is selected

    args = p.parse_args()  # parse argv; argparse errors out here on bad/missing input
    args.func(args)  # call the cmd_* handler wired up by set_defaults above


if __name__ == "__main__":
    main()

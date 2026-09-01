"""Capacitor components for IHP PDK."""

import os
import sys

pdk_root = os.environ.get("PDK_ROOT", "/foss/pdks")
sys.path.append(f"{pdk_root}/ihp-sg13g2/libs.tech/klayout/python")
sys.path.append(f"{pdk_root}/ihp-sg13g2/libs.tech/klayout/python/pycell4klayout-api/source/python/")

from typing import Literal

import gdsfactory as gf
from sg13g2_pycell_lib.ihp.cmim_code import cmim as cmimIHP
from sg13g2_pycell_lib.ihp.cmomf_code import cmomf as cmomfIHP
from sg13g2_pycell_lib.ihp.cmomi_code import cmomi as cmomiIHP
from sg13g2_pycell_lib.ihp.geometry import GridFix
from sg13g2_pycell_lib.ihp.rfcmim_code import rfcmim as rfcmimIHP
from sg13g2_pycell_lib.ihp.SVaricap_code import SVaricap as SVaricapIHP
from sg13g2_pycell_lib.ihp.utility_functions import CbCapCalc, eng_string_to_float

from .. import tech
from .utils import *


def _resolve_cap(cell: str, width, length, C) -> tuple[float, float, float]:
    """Given at most two of (width, length, C), derive the rest with IHP's CbCapCalc.

    The PyCell layout code only reads w and l (its C parameter is display-only,
    recomputed from w/l in setupParams), so the solving the GUI's Calculate
    field triggers has to happen here - using the same CbCapCalc modes the GUI
    callback calls ('w', 'l', 'lw', 'C').

    Args:
        cell: Technology cell name for parameter lookup ('cmim', 'rfcmim').
        width: Width in micrometers, or None to derive it.
        length: Length in micrometers, or None to derive it.
        C: Capacitance in farads, or None to derive it from the geometry.
            A dimension omitted alongside another dimension falls back to the
            technology default size (`<cell>_defLW`).

    Returns:
        (width_um, length_um, C_farads), consistent with each other.

    Raises:
        ValueError: If all three are given, or a dimension is outside the
            technology limits (`<cell>_minLW` .. `<cell>_maxLW`).
    """
    if width is not None and length is not None and C is not None:
        raise ValueError(f"{cell}: give at most two of width, length, C - the third is derived")

    # CbCapCalc signature: (calc, c, l, w, cell); lengths in metres
    if C is None:
        default = eng_string_to_float(tech.techParams[f"{cell}_defLW"]) * 1e6
        width = default if width is None else width
        length = default if length is None else length
        C = CbCapCalc("C", 0, length * 1e-6, width * 1e-6, cell)
    elif width is None and length is None:
        width = length = CbCapCalc("lw", C, 0, 0, cell) * 1e6
    elif width is None:
        width = CbCapCalc("w", C, length * 1e-6, 0, cell) * 1e6
    else:
        length = CbCapCalc("l", C, 0, width * 1e-6, cell) * 1e6

    lo = eng_string_to_float(tech.techParams[f"{cell}_minLW"]) * 1e6
    hi = eng_string_to_float(tech.techParams[f"{cell}_maxLW"]) * 1e6
    for name, value in (("width", width), ("length", length)):
        if not lo <= value <= hi:
            raise ValueError(f"{cell}: {name}={value:.4g}um is outside [{lo:.4g}, {hi:.4g}]um")
    c_lo = eng_string_to_float(tech.techParams[f"{cell}_minC"])
    c_hi = eng_string_to_float(tech.techParams[f"{cell}_maxC"])
    if not c_lo <= C <= c_hi:
        raise ValueError(f"{cell}: C={C * 1e15:.4g}fF is outside [{c_lo * 1e15:.4g}, {c_hi * 1e15:.4g}]fF")

    return width, length, C


@gf.cell
def cmim(
    width: float | None = None,
    length: float | None = None,
    C: float | None = None,
    guardRingType: Literal["none", "psub", "nwell"] = "none",
    guardRingDistance: float = 1,
) -> gf.Component:
    """Create a MIM (Metal-Insulator-Metal) capacitor.

    This function generates a layout cell for a MIM capacitor with optional
    guard rings. The capacitor dimensions and the spacing to the guard ring
    can be customized.

    Give any two of width, length and C (or fewer - missing dimensions fall
    back to the technology default size) and the remaining one is derived
    with IHP's CbCapCalc, like the Calculate field in the PCell dialog:

        cmim(width=10, length=10)   # C follows from the geometry
        cmim(C=1e-12, length=10)    # width follows from C and length
        cmim(C=1e-12)               # square capacitor of that value

    The realised capacitance is reported as `component.info['C']`.

    Args:
        width: Width of the capacitor in micrometers. Derived when omitted.
        length: Length of the capacitor in micrometers. Derived when omitted.
        C: Capacitance in farads. Derived from the geometry when omitted.
        guardRingType: Type of guard ring to include. Options:
            - 'none': No guard ring.
            - 'psub': P-substrate guard ring surrounding the capacitor.
            - 'nwell': N-well guard ring surrounding the capacitor.
        guardRingDistance: Spacing between the capacitor body and the guard ring, in micrometers.

    Returns:
        gdsfactory.Component: The generated MIM capacitor layout.

    Raises:
        ValueError: If width, length and C are all given, or a dimension
            (given or derived from C) is outside the technology limits.
    """
    width, length, C = _resolve_cap("cmim", width, length, C)

    params = {
        "cdf_version": tech.techParams["CDFVersion"],  # not read by IHP code
        "Display": "Selected",  # not read by IHP code
        "Calculate": "w&l",  # only read by the GUI callback, inert here
        "C": C,  # display-only: the PyCell recomputes C from w/l
        "model": tech.techParams["cmim_model"],  # not read by IHP code
        "w": width * 1e-6,  # um to m
        "l": length * 1e-6,  # um to m
        "Cspec": tech_num("cmim_caspec"),  # specific capacitance, not read by IHP code
        "Wmin": tech_num("cmim_minLW"),  # not read by IHP code
        "Lmin": tech_num("cmim_minLW"),  # not read by IHP code
        "Cmax": tech_num("cmim_maxC"),  # not read by IHP code
        "ic": "",  # not read by IHP code
        "m": 1,  # Multiplier, not read by IHP code
        "trise": "",  # not read by IHP code
        "guardRingType": guardRingType,
        "guardRingDistance": guardRingDistance * 1e-6,
    }

    c = generate_gf_from_ihp(cell_name="cmim", cell_params=params, function_name=cmimIHP())

    # add ports to the component
    # no pin layers for cmim, so we use drawing layers
    gf.add_ports.add_ports_from_boxes(
        c,
        pin_layer=(tech.LAYER.Metal5drawing),
        port_type="electrical",
        ports_on_short_side=True,
    )
    c.ports["e1"].name = "B"
    try:
        gf.add_ports.add_ports_from_boxes(
            c,
            pin_layer=(tech.LAYER.TopMetal1drawing),
            port_type="electrical",
            ports_on_short_side=True,
            auto_rename_ports=False,
        )
        c.ports["e1"].name = "T"
    except ValueError:
        # gdsfactory >= 9.45 refuses to register a port that geometrically
        # coincides with an existing one (the concentric MIM plates share the
        # same center). Derive the top port from the TopMetal1 plate box, the
        # same result the regular inference produces.
        lay = gf.get_layer(tech.LAYER.TopMetal1drawing)
        bb = c.get_boxes(layer=lay)[0].bbox()
        snap = 2 * gf.kcl.dbu  # port widths must be even DBU multiples
        w = round(min(bb.right - bb.left, bb.top - bb.bottom) / snap) * snap
        c.add_port(
            name="T",
            center=((bb.left + bb.right) / 2, (bb.bottom + bb.top) / 2),
            width=w,
            orientation=c.ports["B"].orientation,
            layer=lay,
            port_type="electrical",
        )
    c.ports["B"].orientation = 0
    c.ports["T"].orientation = 180
    c.info["C"] = C

    return c


@gf.cell
def rfcmim(
    width: float | None = None,
    length: float | None = None,
    C: float | None = None,
    feed_width: float = 3,
) -> gf.Component:
    """Create an RF MIM (Metal-Insulator-Metal) capacitor with optimized layout.

    This function generates a layout for an RF MIM capacitor with a feed
    line. Give any two of width, length and C (or fewer - missing dimensions
    fall back to the technology default size) and the remaining one is
    derived with IHP's CbCapCalc, like the Calculate field in the PCell
    dialog. The realised capacitance is reported as `component.info['C']`.

    Args:
        width: Width of the capacitor in micrometers. Derived when omitted.
        length: Length of the capacitor in micrometers. Derived when omitted.
        C: Capacitance in farads. Derived from the geometry when omitted.
        feed_width: Width of the feed line connecting to the capacitor, in micrometers.

    Returns:
        gdsfactory.Component: The generated RF MIM capacitor layout.

    Raises:
        ValueError: If width, length and C are all given, or a dimension
            (given or derived from C) is outside the technology limits.
    """
    width, length, C = _resolve_cap("rfcmim", width, length, C)

    params = {
        "cdf_version": tech.techParams["CDFVersion"],  # not declared in KLayout, ignored
        "Display": "Selected",  # not declared in KLayout, ignored
        "Calculate": "C",  # only read by the GUI callback, inert here
        "C": C,  # display-only: the PyCell recomputes C from w/l
        "model": tech.techParams["rfcmim_model"],  # not read by IHP code
        "w": width * 1e-6,  # um to m
        "l": length * 1e-6,  # um to m
        "wfeed": feed_width * 1e-6,
        "Cspec": tech_num("rfcmim_caspec"),  # specific capacitance, not read by IHP code
        "Wmin": tech_num("rfcmim_minLW"),  # not read by IHP code
        "Lmin": tech_num("rfcmim_minLW"),  # not read by IHP code
        "Cmax": tech_num("rfcmim_maxC"),  # not read by IHP code
        "ic": "",  # not declared in KLayout, ignored
        "m": 1,  # Multiplier, not declared in KLayout, ignored
        "trise": "",  # not declared in KLayout, ignored
    }

    c = generate_gf_from_ihp(cell_name="rfcmim", cell_params=params, function_name=rfcmimIHP())

    # add ports to the component
    gf.add_ports.add_ports_from_boxes(
        c,
        pin_layer=(tech.LAYER.Metal5pin),
        port_type="electrical",
        ports_on_short_side=False,
        auto_rename_ports=False,
    )
    c.ports["e1"].name = "MINUS"
    gf.add_ports.add_ports_from_boxes(
        c,
        pin_layer=(tech.LAYER.TopMetal1pin),
        port_type="electrical",
        ports_on_short_side=False,
        auto_rename_ports=False,
    )
    c.ports["e1"].name = "PLUS"
    gf.add_ports.add_ports_from_boxes(
        c,
        pin_layer=(tech.LAYER.Metal1pin),
        port_type="electrical",
        ports_on_short_side=True,
        auto_rename_ports=False,
    )
    c.ports["e1"].name = "TIE"
    c.info["C"] = C

    return c


def _check_mom(cell, width, length, mmin, mmax):
    """Validate MoM sizing and metal stack against the PCell limits.

    Mirrors the guards the PCell dialog applies: the w/l RangeConstraints
    (2..100um, identical in both cells) only bite in the GUI, and both PCells
    silently raise mmax to mmin when it is given lower. Neither runs in this
    scripted flow, so the limits are enforced here instead.

    Args:
        cell: Technology cell name ('cmomf', 'cmomi').
        width: Y extent in micrometers.
        length: X extent in micrometers.
        mmin: Bottom metal of the stack.
        mmax: Top metal of the stack.

    Raises:
        ValueError: If a value is outside the limits, or mmax is below mmin.
    """
    top = cmomfIHP.METAL_MAX  # Metal5; both devices share the thin-metal stack
    check_limits(
        cell,
        [
            ("width", width, 2, 100, "um"),
            ("length", length, 2, 100, "um"),
            ("mmin", mmin, 1, top, ""),
            ("mmax", mmax, 1, top, ""),
        ],
    )
    if mmax < mmin:
        raise ValueError(f"{cell}: mmax={mmax} is below mmin={mmin} (the PCell would silently clamp it)")


@gf.cell
def cmomf(
    width: float = 5.0,
    length: float = 5.0,
    mmin: int = 1,
    mmax: int = 5,
    subblock: bool = False,
) -> gf.Component:
    """Create a fringe (cross-fingered) MoM capacitor.

    Every metal from mmin to mmax carries a comb of fingers whose orientation
    alternates from layer to layer, so neither axis is the finger length -
    both extents simply scale the plate area, and the capacitance is
    continuous in width and length. The sibling `cmomi` is interdigitated
    instead, quantises both extents to its unit cell, and models a different
    capacitance for the same footprint (5x5um on Metal1..Metal5 gives ~39.8fF
    here against ~26.2fF there), so the two are not interchangeable.

    TopMetal1 and TopMetal2 are excluded by design, the thick top metals being
    practically useless as capacitor plates.

    The density behind `component.info['C']` is a simulation-derived fit
    rather than foundry silicon data, carries no corner or mismatch spread,
    and the Metal4 to Metal5 step is extrapolated. Treat the value as a design
    estimate.

    Args:
        width: Y extent in micrometers, 2..100.
        length: X extent in micrometers, 2..100.
        mmin: Bottom metal of the stack, 1 (Metal1) .. 5 (Metal5).
        mmax: Top metal of the stack, 1 (Metal1) .. 5 (Metal5).
        subblock: Add a PWell block for substrate isolation under the device.

    Returns:
        gdsfactory.Component: The generated MoM fringe capacitor, with ports
        'PLUS' (left edge) and 'MINUS' (top edge) on the mmax metal, and the
        modelled capacitance in farads as `component.info['C']`.

    Raises:
        ValueError: If an extent or metal level is outside the limits, or
            mmax is below mmin.
    """
    _check_mom("cmomf", width, length, mmin, mmax)

    params = {
        "model": "cap_cmomf",  # not read by IHP code
        "w": width * 1e-6,  # um to m, Y extent
        "l": length * 1e-6,  # um to m, X extent
        "mmin": mmin,
        "mmax": mmax,
        "subblock": int(subblock),
    }

    c = generate_gf_from_ihp(cell_name="cmomf", cell_params=params, function_name=cmomfIHP())

    # add ports to the component
    # both pins are on the mmax metal, so they are told apart by position:
    # add_ports_from_boxes enumerates the boxes in klayout order, which is not
    # positional, so sort by x - PLUS hugs the left edge, MINUS the top edge.
    pin_layer = getattr(tech.LAYER, f"Metal{mmax}pin")
    gf.add_ports.add_ports_from_boxes(
        c,
        pin_layer=pin_layer,
        port_type="electrical",
        ports_on_short_side=True,
        auto_rename_ports=False,
    )
    plus, minus = sorted(c.ports, key=lambda p: p.center[0])
    plus.name = "PLUS"
    minus.name = "MINUS"
    c.ports["PLUS"].orientation = 180
    c.ports["MINUS"].orientation = 90

    # same expression as the painted C label and cap_cmomf.va: the density for
    # the stack times the extents AFTER they are snapped to the 5nm grid
    c.info["C"] = cmomfIHP.areacap(mmin, mmax) * GridFix(length) * GridFix(width) * 1e-15

    return c


@gf.cell
def cmomi(
    width: float = 5.0,
    length: float = 5.0,
    mmin: int = 1,
    mmax: int = 5,
    feed: Literal["double", "same", "none"] = "double",
    subblock: bool = False,
) -> gf.Component:
    """Create an interdigitated MoM capacitor.

    Brick-staggered teeth tile a 0.84 x 0.89um unit cell across every metal
    from mmin to mmax, so the drawn device floors the request: length to a
    multiple of 0.84um and width to a multiple of 0.89um. The sibling `cmomf`
    is a cross-fingered fringe cap, is continuous in width and length, and
    models a different capacitance for the same footprint (5x5um on
    Metal1..Metal5 gives ~26.2fF here against ~39.8fF there), so the two are
    not interchangeable.

    TopMetal1 and TopMetal2 are excluded by design, the thick top metals being
    practically useless as capacitor plates.

    The feed topology is part of the electrical model, not just the drawing:

        - 'double': opposite-side feed, PLUS pad left and MINUS pad right.
          The reference configuration, and the only one a single-metal stack
          can use.
        - 'same': single-side feed, the two pads stacked on adjacent metals at
          one centre. The plate overlap adds a larger feed capacitance than
          'double'. Needs mmax > mmin.
        - 'none': bare array with no feed routing. NOT a standalone
          two-terminal device - the finger pairs are separate nets and it
          extracts as a partial cap. Only useful when supplying external feed
          routing.

    Args:
        width: Requested Y extent in micrometers, 2..100. Floored to a
            multiple of 0.89um.
        length: Requested X extent in micrometers, 2..100. Floored to a
            multiple of 0.84um.
        mmin: Bottom metal of the stack, 1 (Metal1) .. 5 (Metal5).
        mmax: Top metal of the stack, 1 (Metal1) .. 5 (Metal5).
        feed: Feed topology, 'double', 'same' or 'none'.
        subblock: Add a PWell block for substrate isolation under the device.

    Returns:
        gdsfactory.Component: The generated interdigitated MoM capacitor, with
        ports 'PLUS' and 'MINUS', and the modelled capacitance in farads as
        `component.info['C']`.

    Raises:
        ValueError: If an extent or metal level is outside the limits, mmax is
            below mmin, or feed='same' is asked of a single-metal stack.
    """
    _check_mom("cmomi", width, length, mmin, mmax)
    if feed == "same" and mmax == mmin:
        raise ValueError(
            "cmomi: feed='same' stacks the two pads on adjacent metals and needs mmax > mmin; "
            "use feed='double' for a single-metal stack"
        )

    C = cmomiIHP._model_C_fF(length, width, mmin, mmax, feed) * 1e-15
    Fx, Fy = cmomiIHP._footprint_um(length, width, feed)

    params = {
        "w": width * 1e-6,  # um to m, requested Y extent
        "l": length * 1e-6,  # um to m, requested X extent
        "mmin": mmin,
        "mmax": mmax,
        "feed": feed,
        "subblock": subblock,
        "Calculate": "C",  # only read by the GUI callback, inert here
        "C": C,  # display-only: the PyCell recomputes C from the geometry
        "sep": "",  # dialog separator, not read by IHP code
        "Fx": Fx * 1e-6,  # display-only footprint, recomputed by the PyCell
        "Fy": Fy * 1e-6,  # display-only footprint, recomputed by the PyCell
        "model": "cap_cmomi",  # not read by IHP code
    }

    c = generate_gf_from_ihp(cell_name="cmomi", cell_params=params, function_name=cmomiIHP())

    # add ports to the component
    top_layer = getattr(tech.LAYER, f"Metal{mmax}pin")
    if feed == "same":
        # the two pads are stacked at one centre on adjacent metals, so they
        # are told apart by layer rather than by position
        gf.add_ports.add_ports_from_boxes(
            c,
            pin_layer=top_layer,
            port_type="electrical",
            ports_on_short_side=True,
            auto_rename_ports=False,
        )
        c.ports["e1"].name = "PLUS"
        # gdsfactory >= 9.45 refuses to register a port that geometrically
        # coincides with an existing one, the same way it does for the
        # concentric MIM plates above. Derive the sub-metal port from its pin
        # box, the same result the regular inference produces.
        lay = gf.get_layer(getattr(tech.LAYER, f"Metal{mmax - 1}pin"))
        bb = c.get_boxes(layer=lay)[0].bbox()
        snap = 2 * gf.kcl.dbu  # port widths must be even DBU multiples
        w = round(min(bb.right - bb.left, bb.top - bb.bottom) / snap) * snap
        c.add_port(
            name="MINUS",
            center=((bb.left + bb.right) / 2, (bb.bottom + bb.top) / 2),
            width=w,
            orientation=180,
            layer=lay,
            port_type="electrical",
        )
        c.ports["PLUS"].orientation = 180
    else:
        # 'double' feeds from opposite sides and 'none' pins the outer bars at
        # opposite corners; either way both pins are on the mmax metal and the
        # klayout box order is not positional, so sort by x
        gf.add_ports.add_ports_from_boxes(
            c,
            pin_layer=top_layer,
            port_type="electrical",
            ports_on_short_side=True,
            auto_rename_ports=False,
        )
        plus, minus = sorted(c.ports, key=lambda p: p.center[0])
        plus.name = "PLUS"
        minus.name = "MINUS"
        c.ports["PLUS"].orientation = 180
        c.ports["MINUS"].orientation = 0

    c.info["C"] = C

    return c


@gf.cell
def svaricap(
    width: Literal["3.74u", "9.74u"] = "9.74u",
    length: Literal["0.3u", "0.8u"] = "0.8u",
    Nx: int = 1,
    guardRingType: Literal["none", "nwell"] = "none",
    guardRingDistance: float = 1,
) -> gf.Component:
    """Create a MOS varicap (variable capacitor) layout.

    This function generates a parametric MOS varicap with optional n-well
    guard rings. The device geometry and number of fingers can be customized.

    Args:
        width: Width of the varicap. Must be one of: '3.74u', '9.74u'.
        length: Length of the varicap. Must be one of: '0.3u', '0.8u'.
        Nx: Number of fingers for the varicap.
        guardRingType: Type of guard ring to include. Options:
            - 'none': No guard ring.
            - 'nwell': N-well guard ring.
        guardRingDistance: Spacing between the varicap body and the guard ring, in micrometers.

    Returns:
        gdsfactory.Component: The generated varicap layout.
    """

    params = {
        "cdf_version": tech.techParams["CDFVersion"],  # not declared in KLayout, ignored
        "Display": "Selected",  # not declared in KLayout, ignored
        "model": tech.techParams["SVaricap_model"],  # not read by IHP code
        "w": width,  # eng-format string, e.g. "9.74u"
        "l": length,  # eng-format string, e.g. "0.8u"
        "Nx": Nx,
        "bn": "sub!",  # not read by IHP code
        "trise": "",  # not declared in KLayout, ignored
        "guardRingType": guardRingType,
        "guardRingDistance": guardRingDistance * 1e-6,
    }

    c = generate_gf_from_ihp(cell_name="svaricap", cell_params=params, function_name=SVaricapIHP())

    # add ports to the component
    gf.add_ports.add_ports_from_boxes(
        c,
        pin_layer=(tech.LAYER.Metal1pin),
        port_type="electrical",
        ports_on_short_side=True,
    )
    c.ports["e1"].orientation = 90
    c.ports["e2"].orientation = 270
    c.ports["e3"].orientation = 180

    return c

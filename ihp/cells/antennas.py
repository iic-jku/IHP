"""Antenna components for IHP PDK."""

import os
import sys

pdk_root = os.environ.get("PDK_ROOT", "/foss/pdks")
sys.path.append(f"{pdk_root}/ihp-sg13g2/libs.tech/klayout/python")
sys.path.append(
    f"{pdk_root}/ihp-sg13g2/libs.tech/klayout/python/pycell4klayout-api/source/python/"
)

from typing import Literal

import gdsfactory as gf
from sg13g2_pycell_lib.ihp.dantenna_code import dantenna as dantennaIHP
from sg13g2_pycell_lib.ihp.dpantenna_code import dpantenna as dpantennaIHP
from sg13g2_pycell_lib.ihp.utility_functions import CbDiodeCalc

from .. import tech
from .utils import *


def _resolve_diode(cell, width, length, area):
    """Given at most two of (width, length, area), derive the rest with IHP's
    CbDiodeCalc, like the Calculate field in the PCell dialog.

    Args:
        cell: Technology cell name ('dantenna', 'dpantenna').
        width: Diode width in micrometers, or None to derive it.
        length: Diode length in micrometers, or None to derive it.
        area: Junction area in square metres, or None to derive it. Area
            alone yields a square diode; a dimension omitted alongside
            another dimension falls back to the technology default.

    Returns:
        (width_um, length_um, area_m2, perimeter_m), consistent with each other.

    Raises:
        ValueError: If all three are given, or a dimension (given or derived)
            is outside the technology limits.
    """
    if width is not None and length is not None and area is not None:
        raise ValueError(
            f"{cell}: give at most two of width, length, area - the third is derived"
        )

    # CbDiodeCalc signature: (calc, a, l, w, cell); lengths in metres, area in m^2
    if area is None:
        width = tech_num(f"{cell}_defW", 1e6) if width is None else width
        length = tech_num(f"{cell}_defL", 1e6) if length is None else length
        area = CbDiodeCalc("a", 0, length * 1e-6, width * 1e-6, cell)
    elif width is None and length is None:
        width = length = CbDiodeCalc("wl", area, 0, 0, cell) * 1e6
    elif width is None:
        width = CbDiodeCalc("w", area, length * 1e-6, 0, cell) * 1e6
    else:
        length = CbDiodeCalc("l", area, 0, width * 1e-6, cell) * 1e6

    check_limits(
        cell,
        [
            ("width", width, tech_num(f"{cell}_minW", 1e6), tech_num(f"{cell}_maxW", 1e6), "um"),
            ("length", length, tech_num(f"{cell}_minL", 1e6), tech_num(f"{cell}_maxL", 1e6), "um"),
        ],
    )
    perimeter = CbDiodeCalc("p", 0, length * 1e-6, width * 1e-6, cell)
    return width, length, area, perimeter


@gf.cell
def dantenna(
    width: float | None = None,
    length: float | None = None,
    area: float | None = None,
    addRecLayer: Literal["t", "f"] = "t",
    guardRingType: Literal["none", "psub"] = "none",
    guardRingDistance: float = 1,
) -> gf.Component:
    """Creates a diode antenna (dantenna) structure.

    This function generates a layout cell containing a rectangular antenna
    region with optional recognition layers and guard ring structures.
    Parameters allow customization of the antenna geometry and the type
    and spacing of guard rings.

    Give any two of width, length and area (or fewer - missing dimensions
    fall back to the technology defaults) and the remaining one is derived
    with IHP's CbDiodeCalc, like the Calculate field in the PCell dialog.
    The realised area and perimeter are reported as `component.info['area']`
    / `['perim']` (m^2 / m).

    Args:
        width: Width of the antenna rectangle in microns. Derived when omitted.
        length: Length of the antenna rectangle in microns. Derived when omitted.
        area: Junction area in square metres. Derived when omitted.
        addRecLayer: Whether to add a recognition layer. Valid values:
            - 't': Add recognition layer.
            - 'f': Do not add a recognition layer.
        guardRingType: Type of guard ring to include. Options include:
            - 'none': No guard ring
            - 'psub': P-type guard ring
        guardRingDistance: Spacing between the antenna body and guard ring in microns.

    Returns:
        gdsfactory.Component: The generated antenna component.
    """

    width, length, area, perimeter = _resolve_diode("dantenna", width, length, area)

    params = {
        "cdf_version": tech.techParams["CDFVersion"],  # not read by IHP code
        "Display": "Selected",  # not read by IHP code
        "model": tech.techParams["dantenna_model"],  # not read by IHP code
        "Calculate": "a",  # only read by the GUI callback, inert here
        "w": width * 1e-6,
        "l": length * 1e-6,
        "a": area,
        "p": perimeter,
        "addRecLayer": addRecLayer,
        "bn": "sub!",  # not read by IHP code
        "off": False,  # not read by IHP code
        "Vd": "",  # not read by IHP code
        "perim": "",  # not read by IHP code
        "m": 1,  # not read by IHP code
        "trise": "",  # not read by IHP code
        "region": "",  # not read by IHP code
        "dtemp": "",  # not read by IHP code
        "mode": "No",  # not read by IHP code
        "guardRingType": guardRingType,
        "guardRingDistance": guardRingDistance * 1e-6,
    }

    c = generate_gf_from_ihp(
        cell_name="dantenna", cell_params=params, function_name=dantennaIHP()
    )

    # add ports to the component
    gf.add_ports.add_ports_from_boxes(
        c,
        pin_layer=(tech.LAYER.Metal1drawing),
        port_type="electrical",
        port_name_prefix="t",
        ports_on_short_side=True,
    )
    c.info["area"] = area
    c.info["perim"] = perimeter

    return c


@gf.cell
def dpantenna(
    width: float | None = None,
    length: float | None = None,
    area: float | None = None,
    addRecLayer: Literal["t", "f"] = "t",
    guardRingType: Literal["none", "nwell"] = "none",
    guardRingDistance: float = 1,
) -> gf.Component:
    """Creates a p-type diode antenna (dpantenna) structure.

    Generates a layout cell containing a rectangular antenna region with an
    optional recognition layer and an optional n-well guard ring. Parameters
    allow customization of the antenna geometry and the spacing between the
    antenna body and the surrounding guard ring.

    Give any two of width, length and area (or fewer - missing dimensions
    fall back to the technology defaults) and the remaining one is derived
    with IHP's CbDiodeCalc, like the Calculate field in the PCell dialog.
    The realised area and perimeter are reported as `component.info['area']`
    / `['perim']` (m^2 / m).

    Args:
        width: Width of the antenna rectangle in microns. Derived when omitted.
        length: Length of the antenna rectangle in microns. Derived when omitted.
        area: Junction area in square metres. Derived when omitted.
        addRecLayer: Whether to add a recognition layer. Valid values:
            - 't': Add recognition layer.
            - 'f': Do not add a recognition layer.
        guardRingType: Type of guard ring to include. Valid values:
            - 'none': No guard ring.
            - 'nwell': Surrounding n-well guard ring.
        guardRingDistance: Spacing between the antenna body and the n-well
            guard ring, in microns.

    Returns:
        gdsfactory.Component: The generated antenna component.
    """

    width, length, area, perimeter = _resolve_diode("dpantenna", width, length, area)

    params = {
        "cdf_version": tech.techParams["CDFVersion"],  # not read by IHP code
        "Display": "Selected",  # not read by IHP code
        "model": tech.techParams["dpantenna_model"],  # not read by IHP code
        "Calculate": "a",  # only read by the GUI callback, inert here
        "w": width * 1e-6,
        "l": length * 1e-6,
        "a": area,
        "p": perimeter,
        "addRecLayer": addRecLayer,
        "bn": "sub!",  # not declared in KLayout, ignored
        "off": False,  # not read by IHP code
        "Vd": "",  # not read by IHP code
        "perim": "",  # not read by IHP code
        "m": 1,  # not read by IHP code
        "trise": "",  # not read by IHP code
        "region": "",  # not read by IHP code
        "dtemp": "",  # not read by IHP code
        "mode": "No",  # not read by IHP code
        "guardRingType": guardRingType,
        "guardRingDistance": guardRingDistance * 1e-6,
    }

    c = generate_gf_from_ihp(
        cell_name="dpantenna", cell_params=params, function_name=dpantennaIHP()
    )

    # add ports to the component
    gf.add_ports.add_ports_from_boxes(
        c,
        pin_layer=(tech.LAYER.Metal1drawing),
        port_type="electrical",
        port_name_prefix="DS",
        ports_on_short_side=True,
    )
    c.info["area"] = area
    c.info["perim"] = perimeter

    return c

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

from .. import tech
from .utils import *


@gf.cell
def dantenna(
    width: float = 0.78,
    length: float = 0.78,
    addRecLayer: Literal["t", "f"] = "t",
    guardRingType: Literal["none", "psub"] = "none",
    guardRingDistance: float = 1,
) -> gf.Component:
    """Creates a diode antenna (dantenna) structure.

    This function generates a layout cell containing a rectangular antenna
    region with optional recognition layers and guard ring structures.
    Parameters allow customization of the antenna geometry and the type
    and spacing of guard rings.

    Args:
        width: Width of the antenna rectangle in microns.
        length: Length of the antenna rectangle in microns.
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

    area = width * 1e-6 * length * 1e-6
    perimeter = 2 * (width * 1e-6 + length * 1e-6)
    params = {
        "cdf_version": tech.techParams["CDFVersion"],  # not read by IHP code
        "Display": "Selected",  # not read by IHP code
        "model": tech.techParams["dantenna_model"],  # not read by IHP code
        "Calculate": "a",
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

    return c


@gf.cell
def dpantenna(
    width: float = 0.78,
    length: float = 0.78,
    addRecLayer: Literal["t", "f"] = "t",
    guardRingType: Literal["none", "nwell"] = "none",
    guardRingDistance: float = 1,
) -> gf.Component:
    """Creates a p-type diode antenna (dpantenna) structure.

    Generates a layout cell containing a rectangular antenna region with an
    optional recognition layer and an optional n-well guard ring. Parameters
    allow customization of the antenna geometry and the spacing between the
    antenna body and the surrounding guard ring.

    Args:
        width: Width of the antenna rectangle in microns.
        length: Length of the antenna rectangle in microns.
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

    area = width * 1e-6 * length * 1e-6
    perimeter = 2 * (width * 1e-6 + length * 1e-6)
    params = {
        "cdf_version": tech.techParams["CDFVersion"],  # not read by IHP code
        "Display": "Selected",  # not read by IHP code
        "model": tech.techParams["dpantenna_model"],  # not read by IHP code
        "Calculate": "a",
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

    return c

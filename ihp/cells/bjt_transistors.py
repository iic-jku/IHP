"""Bipolar transistor (HBT) components for IHP PDK."""

import os
import sys

pdk_root = os.environ.get("PDK_ROOT", "/foss/pdks")
sys.path.append(f"{pdk_root}/ihp-sg13g2/libs.tech/klayout/python")
sys.path.append(f"{pdk_root}/ihp-sg13g2/libs.tech/klayout/python/pycell4klayout-api/source/python/")


import gdsfactory as gf
from sg13g2_pycell_lib.ihp.npn13G2_code import npn13G2 as npn13G2IHP
from sg13g2_pycell_lib.ihp.npn13G2L_code import npn13G2L as npn13G2LIHP
from sg13g2_pycell_lib.ihp.npn13G2V_code import npn13G2V as npn13G2VIHP
from sg13g2_pycell_lib.ihp.pnpMPA_code import pnpMPA as pnpMPAIHP

from .. import tech
from .utils import *


@gf.cell
def npn13G2(
    STI: float = 0.44,
    baspolyx: float = 0.3,
    bipwinx: float = 0.07,
    bipwiny: float = 0.1,
    empolyx: float = 0.15,
    empolyy: float = 0.18,
    emitter_length: float = 0.9,
    emitter_width: float = 0.07,
    Nx: int = 1,
    Ny: int = 1,
    text: str = "npn13G2",
    CMetY1: float = 0,
    CMetY2: float = 0,
) -> gf.Component:
    """Returns the IHP npn13G2 BJT transistor as a gdsfactory Component.

    This function generates a parametric layout of the npn13G2 heterojunction
    bipolar transistor (HBT) from the IHP SG13G2 process. Geometry parameters
    control the emitter, base, and implant enclosure sizes, while Nx and Ny
    define the emitter finger array configuration.

    Args:
        STI: STI enclosure around the active device, in microns.
        baspolyx: Base poly enclosure in the x-direction, in microns.
        bipwinx: BIP window enclosure in the x-direction, in microns.
        bipwiny: BIP window enclosure in the y-direction, in microns.
        empolyx: Emitter poly enclosure in the x-direction, in microns.
        empolyy: Emitter poly enclosure in the y-direction, in microns.
        emitter_length: Length of each emitter finger, in microns.
        emitter_width: Width of each emitter finger, in microns.
        Nx: Number of emitter fingers.
        Ny: Number of emitter rows (not used by current IHP PyCell implementation).
        text: Label text to place on the device.
        CMetY1: Optional metal extension on the collector side (lower side), in microns.
        CMetY2: Optional metal extension on the collector side (upper side), in microns.

    Returns:
        gdsfactory.Component: The generated npn13G2 transistor layout.
    """

    # npn13G2_code swaps le/we internally, so the wrapper's emitter_length
    # maps to the technology's WE limits and emitter_width to LE (both are
    # fixed sizes in SG13G2 - only the finger count Nx is really variable)
    check_limits(
        "npn13G2",
        [
            (
                "emitter_length",
                emitter_length,
                tech_num("npn13G2_minWE", 1e6),
                tech_num("npn13G2_maxWE", 1e6),
                "um",
            ),
            (
                "emitter_width",
                emitter_width,
                tech_num("npn13G2_minLE", 1e6),
                tech_num("npn13G2_maxLE", 1e6),
                "um",
            ),
            ("Nx", Nx, tech_num("npn13G2_minNX"), tech_num("npn13G2_maxNX"), ""),
            ("Ny", Ny, tech_num("npn13G2_minNY"), tech_num("npn13G2_maxNY"), ""),
        ],
    )

    params = {
        "cdf_version": tech.techParams["CDFVersion"],  # not read by IHP code
        "Display": "Selected",  # not read by IHP code
        "model": tech.techParams["npn13G2_model"],  # not read by IHP code
        "Nx": Nx,
        "Ny": Ny,
        "le": emitter_length * 1e-6,  # um to m
        "we": emitter_width * 1e-6,  # um to m
        "STI": STI * 1e-6,
        "baspolyx": baspolyx * 1e-6,
        "bipwinx": bipwinx * 1e-6,
        "bipwiny": bipwiny * 1e-6,
        "empolyx": empolyx * 1e-6,
        "empolyy": empolyy * 1e-6,
        "Icmax": 3 * 1e-3,  # hardcoded in IHP PyCell, not in techparams, not read by IHP code
        "Iarea": 1 * 1e-3,  # hardcoded in IHP PyCell, not in techparams, not read by IHP code
        "area": 1,  # hardcoded in IHP PyCell, not in techparams, not read by IHP code
        "bn": "sub!",  # hardcoded in IHP PyCell, not in techparams, not read by IHP code
        "m": 1,  # not read by IHP code
        "trise": "",  # not read by IHP code
        "Text": text,
        "CMetY1": CMetY1 * 1e-6,  # hardcoded in IHP PyCell, not in techparams
        "CMetY2": CMetY2 * 1e-6,  # hardcoded in IHP PyCell, not in techparams
    }

    c = generate_gf_from_ihp(cell_name="npn13G2", cell_params=params, function_name=npn13G2IHP())

    # add ports to the component
    gf.add_ports.add_ports_from_boxes(
        c,
        pin_layer=(tech.LAYER.Metal1pin),
        port_type="electrical",
        ports_on_short_side=True,
    )
    gf.add_ports.add_ports_from_boxes(
        c,
        pin_layer=(tech.LAYER.Metal2pin),
        port_name_prefix="E",
        port_type="electrical",
        ports_on_short_side=False,
    )
    c.ports["e1"].name = "B"
    c.ports["e2"].name = "C"
    c.ports["e3"].name = "E"

    return c


@gf.cell
def npn13G2L(
    Nx: int = 1,
    emitter_length: float = 1,
    emitter_width: float = 0.07,
) -> gf.Component:
    """Returns the IHP npn13G2L BJT transistor as a gdsfactory Component.

    This function generates a layout for the npn13G2L heterojunction
    bipolar transistor (HBT) from the IHP SG13G2 process. The transistor
    geometry is defined by the number of emitter fingers and the dimensions
    of each emitter finger.

    Args:
        Nx: Number of emitter fingers.
        emitter_length: Length of each emitter finger, in microns.
        emitter_width: Width of each emitter finger, in microns.

    Returns:
        gdsfactory.Component: The generated npn13G2L transistor layout.
    """

    # npn13G2L's techparams LE/WE limits are stale copies of npn13G2's and
    # would reject this cell's own defaults, so only Nx is validated
    check_limits(
        "npn13G2L",
        [("Nx", Nx, tech_num("npn13G2L_minNX"), tech_num("npn13G2L_maxNX"), "")],
    )

    params = {
        "cdf_version": tech.techParams["CDFVersion"],  # not read by IHP code
        "Display": "Selected",  # not read by IHP code
        "model": tech.techParams["npn13G2L_model"],  # not read by IHP code
        "Nx": Nx,
        "le": emitter_length * 1e-6,  # um to m
        "we": emitter_width * 1e-6,  # um to m
        "Icmax": 3 * 1e-3,  # hardcoded in IHP PyCell, not in techparams, not read by IHP code
        "Iarea": 1 * 1e-3,  # hardcoded in IHP PyCell, not in techparams, not read by IHP code
        "area": 1,  # hardcoded in IHP PyCell, not in techparams, not read by IHP code
        "bn": "sub!",  # hardcoded in IHP PyCell, not in techparams, not read by IHP code
        "Vbe": "",  # not read by IHP code
        "Vce": "",  # not read by IHP code
        "m": 1,  # not read by IHP code
        "trise": "",  # not read by IHP code
    }

    c = generate_gf_from_ihp(cell_name="npn13G2L", cell_params=params, function_name=npn13G2LIHP())

    # add ports to the component
    gf.add_ports.add_ports_from_boxes(
        c,
        pin_layer=(tech.LAYER.Metal1pin),
        port_type="electrical",
        ports_on_short_side=True,
    )
    gf.add_ports.add_ports_from_boxes(
        c,
        pin_layer=(tech.LAYER.Metal2pin),
        port_name_prefix="E",
        port_type="electrical",
        ports_on_short_side=True,
    )
    c.ports["e1"].name = "B"
    c.ports["e2"].name = "E"
    c.ports["e3"].name = "C"

    return c


@gf.cell
def npn13G2V(
    Nx: int = 1,
    emitter_length: float = 1,
    emitter_width: float = 0.12,
) -> gf.Component:
    """Returns the IHP npn13G2V BJT transistor as a gdsfactory Component.

    This function generates a layout for the npn13G2V heterojunction
    bipolar transistor (HBT) from the IHP SG13G2 process. The transistor
    geometry is defined by the number of emitter fingers and the dimensions
    of each emitter finger.

    Args:
        Nx: Number of emitter fingers. Valid range: [1, 8].
        emitter_length: Length of each emitter finger, in microns.
        emitter_width: Width of each emitter finger, in microns.

    Returns:
        gdsfactory.Component: The generated npn13G2V transistor layout.
    """

    # npn13G2V's techparams LE/WE limits are stale copies of npn13G2's and
    # would reject this cell's own defaults, so only Nx is validated
    check_limits(
        "npn13G2V",
        [("Nx", Nx, tech_num("npn13G2V_minNX"), tech_num("npn13G2V_maxNX"), "")],
    )

    params = {
        "cdf_version": tech.techParams["CDFVersion"],  # not read by IHP code
        "Display": "Selected",  # not read by IHP code
        "model": tech.techParams["npn13G2V_model"],  # not read by IHP code
        "Nx": Nx,
        "le": emitter_length * 1e-6,  # um to m
        "we": emitter_width * 1e-6,  # um to m
        "Icmax": 3 * 1e-3,  # hardcoded in IHP PyCell, not in techparams, not read by IHP code
        "Iarea": 1 * 1e-3,  # hardcoded in IHP PyCell, not in techparams, not read by IHP code
        "area": 1,  # hardcoded in IHP PyCell, not in techparams, not read by IHP code
        "bn": "sub!",  # hardcoded in IHP PyCell, not in techparams, not read by IHP code
        "Vbe": "",  # not read by IHP code
        "Vce": "",  # not read by IHP code
        "m": 1,  # not read by IHP code
        "trise": "",  # not read by IHP code
    }

    c = generate_gf_from_ihp(cell_name="npn13G2V", cell_params=params, function_name=npn13G2VIHP())

    # add ports to the component
    gf.add_ports.add_ports_from_boxes(
        c,
        pin_layer=(tech.LAYER.Metal1pin),
        port_type="electrical",
        ports_on_short_side=True,
    )
    gf.add_ports.add_ports_from_boxes(
        c,
        pin_layer=(tech.LAYER.Metal2pin),
        port_name_prefix="E",
        port_type="electrical",
        ports_on_short_side=True,
    )
    c.ports["e1"].name = "B"
    c.ports["e2"].name = "C"
    c.ports["e3"].name = "E"

    return c


@gf.cell
def pnpMPA(
    width: float = 0.7,
    length: float = 2,
) -> gf.Component:
    """Returns the IHP pnpMPA BJT transistor as a gdsfactory Component.

    This function generates a layout for a PNP transistor using the IHP process.
    The geometry of the transistor is defined by its width and length.

    Args:
        width: Width of the transistor, in microns.
        length: Length of the transistor, in microns.

    Returns:
        gdsfactory.Component: The generated pnpMPA transistor layout.
    """

    check_limits(
        "pnpMPA",
        [
            (
                "width",
                width,
                tech_num("pnpMPA_minW", 1e6),
                tech_num("pnpMPA_maxW", 1e6),
                "um",
            ),
            (
                "length",
                length,
                tech_num("pnpMPA_minL", 1e6),
                tech_num("pnpMPA_maxL", 1e6),
                "um",
            ),
        ],
    )

    area = width * length
    perimeter = 2 * (width + length)
    params = {
        "cdf_version": tech.techParams["CDFVersion"],  # not declared in KLayout, ignored
        "Display": "Selected",  # not declared in KLayout, ignored
        "model": tech.techParams["pnpMPA_model"],  # not read by IHP code
        "Calculate": "a",  # not read by IHP code
        "w": width * 1e-6,  # um to m
        "l": length * 1e-6,  # um to m
        "a": area * 1e-12,  # not read by IHP code
        "p": perimeter * 1e-6,  # not read by IHP code
        "ac": 7.524 * 1e-12,  # not read by IHP code
        "pc": 11.16 * 1e-6,  # not read by IHP code
        "m": 1,  # Multiplier, not read by IHP code
        "region": "",  # not read by IHP code
        "trise": "",  # not read by IHP code
    }

    c = generate_gf_from_ihp(cell_name="pnpMPA", cell_params=params, function_name=pnpMPAIHP())

    # add ports to the component
    gf.add_ports.add_ports_from_boxes(
        c,
        pin_layer=(tech.LAYER.Metal1pin),
        port_type="electrical",
        ports_on_short_side=True,
    )
    c.ports["e1"].name = "TIE"
    c.ports["e2"].name = "PLUS"
    c.ports["e3"].name = "MINUS"

    return c

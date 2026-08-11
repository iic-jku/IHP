"""Resistor components for IHP PDK."""

import os
import sys

pdk_root = os.environ.get("PDK_ROOT", "/foss/pdks")
sys.path.append(f"{pdk_root}/ihp-sg13g2/libs.tech/klayout/python")
sys.path.append(f"{pdk_root}/ihp-sg13g2/libs.tech/klayout/python/pycell4klayout-api/source/python/")

from typing import Literal

import gdsfactory as gf
from sg13g2_pycell_lib.ihp.rhigh_code import rhigh as rhighIHP
from sg13g2_pycell_lib.ihp.rppd_code import rppd as rppdIHP
from sg13g2_pycell_lib.ihp.rsil_code import rsil as rsilIHP
from sg13g2_pycell_lib.ihp.utility_functions import (
    CbResCalc,
    CbResCurrent,
)

from .. import tech
from .utils import *


def _resolve_res(cell, length, width, R, bends, polySpace):
    """Given at most two of (length, width, R), derive the rest with IHP's CbResCalc.

    The PCell layout code draws from w/l (rsil additionally reads R for its
    silicide handling), so the solving the GUI's Calculate field triggers has
    to happen here, using the same CbResCalc modes the GUI callback calls
    ('R', 'l', 'w'). Bends and poly spacing enter the resistance formula and
    are always taken as given.

    Args:
        cell: Technology cell name ('rsil', 'rppd', 'rhigh').
        length: Resistor length in micrometers, or None to derive it.
        width: Resistor width in micrometers, or None to derive it.
        R: Resistance in ohms, or None to derive it from the geometry.
            A dimension omitted alongside R falls back to the technology
            default; with R given and both dimensions omitted, the default
            width is kept and the length is solved.
        bends: Number of bends.
        polySpace: Poly spacing in micrometers.

    Returns:
        (length_um, width_um, R_ohms), consistent with each other.

    Raises:
        ValueError: If all three are given, or a value (given or derived) is
            outside the technology limits.
    """
    if length is not None and width is not None and R is not None:
        raise ValueError(f"{cell}: give at most two of length, width, R - the third is derived")

    # CbResCalc signature: (calc, r, l, w, b, ps, cell); lengths in metres
    ps_m = polySpace * 1e-6
    if R is None:
        width = tech_num(f"{cell}_defW", 1e6) if width is None else width
        length = tech_num(f"{cell}_defL", 1e6) if length is None else length
        R = CbResCalc("R", 0, length * 1e-6, width * 1e-6, bends, ps_m, cell)
    elif length is None:
        width = tech_num(f"{cell}_defW", 1e6) if width is None else width
        length = CbResCalc("l", R, 0, width * 1e-6, bends, ps_m, cell) * 1e6
    else:  # width is None
        width = CbResCalc("w", R, length * 1e-6, 0, bends, ps_m, cell) * 1e6

    check_limits(
        cell,
        [
            (
                "width",
                width,
                tech_num(f"{cell}_minW", 1e6),
                tech_num(f"{cell}_maxW", 1e6),
                "um",
            ),
            (
                "length",
                length,
                tech_num(f"{cell}_minL", 1e6),
                tech_num(f"{cell}_maxL", 1e6),
                "um",
            ),
            (
                "polySpace",
                polySpace,
                tech_num(f"{cell}_minPS", 1e6),
                tech_num(f"{cell}_maxPS", 1e6),
                "um",
            ),
            ("bends", bends, tech_num(f"{cell}_minB"), tech_num(f"{cell}_maxB"), ""),
        ],
    )
    return length, width, R


@gf.cell
def rhigh(
    length: float | None = None,
    width: float | None = None,
    R: float | None = None,
    bends: int = 0,
    polySpace: float = 0.18,
    numberOfSegments: int = 1,
    segmentConnection: Literal["None", "Serial", "Parallel"] = "Serial",
    segmentSpacing: float = 2,
    guardRingType: Literal["none", "nwell", "psub"] = "none",
    guardRingDistance: float = 1,
) -> gf.Component:
    """Create a high-resistance polysilicon resistor layout.

    This function generates a parametric high-resistance polysilicon resistor
    with configurable width, length, bends, and multiple segments. Optional
    guard rings can be added for isolation.

    Give any two of length, width and R (or fewer - missing dimensions fall
    back to the technology defaults) and the remaining one is derived with
    IHP's CbResCalc, like the Calculate field in the PCell dialog:

        rhigh(length=2, width=0.5)   # R follows from the geometry
        rhigh(R=10e3, width=0.5)     # length follows from R and width
        rhigh(R=10e3)                # default width, length solved

    The realised resistance is reported as `component.info['R']`.

    Args:
        length: Length of the resistor in micrometers. Derived when omitted.
        width: Width of the resistor in micrometers. Derived when omitted.
        R: Resistance in ohms. Derived from the geometry when omitted.
        bends: Number of bends in the resistor path.
        polySpace: Spacing between polysilicon lines in micrometers.
        numberOfSegments: Number of resistor segments.
        segmentConnection: Connection type between segments. Options:
            - 'None': Segments not connected.
            - 'Serial': Segments connected in series.
            - 'Parallel': Segments connected in parallel.
        segmentSpacing: Spacing between segments in micrometers.
        guardRingType: Type of guard ring to include. Options:
            - 'none': No guard ring.
            - 'nwell': N-well guard ring.
            - 'psub': P-substrate guard ring.
        guardRingDistance: Distance between the resistor and guard ring in micrometers.

    Returns:
        gdsfactory.Component: The generated high-resistance polysilicon resistor layout.

    Raises:
        ValueError: If length, width and R are all given, or a value (given
            or derived) is outside the technology limits.
    """
    length, width, R = _resolve_res("rhigh", length, width, R, bends, polySpace)

    params = {
        "cdf_version": tech.techParams["CDFVersion"],  # not read by IHP code
        "Display": "Selected",  # not read by IHP code
        "Calculate": "l",  # only read by the GUI callback, inert here
        "Recommendation": "No",
        "model": tech.techParams["rhigh_model"],  # not read by IHP code
        "R": R,  # display-only for rhigh; resolved by _resolve_res
        "w": width * 1e-6,  # um to m
        "l": length * 1e-6,  # um to m
        "b": bends,
        "ps": polySpace * 1e-6,
        "Imax": CbResCurrent(width * 1e-6, tech.techParams["epsilon2"], "rhighG2"),  # only for GUI feedback
        "bn": "sub!",  # not read by IHP code
        "Wmin": tech_num("rhigh_minW", 1e-6),  # not read by IHP code
        "Lmin": tech_num("rhigh_minL", 1e-6),  # not read by IHP code
        "PSmin": tech_num("rhigh_minPS", 1e-6),  # not read by IHP code
        "Rspec": tech.techParams["rhigh_rspec"],  # not read by IHP code
        "Rkspec": tech.techParams["rhigh_rkspec"],  # not read by IHP code
        "Rzspec": tech.techParams["rhigh_rzspec"],  # not read by IHP code
        "tc1": -2300e-6,  # hardcoded in the PCell, not read by IHP code
        "tc2": 2.1e-6,  # hardcoded in the PCell, not read by IHP code
        "PWB": "No",  # not read by IHP code
        "m": 1,  # Multiplier, not read by IHP code
        "trise": 0,  # not read by IHP code
        "NumberOfSegments": numberOfSegments,
        "SegmentConnection": segmentConnection,
        "SegmentSpacing": segmentSpacing * 1e-6,
        "guardRingType": guardRingType,
        "guardRingDistance": guardRingDistance * 1e-6,
    }

    c = generate_gf_from_ihp(cell_name="rhigh", cell_params=params, function_name=rhighIHP())

    # add ports to the component
    gf.add_ports.add_ports_from_boxes(
        c,
        pin_layer=(tech.LAYER.Metal1pin),
        port_type="electrical",
        ports_on_short_side=False,
    )
    c.info["R"] = R

    return c


@gf.cell
def rppd(
    length: float | None = None,
    width: float | None = None,
    R: float | None = None,
    bends: int = 0,
    polySpace: float = 0.18,
    numberOfSegments: int = 1,
    segmentConnection: Literal["None", "Serial", "Parallel"] = "Serial",
    segmentSpacing: float = 2,
    guardRingType: Literal["none", "nwell", "psub"] = "none",
    guardRingDistance: float = 1,
) -> gf.Component:
    """Create a P+ polysilicon resistor (rppd) layout.

    This function generates a parametric P+ polysilicon resistor with
    configurable width, length, bends, and multiple segments. Optional
    guard rings can be added for isolation.

    Give any two of length, width and R (or fewer - missing dimensions fall
    back to the technology defaults) and the remaining one is derived with
    IHP's CbResCalc, like the Calculate field in the PCell dialog. The
    realised resistance is reported as `component.info['R']`.

    Args:
        length: Length of the resistor in micrometers. Derived when omitted.
        width: Width of the resistor in micrometers. Derived when omitted.
        R: Resistance in ohms. Derived from the geometry when omitted.
        bends: Number of bends in the resistor path.
        polySpace: Spacing between polysilicon lines in micrometers.
        numberOfSegments: Number of resistor segments.
        segmentConnection: Connection type between segments. Options:
            - 'None': Segments not connected.
            - 'Serial': Segments connected in series.
            - 'Parallel': Segments connected in parallel.
        segmentSpacing: Spacing between segments in micrometers.
        guardRingType: Type of guard ring to include. Options:
            - 'none': No guard ring.
            - 'nwell': N-well guard ring.
            - 'psub': P-substrate guard ring.
        guardRingDistance: Distance between the resistor and guard ring in micrometers.

    Returns:
        gdsfactory.Component: The generated P+ polysilicon resistor layout.

    Raises:
        ValueError: If length, width and R are all given, or a value (given
            or derived) is outside the technology limits.
    """
    length, width, R = _resolve_res("rppd", length, width, R, bends, polySpace)

    params = {
        "cdf_version": tech.techParams["CDFVersion"],  # not read by IHP code
        "Display": "Selected",  # not read by IHP code
        "Calculate": "l",  # only read by the GUI callback, inert here
        "Recommendation": "No",
        "model": tech.techParams["rppd_model"],  # not read by IHP code
        "R": R,  # display-only for rppd; resolved by _resolve_res
        "w": width * 1e-6,  # um to m
        "l": length * 1e-6,  # um to m
        "b": bends,
        "ps": polySpace * 1e-6,
        "Imax": CbResCurrent(width * 1e-6, tech.techParams["epsilon2"], "rppdG2"),  # only for GUI feedback
        "bn": "sub!",  # not read by IHP code
        "Wmin": tech_num("rppd_minW", 1e-6),  # not read by IHP code
        "Lmin": tech_num("rppd_minL", 1e-6),  # not read by IHP code
        "PSmin": tech_num("rppd_minPS", 1e-6),  # not read by IHP code
        "Rspec": tech.techParams["rppd_rspec"],  # not read by IHP code
        "Rkspec": tech.techParams["rppd_rkspec"],  # not read by IHP code
        "Rzspec": tech.techParams["rppd_rzspec"],  # not read by IHP code
        "tc1": -170e-6,  # hardcoded in the PCell, not read by IHP code
        "tc2": 0.4e-6,  # hardcoded in the PCell, not read by IHP code
        "PWB": "No",  # not read by IHP code
        "m": 1,  # Multiplier, not read by IHP code
        "trise": 0,  # not read by IHP code
        "NumberOfSegments": numberOfSegments,
        "SegmentConnection": segmentConnection,
        "SegmentSpacing": segmentSpacing * 1e-6,
        "guardRingType": guardRingType,
        "guardRingDistance": guardRingDistance * 1e-6,
    }

    c = generate_gf_from_ihp(cell_name="rppd", cell_params=params, function_name=rppdIHP())

    # add ports to the component
    gf.add_ports.add_ports_from_boxes(
        c,
        pin_layer=(tech.LAYER.Metal1pin),
        port_type="electrical",
        ports_on_short_side=False,
    )
    c.info["R"] = R

    return c


@gf.cell
def rsil(
    length: float | None = None,
    width: float | None = None,
    R: float | None = None,
    polySpace: float = 0.18,
    numberOfSegments: int = 1,
    segmentConnection: Literal["None", "Serial", "Parallel"] = "Serial",
    segmentSpacing: float = 2,
    guardRingType: Literal["none", "nwell", "psub"] = "none",
    guardRingDistance: float = 1,
) -> gf.Component:
    """Create a silicided polysilicon resistor (rsil) layout.

    This function generates a parametric silicided polysilicon resistor
    with configurable width, length, target resistance, multiple segments,
    and optional guard rings for isolation.

    Give any two of length, width and R (or fewer - missing dimensions fall
    back to the technology defaults) and the remaining one is derived with
    IHP's CbResCalc, like the Calculate field in the PCell dialog. The
    realised resistance is reported as `component.info['R']`.

    Args:
        length: Length of the resistor in micrometers. Derived when omitted.
        width: Width of the resistor in micrometers. Derived when omitted.
        R: Resistance in ohms. Derived from the geometry when omitted.
        polySpace: Spacing between polysilicon lines in micrometers.
        numberOfSegments: Number of resistor segments.
        segmentConnection: Connection type between segments. Options:
            - 'None': Segments not connected.
            - 'Serial': Segments connected in series.
            - 'Parallel': Segments connected in parallel.
        segmentSpacing: Spacing between segments in micrometers.
        guardRingType: Type of guard ring to include. Options:
            - 'none': No guard ring.
            - 'nwell': N-well guard ring.
            - 'psub': P-substrate guard ring.
        guardRingDistance: Distance between the resistor and guard ring in micrometers.

    Returns:
        gdsfactory.Component: The generated silicided polysilicon resistor layout.

    Raises:
        ValueError: If length, width and R are all given, or a value (given
            or derived) is outside the technology limits.
    """
    # rsil has no bends parameter; CbResCalc still takes b, fixed at 0
    length, width, R = _resolve_res("rsil", length, width, R, 0, polySpace)

    params = {
        "cdf_version": tech.techParams["CDFVersion"],  # not read by IHP code
        "Display": "Selected",  # not read by IHP code
        "Calculate": "l",  # only read by the GUI callback, inert here
        "Recommendation": "No",  # not declared in KLayout, ignored
        "model": tech.techParams["rsil_model"],  # not read by IHP code
        "R": R,  # read by rsil's layout code; resolved by _resolve_res
        "w": width * 1e-6,  # um to m
        "l": length * 1e-6,  # um to m
        "ps": polySpace * 1e-6,
        "Imax": CbResCurrent(width * 1e-6, tech.techParams["epsilon2"], "rsilG2"),  # only for GUI feedback
        "bn": "sub!",  # not read by IHP code
        "Wmin": tech_num("rsil_minW", 1e-6),  # not read by IHP code
        "Lmin": tech_num("rsil_minL", 1e-6),  # not read by IHP code
        "PSmin": tech_num("rsil_minPS", 1e-6),  # not read by IHP code
        "Rspec": tech.techParams["rsil_rspec"],  # not read by IHP code
        "Rkspec": tech.techParams["rsil_rkspec"],  # not read by IHP code
        "Rzspec": tech.techParams["rsil_rzspec"],  # not read by IHP code
        "tc1": -170e-6,  # hardcoded in the PCell, not read by IHP code
        "tc2": 0.4e-6,  # hardcoded in the PCell, not read by IHP code
        "PWB": "No",  # not declared in KLayout, ignored
        "m": 1,  # Multiplier, not read by IHP code
        "trise": 0,  # not read by IHP code
        "NumberOfSegments": numberOfSegments,
        "SegmentConnection": segmentConnection,
        "SegmentSpacing": segmentSpacing * 1e-6,
        "guardRingType": guardRingType,
        "guardRingDistance": guardRingDistance * 1e-6,
    }

    c = generate_gf_from_ihp(cell_name="rsil", cell_params=params, function_name=rsilIHP())

    # add ports to the component
    gf.add_ports.add_ports_from_boxes(
        c,
        pin_layer=(tech.LAYER.Metal1pin),
        port_type="electrical",
        ports_on_short_side=False,
    )
    c.info["R"] = R

    return c


if __name__ == "__main__":
    # Test the components
    c1 = rsil(width=1.0, length=10.0)
    c1.show()

    c2 = rppd(width=0.8, length=20.0)
    c2.show()

    c3 = rhigh(width=1.4, length=50.0)
    c3.show()

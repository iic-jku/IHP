"""Via stack components for IHP PDK."""

import os
import sys

pdk_root = os.environ.get("PDK_ROOT", "/foss/pdks")
sys.path.append(f"{pdk_root}/ihp-sg13g2/libs.tech/klayout/python")
sys.path.append(f"{pdk_root}/ihp-sg13g2/libs.tech/klayout/python/pycell4klayout-api/source/python/")

from typing import Literal

import gdsfactory as gf
from sg13g2_pycell_lib.ihp.via_stack_code import via_stack as via_stackIHP

from .. import tech
from .utils import *


@gf.cell
def via_stack(
    bottom_layer: Literal[
        "Activ",
        "GatPoly",
        "Metal1",
        "Metal2",
        "Metal3",
        "Metal4",
        "Metal5",
        "TopMetal1",
        "TopMetal2",
    ] = "Metal1",
    top_layer: Literal[
        "Activ",
        "GatPoly",
        "Metal1",
        "Metal2",
        "Metal3",
        "Metal4",
        "Metal5",
        "TopMetal1",
        "TopMetal2",
    ] = "Metal2",
    vn_columns: int = 2,
    vn_rows: int = 2,
    vt1_columns: int = 1,
    vt1_rows: int = 1,
    vt2_columns: int = 1,
    vt2_rows: int = 1,
) -> gf.Component:
    """Create a via stack component.

    This function generates a layout for a via stack connecting a bottom
    layer to a top layer. The number of columns and rows for standard vias
    (Via1-Via4) and top vias (TopVia1, TopVia2) can be specified.

    Args:
        bottom_layer: Bottom layer name. Options: 'Activ', 'GatPoly', 'Metal1'-'Metal5', 'TopMetal1', 'TopMetal2'.
        top_layer: Top layer name. Options: 'Activ', 'GatPoly', 'Metal1'-'Metal5', 'TopMetal1', 'TopMetal2'.
        vn_columns: Number of columns for standard vias (Via1-Via4).
        vn_rows: Number of rows for standard vias.
        vt1_columns: Number of columns for TopVia1.
        vt1_rows: Number of rows for TopVia1.
        vt2_columns: Number of columns for TopVia2.
        vt2_rows: Number of rows for TopVia2.

    Returns:
        gdsfactory.Component: The generated via stack layout.
    """

    params = {
        "cdf_version": tech.techParams["CDFVersion"],
        "Display": "Selected",
        "b_layer": bottom_layer,
        "t_layer": top_layer,
        "vn_columns": vn_columns,
        "vn_rows": vn_rows,
        "vt1_columns": vt1_columns,
        "vt1_rows": vt1_rows,
        "vt2_columns": vt2_columns,
        "vt2_rows": vt2_rows,
    }

    c = generate_gf_from_ihp(cell_name="via_stack", cell_params=params, function_name=via_stackIHP())

    # add ports to the component
    layer_map = {  # necessary for mapping layer names to tech layers
        "Activ": tech.LAYER.Activdrawing,
        "GatPoly": tech.LAYER.GatPolydrawing,
        "Metal1": tech.LAYER.Metal1drawing,
        "Metal2": tech.LAYER.Metal2drawing,
        "Metal3": tech.LAYER.Metal3drawing,
        "Metal4": tech.LAYER.Metal4drawing,
        "Metal5": tech.LAYER.Metal5drawing,
        "TopMetal1": tech.LAYER.TopMetal1drawing,
        "TopMetal2": tech.LAYER.TopMetal2drawing,
    }

    gf.add_ports.add_ports_from_boxes(
        c,
        pin_layer=(layer_map[bottom_layer]),
        port_type="electrical",
        ports_on_short_side=False,
    )
    c.ports["e1"].name = "bottom"
    try:
        gf.add_ports.add_ports_from_boxes(
            c,
            pin_layer=(layer_map[top_layer]),
            port_type="electrical",
            ports_on_short_side=False,
            auto_rename_ports=False,
        )
        c.ports["e1"].name = "top"
    except ValueError:
        # gdsfactory >= 9.45 refuses to register a port that geometrically
        # coincides with an existing one. Derive the top port from the
        # top-layer pin box instead (same result as the regular inference).
        lay = gf.get_layer(layer_map[top_layer])
        bb = c.get_boxes(layer=lay)[0].bbox()
        snap = 2 * gf.kcl.dbu  # port widths must be even DBU multiples
        w = round(min(bb.right - bb.left, bb.top - bb.bottom) / snap) * snap
        c.add_port(
            name="top",
            center=((bb.left + bb.right) / 2, (bb.bottom + bb.top) / 2),
            width=w,
            orientation=c.ports["bottom"].orientation,
            layer=lay,
            port_type="electrical",
        )

    return c

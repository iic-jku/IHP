"""Via stack components for IHP PDK. Also includes NoFillerStack."""
#TODO prbably not the right place for NoFillerStack
import sys
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python")
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python/pycell4klayout-api/source/python/")
from sg13g2_pycell_lib.ihp.via_stack_code import via_stack as via_stackIHP
from sg13g2_pycell_lib.ihp.NoFillerStack_code import NoFillerStack as no_filler_stackIHP

from cni.tech import Tech

from cni.dlo import PCellWrapper
import pya
import gdsfactory as gf
from gdsfactory import Component
import os

from functools import partial
from .. import tech


@gf.cell
def via_stack(
    bottom_layer: str = "Metal1",
    top_layer: str = "Metal2",
    vn_columns: int = 2,
    vn_rows: int = 2,
    vt1_columns: int = 1,
    vt1_rows: int = 1,
    vt2_columns: int = 1,
    vt2_rows: int = 1,
) -> Component:
    """Create a via stack test component.

    Args:
        bottom_layer: Bottom metal layer name.
        top_layer: Top metal layer name.
        vn_columns: Number of columns for normal vias (Via1-Via4).
        vn_rows: Number of rows for normal vias.
        vt1_columns: Number of columns for TopVia1.
        vt1_rows: Number of rows for TopVia1.
        vt2_columns: Number of columns for TopVia2.
        vt2_rows: Number of rows for TopVia2.

    Returns:
        Component with via stack test.
    """
    # ----------------------------------------------------------------
    # Step 1: Get the technology object
    # ----------------------------------------------------------------
    tech = Tech.get("SG13_dev")  # Must match the name registered in SG13_Tech

    # ----------------------------------------------------------------
    # Step 2: Create a layout and a cell
    # ----------------------------------------------------------------
    layout = pya.Layout()                # new empty layout
    cell = layout.create_cell("VIA_STACK_1")  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=via_stackIHP(), tech=tech)

    # ----------------------------------------------------------------
    # Step 4: Define parameters
    # ----------------------------------------------------------------
    params = {
        'cdf_version': 8,
        'Display': 'Selected',
        'b_layer': bottom_layer,
        't_layer': top_layer,
        'vn_columns': vn_columns,
        'vn_rows': vn_rows,
        'vt1_columns': vt1_columns,
        'vt1_rows': vt1_rows,
        'vt2_columns': vt2_columns,
        'vt2_rows': vt2_rows
    }

    # Convert params into a list in the order of device.param_decls
    param_values = [params[p.name] for p in device.param_decls]

    # ----------------------------------------------------------------
    # Step 5: Produce the layout
    # ----------------------------------------------------------------
    device.produce(layout=layout,
                layers={},        # can pass layer map if needed
                parameters=param_values,
                cell=cell)

    # ----------------------------------------------------------------
    # Step 6: Save GDS
    # ----------------------------------------------------------------
    layout.write("temp.gds")
    print("✅ Via Stack PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    c = gf.read.import_gds(gdspath="temp.gds")
    
    os.remove("temp.gds")
    return c


@gf.cell
def no_filler_stack(
    width: int = 10,
    length: int = 10,
    noAct: str = "Yes",   # no active filler
    noGP: str = "Yes",    # no GatePoly filler
    noM1: str = "Yes",    # no M1 filler
    noM2: str = "Yes",    # no M2 filler
    noM3: str = "Yes",    # no M3 filler
    noM4: str = "Yes",    # no M4 filler
    noM5: str = "Yes",    # no M5 filler
    noTM1: str = "Yes",   # no TM1 filler
    noTM2: str = "Yes",   # no TM2 filler
) -> Component:
    """Create a NoFiller via stack test component.

    Interface mirrors the provided GUI (except minLW).

    Args:
        bottom_layer: Bottom metal layer name.
        top_layer: Top metal layer name.
        width: device width (string with units, e.g. '100u').
        length: device length (string with units).
        noAct..noTM2: booleans to enable/disable filler for each layer.

    Returns:
        gdsfactory.Component with NoFiller via stack.
    """
    tech = Tech.get("SG13_dev")

    layout = pya.Layout()
    cell = layout.create_cell("NO_FILLER_STACK")

    device = PCellWrapper(impl=no_filler_stackIHP(), tech=tech)

    params = {
        "cdf_version": 8,
        "Display": "Selected",
        "w": width*1e-6,
        "l": length*1e-6,
        "noAct": noAct,
        "noGP": noGP,
        "noM1": noM1,
        "noM2": noM2,
        "noM3": noM3,
        "noM4": noM4,
        "noM5": noM5,
        "noTM1": noTM1,
        "noTM2": noTM2,
    }

    # Convert params into a list in the order of device.param_decls
    param_values = [params.get(p.name, None) for p in device.param_decls]

    device.produce(
        layout=layout,
        layers={},
        parameters=param_values,
        cell=cell,
    )

    layout.write("temp.gds")
    c = gf.read.import_gds(gdspath="temp.gds")
    os.remove("temp.gds")
    return c


if __name__ == "__main__":
    # Test the components
    c = via_stack(bottom_layer="Metal1", top_layer="Metal5")
    c.show()


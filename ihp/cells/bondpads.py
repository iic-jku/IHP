"""Bondpad components for IHP PDK."""

import sys
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python")
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python/pycell4klayout-api/source/python/")
from sg13g2_pycell_lib.ihp.bondpad_code import bondpad as bondpadIHP
from cni.tech import Tech

from cni.dlo import PCellWrapper
import pya
import gdsfactory as gf
from gdsfactory import Component
import os



@gf.cell
def bondpad(
    shape: str = "octagon",
    stack_metals: str = 't',
    fill_metals: str = 'nil',
    flip_chip: str = 'no',
    diameter: float = 80.0,
    top_metal: str = "TM2",
    bottom_metal: str = "3",
    pad_type: str = "bondpad",
    pass_encl: float = 2.1,
    hw_quota: float = 1,
    add_filler_ex: str = 'nil',
) -> Component:
    """Create a bondpad for wire bonding or flip-chip connection.

    Args:
        shape: Shape of the bondpad ("octagon", "square", or "circle").
        stack_metals: Stack all metal layers from bottom to top.
        fill_metals: Add metal fill patterns.
        flip_chip: Enable flip-chip configuration.
        diameter: Diameter or size of the bondpad in micrometers.
        top_metal: Top metal layer name.
        bottom_metal: Bottom metal layer name.

    Returns:
        Component with bondpad layout.
    """
    # ----------------------------------------------------------------
    # Step 1: Get the technology object
    # ----------------------------------------------------------------
    tech = Tech.get("SG13_dev")  # Must match the name registered in SG13_Tech

    # ----------------------------------------------------------------
    # Step 2: Create a layout and a cell
    # ----------------------------------------------------------------
    layout = pya.Layout()                # new empty layout
    cell = layout.create_cell("BONDPAD_1")  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=bondpadIHP(), tech=tech)

    # ----------------------------------------------------------------
    # Step 4: Define parameters
    # ----------------------------------------------------------------
    params = {
        'cdf_version': 8, 
        'model': "bondpad",
        'Display': 'Selected',
        'shape': shape,
        'stack': stack_metals,
        'fill': fill_metals,
        'FlipChip': flip_chip,
        'diameter': diameter*1e-6,
        'hwquota': hw_quota,
        'topMetal': top_metal,
        'bottomMetal': bottom_metal,
        'addFillerEx': add_filler_ex,
        'passEncl': pass_encl*1e-6,
        'padType' : pad_type,
        'padPin': 'PAD'   
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
    print("✅ Bondpad PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    c = gf.read.import_gds(gdspath="temp.gds")
    
    os.remove("temp.gds")
    return c


@gf.cell
def bondpad_array(
    n_pads: int = 4,
    pad_pitch: float = 100.0,
    pad_diameter: float = 68.0,
    shape: str = "octagon",
    stack_metals: bool = True,
) -> Component:
    """Create an array of bondpads.

    Args:
        n_pads: Number of bondpads.
        pad_pitch: Pitch between bondpad centers in micrometers.
        pad_diameter: Diameter of each bondpad in micrometers.
        shape: Shape of the bondpads.
        stack_metals: Stack all metal layers.

    Returns:
        Component with bondpad array.
    """
    c = Component()

    for i in range(n_pads):
        pad = bondpad(
            shape=shape,
            stack_metals=stack_metals,
            diameter=pad_diameter,
        )
        pad_ref = c.add_ref(pad)
        pad_ref.movex(i * pad_pitch)

        

    

    return c


if __name__ == "__main__":
    # Test the components
    c1 = bondpad(shape="octagon")
    c1.show()

    c2 = bondpad(shape="square", flip_chip=True)
    c2.show()

    c3 = bondpad_array(n_pads=6)
    c3.show()

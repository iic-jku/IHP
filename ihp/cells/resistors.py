"""Resistor components for IHP PDK."""
import sys
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python")
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python/pycell4klayout-api/source/python/")
from sg13g2_pycell_lib.ihp.rhigh_code import rhigh as rhighIHP
from sg13g2_pycell_lib.ihp.rppd_code import rppd as rppdIHP
from sg13g2_pycell_lib.ihp.rsil_code import rsil as rsilIHP

from cni.tech import Tech

from cni.dlo import PCellWrapper
import pya
import gdsfactory as gf
from gdsfactory import Component
import os

from functools import partial
from .. import tech


@gf.cell
def rhigh(
    length = 0.96,
    width = 0.5,
    bends = 0,
    poly_space = 0.18    
) -> Component:
    """Create a high-resistance polysilicon resistor.

    Args:
        width: Width of the resistor in micrometers.
        length: Length of the resistor in micrometers.
        #TODO

    Returns:
        Component with high-resistance poly resistor layout.
    """
    
    # ----------------------------------------------------------------
    # Step 1: Get the technology object
    # ----------------------------------------------------------------
    tech = Tech.get("SG13_dev")  # Must match the name registered in SG13_Tech

    # ----------------------------------------------------------------
    # Step 2: Create a layout and a cell
    # ----------------------------------------------------------------
    layout = pya.Layout()                # new empty layout
    cell = layout.create_cell("RHIGH_1")  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=rhighIHP(), tech=tech)

    # ----------------------------------------------------------------
    # Step 4: Define parameters
    # ----------------------------------------------------------------
    params = {
        'cdf_version': 8,
        'Display': 'Selected',
        'Calculate': 'l',
        'Recommendation': "No",
        'model': 'res_high',
        'R': 3.16*1e3,
        'w': width*1e-6,    # Length in μm
        'l': length*1e-6,   # Length in μm
        'b': bends,
        'ps': poly_space,
        'Imax': 0.3*1e-3,
        'bn': "sub!",
        'Wmin': 0.5*1e-6,
        'Lmin': 0.96*1e-6,
        'PSmin': 0.18*1e-6,
        'Rspec': 1300,
        'Rkspec': 0,
        'Rzspec': 80e-6,
        'tc1': -2300e-6,
        'tc2': 2.1*1e-6,
        'PWB': "No",
        'm': 1,      # Multiplier
        'trise': 0,
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
    print("✅ Rhigh PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    c = gf.read.import_gds(gdspath="temp.gds")
    
    os.remove("temp.gds")
    return c

@gf.cell
def rppd(
    length = 0.5,
    width = 0.5,
    bends = 0,
    poly_space = 0.18    
) -> Component:
    """Create a high-resistance polysilicon resistor.

    Args:
        width: Width of the resistor in micrometers.
        length: Length of the resistor in micrometers.
        #TODO

    Returns:
        Component with high-resistance poly resistor layout.
    """
    
    # ----------------------------------------------------------------
    # Step 1: Get the technology object
    # ----------------------------------------------------------------
    tech = Tech.get("SG13_dev")  # Must match the name registered in SG13_Tech

    # ----------------------------------------------------------------
    # Step 2: Create a layout and a cell
    # ----------------------------------------------------------------
    layout = pya.Layout()                # new empty layout
    cell = layout.create_cell("RPPD_1")  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=rppdIHP(), tech=tech)

    # ----------------------------------------------------------------
    # Step 4: Define parameters
    # ----------------------------------------------------------------
    params = {
        'cdf_version': 8,
        'Display': 'Selected',
        'Calculate': 'l',
        'Recommendation': "No",
        'model': 'res_rppd',
        'R': 397,
        'w': width*1e-6,    # Length in μm
        'l': length*1e-6,   # Length in μm
        'b': bends,
        'ps': poly_space,
        'Imax': 0.6*1e-3,
        'bn': "sub!",
        'Wmin': 0.5*1e-6,
        'Lmin': 0.5*1e-6,
        'PSmin': 0.18*1e-6,
        'Rspec': 260,
        'Rkspec': 0,
        'Rzspec': 35*1e-6,
        'tc1': 170*1e-6,
        'tc2': 0.4*1e-6,
        'PWB': "No",
        'm': 1,      # Multiplier
        'trise': 0,
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
    print("✅ Rppd PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    c = gf.read.import_gds(gdspath="temp.gds")
    
    os.remove("temp.gds")
    return c


@gf.cell
def rsil(
    length = 0.5,
    width = 0.5,
    poly_space = 0.18,
    resistance = 24.9 
) -> Component:
    """Create a high-resistance polysilicon resistor.

    Args:
        width: Width of the resistor in micrometers.
        length: Length of the resistor in micrometers.
        #TODO

    Returns:
        Component with high-resistance poly resistor layout.
    """
    
    # ----------------------------------------------------------------
    # Step 1: Get the technology object
    # ----------------------------------------------------------------
    tech = Tech.get("SG13_dev")  # Must match the name registered in SG13_Tech

    # ----------------------------------------------------------------
    # Step 2: Create a layout and a cell
    # ----------------------------------------------------------------
    layout = pya.Layout()                # new empty layout
    cell = layout.create_cell("RSIL_1")  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=rsilIHP(), tech=tech)

    # ----------------------------------------------------------------
    # Step 4: Define parameters
    # ----------------------------------------------------------------
    params = {
        'cdf_version': 8,
        'Display': 'Selected',
        'Calculate': 'l',
        'model': 'res_rppd',
        'R': resistance,
        'w': width*1e-6,    # Length in μm
        'l': length*1e-6,   # Length in μm
        'ps': poly_space,
        'Imax': 1*1e-3,
        'bn': "sub!",
        'Wmin': 0.5*1e-6,
        'Lmin': 0.5*1e-6,
        'PSmin': 0.18*1e-6,
        'Rspec': 7,
        'Rkspec': 0,
        'Rzspec': 4.5e-6,
        'tc1': 3100*1e-6,
        'tc2': 0.3*1e-6,
        'PWB': "No",
        'm': 1,      # Multiplier
        'trise': 0,
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
    print("✅ Rsil PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    c = gf.read.import_gds(gdspath="temp.gds")
    
    os.remove("temp.gds")
    return c


if __name__ == "__main__":
    # Test the components
    c1 = rsil(width=1.0, length=10.0)
    c1.show()

    c2 = rppd(width=0.8, length=20.0)
    c2.show()

    c3 = rhigh(width=1.4, length=50.0)
    c3.show()

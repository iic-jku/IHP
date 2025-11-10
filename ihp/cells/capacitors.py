"""Capacitor components for IHP PDK."""
import sys
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python")
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python/pycell4klayout-api/source/python/")
from sg13g2_pycell_lib.ihp.cmim_code import cmim as cmimIHP
from sg13g2_pycell_lib.ihp.rfcmim_code import rfcmim as rfcmimIHP
from sg13g2_pycell_lib.ihp.SVaricap_code import SVaricap as SVaricapIHP

from cni.tech import Tech

from cni.dlo import PCellWrapper
import pya
import gdsfactory as gf
from gdsfactory import Component
import os

from functools import partial
from .. import tech

@gf.cell
def cmim(
    width = 6.99,
    length = 6.99,
) -> Component:
    """Create a MIM (Metal-Insulator-Metal) capacitor.

    Args:
        width: Width of the capacitor in micrometers.
        length: Length of the capacitor in micrometers.
        #TODO

    Returns:
        Component with MIM capacitor layout.
    """
    
    # ----------------------------------------------------------------
    # Step 1: Get the technology object
    # ----------------------------------------------------------------
    tech = Tech.get("SG13_dev")  # Must match the name registered in SG13_Tech

    # ----------------------------------------------------------------
    # Step 2: Create a layout and a cell
    # ----------------------------------------------------------------
    layout = pya.Layout()                # new empty layout
    cell = layout.create_cell("CMIM_1")  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=cmimIHP(), tech=tech)

    # ----------------------------------------------------------------
    # Step 4: Define parameters
    # ----------------------------------------------------------------
    params = {
        'cdf_version': 8,
        'Display': 'Selected',
        'Calculate': "w&l",
        'model': "cap_cmim",
        'C': 74.6*1e-15,
        'w': width,    # Width in μm
        'l': length,   # Length in μm
        'Cspec': 1.5*1e-3,     # Number of gates
        'Wmin': 1.14*1e-6,
        'Lmin': 1.14*1e-6,
        'Cmax': 8*1e-12,
        'ic': "",
        'm': 1,      # Multiplier
        'trise': ""
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
    print("✅ Cmim PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    c = gf.read.import_gds(gdspath="temp.gds")
    
    os.remove("temp.gds")
    return c


@gf.cell
def rfcmim(
    width: float = 7,
    length: float = 7,
    capacitance: float = 74.8,
    feed_width: float = 3
) -> Component:
    """Create an RF MIM capacitor with optimized layout.

    Args:
        width: Width of the capacitor in micrometers.
        length: Length of the capacitor in micrometers.
        capacitance: Target capacitance in fF (optional).
        #TODO

    Returns:
        Component with RF MIM capacitor layout.
    """
    
    # ----------------------------------------------------------------
    # Step 1: Get the technology object
    # ----------------------------------------------------------------
    tech = Tech.get("SG13_dev")  # Must match the name registered in SG13_Tech

    # ----------------------------------------------------------------
    # Step 2: Create a layout and a cell
    # ----------------------------------------------------------------
    layout = pya.Layout()                # new empty layout
    cell = layout.create_cell("RFCMIM_1")  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=rfcmimIHP(), tech=tech)

    # ----------------------------------------------------------------
    # Step 4: Define parameters
    # ----------------------------------------------------------------
    params = {
        'cdf_version': 8,
        'Display': 'Selected',
        'Calculate': "C",
        'model': "cap_cmim",
        'C': capacitance*1e-15,
        'w': width,    # Width in μm
        'l': length,   # Length in μm
        'wfeed': feed_width*1e-6,
        'Cspec': 1.5*1e-3,     # Number of gates
        'Wmin': 7*1e-6,
        'Lmin': 7*1e-6,
        'Cmax': 1.5*1e-9,
        'ic': "",
        'm': 1,      # Multiplier
        'trise': ""
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
    print("✅ RFCmim PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    c = gf.read.import_gds(gdspath="temp.gds")
    
    os.remove("temp.gds")
    return c


@gf.cell
def svaricap(
    width: float = '9.74u',
    length: float = '0.8u',
    Nx: int = 1,
) -> Component:
    """Create a MOS varicap (variable capacitor).

    Args:
        width: Width of the varicap in micrometers.
        length: Length of the varicap in micrometers.
        nf: Number of fingers.
        model: Device model name.

    Returns:
        Component with varicap layout.
    """
    # ----------------------------------------------------------------
    # Step 1: Get the technology object
    # ----------------------------------------------------------------
    tech = Tech.get("SG13_dev")  # Must match the name registered in SG13_Tech

    # ----------------------------------------------------------------
    # Step 2: Create a layout and a cell
    # ----------------------------------------------------------------
    layout = pya.Layout()                # new empty layout
    cell = layout.create_cell("SVARICAP_1")  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=SVaricapIHP(), tech=tech)

    # ----------------------------------------------------------------
    # Step 4: Define parameters
    # ----------------------------------------------------------------
    params = {
        'cdf_version': 8,
        'Display': 'Selected',
        'model': "cap_cmim",
        'w': width,    # Width in μm
        'l': length,   # Length in μm
        'Nx': Nx,
        'bn': "sub!",      
        'trise': ""
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
    print("✅ SVaricap PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    c = gf.read.import_gds(gdspath="temp.gds")
    
    os.remove("temp.gds")
    return c


if __name__ == "__main__":
    # Test the components
    c1 = cmim(width=10, length=10)
    c1.show()

    c2 = rfcmim(width=20, length=20)
    c2.show()

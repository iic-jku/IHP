import sys
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python")
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python/pycell4klayout-api/source/python/")
from sg13g2_pycell_lib.ihp.inductor2_code import inductor2 as inductor2IHP
from sg13g2_pycell_lib.ihp.inductor3_code import inductor3 as inductor3IHP

from cni.tech import Tech

from cni.dlo import PCellWrapper
import pya
import gdsfactory as gf
from gdsfactory import Component
import os

from functools import partial
from .. import tech


def inductor2(
    model = "inductor2",
    width = 2,
    space = 2.1,
    distance = 15.48,
    resistance = 1,
    inductance = 1,
    num_turns = 1,
    block_qrc = True,
    subE = False,
    L_estim = 33.303,
    R_estim = 577.7,
    Wmin = 2,
    Smin = 2.1,
    Dmin = 15.48,
    min_num_turns = 1,
    merge_Stat = 16
    ) -> Component:
    """
    Args:
    
    Returns:
        gdsfactory Component
    
    
    """
    
    # ----------------------------------------------------------------
    # Step 1: Get the technology object
    # ----------------------------------------------------------------
    tech = Tech.get("SG13_dev")  # Must match the name registered in SG13_Tech

    # ----------------------------------------------------------------
    # Step 2: Create a layout and a cell
    # ----------------------------------------------------------------
    layout = pya.Layout()                # new empty layout
    cell = layout.create_cell("inductor2")  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=inductor2IHP(), tech=tech)

    # ----------------------------------------------------------------
    # Step 4: Define parameters
    # ----------------------------------------------------------------
    params = {
        'cdf_version': 8,
        'Display': 'Selected',
        'model': model,
        'w': width*1e-6,
        's': space*1e-6,
        'd': distance*1e-6,
        'r': resistance*1e-3,
        'l': inductance*1e-9,
        'nr_r': num_turns,
        'blockqrc': block_qrc,
        'subE': subE,
        'lEstim': L_estim*1e-9,
        'rEstim': R_estim*1e-3,
        'Wmin': Wmin*1e-6,
        'Smin': Smin*1e-6,
        'Dmin': Dmin*1e-6,
        'minNr_t': min_num_turns,
        'mergeStat': merge_Stat        
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
    print("✅ inductor2 PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    c = gf.read.import_gds(gdspath="temp.gds")
    
    # TODO : add ports properly using post_process
    # # Adjust port orientations, for metal1 so every other port points in the opposite direction
    # for i, port in enumerate(c.ports):
    #     port.orientation = 90 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    
    os.remove("temp.gds")
    return c

def inductor3(
    model = "inductor3",
    width = 2,
    space = 2.1,
    distance = 25.84,
    resistance = 1,
    inductance = 1,
    num_turns = 2,
    block_qrc = True,
    subE = False,
    L_estim = 221.5,
    R_estim = 1386,
    Wmin = 2,
    Smin = 2.1,
    Dmin = 25.84,
    min_num_turns = 2,
    merge_Stat = 16
    ) -> Component:
    """
    Args:
    
    Returns:
        gdsfactory Component
    
    
    """
    
    # ----------------------------------------------------------------
    # Step 1: Get the technology object
    # ----------------------------------------------------------------
    tech = Tech.get("SG13_dev")  # Must match the name registered in SG13_Tech

    # ----------------------------------------------------------------
    # Step 2: Create a layout and a cell
    # ----------------------------------------------------------------
    layout = pya.Layout()                # new empty layout
    cell = layout.create_cell("inductor3")  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=inductor3IHP(), tech=tech)

    # ----------------------------------------------------------------
    # Step 4: Define parameters
    # ----------------------------------------------------------------
    params = {
        'cdf_version': 8,
        'Display': 'Selected',
        'model': model,
        'w': width*1e-6,
        's': space*1e-6,
        'd': distance*1e-6,
        'r': resistance*1e-3,
        'l': inductance*1e-9,
        'nr_r': num_turns,
        'blockqrc': block_qrc,
        'subE': subE,
        'lEstim': L_estim*1e-9,
        'rEstim': R_estim*1e-3,
        'Wmin': Wmin*1e-6,
        'Smin': Smin*1e-6,
        'Dmin': Dmin*1e-6,
        'minNr_t': min_num_turns,
        'mergeStat': merge_Stat        
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
    print("✅ inductor3 PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    c = gf.read.import_gds(gdspath="temp.gds")
    
    # TODO : add ports properly using post_process
    # # Adjust port orientations, for metal1 so every other port points in the opposite direction
    # for i, port in enumerate(c.ports):
    #     port.orientation = 90 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    
    os.remove("temp.gds")
    return c
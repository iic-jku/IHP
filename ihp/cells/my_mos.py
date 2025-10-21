import sys
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python")
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python/pycell4klayout-api/source/python/")
from sg13g2_pycell_lib.ihp.nmos_code import nmos
from sg13g2_pycell_lib.ihp.pmos_code import pmos
from cni.tech import Tech

from cni.dlo import PCellWrapper
import pya
import gdsfactory as gf
from gdsfactory import Component
import os

from functools import partial
from .. import tech


_add_ports_metal1 = partial(
    gf.add_ports.add_ports_from_boxes, pin_layer=(tech.LAYER.Metal1drawing), port_type="electrical", port_name_prefix="DS", ports_on_short_side=True
)
_add_ports_poly = partial(
    gf.add_ports.add_ports_from_boxes, pin_layer=(tech.LAYER.GatPolydrawing), port_type="electrical", port_name_prefix="G", ports_on_short_side=True
)
_add_ports = (_add_ports_metal1, _add_ports_poly)

@gf.cell
def my_nmos(
    cdf_version = 8, 
    model = 'sg13_lv_nmos', 
    w = 0.15, 
    ws = 150, 
    l = 0.13, 
    Wmin = 0.15, 
    Lmin = 0.13, 
    ng = 1, 
    m = 1, 
    trise = '',
    ) -> Component:
    """Create an NMOS transistor.

    Args:
        cdf_version: CDF version.
        model: Device model name.
        w: Total width of the transistor in micrometers.
        ws: Single width in nanometers.
        l: Length of the transistor in micrometers.
        Wmin: Minimum width in micrometers.
        Lmin: Minimum length in micrometers.
        ng: Number of gates/fingers.
        m: Multiplier (number of parallel devices).
        trise: Temp rise from ambient

    Returns:
        Component with NMOS transistor layout.
    """
    
    
    # ----------------------------------------------------------------
    # Step 1: Get the technology object
    # ----------------------------------------------------------------
    tech = Tech.get("SG13_dev")  # Must match the name registered in SG13_Tech

    # ----------------------------------------------------------------
    # Step 2: Create a layout and a cell
    # ----------------------------------------------------------------
    layout = pya.Layout()                # new empty layout
    cell = layout.create_cell("NMOS_1")  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=nmos(), tech=tech)

    # ----------------------------------------------------------------
    # Step 4: Define parameters
    # ----------------------------------------------------------------
    params = {
        'cdf_version': cdf_version,
        'model': model,
        'w': w*1e-6,    # Width in μm
        'ws': ws*1e-6,   # Single Width in nm
        'l': l*1e-6,   # Length in μm
        'ng': ng,     # Number of gates
        'm': m,      # Multiplier
        'Wmin': Wmin*1e-6,
        'Lmin': Lmin*1e-6,
        'trise': trise,
        'Display': 'Selected'
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
    layout.write("nmos_test.gds")
    print("✅ NMOS PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    nm = gf.read.import_gds(gdspath="nmos_test.gds", post_process=_add_ports)
    os.remove("nmos_test.gds")
    return nm


@gf.cell
def my_pmos(
    cdf_version = 8, 
    model = 'sg13_lv_pmos', 
    w = 0.15, 
    ws = 150, 
    l = 0.13, 
    Wmin = 0.15, 
    Lmin = 0.13, 
    ng = 1, 
    m = 1, 
    trise = '',
    ) -> Component:
    """Create an PMOS transistor.

    Args:
        cdf_version: CDF version.
        model: Device model name.
        w: Total width of the transistor in micrometers.
        ws: Single width in nanometers.
        l: Length of the transistor in micrometers.
        Wmin: Minimum width in micrometers.
        Lmin: Minimum length in micrometers.
        ng: Number of gates/fingers.
        m: Multiplier (number of parallel devices).
        trise: Temp rise from ambient

    Returns:
        Component with PMOS transistor layout.
    """
    
    
    # ----------------------------------------------------------------
    # Step 1: Get the technology object
    # ----------------------------------------------------------------
    tech = Tech.get("SG13_dev")  # Must match the name registered in SG13_Tech

    # ----------------------------------------------------------------
    # Step 2: Create a layout and a cell
    # ----------------------------------------------------------------
    layout = pya.Layout()                # new empty layout
    cell = layout.create_cell("PMOS_1")  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=pmos(), tech=tech)

    # ----------------------------------------------------------------
    # Step 4: Define parameters
    # ----------------------------------------------------------------
    params = {
        'cdf_version': cdf_version,
        'model': model,
        'w': w*1e-6,    # Width in μm
        'ws': ws*1e-6,   # Single Width in nm
        'l': l*1e-6,   # Length in μm
        'ng': ng,     # Number of gates
        'm': m,      # Multiplier
        'Wmin': Wmin*1e-6,
        'Lmin': Lmin*1e-6,
        'trise': trise,
        'Display': 'Selected'
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
    layout.write("pmos_test.gds")
    print("✅ PMOS PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    pm = gf.import_gds(gdspath="pmos_test.gds", post_process=_add_ports)
    os.remove("pmos_test.gds")
    return pm
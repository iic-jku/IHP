import sys
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python")
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python/pycell4klayout-api/source/python/")
import gdsfactory as gf # to have gf.Component
from cni.tech import Tech # to get the technology
from cni.dlo import PCellWrapper # to wrap the PyCell
import pya # KLayout Python API
import os



def generate_gf_from_ihp(
    cell_name, 
    cell_params, 
    function_name
    ) -> gf.Component: 
    
    # ----------------------------------------------------------------
    # Step 1: Get the technology object
    # ----------------------------------------------------------------
    tech = Tech.get("SG13_dev")  # Must match the name registered in SG13_Tech

    # ----------------------------------------------------------------
    # Step 2: Create a layout and a cell
    # ----------------------------------------------------------------
    layout = pya.Layout()                # new empty layout
    cell = layout.create_cell(cell_name)  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=function_name, tech=tech)
    
    # Convert params into a list in the order of device.param_decls
    param_values = [cell_params[p.name] for p in device.param_decls]

    # ----------------------------------------------------------------
    # Step 4: Produce the layout
    # ----------------------------------------------------------------
    device.produce(layout=layout,
                layers={},        # can pass layer map if needed
                parameters=param_values,
                cell=cell)

    # ----------------------------------------------------------------
    # Step 5: Bring to GDSFactory
    # ----------------------------------------------------------------
    layout.write("temp.gds")
    print(f"✅ {cell_name} PyCell placed successfully and GDS written.")
    c = gf.read.import_gds(gdspath="temp.gds")
    os.remove("temp.gds")
    # ----------------------------------------------------------------
    
    return c
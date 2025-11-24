"""Passive components (varicaps, ESD, taps, seal rings) for IHP PDK."""
import sys
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python")
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python/pycell4klayout-api/source/python/")
from sg13g2_pycell_lib.ihp.esd_code import esd as esdIHP
from sg13g2_pycell_lib.ihp.ptap1_code import ptap1 as ptap1IHP
from sg13g2_pycell_lib.ihp.ntap1_code import ntap1 as ntap1IHP
from sg13g2_pycell_lib.ihp.sealring_code import sealring as sealringIHP
from cni.tech import Tech

from cni.dlo import PCellWrapper
import pya
import gdsfactory as gf
from gdsfactory import Component
import os



@gf.cell
def esd(
    model: str = "diodevdd_2kv",
) -> Component:
    """Create an ESD protection NMOS device.

    Args:
        model: Device model name.

    Returns:
        Component with ESD NMOS layout.
    """
    # ----------------------------------------------------------------
    # Step 1: Get the technology object
    # ----------------------------------------------------------------
    tech = Tech.get("SG13_dev")  # Must match the name registered in SG13_Tech

    # ----------------------------------------------------------------
    # Step 2: Create a layout and a cell
    # ----------------------------------------------------------------
    layout = pya.Layout()                # new empty layout
    cell = layout.create_cell("ESD")  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=esdIHP(), tech=tech)

    # ----------------------------------------------------------------
    # Step 4: Define parameters
    # ----------------------------------------------------------------
    params = {
        'cdf_version': 8,
        'Display': 'Selected',
        'model': model
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
    print("✅ ESD PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    c = gf.read.import_gds(gdspath="temp.gds")
    
    os.remove("temp.gds")
    return c



@gf.cell
def ptap1(
    calculate = "R,A",
    R = 263,
    width = 0.78,
    length = 0.78,
    Area = 0.6084,
    Perimeter = 3.12,
    Rspec = 0.980
    ) -> Component:
    """Create a P+ substrate tap.

    Args:
        width: Width of the tap in micrometers.
        length: Length of the tap in micrometers.
        rows: Number of contact rows.
        cols: Number of contact columns.

    Returns:
        Component with P+ tap layout.
    """
    # ----------------------------------------------------------------
    # Step 1: Get the technology object
    # ----------------------------------------------------------------
    tech = Tech.get("SG13_dev")  # Must match the name registered in SG13_Tech

    # ----------------------------------------------------------------
    # Step 2: Create a layout and a cell
    # ----------------------------------------------------------------
    layout = pya.Layout()                # new empty layout
    cell = layout.create_cell("PTAP_1")  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=ptap1IHP(), tech=tech)

    # ----------------------------------------------------------------
    # Step 4: Define parameters
    # ----------------------------------------------------------------
    params = {
        'cdf_version': 8,
        'Display': 'Selected',
        'Calculate': calculate,
        'R': R,
        'w': width*1e-6,    # Length in μm
        'l': length*1e-6,   # Length in μm
        'A': Area,
        'Perim': Perimeter,
        'Rspec': Rspec,
        'Wmin': 0.5,
        'Lmin': 0.5,
        'm': 1
        
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
    print("✅ PTAP PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    c = gf.read.import_gds(gdspath="temp.gds")
    
    os.remove("temp.gds")
    return c


@gf.cell
def ntap1(
    calculate = "R,A",
    R = 263,
    width = 0.78,
    length = 0.78,
    Area = 0.6084,
    Perimeter = 3.12,
    Rspec = 0.980
) -> Component:
    """Create an N+ substrate tap.

    Args:
        width: Width of the tap in micrometers.
        length: Length of the tap in micrometers.
        rows: Number of contact rows.
        cols: Number of contact columns.

    Returns:
        Component with N+ tap layout.
    """
    # ----------------------------------------------------------------
    # Step 1: Get the technology object
    # ----------------------------------------------------------------
    tech = Tech.get("SG13_dev")  # Must match the name registered in SG13_Tech

    # ----------------------------------------------------------------
    # Step 2: Create a layout and a cell
    # ----------------------------------------------------------------
    layout = pya.Layout()                # new empty layout
    cell = layout.create_cell("NTAP_1")  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=ntap1IHP(), tech=tech)

    # ----------------------------------------------------------------
    # Step 4: Define parameters
    # ----------------------------------------------------------------
    params = {
        'cdf_version': 8,
        'Display': 'Selected',
        'Calculate': calculate,
        'R': R,
        'w': width*1e-6,    # Length in μm
        'l': length*1e-6,   # Length in μm
        'A': Area,
        'Perim': Perimeter,
        'Rspec': Rspec,
        'Wmin': 0.5,
        'Lmin': 0.5,
        'm': 1
        
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
    print("✅ NTAP PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    c = gf.read.import_gds(gdspath="temp.gds")
    
    os.remove("temp.gds")
    return c


@gf.cell
def sealring(
    width: float = 400.0,
    height: float = 400.0
) -> Component:
    """Create a seal ring for die protection.

    Args:
        width: Inner width of the seal ring in micrometers.
        height: Inner height of the seal ring in micrometers.
        ring_width: Width of the seal ring metal in micrometers.

    Returns:
        Component with seal ring layout.
    """
    # ----------------------------------------------------------------
    # Step 1: Get the technology object
    # ----------------------------------------------------------------
    tech = Tech.get("SG13_dev")  # Must match the name registered in SG13_Tech

    # ----------------------------------------------------------------
    # Step 2: Create a layout and a cell
    # ----------------------------------------------------------------
    layout = pya.Layout()                # new empty layout
    cell = layout.create_cell("SEALRING_1")  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=sealringIHP(), tech=tech)

    # ----------------------------------------------------------------
    # Step 4: Define parameters
    # ----------------------------------------------------------------
    params = {
        'cdf_version': 8,
        'Display': 'Selected',
        'l': width*1e-6,    # Length in μm
        'w': height*1e-6,   # Length in μm
        'addLabel': 'nil',
        'addSlit': 'nil',
        'Wmin': 150*1e-6,
        'Lmin': 150*1e-6,
        'edgeBox': 25*1e-6
        
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
    print("✅ Sealring PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    c = gf.read.import_gds(gdspath="temp.gds")
    
    os.remove("temp.gds")
    return c


if __name__ == "__main__":
    # Test the components
    c1 = svaricap(width=2.0, length=1.0, nf=4)
    c1.show()

    c2 = esd_nmos(width=100.0, length=0.5, nf=20)
    c2.show()

    c3 = ptap1(width=2.0, length=2.0, rows=2, cols=2)
    c3.show()

    c4 = sealring(width=500, height=500, ring_width=10)
    c4.show()

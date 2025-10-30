import sys
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python")
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python/pycell4klayout-api/source/python/")
from sg13g2_pycell_lib.ihp.nmos_code import nmos as nmosIHP
from sg13g2_pycell_lib.ihp.nmosHV_code import nmosHV as nmosHVIHP
from sg13g2_pycell_lib.ihp.pmos_code import pmos as pmosIHP
from sg13g2_pycell_lib.ihp.pmosHV_code import pmosHV as pmosHVIHP
from sg13g2_pycell_lib.ihp.rfnmos_code import rfnmos as rfnmosIHP
from sg13g2_pycell_lib.ihp.rfnmosHV_code import rfnmosHV as rfnmosHVIHP
from sg13g2_pycell_lib.ihp.rfpmos_code import rfpmos as rfpmosIHP
from sg13g2_pycell_lib.ihp.rfpmosHV_code import rfpmosHV as rfpmosHVIHP

from cni.tech import Tech

from cni.dlo import PCellWrapper
import pya
import gdsfactory as gf
from gdsfactory import Component
import os

from functools import partial
from .. import tech


_add_ports_metal1 = partial(
    gf.add_ports.add_ports_from_boxes, pin_layer=(tech.LAYER.Metal1pin), port_type="electrical", port_name_prefix='DS_', ports_on_short_side=True, auto_rename_ports=False
)
_add_ports_poly = partial(
    gf.add_ports.add_ports_from_boxes, pin_layer=(tech.LAYER.GatPolydrawing), port_type="electrical", port_name_prefix="G_", ports_on_short_side=True, auto_rename_ports=False
)
_add_ports = (_add_ports_metal1, _add_ports_poly)

@gf.cell
def nmos(
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
    device = PCellWrapper(impl=nmosIHP(), tech=tech)

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
    layout.write("temp.gds")
    print("✅ NMOS PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    c = gf.read.import_gds(gdspath="temp.gds", post_process=_add_ports)
    
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    for i, port in enumerate(c.ports):
        port.orientation = 90 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    os.remove("temp.gds")
    return c

@gf.cell
def nmosHV(
    cdf_version = 8, 
    model = 'sg13_hv_pmos', 
    w = 0.60, 
    ws = 600, 
    l = 0.45, 
    Wmin = 0.30, 
    Lmin = 0.45, 
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
    cell = layout.create_cell("NMOS_HV_1")  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=nmosHVIHP(), tech=tech)

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
    layout.write("temp.gds")
    print("✅ NMOS_HV PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    c = gf.import_gds(gdspath="temp.gds", post_process=_add_ports)
    
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    for i, port in enumerate(c.ports):
        port.orientation = 270 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    os.remove("temp.gds")
    return c


@gf.cell
def pmos(
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
    device = PCellWrapper(impl=pmosIHP(), tech=tech)

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
    layout.write("temp.gds")
    print("✅ PMOS PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    c = gf.import_gds(gdspath="temp.gds", post_process=_add_ports)
    
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    for i, port in enumerate(c.ports):
        port.orientation = 270 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    os.remove("temp.gds")
    return c


@gf.cell
def pmosHV(
    cdf_version = 8, 
    model = 'sg13_hv_pmos', 
    w = 0.30, 
    ws = 300, 
    l = 0.40, 
    Wmin = 0.30, 
    Lmin = 0.40, 
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
    cell = layout.create_cell("PMOS_HV_1")  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=pmosHVIHP(), tech=tech)

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
    layout.write("temp.gds")
    print("✅ PMOS_HV PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    c = gf.import_gds(gdspath="temp.gds", post_process=_add_ports)
    
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    for i, port in enumerate(c.ports):
        port.orientation = 270 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    os.remove("temp.gds")
    return c


@gf.cell
def rfnmos(
    cdf_version=8,
    rfmode=1,
    model='sg13_lv_nmos',
    w=1.0,
    ws=1,
    l=0.72,
    ng=1,
    calculate=True,
    cnt_rows=1,
    Met2Cont="Yes",
    gat_ring="Yes",
    guard_ring="Yes",
    Wmin=0.15,
    Lmin=0.13
    ) -> Component:
    """Create an RF NMOS transistor.

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
        # TODO: complete other params

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
    cell = layout.create_cell("RF_NMOS_1")  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=rfnmosIHP(), tech=tech)

    # ----------------------------------------------------------------
    # Step 4: Define parameters
    # ----------------------------------------------------------------
    params = {       
        'cdf_version': cdf_version, 
        'rfmode': rfmode,
        'model': model,
        'w': w*1e-6,    # Width in μm
        'ws': ws*1e-6,   # Single Width in nm
        'l': l*1e-6,   # Length in μm
        'ng': ng,     # Number of gates
        'calculate': calculate,
        'cnt_rows': cnt_rows,
        'Met2Cont': Met2Cont,
        'gat_ring': gat_ring,
        'guard_ring': guard_ring,
        'Wmin': Wmin*1e-6,
        'Lmin': Lmin*1e-6,
        'm': 1,
        'trise': '',
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
    layout.write("temp.gds")
    print("✅ RF_NMOS PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    c = gf.import_gds(gdspath="temp.gds", post_process=_add_ports)
    
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    for i, port in enumerate(c.ports):
        port.orientation = 270 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    os.remove("temp.gds")
    return c


@gf.cell
def rfnmosHV(
    cdf_version=8,
    rfmode=1,
    model='sg13_hv_nmos',
    w=1.0,
    ws=1.0,
    l=0.72,
    ng=1,
    calculate=True,
    cnt_rows=1,
    Met2Cont="Yes",
    gat_ring="Yes",
    guard_ring="Yes",
    Wmin=0.33,
    Lmin=0.45
    ) -> Component:
    """Create an RF NMOS transistor.

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
        # TODO: complete other params

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
    cell = layout.create_cell("RF_NMOS_HV_1")  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=rfnmosHVIHP(), tech=tech)

    # ----------------------------------------------------------------
    # Step 4: Define parameters
    # ----------------------------------------------------------------
    params = {       
        'cdf_version': cdf_version, 
        'rfmode': rfmode,
        'model': model,
        'w': w*1e-6,    # Width in μm
        'ws': ws*1e-6,   # Single Width in nm
        'l': l*1e-6,   # Length in μm
        'ng': ng,     # Number of gates
        'calculate': calculate,
        'cnt_rows': cnt_rows,
        'Met2Cont': Met2Cont,
        'gat_ring': gat_ring,
        'guard_ring': guard_ring,
        'Wmin': Wmin*1e-6,
        'Lmin': Lmin*1e-6,
        'm': 1,
        'trise': '',
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
    layout.write("temp.gds")
    print("✅ RF_NMOS_HV PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    c = gf.import_gds(gdspath="temp.gds", post_process=_add_ports)
    
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    for i, port in enumerate(c.ports):
        port.orientation = 270 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    os.remove("temp.gds")
    return c


@gf.cell
def rfpmos(
    cdf_version=8,
    rfmode=1,
    model='sg13_lv_pmos',
    w=1.0,
    ws=1.0,
    l=0.72,
    ng=1,
    calculate=True,
    cnt_rows=1,
    Met2Cont="Yes",
    gat_ring="Yes",
    guard_ring="Yes",
    Wmin=0.15,
    Lmin=0.13
    ) -> Component:
    """Create an RF NMOS transistor.

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
        # TODO: complete other params

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
    cell = layout.create_cell("RF_PMOS_1")  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=rfpmosIHP(), tech=tech)

    # ----------------------------------------------------------------
    # Step 4: Define parameters
    # ----------------------------------------------------------------
    params = {       
        'cdf_version': cdf_version, 
        'rfmode': rfmode,
        'model': model,
        'w': w*1e-6,    # Width in μm
        'ws': ws*1e-6,   # Single Width in nm
        'l': l*1e-6,   # Length in μm
        'ng': ng,     # Number of gates
        'calculate': calculate,
        'cnt_rows': cnt_rows,
        'Met2Cont': Met2Cont,
        'gat_ring': gat_ring,
        'guard_ring': guard_ring,
        'Wmin': Wmin*1e-6,
        'Lmin': Lmin*1e-6,
        'm': 1,
        'trise': '',
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
    layout.write("temp.gds")
    print("✅ RF_PMOS PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    c = gf.import_gds(gdspath="temp.gds", post_process=_add_ports)
    
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    for i, port in enumerate(c.ports):
        port.orientation = 270 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    os.remove("temp.gds")
    return c

@gf.cell
def rfpmosHV(
    cdf_version=8,
    rfmode=1,
    model='sg13_hv_pmos',
    w=1.0,
    ws=1.0,
    l=0.72,
    ng=1,
    calculate=True,
    cnt_rows=1,
    Met2Cont="Yes",
    gat_ring="Yes",
    guard_ring="Yes",
    Wmin=0.39,
    Lmin=0.4
    ) -> Component:
    """Create an RF NMOS transistor.

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
        # TODO: complete other params

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
    cell = layout.create_cell("RF_PMOS_HV_1")  # new cell for your transistor

    # ----------------------------------------------------------------
    # Step 3: Wrap the PyCell
    # ----------------------------------------------------------------
    # PCellWrapper acts like the 'specs' object in KLayout
    # It handles parameter declarations and calls defineParamSpecs internally
    device = PCellWrapper(impl=rfpmosHVIHP(), tech=tech)

    # ----------------------------------------------------------------
    # Step 4: Define parameters
    # ----------------------------------------------------------------
    params = {       
        'cdf_version': cdf_version, 
        'rfmode': rfmode,
        'model': model,
        'w': w*1e-6,    # Width in μm
        'ws': ws*1e-6,   # Single Width in nm
        'l': l*1e-6,   # Length in μm
        'ng': ng,     # Number of gates
        'calculate': calculate,
        'cnt_rows': cnt_rows,
        'Met2Cont': Met2Cont,
        'gat_ring': gat_ring,
        'guard_ring': guard_ring,
        'Wmin': Wmin*1e-6,
        'Lmin': Lmin*1e-6,
        'm': 1,
        'trise': '',
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
    layout.write("temp.gds")
    print("✅ RF_PMOS_HV PyCell placed successfully and GDS written.")
    # ----------------------------------------------------------------
    c = gf.import_gds(gdspath="temp.gds", post_process=_add_ports)
    
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    for i, port in enumerate(c.ports):
        port.orientation = 270 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    os.remove("temp.gds")
    return c
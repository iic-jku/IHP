import sys
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python")
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python/pycell4klayout-api/source/python/")

from sg13g2_pycell_lib.ihp.utility_functions import eng_string_to_float

from sg13g2_pycell_lib.ihp.nmos_code import nmos as nmosIHP
from sg13g2_pycell_lib.ihp.nmosHV_code import nmosHV as nmosHVIHP
from sg13g2_pycell_lib.ihp.pmos_code import pmos as pmosIHP
from sg13g2_pycell_lib.ihp.pmosHV_code import pmosHV as pmosHVIHP
from sg13g2_pycell_lib.ihp.rfnmos_code import rfnmos as rfnmosIHP
from sg13g2_pycell_lib.ihp.rfnmosHV_code import rfnmosHV as rfnmosHVIHP
from sg13g2_pycell_lib.ihp.rfpmos_code import rfpmos as rfpmosIHP
from sg13g2_pycell_lib.ihp.rfpmosHV_code import rfpmosHV as rfpmosHVIHP


import gdsfactory as gf

from .utils import *
from functools import partial
from .. import tech



_add_ports_metal1 = partial(
    gf.add_ports.add_ports_from_boxes, pin_layer=(tech.LAYER.Metal1drawing), port_type="electrical", port_name_prefix='DS_', ports_on_short_side=True, auto_rename_ports=False
)
_add_ports_poly = partial(
    gf.add_ports.add_ports_from_boxes, pin_layer=(tech.LAYER.GatPolydrawing), port_type="electrical", port_name_prefix="G_", ports_on_short_side=True, auto_rename_ports=False
)
_add_ports = (_add_ports_metal1, _add_ports_poly)

@gf.cell
def nmos(
    w = 0.15, 
    l = 0.13, 
    ng = 1,
    ) -> gf.Component:
    """Create an NMOS transistor.

    Args:
        w: Total width of the transistor in micrometers.
        l: Length of the transistor in micrometers.
        ng: Number of gates/fingers.

    Returns:
        Component with NMOS transistor layout.
    """
   
    params = {
        'cdf_version': tech.techParams['CDFVersion'],
        'model': tech.techParams['nmos_model'],
        'w': w*1e-6,    # Width in μm
        'ws': eng_string_to_float(tech.techParams['nmos_defW'])/eng_string_to_float(tech.techParams['nmos_defNG']),   # Single Width in nm
        'l': l*1e-6,   # Length in μm
        'ng': ng,     # Number of gates
        'm': 1,      # Multiplier
        'Wmin': eng_string_to_float(tech.techParams['nmos_minW']),
        'Lmin': eng_string_to_float(tech.techParams['nmos_minL']),
        'trise': '',
        'Display': 'Selected'
    }

    c = generate_gf_from_ihp(cell_name="nmos", cell_params=params, function_name=nmosIHP())
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    # for i, port in enumerate(c.ports):
    #     port.orientation = 90 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    return c

@gf.cell
def nmosHV(
    w = 0.60, 
    l = 0.45, 
    ng = 1, 
    ) -> gf.Component:
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
    
    
    params = {
        'cdf_version': tech.techParams['CDFVersion'],
        'model': tech.techParams['nmosHV_model'],
        'w': w*1e-6,    # Width in μm
        'ws': eng_string_to_float(tech.techParams['nmosHV_defW'])/eng_string_to_float(tech.techParams['nmosHV_defNG']),   # Single Width in nm
        'l': l*1e-6,   # Length in μm
        'ng': ng,     # Number of gates
        'm': 1,      # Multiplier
        'Wmin': eng_string_to_float(tech.techParams['nmosHV_minW']),
        'Lmin': eng_string_to_float(tech.techParams['nmosHV_minL']),
        'trise': '',
        'Display': 'Selected'
    }

    c = generate_gf_from_ihp(cell_name="nmosHV", cell_params=params, function_name=nmosHVIHP())
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    # for i, port in enumerate(c.ports):
    #     port.orientation = 90 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    return c


@gf.cell
def pmos(
    w = 0.15, 
    l = 0.13, 
    ng = 1,
    ) -> gf.Component:
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
    
    params = {
        'cdf_version': tech.techParams['CDFVersion'],
        'model': tech.techParams['pmos_model'],
        'w': w*1e-6,    # Width in μm
        'ws': eng_string_to_float(tech.techParams['pmos_defW'])/eng_string_to_float(tech.techParams['pmos_defNG']),   # Single Width in nm
        'l': l*1e-6,   # Length in μm
        'ng': ng,     # Number of gates
        'm': 1,      # Multiplier
        'Wmin': eng_string_to_float(tech.techParams['pmos_minW']),
        'Lmin': eng_string_to_float(tech.techParams['pmos_minL']),
        'trise': '',
        'Display': 'Selected'
    }

    c = generate_gf_from_ihp(cell_name="pmos", cell_params=params, function_name=pmosIHP())
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    # for i, port in enumerate(c.ports):
    #     port.orientation = 90 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    return c


@gf.cell
def pmosHV(
    w = 0.30, 
    l = 0.40, 
    ng = 1,
    ) -> gf.Component:
    """Create an PMOSHV transistor.

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
    
    params = {
        'cdf_version': tech.techParams['CDFVersion'],
        'model': tech.techParams['pmosHV_model'],
        'w': w*1e-6,    # Width in μm
        'ws': eng_string_to_float(tech.techParams['pmosHV_defW'])/eng_string_to_float(tech.techParams['pmosHV_defNG']),   # Single Width in nm
        'l': l*1e-6,   # Length in μm
        'ng': ng,     # Number of gates
        'm': 1,      # Multiplier
        'Wmin': eng_string_to_float(tech.techParams['pmosHV_minW']),
        'Lmin': eng_string_to_float(tech.techParams['pmosHV_minL']),
        'trise': '',
        'Display': 'Selected'
    }

    c = generate_gf_from_ihp(cell_name="pmosHV", cell_params=params, function_name=pmosHVIHP())
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    # for i, port in enumerate(c.ports):
    #     port.orientation = 90 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    return c


# @gf.cell
# def rfnmos(
#     cdf_version=8,
#     rfmode=1,
#     model='sg13_lv_nmos',
#     w=1.0,
#     ws=1,
#     l=0.72,
#     ng=1,
#     calculate=True,
#     cnt_rows=1,
#     Met2Cont="Yes",
#     gat_ring="Yes",
#     guard_ring="Yes",
#     Wmin=0.15,
#     Lmin=0.13
#     ) -> gf.Component:
#     """Create an RF NMOS transistor.

#     Args:
#         cdf_version: CDF version.
#         model: Device model name.
#         w: Total width of the transistor in micrometers.
#         ws: Single width in nanometers.
#         l: Length of the transistor in micrometers.
#         Wmin: Minimum width in micrometers.
#         Lmin: Minimum length in micrometers.
#         ng: Number of gates/fingers.
#         m: Multiplier (number of parallel devices).
#         trise: Temp rise from ambient
#         # TODO: complete other params

#     Returns:
#         Component with PMOS transistor layout.
#     """
    
    
#     # ----------------------------------------------------------------
#     # Step 1: Get the technology object
#     # ----------------------------------------------------------------
#     tech = Tech.get("SG13_dev")  # Must match the name registered in SG13_Tech

#     # ----------------------------------------------------------------
#     # Step 2: Create a layout and a cell
#     # ----------------------------------------------------------------
#     layout = pya.Layout()                # new empty layout
#     cell = layout.create_cell("RF_NMOS_1")  # new cell for your transistor

#     # ----------------------------------------------------------------
#     # Step 3: Wrap the PyCell
#     # ----------------------------------------------------------------
#     # PCellWrapper acts like the 'specs' object in KLayout
#     # It handles parameter declarations and calls defineParamSpecs internally
#     device = PCellWrapper(impl=rfnmosIHP(), tech=tech)

#     # ----------------------------------------------------------------
#     # Step 4: Define parameters
#     # ----------------------------------------------------------------
#     params = {       
#         'cdf_version': cdf_version, 
#         'rfmode': rfmode,
#         'model': model,
#         'w': w*1e-6,    # Width in μm
#         'ws': ws*1e-6,   # Single Width in nm
#         'l': l*1e-6,   # Length in μm
#         'ng': ng,     # Number of gates
#         'calculate': calculate,
#         'cnt_rows': cnt_rows,
#         'Met2Cont': Met2Cont,
#         'gat_ring': gat_ring,
#         'guard_ring': guard_ring,
#         'Wmin': Wmin*1e-6,
#         'Lmin': Lmin*1e-6,
#         'm': 1,
#         'trise': '',
#         'Display': 'Selected'
#     }

#     # Convert params into a list in the order of device.param_decls
#     param_values = [params[p.name] for p in device.param_decls]

#     # ----------------------------------------------------------------
#     # Step 5: Produce the layout
#     # ----------------------------------------------------------------
#     device.produce(layout=layout,
#                 layers={},        # can pass layer map if needed
#                 parameters=param_values,
#                 cell=cell)

#     # ----------------------------------------------------------------
#     # Step 6: Save GDS
#     # ----------------------------------------------------------------
#     layout.write("temp.gds")
#     print("✅ RF_NMOS PyCell placed successfully and GDS written.")
#     # ----------------------------------------------------------------
#     c = gf.import_gds(gdspath="temp.gds", post_process=_add_ports)
    
#     # Adjust port orientations, for metal1 so every other port points in the opposite direction
#     for i, port in enumerate(c.ports):
#         port.orientation = 270 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
#     os.remove("temp.gds")
#     return c


# @gf.cell
# def rfnmosHV(
#     cdf_version=8,
#     rfmode=1,
#     model='sg13_hv_nmos',
#     w=1.0,
#     ws=1.0,
#     l=0.72,
#     ng=1,
#     calculate=True,
#     cnt_rows=1,
#     Met2Cont="Yes",
#     gat_ring="Yes",
#     guard_ring="Yes",
#     Wmin=0.33,
#     Lmin=0.45
#     ) -> gf.Component:
#     """Create an RF NMOS transistor.

#     Args:
#         cdf_version: CDF version.
#         model: Device model name.
#         w: Total width of the transistor in micrometers.
#         ws: Single width in nanometers.
#         l: Length of the transistor in micrometers.
#         Wmin: Minimum width in micrometers.
#         Lmin: Minimum length in micrometers.
#         ng: Number of gates/fingers.
#         m: Multiplier (number of parallel devices).
#         trise: Temp rise from ambient
#         # TODO: complete other params

#     Returns:
#         Component with PMOS transistor layout.
#     """
    
    
#     # ----------------------------------------------------------------
#     # Step 1: Get the technology object
#     # ----------------------------------------------------------------
#     tech = Tech.get("SG13_dev")  # Must match the name registered in SG13_Tech

#     # ----------------------------------------------------------------
#     # Step 2: Create a layout and a cell
#     # ----------------------------------------------------------------
#     layout = pya.Layout()                # new empty layout
#     cell = layout.create_cell("RF_NMOS_HV_1")  # new cell for your transistor

#     # ----------------------------------------------------------------
#     # Step 3: Wrap the PyCell
#     # ----------------------------------------------------------------
#     # PCellWrapper acts like the 'specs' object in KLayout
#     # It handles parameter declarations and calls defineParamSpecs internally
#     device = PCellWrapper(impl=rfnmosHVIHP(), tech=tech)

#     # ----------------------------------------------------------------
#     # Step 4: Define parameters
#     # ----------------------------------------------------------------
#     params = {       
#         'cdf_version': cdf_version, 
#         'rfmode': rfmode,
#         'model': model,
#         'w': w*1e-6,    # Width in μm
#         'ws': ws*1e-6,   # Single Width in nm
#         'l': l*1e-6,   # Length in μm
#         'ng': ng,     # Number of gates
#         'calculate': calculate,
#         'cnt_rows': cnt_rows,
#         'Met2Cont': Met2Cont,
#         'gat_ring': gat_ring,
#         'guard_ring': guard_ring,
#         'Wmin': Wmin*1e-6,
#         'Lmin': Lmin*1e-6,
#         'm': 1,
#         'trise': '',
#         'Display': 'Selected'
#     }

#     # Convert params into a list in the order of device.param_decls
#     param_values = [params[p.name] for p in device.param_decls]

#     # ----------------------------------------------------------------
#     # Step 5: Produce the layout
#     # ----------------------------------------------------------------
#     device.produce(layout=layout,
#                 layers={},        # can pass layer map if needed
#                 parameters=param_values,
#                 cell=cell)

#     # ----------------------------------------------------------------
#     # Step 6: Save GDS
#     # ----------------------------------------------------------------
#     layout.write("temp.gds")
#     print("✅ RF_NMOS_HV PyCell placed successfully and GDS written.")
#     # ----------------------------------------------------------------
#     c = gf.import_gds(gdspath="temp.gds", post_process=_add_ports)
    
#     # Adjust port orientations, for metal1 so every other port points in the opposite direction
#     for i, port in enumerate(c.ports):
#         port.orientation = 270 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
#     os.remove("temp.gds")
#     return c


# @gf.cell
# def rfpmos(
#     cdf_version=8,
#     rfmode=1,
#     model='sg13_lv_pmos',
#     w=1.0,
#     ws=1.0,
#     l=0.72,
#     ng=1,
#     calculate=True,
#     cnt_rows=1,
#     Met2Cont="Yes",
#     gat_ring="Yes",
#     guard_ring="Yes",
#     Wmin=0.15,
#     Lmin=0.13
#     ) -> gf.Component:
#     """Create an RF NMOS transistor.

#     Args:
#         cdf_version: CDF version.
#         model: Device model name.
#         w: Total width of the transistor in micrometers.
#         ws: Single width in nanometers.
#         l: Length of the transistor in micrometers.
#         Wmin: Minimum width in micrometers.
#         Lmin: Minimum length in micrometers.
#         ng: Number of gates/fingers.
#         m: Multiplier (number of parallel devices).
#         trise: Temp rise from ambient
#         # TODO: complete other params

#     Returns:
#         Component with PMOS transistor layout.
#     """
    
    
#     # ----------------------------------------------------------------
#     # Step 1: Get the technology object
#     # ----------------------------------------------------------------
#     tech = Tech.get("SG13_dev")  # Must match the name registered in SG13_Tech

#     # ----------------------------------------------------------------
#     # Step 2: Create a layout and a cell
#     # ----------------------------------------------------------------
#     layout = pya.Layout()                # new empty layout
#     cell = layout.create_cell("RF_PMOS_1")  # new cell for your transistor

#     # ----------------------------------------------------------------
#     # Step 3: Wrap the PyCell
#     # ----------------------------------------------------------------
#     # PCellWrapper acts like the 'specs' object in KLayout
#     # It handles parameter declarations and calls defineParamSpecs internally
#     device = PCellWrapper(impl=rfpmosIHP(), tech=tech)

#     # ----------------------------------------------------------------
#     # Step 4: Define parameters
#     # ----------------------------------------------------------------
#     params = {       
#         'cdf_version': cdf_version, 
#         'rfmode': rfmode,
#         'model': model,
#         'w': w*1e-6,    # Width in μm
#         'ws': ws*1e-6,   # Single Width in nm
#         'l': l*1e-6,   # Length in μm
#         'ng': ng,     # Number of gates
#         'calculate': calculate,
#         'cnt_rows': cnt_rows,
#         'Met2Cont': Met2Cont,
#         'gat_ring': gat_ring,
#         'guard_ring': guard_ring,
#         'Wmin': Wmin*1e-6,
#         'Lmin': Lmin*1e-6,
#         'm': 1,
#         'trise': '',
#         'Display': 'Selected'
#     }

#     # Convert params into a list in the order of device.param_decls
#     param_values = [params[p.name] for p in device.param_decls]

#     # ----------------------------------------------------------------
#     # Step 5: Produce the layout
#     # ----------------------------------------------------------------
#     device.produce(layout=layout,
#                 layers={},        # can pass layer map if needed
#                 parameters=param_values,
#                 cell=cell)

#     # ----------------------------------------------------------------
#     # Step 6: Save GDS
#     # ----------------------------------------------------------------
#     layout.write("temp.gds")
#     print("✅ RF_PMOS PyCell placed successfully and GDS written.")
#     # ----------------------------------------------------------------
#     c = gf.import_gds(gdspath="temp.gds", post_process=_add_ports)
    
#     # Adjust port orientations, for metal1 so every other port points in the opposite direction
#     for i, port in enumerate(c.ports):
#         port.orientation = 270 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
#     os.remove("temp.gds")
#     return c

# @gf.cell
# def rfpmosHV(
#     cdf_version=8,
#     rfmode=1,
#     model='sg13_hv_pmos',
#     w=1.0,
#     ws=1.0,
#     l=0.72,
#     ng=1,
#     calculate=True,
#     cnt_rows=1,
#     Met2Cont="Yes",
#     gat_ring="Yes",
#     guard_ring="Yes",
#     Wmin=0.39,
#     Lmin=0.4
#     ) -> gf.Component:
#     """Create an RF NMOS transistor.

#     Args:
#         cdf_version: CDF version.
#         model: Device model name.
#         w: Total width of the transistor in micrometers.
#         ws: Single width in nanometers.
#         l: Length of the transistor in micrometers.
#         Wmin: Minimum width in micrometers.
#         Lmin: Minimum length in micrometers.
#         ng: Number of gates/fingers.
#         m: Multiplier (number of parallel devices).
#         trise: Temp rise from ambient
#         # TODO: complete other params

#     Returns:
#         Component with PMOS transistor layout.
#     """
    
    
#     # ----------------------------------------------------------------
#     # Step 1: Get the technology object
#     # ----------------------------------------------------------------
#     tech = Tech.get("SG13_dev")  # Must match the name registered in SG13_Tech

#     # ----------------------------------------------------------------
#     # Step 2: Create a layout and a cell
#     # ----------------------------------------------------------------
#     layout = pya.Layout()                # new empty layout
#     cell = layout.create_cell("RF_PMOS_HV_1")  # new cell for your transistor

#     # ----------------------------------------------------------------
#     # Step 3: Wrap the PyCell
#     # ----------------------------------------------------------------
#     # PCellWrapper acts like the 'specs' object in KLayout
#     # It handles parameter declarations and calls defineParamSpecs internally
#     device = PCellWrapper(impl=rfpmosHVIHP(), tech=tech)

#     # ----------------------------------------------------------------
#     # Step 4: Define parameters
#     # ----------------------------------------------------------------
#     params = {       
#         'cdf_version': cdf_version, 
#         'rfmode': rfmode,
#         'model': model,
#         'w': w*1e-6,    # Width in μm
#         'ws': ws*1e-6,   # Single Width in nm
#         'l': l*1e-6,   # Length in μm
#         'ng': ng,     # Number of gates
#         'calculate': calculate,
#         'cnt_rows': cnt_rows,
#         'Met2Cont': Met2Cont,
#         'gat_ring': gat_ring,
#         'guard_ring': guard_ring,
#         'Wmin': Wmin*1e-6,
#         'Lmin': Lmin*1e-6,
#         'm': 1,
#         'trise': '',
#         'Display': 'Selected'
#     }

#     # Convert params into a list in the order of device.param_decls
#     param_values = [params[p.name] for p in device.param_decls]

#     # ----------------------------------------------------------------
#     # Step 5: Produce the layout
#     # ----------------------------------------------------------------
#     device.produce(layout=layout,
#                 layers={},        # can pass layer map if needed
#                 parameters=param_values,
#                 cell=cell)

#     # ----------------------------------------------------------------
#     # Step 6: Save GDS
#     # ----------------------------------------------------------------
#     layout.write("temp.gds")
#     print("✅ RF_PMOS_HV PyCell placed successfully and GDS written.")
#     # ----------------------------------------------------------------
#     c = gf.import_gds(gdspath="temp.gds", post_process=_add_ports)
    
#     # Adjust port orientations, for metal1 so every other port points in the opposite direction
#     for i, port in enumerate(c.ports):
#         port.orientation = 270 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
#     os.remove("temp.gds")
#     return c
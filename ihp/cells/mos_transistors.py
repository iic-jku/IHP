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
    guardRingType = "none",
    guardRingDistance = 1,
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
        'Display': 'Selected',
        'guardRingType': guardRingType,
        'guardRingDistance': guardRingDistance*1e-6,
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
    guardRingType = "none",
    guardRingDistance = 1,
    ) -> gf.Component:
    """Create an PMOS transistor.

    Args:
        w: Total width of the transistor in micrometers.
        l: Length of the transistor in micrometers.
        ng: Number of gates/fingers.
        guardRingType: Type of guard ring ("none", "psub").
        #TODO
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
        'Display': 'Selected',
        'guardRingType': guardRingType,
        'guardRingDistance': guardRingDistance*1e-6,
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
    guardRingType = "none",
    guardRingDistance = 1,
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
        'Display': 'Selected',
        'guardRingType': guardRingType,
        'guardRingDistance': guardRingDistance*1e-6,
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
    guardRingType = "none",
    guardRingDistance = 1,
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
        #TODO
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
        'Display': 'Selected',
        'guardRingType': guardRingType,
        'guardRingDistance': guardRingDistance*1e-6,
    }

    c = generate_gf_from_ihp(cell_name="pmosHV", cell_params=params, function_name=pmosHVIHP())
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    # for i, port in enumerate(c.ports):
    #     port.orientation = 90 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    return c


@gf.cell
def rfnmos(
    w=1.0,
    l=0.72,
    ng=1,
    cnt_rows=1,
    Met2Cont="Yes",
    gat_ring="Yes",
    guard_ring="Yes",
    ) -> gf.Component:
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
    
    params = {       
        'cdf_version': tech.techParams['CDFVersion'], 
        'rfmode': 1,
        'model': tech.techParams['rfnmos_model'],
        'w': w*1e-6,    # Width in μm
        'ws': eng_string_to_float(tech.techParams['rfnmos_defW'])/eng_string_to_float(tech.techParams['rfnmos_defNG'])*1e-6,   # Single Width in nm
        'l': l*1e-6,   # Length in μm
        'ng': ng,     # Number of gates
        'calculate': True,
        'cnt_rows': cnt_rows,
        'Met2Cont': Met2Cont,
        'gat_ring': gat_ring,
        'guard_ring': guard_ring,
        'Wmin': eng_string_to_float(tech.techParams['rfnmos_minW']),
        'Lmin': eng_string_to_float(tech.techParams['rfnmos_minL']),
        'm': 1,
        'trise': '',
        'Display': 'Selected'
    }

    c = generate_gf_from_ihp(cell_name="rfnmos", cell_params=params, function_name=rfnmosIHP())
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    # for i, port in enumerate(c.ports):
    #     port.orientation = 90 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    return c


@gf.cell
def rfnmosHV(
    w=1.0,
    l=0.72,
    ng=1,
    cnt_rows=1,
    Met2Cont="Yes",
    gat_ring="Yes",
    guard_ring="Yes",
    ) -> gf.Component:
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
    
    params = {       
        'cdf_version': tech.techParams['CDFVersion'], 
        'rfmode': 1,
        'model': tech.techParams['rfnmosHV_model'],
        'w': w*1e-6,    # Width in μm
        'ws': eng_string_to_float(tech.techParams['rfnmosHV_defW'])/eng_string_to_float(tech.techParams['rfnmosHV_defNG'])*1e-6,   # Single Width in nm
        'l': l*1e-6,   # Length in μm
        'ng': ng,     # Number of gates
        'calculate': True,
        'cnt_rows': cnt_rows,
        'Met2Cont': Met2Cont,
        'gat_ring': gat_ring,
        'guard_ring': guard_ring,
        'Wmin': eng_string_to_float(tech.techParams['rfnmosHV_minW']),
        'Lmin': eng_string_to_float(tech.techParams['rfnmosHV_minL']),
        'm': 1,
        'trise': '',
        'Display': 'Selected'
    }

    c = generate_gf_from_ihp(cell_name="rfnmosHV", cell_params=params, function_name=rfnmosHVIHP())
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    # for i, port in enumerate(c.ports):
    #     port.orientation = 90 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    return c


@gf.cell
def rfpmos(
    w=1.0,
    l=0.72,
    ng=1,
    cnt_rows=1,
    Met2Cont="Yes",
    gat_ring="Yes",
    guard_ring="Yes",
    ) -> gf.Component:
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
    
    params = {       
        'cdf_version': tech.techParams['CDFVersion'], 
        'rfmode': 1,
        'model': tech.techParams['rfpmos_model'],
        'w': w*1e-6,    # Width in μm
        'ws': eng_string_to_float(tech.techParams['rfpmos_defW'])/eng_string_to_float(tech.techParams['rfpmos_defNG'])*1e-6,   # Single Width in nm
        'l': l*1e-6,   # Length in μm
        'ng': ng,     # Number of gates
        'calculate': True,
        'cnt_rows': cnt_rows,
        'Met2Cont': Met2Cont,
        'gat_ring': gat_ring,
        'guard_ring': guard_ring,
        'Wmin': eng_string_to_float(tech.techParams['rfpmos_minW']),
        'Lmin': eng_string_to_float(tech.techParams['rfpmos_minL']),
        'm': 1,
        'trise': '',
        'Display': 'Selected'
    }

    c = generate_gf_from_ihp(cell_name="rfpmos", cell_params=params, function_name=rfpmosIHP())
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    # for i, port in enumerate(c.ports):
    #     port.orientation = 90 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    return c

@gf.cell
def rfpmosHV(
    w=1.0,
    l=0.72,
    ng=1,
    cnt_rows=1,
    Met2Cont="Yes",
    gat_ring="Yes",
    guard_ring="Yes",
    ) -> gf.Component:
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
    
    params = {       
        'cdf_version': tech.techParams['CDFVersion'], 
        'rfmode': 1,
        'model': tech.techParams['rfpmosHV_model'],
        'w': w*1e-6,    # Width in μm
        'ws': eng_string_to_float(tech.techParams['rfpmosHV_defW'])/eng_string_to_float(tech.techParams['rfpmosHV_defNG'])*1e-6,   # Single Width in nm
        'l': l*1e-6,   # Length in μm
        'ng': ng,     # Number of gates
        'calculate': True,
        'cnt_rows': cnt_rows,
        'Met2Cont': Met2Cont,
        'gat_ring': gat_ring,
        'guard_ring': guard_ring,
        'Wmin': eng_string_to_float(tech.techParams['rfpmosHV_minW']),
        'Lmin': eng_string_to_float(tech.techParams['rfpmosHV_minL']),
        'm': 1,
        'trise': '',
        'Display': 'Selected'
    }

    c = generate_gf_from_ihp(cell_name="rfpmosHV", cell_params=params, function_name=rfpmosHVIHP())
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    # for i, port in enumerate(c.ports):
    #     port.orientation = 90 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    return c
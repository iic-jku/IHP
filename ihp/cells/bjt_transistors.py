import sys
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python")
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python/pycell4klayout-api/source/python/")

from sg13g2_pycell_lib.ihp.npn13G2_code import npn13G2 as npn13G2IHP
from sg13g2_pycell_lib.ihp.npn13G2L_code import npn13G2L as npn13G2LIHP
from sg13g2_pycell_lib.ihp.npn13G2V_code import npn13G2V as npn13G2VIHP
from sg13g2_pycell_lib.ihp.pnpMPA_code import pnpMPA as pnpMPAIHP


import gdsfactory as gf

from .utils import *
from functools import partial
from .. import tech


def npn13G2(
    STI = 0.44,
    baspolyx = 0.3,
    bipwinx = 0.07,
    bipwiny = 0.1,
    empolyx = 0.15,
    empolyy = 0.18,
    emitter_length = 0.9,
    emitter_width = 0.7,
    Nx = 1,
    Ny = 1,
    text = 'npn13G2',
    CMetY1 = 0,
    CMetY2 = 0,
    ) -> gf.Component:
    """Returns IHP npn13G2 BJT transistor as a gdsfactory Component.
    Args:
        model: model name
        Nx: number of emitter fingers
        Ny: number of emitter rows (doesnt do anything in IHP PyCell)
        emitter_length: emitter length in um
        emitter_width: emitter width in um
        bn: Bulk node connection
        m: multiplier
        text: label text
        #TODO
    Returns:
        gdsfactory Component
    """
    
    params = {
        'cdf_version': tech.techParams['CDFVersion'],
        'Display': 'Selected',
        'model': tech.techParams['npn13G2_model'],
        'Nx': Nx,
        'Ny': Ny,
        'le': emitter_length*1e-6,    # Length in μm
        'we': emitter_width*1e-6,   # Width in nm
        'STI': STI*1e-6,
        'baspolyx': baspolyx*1e-6,
        'bipwinx': bipwinx*1e-6,
        'bipwiny': bipwiny*1e-6,
        'empolyx': empolyx*1e-6,
        'empolyy': empolyy*1e-6,
        'Icmax': 3*1e-3, # hardcoded in IHP PyCell, not in techparams
        'Iarea': 1*1e-3, # hardcoded in IHP PyCell, not in techparams
        'area': 1, # hardcoded in IHP PyCell, not in techparams
        'bn': 'sub!',    # hardcoded in IHP PyCell, not in techparams
        'm': 1,      
        'trise': '',
        'Text': text,
        'CMetY1': 0, # hardcoded in IHP PyCell, not in techparams
        'CMetY2': 0, # hardcoded in IHP PyCell, not in techparams
    }

    c = generate_gf_from_ihp(cell_name="npn13G2", cell_params=params, function_name=npn13G2IHP())
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    # for i, port in enumerate(c.ports):
    #     port.orientation = 90 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    return c

def npn13G2L(
    Nx = 1,
    emitter_length = 1,
    emitter_width = 0.07,
    ) -> gf.Component:
    """Returns IHP npn13G2L BJT transistor as a gdsfactory Component.
    Args:
        model: model name
        Nx: number of emitter fingers
        emitter_length: emitter length in um
        emitter_width: emitter width in um
        bn: Bulk node connection
        m: multiplier
        text: label text
    Returns:
        gdsfactory Component
    """
    
    params = {
        'cdf_version': tech.techParams['CDFVersion'],
        'Display': 'Selected',
        'model': tech.techParams['npn13G2L_model'],
        'Nx': Nx,
        'le': emitter_length*1e-6,    # Length in μm
        'we': emitter_width*1e-6,   # Width in nm
        'Icmax': 3*1e-3, # hardcoded in IHP PyCell, not in techparams
        'Iarea': 1*1e-3, # hardcoded in IHP PyCell, not in techparams
        'area': 1, # hardcoded in IHP PyCell, not in techparams
        'bn': 'sub!',    # hardcoded in IHP PyCell, not in techparams
        'Vbe': '',
        'Vce': '',
        'm': 1,      
        'trise': '',
    }

    c = generate_gf_from_ihp(cell_name="npn13G2L", cell_params=params, function_name=npn13G2LIHP())
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    # for i, port in enumerate(c.ports):
    #     port.orientation = 90 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    return c

def npn13G2V(
    Nx = 1,
    emitter_length = 1,
    emitter_width = 0.12,
    ) -> gf.Component:
    """Returns IHP npn13G2V BJT transistor as a gdsfactory Component.
    Args:
        model: model name
        Nx: number of emitter fingers [1, 8]
        emitter_length: emitter length in um
        emitter_width: emitter width in um
        bn: Bulk node connection
        m: multiplier
        text: label text
    Returns:
        gdsfactory Component
    """
    
    params = {
        'cdf_version': tech.techParams['CDFVersion'],
        'Display': 'Selected',
        'model': tech.techParams['npn13G2V_model'],
        'Nx': Nx,
        'le': emitter_length*1e-6,    # Length in μm
        'we': emitter_width*1e-6,   # Width in nm
        'Icmax': 3*1e-3, # hardcoded in IHP PyCell, not in techparams
        'Iarea': 1*1e-3, # hardcoded in IHP PyCell, not in techparams
        'area': 1, # hardcoded in IHP PyCell, not in techparams
        'bn': 'sub!',    # hardcoded in IHP PyCell, not in techparams
        'Vbe': '',
        'Vce': '',
        'm': 1,      
        'trise': '',
    }

    c = generate_gf_from_ihp(cell_name="npn13G2V", cell_params=params, function_name=npn13G2VIHP())
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    # for i, port in enumerate(c.ports):
    #     port.orientation = 90 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    return c


def pnpMPA(
    width = 0.7,
    length = 2,
    m = 1,
    ) -> gf.Component:
    """Returns IHP npn13G2V BJT transistor as a gdsfactory Component.
    Args:
        model: model name
        Nx: number of emitter fingers [1, 8]
        emitter_length: emitter length in um
        emitter_width: emitter width in um
        bn: Bulk node connection
        m: multiplier
        text: label text
    Returns:
        gdsfactory Component
    """
    area = width * length
    perimeter = 2 * (width + length)
    params = {
        'cdf_version': tech.techParams['CDFVersion'],
        'Display': 'Selected',
        'model': tech.techParams['pnpMPA_model'],
        'Calculate': 'a',
        'w': width*1e-6,    # Length in μm
        'l': length*1e-6,   # Width in nm
        'a': area*1e-12,
        'p': perimeter*1e-6,
        'ac': 7.524*1e-12,
        'pc': 11.16*1e-6,
        'm': m,      # Multiplier
        'region': '',
        'trise': ''
    }

    c = generate_gf_from_ihp(cell_name="pnpMPA", cell_params=params, function_name=pnpMPAIHP())
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    # for i, port in enumerate(c.ports):
    #     port.orientation = 90 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    return c
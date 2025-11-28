import sys
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python")
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python/pycell4klayout-api/source/python/")

from sg13g2_pycell_lib.ihp.inductor2_code import inductor2 as inductor2IHP
from sg13g2_pycell_lib.ihp.inductor3_code import inductor3 as inductor3IHP


import gdsfactory as gf

from .utils import *
from functools import partial
from .. import tech


def inductor2(
    width = 2,
    space = 2.1,
    distance = 15.48,
    resistance = 1,
    inductance = 1,
    num_turns = 1,
    block_qrc = True,
    subE = False,
    guardRingType = "none",
    guardRingDistance = 1,
    ) -> gf.Component:
    """
    Args:
    
    Returns:
        gdsfactory Component
    
    
    """
    
    params = {
        'cdf_version': tech.techParams['CDFVersion'],
        'Display': 'Selected',
        'model': 'inductor2',
        'w': width*1e-6,
        's': space*1e-6,
        'd': distance*1e-6,
        'r': resistance*1e-3,
        'l': inductance*1e-9,
        'nr_r': num_turns,
        'blockqrc': block_qrc,
        'subE': subE,
        'lEstim': 33.303*1e-9,
        'rEstim': 577.7*1e-3,
        'Wmin': 2*1e-6,
        'Smin': 2.1*1e-6,
        'Dmin': 15.48*1e-6,
        'minNr_t': 1,
        'mergeStat': 16,
        'guardRingType': guardRingType,
        'guardRingDistance': guardRingDistance*1e-6   
    }

    c = generate_gf_from_ihp(cell_name="inductor2", cell_params=params, function_name=inductor2IHP())
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    # for i, port in enumerate(c.ports):
    #     port.orientation = 90 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    return c

def inductor3(
    width = 2,
    space = 2.1,
    distance = 25.84,
    resistance = 1,
    inductance = 1,
    num_turns = 1,
    block_qrc = True,
    subE = False,
    guardRingType = "none",
    guardRingDistance = 1,
    ) -> gf.Component:
    """
    Args:
    
    Returns:
        gdsfactory Component
    
    
    """
    
    params = {
        'cdf_version': tech.techParams['CDFVersion'],
        'Display': 'Selected',
        'model': 'inductor3',
        'w': width*1e-6,
        's': space*1e-6,
        'd': distance*1e-6,
        'r': resistance*1e-3,
        'l': inductance*1e-9,
        'nr_r': num_turns,
        'blockqrc': block_qrc,
        'subE': subE,
        'lEstim': 33.303*1e-9,
        'rEstim': 577.7*1e-3,
        'Wmin': 2*1e-6,
        'Smin': 2.1*1e-6,
        'Dmin': 25.84*1e-6,
        'minNr_t': 2,
        'mergeStat': 16,
        'guardRingType': guardRingType,
        'guardRingDistance': guardRingDistance*1e-6
    }

    c = generate_gf_from_ihp(cell_name="inductor3", cell_params=params, function_name=inductor3IHP())
    # Adjust port orientations, for metal1 so every other port points in the opposite direction
    # for i, port in enumerate(c.ports):
    #     port.orientation = 90 if port.name.startswith("DS_") and i % 2 == 1 else port.orientation
    return c
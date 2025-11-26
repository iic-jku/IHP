"""Antenna components for IHP PDK."""
import sys
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python")
sys.path.append("/foss/pdks/ihp-sg13g2/libs.tech/klayout/python/pycell4klayout-api/source/python/")
from sg13g2_pycell_lib.ihp.dantenna_code import dantenna as dantennaIHP
from sg13g2_pycell_lib.ihp.dpantenna_code import dpantenna as dpantennaIHP

from cni.tech import Tech

from cni.dlo import PCellWrapper
import pya
import gdsfactory as gf
from gdsfactory import Component
import os


@gf.cell
def dantenna(
    width: float = 0.78,
    length: float = 0.78,
    addRecLayer: str = 't'
) -> Component:
    """Create a 

    

    Args:
        

    Returns:
        gdsfactory.Component 
    """
    tech = Tech.get("SG13_dev")

    layout = pya.Layout()
    cell = layout.create_cell("DANTENNA")

    device = PCellWrapper(impl=dantennaIHP(), tech=tech)

    params = {
        "cdf_version": 8,
        "Display": "Selected",
        "model": "dantenna",
        "w": width*1e-6,
        "l": length*1e-6,
        "addRecLayer": addRecLayer,
    }

    # Convert params into a list in the order of device.param_decls
    param_values = [params.get(p.name, None) for p in device.param_decls]

    device.produce(
        layout=layout,
        layers={},
        parameters=param_values,
        cell=cell,
    )

    layout.write("temp.gds")
    c = gf.read.import_gds(gdspath="temp.gds")
    os.remove("temp.gds")
    return c


@gf.cell
def dpantenna(
    width: float = 0.78,
    length: float = 0.78,
    addRecLayer: str = 't'
) -> Component:
    """Create a 

    

    Args:
        

    Returns:
        gdsfactory.Component 
    """
    tech = Tech.get("SG13_dev")

    layout = pya.Layout()
    cell = layout.create_cell("DPANTENNA")

    device = PCellWrapper(impl=dpantennaIHP(), tech=tech)

    params = {
        "cdf_version": 8,
        "Display": "Selected",
        "model": "dpantenna",
        "w": width*1e-6,
        "l": length*1e-6,
        "addRecLayer": addRecLayer,
    }

    # Convert params into a list in the order of device.param_decls
    param_values = [params.get(p.name, None) for p in device.param_decls]

    device.produce(
        layout=layout,
        layers={},
        parameters=param_values,
        cell=cell,
    )

    layout.write("temp.gds")
    c = gf.read.import_gds(gdspath="temp.gds")
    os.remove("temp.gds")
    return c

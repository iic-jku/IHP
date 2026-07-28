import os

import gdsfactory as gf
import ihp

# activate the IHP PDK
ihp.PDK.activate()

# resolve output directory relative to this script, not the current working directory
GDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gds", "wpd")

# define frequency range
frequencys = [f * 1e9 for f in range(60, 301, 20)]

for f in frequencys:

    c = gf.Component("wpd_" + str(int(f / 1e9)) + "GHz")
    wpd = c.add_ref(ihp.cells.wilkinson_power_divider(
        connection_length=0.0,
        frequency=f,
        shape="U"
    ))

    # port 1: input, faces left -> shift the marker inward (+x)
    port1 = c.add_ref(gf.components.rectangle(size=(0.1, wpd.ports["e1"].width), layer=(201, 0)))
    port1.center = (wpd.ports["e1"].center)
    port1.move((0.05, 0))

    # ports 2/3: U-shape outputs are vertical: e2 faces up, e3 faces down
    # -> horizontal marker rectangles, shifted inward (-y / +y)
    port2 = c.add_ref(gf.components.rectangle(size=(wpd.ports["e2"].width, 0.1), layer=(202, 0)))
    port2.center = (wpd.ports["e2"].center)
    port2.move((0, -0.05))

    port3 = c.add_ref(gf.components.rectangle(size=(wpd.ports["e3"].width, 0.1), layer=(203, 0)))
    port3.center = (wpd.ports["e3"].center)
    port3.move((0, 0.05))

    c.write_gds(os.path.join(GDS_DIR, "wpd_" + str(int(f / 1e9)) + "GHz.gds"), with_metadata=False)

    c.show()

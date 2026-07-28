import os

import gdsfactory as gf
import ihp

# activate the IHP PDK
ihp.PDK.activate()

# resolve output directory relative to this script, not the current working directory
GDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gds", "blc")

# define frequency range
frequencys = [f * 1e9 for f in range(60, 301, 20)]

for f in frequencys:
    
    c = gf.Component("blc_" + str(int(f / 1e9)) + "GHz")
    blc = c.add_ref(ihp.cells.branch_line_coupler(
        connection_length=0.0,
        frequency=f
    ))
    
    port1 = c.add_ref(gf.components.rectangle(size=(0.1, blc.ports["e1"].width), layer=(201,0)))
    port1.center = (blc.ports["e1"].center)
    port1.move((0.05,0))
    port2 = c.add_ref(gf.components.rectangle(size=(0.1, blc.ports["e2"].width), layer=(202,0)))
    port2.center = (blc.ports["e2"].center)
    port2.move((-0.05,0))

    port3 = c.add_ref(gf.components.rectangle(size=(0.1, blc.ports["e3"].width), layer=(203,0)))
    port3.center = (blc.ports["e3"].center)
    port3.move((-0.05,0))

    port4 = c.add_ref(gf.components.rectangle(size=(0.1, blc.ports["e4"].width), layer=(204,0)))
    port4.center = (blc.ports["e4"].center)
    port4.move((0.05,0))
    
    c.write_gds(os.path.join(GDS_DIR, "blc_" + str(int(f / 1e9)) + "GHz.gds"), with_metadata=False)

    c.show()


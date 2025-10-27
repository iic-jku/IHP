import gdsfactory as gf
import ihp
import sys
import os

# paths_to_remove = [
#     "/foss/pdks/ihp-sg13g2/libs.tech/klayout/python",
#     "/foss/pdks/ihp-sg13g2/libs.tech/klayout/python/pycell4klayout-api/source/python/"
# ]

# for p in paths_to_remove:
#     if p in sys.path:
#         sys.path.remove(p)

# import sys

# # Print every path entry on its own line
# for p in sys.path:
#     print(p)

ihp.PDK.activate()


# c= ihp.cells.straight(length = 30, cross_section="metal5_routing")
# c.show()


# ----------------------------------------------------------------
# not working anymore due to changes in via array generation

# c = ihp.cells.via_stack(bottom_layer="Metal1", top_layer="TopMetal2", vn_columns=3, vn_rows=4)
# c.show()

# ----------------------------------------------------------------


# c = ihp.cells.via_stack_test(bottom_layer="TopMetal2", top_layer="Metal2", vn_columns=3, vn_rows=4)
# c.draw_ports()
# c.show()

# ----------------------------------------------------------------

# c = ihp.cells.nmos(width=0.15, length=0.13, nf=1, m=1)
# c.show()

# ----------------------------------------------------------------

# c = gf.import_gds("ihp/gds/test.gds").copy()
# c.pprint_ports()
# c.show()

# c_with_ports = gf.add_ports.add_ports_from_boxes(c, pin_layer=(ihp.LAYER.Metal1pin), port_type="electrical", port_name_prefix="DS", ports_on_short_side=True)
# c_with_ports = gf.add_ports.add_ports_from_boxes(c, pin_layer=(ihp.LAYER.GatPolypin), port_type="electrical", port_name_prefix="G", ports_on_short_side=True)
# c_with_ports.pprint_ports()
# c_with_ports.draw_ports()
# c_with_ports.show()

# ----------------------------------------------------------------

# c = gf.read.import_gds("ihp/gds/test2.gds")
# c.pprint_ports()
# c.show()

# c_with_ports = gf.add_ports.add_ports_from_boxes(c, pin_layer=(ihp.LAYER.Metal1drawing), port_type="electrical", port_name_prefix="DS", ports_on_short_side=True)
# c_with_ports = gf.add_ports.add_ports_from_boxes(c, pin_layer=(ihp.LAYER.GatPolydrawing), port_type="electrical", port_name_prefix="G", ports_on_short_side=True)
# c_with_ports.pprint_ports()
# c_with_ports.draw_ports()
# c_with_ports.show()

# ----------------------------------------------------------------

# c = gf.Component()
# nm_1 = ihp.cells.my_nmos(ng = 10).copy()
# nm_2 = ihp.cells.my_nmos(ng = 8).copy()
# nm_1_ref = c.add_ref(nm_1)
# nm_1_ref_2 = c.add_ref(nm_1)
# nm_1_ref_2.move((0, 1))
# pm = c.add_ref(ihp.cells.my_pmos(ng = 5).copy())
# nm_2_ref = c.add_ref(nm_2)

# nm_2.move((0, -2))
# pm.move((0, -1))
# c.show()


# wg = ihp.cells.straight(length = 2, width = 0.16, cross_section="metal1_routing")
# wg.draw_ports()
# wg_ref = c.add_ref(wg)

# wg_ref.connect("e1", nm_1_ref.ports["DS_9"], allow_width_mismatch=True)
# nm_2_ref.connect("DS_1", wg_ref.ports["e2"], allow_width_mismatch=True)

# nm_1.draw_ports()
# nm_2.draw_ports()
# c.draw_ports()
# print("NMOS 1 ports:")
# nm_1.pprint_ports()
# c.add_ports(nm_1.ports)
# c.add_ports(nm_2.ports)
# c.add_ports(pm.ports)
# print("Component ports:")
# c.pprint_ports()
# c.show()




# ----------------------------------------------------------------

# c = ihp.cells.my_nmos().copy()
# c.move((0,1))
# c << ihp.cells.my_nmos(ng = 2).copy()
# c.draw_ports()
# c.show()

# ----------------------------------------------------------------

# c = ihp.cells.my_nmos(ng = 5).copy()
# c.pprint_ports()
# c.draw_ports()
# c.show()

# ----------------------------------------------------------------

# c = ihp.cells.my_nmosHV(ng = 15).copy()
# c.pprint_ports()
# c.draw_ports()
# c.move((0,2))
# c.show()

# c.add_ref(ihp.cells.my_pmosHV(ng=15).copy())
# c.draw_ports()
# c.show()

# ----------------------------------------------------------------

c = ihp.cells.my_rfnmos().copy()
c.pprint_ports()
c.draw_ports()
c.show()
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
# nm_1 = ihp.cells.nmos(ng = 10).copy()
# nm_2 = ihp.cells.nmos(ng = 8).copy()
# nm_1_ref = c.add_ref(nm_1)
# nm_1_ref_2 = c.add_ref(nm_1)
# nm_1_ref_2.move((0, 1))
# pm = c.add_ref(ihp.cells.pmos(ng = 5).copy())
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
# test mos_transistors.py 


c = gf.Component()

c.add_ref(ihp.cells.nmos(ng = 1, guardRingType="psub", guardRingDistance=1))
c.move((0,4))

c.add_ref(ihp.cells.pmos(ng=1, guardRingType="nwell", guardRingDistance=1))
c.move((0,5))

c.add_ref(ihp.cells.nmosHV(ng = 1, guardRingType="psub", guardRingDistance=1))
c.move((0,5))

c.add_ref(ihp.cells.pmosHV(ng=1, guardRingType="nwell", guardRingDistance=1))
c.move((1.5,3))

c.add_ref(ihp.cells.rfnmos(ng = 1)).rotate(-90)
c.move((0,6))
c.show()

# nm = c.add_ref(ihp.cells.nmos(w=1, l=0.72).copy())
# nm.rotate(90)
# c. move((0,6))


# c.add_ref(ihp.cells.rfnmosHV().copy())

# c.pprint_ports()
# c.draw_ports()
# c.show()

# c.move((0,5))

# c.add_ref(ihp.cells.rfpmos().copy())
# c.pprint_ports()
# c.draw_ports()
# c.show()

# c.move((0,6))

# c.add_ref(ihp.cells.rfpmosHV().copy())
# c.pprint_ports()
# c.draw_ports()
# c.show()

# ----------------------------------------------------------------
# c = gf.Component()

# c.add_ref(ihp.cells.npn13G2().copy())
# c.show()
# c.move((4,11))

# c.add_ref(ihp.cells.npn13G2L().copy())
# c.show()
# c.move((0,8))

# c.add_ref(ihp.cells.npn13G2V().copy())
# c.show()
# c.move((-3.5,4))

# c.add_ref(ihp.cells.pnpMPA().copy())
# c.show()


# ----------------------------------------------------------------
# c = gf.Component()

# c.add_ref(ihp.cells.inductor2().copy())
# c.show()
# c.move((-100, 10))

# c.add_ref(ihp.cells.inductor3().copy())
# c.show()

# -----------------------------------------------------------------
# c = gf.Component()

# c.add_ref(ihp.cells.rhigh(length=10))
# c.move((5,0))
# c.add_ref(ihp.cells.rhigh(length=20, width=1))

# c.move((5,0))
# c.add_ref(ihp.cells.rppd(length=10))
# c.move((5,0))
# c.add_ref(ihp.cells.rppd(length=20, width=1))
# c.show()

# c.move((5,0))
# c.add_ref(ihp.cells.rsil(length=10))
# c.move((5,0))
# c.add_ref(ihp.cells.rsil(length=20, width=1))
# c.show()


# -----------------------------------------------------------------
# c = gf.Component()

# c.add_ref(ihp.cells.capacitors.cmim(width="10u", length="10u"))
# c.move((40,0))
# c.add_ref(ihp.cells.capacitors.cmim(width="20u", length="20u"))


# c.move((-40,35))
# c.add_ref(ihp.cells.capacitors.rfcmim(width="10u", length="10u"))
# c.move((40,0))
# c.add_ref(ihp.cells.capacitors.rfcmim(width="20u", length="20u"))

# c.move((-40,35))
# c.add_ref(ihp.cells.capacitors.svaricap(Nx=1))
# c.move((40,0))
# c.add_ref(ihp.cells.capacitors.svaricap(Nx=10))
# c.show()

# -----------------------------------------------------------------

# c = gf.Component()

# c.add_ref(ihp.cells.via_stack(top_layer="TopMetal2", bottom_layer="Metal1"))
# c.show()

# -----------------------------------------------------------------

# c = gf.Component()

# c.add_ref(ihp.cells.passives.esd(model="diodevdd_2kv"))
# c.show()

# c.move((0,5))
# c.add_ref(ihp.cells.passives.ptap1())
# c.show()

# c.move((0,5))
# c.add_ref(ihp.cells.passives.ntap1())
# c.show()


# c.move((200,200))
# c.add_ref(ihp.cells.passives.sealring())
# c.show()

# -----------------------------------------------------------------

# c = gf.Component()

# c.add_ref(ihp.cells.bondpads.bondpad(shape="octagon"))
# c.show()

# c.move((0,100))
# c.add_ref(ihp.cells.bondpads.bondpad_array(n_pads=4, pad_pitch=100))
# c.show()


# -----------------------------------------------------------------

# c = gf.Component()

# c.add_ref(ihp.cells.via_stacks.no_filler_stack())
# c.show()

# -----------------------------------------------------------------

# c = gf.Component()
# c.add_ref(ihp.cells.antennas.dantenna())
# c.show()

# c.move((0,2))

# c.add_ref(ihp.cells.antennas.dpantenna())
# c.show()
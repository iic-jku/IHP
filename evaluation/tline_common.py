import itertools
import os

import gdsfactory as gf

import ihp

ihp.PDK.activate()

# metal stack, ordered from bottom (possible ground) to top (possible signal)
METAL_STACK = [
    "metal1_routing",
    "metal2_routing",
    "metal3_routing",
    "metal4_routing",
    "metal5_routing",
    "topmetal1_routing",
    "topmetal2_routing",
]

# DRC minimum width per signal layer (um), narrower widths are skipped for that layer
MIN_WIDTH = {
    "metal1_routing": 0.14,
    "metal2_routing": 0.16,
    "metal3_routing": 0.20,
    "metal4_routing": 0.20,
    "metal5_routing": 0.20,
    "topmetal1_routing": 1.0,
    "topmetal2_routing": 2.0,
}

# every usable (ground, signal) pair, ground always below signal in the stack
METAL_STACKS = [(METAL_STACK[i], METAL_STACK[j]) for i, j in itertools.combinations(range(len(METAL_STACK)), 2)]

# (ground, signal) pairs realistic for RF routing: Metal1-Metal5 are thin,
# high-resistance-per-square logic/routing layers that nobody would route a real RF
# line on, so only stacks with a thick top metal (TopMetal1/TopMetal2) as the signal
# layer are included - which is what those layers exist for.
RF_METAL_STACKS = [
    (ground, signal) for ground, signal in METAL_STACKS if signal in ("topmetal1_routing", "topmetal2_routing")
]


def short_name(cross_section: str) -> str:
    """Strip the '_routing' suffix off a cross-section name for use in filenames
    (e.g. 'topmetal2_routing' -> 'topmetal2')."""
    return cross_section.removesuffix("_routing")


def fmt_width(width: float) -> str:
    """Format a width for use in a filename, dropping any trailing '.0' (2.0 -> '2', 0.5 -> '0.5')."""
    return f"{width:g}"


def write_tline_gds(tline: gf.Component, name: str, gds_dir: str) -> None:
    """Wrap a tline component with port markers on layers 201/202 and write it to gds_dir."""
    c = gf.Component(name)
    t = c.add_ref(tline)

    port1 = c.add_ref(gf.components.rectangle(size=(0.1, t.ports["e1"].width), layer=(201, 0)))
    port1.center = t.ports["e1"].center
    port1.move((0.05, 0))

    port2 = c.add_ref(gf.components.rectangle(size=(0.1, t.ports["e2"].width), layer=(202, 0)))
    port2.center = t.ports["e2"].center
    port2.move((-0.05, 0))

    c.write_gds(os.path.join(gds_dir, f"{name}.gds"), with_metadata=False)

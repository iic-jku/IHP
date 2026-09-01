import os

from tline_common import (
    MIN_WIDTH,
    RF_METAL_STACKS,
    fmt_width,
    short_name,
    write_tline_gds,
)

import ihp

# structures for a Zc(w) plot per metal stack.
# Zc is roughly frequency-independent, so a single frequency point is enough,
# unlike the loss(w)/mm sweep which genuinely varies with frequency.
#
# restricted to RF_METAL_STACKS (see tline_common.py), same as the loss sweep:
# Metal1-Metal5 aren't realistic RF signal layers, so a Zc curve for those stacks
# wouldn't be actionable for RF design either.

GDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gds", "tline_z0")

# signal widths to sweep (um)
widths = [1.64, 2, 2.5, 3, 5, 7, 7.2, 7.5, 8, 8.5, 9, 10, 12.5, 15, 20]

# fixed line length (um)
length = 1000

# single simulation frequency (Hz)
frequency = 200e9

for ground_cross_section, signal_cross_section in RF_METAL_STACKS:
    stack_name = f"{short_name(signal_cross_section)}_over_{short_name(ground_cross_section)}"
    min_width = MIN_WIDTH[signal_cross_section]

    for width in widths:
        if width < min_width:
            continue

        tline = ihp.cells.tline(
            length=length,
            signal_cross_section=signal_cross_section,
            ground_cross_section=ground_cross_section,
            width=width,
        )

        name = f"tline_{stack_name}_w{fmt_width(width)}um_{int(frequency / 1e9)}GHz"
        write_tline_gds(tline, name, GDS_DIR)

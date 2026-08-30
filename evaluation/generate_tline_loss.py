import os

from tline_common import (
    MIN_WIDTH,
    RF_METAL_STACKS,
    fmt_width,
    short_name,
    write_tline_gds,
)

import ihp

# structures for a loss(w)/mm plot per metal stack.
# loss depends on frequency (skin effect, dielectric loss), so the full
# frequency band is swept here, unlike the roughly frequency-independent Zc(w) sweep.
#
# loss is extracted via the two-length (multiline) method: two lines of the same
# width/stack/frequency but different length (length1, length2) are simulated with
# identical port launches. Taking eigenvalues of T2 . inv(T1) (ratio of ABCD
# matrices) cancels any port/launch effect common to both lines exactly, leaving
# only the propagation constant of the added length dL = length2 - length1 - unlike
# extracting from a single line, this doesn't rely on trusting an assumed port model.
#
# this sweep is expensive (full frequency band x two lengths per point), so it's
# restricted to RF_METAL_STACKS rather than every metal pair (see tline_common.py).

GDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gds", "tline_loss")

# signal widths to sweep (um)
widths = [0.5, 1, 2, 3, 5, 7, 10, 15, 20]
widths = [2.5,8, 9, 12.5]  

# two line lengths (um) for two-length de-embedding; dL = length2 - length1
length1 = 500
length2 = 1000

# frequencies to sweep (Hz)
frequencys = [f * 1e9 for f in range(60, 301, 20)]
frequencys = [200e9]  # --- IGNORE ---

for ground_cross_section, signal_cross_section in RF_METAL_STACKS:
    stack_name = f"{short_name(signal_cross_section)}_over_{short_name(ground_cross_section)}"
    min_width = MIN_WIDTH[signal_cross_section]

    for width in widths:
        if width < min_width:
            continue

        for length in (length1, length2):
            tline = ihp.cells.tline(
                length=length,
                signal_cross_section=signal_cross_section,
                ground_cross_section=ground_cross_section,
                width=width,
            )

            for f in frequencys:
                name = f"tline_{stack_name}_w{fmt_width(width)}um_l{length}um_{int(f / 1e9)}GHz"
                write_tline_gds(tline, name, GDS_DIR)

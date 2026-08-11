import os

from tline_common import METAL_STACKS, short_name, write_tline_gds

import ihp

# general S-parameter verification sweep: fixed 50 ohm lines across lengths,
# metal stacks and frequency bands (distinct from the Zc(w)/loss(w) plot sweeps)

GDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gds", "tline_sparams")

# lengths to sweep (um)
lengths = [10, 25, 50, 100, 200, 500]
lengths = [1000]
# frequencies to sweep (Hz) - sets the simulated frequency band via the filename,
# tline geometry itself is frequency-independent
frequencys = [f * 1e9 for f in range(60, 301, 20)]

# target characteristic impedance Zc for all lines (ohm).
# (the ihp tline() cell names this parameter Z0, so it's passed as Z0=ZC_TARGET below)
ZC_TARGET = 50.0

for ground_cross_section, signal_cross_section in METAL_STACKS:
    stack_name = f"{short_name(signal_cross_section)}_over_{short_name(ground_cross_section)}"

    for length in lengths:
        try:
            tline = ihp.cells.tline(
                length=length,
                signal_cross_section=signal_cross_section,
                ground_cross_section=ground_cross_section,
                Z0=ZC_TARGET,
            )
        except ValueError as e:
            print(f"skipping {stack_name}: {e}")
            break

        for f in frequencys:
            name = f"tline_{stack_name}_l{length}um_{int(f / 1e9)}GHz"
            write_tline_gds(tline, name, GDS_DIR)

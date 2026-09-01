"""Build the IHP cells in a few variations each and send them to KLayout.

Replaces the per-module `if __name__ == "__main__":` blocks, which could not
be run: as a script they broke on the package-relative imports, and as a module
they never activated the PDK, so `tech.LAYER` could not be resolved.

Usage:
    python show.py                      # every cell, every variation
    python show.py cmomf cmomi          # only the named cells
    python show.py --list               # what would be built, without building
    python show.py --gds gallery.gds    # also write the gallery to a file
    python show.py --no-show            # build and report only
"""

import argparse

import gdsfactory as gf

import ihp
from ihp import tech

# Registered by get_cells but a helper rather than a layout cell.
SKIP = {"generate_gf_from_ihp"}

# Variations worth looking at. Any registered cell not listed here is built
# once with its defaults. The entries carry over the examples that used to live
# in the per-module __main__ blocks.
VARIATIONS = {
    # capacitors
    "cmim": [{"width": 10, "length": 10}, {"width": 20, "length": 20}, {"C": 1e-12}],
    "rfcmim": [{"width": 10, "length": 10}, {"width": 20, "length": 20}],
    "cmomf": [{}, {"width": 10, "length": 20}, {"mmin": 2, "mmax": 4}, {"mmin": 3, "mmax": 3}],
    "cmomi": [
        {"feed": "double"},
        {"feed": "same"},
        {"feed": "none"},
        {"width": 10, "length": 20},
        {"mmin": 2, "mmax": 4, "feed": "same"},
    ],
    "svaricap": [{"Nx": 1}, {"Nx": 10, "guardRingType": "nwell", "guardRingDistance": 2}],
    # resistors
    "rsil": [{"width": 1.0, "length": 10.0}],
    "rppd": [{"width": 0.8, "length": 20.0}],
    "rhigh": [{"width": 1.4, "length": 50.0}],
    # passives
    # all six models: the diodes carry PAD/VDD/VSS, the clamps VSS/VDD
    "esd": [
        {"model": "diodevdd_2kv"},
        {"model": "diodevss_2kv"},
        {"model": "diodevdd_4kv"},
        {"model": "diodevss_4kv"},
        {"model": "nmoscl_2"},
        {"model": "nmoscl_4"},
    ],
    "ptap1": [{"width": 2.0, "length": 2.0}],
    "ntap1": [{"width": 2.0, "length": 2.0}],
    "sealring": [{"width": 500, "height": 500}],
    "guard_ring": [{"width": 10, "height": 10, "guardRingType": "nwell"}],
    # bondpads
    # flipChip needs octagon or circle: with square the PCell prints a
    # warning, raises internally and hands back an EMPTY cell
    "bondpad": [{"shape": "octagon"}, {"shape": "square"}, {"shape": "octagon", "flipChip": "yes"}],
    "bondpad_array": [{"config": "GSG"}, {"config": "GSGSG"}],
    # via stacks
    "via_stack": [{"bottom_layer": "Metal1", "top_layer": "Metal5"}],
    # transmission lines: both need width or Z0, they have no usable default
    "tline": [{"width": 7.2}, {"Z0": 50}],
    "tline_corner": [{"width": 7.2}],
    # transistors
    # w is the TOTAL width and the per-finger minimum scales with ng,
    # so a multi-finger variation has to widen w along with it
    "nmos": [{}, {"w": 2.4, "ng": 4}],
    "pmos": [{}, {"w": 2.4, "ng": 4}],
}


def _label(name: str, kwargs: dict) -> str:
    """Short human-readable name for one variation."""
    if not kwargs:
        return f"{name}()"
    args = ", ".join(f"{k}={v!r}" if isinstance(v, str) else f"{k}={v}" for k, v in kwargs.items())
    return f"{name}({args})"


def _plan(selected: list[str] | None) -> list[tuple[str, dict]]:
    """Cell name and kwargs for every variation to build, in name order."""
    names = sorted(n for n in ihp.PDK.cells if n not in SKIP)
    if selected:
        unknown = sorted(set(selected) - set(names))
        if unknown:
            raise SystemExit(f"unknown cell(s): {', '.join(unknown)}\nrun --list to see what is available")
        names = [n for n in names if n in selected]
    return [(n, kw) for n in names for kw in VARIATIONS.get(n, [{}])]


def _is_empty(c: gf.Component) -> bool:
    """True when a cell has no geometry at all.

    Some PCells report a bad parameter combination by printing a message and
    raising inside their own genLayout, which the KLayout wrapper swallows, so
    the call returns an empty cell instead of failing. bondpad(shape='square',
    flipChip='yes') is one, and it looks like a success otherwise. The bounding
    box is the test rather than a shape count, because the container cells draw
    nothing themselves and hold only references.
    """
    return c.dbbox().empty()


def _info(c: gf.Component) -> str:
    """The values a cell reports about itself, for the summary line."""
    bits = []
    if "C" in c.info:
        bits.append(f"C={c.info['C'] * 1e15:.3f}fF")
    if "R" in c.info:
        bits.append(f"R={c.info['R']:.3f}ohm")
    bb = c.dbbox()
    bits.append(f"{bb.width():.2f}x{bb.height():.2f}um")
    bits.append(f"{len(c.ports)} ports")
    return "  ".join(bits)


def _gallery(built: list[tuple[str, gf.Component]], max_row_um: float = 1500.0, gap: float = 20.0) -> gf.Component:
    """Lay the built cells out in rows, each labelled on the TEXT layer."""
    gallery = gf.Component()
    x = y = row_height = 0.0
    for label, cell in built:
        bb = cell.dbbox()
        if x > 0 and x + bb.width() > max_row_um:
            x = 0.0
            y += row_height + 3 * gap
            row_height = 0.0
        ref = gallery.add_ref(cell)
        ref.movex(x - bb.left)
        ref.movey(y - bb.bottom)
        gallery.add_label(text=label, position=(x, y - gap), layer=tech.LAYER.TEXTdrawing)
        x += bb.width() + gap
        row_height = max(row_height, bb.height())
    return gallery


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("cells", nargs="*", help="cell names to build (default: all)")
    parser.add_argument("--list", action="store_true", help="list the variations without building them")
    parser.add_argument("--gds", metavar="PATH", help="write the gallery to this GDS file")
    parser.add_argument("--no-show", action="store_true", help="do not send the gallery to KLayout")
    args = parser.parse_args()

    ihp.PDK.activate()
    plan = _plan(args.cells or None)

    if args.list:
        for name, kwargs in plan:
            print(_label(name, kwargs))
        print(f"\n{len(plan)} variations across {len({n for n, _ in plan})} cells")
        return

    built: list[tuple[str, gf.Component]] = []
    failed: list[tuple[str, str]] = []
    for name, kwargs in plan:
        label = _label(name, kwargs)
        try:
            cell = ihp.PDK.cells[name](**kwargs)
        except Exception as e:  # a broken cell must not stop the rest of the gallery
            failed.append((label, f"{type(e).__name__}: {e}"))
            print(f"FAIL  {label}\n        {type(e).__name__}: {str(e)[:100]}")
            continue
        if _is_empty(cell):
            failed.append((label, "drew nothing (the PyCell swallowed an error)"))
            print(f"EMPTY {label}\n        drew nothing (the PyCell swallowed an error)")
            continue
        built.append((label, cell))
        print(f"ok    {label:44} {_info(cell)}")

    print(f"\n{len(built)} built, {len(failed)} failed")
    if failed:
        print("failed:")
        for label, err in failed:
            print(f"  {label:44} {err[:100]}")

    if not built:
        return

    gallery = _gallery(built)
    print(f"gallery: {gallery.dbbox().width():.1f} x {gallery.dbbox().height():.1f} um")
    if args.gds:
        gallery.write_gds(args.gds, with_metadata=False)
        print(f"wrote {args.gds}")
    if not args.no_show:
        gallery.show()


if __name__ == "__main__":
    main()

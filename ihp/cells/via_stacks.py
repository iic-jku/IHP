"""Via stack components for IHP PDK."""

import gdsfactory as gf
from gdsfactory import Component
from .. import tech

# Define metal and via layers for IHP PDK
METAL_LAYERS = {
    "Metal1": tech.LAYER.METAL1,
    "Metal2": tech.LAYER.METAL2,
    "Metal3": tech.LAYER.METAL3,
    "Metal4": tech.LAYER.METAL4,
    "Metal5": tech.LAYER.METAL5,
    "TopMetal1": tech.LAYER.TOPMETAL1,
    "TopMetal2": tech.LAYER.TOPMETAL2,
}

VIA_LAYERS = {
    "Via1": tech.LAYER.VIA1,
    "Via2": tech.LAYER.VIA2,
    "Via3": tech.LAYER.VIA3,
    "Via4": tech.LAYER.VIA4,
    "TopVia1": tech.LAYER.TOPVIA1,
    "TopVia2": tech.LAYER.TOPVIA2,
}

# Via design rules (in micrometers)
VIA_RULES = {
    "Via1": {
        "size": tech.TECH.via1_size,
        "spacing": tech.TECH.via1_spacing,
        "enclosure": tech.TECH.via1_enc_metal,
    },
    "Via2": {
        "size": tech.TECH.via1_size,
        "spacing": tech.TECH.via1_spacing,
        "enclosure": tech.TECH.via1_enc_metal,
    },
    "Via3": {
        "size": tech.TECH.via1_size,
        "spacing": tech.TECH.via1_spacing,
        "enclosure": tech.TECH.via1_enc_metal,
    },
    "Via4": {
        "size": tech.TECH.via1_size,
        "spacing": tech.TECH.via1_spacing,
        "enclosure": tech.TECH.via1_enc_metal,
    },
    "TopVia1": {
        "size": tech.TECH.topvia1_size,
        "spacing": tech.TECH.topvia1_spacing,
        "enclosure": tech.TECH.topvia1_enc_metal,
    },
    "TopVia2": {
        "size": tech.TECH.topvia2_size,
        "spacing": tech.TECH.topvia2_spacing,
        "enclosure": tech.TECH.topvia2_enc_metal,
    },
}


def get_via_name(bottom_metal: str, top_metal: str) -> str | None:
    """Get the via layer name between two metal layers.

    Args:
        bottom_metal: Bottom metal layer name.
        top_metal: Top metal layer name.

    Returns:
        Via layer name or None if not adjacent.
    """
    via_mapping = {
        ("Metal1", "Metal2"): "Via1",
        ("Metal2", "Metal3"): "Via2",
        ("Metal3", "Metal4"): "Via3",
        ("Metal4", "Metal5"): "Via4",
        ("Metal5", "TopMetal1"): "TopVia1",
        ("TopMetal1", "TopMetal2"): "TopVia2",
    }

    if (bottom_metal, top_metal) in via_mapping:
        return via_mapping[(bottom_metal, top_metal)]
    return None


@gf.cell
def via_array(
    via_type: str = "Via1",
    columns: int = 2,
    rows: int = 2,
    via_size: float | None = None,
    via_spacing: float | None = None,
    via_enclosure: float | None = None,
) -> Component:
    """Create an array of vias.

    Args:
        via_type: Type of via (Via1, Via2, Via3, Via4, TopVia1, TopVia2).
        columns: Number of via columns.
        rows: Number of via rows.
        via_size: Via size in micrometers (uses default if None).
        via_spacing: Via spacing in micrometers (uses default if None).
        via_enclosure: Metal enclosure in micrometers (uses default if None).

    Returns:
        Component with via array.
    """
    c = Component()

    # Get via parameters
    if via_type not in VIA_LAYERS:
        raise ValueError(f"Unknown via type: {via_type}")

    via_layer = VIA_LAYERS[via_type]
    rules = VIA_RULES[via_type]

    # Use provided values or defaults
    # size = via_size if via_size is not None else rules["size"]
    # spacing = via_spacing if via_spacing is not None else rules["spacing"]
    # enclosure = via_enclosure if via_enclosure is not None else rules["enclosure"]
    size = via_size 
    spacing = via_spacing 
    enclosure = via_enclosure 
    # Create via array
    for col in range(columns):
        for row in range(rows):
            x = col * spacing
            y = row * spacing

            via = gf.components.rectangle(
                size=(size, size),
                layer=via_layer,
            )
            via_ref = c.add_ref(via)
            via_ref.move((x + col * size, y + row * size))

    # Calculate total dimensions
    array_width = size if columns == 1 else (columns - 1) * spacing + size * columns
    array_height = size if rows == 1 else (rows - 1) * spacing + size * rows
    # Center the array
    c.move((-array_width / 2, -array_height / 2))
    
    #c.move((-array_width / 2, -array_height / 2))
    # Add metadata
    c.info["via_type"] = via_type
    c.info["columns"] = columns
    c.info["rows"] = rows
    c.info["array_width"] = array_width
    c.info["array_height"] = array_height
    c.info["enclosure_width"] = array_width + 2 * enclosure
    c.info["enclosure_height"] = array_height + 2 * enclosure

    return c


@gf.cell
def via_stack(
    bottom_layer: str = "Metal1",
    top_layer: str = "Metal2",
    size: tuple[float, float] = (10.0, 10.0),
    vn_columns: int = 2,
    vn_rows: int = 2,
    vt1_columns: int = 1,
    vt1_rows: int = 1,
    vt2_columns: int = 1,
    vt2_rows: int = 1,
) -> Component:
    """Create a via stack connecting multiple metal layers.

    Args:
        bottom_layer: Bottom metal layer name.
        top_layer: Top metal layer name.
        size: Size of the metal stack (width, height) in micrometers.
        vn_columns: Number of columns for normal vias (Via1-Via4).
        vn_rows: Number of rows for normal vias.
        vt1_columns: Number of columns for TopVia1.
        vt1_rows: Number of rows for TopVia1.
        vt2_columns: Number of columns for TopVia2.
        vt2_rows: Number of rows for TopVia2.

    Returns:
        Component with via stack.
    """
    c = Component()

    # Validate layers
    metal_order = [
        "Metal1",
        "Metal2",
        "Metal3",
        "Metal4",
        "Metal5",
        "TopMetal1",
        "TopMetal2",
    ]

    if bottom_layer not in metal_order or top_layer not in metal_order:
        raise ValueError(f"Invalid metal layers: {bottom_layer}, {top_layer}")

    bottom_idx = metal_order.index(bottom_layer)
    top_idx = metal_order.index(top_layer)

    if bottom_idx >= top_idx:
        raise ValueError(
            f"Bottom layer must be below top layer: {bottom_layer} -> {top_layer}"
        )

    width, height = size

    # Add metal layers
    for idx in range(bottom_idx, top_idx + 1):
        metal_name = metal_order[idx]
        metal_layer = METAL_LAYERS[metal_name]

        metal = gf.components.rectangle(
            size=(width, height),
            layer=metal_layer,
            centered=True,
        )
        c.add_ref(metal)

    # Add vias between layers
    for idx in range(bottom_idx, top_idx):
        bottom_metal = metal_order[idx]
        top_metal = metal_order[idx + 1]
        via_name = get_via_name(bottom_metal, top_metal)

        if via_name:
            rules = VIA_RULES[via_name]
            via_size = rules["size"]
            via_spacing = rules["spacing"]
            via_enclosure = rules["enclosure"]

            # Determine number of vias based on type
            if "TopVia" in via_name:
                if via_name == "TopVia1":
                    columns = vt1_columns
                    rows = vt1_rows
                else:  # TopVia2
                    columns = vt2_columns
                    rows = vt2_rows
            else:
                columns = vn_columns
                rows = vn_rows

            # Calculate maximum number of vias that fit
            max_columns = int((width - 2 * via_enclosure - via_size) / via_spacing) + 1
            max_rows = int((height - 2 * via_enclosure - via_size) / via_spacing) + 1

            # Use minimum of requested and maximum
            actual_columns = min(columns, max_columns)
            actual_rows = min(rows, max_rows)

            if actual_columns > 0 and actual_rows > 0:
                # Create via array
                via_array_comp = via_array(
                    via_type=via_name,
                    columns=actual_columns,
                    rows=actual_rows,
                    via_size=via_size,
                    via_spacing=via_spacing,
                    via_enclosure=via_enclosure,
                )

                # Center the via array
                array_width = via_array_comp.info["array_width"]
                array_height = via_array_comp.info["array_height"]

                via_ref = c.add_ref(via_array_comp)
                via_ref.move((-array_width / 2, -array_height / 2))

    # Add ports
    c.add_port(
        name="bottom",
        center=(0, 0),
        width=width,
        orientation=0,
        layer=METAL_LAYERS[bottom_layer],
        port_type="electrical",
    )

    c.add_port(
        name="top",
        center=(0, 0),
        width=width,
        orientation=0,
        layer=METAL_LAYERS[top_layer],
        port_type="electrical",
    )

    # Add metadata
    c.info["bottom_layer"] = bottom_layer
    c.info["top_layer"] = top_layer
    c.info["width"] = width
    c.info["height"] = height
    c.info["n_layers"] = top_idx - bottom_idx + 1

    return c

@gf.cell
def via_stack_test(
    bottom_layer: str = "Metal1",
    top_layer: str = "Metal2",
    vn_columns: int = 2,
    vn_rows: int = 2,
    vt1_columns: int = 1,
    vt1_rows: int = 1,
    vt2_columns: int = 1,
    vt2_rows: int = 1,
) -> Component:
    """Create a via stack test component.

    Args:
        bottom_layer: Bottom metal layer name.
        top_layer: Top metal layer name.
        vn_columns: Number of columns for normal vias (Via1-Via4).
        vn_rows: Number of rows for normal vias.
        vt1_columns: Number of columns for TopVia1.
        vt1_rows: Number of rows for TopVia1.
        vt2_columns: Number of columns for TopVia2.
        vt2_rows: Number of rows for TopVia2.

    Returns:
        Component with via stack test.
    """
    c = Component()

    #*************************************************************************
    #*
    #* Generic Design Rule Definitions
    #*
    #************************************************************************
    epsilon = tech.TECH.techParams['epsilon1']
    v1_size = tech.TECH.techParams['V1_a']
    v1_sep1 = tech.TECH.techParams['V1_b']
    v1_sep2 = tech.TECH.techParams['V1_b1']
    v1_enc = tech.TECH.techParams['V1_c1']
    vn_size = tech.TECH.techParams['Vn_a']
    vn_sep1 = tech.TECH.techParams['Vn_b']
    vn_sep2 = tech.TECH.techParams['Vn_b1']
    vn_enc = tech.TECH.techParams['Vn_c1']
    Topvia1_size = tech.TECH.techParams['TV1_a']
    TopVia1_sep = tech.TECH.techParams['TV1_b']
    Topvia1_enc_met5 = tech.TECH.techParams['TV1_c']
    Topvia1_enc_top1 = tech.TECH.techParams['TV1_d']
    Topvia2_size = tech.TECH.techParams['TV2_a']
    TopVia2_sep = tech.TECH.techParams['TV2_b']
    Topvia2_enc_top1 = tech.TECH.techParams['TV2_c']
    Topvia2_enc_top2 = tech.TECH.techParams['TV2_d']
    TopMetal1_min = tech.TECH.techParams['TM1_a']
    TopMetal2_min = tech.TECH.techParams['TM2_a']
    
    #*************************************************************************
    #*
    #* Device Specific Design Rule Definitions
    #*
    #************************************************************************
    
    metal_layers = ['Metal1', 'Metal2', 'Metal3', 'Metal4', 'Metal5', 'TopMetal1', 'TopMetal2']
    via_layers = ['Via1', 'Via2', 'Via3', 'Via4', 'TopVia1', 'TopVia2']
    
    #*************************************************************************
    #*
    #* Main body of code
    #*
    #************************************************************************
    idx_b = metal_layers.index(bottom_layer)
    idx_t = metal_layers.index(top_layer)
    
    if idx_b > idx_t:
        idx_b, idx_t = idx_t, idx_b
        bottom_layer, top_layer = top_layer, bottom_layer
    stack_layers = metal_layers[idx_b:idx_t+1]
    
    for layer in stack_layers:
        #pre-procesing
        if layer == 'Metal1':
            columns = vn_columns
            rows = vn_rows
            via_size = v1_size
            via_sep = v1_sep1 if (columns<4 and rows<4) else v1_sep2
            via_enc = v1_enc
            w_x = (columns * via_size + (columns - 1) * via_sep)
            w_y = (rows * via_size + (rows - 1) * via_sep)
            
        elif layer == 'TopMetal1':
            via_size = Topvia1_size
            via_sep = TopVia1_sep
            via_enc = Topvia1_enc_met5
            columns = vt1_columns
            rows = vt1_rows
            w_x = (columns * via_size + (columns - 1) * via_sep)
            w_y = (rows * via_size + (rows - 1) * via_sep)
            if "Metal5" in stack_layers:
                c << gf.components.rectangle(size = (w_x+2*via_enc, w_y+2*via_enc), layer = METAL_LAYERS["Metal5"], centered = True, port_type = "electrical")
            via_enc = Topvia1_enc_top1
            
        elif layer == 'TopMetal2':
            via_size = Topvia2_size
            via_sep = TopVia2_sep
            via_enc = Topvia2_enc_top1
            columns = vt2_columns
            rows = vt2_rows
            w_x = (columns * via_size + (columns - 1) * via_sep)
            w_y = (rows * via_size + (rows - 1) * via_sep)
            c << gf.components.rectangle(size = (w_x+2*via_enc, w_y+2*via_enc), layer = METAL_LAYERS["TopMetal1"], centered = True, port_type = "electrical")
            
        else:
            columns = vn_columns
            rows = vn_rows
            via_size = vn_size
            via_sep = vn_sep1 if (columns<4 and rows<4) else vn_sep2
            via_enc = vn_enc
            w_x = (columns * via_size + (columns - 1) * via_sep)
            w_y = (rows * via_size + (rows - 1) * via_sep)
            
        #metal draw
        if layer == 'TopMetal1':
            if columns * via_size + (columns - 1) * 2 * via_sep < TopMetal1_min:
                via_enc = (TopMetal1_min - Topvia1_size)/2
        elif layer == 'TopMetal2':
            if columns * via_size + (columns - 1) * 2 * via_sep < TopMetal2_min:
                via_enc = (TopMetal2_min - Topvia2_size) / 2
        c << gf.components.rectangle(size = (w_x+2*via_enc, w_y+2*via_enc), layer = METAL_LAYERS[layer], centered = True, port_type = "electrical")
        
        #via draw
        if layer != bottom_layer:
            
            via_layer = via_layers[metal_layers.index(layer)-1]
            c << via_array(via_type=via_layer, columns=columns, rows=rows, via_size=via_size, via_spacing=via_sep, via_enclosure=via_enc)               

        #port draw
        if layer == bottom_layer:
            c.add_port(
                name="bottom",
                center=(0, 0),
                width=min(w_x+2*via_enc, w_y+2*via_enc),
                orientation=0,
                layer=METAL_LAYERS[bottom_layer],
                port_type="electrical",
            )       
        
        if layer == top_layer:
            c.add_port(
                name="top",
                center=(0, 0),
                width=min(w_x+2*via_enc, w_y+2*via_enc),
                orientation=0,
                layer=METAL_LAYERS[top_layer],
                port_type="electrical",
            )
    
    return c

@gf.cell
def via_stack_with_pads(
    bottom_layer: str = "Metal1",
    top_layer: str = "TopMetal2",
    size: tuple[float, float] = (10.0, 10.0),
    pad_size: tuple[float, float] = (20.0, 20.0),
    pad_spacing: float = 50.0,
) -> Component:
    """Create a via stack with test pads.

    Args:
        bottom_layer: Bottom metal layer name.
        top_layer: Top metal layer name.
        size: Size of the via stack (width, height) in micrometers.
        pad_size: Size of the test pads (width, height) in micrometers.
        pad_spacing: Spacing between pads in micrometers.

    Returns:
        Component with via stack and test pads.
    """
    c = Component()

    # Create via stack
    stack = via_stack(
        bottom_layer=bottom_layer,
        top_layer=top_layer,
        size=size,
    )
    c.add_ref(stack)

    # Add bottom pad
    bottom_pad = gf.components.rectangle(
        size=pad_size,
        layer=METAL_LAYERS[bottom_layer],
        centered=True,
    )
    bottom_pad_ref = c.add_ref(bottom_pad)
    bottom_pad_ref.movex(-pad_spacing / 2)

    # Add top pad
    top_pad = gf.components.rectangle(
        size=pad_size,
        layer=METAL_LAYERS[top_layer],
        centered=True,
    )
    top_pad_ref = c.add_ref(top_pad)
    top_pad_ref.movex(pad_spacing / 2)

    # Connect pads to stack
    bottom_trace = gf.components.rectangle(
        size=(pad_spacing / 2 - size[0] / 2, 2.0),
        layer=METAL_LAYERS[bottom_layer],
    )
    bottom_trace_ref = c.add_ref(bottom_trace)
    bottom_trace_ref.move((-pad_spacing / 2, -1.0))

    top_trace = gf.components.rectangle(
        size=(pad_spacing / 2 - size[0] / 2, 2.0),
        layer=METAL_LAYERS[top_layer],
    )
    top_trace_ref = c.add_ref(top_trace)
    top_trace_ref.move((size[0] / 2, -1.0))

    # Add ports
    c.add_port(
        name="pad1",
        center=(-pad_spacing / 2, 0),
        width=pad_size[1],
        orientation=180,
        layer=METAL_LAYERS[bottom_layer],
        port_type="electrical",
    )

    c.add_port(
        name="pad2",
        center=(pad_spacing / 2, 0),
        width=pad_size[1],
        orientation=0,
        layer=METAL_LAYERS[top_layer],
        port_type="electrical",
    )

    return c


if __name__ == "__main__":
    # Test the components
    c1 = via_array(via_type="Via1", columns=3, rows=3)
    c1.show()

    c2 = via_stack(bottom_layer="Metal1", top_layer="Metal5")
    c2.show()

    c3 = via_stack_with_pads(bottom_layer="Metal1", top_layer="TopMetal2")
    c3.show()

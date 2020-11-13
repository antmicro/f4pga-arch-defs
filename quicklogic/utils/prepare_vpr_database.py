#!/usr/bin/env python3
import argparse
import pickle
import itertools
import re
from collections import defaultdict

from data_structs import *
from utils import yield_muxes, get_loc_of_cell, find_cell_in_tile
from utils import get_pin_name

from timing import compute_switchbox_timing_model
from timing import populate_switchbox_timing, copy_switchbox_timing

# =============================================================================

# Grid margin size (left, top, right, bottom)
GRID_MARGIN = (3, 2, 2, 2)

# IO cell types to ignore. They do not correspond to routable IO pads.
IGNORED_IO_CELL_TYPES = (
    "VCC",
    "GND",
)

# =============================================================================


def is_loc_within_limit(loc, limit):
    """
    Returns true when the given location lies within the given limit.
    Returns true if the limit is None. Coordinates in the limit are
    inclusive.
    """

    if limit is None:
        return True

    if loc.x < limit[0] or loc.x > limit[2]:
        return False
    if loc.y < limit[1] or loc.y > limit[3]:
        return False

    return True


def is_loc_free(loc, tile_grid):
    """
    Checks whether a location in the given tilegrid is free.
    """

    if loc not in tile_grid:
        return True
    if tile_grid[loc] == None:
        return True

    return False


# =============================================================================


def add_synthetic_cell_and_tile_types(tile_types, cells_library):

    # Add a synthetic tile types for the VCC and GND const sources.
    # Models of the VCC and GND cells are already there in the cells_library.
    for const in ["VCC", "GND"]:
        tile_type = TileType("SYN_{}".format(const), {const: 1})
        tile_type.make_pins(cells_library)
        tile_types[tile_type.type] = tile_type


def make_tile_type(cells, cells_library, tile_types):
    """
    Creates a tile type given a list of cells that constitute to it.
    """

    # Count cell types
    cell_types = sorted([c.type for c in cells])
    cell_counts = {t: 0 for t in cell_types}

    for cell in cells:
        cell_counts[cell.type] += 1

    # Format type name
    parts = []
    for t, c in cell_counts.items():
        if c == 1:
            parts.append(t)
        else:
            parts.append("{}x{}".format(c, t))

    type_name = "_".join(parts).upper()

    # If the new tile type already exists, use the existing one
    if type_name in tile_types:
        return tile_types[type_name]

    # Create the new tile type
    tile_type = TileType(type=type_name, cells=cell_counts)

    # Create pins
    tile_type.make_pins(cells_library)

    # Add it to the list
    tile_types[type_name] = tile_type
    return tile_type


def strip_cells(tile, cell_types, tile_types, cells_library):
    """
    Removes cells of the particular type from the tile and tile_type.
    Possibly creates a new tile type
    """
    tile_type = tile_types[tile.type]

    # Check if there is something to remove
    if not len(set(cell_types) & set(tile_type.cells.keys())):
        return tile

    # Filter cells
    new_cells = [c for c in tile.cells if c.type not in cell_types]
    if not new_cells:
        return None

    # Create the new tile type and tile
    new_tile_type = make_tile_type(new_cells, cells_library, tile_types)
    new_tile = Tile(type=new_tile_type.type, name=tile.name, cells=new_cells)

    return new_tile


def process_tilegrid(
        tile_types,
        tile_grid,
        clock_cells,
        cells_library,
        grid_size,
        grid_offset,
        grid_limit=None
):
    """
    Processes the tilegrid. May add/remove tiles. Returns a new one.
    """    

    vpr_tile_grid = {}
    fwd_loc_map = {}
    bwd_loc_map = {}
    ram_blocks = []
    mult_blocks = []
    vpr_clock_cells = {}

    def add_loc_map(phy_loc, vpr_loc):
        fwd_loc_map[phy_loc] = vpr_loc
        bwd_loc_map[vpr_loc] = phy_loc

    # Generate the VPR tile grid
    for phy_loc, tile in tile_grid.items():

        # Limit the grid range
        if not is_loc_within_limit(phy_loc, grid_limit):
            continue

        vpr_loc = Loc(
            x=phy_loc.x + grid_offset[0], y=phy_loc.y + grid_offset[1]
        )

        # If the tile contains QMUX or CAND then strip it. Possibly create a 
        # new tile type.
        tile_type = tile_types[tile.type]
        if "QMUX" in tile_type.cells or "CAND" in tile_type.cells:

            # Store the stripped cells
            for cell in tile.cells:
                if cell.type in ["QMUX", "CAND"]:

                    # Find it in the physical clock cell list
                    if cell.name not in clock_cells:
                        print("WARNING: Clock cell '{}' not on the clock cell list!".format(cell.name))
                        continue

                    clock_cell = clock_cells[cell.name]
                    clock_cell = ClockCell(
                        type = clock_cell.type,
                        name = clock_cell.name,
                        loc = vpr_loc,
                        quadrant = clock_cell.quadrant,
                        pin_map = clock_cell.pin_map
                    )

                    vpr_clock_cells[clock_cell.name] = clock_cell

            # Strip the cells
            tile = strip_cells(tile, ["QMUX", "CAND"], tile_types, cells_library)
            if tile is None:
                continue

        # The tile contains a BIDIR or CLOCK cell. it is an IO tile
        tile_type = tile_types[tile.type]
        if "BIDIR" in tile_type.cells or "CLOCK" in tile_type.cells:

            # For the BIDIR cell create a synthetic tile
            if "BIDIR" in tile_type.cells:
                assert tile_type.cells["BIDIR"] == 1

                cells = [c for c in tile.cells if c.type == "BIDIR"]
                new_type = make_tile_type(cells, cells_library, tile_types)

                add_loc_map(phy_loc, vpr_loc)
                vpr_tile_grid[vpr_loc] = Tile(
                    type=new_type.type, name=tile.name, cells=cells
                )

            # For the CLOCK cell create a synthetic tile
            if "CLOCK" in tile_type.cells:
                assert tile_type.cells["CLOCK"] == 1

                cells = [c for c in tile.cells if c.type == "CLOCK"]
                new_type = make_tile_type(cells, cells_library, tile_types)

                # If the tile has a BIDIR cell then place the CLOCK tile in a
                # free location next to the original one.
                if "BIDIR" in tile_type.cells:
                    for ox, oy in ((-1, 0), (+1, 0), (0, -1), (0, +1)):
                        test_loc = Loc(x=phy_loc.x + ox, y=phy_loc.y + oy)
                        if is_loc_free(test_loc, tile_grid):
                            new_loc = Loc(x=vpr_loc.x + ox, y=vpr_loc.y + oy)
                            break
                    else:
                        assert False, ("No free location to place CLOCK tile", vpr_loc)

                # Don't move
                else:
                    new_loc = vpr_loc

                # Add only the backward location correspondence for CLOCK tile
                bwd_loc_map[new_loc] = phy_loc
                vpr_tile_grid[new_loc] = Tile(
                    type=new_type.type, name=tile.name, cells=cells
                )

# Mults and RAMs occupy multiple cells
# We'll create a synthetic tile with a single cell for each
# RAM and MULT block
        if "RAM" in tile_type.cells or "MULT" in tile_type.cells:
            for cell in tile.cells:
                # Check if the current location is not taken
                # this could happen because RAM and MULTS share
                # the same location. General rule here is that
                # we create a synthetic Tile/Cell in the first
                # available neighboring location of the original block of cells
                if cell.type == 'RAM':
                    cells_set = ram_blocks
                elif cell.type == 'MULT':
                    cells_set = mult_blocks
                else:
                    continue

                # Find free location in the physical tile grid close to the
                # original one. Once found, convert it to location in the
                # VPR tile grid.
                for ox, oy in ((0, 0), (0, -1), (0, +1), (-1, 0), (+1, 0)):
                    test_loc = Loc(x=phy_loc.x + ox, y=phy_loc.y + oy)
                    if is_loc_free(test_loc, tile_grid):
                        new_loc = Loc(x=vpr_loc.x + ox, y=vpr_loc.y + oy)
                        break
                else:
                    assert False, "No free location to place {} tile".format(
                        cell.type
                    )

                # The VPR location is already occupied. Probably another
                # instance of the same cell is already there.
                if not is_loc_free(new_loc, vpr_tile_grid):
                    continue

                if cell.name not in cells_set:
                    cells_set.append(cell.name)
                    tile_type = make_tile_type(
                        [cell], cells_library, tile_types
                    )
                    vpr_tile_grid[new_loc] = Tile(
                        tile_type.type, name=cell.type, cells=[cell]
                    )

        # The tile contains SDIOMUX cell(s). This is an IO tile.
        if "SDIOMUX" in tile_type.cells:

            # Split the tile into individual SDIOMUX cells. Each one will be
            # inside a synthetic tile occupying different grid location.
            cells = [c for c in tile.cells if c.type == "SDIOMUX"]
            for i, cell in enumerate(cells):

                # Create a synthetic tile that will hold just the SDIOMUX cell
                new_type = make_tile_type([cell], cells_library, tile_types)

                # Choose a new location for the tile
                # FIXME: It is assumed that SDIOMUX tiles are on the left edge
                # of the grid and there is enough space to split them.
                new_loc = Loc(vpr_loc.x - i, vpr_loc.y)
                assert new_loc.x >= 1, new_loc

                # For the offset 0 add the full mapping, for others, just the
                # backward correspondence.
                if new_loc == vpr_loc:
                    add_loc_map(phy_loc, new_loc)
                else:
                    bwd_loc_map[new_loc] = phy_loc

                # Change index of the cell
                new_cell = Cell(
                    type=cell.type, index=0, name=cell.name, alias=cell.alias
                )

                # Add the tile instance
                vpr_tile_grid[new_loc] = Tile(
                    type=new_type.type, name=tile.name, cells=[new_cell]
                )

        # A homogeneous tile
        if len(tile_type.cells) == 1:
            cell_type = list(tile_type.cells.keys())[0]

            # Keep only these types
            if cell_type in ["LOGIC", "GMUX",]:
                add_loc_map(phy_loc, vpr_loc)
                vpr_tile_grid[vpr_loc] = tile
                continue

    # Find the ASSP tile. There are multiple tiles that contain the ASSP cell
    # but in fact there is only one ASSP cell for the whole FPGA which is
    # "distributed" along top and left edge of the grid.
    if "ASSP" in tile_types:        

        # Verify that the location is empty
        assp_loc = Loc(x=1, y=1)
        assert is_loc_free(vpr_tile_grid, assp_loc), ("ASSP", assp_loc)

        # Place the ASSP tile
        vpr_tile_grid[assp_loc] = Tile(
            type="ASSP",
            name="ASSP",
            cells=[Cell(type="ASSP", index=0, name="ASSP", alias=None)]
        )

        # Remove "FBIO_*" pins from the ASSP tile. These pins are handled by
        # SDIOMUX IO cells
        tile_type = tile_types["ASSP"]
        tile_type.pins = [p for p in tile_type.pins if "FBIO_" not in p.name]

    # Insert synthetic VCC and GND source tiles.
    # FIXME: This assumes that the locations specified are empty!
    for const, loc in [("VCC", Loc(x=2, y=1)), ("GND", Loc(x=3, y=1))]:

        # Verify that the location is empty
        assert is_loc_free(vpr_tile_grid, loc), (const, loc)

        # Add the tile instance
        name = "SYN_{}".format(const)
        vpr_tile_grid[loc] = Tile(
            type=name,
            name=name,
            cells=[Cell(type=const, index=0, name=const, alias=None)]
        )

    # Extend the grid by 1 on the right and bottom side. Fill missing locs
    # with empty tiles.
    for x, y in itertools.product(range(grid_size[0]), range(grid_size[1])):
        loc = Loc(x=x, y=y)

        if loc not in vpr_tile_grid:
            vpr_tile_grid[loc] = None

    return vpr_tile_grid, vpr_clock_cells, LocMap(fwd=fwd_loc_map, bwd=bwd_loc_map),


# =============================================================================


def process_switchbox_grid(
        phy_switchbox_grid, loc_map, grid_offset, grid_limit=None
):
    """
    Processes the switchbox grid
    """

    fwd_loc_map = loc_map.fwd
    bwd_loc_map = loc_map.bwd

    def add_loc_map(phy_loc, vpr_loc):

        if phy_loc in fwd_loc_map:
            assert fwd_loc_map[phy_loc] == vpr_loc, (phy_loc, vpr_loc)
        else:
            fwd_loc_map[phy_loc] = vpr_loc

        if vpr_loc in bwd_loc_map:
            assert bwd_loc_map[vpr_loc] == phy_loc, (phy_loc, vpr_loc)
        else:
            bwd_loc_map[vpr_loc] = phy_loc

    # Remap locations
    vpr_switchbox_grid = {}
    for phy_loc, switchbox_type in phy_switchbox_grid.items():

        # Limit the grid range
        if not is_loc_within_limit(phy_loc, grid_limit):
            continue

        # compute VPR grid location
        vpr_loc = Loc(
            x=phy_loc.x + grid_offset[0], y=phy_loc.y + grid_offset[1]
        )

        # Place the switchbox
        vpr_switchbox_grid[vpr_loc] = switchbox_type

        # Add location correspondence
        add_loc_map(phy_loc, vpr_loc)

    return vpr_switchbox_grid, LocMap(fwd=fwd_loc_map, bwd=bwd_loc_map),


# =============================================================================


def process_connections(
        phy_connections, loc_map, vpr_tile_grid, phy_tile_grid, grid_limit=None
):
    """
    Process the connection list.
    """
    # Pin map
    pin_map = {}
    fwd_loc_map = loc_map.fwd
    bwd_loc_map = loc_map.bwd

    # Remap locations, remap pins
    vpr_connections = []
    for connection in phy_connections:

        # Reject connections that reach outsite the grid limit
        if not is_loc_within_limit(connection.src.loc, grid_limit):
            continue
        if not is_loc_within_limit(connection.dst.loc, grid_limit):
            continue

        # Remap source and destination coordinates
        src_loc = connection.src.loc
        dst_loc = connection.dst.loc

        if src_loc not in loc_map.fwd:
            continue
        if dst_loc not in loc_map.fwd:
            continue

        # Remap pins or discard the connection
        src_pin = connection.src.pin
        dst_pin = connection.dst.pin

        if src_pin in pin_map:
            src_pin = pin_map[src_pin]

        if dst_pin in pin_map:
            dst_pin = pin_map[dst_pin]

        if src_pin is None or dst_pin is None:
            continue

        # Add the new connection
        new_connection = Connection(
            src=ConnectionLoc(
                loc=loc_map.fwd[src_loc],
                pin=src_pin,
                type=connection.src.type,
            ),
            dst=ConnectionLoc(
                loc=loc_map.fwd[dst_loc],
                pin=dst_pin,
                type=connection.dst.type,
            ),
        )
        vpr_connections.append(new_connection)

    # Remap locations of connections that go to CLOCK pads. A physical
    # BIDIR+CLOCK tile is split into separate BIDIR and CLOCK tiles.
    for i, connection in enumerate(vpr_connections):      

        eps = [connection.src, connection.dst]
        for j, ep in enumerate(eps):

            # This endpoint is not relevant to a CLOCK cell
            if not ep.pin.startswith("CLOCK"):
                continue

            # The endpoint location points to a BIDIR tile. Find the assocated
            # CLOCK tile
            org_loc = loc_map.bwd[ep.loc]
            for vpr_loc, phy_loc in loc_map.bwd.items():
                if phy_loc == org_loc and vpr_loc != ep.loc:
                    clock_loc = vpr_loc
                    break
            else:
                assert False, ("Couldn't find a CLOCK cell in the VPR grid!", connection)
    
            eps[j] = ConnectionLoc(
                loc=clock_loc,
                pin=ep.pin,
                type=ep.type,
            )

        # Modify the connection
        vpr_connections[i] = Connection(src=eps[0], dst=eps[1])

    # Find SFBIO connections, map their endpoints to SDIOMUX tiles
    # FIXME: This should be read from the techfine. Definition of the SDIOMUX
    # cell has  "realPortName" fields.
    SDIOMUX_PIN_MAP = {
        "FBIO_In": "IZ",
        "FBIO_In_En": "IE",
        "FBIO_Out": "OQI",
        "FBIO_Out_En": "OE",
    }

    for i, connection in enumerate(vpr_connections):

        eps = [connection.src, connection.dst]
        for j, ep in enumerate(eps):

            # Must have "ASSP" and "FBIO_" in name and refer to a tile.
            if "ASSP" not in ep.pin:
                continue
            if "FBIO_" not in ep.pin:
                continue
            if ep.type != ConnectionType.TILE:
                continue

            # Get the pin name and index
            pin_name, pin_index = get_pin_name(ep.pin)
            assert pin_index is not None, ep

            # Strip cell name
            pin_name = pin_name.split("_", maxsplit=1)[1]

            # Find where is an SDIOMUX cell for that index
            cell_name = "SFB_{}_IO".format(pin_index)

            # New location and pin name
            new_loc = get_loc_of_cell(cell_name, vpr_tile_grid)
            cell = find_cell_in_tile(cell_name, vpr_tile_grid[new_loc])

            new_pin = "{}{}_{}".format(
                cell.type, cell.index, SDIOMUX_PIN_MAP[pin_name]
            )

            eps[j] = ConnectionLoc(
                loc=new_loc,
                pin=new_pin,
                type=ep.type,
            )

        # Modify the connection
        vpr_connections[i] = Connection(src=eps[0], dst=eps[1])

    # Find locations of "special" tiles
    special_tile_loc = {"ASSP": None}

    for loc, tile in vpr_tile_grid.items():
        if tile is not None and tile.type in special_tile_loc:
            assert special_tile_loc[tile.type] is None, tile
            special_tile_loc[tile.type] = loc

    # Map connections going to/from them to their locations in the VPR grid
    for i, connection in enumerate(vpr_connections):

        # Process connection endpoints
        eps = [connection.src, connection.dst]
        for j, ep in enumerate(eps):

            if ep.type != ConnectionType.TILE:
                continue

            cell_name, pin = ep.pin.split("_", maxsplit=1)
            cell_type = cell_name[:-1]
            # FIXME: The above will fail on cell with index >= 10

            if cell_type in special_tile_loc:
                loc = special_tile_loc[cell_type]

                eps[j] = ConnectionLoc(
                    loc=loc,
                    pin=ep.pin,
                    type=ep.type,
                )

        # Modify the connection
        vpr_connections[i] = Connection(src=eps[0], dst=eps[1])

    # handle RAM and MULT locations
    ram_locations = {}
    mult_locations = {}
    for loc, tile in vpr_tile_grid.items():
        if tile is None:
            continue
        cell = tile.cells[0]
        cell_name = cell.name
        if tile.type == "RAM":
            ram_locations[cell_name] = loc
        if tile.type == "MULT":
            mult_locations[cell_name] = loc

    ram_cell = 0
    for i, connection in enumerate(vpr_connections):
        # Process connection endpoints
        eps = [connection.src, connection.dst]
        for j, ep in enumerate(eps):

            if ep.type != ConnectionType.TILE:
                continue

            cell_name, pin = ep.pin.split("_", maxsplit=1)
            cell_type = cell_name[:-1]
            # FIXME: The above will fail on cell with index >= 10

            # We handle on MULT and RAM here
            if cell_type != "MULT" and cell_type != "RAM":
                continue

            loc = bwd_loc_map[ep.loc]
            tile = phy_tile_grid[loc]
            cell = [cell for cell in tile.cells if cell.type == cell_type]

            cell_name = cell[0].name

            if cell_type == "MULT":
                loc = mult_locations[cell_name]
            else:
                loc = ram_locations[cell_name]

            eps[j] = ConnectionLoc(
                loc=loc,
                pin=ep.pin,
                type=ep.type,
            )

        # Modify the connection
        vpr_connections[i] = Connection(src=eps[0], dst=eps[1])

    return vpr_connections


# =============================================================================


def process_package_pinmap(package_pinmap, vpr_tile_grid, grid_limit=None):
    """
    Processes the package pinmap. Reloacted pin mappings. Reject mappings
    that lie outside the grid limit.
    """

    # Remap locations, reject cells that are either ignored or not in the
    # tilegrid.
    new_package_pinmap = defaultdict(lambda: [])

    for pin_name, pins in package_pinmap.items():
        for pin in pins:

            # The loc is outside the grid limit, skip it.
            if not is_loc_within_limit(pin.loc, grid_limit):
                continue

            # Ignore this one
            if pin.cell.type in IGNORED_IO_CELL_TYPES:
                continue

            # Find the cell
            loc = get_loc_of_cell(pin.cell.name, vpr_tile_grid)
            if loc is None:
                continue

            cell = find_cell_in_tile(pin.cell.name, vpr_tile_grid[loc])
            assert cell is not None, (loc, pin)

            # Remap location
            new_package_pinmap[pin.name].append(
                PackagePin(name=pin.name, loc=loc, cell=cell)
            )

    # Convert to regular dict
    new_package_pinmap = dict(**new_package_pinmap)

    return new_package_pinmap


# =============================================================================


def build_switch_list():
    """
    Builds a list of all switch types used by the architecture
    """
    switches = {}

    # Add a generic mux switch to make VPR happy
    switch = VprSwitch(
        name="generic",
        type="mux",
        t_del=1e-15, # A deliberate dummy small delay
        r=0.0,
        c_in=0.0,
        c_out=0.0,
        c_int=0.0,
    )
    switches[switch.name] = switch

    # A delayless short
    switch = VprSwitch(
        name="short",
        type="short",
        t_del=0.0,
        r=0.0,
        c_in=0.0,
        c_out=0.0,
        c_int=0.0,
    )
    switches[switch.name] = switch

    return switches


def build_segment_list():
    """
    Builds a list of all segment types used by the architecture
    """
    segments = {}

    # A generic segment
    segment = VprSegment(
        name="generic",
        length=1,
        r_metal=0.0,
        c_metal=0.0,
    )
    segments[segment.name] = segment

    # Padding segment
    segment = VprSegment(
        name="pad",
        length=1,
        r_metal=0.0,
        c_metal=0.0,
    )
    segments[segment.name] = segment

    # Switchbox segment
    segment = VprSegment(
        name="sbox",
        length=1,
        r_metal=0.0,
        c_metal=0.0,
    )
    segments[segment.name] = segment

    # VCC and GND segments
    for const in ["VCC", "GND"]:
        segment = VprSegment(
            name=const.lower(),
            length=1,
            r_metal=0.0,
            c_metal=0.0,
        )
        segments[segment.name] = segment

    # HOP wire segments
    for i in [1, 2, 3, 4]:
        segment = VprSegment(
            name="hop{}".format(i),
            length=i,
            r_metal=0.0,
            c_metal=0.0,
        )
        segments[segment.name] = segment

    # Global clock network segment
    segment = VprSegment(
        name="clock",
        length=1,
        r_metal=0.0,
        c_metal=0.0,
    )
    segments[segment.name] = segment

    # A segment for "hop" connections to "special" tiles.
    segment = VprSegment(
        name="special",
        length=1,
        r_metal=0.0,
        c_metal=0.0,
    )
    segments[segment.name] = segment

    return segments


# =============================================================================


def main():

    # Parse arguments
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--phy-db",
        type=str,
        required=True,
        help="Input physical device database file"
    )
    parser.add_argument(
        "--vpr-db",
        type=str,
        default="vpr_database.pickle",
        help="Output VPR database file"
    )
    parser.add_argument(
        "--grid-limit",
        type=str,
        default=None,
        help="Grid coordinate range to import eg. '0,0,10,10' (def. None)"
    )

    args = parser.parse_args()

    # Grid limit
    if args.grid_limit is not None:
        grid_limit = [int(q) for q in args.grid_limit.split(",")]
    else:
        grid_limit = None

    # Load data from the database
    with open(args.phy_db, "rb") as fp:
        db = pickle.load(fp)

        phy_quadrants = db["phy_quadrants"]
        cells_library = db["cells_library"]
        tile_types = db["tile_types"]
        phy_tile_grid = db["phy_tile_grid"]
        phy_clock_cells = db["phy_clock_cells"]
        switchbox_types = db["switchbox_types"]
        phy_switchbox_grid = db["switchbox_grid"]
        switchbox_timing = db["switchbox_timing"]
        connections = db["connections"]
        package_pinmaps = db["package_pinmaps"]

    # Add synthetic stuff
    add_synthetic_cell_and_tile_types(tile_types, cells_library)

    # Determine the grid offset so occupied locations start at GRID_MARGIN
    tl_min = min([loc.x for loc in phy_tile_grid]), \
             min([loc.y for loc in phy_tile_grid])
    tl_max = max([loc.x for loc in phy_tile_grid]), \
             max([loc.y for loc in phy_tile_grid])

    sb_min = min([loc.x for loc in phy_switchbox_grid]), \
             min([loc.y for loc in phy_switchbox_grid])
    sb_max = max([loc.x for loc in phy_switchbox_grid]), \
             max([loc.y for loc in phy_switchbox_grid])

    grid_min = min(tl_min[0], sb_min[0]), min(tl_min[1], sb_min[1])
    grid_max = max(tl_max[0], sb_max[0]), max(tl_max[1], sb_max[1])

    # Compute VPR grid offset w.r.t the physical grid and its size
    grid_offset = GRID_MARGIN[0] - grid_min[0], \
                  GRID_MARGIN[1] - grid_min[1]

    grid_size = GRID_MARGIN[0] + GRID_MARGIN[2] + \
                (grid_max[0] - grid_min[0] + 1), \
                GRID_MARGIN[1] + GRID_MARGIN[3] + \
                (grid_max[1] - grid_min[1] + 1)

    # Remap quadrant locations
    vpr_quadrants = {}
    for quadrant in phy_quadrants.values():
        vpr_quadrants[quadrant.name] = Quadrant(
            name = quadrant.name,
            x0 = quadrant.x0 + grid_offset[0],
            x1 = quadrant.x1 + grid_offset[0],
            y0 = quadrant.y0 + grid_offset[1],
            y1 = quadrant.y1 + grid_offset[1]
        )

    # Process the tilegrid
    vpr_tile_grid, vpr_clock_cells, loc_map = process_tilegrid(
        tile_types, phy_tile_grid, phy_clock_cells,
        cells_library, grid_size, grid_offset, grid_limit
    )

    # Process the switchbox grid
    vpr_switchbox_grid, loc_map = process_switchbox_grid(
        phy_switchbox_grid, loc_map, grid_offset, grid_limit
    )

    # Process connections
    connections = process_connections(
        connections, loc_map, vpr_tile_grid, phy_tile_grid, grid_limit
    )

    # Process package pinmaps
    vpr_package_pinmaps = {}
    for package, pkg_pin_map in package_pinmaps.items():
        vpr_package_pinmaps[package] = process_package_pinmap(
            pkg_pin_map, vpr_tile_grid, grid_limit
        )

    # Get tile types present in the grid
    vpr_tile_types = set(
        [t.type for t in vpr_tile_grid.values() if t is not None]
    )
    vpr_tile_types = {
        k: v
        for k, v in tile_types.items()
        if k in vpr_tile_types
    }

    # Get the switchbox types present in the grid
    vpr_switchbox_types = set(
        [s for s in vpr_switchbox_grid.values() if s is not None]
    )
    vpr_switchbox_types = {
        k: v
        for k, v in switchbox_types.items()
        if k in vpr_switchbox_types
    }

    # Make tile -> site equivalence list
    vpr_equivalent_sites = {}

    # Make switch list
    vpr_switches = build_switch_list()
    # Make segment list
    vpr_segments = build_segment_list()

    # Process timing data
    if switchbox_timing is not None:
        print("Processing timing data...")

        # The timing data seems to be the same for each switchbox type and is
        # stored under the SB_LC name.
        timing_data = switchbox_timing["SB_LC"]

        # Compute the timing model for the most generic SB_LC switchbox.
        switchbox = vpr_switchbox_types["SB_LC"]
        driver_timing, sink_map = compute_switchbox_timing_model(
            switchbox, timing_data
        )

        # Populate the model, create and assign VPR switches.
        populate_switchbox_timing(
            switchbox, driver_timing, sink_map, vpr_switches
        )

        # Propagate the timing data to all other switchboxes. Even though they
        # are of different type, physically they are the same.
        for dst_switchbox in vpr_switchbox_types.values():
            if dst_switchbox.type != "SB_LC":
                copy_switchbox_timing(switchbox, dst_switchbox)

    # DBEUG
    print("Tile grid:")
    xmax = max([loc.x for loc in vpr_tile_grid])
    ymax = max([loc.y for loc in vpr_tile_grid])
    for y in range(ymax + 1):
        l = " {:>2}: ".format(y)
        for x in range(xmax + 1):
            loc = Loc(x=x, y=y)
            if loc not in vpr_tile_grid:
                l += " "
            elif vpr_tile_grid[loc] is not None:
                tile_type = vpr_tile_types[vpr_tile_grid[loc].type]
                label = sorted(list(tile_type.cells.keys()))[0][0].upper()
                l += label
            else:
                l += "."
        print(l)

    # DEBUG
    print("Switchbox grid:")
    xmax = max([loc.x for loc in vpr_switchbox_grid])
    ymax = max([loc.y for loc in vpr_switchbox_grid])
    for y in range(ymax + 1):
        l = " {:>2}: ".format(y)
        for x in range(xmax + 1):
            loc = Loc(x=x, y=y)
            if loc not in vpr_switchbox_grid:
                l += " "
            elif vpr_switchbox_grid[loc] is not None:
                l += "X"
            else:
                l += "."
        print(l)

    # DBEUG
    print("Route-through global clock cells:")
    xmax = max([loc.x for loc in vpr_tile_grid])
    ymax = max([loc.y for loc in vpr_tile_grid])
    for y in range(ymax + 1):
        l = " {:>2}: ".format(y)
        for x in range(xmax + 1):
            loc = Loc(x=x, y=y)

            for cell in vpr_clock_cells.values():
                if cell.loc == loc:
                    l += cell.name[0].upper()
                    break
            else:
                l += "."
        print(l)

    # DEBUG
    print("VPR Segments:")
    for s in vpr_segments.values():
        print("", s)

    # DEBUG
    print("VPR Switches:")
    for s in vpr_switches.values():
        print("", s)

    # Prepare the VPR database and write it
    db_root = {
        "cells_library": cells_library,
        "loc_map": loc_map,
        "vpr_quadrants": vpr_quadrants,
        "vpr_tile_types": vpr_tile_types,
        "vpr_tile_grid": vpr_tile_grid,
        "vpr_clock_cells": vpr_clock_cells,
        "vpr_equivalent_sites": vpr_equivalent_sites,
        "vpr_switchbox_types": vpr_switchbox_types,
        "vpr_switchbox_grid": vpr_switchbox_grid,
        "connections": connections,
        "vpr_package_pinmaps": vpr_package_pinmaps,
        "segments": list(vpr_segments.values()),
        "switches": list(vpr_switches.values()),
    }

    with open(args.vpr_db, "wb") as fp:
        pickle.dump(db_root, fp, protocol=3)


# =============================================================================

if __name__ == "__main__":
    main()

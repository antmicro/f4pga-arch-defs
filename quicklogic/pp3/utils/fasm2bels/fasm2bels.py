#!/usr/bin/env python3
import argparse
import re
import pickle

from collections import namedtuple, defaultdict
from pathlib import Path

import fasm

from data_structs import Loc, SwitchboxPinLoc, PinDirection, Connection, ConnectionLoc, ConnectionType, TilePin
from utils import get_quadrant_for_loc

from netlist import Netlist

# =============================================================================


class Fasm2Bels:

    ConfigFeature = namedtuple("ConfigFeature", "name value")
    RoutingFeature = namedtuple('RoutingFeature', 'stage stage_id switch_id mux_id sel_id')

    # ...........................................

    class Exception(Exception):
        """
        Exception for Fasm2Bels errors and unsupported features.
        """

        def __init__(self, message):
            self.message = message

        def __str__(self):
            return self.message
        def __repr__(self):
            return self.message

    # ...........................................

    def __init__(self, db, device_name, package_name):
        """
        Constructor
        """

        self.device_name = device_name
        self.package_name = package_name

        # Get data from database
        self.switchbox_types = db["switchbox_types"]
        self.switchbox_grid = db["switchbox_grid"]
        self.connections = db["connections"]
        self.cells_library = db["cells_library"]
        self.tile_grid = db["phy_tile_grid"]
        self.quadrants = db["phy_quadrants"]

        # Get package pinmap
        if self.package_name not in db["package_pinmaps"]:
            raise self.Exception(
                "ERROR: '{}' is not a vaild package for device '{}'. Valid ones are: {}"
                .format(
                    self.package_name, self.device_name,
                    ", ".join(db["package_pinmaps"].keys())
                )
            )

        self.io_names = dict()
        for name, package in db['package_pinmaps'][self.package_name].items():
            self.io_names[package[0].loc] = name

        # Build maps that bind cell locations and their instance names
        self.cell_name_to_loc = defaultdict(list)
        self.loc_to_cell_name = defaultdict(dict)

        name_to_type = dict()
        for loc, tile in self.tile_grid.items():
            for cell in tile.cells:

                if cell.type == "LOGIC":
                    continue

                name_to_type[cell.name] = cell.type

                self.cell_name_to_loc[cell.name].append(loc)
                self.loc_to_cell_name[loc][cell.type] = cell.name

        # Identify cells that occupy multiple locations (RAMs etc.)
        self.multiloc_cells = set()
        for name, locs in self.cell_name_to_loc.items():
            if len(locs) > 1:
                self.multiloc_cells.add(name_to_type[name])

        # QMUX fixup
        self.fixup_qmux_connections_and_cells()

        # CAND fixup
        self.fixup_cand_connections()

        # Sort connections by their endpoints
        self.connections_to = dict()
        self.connections_from = dict()

        for conn in self.connections:
            self.connections_from[conn.src] = conn
            self.connections_to[conn.dst] = conn

        self.features = dict()
        self.io_constraints = dict()

    def fixup_qmux_connections_and_cells(self):
        """
        A QMUX should have 3 QCLKIN inputs but accorting to the EOS S3/PP3E
        techfile it has only one. It is assumed then when "QCLKIN0=GMUX_1" then
        "QCLKIN1=GMUX_2" etc.
        """

        # Fixup connections
        new_connections = []
        for connection in self.connections:

            # Get only those that target QCLKIN0 of a QMUX.
            if connection.dst.type != ConnectionType.CLOCK:
                continue
            if connection.src.type != ConnectionType.TILE:
                continue

            dst_cell_name, dst_pin = connection.dst.pin.split(".", maxsplit=1)
            if not dst_cell_name.startswith("QMUX") or dst_pin != "QCLKIN0":
                continue

            src_cell_name = "{}{}".format(
                connection.src.pin.cell, connection.src.pin.index
            )
            if not src_cell_name.startswith("GMUX"):
                continue

            # Add two new connections for QCLKIN1 and QCLKIN2.
            # GMUX connections are already spread along the Z axis so the Z
            # coordinate indicates the GMUX cell index.
            gmux_base = connection.src.loc.z
            for i in [1, 2]:
                gmux_idx = (gmux_base + i) % 5

                gmux_pin = TilePin(cell="GMUX", index=gmux_idx, pin="IZ") #0
                if connection.src.type != ConnectionType.TILE:
                    gmux_pin = str(gmux_pin)

                c = Connection(
                    src=ConnectionLoc(
                        loc=Loc(
                            x=connection.src.loc.x,
                            y=connection.src.loc.y,
                            z=0 #gmux_idx
                        ),
                        pin=gmux_pin,
                        type=connection.src.type
                    ),
                    dst=ConnectionLoc(
                        loc=connection.dst.loc,
                        pin="{}.QCLKIN{}".format(dst_cell_name, i),
                        type=connection.dst.type
                    ),
                    is_direct=connection.is_direct
                )
                new_connections.append(c)

        self.connections.extend(new_connections)

        # Fixup cell library
        # TODO:
        
    def fixup_cand_connections(self):
        """
        Adds column clock connections
        """

        # CAND name regular expressiong
        expr = re.compile(r"CAND(?P<idx>[0-9]+)_(?P<quad>[A-Z]+)_(?P<col>[0-9]+)")

        for cand_loc, tile in self.tile_grid.items():
            quadrant = get_quadrant_for_loc(cand_loc, self.quadrants)

            # Filter cells
            for cell in [c for c in tile.cells if c.type == "CAND"]:

                # Match name, get index
                match = expr.fullmatch(cell.name)
                assert match is not None, cell.name

                index = int(match.group("idx"))

                # Populate connections CAND -> switchbox
                for y in range(quadrant.y0, quadrant.y1 + 1):
                    sb_loc = Loc(cand_loc.x, y, 0)

                    conn = Connection(
                        src = ConnectionLoc(
                            loc = cand_loc,
                            pin = TilePin(cell="CAND", index=index, pin="IZ"),
                            type = ConnectionType.CLOCK
                        ),
                        dst = ConnectionLoc(
                            loc = sb_loc,
                            pin = "CAND{}".format(index),
                            type = ConnectionType.SWITCHBOX
                        ),
                        is_direct = False
                    )
                    self.connections.append(conn)

    def parse_routing_feature(self, feature):
        """
        Parses routing feature, returns a RoutingFeature object
        """

        # Highway
        match = re.match(
            r'^I_highway\.IM(?P<switch_id>[0-9]+)\.I_pg(?P<sel_id>[0-9]+)$',
            feature
        )
        if match:
            return self.RoutingFeature(
                stage="HIGHWAY",
                stage_id=3, # FIXME: Get HIGHWAY stage id from the switchbox
                switch_id=int(match.group('switch_id')),
                mux_id=0,
                sel_id=int(match.group('sel_id'))
            )

        # Street
        match = re.match(
            r'^I_street\.Isb(?P<stage_id>[0-9])(?P<switch_id>[0-9])\.I_M(?P<mux_id>[0-9]+)\.I_pg(?P<sel_id>[0-9]+)$',  # noqa: E501
            feature
        )
        if match:
            return self.RoutingFeature(
                stage="STREET",
                stage_id = int(match.group('stage_id')) - 1,
                switch_id = int(match.group('switch_id')) - 1,
                mux_id = int(match.group('mux_id')),
                sel_id = int(match.group('sel_id')),
            )

        # Shouldn't happen
        raise self.Exception("Unrecognized routing FASM feature '{}'".format(
            feature))

    def parse_fasm_lines(self, fasm_lines):
        """
        Parses input FASM lines, groups them by grid location and type
        """

        loctyp = re.compile(
            r'^X(?P<x>[0-9]+)Y(?P<y>[0-9]+)\.(?P<type>[A-Z]+[0-4]?)\.(?P<feature>.*)$'
        ) # noqa: E501

        self.features = dict()
        for line in fasm_lines:

            if not line.set_feature:
                continue

            match = loctyp.match(line.set_feature.feature)
            if not match:
                raise self.Exception(
                    f'FASM feature has unsupported format: {line.set_feature}'
                )  # noqa: E501

            loc = Loc(x=int(match.group("x")), y=int(match.group("y")), z=0)
            typ = match.group("type").upper()

            if typ != "ROUTING":
                typ = "CONFIG"

            if loc not in self.features:
                self.features[loc] = {
                    "ROUTING": [],
                    "CONFIG": [],
                }

            if typ == "CONFIG":
                self.features[loc][typ].append(self.ConfigFeature(
                    name=match.group("feature"),
                    value=line.set_feature.value,
                ))
            elif typ == "ROUTING":
                self.features[loc][typ].append(
                    self.parse_routing_feature(match.group("feature"))
                )

    def get_features_at_locs(self, locs, typ="CONFIG"):
        """
        Returns a list of FASM features corresponding to the given locations
        """
        features = list()

        for loc in locs:
            if loc not in self.features:
                continue
            if typ not in self.features[loc]:
                continue

            features.extend(self.features[loc][typ])

        return features

    def get_io_name(self, loc, constraints=None):
        """
        Formats IO port name. Returns the name and the associated pad.
        """
        name = "PAD_X{}Y{}".format(loc.x, loc.y)

        pad = self.io_names.get(loc, None)
        if pad is not None:
            if constraints and pad in constraints:
                name = constraints[pad]
            else:
                name = "PAD_" + pad

        return name, pad

    def decode_switchbox(self, switchbox, features):
        """
        Decodes all switchboxes to extract full connections' info.

        For every output, this method determines its input in the routing
        switchboxes. In this representation, an input and output can be either
        directly connected to a BEL, or to a hop wire.

        Parameters
        ----------
        switchbox: a Switchbox object from vpr_switchbox_types
        features: features regarding given switchbox

        Returns
        -------
        dict: a mapping from output pin to input pin for a given switchbox
        """

        # Group switchbox connections by destinationa
        conn_by_dst = defaultdict(set)
        for c in switchbox.connections:
            conn_by_dst[c.dst].add(c)

        # Prepare data structure
        mux_sel = {}
        for stage_id, stage in switchbox.stages.items():
            mux_sel[stage_id] = {}
            for switch_id, switch in stage.switches.items():
                mux_sel[stage_id][switch_id] = {}
                for mux_id, mux in switch.muxes.items():
                    mux_sel[stage_id][switch_id][mux_id] = None

        for feature in features:
            assert mux_sel[feature.stage_id][feature.switch_id][
                feature.mux_id] is None, feature  # noqa: E501
            mux_sel[feature.stage_id][feature.switch_id][
                feature.mux_id] = feature.sel_id  # noqa: E501

        def expand_mux(out_loc):
            """
            Expands a multiplexer output until a switchbox input is reached.
            Returns name of the input or None if not found.

            Parameters
            ----------
            out_loc: the last output location

            Returns
            -------
            str: None if input name not found, else string
            """

            # Get mux selection, If it is set to None then the mux is
            # not active
            sel = mux_sel[out_loc.stage_id][out_loc.switch_id][out_loc.mux_id]
            if sel is None:
                return None

            stage = switchbox.stages[out_loc.stage_id]
            switch = stage.switches[out_loc.switch_id]
            mux = switch.muxes[out_loc.mux_id]
            pin = mux.inputs[sel]

            if pin.name is not None:
                return pin.name

            inp_loc = SwitchboxPinLoc(
                stage_id=out_loc.stage_id,
                switch_id=out_loc.switch_id,
                mux_id=out_loc.mux_id,
                pin_id=sel,
                pin_direction=PinDirection.INPUT
            )

            # Expand all "upstream" muxes that connect to the selected
            # input pin

            #assert inp_loc in conn_by_dst, inp_loc
            if inp_loc not in conn_by_dst:
                return None

            for c in conn_by_dst[inp_loc]:
                inp = expand_mux(c.src)
                if inp is not None:
                    return inp

            # Nothing found
            return None

        # For each output pin of a switchbox determine to which input is it
        # connected to.
        routes = {}
        for out_pin in switchbox.outputs.values():
            out_loc = out_pin.locs[0]
            routes[out_pin.name] = expand_mux(out_loc)

        return routes

    def decode_routing(self):
        """
        Decodes routing
        """

        self.switchbox_routes = defaultdict(dict)
        self.global_routes = []

        # Handle all routing features - decode switchboxes
        for loc in self.features.keys():
            features = self.get_features_at_locs([loc], "ROUTING")

            if loc in self.switchbox_grid:
                typ = self.switchbox_grid[loc]
                switchbox = self.switchbox_types[typ]

                routes = self.decode_switchbox(switchbox, features)
                self.switchbox_routes[loc] = routes

            # FASM features for a non-existent switchbox
            else:
                print("", "WARNING: No switchbox at {}".format(loc))

        def walk(ep):
            """
            Recursive walker from a connection destination endpoint to its
            driving souce one.
            """

            # Find and traverse the connection
            conn = self.connections_to.get(ep, None)
            if conn is None:
                print("", "WARNING: No connection to {}".format(ep))
                return ConnectionLoc(ep.loc, None, ConnectionType.UNSPEC)

            ep = conn.src

            # This is a connection from a switchbox, traverse it
            if ep.type == ConnectionType.SWITCHBOX:

                # Use decoded switchbox routes, return the endpoint if the
                # switchbox is not set
                inp = self.switchbox_routes[ep.loc].get(str(ep.pin), None)
                if inp is None:
                    return ConnectionLoc(ep.loc, None, ConnectionType.UNSPEC)

                # We have hit a const
                if inp in ["VCC", "GND"]:
                    return ConnectionLoc(ep.loc, inp, ConnectionType.UNSPEC)

                # Recurse
                ep = ConnectionLoc(ep.loc, inp, ConnectionType.SWITCHBOX)
                return walk(ep)

            return ep

        # Trace all design connections
        for conn in self.connections:

            # Skip connections to switchbox
            if conn.dst.type == ConnectionType.SWITCHBOX:
                continue

            # Walk from sink to source
            ep = walk(conn.dst)
            if ep.pin is not None:
                self.global_routes.append((ep, conn.dst,))

    def build_netlist(self):
        """
        Builds initial netlist basing on decoded global routing.
        """

        self.netlist = Netlist("top")

        def get_type_name_pin(ep):

            # The endpoint pin is a string
            if isinstance(ep.pin, str):
                cell, pin = ep.pin.split(".", maxsplit=1)

                if ep.type == ConnectionType.CLOCK:
                    cell = cell.replace("_TL", "")
                    cell = cell.replace("_TR", "")
                    cell = cell.replace("_BL", "")
                    cell = cell.replace("_BR", "")                    

                if cell.startswith("CAND"):
                    cell = cell.split("_", maxsplit=1)[0]

                if cell[-1].isdigit():
                    name = cell
                    cell = cell[:-1]
                else:
                    name = cell + "0"

            # The endpoint pin is a TilePin
            else:
                cell = ep.pin.cell
                name = "{}{}".format(ep.pin.cell, ep.pin.index)
                pin  = ep.pin.pin

            # Handle mult-loc cells
            if cell in self.multiloc_cells:
                name = self.loc_to_cell_name[ep.loc][cell]
            else:
                name = "{}_X{}Y{}".format(name, ep.loc.x, ep.loc.y)

            return (cell, name, pin)

        # Identify all cell instances, their placement and port connections
        self.placement = defaultdict(set)
        connections = defaultdict(dict) 
        for eps in self.global_routes:

            # Format net name. Unify constant nets
            if eps[0].pin == "GND":
                net = "1'b0"
            elif eps[0].pin == "VCC":
                net = "1'b1"
            else:
                _, name, pin = get_type_name_pin(eps[0])
                net = "{}_{}".format(name, pin)

            # Collect instances
            for ep in eps:

                if ep.type not in [ConnectionType.TILE, ConnectionType.CLOCK]:
                    continue

                typ, name, pin = get_type_name_pin(ep)

                # Add the instance placement and connection
                self.placement[name].add(ep.loc)
                connections[(typ, name)][pin] = net

        # Add instances
        for (typ, instance), port_connections in connections.items():

            # Get cell type from the library
            cell_type = self.cells_library[typ]
            # Add the cell
            cell = self.netlist.add_cell(instance, cell_type)

            # Set port connections
            for port, net in port_connections.items():

                if port not in cell.connections:
                    print("", "WARNING: Port '{}' not present in the definition of cell type '{}'".format(port, cell.type))

                cell.connections[port] = net

    def handle_logic_cells(self):
        """
        Converts LOGIC cells to logic_cell_macro. Prunes powered-down cells.
        """

        for cell_name in list(self.netlist.cells.keys()):

            cell = self.netlist.cells[cell_name]
            if cell.type != "LOGIC":
                continue

            locs = self.placement[cell_name]
            assert len(locs) == 1, (cell_name, locs)
            features = {f.name: f.value for f in self.get_features_at_locs(locs)}

            # The LOGIC cell is not powered, remove it completely
            if "LOGIC.Ipwr_gates.J_pwr_st" not in features:
                self.netlist.remove_cell(cell_name, True)
                continue

            # Add ports controlling inverters
            cell.connections["TAS1"] = \
                "1'b1" if "LOGIC.INV.TA1" in features else "1'b0"
            cell.connections["TAS2"] = \
                "1'b1" if "LOGIC.INV.TA2" in features else "1'b0"
            cell.connections["TBS1"] = \
                "1'b1" if "LOGIC.INV.TB1" in features else "1'b0"
            cell.connections["TBS2"] = \
                "1'b1" if "LOGIC.INV.TB2" in features else "1'b0"
            cell.connections["BAS1"] = \
                "1'b1" if "LOGIC.INV.BA1" in features else "1'b0"
            cell.connections["BAS2"] = \
                "1'b1" if "LOGIC.INV.BA2" in features else "1'b0"
            cell.connections["BBS1"] = \
                "1'b1" if "LOGIC.INV.BB1" in features else "1'b0"
            cell.connections["BBS2"] = \
                "1'b1" if "LOGIC.INV.BB2" in features else "1'b0"

            # Clock inversion
            cell.connections["QCKS"] = \
                "1'b0" if "LOGIC.ZINV.QCK" in features else "1'b1"

            # TODO: Possibly split the macro into individual blocks

            # Change type
            cell.type = "logic_cell_macro"

    def handle_bidir_cells(self, pcf_data):

        for cell_name in list(self.netlist.cells.keys()):

            cell = self.netlist.cells[cell_name]
            if cell.type != "BIDIR":
                continue

            locs = self.placement[cell_name]
            assert len(locs) == 1, (cell_name, locs)
            features = {f.name: f.value for f in self.get_features_at_locs(locs)}

            loc = next(iter(locs))

            # The BIDIR is unconnected, remove it completely
            if not cell.connections.get("IZ", "") and \
               not cell.connections.get("IQZ", "") and \
               not cell.connections.get("OQI", ""):
                del self.netlist.cells[cell_name]
                continue

            # Input
            is_input = cell.connections.get("INEN", "") not in ["", "1'b0"]

            if not cell.connections.get("IZ", "") and \
               not cell.connections.get("IQZ", ""):
                is_input = False

            # Output
            is_output = cell.connections.get("IE", "") not in ["", "1'b0"]

            if not cell.connections.get("OQI", ""):
                is_output = False

            # Determine IO direction
            if is_input and not is_output:
                direction = "input"
            elif not is_input and is_output:
                direction = "output"
            elif is_input and is_output:
                direction = "inout"
            else:
                self.netlist.remove_cell(cell_name, True)
                continue

            # Determine IO port name
            net, pad = self.get_io_name(loc, pcf_data)
            self.io_constraints[net] = {
                "loc": pad
            }

            # Add the top-level port and its connection to BIDIR.IP
            self.netlist.ports[direction].append(net)
            cell.connections["IP"] = net

            # Mark the cell port direction
            if direction == "input":
                cell.ports["IP"] = PinDirection.INPUT
            else:
                cell.ports["IP"] = PinDirection.OUTPUT

            # Add ports controlling inverters
            cell.connections["ESEL"] = \
                "1'b0" if "BIDIR.INV.ESEL" in features else "1'b1"
            cell.connections["OSEL"] = \
                "1'b0" if "BIDIR.INV.OSEL" in features else "1'b1"

            cell.connections["FIXHOLD"] = \
                "1'b1" if "BIDIR.INV.FIXHOLD" in features else "1'b0"
            cell.connections["WPD"] = \
                "1'b1" if "BIDIR.INV.WPD" in features else "1'b0"
            cell.connections["DS"] = \
                "1'b1" if "BIDIR.INV.DS" in features else "1'b0"

            # TODO: Are there any bits controling IQCS ?

            # Change type
            cell.type = "gpio_cell_macro"

    def handle_clock_cells(self, pcf_data):

        for cell_name in list(self.netlist.cells.keys()):

            cell = self.netlist.cells[cell_name]
            if cell.type != "CLOCK":
                continue

            locs = self.placement[cell_name]
            assert len(locs) == 1, (cell_name, locs)
            features = {f.name: f.value for f in self.get_features_at_locs(locs)}

            loc = next(iter(locs))

            # The clock input is disabled, remove it
            if "ASSP.INV.ASSPInvPortAlias" not in features:
                self.netlist.remove_cell(cell_name, True)
                continue

            # Determine IO port name
            net, pad = self.get_io_name(loc, pcf_data)
            self.io_constraints[net] = {
                "loc": pad
            }

            # Add the top-level port and its connection to CLOCK.P
            self.netlist.ports["input"].append(net)
            cell.connections["P"] = net
            cell.ports["P"] = PinDirection.INPUT

            # Rename the output port
            cell.rename_port("IC", "Q")

            # Change type
            cell.type = "ckpad"

    def handle_gmux_cells(self):

        for cell_name in list(self.netlist.cells.keys()):

            cell = self.netlist.cells[cell_name]
            if cell.type != "GMUX":
                continue

            # The GMUX is unused, remove it completely
            if not cell.connections.get("IC", "") and \
               not cell.connections.get("IP", ""):
                self.netlist.remove_cell(cell_name, True)
                continue

            # Examine the IS0 connection
            is0 = cell.connections.get("IS0", "")
            if not is0:
                print("", "WARNING: Cell '{}' has the 'IS0' input unconnected, prunning...".format(cell.name))

                self.netlist.remove_cell(cell_name, True)
                continue

            # Static clock from "clock", implicit pass-through
            if is0 == "1'b0":

                inp_net = cell.connections["IP"]
                out_net = cell.connections["IZ"]
                self.netlist.remove_cell(cell_name)

                self.netlist.rename_net(out_net, inp_net)

            # Static clock from routing. Add an instance of gclkbuff
            elif is0 == "1'b1":

                cell.rename_port("IC", "A")
                cell.rename_port("IZ", "Q")
                del cell.connections["IS0"]

                cell.type = "gclkbuff"

            # Dynamic
            else:
                raise Exception("{} uses dynamic selection which is not supported yet".format(cell.name))

    def handle_qmux_cells(self):

        for cell_name in list(self.netlist.cells.keys()):

            cell = self.netlist.cells[cell_name]
            if cell.type != "QMUX":
                continue

            # FIXME:
            #del self.netlist.cells[cell_name]

    def handle_cand_cells(self):

        for cell_name in list(self.netlist.cells.keys()):

            cell = self.netlist.cells[cell_name]
            if cell.type != "CAND":
                continue

            # Get location(s)
            locs = self.placement[cell_name]
            assert len(locs) == 1, (cell_name, locs)
            loc = next(iter(locs))

            # Fixup location. Even CAND cells are located on even rows while
            # odd ones in odd rows. However, FASM features mention only even
            # rows. For odd indices take features from the even row above.
            cand_name = cell_name.split("_", maxsplit=1)[0]
            if cand_name in ["CAND1", "CAND3"]:
                loc = Loc(loc.x, loc.y + 1, 0)

            # Get features
            features = {f.name: f.value for f in self.get_features_at_locs(loc)}
            print(cand_name, loc, features)

            # Filter features
            features = {k: v for k, v in features.items() \
                        if k.split(".", maxsplit=1)[0] == cand_name}

            hilojoint = "{}.I_hilojoint".format(cand_name) in features
            enjoint = "{}.I_enjoint".format(cand_name) in features

            # TODO: Do not support dynamically enabled CANDs for now.
            assert enjoint is False, "Dynamically enabled CANDs are not supported yet"

            # Statically disabled, remove
            if hilojoint is False:
                self.netlist.remove_cell(cell_name, True)
                continue

            # Convert to a buffer
            del cell.ports["EN"]
            del cell.connections["EN"]
            cell.rename_port("IC", "i")
            cell.rename_port("IZ", "o")
            cell.type = "$buf"

    def process_netlist(self, pcf_data):
        """
        Processes the netlist
        """

        self.handle_logic_cells()
        self.handle_bidir_cells(pcf_data)
        self.handle_clock_cells(pcf_data)
        self.handle_gmux_cells()
        self.handle_qmux_cells()
        self.handle_cand_cells()

        # Iteratively prune unused nets / cells from the netlist
        while True:
            self.netlist.prune_dangling_nets()
            if not self.netlist.prune_leaf_cells():
                break

    def run(self, fasm_lines, pcf_data=None):
        """
        Main fasm2bels flow entry procedure
        """

        # Parse and group FASM features
        print("Processing FASM features...")
        self.parse_fasm_lines(fasm_lines)

        # Decode routing (switchbox configuration)
        print("Decoding routing...")
        self.decode_routing()

        # Build netlist
        print("Building netlist...")
        self.build_netlist()

        # Process netlist
        print("Processing netlist...")
        self.process_netlist(pcf_data)

    def dump_pcf(self):
        """
        Generates PCF file content for decoded IO constraints
        """
        code = ""
        for key in sorted(list(self.io_constraints.keys())):
            constraints = self.io_constraints[key]
            code += "set_io {} {}\n".format(key, constraints["loc"])

        return code

    def dump_qcf(self):
        """
        Generates QCF file content for decoded IO constraints
        """
        code = "#[Fixed Pin Placement]\n"
        for key in sorted(list(self.io_constraints.keys())):
            constraints = self.io_constraints[key]
            code += "place {} {}\n".format(key, constraints["loc"])

        return code

# =============================================================================

# FIXME: Use more roboust PCF parser
def parse_pcf(pcf):
    pcf_data = {}
    with open(pcf, 'r') as fp:
        for line in fp:
            line = line.strip().split()
            if len(line) < 3:
                continue
            if len(line) > 3 and not line[3].startswith("#"):
                continue
            if line[0] != 'set_io':
                continue
            pcf_data[line[2]] = line[1]
    return pcf_data

# =============================================================================


def main():

    # Parse arguments
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "input_file",
        type=Path,
        help="Input FASM/bitstream file"
    )

    parser.add_argument(
        "--phy-db",
        type=str,
        required=True,
        help="Physical device database file"
    )

    parser.add_argument(
        "--device-name",
        type=str,
        required=True,
        choices=["eos-s3", "pp3", "pp3e"],
        help="Device name"
    )
    parser.add_argument(
        "--package-name",
        type=str,
        required=True,
        help="Device package name"
    )

    parser.add_argument(
        "--input-type",
        type=str,
        choices=['bitstream', 'fasm'],
        default='bitstream',
        help="Input type ('bitstream' or 'fasm')"
    )

    parser.add_argument(
        "--input-pcf",
        type=Path,
        required=False,
        help="Input PCF constraint file (to preserve original port names)"
    )

    parser.add_argument(
        "--output-verilog",
        type=Path,
        required=True,
        help="Output Verilog file name"
    )
    parser.add_argument(
        "--output-pcf",
        type=Path,
        required=False,
        help="Output PCF file"
    )
    parser.add_argument("--output-qcf",
        type=Path,
        required=False,
        help="Output QCF file"
    )

    args = parser.parse_args()

    # Load input PCF constraints if given
    pcf_data = {}
    if args.input_pcf is not None:
        pcf_data = parse_pcf(args.input_pcf)

    # Load data from the database
    print("Loading device database...")
    with open(args.phy_db, "rb") as fp:
        db = pickle.load(fp)

    # Disassemble bitstream + parse FASM
    if args.input_type == 'bitstream':
        print("Disassembling bitstream...")

        from quicklogic_fasm.qlfasm import load_quicklogic_database, get_db_dir
        from quicklogic_fasm.qlfasm import QL732BAssembler, QL725AAssembler

        qlfasmdb = load_quicklogic_database(
            get_db_dir("ql-" + args.device_name)
        )

        if args.device_name == "eos-s3":
            assembler = QL732BAssembler(qlfasmdb)

        elif args.device_name == "pp3":
            assembler = QL725AAssembler(
                qlfasmdb,
                spi_master=True,
                osc_freq=False,
                cfg_write_chcksum_post=False,
                cfg_read_chcksum_post=False,
                cfg_done_out_mask=False,
                add_header=True,
                add_checksum=True
            )

        elif args.device_name == "pp3e":
            raise RuntimeError("PP3E not supported yet")

        else:
            assert False, args.device_name

        assembler.read_bitstream(args.input_file)
        fasm_lines = assembler.disassemble()
        fasm_lines = [
            line for line in fasm.parse_fasm_string('\n'.join(fasm_lines))
        ]

    # Load and parse FASM
    else:
        print("Parsing FASM...")
        fasm_lines = [
            line for line in fasm.parse_fasm_filename(args.input_file)
        ]

    # Run FASM to bels
    try:
        f2b = Fasm2Bels(db, args.device_name, args.package_name)
        f2b.run(fasm_lines, pcf_data)

    except Fasm2Bels.Exception as ex:
        print(str(ex))
        exit(-1)

    # Write output file(s)
    print("Writing output file(s)...")

    with open(args.output_verilog, "w") as fp:
        fp.write(f2b.netlist.dump_verilog())

    if args.output_pcf:
        with open(args.output_pcf, 'w') as fp:
            fp.write(f2b.dump_pcf())

    if args.output_qcf:
        with open(args.output_qcf, 'w') as fp:
            fp.write(f2b.dump_qcf())

if __name__ == "__main__":
    main()

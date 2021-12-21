#!/usr/bin/env python3
"""
This utility generates a FASM file with a default bitstream configuration for
the given device.
"""
import argparse
import pickle

from data_structs import ConnectionType

from switchbox_router import SwitchboxRouter

# =============================================================================

# FIXME: Move to eg. a JSON file
DEFAULT_CONNECTIONS = {

    "LOGIC": {
        "TBS": "GND",
        "TAB": "GND",
        "TSL": "GND",
        "TA1": "GND",
        "TA2": "GND",
        "TB1": "GND",
        "TB2": "GND",
        "BAB": "GND",
        "BA1": "GND",
        "BA2": "GND",
        "BB1": "GND",
        "BB2": "GND",
        "QCK": "GND",
        "QRT": "GND",
        "QST": "GND",
        "QEN": "GND",
        "QDS": "GND",
        "QDI": "GND",
        "F1": "GND",
        "F2": "GND",
        "FS": "GND",
    },

    "BIDIR": {
        "IE": "GND",
        "OQI": "GND",
        "OQE": "GND",
        "IQE": "GND",
        "INEN": "GND",
        "IQIN": "GND",
        "IQR": "GND",
        "IQC": "GND",
    },

    "QMUX": {
        "IS0": "VCC",
        "IS1": "VCC",
        "HSCKIN": "GND",
    },

    "GMUX": {
        "IS0": "VCC",
        "IC": "GND",
    },
}

# =============================================================================


class SwitchboxConfigBuilder:
    """
    A class responsible for building configuration of an unused switchbox
    """

    def __init__(self, db, default_connections):

        self.dot = None

        self.switchbox_types = db["switchbox_types"]
        self.switchbox_grid = db["switchbox_grid"]

        self.default_connections = default_connections

        # Sort connections by their source locations
        connections = db["connections"]
        self.connections_by_src = {}

        for conn in connections:
            loc = conn.src.loc
            if loc not in self.connections_by_src:
                self.connections_by_src[loc] = []
            self.connections_by_src[loc].append(conn)

    def build(self, loc, dump_dot=False, allow_routing_failures=False, verbose=0):
        """
        Builds default configuration for a switchbox at the given locatio.
        Returns a list of FASM features
        """

        # Get the switchbox type
        switchbox_loc = loc
        switchbox_type = self.switchbox_grid[loc]
        switchbox = self.switchbox_types[switchbox_type]

        if verbose >= 1:
            print("Switchbox '{}' at {}".format(switchbox_type, switchbox_loc))

        # Initialize router
        router = SwitchboxRouter(switchbox)
        routing_failed = False

        # Determine how to route specific outputs
        pin_connections = {}
        if loc in self.connections_by_src:

            # Find all connections that go from this switchbox to a tile
            conns = [c for c in self.connections_by_src[switchbox_loc] if \
                     c.src.type == ConnectionType.SWITCHBOX and \
                     c.dst.type != ConnectionType.SWITCHBOX]

            # Identify required tile pin connections
            for c in conns:
                cell_conns = self.default_connections.get(c.dst.pin.cell, None)
                if cell_conns:
                    net = str(cell_conns.get(c.dst.pin.pin, ""))
                    if net:
                        pin_connections[c.src.pin] = net

        # Determine which inputs to propagate (HIGHWAY)
        pin_propagations = set()
        for c in conns:

            # Find all connections that go from this switchbox to a tile
            conns = [c for c in self.connections_by_src[switchbox_loc] if \
                     c.src.type != ConnectionType.SWITCHBOX and \
                     c.dst.type == ConnectionType.SWITCHBOX]

            for c in conns:
                pin = c.dst.pin
                if pin in router.nodes["HIGHWAY"]:
                    pin_propagations.add(pin)

        # Route required tile pins first
        for pin, net in pin_connections.items():

            if verbose >= 1:
                print(" routing '{}' to '{}'".format(pin, net))

            res = router.route_output_to_input("STREET", pin, net)
            if not res:
                routing_failed = True

                if verbose >= 1:
                    print("  failed!")

        # Propagate pins
        for pin in pin_propagations:

            if verbose >= 1:
                print(" propagating '{}'".format(pin))

            router.propagate_input("HIGHWAY", pin)

        # Next route all unrouted mux outputs
        if verbose >= 2:
            print(" finalizing...");

        router.route_all("HIGHWAY")
        router.route_all("STREET")

        # Check if all nodes are configured
        if not router.check_nodes():
            routing_failed = True

        if verbose >= 1 and not routing_failed:
            print(" fully routed.")

        # Store graphviz visualization
        if dump_dot:
            self.dot = router.dump_dot()
        else:
            self.dot = None

        if routing_failed:
            print("Routing for switchbox '{}' at {} failed!".format(
                switchbox.type, switchbox_loc
            ))
            if not allow_routing_failures:
                exit(-1)

        # Return FASM features
        return router.fasm_features(loc)

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
        "--fasm",
        type=str,
        default="default.fasm",
        help="Output FASM file name"
    )
    parser.add_argument(
        "--device",
        type=str,
        choices=["eos-s3", "pp3"],
        default="eos-s3",
        help="Device name to generate the FASM file for"
    )
    parser.add_argument(
        "--dump-dot",
        action="store_true",
        help="Dump Graphviz .dot files for each routed switchbox type"
    )
    parser.add_argument(
        "--allow-routing-failures",
        action="store_true",
        help="Skip switchboxes that fail routing"
    )
    parser.add_argument(
        "--verbose",
        type=int,
        default=0,
        help="Verbosity level"
    )

    args = parser.parse_args()

    # Load data from the database
    print("Loading device database...")
    with open(args.phy_db, "rb") as fp:
        db = pickle.load(fp)
        tile_types = db["tile_types"]
        tile_grid = db["phy_tile_grid"]
        switchbox_grid = db["switchbox_grid"]

    # Configure switchboxes
    print("Making switchbox routes...")
    builder = SwitchboxConfigBuilder(db, DEFAULT_CONNECTIONS)

    fasm = []
    for sbox_loc, sbox_type in switchbox_grid.items():

        # Build config
        sbox_fasm = builder.build(sbox_loc, args.dump_dot, args.allow_routing_failures, args.verbose)
        fasm.extend(sbox_fasm)

        # Write graphviz for debugging
        if builder.dot:
            fn = "{}_at_X{}Y{}.dot".format(sbox_type, sbox_loc.x, sbox_loc.y)
            with open(fn, "w") as fp:
                fp.write(builder.dot)

    # Power on all LOGIC cells. Since there is no way to route any of the
    # HIGHWAY output to GND/VCC they are routed to tile outpus. For tile
    # outputs to generate a stable logic level the power must be on.
    print("Configuring cells...")
    for loc, tile in tile_grid.items():

        # Get the tile type object
        tile_type = tile_types[tile.type]

        # If this tile has a LOGIC cell then emit the FASM feature that
        # enables its power
        if "LOGIC" in tile_type.cells:
            feature = "X{}Y{}.LOGIC.LOGIC.Ipwr_gates.J_pwr_st".format(
                loc.x, loc.y
            )
            fasm.append(feature)

    # Write FASM
    print("Writing FASM file...")
    with open(args.fasm, "w") as fp:
        fp.write("\n".join(fasm) + "\n")


# =============================================================================


if __name__ == "__main__":
    main()

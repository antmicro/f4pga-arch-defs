#!/usr/bin/env python3
"""
This utility generates a FASM file with a default bitstream configuration for
the given device.
"""
import argparse
import random
import colorsys
from enum import Enum

import lxml.etree as ET

from data_structs import *
from data_import import import_data

from utils import yield_muxes

from switchbox_model import SwitchboxModel

# =============================================================================

class SwitchboxConfigBuilder:
    """
    This class is responsible for routing a switchbox according to the
    requested parameters and writing FASM features that configure it.
    """

    class NodeType(Enum):
        MUX = 0
        SOURCE = 1
        SINK = 2

    class Node:
        """
        Represents a graph node that corresponds either to a switchbox mux
        output or to a virtual source / sink node.
        """
        def __init__(self, type, key):
            self.type = type
            self.key = key

            # Current "net"
            self.net = None

            # Mux input ids indexed by keys and mux selection
            self.inp = {}
            self.sel = None

    def __init__(self, switchbox):
        self.switchbox = switchbox
        self.nodes = {}

        # Build nodes representing the switchbox connectivity graph
        self._build_nodes()

    def _build_nodes(self):
        """
        Creates all nodes for routing.
        """

        # Create all mux nodes
        for stage, switch, mux in yield_muxes(self.switchbox):

            # Create the node
            key = (stage.id, switch.id, mux.id)
            node = self.Node(self.NodeType.MUX, key)

            # Store the node
            if stage.type not in self.nodes:
                self.nodes[stage.type] = {}

            assert node.key not in self.nodes[stage.type], (stage.type, node.key)
            self.nodes[stage.type][node.key] = node

        # Create all source and sink nodes, populate their connections with mux
        # nodes.
        for pin in self.switchbox.pins:

            # Node type
            if pin.direction == PinDirection.INPUT:
                node_type = self.NodeType.SOURCE
            elif pin.direction == PinDirection.OUTPUT:
                node_type = self.NodeType.SINK
            else:
                assert False, node_type

            # Create one for each stage type
            stage_ids = set([loc.stage_id for loc in pin.locs])
            for stage_id in stage_ids:

                # Create the node
                key = pin.name
                node = self.Node(node_type, key)

                # Initially annotate source nodes with net names
                if node.type == self.NodeType.SOURCE:
                    node.net = pin.name

                # Get the correct node list
                stage_type = self.switchbox.stages[stage_id].type
                assert stage_type in self.nodes, stage_type
                nodes = self.nodes[stage_type]

                # Add the node
                assert node.key not in self.nodes, node.key
                nodes[node.key] = node

            # Populate connections
            for pin_loc in pin.locs:

                # Get the correct node list
                stage_type = self.switchbox.stages[pin_loc.stage_id].type
                assert stage_type in self.nodes, stage_type
                nodes = self.nodes[stage_type]

                if pin.direction == PinDirection.INPUT:

                    # Get the mux node
                    key = (pin_loc.stage_id, pin_loc.switch_id, pin_loc.mux_id)
                    assert key in nodes, key
                    node = nodes[key]

                    # Append reference to the input pin to the node
                    key = pin.name
                    assert key == "GND" or key not in node.inp, key
                    node.inp[key] = pin_loc.pin_id

                elif pin.direction == PinDirection.OUTPUT:

                    # Get the sink node
                    key = pin.name
                    assert key in nodes, key
                    node = nodes[key]
                    assert node.type == self.NodeType.SINK

                    # Append reference to the mux
                    key = (pin_loc.stage_id, pin_loc.switch_id, pin_loc.mux_id)
                    node.inp[key] = 0

                else:
                    assert False, pin.direction

        # Populate mux to mux connections
        for conn in self.switchbox.connections:

            # Get the correct node list
            stage_type = self.switchbox.stages[conn.dst.stage_id].type
            assert stage_type in self.nodes, stage_type
            nodes = self.nodes[stage_type]

            # Get the node
            key = (conn.dst.stage_id, conn.dst.switch_id, conn.dst.mux_id)
            assert key in nodes, key
            node = nodes[key]

            # Add its input and pin index
            key = (conn.src.stage_id, conn.src.switch_id, conn.src.mux_id)
            node.inp[key] = conn.dst.pin_id

    def stage_inputs(self, stage_type):
        """
        Yields inputs of the given stage type
        """
        assert stage_type in self.nodes, stage_type
        for node in self.nodes[stage_type].values():
            if node.type == self.NodeType.SOURCE:
                yield node.key

    def stage_outputs(self, stage_type):
        """
        Yields outputs of the given stage type
        """
        assert stage_type in self.nodes, stage_type
        for node in self.nodes[stage_type].values():
            if node.type == self.NodeType.SINK:
                yield node.key

    def route_output(self, stage_type, output_name, net):
        """
        Routes the given output of a stage type to the given input net name.
        Net names are initially input port names.
        """

        # Get the correct node list
        assert stage_type in self.nodes, stage_type
        nodes = self.nodes[stage_type]

        def walk(node, path=None):

            # Initialize path
            if path is None:
                path = []

            # Append the current node to the path
            path = [node.key] + path

            # We've hit the net we want. Terminate
            if node.net == net:
                return path

            # Recurse for all upstream connections
            for key, pin in node.inp.items():

                # Recurse
                assert key in nodes, key
                res = walk(nodes[key], list(path))

                # Got a path, terminate
                if res:
                    return res

            # No path found
            return None

        # Find the sink node        
        assert output_name in nodes, output_name
        sink_node = nodes[output_name]

        # Walk upstream
        path = walk(sink_node)
        if not path:
            return False

        # Mark the path
        for node_key, drv_key in zip(path, [None] + path[:-1]):

            # Set the net
            assert node_key in nodes, key
            node = nodes[node_key]
            node.net = net

            # Set selection
            if drv_key is not None:
                assert drv_key in node.inp, drv_key
                node.sel = node.inp[drv_key]

        return True

    def ripup(self, stage_type):
        """
        Rips up all routes within the given stage
        """
        assert stage_type in self.nodes, stage_type
        for node in self.nodes[stage_type].values():
            if node.type != self.NodeType.SOURCE:
                node.net = None
                node.sel = None

    def fasm_features(self, loc):
        """
        Returns a list of FASM lines that correspond to the routed switchbox
        configuration.
        """
        lines = []

        for stage_type, nodes in self.nodes.items():
            for key, node in nodes.items():

                # For muxes with active selection
                if node.type == self.NodeType.MUX and node.sel is not None:
                    stage_id, switch_id, mux_id = key

                    # Get FASM features using the switchbox model.
                    features = SwitchboxModel.get_metadata_for_mux(
                        loc,
                        self.switchbox.stages[stage_id],
                        switch_id,
                        mux_id,
                        node.sel
                    )
                    lines.extend(features)

        return lines

    def dump_dot(self):
        """
        Dumps a routed switchbox visualization into Graphviz format for
        debugging purposes.
        """
        dot = []

        def key2str(key):
            if isinstance(key, str):
                return key
            else:
                return "st{}_sw{}_mx{}".format(*key)

        def fixup_label(lbl):
            lbl = lbl.replace("[", "(").replace("]", ")")

        # All nets
        nets = set()
        for nodes in self.nodes.values():
            for node in nodes.values():
                if node.net is not None:
                    nets.add(node.net)

        # Net colors
        node_colors = {None: "#C0C0C0"}
        edge_colors = {None: "#000000"}

        nets = sorted(list(nets))
        for i, net in enumerate(nets):

            h = i / len(nets)
            l = 0.33
            s = 1.0

            r, g, b = colorsys.hls_to_rgb(h, l, s)
            color = "#{:02X}{:02X}{:02X}".format(
                int(r * 255.0),
                int(g * 255.0),
                int(b * 255.0),
            )

            node_colors[net] = color
            edge_colors[net] = color

        # Add header
        dot.append("digraph {} {{".format(self.switchbox.type))
        dot.append("  graph [nodesep=\"1.0\", ranksep=\"20\"];")
        dot.append("  splines = \"false\";")
        dot.append("  rankdir = LR;")
        dot.append("  margin = 20;")
        dot.append("  node [style=filled];")

        # Stage types
        for stage_type, nodes in self.nodes.items():

            # Stage header
            dot.append("  subgraph \"cluster_{}\" {{".format(stage_type))
            dot.append("    label=\"Stage '{}'\";".format(stage_type))

            # Nodes and internal mux edges
            for key, node in nodes.items():

                # Source node
                if node.type == self.NodeType.SOURCE:
                    name = "{}_inp_{}".format(stage_type, key2str(key))
                    label = key
                    color = node_colors[node.net]

                    dot.append("  \"{}\" [shape=octagon label=\"{}\" fillcolor=\"{}\"];".format(
                        name,
                        label,
                        color,
                    ))

                # Sink node
                elif node.type == self.NodeType.SINK:
                    name = "{}_out_{}".format(stage_type, key2str(key))
                    label = key
                    color = node_colors[node.net]

                    dot.append("  \"{}\" [shape=octagon label=\"{}\" fillcolor=\"{}\"];".format(
                        name,
                        label,
                        color,
                    ))

                # Mux node
                elif node.type == self.NodeType.MUX:
                    name = "{}_{}".format(stage_type, key2str(key))
                    dot.append("    subgraph \"cluster_{}\" {{".format(name))
                    dot.append("      label=\"{}\";".format(str(key)))

                    # Inputs
                    for drv_key, pin in node.inp.items():
                        if node.sel == pin:
                            assert drv_key in nodes, drv_key
                            net = nodes[drv_key].net
                        else:
                            net = None

                        name = "{}_{}_{}".format(stage_type, key2str(key), pin)
                        label = pin
                        color = node_colors[net]

                        dot.append("      \"{}\" [shape=ellipse label=\"{}\" fillcolor=\"{}\"];".format(
                            name,
                            label,
                            color,
                        ))

                    # Output
                    name = "{}_{}".format(stage_type, key2str(key))
                    label = "out"
                    color = node_colors[node.net]

                    dot.append("      \"{}\" [shape=ellipse label=\"{}\" fillcolor=\"{}\"];".format(
                        name,
                        label,
                        color,
                    ))

                    # Internal mux edges
                    for drv_key, pin in node.inp.items():
                        if node.sel == pin:
                            assert drv_key in nodes, drv_key
                            net = nodes[drv_key].net
                        else:
                            net = None

                        src_name = "{}_{}_{}".format(stage_type, key2str(key), pin)
                        dst_name = "{}_{}".format(stage_type, key2str(key))
                        color = edge_colors[net]

                        dot.append("      \"{}\" -> \"{}\" [color=\"{}\"];".format(
                            src_name,
                            dst_name,
                            color,
                        ))

                    dot.append("    }")

                else:
                    assert False, node.type

            # Mux to mux connections
            for key, node in nodes.items():

                # Source node
                if node.type == self.NodeType.SOURCE:
                    pass

                # Sink node
                elif node.type == self.NodeType.SINK:
                    assert len(node.inp) == 1, node.inp
                    src_key = next(iter(node.inp.keys()))

                    dst_name = "{}_out_{}".format(stage_type, key2str(key))
                    if isinstance(src_key, str):
                        src_name = "{}_inp_{}".format(stage_type, key2str(src_key))
                    else:
                        src_name = "{}_{}".format(stage_type, key2str(src_key))

                    color=node_colors[node.net]

                    dot.append("    \"{}\" -> \"{}\" [color=\"{}\"];".format(
                        src_name,
                        dst_name,
                        color,
                    ))

                # Mux node
                elif node.type == self.NodeType.MUX:
                    for drv_key, pin in node.inp.items():
                        if node.sel == pin:
                            assert drv_key in nodes, drv_key
                            net = nodes[drv_key].net
                        else:
                            net = None

                        dst_name = "{}_{}_{}".format(stage_type, key2str(key), pin)
                        if isinstance(drv_key, str):
                            src_name = "{}_inp_{}".format(stage_type, key2str(drv_key))
                        else:
                            src_name = "{}_{}".format(stage_type, key2str(drv_key))

                        color=edge_colors[net]

                        dot.append("    \"{}\" -> \"{}\" [color=\"{}\"];".format(
                            src_name,
                            dst_name,
                            color,
                        ))

                else:
                    assert False, node.type

            # Stage footer
            dot.append("  }")

        # Add footer
        dot.append("}")
        return "\n".join(dot)


# =============================================================================


def main():

    # Parse arguments
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--techfile",
        type=str,
        required=True,
        help="Quicklogic 'TechFile' XML file"
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
        choices=["eos-s3"],
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

    args = parser.parse_args()

    # Read and parse the XML file
    xml_tree = ET.parse(args.techfile)
    xml_root = xml_tree.getroot()

    # Load data
    print("Loading data from the techfile...")
    data = import_data(xml_root)
    switchbox_types = data["switchbox_types"]
    switchbox_grid = data["switchbox_grid"]

    # Route switchboxes
    print("Making switchbox routes...")

    fasm = []
    fully_routed = 0
    partially_routed = 0

    for switchbox in switchbox_types.values():
        print("", switchbox.type)

        # Identify all locations of the switchbox
        locs = [loc for loc, type in switchbox_grid.items() \
                if type == switchbox.type]

        # Initialize the builder
        builder = SwitchboxConfigBuilder(switchbox)

        # Route all STREET outputs to GND
        stage = "STREET"
        for output in builder.stage_outputs(stage):
            builder.route_output(stage, output, "GND")

        # Identify all LC inputs of the HIGHWAY stage
        stage = "HIGHWAY"
        inputs = set([pin.name for pin in switchbox.inputs.values() \
            if pin.type not in [SwitchboxPinType.HOP, SwitchboxPinType.GCLK ]])
        inputs = list(inputs & set(builder.stage_inputs(stage)))

        # No imputs from tile, allow any
        if not inputs:
            print("  WARNING: No non-highway inputs to the {} stage".format(stage))
            inputs = list(builder.stage_inputs(stage))

        # Randomly route switchbox outputs to LC outputs. Shuffle lists each
        # time so that if an unroutable situation happens once it is less
        # likely that it would happen again.
        outputs = list(builder.stage_outputs(stage))
        routing_failed = False
        for i in range(1):

            if i > 0:
                print("  Retry routing... ({})".format(i))

            # Ripup if failed previously
            if routing_failed:
                builder.ripup(stage)

            # This is the last retry, use all inputs
            if i == 2:
                print("  WARNING: Using all available inputs of the switchbox")
                inputs = list(builder.stage_inputs(stage))

            # Try
            routing_failed = False
            random.shuffle(outputs)
            for output in builder.stage_outputs(stage):
                random.shuffle(inputs)
                for net in inputs:
                    if builder.route_output(stage, output, net):
                        break
                else:
                    print("  Routing failed: {}, {} -> {}".format(stage, output, net))
                    routing_failed = True

            # Success, terminate
            if not routing_failed:
                break

        # Routing failed
        else:
            print("  ERROR: Routing failed after several retries!")

        # Dump dot
        if args.dump_dot:
            dot = builder.dump_dot()
            fname = "defconfig_{}.dot".format(switchbox.type)
            with open(fname, "w") as fp:
                fp.write(dot)

        # Routing failed
        if routing_failed:
            if not args.allow_routing_failures:
                exit(-1)

        # Stats
        if routing_failed:
            partially_routed += len(locs)
        else:
            fully_routed += len(locs)

        # Emit FASM features for each of them
        for loc in locs:
            fasm.extend(builder.fasm_features(loc))

    print(" Total switchboxes: {}".format(len(switchbox_grid)))
    print(" Fully routed     : {}".format(fully_routed))
    print(" Partially routed : {}".format(partially_routed))

    # Write FASM
    print("Writing FASM file...")
    with open(args.fasm, "w") as fp:
        fp.write("\n".join(fasm))

# =============================================================================

if __name__ == "__main__":
    main()

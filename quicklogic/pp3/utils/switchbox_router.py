#!/usr/bin/env python3
import colorsys
from enum import Enum

from data_structs import PinDirection
from utils import yield_muxes

from switchbox_model import SwitchboxModel

# =============================================================================


class SwitchboxRouter:
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

            # Mux inputs driven by this node as keys
            self.out = set()

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

            assert node.key not in self.nodes[stage.type
                                              ], (stage.type, node.key)
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

                    key = (
                        self.switchbox.type, pin_loc.stage_id,
                        pin_loc.switch_id, pin_loc.mux_id
                    )

                    # Append reference to the input pin to the node
                    key = pin.name

                    # Some muxes can select the same input via multiple
                    # different paths. Allow that but only for primary inputs
                    # which keys are strings.
                    if key in node.inp:
                        assert isinstance(key, str), key
                        continue

                    node.inp[key] = pin_loc.pin_id

                    # Get the SOURCE node
                    key = pin.name
                    assert key in nodes, key
                    node = nodes[key]

                    # Append the mux node as a sink
                    key = (pin_loc.stage_id, pin_loc.switch_id, pin_loc.mux_id)
                    node.out.add(key)

                elif pin.direction == PinDirection.OUTPUT:

                    # Get the sink node
                    key = pin.name
                    assert key in nodes, key
                    node = nodes[key]
                    assert node.type == self.NodeType.SINK

                    # Append reference to the mux
                    key = (pin_loc.stage_id, pin_loc.switch_id, pin_loc.mux_id)
                    node.inp[key] = 0

                    # Get the mux node
                    key = (pin_loc.stage_id, pin_loc.switch_id, pin_loc.mux_id)
                    assert key in nodes, key
                    node = nodes[key]

                    # Append the sink as the mux sink
                    key = pin.name
                    node.out.add(key)

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

            # Get the source node
            key = (conn.src.stage_id, conn.src.switch_id, conn.src.mux_id)
            assert key in nodes, key
            node = nodes[key]

            # Add the destination node to its outputs
            key = (conn.dst.stage_id, conn.dst.switch_id, conn.dst.mux_id)
            node.out.add(key)

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

    def route_output_to_input(self, stage, out, inp):
        """
        Routes from an output pin to an input pin of the given stage. Returns
        whether the routing was successful. For a successful route sets nets
        and selections on all nodes of the route.
        """

        assert stage in self.nodes, stage
        nodes = self.nodes[stage]

        # Input pin is the net name
        net = inp

        # BFS walker
        def walk(node, route=None):

            # Initialize route
            if route is None:
                route = []

            # We have hit the input or any node which is assigned the same
            # net
            if node.net == net:
                return [node.key] + route

            # We have hit a different net
            if node.net is not None:
                return None

            # Free node, expand upstream. First check other nodes that do not
            # have any net assigned.
            uphill = list(node.inp.keys())
            uphill.sort(key=lambda k: nodes[k].net != None)

            for key in uphill:
                r = walk(nodes[key], [node.key] + route)
                if r is not None:
                    return r

            # No more expansion possible
            return None

        # Walk
        route = walk(nodes[out])
        if not route:
            return False

        # Assign nets and mux selections. This needs to be done by iterating
        # the route in reversed order.
        for i in reversed(range(1, len(route))):
            node = nodes[route[i]]
            node.net = net
            node.sel = node.inp[route[i-1]]

        return True

    def route_all(self, stage=None):
        """
        Routes all muxes randomly
        """
        if not stage:
            stages = ["STREET", "HIGHWAY"]
        else:
            stages = [stage]

        # Route stage
        for stage in stages:
            nodes = self.nodes[stage]

            while True:

                all_routed = True
                for node in nodes.values():
                    if not node.net:

                        for key, sel in node.inp.items():
                            if nodes[key].net is not None:
                                node.net = nodes[key].net
                                node.sel = sel
                                break
                            else:
                                all_routed = False

                if all_routed:
                    break

    def propagate_input(self, stage_type, input_name):
        """
        Recursively propagates a net from an input pin to all reachable
        mux / sink nodes.
        """

        # Get the correct node list
        assert stage_type in self.nodes, stage_type
        nodes = self.nodes[stage_type]

        def walk(node):

            # Examine all driven nodes
            for sink_key in node.out:
                assert sink_key in nodes, sink_key
                sink_node = nodes[sink_key]

                # The sink is free
                if sink_node.net is None:

                    # Assign it to the net
                    sink_node.net = node.net
                    if sink_node.type == self.NodeType.MUX:
                        sink_node.sel = sink_node.inp[node.key]

                    # Expand
                    walk(sink_node)

        # Find the source node
        assert input_name in nodes, input_name
        node = nodes[input_name]

        # Walk downstream
        node.net = input_name
        walk(node)

    def ripup(self, stage_type):
        """
        Rips up all routes within the given stage
        """
        assert stage_type in self.nodes, stage_type
        for node in self.nodes[stage_type].values():
            if node.type != self.NodeType.SOURCE:
                node.net = None
                node.sel = None

    def check_nodes(self):
        """
        Check if all mux nodes have their selections set
        """
        result = True

        for stage_type, nodes in self.nodes.items():
            for key, node in nodes.items():

                if node.type == self.NodeType.MUX and node.sel is None:
                    result = False
                    print("WARNING: mux unconfigured", stage_type, key)

        return result

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
                        loc, self.switchbox.stages[stage_id], switch_id,
                        mux_id, node.sel
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

            hue = i / len(nets)
            light = 0.33
            saturation = 1.0

            r, g, b = colorsys.hls_to_rgb(hue, light, saturation)
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

                    dot.append(
                        "  \"{}\" [shape=octagon label=\"{}\" fillcolor=\"{}\"];"
                        .format(
                            name,
                            label,
                            color,
                        )
                    )

                # Sink node
                elif node.type == self.NodeType.SINK:
                    name = "{}_out_{}".format(stage_type, key2str(key))
                    label = key
                    color = node_colors[node.net]

                    dot.append(
                        "  \"{}\" [shape=octagon label=\"{}\" fillcolor=\"{}\"];"
                        .format(
                            name,
                            label,
                            color,
                        )
                    )

                # Mux node
                elif node.type == self.NodeType.MUX:
                    name = "{}_{}".format(stage_type, key2str(key))
                    dot.append("    subgraph \"cluster_{}\" {{".format(name))
                    dot.append(
                        "      label=\"{}, sel={}\";".format(
                            str(key), node.sel
                        )
                    )

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

                        dot.append(
                            "      \"{}\" [shape=ellipse label=\"{}\" fillcolor=\"{}\"];"
                            .format(
                                name,
                                label,
                                color,
                            )
                        )

                    # Output
                    name = "{}_{}".format(stage_type, key2str(key))
                    label = "out"
                    color = node_colors[node.net]

                    dot.append(
                        "      \"{}\" [shape=ellipse label=\"{}\" fillcolor=\"{}\"];"
                        .format(
                            name,
                            label,
                            color,
                        )
                    )

                    # Internal mux edges
                    for drv_key, pin in node.inp.items():
                        if node.sel == pin:
                            assert drv_key in nodes, drv_key
                            net = nodes[drv_key].net
                        else:
                            net = None

                        src_name = "{}_{}_{}".format(
                            stage_type, key2str(key), pin
                        )
                        dst_name = "{}_{}".format(stage_type, key2str(key))
                        color = edge_colors[net]

                        dot.append(
                            "      \"{}\" -> \"{}\" [color=\"{}\"];".format(
                                src_name,
                                dst_name,
                                color,
                            )
                        )

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
                        src_name = "{}_inp_{}".format(
                            stage_type, key2str(src_key)
                        )
                    else:
                        src_name = "{}_{}".format(stage_type, key2str(src_key))

                    color = node_colors[node.net]

                    dot.append(
                        "    \"{}\" -> \"{}\" [color=\"{}\"];".format(
                            src_name,
                            dst_name,
                            color,
                        )
                    )

                # Mux node
                elif node.type == self.NodeType.MUX:
                    for drv_key, pin in node.inp.items():
                        if node.sel == pin:
                            assert drv_key in nodes, drv_key
                            net = nodes[drv_key].net
                        else:
                            net = None

                        dst_name = "{}_{}_{}".format(
                            stage_type, key2str(key), pin
                        )
                        if isinstance(drv_key, str):
                            src_name = "{}_inp_{}".format(
                                stage_type, key2str(drv_key)
                            )
                        else:
                            src_name = "{}_{}".format(
                                stage_type, key2str(drv_key)
                            )

                        color = edge_colors[net]

                        dot.append(
                            "    \"{}\" -> \"{}\" [color=\"{}\"];".format(
                                src_name,
                                dst_name,
                                color,
                            )
                        )

                else:
                    assert False, node.type

            # Stage footer
            dot.append("  }")

        # Add footer
        dot.append("}")
        return "\n".join(dot)

# =============================================================================


#!/usr/bin/env python3
import logging

import pb_rr_graph as pb
from pb_type import PbType
from block_path import PathNode

import routing_mux as rrmux
from netlist import Cell

# =============================================================================


class NetPool():
    """
    Net pool. Generates net ids ensuring that they do not overlap with those
    given during its initialization. Does not encounter for later net deletion.
    """

    def __init__(self, nets=None):

        if nets is not None:
            self.used_nets = set(nets)
        else:
            self.used_nets = set()

        self.next_net_id = 0

    def get(self):

        # Generate a next unique ID
        self.next_net_id += 1
        while self.next_net_id in self.used_nets:
            self.next_net_id += 1

        # Add it to the set of used ones and return it
        self.used_nets.add(self.next_net_id)
        return self.next_net_id

# =============================================================================


class Edge(rrmux.Edge):
    """
    A wrapper class that gathers FASM metadata from a cluster edge
    """
    def __init__(self, edge):

        # Get FASM features
        features = set()
        if edge.metadata:
            features = set(edge.metadata)

        super().__init__(edge.src_id, edge.dst_id, features)


class ClusterDecoder:
    """
    Cluster internals decoder
    """

    def __init__(self, xml_pb_type):
        logging.info(" Initializing cluster decoder for '{}'".format(
            xml_pb_type.attrib["name"]
        ))

        # Build the pb_type hierarchy
        self.pb_type = PbType.from_etree(xml_pb_type)

        # Build the pb_type graph
        self.graph = pb.Graph.from_etree(xml_pb_type)

        # Prune nodes and edges
        self._prune_graph()

        # Build useful maps
        self._build_maps()

        # Identify routing muxes
        self._identify_muxes()

    def _prune_graph(self):

        # Prune nodes not related to the physical mode
        nodes = {}
        for node in self.graph.nodes.values():
            parts = [PathNode.from_string(p) for p in node.path.split(".")]

            # Keep top-level
            if len(parts) <= 2:
                nodes[node.id] = node
                continue

            # Must belong to the physical mode
            # FIXME: A physical mode need not to be named "physical" !
            modes = set([part.mode for part in parts])
            if "physical" in modes or modes == set([None, "default"]):
                nodes[node.id] = node
                continue

        # Prune edges not relevant to the physical mode
        edges = []
        for edge in self.graph.edges:
            if edge.src_id in nodes and edge.dst_id in nodes:
                edges.append(edge)

        self.graph.nodes = nodes
        self.graph.edges = edges

    def _build_maps(self):

        # Edges to and from nodes
        self.edges_to = {}
        self.edges_from = {}

        for i, edge in enumerate(self.graph.edges):

            if edge.src_id not in self.edges_from:
                self.edges_from[edge.src_id] = set()
            self.edges_from[edge.src_id].add(i)

            if edge.dst_id not in self.edges_to:
                self.edges_to[edge.dst_id] = set()
            self.edges_to[edge.dst_id].add(i)

        # Sort SOURCE and SINK nodes by cells
        self.nodes_by_cells = {}
        self.cells_by_nodes = {}
        for node in self.graph.nodes.values():

            # Only SOURCE/SINK
            if node.type not in [pb.NodeType.SOURCE, pb.NodeType.SINK]:
                continue

            # Skip top-level nodes
            path = node.path.split(".")
            if len(path) <= 2:
                continue

            # Get the cell path            
            path = ".".join(path[:-1])

            if path not in self.nodes_by_cells:
                self.nodes_by_cells[path] = []
            self.nodes_by_cells[path].append(node.id)

            self.cells_by_nodes[node.id] = path

#        # DEBUG #
#        logging.debug("  Nodes by cells:")
#        for key, ids in self.nodes_by_cells.items():
#            logging.debug("   {}".format(key))
#            for idx in ids:
#                node = self.graph.nodes[idx]
#                logging.debug("    {}".format(str(node)))
#        # DEBUG #

    def _identify_muxes(self):
        """
        Identify routing muxes in the pb_type graph.
        """

        self.muxes = []
        for node in self.graph.nodes.values():

            # Consider only SINK and PORT
            if node.type not in \
                [pb.NodeType.SINK, pb.NodeType.PORT]:
                continue

            # Get edges incoming to the node. There must be at least two.
            edge_ids = self.edges_to.get(node.id, set())
            if len(edge_ids) < 2:
                continue

            # Build a routing mux
            edges = [Edge(self.graph.edges[i]) for i in edge_ids]
            mux = rrmux.RoutingMux(edges)
            self.muxes.append(mux)

        logging.debug("  rr muxes: {}".format(len(self.muxes)))

    def _assign_nets(self, pin_map):
        """
        Assigns top-level nodes with nets according to the pin map
        """
        node_assignments = {}

        # Assign nodes with nets
        for node in self.graph.nodes.values():
            if node.type in [pb.NodeType.SOURCE, pb.NodeType.SINK]:
                path = [PathNode.from_string(p) for p in node.path.split(".")]

                # A top-level node
                if len(path) == 2:
                    net = pin_map.get(str(path[1]), None)
                    if net is not None:

                        assert node.id not in node_assignments, node
                        node_assignments[node.id] = net

        return node_assignments

    def _edge_key(self, edge_id):
        """
        Converts an edge id to edge key
        """
        edge = self.graph.edges[edge_id]
        return (edge.src_id, edge.dst_id)

    def _remove_net(self, net):
        """
        Removes a net
        """
        self.node_assignments = {k: v for k, v in \
                                 self.node_assignments.items() \
                                 if v != net}

    def _merge_nets(self, net_a, net_b):
        """
        Merges two nets preserving the id of one if it is in the frozen net
        list.
        """
        a_frozen = net_a in self.frozen_nets
        b_frozen = net_b in self.frozen_nets

        if not a_frozen and not b_frozen:
            old_id = net_b
            new_id = net_a

        elif a_frozen and not b_frozen:
            old_id = net_b
            new_id = net_a

        elif not a_frozen and b_frozen:
            old_id = net_a
            new_id = net_b

        else:
            assert False, (net_a, net_b)

        # Remap
        self.node_assignments = {k: new_id if v == old_id else v \
                                 for k, v in self.node_assignments.items()}


    def _expand_node(self, node_id):
        """
        Propagates a net from the given node. Returns a set of node ids that
        should be possibly expanded next
        """

        # Filter edges to and from
        edges_to = self.edges_to.get(node_id, set())
        edges_from = self.edges_from.get(node_id, set())

        edges_to = set([self._edge_key(e) for e in edges_to])
        edges_from = set([self._edge_key(e) for e in edges_from])

        edges_to -= self.inactive_edges
        edges_from -= self.inactive_edges

        # Expand incoming paths
        node_ids = set()
        node_net = self.node_assignments[node_id]

        for e, edges in enumerate((edges_to, edges_from)):
            for edge_key in edges:
                other_id = edge_key[e]

                # Same net
                other_net = self.node_assignments.get(other_id, None)
                if node_net == other_net:
                    continue

                # Free node, propagate
                if other_net is None:

                    # Do not propagate over top-level ports
                    other = self.graph.nodes[other_id]
                    if other.type in [pb.NodeType.SOURCE, pb.NodeType.SINK] \
                       and other.path.count(".") <= 1:
                        continue

                    self.node_assignments[other_id] = node_net
                    node_ids.add(other_id)
                    continue

                # Not a free node, stitch nets
                elif other_net is not None:
                    if edge_key in self.active_edges or len(edges) == 1:
                        self._merge_nets(node_net, other_net)
                    continue           

        return node_ids

    def _expand_nets(self):
        """
        Main net expansion loop.
        """

        # Initialize node queue
        node_queue = list(self.node_assignments.keys())

        # Propagate and stitch nets
        while len(node_queue):

            # Pop a node
            node_id = node_queue[0]
            node_queue = node_queue[1:]

            # Expand it
            node_ids = self._expand_node(node_id)
            node_queue.extend(node_ids)

    def _prune_nets(self):

        did_prune = False

        # Build net to nodes map
        nets_to_nodes = {}
        for node_id, net in self.node_assignments.items():

            if net not in nets_to_nodes:
                nets_to_nodes[net] = set()

            nets_to_nodes[net].add(node_id)

        # Early remove trivial unused nets with no sources and sinks
        for net, nodes in nets_to_nodes.items():

            # Gather node types
            srcs = [n for n in nodes if \
                    self.graph.nodes[n].type == pb.NodeType.SOURCE]

            snks = [n for n in nodes if \
                    self.graph.nodes[n].type == pb.NodeType.SINK]

            # Multi-driver net
            if len(srcs) > 1:
                logging.error("  Multi-driver net {}".format(net))

            # No sources
            if not srcs:
                self._remove_net(net)
                did_prune = True
                continue

            # No sinks
            if not snks:
                self._remove_net(net)
                did_prune = True
                continue

        return did_prune

    def _prune_blocks(self):

        did_prune = False

        for path, nodes in self.nodes_by_cells.items():

            # This block has only sources / sinks. Leave it.
            types = set([self.graph.nodes[n].type for n in nodes])
            if len(types) == 1:
                continue

            # Check if a block has active nodes
            nodes = set(nodes) & set(self.node_assignments.keys())
            if not nodes:
                continue

            # Both sources and sinks are active. Leave it
            types = set([self.graph.nodes[n].type for n in nodes])
            if len(types) > 1:
                continue

            # Prune the block
            for n in nodes:
                del self.node_assignments[n]
            did_prune = True

        return did_prune

    def _instantiate_cells(self, netlist, suffix=""):
        """
        Creates cell instances given net assignments to their nodes
        """
        count = 0

        for path, nodes in self.nodes_by_cells.items():

            # Check if a block has active nodes
            nodes = set(nodes) & set(self.node_assignments.keys())
            if not nodes:
                continue

            # Get pb_type
            pb_path = [PathNode.from_string(p) for p in path.split(".")]
            for part in pb_path:
                part.index = None
            pb_path = ".".join([str(p) for p in pb_path])

            pb_type = self.pb_type.find(pb_path)
            assert pb_type is not None, pb_path

            # Format cell type
            assert pb_type.blif_model is not None
            blif_model = pb_type.blif_model.split(maxsplit=1)[-1]
            assert not blif_model.startswith("."), blif_model

            # Format cell name
            parts = [PathNode.from_string(p) for p in path.split(".")]
            names = []

            for part in parts:
                piece = "{}{}".format(part.name, part.index)
                # FIXME: Assume that there is no mode overlap under the
                # physical one
                #if part.mode is not None and part.mode != "default":
                #    piece += "_{}".format(part.mode)
                names.append(piece)
            
            name = "_".join(names)

            # Suffix
            if suffix:
                name += "_" + suffix

            # Get port connections
            conn = {}
            for node_id in nodes:
                node = self.graph.nodes[node_id]
                port = node.path.rsplit(".", maxsplit=1)[1]
                port = PathNode.from_string(port)

                if port.name not in conn:
                    conn[port.name] = {}

                conn[port.name][port.index] = "_{}_".format(node.net)

            # Create the cell
            cell = Cell(blif_model, name)
            keys = sorted(pb_type.ports.keys())
            for port in [pb_type.ports[k] for k in keys]:
                for pin in range(port.width):

                    # Get port name
                    if port.width == 1:
                        pname = port.name
                    else:
                        pname = "{}[{}]".format(port.name, pin)

                    # Assign port connection
                    if port.name not in conn:
                        cell.ports[pname] = None
                    else:
                        cell.ports[pname] = conn[port.name].get(pin, None)

            # Add it
            netlist.add_cell(cell)
            count += 1

        return count
                

    def decode(self, nodes, fasm_features, netlist, net_pool, suffix=""):
        """
        Decodes
        """
        fasm_features = set(fasm_features)

#        logging.debug("  FASM feautres:")
#        for f in fasm_features:
#            logging.debug("   '{}'".format(f))

        # Convert node pin map
        pin_map = {k: v for k, v in nodes.values()}

        # Clear node nets
        for node in self.graph.nodes.values():
            node.net = None

        # Initialize node net assignments derived from routing
        self.node_assignments = self._assign_nets(pin_map)

        # Frozen net ids not to be merged into others
        self.frozen_nets = set(self.node_assignments.values())

        # Assign all other non top-level SOURCE and SINK nodes with new net ids
        for node in self.graph.nodes.values():

            # Not a SOURCE / SINK 
            if node.type not in [pb.NodeType.SOURCE, pb.NodeType.SINK]:
                continue

            # Not top-level
            if node.path.count(".") <= 1:
                continue

            # Already assigned
            if node.id in self.node_assignments:
                continue

            self.node_assignments[node.id] = net_pool.get()

        # Initialize edge states
        self.active_edges = set()
        self.inactive_edges = set()

        # Identify active and inactive edges
        for mux in self.muxes:

            active_nodes, active_edges, inactive_edges = \
                mux.get_active_nodes_and_edges(fasm_features)

            # Store active and inactive edges
            self.active_edges |= active_edges
            self.inactive_edges |= inactive_edges

        # Check for edge activity conflicts
        assert len(self.active_edges & self.inactive_edges) == 0

#        logging.debug("  active nodes:   {}".format(len(self.node_assignments)))
#        logging.debug("  active edges:   {}".format(len(self.active_edges)))
#        logging.debug("  inactive edges: {}".format(len(self.inactive_edges)))

        # Do the net expansion
        self._expand_nets()

        # Prune nets and blocks
        while True:

            pruned_nets = self._prune_nets()
            pruned_blocks = self._prune_blocks()

            if not pruned_nets and not pruned_blocks:
                break

        # Transfer net assignments to nodes
        for node_id, net_id in self.node_assignments.items():
            self.graph.nodes[node_id].net = net_id

#        # DEBUG #
#        logging.debug("  Node assignments:")
#        for node_id, net_id in self.node_assignments.items():
#            node = self.graph.nodes[node_id]
#            if node.type in [pb.NodeType.SOURCE, pb.NodeType.SINK]:
#                logging.debug("   {}, net_id={}".format(str(node), net_id))
#        # DEBUG #

        # Instantiate cells
        count = self._instantiate_cells(netlist, suffix)
        logging.debug("  cells   : {}".format(count))

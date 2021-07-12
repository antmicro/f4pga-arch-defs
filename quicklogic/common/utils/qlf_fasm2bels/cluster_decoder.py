#!/usr/bin/env python3
import logging

import pb_rr_graph as pb
from block_path import PathNode

import routing_mux as rrmux

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

        # Build the pb_type graph
        logging.info(" Initializing cluster decoder for '{}'".format(
            xml_pb_type.attrib["name"]
        ))
        self.graph = pb.Graph.from_etree(xml_pb_type)

        # Prune nodes and edges
        self._prune_graph()

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

        # DEBUG #
        logging.debug("  Nodes by cells:")
        for key, ids in self.nodes_by_cells.items():
            logging.debug("   {}".format(key))
            for idx in ids:
                node = self.graph.nodes[idx]
                logging.debug("    {}".format(str(node)))
        # DEBUG #

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

#    def _instantiate_cells(self):
#
#        # Group nodes by cells
#        nodes_by_cells = {}
#        for node in self.graph.nodes.values():
#
#            # Only assigned SOURCE/SINK
#            if node.net is None or \
#               node.type not in [pb.NodeType.SOURCE, pb.NodeType.SINK]:
#                continue
#
#            # Get the cell path
#            path = node.path.rsplit(".", maxsplit=1)[0]
#
#            if path not in nodes_by_cells:
#                nodes_by_cells[path] = []
#            nodes_by_cells[path].append(node.id)
#
#        # DEBUG
#        logging.debug("  Nodes by cells:")
#        for key, nodes in nodes_by_cells.items():
#            logging.debug("   {}:".format(key))
#            for node_id in nodes:
#                node = self.graph.nodes[node_id]
#                if node.port_type == pb.PortType.OUTPUT:
#                    logging.debug("    {}".format(node))

    def _edge_key(self, edge_id):
        """
        Converts an edge id to edge key
        """

        edge = self.graph.edges[edge_id]
        return (edge.src_id, edge.dst_id)

    def _remap_net(self, old_id, new_id):
        """
        Remaps a net in node net assignments
        """

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

        for edge_key in edges_to:
            src, dst = edge_key
            other_id = src

            # Same net
            other_net = self.node_assignments.get(other_id, None)
            if node_net == other_net:
                continue

            # Free node, propagate
            if other_net is None:
                self.node_assignments[other_id] = node_net
                node_ids.add(other_id)
                continue

            # Not a free node, stitch nets
            elif other_net is not None:
                if edge_key in self.active_edges or len(edges_to) == 1:
                    self._remap_net(other_net, node_net)
                continue           

        # Expand outgoin paths
        for edge_key in edges_from:
            src, dst = edge_key
            other_id = dst

            # Same net
            other_net = self.node_assignments.get(other_id, None)
            if node_net == other_net:
                continue

            # Free node, propagate
            if other_net is None:
                self.node_assignments[other_id] = node_net
                node_ids.add(other_id)
                continue

            # Not a free node, stitch nets
            elif other_net is not None:
                if edge_key in self.active_edges or len(edges_from) == 1:
                    self._remap_net(other_net, node_net)
                continue           

        return node_ids


    def decode(self, nodes, fasm_features, netlist):
        """
        Decodes
        """
        fasm_features = set(fasm_features)

        logging.debug("  FASM feautres:")
        for f in fasm_features:
            logging.debug("   '{}'".format(f))

        # Convert node pin map
        pin_map = {k: v for k, v in nodes.values()}

        # Clear node nets
        for node in self.graph.nodes.values():
            node.net = None

        # Initialize node net assignments derived from routing
        self.node_assignments = self._assign_nets(pin_map)

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

        logging.debug("  active nodes:   {}".format(len(self.node_assignments)))
        logging.debug("  active edges:   {}".format(len(self.active_edges)))
        logging.debug("  inactive edges: {}".format(len(self.inactive_edges)))

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

        # Transfer net assignments to nodes
        for node_id, net_id in self.node_assignments.items():
            self.graph.nodes[node_id].net = net_id

        logging.debug("  Node assignments:")
        for node_id, net_id in self.node_assignments.items():
            node = self.graph.nodes[node_id]
            if node.type in [pb.NodeType.SOURCE, pb.NodeType.SINK]:
                logging.debug("   {}, net_id={}".format(str(node), net_id))

        # Instantiate cells
        #self._instantiate_cells()

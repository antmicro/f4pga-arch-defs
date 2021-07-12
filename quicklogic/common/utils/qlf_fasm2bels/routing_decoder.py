#!/usr/bin/env python3
import re
import logging
from enum import Enum

import rr_graph.graph2 as rr

import routing_mux as rrmux

# =============================================================================


class Edge(rrmux.Edge):
    """
    A wrapper class that gathers FASM metadata from rr graph edge
    """
    def __init__(self, edge):

        # Get FASM features
        features = set()
        for meta, data in edge.metadata:
            if meta == "fasm_features":
                features = set(data.split("\n"))

        super().__init__(edge.src_node, edge.sink_node, features)


class RoutingDecoder():
    """
    Rounting decoder
    """

    def __init__(self, graph):
        self.graph = graph

        # Build maps
        self._build_maps()
        # Identify routing muxes
        self._identify_muxes()

    def _build_maps(self):
        """
        Builds lookup maps
        """
        logging.info(" Building maps...")

        # Base node and edge maps indexed by ids.
        # Edges do not have an id so assign them here,
        self.nodes = {node.id: node for node in self.graph.nodes}
        self.edges = {i: edge for i, edge in enumerate(list(self.graph.edges))}

        # Edges to and from nodes
        self.edges_to = {}
        self.edges_from = {}

        for edge_id, edge in self.edges.items():

            if edge.src_node not in self.edges_from:
                self.edges_from[edge.src_node] = set()
            self.edges_from[edge.src_node].add(edge_id)

            if edge.sink_node not in self.edges_to:
                self.edges_to[edge.sink_node] = set()
            self.edges_to[edge.sink_node].add(edge_id)

    def _identify_muxes(self):
        """
        Identify routing muxes in the graph.

        This works by finding IPIN/CHAN nodes with more than one incoming
        edges. However, this algorithm will fail if those edges are just
        intermediate ones and have no FASM features assigned.
        """

        logging.info(" Identifying routing muxes...")

        self.muxes = []
        for node in self.nodes.values():

            # Consider only CHAN and IPIN nodes
            if node.type not in \
                [rr.NodeType.CHANX, rr.NodeType.CHANY, rr.NodeType.IPIN]:
                continue

            # Get edges incoming to the node. There must be at least two.
            edge_ids = self.edges_to.get(node.id, set())
            if len(edge_ids) < 2:
                continue

            # Build a routing mux
            mux = rrmux.RoutingMux([Edge(self.edges[i]) for i in edge_ids])
            self.muxes.append(mux)

        logging.debug("  rr muxes: {}".format(len(self.muxes)))

    def _edge_key(self, edge_id):
        """
        Converts an edge id to edge key
        """

        edge = self.edges[edge_id]
        return (edge.src_node, edge.sink_node)

    def _remap_net(self, old_id, new_id):
        """
        Remaps a net in node net assignments
        """

        self.node_assignments = {k: new_id if v == old_id else v \
                                 for k, v in self.node_assignments.items()}

    def expand_node(self, node_id):
        """
        Propagates a net from the given node. Returns a set of node ids that
        should be possibly expanded next
        """

        # Filter edges to and from
        edges_to = self.edges_to.get(node_id, set())
        edges_from = self.edges_from.get(node_id, set())

        edges_to = set([self._edge_key(e) for e in edges_to])
        edges_from = set([self._edge_key(e) for e in edges_from])

#        logging.debug("Node {}".format(node_id))
#        logging.debug(" in:{}, out:{}".format(len(edges_to), len(edges_from)))

        edges_to -= self.inactive_edges
        edges_from -= self.inactive_edges

#        logging.debug(" in:{}, out:{}".format(len(edges_to), len(edges_from)))

        # Expand incoming paths
        node_ids = set()
        node_net = self.node_assignments[node_id]

        for edge_key in edges_to:
            src, dst = edge_key
            other_id = src

            # Skip SOURCE and SINK nodes
            if self.nodes[other_id].type in [rr.NodeType.SOURCE, rr.NodeType.SINK]:
                continue

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

            # Skip SOURCE and SINK nodes
            if self.nodes[other_id].type in [rr.NodeType.SOURCE, rr.NodeType.SINK]:
                continue

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

    def decode(self, fasm_features):
        """
        Decodes routing given an interable of set FASM feature names. Returns
        a dict with IPIN/OPIN node ids associating them with individual net
        ids. The net ids are somewhat random.
        """
        logging.info(" Decoding nets...")

        fasm_features = set(fasm_features)

        # Initialize node net assignments
        self.node_assignments = dict()

        # Initialize edge states
        self.active_edges = set()
        self.inactive_edges = set()

        # Initialize assignments
        for mux in self.muxes:

            active_nodes, active_edges, inactive_edges = \
                mux.get_active_nodes_and_edges(fasm_features)

            # Store active and inactive edges
            self.active_edges |= active_edges
            self.inactive_edges |= inactive_edges

            # Assign nets to nodes
            for node_id in active_nodes:
                if node_id not in self.node_assignments:
                    self.node_assignments[node_id] = \
                        len(self.node_assignments) + 1

        # Check for edge activity conflicts
        assert len(self.active_edges & self.inactive_edges) == 0

        logging.debug("  active nodes:   {}".format(len(self.node_assignments)))
        logging.debug("  active edges:   {}".format(len(self.active_edges)))
        logging.debug("  inactive edges: {}".format(len(self.inactive_edges)))

        # Initialize node queue
        node_queue = list(self.node_assignments.keys())

        # Propagate ans stitch nets
        while len(node_queue):

            # Pop a node
            node_id = node_queue[0]
            node_queue = node_queue[1:]

            # Expand it
            node_ids = self.expand_node(node_id)
            node_queue.extend(node_ids)

        # Build IPIN and OPIN to net id map
        pin_to_net = {}
        for node_id, net in self.node_assignments.items():
            node = self.nodes[node_id]
            if node.type in [rr.NodeType.IPIN, rr.NodeType.OPIN]:
                pin_to_net[node_id] = net

        # DEBUG #
        ipin_count = len([n for n in pin_to_net if self.nodes[n].type == rr.NodeType.IPIN])
        opin_count = len([n for n in pin_to_net if self.nodes[n].type == rr.NodeType.OPIN])

        locs = set([(self.nodes[n].loc.x_low, self.nodes[n].loc.y_low) for n in pin_to_net])
        ipin_locs = set([(self.nodes[n].loc.x_low, self.nodes[n].loc.y_low) for n in pin_to_net if self.nodes[n].type == rr.NodeType.IPIN])
        opin_locs = set([(self.nodes[n].loc.x_low, self.nodes[n].loc.y_low) for n in pin_to_net if self.nodes[n].type == rr.NodeType.OPIN])

        logging.debug("  nets     : ({}) {}".format(len(set(self.node_assignments.values())), set(self.node_assignments.values())))
        logging.debug("  IPIN     : {}".format(ipin_count))
        logging.debug("  OPIN     : {}".format(opin_count))
        logging.debug("  all locs : {}".format(len(locs)))
        logging.debug("  IPIN locs: {}".format(len(ipin_locs)))
        logging.debug("  OPIN locs: {}".format(len(opin_locs)))
        # DEBUG #

        return pin_to_net

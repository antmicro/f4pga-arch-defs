#!/usr/bin/env python3
import re
import logging

# =============================================================================


class Edge():
    """
    A generic routing mux edge with FASM annotation
    """
    def __init__(self, src, dst, features=None):
        self.src = src
        self.dst = dst

        if features is not None:
            self.features = set(features)
        else:
            self.features = set()


class RoutingMux():
    """
    A routing mux inferred directly from a graph. Consists of a set of edges
    that converge in a single node
    """

    FEATURE_RE = re.compile(r"(?P<feature>\S+)\[(?P<bit>[0-9]+)\]")

    def __init__(self, edges):

        self.edges = edges

        # Sanity check edges
        sinks = set([e.dst for e in self.edges])
        assert len(sinks) == 1

        # All mux features
        self.features = set()
        for edge in self.edges:
            self.features |= edge.features

        # Check if all features are consistent. They should differ only in the
        # index of the last part
        features = set()
        for feature in self.features:
            match = RoutingMux.FEATURE_RE.fullmatch(feature)
            assert match is not None, feature
            features.add(match.group("feature"))

        if not features:
            logging.critical("ERROR: A routing mux has no FASM features")
            raise RuntimeError

        if len(features) > 1:
            logging.critical(
                "ERROR: Got a routing mux with inconsistent FASM features:"
            )
            for feature in features:
                logging.critical(" '{}'".format(feature))
            raise RuntimeError

    def get_active_nodes_and_edges(self, fasm_features):
        """
        Returns IDs of active node ids, active edges and inactive edges as
        (src, dst) pairs given the set of active canonical FASM features
        """

        width = len(self.edges)

        active_nodes = set()
        active_edges = set()
        inactive_edges = set()

        # Count edges with no features (there can be only one)
        num_no_feature_edges = len([e for e in self.edges if not e.features])
        assert num_no_feature_edges <= 1

        # Pre-filter features
        features = fasm_features & self.features

        # No features and we have at least one edge without features. Make
        # edges with no features active and the others inactive
        if not features and num_no_feature_edges:
            for edge in self.edges:
                edge_key = (edge.src, edge.dst)
                if not edge.features:
                    active_edges.add(edge_key)
                    active_nodes.add(edge.src)
                    active_nodes.add(edge.dst)
                else:
                    inactive_edges.add(edge_key)

        # No features, mark all edges as inactive
        elif not features:
            for edge in self.edges:
                edge_key = (edge.src, edge.dst)
                inactive_edges.add(edge_key)
                
        # Perform FASM feature matching
        else:
            for edge in self.edges:
                edge_key = (edge.src, edge.dst)
                if edge.features:
                    if features == edge.features:
                        active_edges.add(edge_key)
                        active_nodes.add(edge.src)
                        active_nodes.add(edge.dst)
                    else:
                        inactive_edges.add(edge_key)
                else:
                    inactive_edges.add(edge_key)

        return active_nodes, active_edges, inactive_edges


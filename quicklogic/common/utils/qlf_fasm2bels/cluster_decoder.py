#!/usr/bin/env python3
import logging

import pb_rr_graph as pb
from block_path import PathNode

# =============================================================================

class ClusterDecoder:

    def __init__(self, xml_arch, graph, netlist):
        self.xml_arch = xml_arch
        self.graph = graph
        self.netlist = netlist

        self.xml_cplx = xml_arch.find("complexblocklist")
        assert self.xml_cplx is not None

    def decode(self, nodes, pb_type_name, fasm_features):

        # Convert node pin map
        pin_map = {k: v for k, v in nodes.values()}

        # Get the pb_type XML definition
        for xml_item in self.xml_cplx.findall("pb_type"):
            if xml_item.attrib["name"] == pb_type_name:
                xml_pb_type = xml_item
                break
        else:
            assert False, pb_type_name

        # Build pb_type graph
        graph = pb.Graph.from_etree(xml_pb_type)

        # Assign top-level nodes with nets
        all_nets = set(pin_map.values())
        for node in graph.nodes.values():
            if node.type in [pb.NodeType.SOURCE, pb.NodeType.SINK]:
                path = [PathNode.from_string(p) for p in node.path.split(".")]
                if len(path) == 2 and path[0].name == pb_type_name:
                    net = pin_map.get(str(path[1]), None)
                    if net is not None:
                        node.net = net
                        logging.debug("  {} <- {}".format(node.path, net))

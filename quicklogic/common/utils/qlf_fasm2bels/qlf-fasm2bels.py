#!/usr/bin/env python3
import argparse
import os
import logging
import re

import capnp
import capnp.lib.capnp
capnp.remove_import_hook()

import lxml.etree as ET

import rr_graph.graph2 as rr
import rr_graph.xml.graph2 as rr_xml
import rr_graph.capnp.graph2 as rr_capnp
from rr_graph.utils import progressbar_utils as pbar

import fasm

from tile_grid import Grid as TileGrid
from routing_decoder import RoutingDecoder
from cluster_decoder import ClusterDecoder
from netlist import Cell, Netlist

# =============================================================================


def build_pin_name_map(graph):
    """
    Builds a map of IPIN/OPIN node ids to pin names
    """

    pin_map = {}
    for node in graph.nodes:

        # Consider only IPIN/OPIN
        if node.type not in [rr.NodeType.IPIN, rr.NodeType.OPIN]:
            continue

        loc = (node.loc.x_low, node.loc.y_low)
        ptc = node.loc.ptc
        blk_id = graph.loc_map[loc].block_type_id

        pin_name = graph.pin_ptc_to_name_map[(blk_id, ptc)]
        pin_map[node.id] = pin_name

    return pin_map


def group_by_clusters(pin_nodes, graph, pin_names):
    """
    Groups nodes by clusters. Returns a dict indexed by grid locations as
    (x, y, z) of dicts containing cluster block (tile) type "type" and yet
    another dict which maps IPIN/OPIN node IDs to tile pin names.
    """

    INDEX_RE = re.compile(r"(?P<name>\S+)\[(?P<index>[0-9]+)\]")

    clusters = {}
    for node_id, net in pin_nodes.items():
        node = graph.nodes[node_id]
        pin_spec = pin_names[node_id]

        # Get block type and pin name
        block_name, pin_name = pin_spec.split(".", maxsplit=1)

        # Get sub-tile index if applicable
        match = INDEX_RE.fullmatch(block_name)
        if match is not None:
            block_name = match.group("name")
            z = int(match.group("index"))

        # No index, assume Z=0
        else:
            z = 0

        loc = (node.loc.x_low, node.loc.y_low, z)
        if loc not in clusters:
            clusters[loc] = {
                "type": block_name,
                "nodes": {},
            }

        clusters[loc]["nodes"][node_id] = (pin_name, net)

    return clusters

# =============================================================================


def report_routed_nets(file_name, pin_nodes, graph):
    """
    Prepares and writes routed net report for debugging / verification against
    VPR
    """

    # Group IPIN and OPIN nodes by nets
    nets = [] 
    for net in set(pin_nodes.values()):
        nodes = [k for k, v in pin_nodes.items() if v == net]
        ipins = [n for n in nodes if graph.nodes[n].type == rr.NodeType.IPIN]
        opins = [n for n in nodes if graph.nodes[n].type == rr.NodeType.OPIN]

        nets.append({
            "name": net,
            "opins": opins,
            "ipins": ipins,
        })

    # Write the report. Sort data for it to be repetable
    nets = sorted(nets, key=lambda n: sorted(n["opins"])[0])
    with open(file_name, "w") as fp:
        for net in nets:
            for node_id in sorted(net["opins"]):
                node = graph.nodes[node_id]
                fp.write("OPIN {} ({},{})\n".format(
                    node_id,
                    node.loc.x_low,
                    node.loc.y_low
                ))
            for node_id in sorted(net["ipins"]):
                node = graph.nodes[node_id]
                fp.write(" IPIN {} ({},{})\n".format(
                    node_id,
                    node.loc.x_low,
                    node.loc.y_low
                ))
            fp.write("\n")

# =============================================================================


def main():

    # Parse arguments
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--fasm",
        required=True,
        type=str,
        help="Input design FASM file"
    )
    parser.add_argument(
        "--arch",
        required=True,
        type=str,
        help="VPR arch XML"
    )
    parser.add_argument(
        "--rr-graph",
        required=True,
        type=str,
        help="VPR RR graph XML / binary"
    )
    parser.add_argument(
        "--capnp-schema",
        default=None,
        type=str,
        help="Path to rr graph cap'n'proto schema (for binary rr graph)"
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="WARNING",
        help="Log level (def. \"WARNING\")"
    )

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, args.log_level.upper()),
    )

    # Verify the rr graph extension
    rr_graph_ext = os.path.splitext(args.rr_graph)[1].lower()

    if rr_graph_ext == ".xml":
        pass

    elif rr_graph_ext == ".bin":

        # Check if we have Cap'n'proto schema provided
        if args.capnp_schema is None:
            logging.critical(
                "ERROR: Binary rr graph reading requires Cap'n'proto schema")
            exit(-1)

    else:
        logging.critical(
            "ERROR: Unsupported rr graph extension '{}'".format(rr_graph_ext))
        exit(-1)

    # Load and parse FASM
    logging.info("Loading FASM file...")
    fasm_lines = fasm.parse_fasm_filename(args.fasm)

    # Build a set of canonical features
    fasm_features = set()
    for fasm_line in fasm_lines:

        set_feature = fasm_line.set_feature
        if set_feature is None:
            continue

        for one_feature in fasm.canonical_features(set_feature):
            assert one_feature.value == 1, one_feature
            assert one_feature.end is None, one_feature

            bit = one_feature.start
            if bit is None:
                bit = 0

            feature = "{}[{}]".format(one_feature.feature, bit)
            fasm_features.add(feature)

    # Read the architecture
    logging.info("Loading architecture...")
    xml_tree = ET.parse(args.arch,
        ET.XMLParser(remove_blank_text=True, remove_comments=True)
    )
    xml_arch = xml_tree.getroot()
    assert xml_arch is not None and xml_arch.tag == "architecture"

    # Build tile grid
    tile_grid = TileGrid(xml_arch)

    # Read the rr graph
    logging.info("Loading rr graph...")
    if rr_graph_ext == ".xml":
        graph_io = rr_xml.Graph(
            input_file_name=args.rr_graph,
            output_file_name=None,
            rebase_nodes=False,
            filter_nodes=False,
            load_edges=True,
            build_pin_edges=False,
            progressbar=pbar.progressbar
        )

    elif rr_graph_ext == ".bin":
        graph_io = rr_capnp.Graph(
            rr_graph_schema_fname=args.capnp_schema,
            input_file_name=args.rr_graph,
            output_file_name=None,
            rebase_nodes=False,
            filter_nodes=False,
            load_edges=True,
            build_pin_edges=False,
            progressbar=pbar.progressbar
        )

    else:
        assert False, rr_graph_ext

    graph = graph_io.graph

    logging.debug(" rr nodes: {}".format(len(graph.nodes)))
    logging.debug(" rr edges: {}".format(len(graph.edges)))

    # Build pin name map
    pin_names = build_pin_name_map(graph)

    # Decode net routes between clusters
    logging.info("Decoding routing...")
    r_decoder = RoutingDecoder(graph)
    pin_nodes = r_decoder.decode(fasm_features)

    # Check for multi-source nets and undriven nets
    for net in set(pin_nodes.values()):

        nodes = [k for k, v in pin_nodes.items() if v == net]
        ipins = [n for n in nodes if graph.nodes[n].type == rr.NodeType.IPIN]
        opins = [n for n in nodes if graph.nodes[n].type == rr.NodeType.OPIN]

        if len(opins) > 1:
            logging.error(" Multi-driver net {}".fornat(net))
            for node_id in opins:
                loc = (graph.nodes[node_id].loc.x_low, graph.nodes[node_id].loc.y_low)
                logging.error("  OPIN {} {} '{}'".format(node_id, loc, pin_map[node_id]))

        if len(opins) == 0:
            logging.warning(" Undriven net {}".format(net))
            for node_id in ipins:
                loc = (graph.nodes[node_id].loc.x_low, graph.nodes[node_id].loc.y_low)
                logging.warning("  IPIN {} {} '{}'".format(node_id, loc, pin_map[node_id]))

        if len(ipins) == 0:
            logging.warning(" Net with no sink(s) {}".format(net))
            for node_id in opins:
                loc = (graph.nodes[node_id].loc.x_low, graph.nodes[node_id].loc.y_low)
                logging.warning("  OPIN {} {} '{}'".format(node_id, loc, pin_map[node_id]))

    # Group nets by clusters
    cluster_nodes = group_by_clusters(pin_nodes, graph, pin_names)

#    # TEST - make netlist with clusters
#    netlist = Netlist()
#    for loc, cluster in cluster_nodes.items():
#        name = cluster["type"].upper() + "_X{}Y{}Z{}".format(*loc)
#        cell = Cell(cluster["type"], name)
#        cell.attributes["LOC"] = "X{}Y{}Z{}".format(*loc)
#        for node_id, pin_name in cluster["nodes"].items():
#            cell.ports[pin_name] = "net_{}".format(pin_nodes[node_id])
#        netlist.add_cell(cell)      
#    netlist.write_verilog("clusters.v")

    # Decode clusters
    logging.info("Decoding clusters...")
    netlist = Netlist()
    c_decoder = ClusterDecoder(xml_arch, graph, netlist)
    for cluster_loc, cluster_info in cluster_nodes.items():

        logging.info(" {} at {}".format(cluster_info["type"], cluster_loc))

        # Get pb_type name and FASM prefix
        assert cluster_loc in tile_grid.tiles, cluster_loc
        tile = tile_grid.tiles[cluster_loc]

        # The type must match
        assert tile.type == cluster_info["type"], \
            (tile.type == cluster_info["type"])

        logging.debug("  pb_type : {}".format(tile.pb_type))
        logging.debug("  fasm pfx: {}".format(tile.fasm_prefix))

        # Get FASM features for this prefix, remove the prefix
        clb_features = set()
        for feature in fasm_features:
            if feature.startswith(tile.fasm_prefix):
                clb_features.add(feature.replace(tile.fasm_prefix + ".", ""))

        logging.debug("  {} features".format(len(clb_features)))
#        for f in clb_features:
#            logging.debug("   {}".format(f))

        # FIXME: Skip IOs for now
        if cluster_info["type"] != "clb":
            continue

        # Decode the CLB
        c_decoder.decode(cluster_info["nodes"], tile.pb_type, clb_features)

        break        
    
    netlist.write_verilog("netlist.v")

# =============================================================================


if __name__ == "__main__":
    main()


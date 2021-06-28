#!/usr/bin/env python3
import argparse
import os
import logging

import capnp
import capnp.lib.capnp
capnp.remove_import_hook()

import rr_graph.graph2 as rr
import rr_graph.xml.graph2 as rr_xml
import rr_graph.capnp.graph2 as rr_capnp
from rr_graph.utils import progressbar_utils as pbar

import fasm

from routing_decoder import RoutingDecoder

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

    logging.debug("rr nodes: {}".format(len(graph.nodes)))
    logging.debug("rr edges: {}".format(len(graph.edges)))

    # Initialize routing decoder
    r_decoder = RoutingDecoder(graph)
    r_decoder.decode(fasm_features)

# =============================================================================


if __name__ == "__main__":
    main()


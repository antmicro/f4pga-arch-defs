#!/usr/bin/env python3
"""
Identifies and renames top-level ports of a post-pnr netlist from VPR. Tries to
restore their original names so that the netlist can be compared to the pre-pnr
one.

Since post pnr ports are individual bits square brackets '[]' in their names
are replaced with round brackets '()'. This avoids confusion between individual
nets and vector bit indices.
"""

import argparse
import json
import re

# =============================================================================


VPR_PORT_RE = re.compile(r"^io_(out:)?(?P<name>.*)(_input_|_output_)")
VPR_UNCONN_RE = re.compile(r"^__vpr__unconn[0-9]+")
#PORT_IDX_RE = re.compile(r"^(?P<name>[^\[\]]+)(\[(?P<index>[0-9]+)\])?")

def main():

    # Parse arguments
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "json",
        type=str,
        help="JSON file with the design to process"
    )

    args = parser.parse_args()

    # Load the JSON file
    with open(args.json, "r") as fp:
        json_root = json.load(fp)

    # Find the top-level module
    top_name = None
    for mod_name, mod_data in json_root["modules"].items():

        for attr_name, attr_value in mod_data["attributes"].items():
            if attr_name == "top" and int(attr_value) != 0:
                top_name = mod_name
                break

        if top_name is not None:
            break

    module = json_root["modules"][top_name]
    print("Top-level module: '{}'".format(top_name))

    # Find top-level ports to rename
    ports_to_rename = set()
    for port_name, port_data in module["ports"].items():

        # Match the VPR name
        match = VPR_PORT_RE.match(port_name)
        if match is not None:

            # Get original port name
            org_name = match.group("name")

            # Replace '[]' brackets with '()' brackets as the port is an
            # individual net rather than a vector.
            org_name = org_name.replace("[", "(").replace("]", ")")

            # Store the correspondence
            ports_to_rename.add((port_name, org_name))

        # Check if this port is unconnected. If so then mark it for removal
        match = VPR_UNCONN_RE.match(port_name)
        if match is not None:
            ports_to_rename.add((port_name, None))

    # Rename ports, remove explicit unconnected ports
    for old_name, new_name in ports_to_rename:
        port = module["ports"][old_name]
        del module["ports"][old_name]

        if new_name is None:
            print(" removed port '{}'".format(old_name))
        else:
            module["ports"][new_name] = port
            print(" renamed port '{}' -> '{}'".format(old_name, new_name))

    # Rename nets, remove explicit unconnected ports
    for old_name, new_name in ports_to_rename:
        net = module["netnames"][old_name]
        del module["netnames"][old_name]

        if new_name is None:
            print(" removed net '{}'".format(old_name))
        else:
            module["netnames"][new_name] = net
            print(" renamed net '{}' -> '{}'".format(old_name, new_name))

    # Write the JSON file
    with open(args.json, "w") as fp:
        json.dump(json_root, fp, indent=2)


if __name__ == "__main__":
    main()

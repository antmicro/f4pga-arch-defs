#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 The SymbiFlow Authors.
#
# Use of this source code is governed by a ISC-style
# license that can be found in the LICENSE file or at
# https://opensource.org/licenses/ISC
#
# SPDX-License-Identifier: ISC
"""
This is an utility script that performs cell instance renaming in a design in
Yosys JSON format. Cell instance names containing dots are altered so that
all dots are replaced with underscores.
"""

import argparse
import json

# =============================================================================


def fixup_cell_names(design):
    """
    Scans Yosys' JSON data structure and replaces cell instance names that
    contains dots in names with other character.
    """

    # Process modules
    modules = design["modules"]
    for mod_name, mod_data in modules.items():
        print(mod_name)

        # Process cells
        cells = mod_data["cells"]
        for cell_name in list(cells.keys()):

            # Fixup name
            if "." in cell_name:
                new_name = cell_name.replace(".", "_")
                assert new_name not in cells, new_name

                cells[new_name] = cells[cell_name]
                del cells[cell_name]

    return design


# =============================================================================


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("i", type=str, help="Yosys JSON in")
    parser.add_argument("o", type=str, help="Yosys JSON out")

    args = parser.parse_args()

    # Load JSON
    with open(args.i, "r") as fp:
        design = json.load(fp)

    # Fixup names
    design = fixup_cell_names(design)

    # Write JSON
    with open(args.o, "w") as fp:
        json.dump(design, fp, indent=2)


if __name__ == "__main__":
    main()

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
This script parses and then compares contents of two PCF files. If the
constraints are identical exits with code 0. Otherwise prints parsed content
of both files and exits with -1. It is used to verify whether
design constraints were correctly applied during the toolchain flow.
fasm2bels for QuickLogic PP3 architecture can write PCF with actual
IO locations as encoded in the bitstream. This is verified against
the original PCF from the design.
"""
import argparse

from lib.parse_pcf import parse_simple_pcf


def main():
    parser = argparse.ArgumentParser(
        description="Compares IO constraints across two PCF files"
    )
    parser.add_argument("pcf", nargs=2, type=str, help="PCF files")
    args = parser.parse_args()

    # Read constraints, convert them to tuples for easy comparison
    pcf = []
    for i in [0, 1]:
        with open(args.pcf[i], "r") as fp:
            constrs = set()
            for constr in parse_simple_pcf(fp):
                key = tuple(
                    [
                        type(constr).__name__, constr.net,
                        None if not hasattr(constr, "pad") else constr.pad
                    ]
                )
                constrs.add(key)
            pcf.append(constrs)

    # We have a match
    if pcf[0] == pcf[1]:
        exit(0)

    # Print difference
    print("PCF constraints mismatch!")
    for i in [0, 1]:
        print("'{}'".format(args.pcf[i]))
        for key in sorted(pcf[i]):
            print("", key)

    exit(-1)


if __name__ == "__main__":
    main()

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

import re

USAGE_PATTERN = re.compile(
    r'^Netlist\s(?P<type>[A-Za-z0-9_-]+)\sblocks:\s(?P<count>[0-9]+)'
)


def parse_usage(pack_log):
    """ Yield (block, count) from pack_log file.

    Args:
        pack_log (str): Path pack.log file generated from VPR.

    Yields:
        (block, count): Tuple of block name and count of block type.

    """
    with open(pack_log) as f:
        for line in f:
            m = re.match(USAGE_PATTERN, line.strip())
            if m:
                yield (m.group("type"), int(m.group("count")))

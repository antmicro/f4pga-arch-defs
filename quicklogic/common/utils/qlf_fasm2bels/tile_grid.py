#!/usr/bin/env python3
import logging

import lxml.etree as ET

# =============================================================================


class Tile:
    """
    A tile with FASM prefix
    """
    def __init__(self, type, pb_type, fasm_prefix):
        self.type = type
        self.pb_type = pb_type
        self.fasm_prefix = fasm_prefix


class Grid:
    """
    Tile grid. Contains a dict of tiles with FASM prefixes indexed by their
    X, Y, Z locations.
    """

    def __init__(self, xml_root):
        self.site_types = {}
        self.tiles = {}

        self._load_tiles(xml_root)
        self._load_layout(xml_root)

    def _load_tiles(self, xml_root):

        # Get the tiles section
        xml_tiles = xml_root.find("tiles")
        assert xml_tiles is not None

        # Load tiles
        for xml_tile in xml_tiles.findall("tile"):
            type = xml_tile.attrib["name"]

            # Load sub tiles and pb_type names
            z = 0
            for xml_sub_tile in xml_tile.findall("sub_tile"):
                capacity = int(xml_sub_tile.attrib.get("capacity", "1"))

                xml_equiv = xml_sub_tile.find("equivalent_sites")
                assert xml_equiv is not None

                xml_sites = xml_equiv.findall("site")
                if len(xml_sites) > 1:
                    logging.critical("Multiple equivalent sites per sub-tile not supported")

                # FIXME: This assumes 1-to-1 pin map between the tile and the
                # pb_type
                pb_type = xml_sites[0].attrib["pb_type"]

                # Add site types
                for i in range(capacity):
                    self.site_types[(type, z)] = pb_type
                    z = z + 1

    def _load_layout(self, xml_root):

        # Get the layout section
        xml_layout = xml_root.find("layout")
        assert xml_layout is not None

        # Get the fixed layout
        # TODO: Support multiple fixed layouts
        xml_fixed = xml_layout.find("fixed")
        assert xml_layout is not None

        # Get tiles
        self.tiles = {}
        for xml_single in xml_layout.findall("single"):

            # Must have metadata
            xml_metadata = xml_single.find("metadata")
            if not xml_metadata:
                continue

            # Find meta with name="fasm_prefix"
            for xml_item in xml_metadata.findall("meta"):
                if xml_item.tag == "meta" and xml_item.attrib["name"] == "fasm_prefix":
                    xml_meta = xml_item
                    break
            else:
                continue

            type = xml_layout.attrib["type"]
            x = int(xml_layout.attrib["x"])
            y = int(xml_layout.attrib["y"])

            # Split prefixes for sub-tiles
            prefixes = xml_meta.text.strip().split()

            # Add tiles
            for z, prefix in enumerate(prefixes):

                key = (type, z)
                assert key in self.site_types, key
                pb_type = self.site_types[key]

                loc = (x, y, z)
                assert loc not in self.tiles, loc
                self.tiles[loc] = Tile(type, pb_type, prefix)

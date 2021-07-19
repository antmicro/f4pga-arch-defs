#!/usr/bin/env python3

# =============================================================================

class Placement:
    """
    A class for representing VPR cluster placement
    """

    def __init__(self):
        self.cluster_to_loc = {}
        self.loc_to_cluster = {}

    @staticmethod
    def from_file(fp):

        # Read lines
        lines = fp.readlines()

        # Parse
        placement = Placement()
        for line in lines:
            line = line.strip()

            # Discard comment
            pos = line.find("#")
            if pos != -1:
                line = line[:pos]

            # Discard empty line
            line = line.strip()
            if not line:
                continue

            # Skip header lines
            if line.startswith("Netlist_File:"):
                continue
            if line.startswith("Array size:"):
                continue

            # Consider only 4 column lines
            fields = line.split()
            if len(fields) != 4:
                continue

            # Get data
            cluster = fields[0]
            loc = (int(fields[1]), int(fields[2]), int(fields[3]))

            placement.cluster_to_loc[cluster] = loc
            placement.loc_to_cluster[loc] = cluster

        return placement

    def get_cluster_at(self, loc):
        return self.loc_to_cluster.get(loc, None)

    def get_loc_of_cluster(self, cluster):
        return self.cluster_to_loc(cluster, None)

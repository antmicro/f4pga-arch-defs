#!/usr/bin/env python3
"""
This script provides a temporary solution for direct connections
between a non-buf primitive and IPADs/OPADs.

The script loads the design from a JSON file generated by Yosys. Then it
removes automatically generated IBUFs/OBUFs and makes direct connection
between a primitive and constrained signals.

The JSON design format used by Yosys is documented there:
- http://www.clifford.at/yosys/cmd_write_json.html
- http://www.clifford.at/yosys/cmd_read_json.html

"""
import argparse
import sys
import simplejson as json

# =============================================================================


class IOBufDeleter():
    def __find_top_module(self, design):
        """
        Looks for the top-level module in the design. Returns its name. Throws
        an exception if none was found.
        """

        for name, module in design["modules"].items():
            attrs = module["attributes"]
            if "top" in attrs and int(attrs["top"]) == 1:
                return name

        raise RuntimeError("No top-level module found in the design!")

    def __init__(self, design, primitives):
        self.design = design
        self.primitives = primitives
        self.top_name = self.__find_top_module(design)
        self.module = design["modules"][self.top_name]

    def __delete_buffers(self, ports_connections, prim_connections):
        """
        Delete Buffers for every 'cells' and 'netnames' entry that uses
        a constrained port which is connected to the primitive.
        """
        cells = self.module["cells"]
        netnames = self.module["netnames"]

        connected_ports = list()
        for port, (port_bits, top_io_bits) in ports_connections.items():
            for cell, connections in prim_connections.items():
                for cell_port, cell_bits in connections.items():
                    if port_bits == cell_bits:
                        connected_ports.append(port)

                        # Connect the cell's ports to the top level I/Os
                        connections = cells[cell]["connections"]
                        connections[cell_port] = top_io_bits

        for port in connected_ports:
            for cell_name, cfgs in cells.items():
                if "iopadmap" in cell_name and port in cell_name:
                    del cells[cell_name]
                    break

            for net_name, config in netnames.items():
                if "iopadmap" in net_name and port in net_name:
                    del netnames[net_name]
                    break

    def __get_primitive_connections(self, primitive):
        """
        Get all 'bits' from 'connections' section for a given primitive
        to be later used to find out which of primitive ports have
        direct IO connection.
        """

        conns = dict()

        for cell, data in self.module["cells"].items():
            if data["type"] != primitive:
                continue

            conns[cell] = data["connections"]

        return conns

    def __get_ports_connections(self):
        """
        Get all constrained ports with their corresponding 'bits'.
        """
        ports = dict()

        for port, cfg in self.module["ports"].items():
            ports[port] = cfg["bits"]

        ports_connections = dict()

        for port, top_bits in ports.items():
            for net_name, cfg in self.module["netnames"].items():
                if "iopadmap" in net_name and port in net_name:
                    ports_connections[port] = (cfg["bits"], top_bits)
                    break

        return ports_connections

    def __find_and_remove_bufs(self, primitive):
        """
        Gather ports and primitive connections and run IO BUFs
        removal.
        """
        ports_connections = self.__get_ports_connections()
        prim_connections = self.__get_primitive_connections(primitive)
        if prim_connections is not None:
            self.__delete_buffers(ports_connections, prim_connections)

    def process_direct_ios(self):
        """
        Find and remove if possible IO BUFs for each primitive.
        """
        for prim in self.primitives:
            self.__find_and_remove_bufs(prim)

        return self.design


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-p",
        default=None,
        type=str,
        help="Comma separated list of primitives which \
                              have direct IO connection and do not require \
                              IBUF/OBUF"
    )

    args = parser.parse_args()
    design = json.load(sys.stdin)

    if args.p:
        primitives = args.p.split(',')
        deleter = IOBufDeleter(design, primitives)
        design = deleter.process_direct_ios()

    json.dump(design, sys.stdout, indent=2)


if __name__ == "__main__":
    main()

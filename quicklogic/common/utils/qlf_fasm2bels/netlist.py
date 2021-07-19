#!/usr/bin/env python3

# =============================================================================

class Cell:
    """
    A generic blackbox netlist cell with attributes and parameters
    """

    def __init__(self, type, name=None):

        # Cell type (model)
        self.type = type

        # Cell instance name
        self.name = name

        # Ports and connections. Indexed by port specificatons
        # (as <port>[<bit>]), contains net names.
        self.ports = {}

        self.attributes = {}  # name: value, strings
        self.parameters = {}  # name: value, strings


class Netlist:
    """
    Nelist
    """

    def __init__(self):

        # Top-level inputs, outputs and inouts
        self.ports = {
            "input": set(),
            "output": set(),
            "inout": set(),
        }

        # Cells indexed by names.
        self.cells = {}

    def add_cell(self, cell):
        """
        Adds a cell ensuring that there is no name duplicate
        """
        assert cell.name not in self.cells, cell.name
        self.cells[cell.name] = cell

    def all_nets(self):
        """
        Returns the set of all nets
        """
        nets = set()

        # Collect all nets
        for cell in self.cells.values():
            for net in cell.ports.values():
                if net is not None:
                    nets.add(net)

        for type, ports in self.ports.items():
            for port in ports:
                nets.add(port)

        return nets

    def remap_nets(self, net_map):
        """
        Remaps net names according to the given map
        """
        for cell in self.cells.values():
            for port, net in cell.ports.items():
                cell.ports[port] = net_map.get(net, net)

        for type, ports in self.ports.items():
            self.ports[type] = set([net_map.get(net, net) for net in ports])

    @staticmethod
    def escape(s):

        if set(s) & {'[', ']', '(', ')'}:
            return "\\" + s
        return s

    @staticmethod
    def net2str(net):

        if net is None:
            return ""
        elif isinstance(net, int):
            return "_" + str(net) + "_"
        elif isinstance(net, str):
            return net

        assert False, net

    def write_verilog(self, file_name):

        lines = []
        lines.append("module top (")

        # Top-level ports
        for type, ports in self.ports.items():
            for port in ports:
                port = self.escape(self.net2str(port))
                lines.append("  {} {} ,".format(type, port))

        lines[-1] = lines[-1].replace(",", "")
        lines.append(");")

        # Nets (wires)
        for net in self.all_nets():
            net = self.escape(self.net2str(net))
            lines.append("  wire {} ;".format(net))
        lines.append("")

        # Cell instances
        for cell in self.cells.values():

            # Attributes
            for name, value in cell.attributes.items():
                if isinstance(value, str):
                    value = "\"" + value + "\""
                lines.append("  (* {} = {} *)".format(name, value))

            # Instance + parameters
            if cell.parameters:
                lines.append("  {} # (".format(cell.type))
                for name, value in cell.parameters.items():
                    lines.append("    .{} ({}),".format(name, value))
                lines[-1] = lines[-1].replace(",", "")
                lines.append("  ) {} (".format(cell.name))

            # Instance + no parameters
            else:
                lines.append("  {} {} (".format(cell.type, cell.name))

            # Port connections
            ports = sorted(cell.ports.keys())
            for port in ports:
                net = self.escape(self.net2str(cell.ports[port]))
                lines.append("    .{} ({} ),".format(self.escape(port), net))
            lines[-1] = lines[-1].replace(",", "")
            lines.append("  );")
            lines.append("")

        lines.append("endmodule")

        # Write the lines
        with open(file_name, "w") as fp:
            for line in lines:
                fp.write(line + "\n")

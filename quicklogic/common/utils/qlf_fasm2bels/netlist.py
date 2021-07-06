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

        # Cells indexed by names.
        self.cells = {}

    def add_cell(self, cell):
        assert cell.name not in self.cells, cell.name
        self.cells[cell.name] = cell

    def all_nets(self):
        nets = set()

        # Collect all nets
        for cell in self.cells.values():
            for net in cell.ports.values():
                if net is not None:
                    nets.add(net)

        return nets

    @staticmethod
    def escape(s):
        if set(s) & {'[', ']', '(', ')'}:
            return "\\" + s
        return s

    def write_verilog(self, file_name):

        def net2str(net):
            if net is None:
                return ""
            if not isinstance(net, str):
                return "_" + str(net) + "_"
            return net

        lines = []
        lines.append("module top ();")

        # Nets (wires)
        for net in self.all_nets():
            lines.append("  wire [0:0] {};".format(self.escape(net2str(net))))
        lines.append("")

        # Cell instances
        for cell in self.cells.values():

            # Attributes
            for name, value in cell.attributes.items():
                if isinstance(value, str):
                    value = "\"" + value + "\""
                lines.append("  (* {} = {} *)".format(name, value))

            # TODO: Parameters

            # Instance
            lines.append("  {} {} (".format(cell.type, cell.name))
            ports = sorted(cell.ports.keys())
            for port in ports:
                net = net2str(cell.ports[port])
                lines.append("    .{} ({}),".format(self.escape(port), self.escape(net)))
            lines.append("  );")
            lines.append("")

        lines.append("endmodule")

        with open(file_name, "w") as fp:
            for line in lines:
                fp.write(line + "\n")

from collections import defaultdict

from data_structs import PinDirection

# =============================================================================


class Netlist:
    """
    Netlist
    """

    class Cell:
        """
        Cell instance within a netlist
        """

        def __init__(self, name, cell_type):
            """
            Constructs a cell instnce given its type definition (CellType)
            taken from the physical database.
            """

            self.name = name
            self.type = cell_type.type
            self.ports = defaultdict(None)

            self.attributes = {}
            self.parameters = {}
            self.metadata = {}

            self.connections = {}

            # Initialize port directions and their connections
            for pin in cell_type.pins:
                self.ports[pin.name] = pin.direction
                self.connections[pin.name] = ""

        def rename_port(self, name, new_name):
            """
            Renames a port
            """
            assert name in self.connections, name
            assert new_name not in self.connections, new_name

            self.connections[new_name] = self.connections[name]
            del self.connections[name]

            if name in self.ports:
                self.ports[new_name] = self.ports[name]
                del self.ports[name]

        def is_leaf(self):
            """
            Returns true if the cell is a leaf (does not drive anything)
            """

            for port, direction in self.ports.items():
                if direction == PinDirection.OUTPUT:
                    if self.connections.get(port, ""):
                        return False

            return True

    # ...........................................

    def __init__(self, name):
        self.name = name
        self.ports = defaultdict(list)
        self.cells = {}

    def add_cell(self, name, cell_type):
        """
        Adds a new cell instance based on a library type
        """
        assert name not in self.cells, name

        self.cells[name] = self.Cell(name, cell_type)
        return self.cells[name]

    def remove_cell(self, name, remove_nets=False):
        """
        Removes a cell along with all nets that it drives if requested
        """
        assert name in self.cells, name

        if remove_nets:
            cell = self.cells[name]
            for port, direction in cell.ports.items():
                if direction == PinDirection.OUTPUT:
                    net = cell.connections.get(port, None)
                    if net:
                        self.remove_net(net)

        del self.cells[name]

    def rename_cell(self, name, new_name):
        """
        Renames a cell instance
        """
        assert name in self.cells, name
        assert new_name not in self.cells, new_name

        self.cells[new_name] = self.cells[name]
        del self.cells[name]

    def rename_net(self, name, new_name):
        """
        Renames a net
        """
        for cell in self.cells.values():
            for port in cell.connections.keys():
                if cell.connections[port] == name:
                    cell.connections[port] = new_name

    def remove_net(self, name):
        """
        Removes a net leaving its sources / sinks unconnected
        """
        self.rename_net(name, "")

    def prune_dangling_nets(self):
        """
        Removes all nets that are connected to only a single port
        """

        # Count net endpoints
        counts = defaultdict(int)
        for cell in self.cells.values():
            for port, net in cell.connections.items():
                if net:
                    counts[net] += 1

        # Count top-level port nets too
        for direction, ports in self.ports.items():
            for port in ports:
                counts[port] += 1        

        # Prune nets
        for net, count in counts.items():
            if net in (None, "", "1'b0", "1'b1", "1'bx"):
                continue
            if count == 1:
                self.remove_net(net)

    def prune_leaf_cells(self):
        """
        Removes all leaf cells
        """

        cells_to_prune = []
        for cell_name, cell in self.cells.items():
            if cell.is_leaf():
                cells_to_prune.append(cell_name)

        if not cells_to_prune:
            return False

        for cell_name in cells_to_prune:
            self.remove_cell(cell_name, True)

        return True

    def collapse_buffers(self):
        """
        Removes all $buf cells and replaces their output nets with input nets
        in other cells
        """

        # Loop until there is no more $buf cells
        while True:

            # Process buffers, replace their output nets with input nets
            cells_to_prune = []
            for name, cell in self.cells.items():

                if cell.type != "$buf":
                    continue

                out = cell.connections["o"]
                inp = cell.connections["i"]
                self.rename_net(out, inp)

                cells_to_prune.append(name)

            # Terminate
            if not cells_to_prune:
                break

            # Remove the buffer cells
            for cell_name in cells_to_prune:
                self.remove_cell(cell_name)

    def dump_verilog(self):
        """
        Dumps the netlist as Verilog code.
        """

        def quote_value(v):
            if isinstance(v, int) or isinstance(v, float):
                return str(v)
            else:
                return "\"" + str(v) + "\""

        def escape(s):
            # TODO
            return s

        # Header
        code = "`default_nettype none\n\n"

        # Collect all nets
        nets = set()
        for cell in self.cells.values():
            for net in cell.connections.values():
                nets.add(net)

        # Collect all ports
        ports = set()
        for key, vals in self.ports.items():
            ports |= set(vals)

        # Remove special net names
        nets -= {None, "", "1'b0", "1'b1", "1'bx"}

        # Module definition
        code += "module {} (\n".format(escape(self.name))
        for direction in ["input", "output", "inout"]:
            for port in sorted(self.ports[direction]):
                code += "  {:6s} wire {},\n".format(direction, escape(port))
        code = code[:-2] + "\n"
        code += ");\n\n"

        # Wire declarations
        for net in sorted(list(nets)):
            if net in ports:
                continue
            code += "wire {};\n".format(escape(net))
        code += "\n"

        # Cell instances
        for key in sorted(list(self.cells.keys())):
            cell = self.cells[key]

            # Skip buffers
            if cell.type == "$buf":
                continue

            # Attributes
            for attr in sorted(list(cell.attributes.keys())):
                value = quote_value(cell.attributes[attr])
                code += "(* {} = {} *)\n".format(attr, value)

            # Instance (with parameters)
            if cell.parameters:
                code += "{} # (\n".format(cell.type)
                for param in sorted(list(cell.parameters.keys())):
                    value = quote_value(cell.parameters[param])
                    code += "  .{} ({}),\n".format(param, value)
                code = code[:-2] + "\n"
                code += "{} (\n".format(escape(cell.name))

            # Instance (no parameters)
            else:
                code += "{} {} (\n".format(cell.type, escape(cell.name))

            # Connections
            lnt = max([len(p) for p in cell.connections])
            for port in sorted(list(cell.connections.keys())):
                net = cell.connections[port]
                code += "  .{} ({}),\n".format(port.ljust(lnt), escape(net))
            code = code[:-2] + "\n"

            code += ");\n\n"

        # Buffers (assigns)
        for cell_name, cell in self.cells.items():

            # Skip non-buffers
            if cell.type != "$buf":
                continue

            inp = cell.connections["i"]
            out = cell.connections["o"]
            assert out is not None, cell_name

            if not inp:
                inp = "1'bx"

            code += "assign {} = {};\n".format(out, inp);

        code += "\n"

        # Footer
        code += "endmodule\n"

        return code

import re

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

    def group_instance_ports(self, connections):
        ports_dict = {}
        indexed_identifier = r'(?P<port_name>[a-zA-Z0-9$_]+)(\[(?P<port_index>[0-9]+)\])?'

        for port in sorted(list(connections.keys())):
            match = re.search(indexed_identifier, port)
            if match is None:
                continue
            port_name = match.group("port_name")
            if (match.group("port_index") is not None):
                port_index = int(match.group("port_index"))
            else:
                port_index = 0

            # Record multi-bit port
            if (port_name not in ports_dict.keys()):
                ports_dict[port_name] = {}

            assert port_index not in ports_dict[port_name].keys(), port_index
            # Record port index and connected net
            ports_dict[port_name][port_index] = connections[port]

        grouped_ports = {}
        for port_name in ports_dict.keys():
            sorted_port = [ ports_dict[port_name][port_index] for port_index in sorted(ports_dict[port_name]) ]
            grouped_ports[port_name] = sorted_port

        return grouped_ports

    def group_module_nets(self, ports):
        ports_dict = {}
        indexed_identifier = r'(?P<port_name>[a-zA-Z0-9$_]+)(\[(?P<port_index>[0-9]+)\])?'

        for port in sorted(ports):
            match = re.search(indexed_identifier, port)
            if match is None:
                continue
            port_name = match.group("port_name")
            if (match.group("port_index") is not None):
                port_index = int(match.group("port_index"))
            else:
                port_index = 0

            # Record multi-bit port
            if (port_name not in ports_dict.keys()):
                ports_dict[port_name] = []

            assert port_index not in ports_dict[port_name], port_index
            # Record port index and connected net
            ports_dict[port_name].append(port_index)

        grouped_ports = {}
        for port_name in ports_dict.keys():
            sorted_port = sorted(ports_dict[port_name])
            grouped_ports[port_name] = sorted_port

        return grouped_ports

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

        # Group multi-bit ports from module definition
        module_ports = {}
        for direction in ["input", "output", "inout"]:
            module_ports[direction] = self.group_module_nets(self.ports[direction])

        # Module definition
        code += "module {} (\n".format(escape(self.name))

        for direction, ports in module_ports.items():
            for port, sigs in ports.items():
                code += "  {:6s} wire {}".format(direction, escape(port))
                if (len(sigs) > 1):
                    code += "[{}:{}]".format(sigs[-1], sigs[0])
                code += ",\n"
        code = code[:-2] + "\n"
        code += ");\n\n"

        # Group multi-bit wires
        grouped_wires = self.group_module_nets(list(nets))

        # Wire declarations
        for net, sigs in grouped_wires.items():
            # Don't write explicit wires for module ports
            if (net in module_ports["input"].keys() or
                net in module_ports["output"].keys() or
                net in module_ports["inout"].keys()):
                continue
            if (len(sigs) > 1):
                code += "wire [{}:{}] {};\n".format(sigs[-1], sigs[0], escape(net))
            else:
                code += "wire {};\n".format(escape(net))
        code += "\n"

        # Group multi-bit ports in cell instances
        grouped_cell_ports = {}
        for key in sorted(list(self.cells.keys())):
            cell = self.cells[key]

            # Skip buffers
            if cell.type == "$buf":
                continue

            assert cell.name not in grouped_cell_ports.keys(), cell.name
            # Record new cell instance
            grouped_cell_ports[cell.name] = self.group_instance_ports(cell.connections)

        # Cell instances
        for key in sorted(list(self.cells.keys())):
            cell = self.cells[key]

            # Skip buffers
            if cell.type == "$buf":
                continue

            # Comment
            comment = cell.metadata.get("comment", "")
            if comment:
                code += "// {}\n".format(comment)

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
            for port, nets in grouped_cell_ports[cell.name].items():
                # Multi-bit port - concatenate parts of the port
                if (len(nets) > 1):
                    port_header = "  .{} ({{".format(port)
                    net_spacer = len(port_header) * " "
                    code += port_header
                    i = 0
                    for net in reversed(nets):
                        if ((net == '') and (cell.ports.get(port, PinDirection.INPUT) == PinDirection.INPUT)):
                            net = "1'bx"
                        if (i == 0):
                            code += "{},\n".format(escape(net))
                        else:
                            code += net_spacer + "{},\n".format(escape(net))
                        i += 1
                    code = code[:-2] + "}),\n"
                # Single-bit port
                else:
                    if ((nets[0] == '') and (cell.ports.get(port, PinDirection.INPUT) == PinDirection.INPUT)):
                        nets[0] = "1'bx"
                    code += "  .{} ({}),\n".format(port, nets[0])
            code = code[:-2] + "\n"
            code += ");\n\n"

        # Buffers (assigns)
        for cell_name, cell in self.cells.items():

            # Skip non-buffers
            if cell.type != "$buf":
                continue

            # Comment
            comment = cell.metadata.get("comment", "")
            if comment:
                comment = " // {}".format(comment)

            inp = cell.connections["i"]
            out = cell.connections["o"]
            assert out is not None, cell_name

            if not inp:
                inp = "1'bx"

            code += "assign {} = {};{}\n".format(out, inp, comment);

        code += "\n"

        # Footer
        code += "endmodule\n"

        return code

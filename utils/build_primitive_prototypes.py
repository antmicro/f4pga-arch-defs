"""Tool for generating pb_type/model/cells_[sim|map] prototypes from cells_data JSONs.

utils/build_primitive_prototypes.py is a helper script to accelerate development
of adding support for new primitves. It uses cells_data JSONs (attributes and ports)
to generate XMLs: pb_type and model and verilog prototypes for cells_sim and cells_map.

The output files of the script should be treated as prototypes - they may need
some manual adjustments.

"""
import argparse
import os
import json
import re
import lxml.etree as ET

from sdf_timing.sdfparse import parse

BIN = "BIN"
BOOL = "BOOL"
INT = "INT"
STR = "STR"


def strip_trailing_number(signal):
    trailing_rgx = '[0-9]*$'
    res = re.search(trailing_rgx, signal)
    if res is None:
        return
    index = res.group()

    return signal.strip(index), index


class DelayEntry():
    def __init__(self, delay_name, delay_data):
        self.__to_pin = {"name": delay_data["to_pin"], "index": None}
        self.__from_pin = delay_data["from_pin"]
        self.__type = delay_data["type"]
        self.__delay_name = delay_name
        self.__pin_port = self.__to_pin["name"]

    def get_from_pin_name(self):
        return self.__from_pin

    def get_to_pin_name(self):
        return self.__to_pin["name"]

    def get_to_pin_index(self):
        return self.__to_pin["index"]

    def get_pin_port(self):
        return self.__pin_port

    def get_delay_name(self):
        return self.__delay_name

    def get_type(self):
        return self.__type

    def is_in_ports(self, ports):
        if self.__pin_port not in ports:
            stripped_port, index = strip_trailing_number(self.__pin_port)
            if stripped_port is None:
                return False
            elif stripped_port in ports:
                self.__pin_port = stripped_port
                self.__to_pin["name"] = "{}[{}]".format(self.__pin_port, index)
                self.__to_pin["index"] = index
                dly_name, index = strip_trailing_number(self.__delay_name)
                #self.__delay_name = "{}[{}]".format(dly_name, index)
            else:
                return False

        return self.__from_pin in ports


def is_clock_delay(pin, clock_ports):
    return any(pin == clock_port["name"] for clock_port in clock_ports)


def get_ports_dictionary(ports):
    ports_dict = {"input": list(), "output": list(), "clock": list()}

    for port_name, config in ports.items():
        direction = config["direction"]
        width = config["width"]

        port_attrs = {
            "name": port_name,
            "num_pins": str(width),
        }

        ports_dict[direction].append(port_attrs)

    return ports_dict


def build_pb_type_prototype(
        ports, attrs, primitive, delay_data, filter_clock_delays,
        pre_built_pb_type
):

    params_list = list()
    if pre_built_pb_type is not None:
        parser = ET.XMLParser(remove_blank_text=True)
        pb_type_xml = ET.parse(pre_built_pb_type, parser=parser).getroot()
        fasm_params_xml = pb_type_xml.xpath("//meta[@name='fasm_params']")[0]
        fasm_params_list = [
            x.strip() for x in fasm_params_xml.text.split('\n') if x.strip()
        ]

        for param in fasm_params_list:
            fields = [x.strip() for x in param.split("=")]
            param_key = fields[0]
            param_value = fields[1]

            params_list.append((param_key, param_value))
    else:
        pb_type_xml = ET.Element(
            "pb_type", {
                "name": primitive.upper(),
                "num_pb": "1",
                "blif_model": ".subckt {}_VPR".format(primitive.upper())
            }
        )

        metadata = ET.SubElement(pb_type_xml, "metadata")
        fasm_params_xml = ET.SubElement(
            metadata, "meta", {"name": "fasm_params"}
        )

    ports_dict = get_ports_dictionary(ports)

    for port_type, port_list in ports_dict.items():
        for port in sorted(port_list, key=lambda port: port["name"]):
            ET.SubElement(pb_type_xml, port_type, port)

    delays = list()
    for delay in delay_data:
        from_pin = delay.get_from_pin_name()
        to_pin = delay.get_to_pin_name()
        pin_port = delay.get_pin_port()
        type = delay.get_type()
        delay_name = delay.get_delay_name()

        is_clk_dly = is_clock_delay(from_pin, ports_dict["clock"])

        if is_clk_dly and from_pin in filter_clock_delays:
            continue

        if type == "hold":
            assert is_clk_dly, from_pin
            delay_type = "T_hold"
            delay_attrs = {
                "value": "{%s}" % delay_name,
                "port": to_pin,
                "clock": from_pin
            }
        elif type == "setup":
            assert is_clk_dly
            delay_type = "T_setup"
            delay_attrs = {
                "value": "{%s}" % delay_name,
                "port": to_pin,
                "clock": from_pin
            }
        elif type == "iopath" and is_clk_dly:
            delay_type = "T_clock_to_Q"
            delay_attrs = {
                "max": "{%s}" % delay_name,
                "port": to_pin,
                "clock": from_pin
            }
        elif type == "iopath":
            delay_type = "delay_constant"
            delay_attrs = {
                "max": "{%s}" % delay_name,
                "out_port": to_pin,
                "in_port": from_pin
            }
        else:
            assert False, delay_data

        port_name = pin_port if is_clk_dly else from_pin

        delays.append((delay_type, delay_attrs, port_name))

    for delay_type, delay_attrs, _ in sorted(delays, key=lambda port: port[0]):
        ET.SubElement(pb_type_xml, delay_type, delay_attrs)

    for attr_name, config in attrs.items():
        attr_type = config["type"]
        values = config["values"]
        digits = config["digits"]
        if attr_type == BIN or attr_type == INT:
            attr_key = "{}[{}:0]".format(attr_name, digits - 1)
            attr_value = attr_name

            params_list.append((attr_key, attr_value))
        elif attr_type == BOOL:
            params_list.append((attr_name, attr_name))
        else:
            assert attr_type == STR
            for val in values:
                attr_key = "{}.{}".format(attr_name, val)
                attr_value = "{}_{}".format(attr_name, val)
                params_list.append((attr_key, attr_value))

    params_txt = "\n"
    for param_key, param_value in params_list:
        params_txt += "{} = {}\n".format(param_key, param_value)

    fasm_params_xml.text = params_txt

    return pb_type_xml


def build_model_prototype(ports, name, delay_data, filter_clock_delays):
    xi_url = "http://www.w3.org/2001/XInclude"
    ET.register_namespace('xi', xi_url)
    models_xml = ET.Element("models", {}, nsmap={"xi": xi_url})
    model_xml = ET.SubElement(
        models_xml, "model", {"name": "{}_VPR".format(name.upper())}
    )
    input_ports = ET.SubElement(model_xml, "input_ports")
    output_ports = ET.SubElement(model_xml, "output_ports")

    ports_dict = get_ports_dictionary(ports)

    for port_name, config in ports.items():
        input_type = config["direction"]

        attrs = {"name": port_name}

        if input_type == "clock":
            selected_ports = input_ports
            attrs["is_clock"] = "1"
        elif input_type == "input":
            selected_ports = input_ports

            for delay in delay_data:
                to_pin = delay.get_to_pin_name()
                from_pin = delay.get_from_pin_name()
                pin_port = delay.get_pin_port()

                if type == "iopath" and port_name == from_pin:
                    if "combinational_sink_ports" not in attrs:
                        attrs["combinational_sink_ports"] = to_pin
                    else:
                        attrs["combinational_sink_ports"] += " {}".format(
                            to_pin
                        )
                elif pin_port == port_name and from_pin not in filter_clock_delays:
                    attrs["clock"] = from_pin
                    break
        else:
            selected_ports = output_ports

            for delay in delay_data:
                from_pin = delay.get_from_pin_name()
                pin_port = delay.get_pin_port()
                is_clk_dly = is_clock_delay(from_pin, ports_dict["clock"])

                if pin_port == port_name and is_clk_dly and from_pin not in filter_clock_delays:
                    attrs["clock"] = from_pin

        assert selected_ports is not None
        ET.SubElement(selected_ports, "port", attrs)

    return models_xml


def build_cells_prototypes(ports, attrs, name, cells_sim, cells_map):
    module_regx = "module {}".format(name.upper())
    with open(cells_map, "r") as f:
        data = f.read()
        # Check if the module is already added
        if re.search(module_regx, data, re.MULTILINE) is not None:
            print(
                '*** WARNING *** Skipping generating cells_map for "{}"' \
                ' primitive - module exists.'.format(
                    name
                ),
            )
            return None, None
    with open(cells_sim, "r") as f:
        data = f.read()
        # Check if the module is already added
        if re.search(module_regx, data, re.MULTILINE) is not None:
            print(
                '*** WARNING *** Skipping generating cells_sim for "{}"' \
                ' primitive - module exists.'.format(
                    name
                ),
            )
            return None, None

    verilog_sim_module = "module {}_VPR (\n".format(name.upper())

    ports_str = list()
    for port_name, config in ports.items():
        direction = config["direction"]
        width = config["width"]
        port_str = "  input" if (direction == "input" or direction == "clock") else "  output"
        if width > 1:
            port_str += " [{}:0]".format(width - 1)
        port_str += " {},".format(port_name)
        ports_str.append(port_str)

    ports_str[-1] = ports_str[-1][:-1] + "\n"
    verilog_sim_module += "\n".join(port for port in ports_str)
    verilog_sim_module += ");\n"

    fasm_params_str = list()
    for attr_name, config in attrs.items():
        attr_type = config["type"]
        values = config["values"]
        digits = config["digits"]
        if attr_type == BIN:
            # Default single value
            if type(values) is int:
                fasm_param_str = "  parameter [{}:0] {} = {}'d{};" \
                                 .format(digits - 1, attr_name, digits, values)
            # Choice, pick the 1st one as default
            elif type(values) is list and len(values) > 1:
                fasm_param_str = "  parameter [{}:0] {} = {}'d{};" \
                                 .format(digits - 1, attr_name, digits, values[0])
            else:
                fasm_param_str = "  parameter [{}:0] {} = {}'d0;" \
                                 .format(digits - 1, attr_name, digits)
        elif attr_type == BOOL or attr_type == STR:
            fasm_param_str = "  parameter {} = \"{}\";" \
                             .format(attr_name, values[0])
        else:
            assert attr_type == INT
            fasm_param_str = "  parameter integer {} = {};" \
                             .format(attr_name, values[0])

        fasm_params_str.append(fasm_param_str)

    verilog_sim_module += "\n".join(param for param in fasm_params_str)
    verilog_map_module = verilog_sim_module.replace(
        "{}_VPR".format(name.upper()), name.upper()
    )
    verilog_sim_module += "\nendmodule"

    verilog_map_module += "\n\n  {}_VPR #(\n".format(name.upper())

    init_fasm_params_str = list()
    for attr_name, config in attrs.items():
        attr_type = config["type"]
        if attr_type == BOOL:
            init_fasm_param_str = "    .{}({} == \"TRUE\"),".format(
                attr_name, attr_name
            )
        else:
            init_fasm_param_str = "    .{}({}),".format(attr_name, attr_name)
        init_fasm_params_str.append(init_fasm_param_str)

    init_fasm_params_str[-1] = init_fasm_params_str[-1][:-1] + "\n"
    verilog_map_module += "\n".join(param for param in init_fasm_params_str)
    verilog_map_module += "  ) _TECHMAP_REPLACE_ (\n"

    init_ports_str = list()
    for port in ports.keys():
        init_port_str = "    .{}({}),".format(port, port)
        init_ports_str.append(init_port_str)

    init_ports_str[-1] = init_ports_str[-1][:-1] + "\n"
    verilog_map_module += "\n".join(port for port in init_ports_str)
    verilog_map_module += "  );\nendmodule"

    return verilog_sim_module, verilog_map_module


def get_delay_data(sdf_timings_dir, primitive, ports):
    """
    This function retrieves timing data from the SDF files in the prjxray-db.

    It returns a list with all timing annotation to add in the
    pb_type and model of the input primitve.
    """

    bels = set()
    primitive_delays = list()

    for filename in os.listdir(sdf_timings_dir):
        if not filename.endswith(".sdf"):
            continue

        with open(os.path.join(sdf_timings_dir, filename), "r") as fp:
            timings = parse(fp.read())

        for cell, cell_data in timings["cells"].items():
            for instance, instance_data in cell_data.items():

                if instance != primitive:
                    continue

                bels.add("{}.{}".format(cell, instance))

                for delay_name, delay_data in instance_data.items():
                    delay_entry = DelayEntry(delay_name, delay_data)
                    if not delay_entry.is_in_ports(ports):
                        continue
                    primitive_delays.append(delay_entry)

    blk_tl_primitive = "BLK-TL-{}".format(primitive)
    bels_json = {primitive: {primitive: {blk_tl_primitive: list()}}}
    for bel in bels:
        bels_json[primitive][primitive][blk_tl_primitive].append(bel)

    return primitive_delays, bels_json


def main():
    parser = argparse.ArgumentParser(
        description="Creates XML and techmap files for given primitives."
    )
    parser.add_argument(
        "--arch",
        default="artix7",
        choices=["artix7", "zynq7", "kintex7"],
        help="Architectures available: artix7, kintex7, zynq7"
    )
    parser.add_argument(
        "--prjxray-db", required=True, help="Path to prjxray-db directory"
    )
    parser.add_argument(
        "--techmap-dir", required=True, help="Path to techmap directory"
    )
    parser.add_argument(
        "--bels-json",
        required=True,
        help="bels.json file used for updating timing info"
    )
    parser.add_argument(
        "--primitive", required=True, help="Name of the primitive."
    )
    parser.add_argument(
        "--build-cells",
        action="store_true",
        help="Enable building verilog models."
    )
    parser.add_argument(
        "--output-dir", default=os.getcwd(), help="Output directory."
    )
    parser.add_argument(
        "--pre-built-pb-type",
        default=None,
        help="Path to a pre-built pb_type with initial configurations."
    )
    parser.add_argument(
        "--filter-clock-delays",
        default="",
        help="Comma separated list of clocks to filter out from delays"
    )

    args = parser.parse_args()

    primitive = args.primitive

    attrs_file = os.path.join(
        args.prjxray_db, args.arch, "cells_data",
        "{}_attrs.json".format(primitive)
    )
    ports_file = os.path.join(
        args.prjxray_db, args.arch, "cells_data",
        "{}_ports.json".format(primitive)
    )

    assert os.path.exists(attrs_file) and os.path.exists(ports_file), (
        attrs_file, ports_file
    )

    with open(attrs_file, "r") as f:
        attrs = json.load(f)

    with open(ports_file) as f:
        ports = json.load(f)

    sdf_timings_dir = os.path.join(args.prjxray_db, args.arch, "timings")
    delay_data, bels_json = get_delay_data(
        sdf_timings_dir, primitive.upper(), ports
    )

    filter_clock_delays = args.filter_clock_delays.split(",")
    model_xml = build_model_prototype(
        ports, primitive, delay_data, filter_clock_delays
    )
    pb_type_xml = build_pb_type_prototype(
        ports, attrs, primitive, delay_data, filter_clock_delays,
        args.pre_built_pb_type
    )
    if args.build_cells:
        assert os.path.exists(args.techmap_dir), (args.techmap_dir)
        cells_sim = os.path.join(args.techmap_dir, "cells_sim.v")
        cells_map = os.path.join(args.techmap_dir, "cells_map.v")
        verilog_sim_module, verilog_map_module = build_cells_prototypes(
            ports, attrs, primitive, cells_sim, cells_map
        )
        if verilog_sim_module is not None and verilog_map_module is not None:
            with open(cells_sim, "a") as f:
                f.write("\n")
                f.write(verilog_sim_module)
            with open(cells_map, "a") as f:
                f.write("\n")
                f.write(verilog_map_module)

    model_file = "{}.model.xml".format(primitive)
    with open(os.path.join(args.output_dir, model_file), "w") as f:
        xml_str = ET.tostring(model_xml, pretty_print=True).decode("utf-8")
        f.write(xml_str)

    pb_type_file = "{}.pb_type.xml".format(primitive)
    with open(os.path.join(args.output_dir, pb_type_file), "w") as f:
        xml_str = ET.tostring(pb_type_xml, pretty_print=True).decode("utf-8")
        f.write(xml_str)

    with open(args.bels_json, "r") as f:
        data = json.load(f)
        bels_json.update(data)

    with open(args.bels_json, "w") as f:
        json.dump(bels_json, f, indent=4)


if __name__ == "__main__":
    main()

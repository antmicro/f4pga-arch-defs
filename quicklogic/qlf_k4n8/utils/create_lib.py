#!/usr/bin/env python3
"""
Creates a device library file
"""
import argparse
import sys
import csv
import os
from collections import namedtuple
from datetime import date
import lxml.etree as ET

# =============================================================================


# =============================================================================
"""
Pin properties
name - pin_name
dir - direction (input/output)
used - specify 'yes' if user is using the pin else specify 'no'
clk - specify associate clock
"""
PinData = namedtuple("PinData", "name dir used clk")

# =============================================================================

def main():
    """
    Creates a device library file by getting data from given csv and xml file
    """
    parser = argparse.ArgumentParser(
        description='Creates a device library file.'
    )
    parser.add_argument(
        "--lib",
        "-l",
        "-L",
        type=str,
        default="qlf_k4n8.lib",
        help='The output device lib file'
    )
    parser.add_argument(
        "--lib_name",
        "-n",
        "-N",
        type=str,
        required=True,
        help='Specify library name'
    )
    parser.add_argument(
        "--cell_name",
        "-m",
        "-M",
        type=str,
        required=True,
        help='Specify cell name'
    )
    parser.add_argument(
        "--csv",
        "-c",
        "-C",
        type=str,
        required=True,
        help='Input pin-map csv file'
    )
    parser.add_argument(
        "--xml",
        "-x",
        "-X",
        type=str,
        required=True,
        help='Input interface-mapping xml file'
    )

    args = parser.parse_args()

    csv_pin_data = set()
    assoc_clk = dict()
    with open(args.csv, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            csv_pin_data.add(row['port_name'])
            if row['Associated Clock'] is not None:
                assoc_clk[row['port_name']] = row['Associated Clock'].strip()

    port_names = parse_xml(args.xml)
    create_lib(
        port_names, csv_pin_data, args.lib_name, args.lib, args.cell_name,
        assoc_clk
    )


# =============================================================================
def create_lib(
    port_names, csv_pin_data, lib_name, lib_file_name, cell_name, assoc_clk
):
    """
    Create lib file
    """
    # Read header template file and populate lib file with this data
    curr_dir = os.path.dirname(os.path.abspath(__file__))

    header_templ_file = os.path.join(
        curr_dir, '../devices/umc22/lib_header_template.txt'
    )
    in_str = open(header_templ_file, 'r').read()
    curr_str = in_str.replace("@lib_name@", lib_name)
    today = date.today()
    curr_date = today.strftime("%B %d, %Y")
    str_rep_date = curr_str.replace("@Date@", curr_date)
    str1= str_rep_date.replace("@cell_name@", cell_name)

    pins = []
    for port in port_names:
        pin_dir = "input"
        if port.find("F2A") != -1:
            pin_dir = "output"

        pin_used = False
        if port in csv_pin_data:
            pin_used = True

        clk = ""
        if port in assoc_clk:
            if assoc_clk[port].strip() != '':
                clk = assoc_clk[port].strip()

        pin_data = PinData(
            name = port,
            dir = pin_dir,
            used = pin_used,
            clk = clk
        )
        pins.append(pin_data)

    curly_braces_open = "{"
    curly_braces_close = "}"
    lib_data = ""
    for pin in pins:
        if pin.used:
            if pin.dir == "input":
                curr_str = "\n\t\tpin ({}) {}".format(pin.name, curly_braces_open)
                cap = "0.01686"
                max_tran = "0.2000"
                curr_str += form_pin_header(pin.dir, cap, max_tran)

                if pin.clk != '':
                    clks = pin.clk.split(' ')
                    for clk in clks:
                        clk_name = clk
                        timing_type = ['setup_rising', 'hold_rising']
                        for val in timing_type:
                            curr_str += form_in_timing_group(clk_name, val)
                curr_str += "\n\t\t{}".format(curly_braces_close)
                lib_data += curr_str
            else:
                curr_str = "\n\t\tpin ({}) {}".format(
                    pin.name, curly_braces_open
                )
                cap = "0.013646"
                max_tran = "0.2000"
                curr_str += form_pin_header(pin.dir, cap, max_tran)

                if pin.clk != '':
                    clks = pin.clk.split(' ')
                    for clk in clks:
                        clk_name = clk
                        timing_type = "rising_edge"
                        curr_str += form_out_timing_group(
                            clk_name, timing_type
                        )
                    curr_str += form_out_reset_timing_group(
                        "RESET_N", "positive_unate", "clear"
                    )
                curr_str += "\n\t\t{}".format(curly_braces_close)
                lib_data += curr_str
        else:
            if pin.dir == "input":
                curr_str = "\n\t\tpin ({}) {}".format(
                    pin.name, curly_braces_open
                )
                cap = "0.01686"
                max_tran = "0.2000"
                curr_str += form_pin_header(pin.dir, cap, max_tran)
                curr_str += "\n\t\t{}".format(curly_braces_close)
                lib_data += curr_str
            else:
                curr_str = "\n\t\tpin ({}) {}".format(
                    pin.name, curly_braces_open
                )
                cap = "0.013646"
                max_tran = "0.2000"
                curr_str += form_pin_header(pin.dir, cap, max_tran)
                curr_str += "\n\t\t{}".format(curly_braces_close)
                lib_data += curr_str

    dedicated_pin_lib_file = os.path.join(
        curr_dir, '../devices/umc22/dedicated_pin_lib_data.txt'
    )
    dedicated_pin_data = open(dedicated_pin_lib_file, 'r').read()

    inter_str = str1.replace("@dedicated_pin_data@", dedicated_pin_data)

    final_str = inter_str.replace("@user_pin_data@", lib_data)
    with open(lib_file_name, 'w') as out_fp:
        out_fp.write(final_str)


# =============================================================================

def form_pin_header(direction, cap, max_tran):
    '''
    Form pin header section
    '''
    curr_str = "\n\t\t\tdirection : {};\n\t\t\tcapacitance : {};".format(
        direction, cap
    )
    curr_str += "\n\t\t\tmax_transition : {};".format(max_tran)
    return curr_str

# =============================================================================


def form_out_reset_timing_group(reset_name, timing_sense, timing_type):
    '''
    Form timing group for output pin when related pin is reset
    '''
    cell_fall_val = "4.6000"
    fall_tran_val = "0.2000"
    curly_braces_open = "{"
    curly_braces_close = "}"
    curr_str = "\n\t\t\ttiming () {}\n\t\t\t\trelated_pin : \"{}\";".format(
        curly_braces_open, reset_name
    )
    curr_str += "\n\t\t\t\ttiming_sense : {};".format(timing_sense)
    curr_str += "\n\t\t\t\ttiming_type : {};".format(timing_type)
    curr_str += "\n\t\t\t\tcell_fall (scalar) {}\n\t\t\t\t\tvalues({});".format(
        curly_braces_open, cell_fall_val
    )
    curr_str += "\n\t\t\t\t{}".format(curly_braces_close)
    curr_str += "\n\t\t\t\tfall_transition (scalar) {}\n\t\t\t\t\tvalues({});".format(
        curly_braces_open, fall_tran_val
    )
    curr_str += "\n\t\t\t\t{}".format(curly_braces_close)
    curr_str += "\n\t\t\t{}".format(curly_braces_close)
    return curr_str

# =============================================================================

def form_out_timing_group(clk_name, timing_type):
    '''
    Form timing group for output pin in a Pin group in a library file
    '''
    cell_rise_val = "2.59"
    cell_fall_val = "2.59"
    rise_tran_val = "0.85"
    fall_tran_val = "0.85"
    curly_braces_open = "{"
    curly_braces_close = "}"
    curr_str = "\n\t\t\ttiming () {}\n\t\t\t\trelated_pin : \"{}\";".format(
        curly_braces_open, clk_name
    )
    curr_str += "\n\t\t\t\ttiming_type : {};".format(timing_type)
    curr_str += "\n\t\t\t\tcell_rise (scalar) {}\n\t\t\t\t\tvalues({});\n\t\t\t\t{}".format(
        curly_braces_open, cell_rise_val, curly_braces_close
    )
    curr_str += "\n\t\t\t\trise_transition (scalar) {}\n\t\t\t\t\tvalues({});".format(
        curly_braces_open, rise_tran_val
    )
    curr_str += "\n\t\t\t\t{}".format(curly_braces_close)
    curr_str += "\n\t\t\t\tcell_fall (scalar) {}\n\t\t\t\t\tvalues({});".format(
        curly_braces_open, cell_fall_val
    )
    curr_str += "\n\t\t\t\t{}".format(curly_braces_close)
    curr_str += "\n\t\t\t\tfall_transition (scalar) {}\n\t\t\t\t\tvalues({});".format(
        curly_braces_open, fall_tran_val
    )
    curr_str += "\n\t\t\t\t{}".format(curly_braces_close)
    curr_str += "\n\t\t\t{}".format(curly_braces_close)
    return curr_str


# =============================================================================

def form_in_timing_group(clk_name, timing_type):
    '''
    Form timing group for input pin in a Pin group in a library file
    '''
    rise_constraint_val = "0.0"
    fall_constraint_val = "0.0"
    if timing_type == "setup_rising":
        rise_constraint_val = "-2.1"
        fall_constraint_val = "-2.1"
    else:
        rise_constraint_val = "2.21"
        fall_constraint_val = "2.21"

    curly_braces_open = "{"
    curly_braces_close = "}"
    curr_str = "\n\t\t\ttiming () {}\n\t\t\t\trelated_pin : \"{}\";".format(
        curly_braces_open, clk_name
    )
    curr_str += "\n\t\t\t\ttiming_type : {};".format(timing_type)
    curr_str += "\n\t\t\t\trise_constraint (scalar) {}\n\t\t\t\t\tvalues({});".format(
        curly_braces_open, rise_constraint_val
    )
    curr_str += "\n\t\t\t\t{}".format(curly_braces_close)
    curr_str += "\n\t\t\t\tfall_constraint (scalar) {}\n\t\t\t\t\tvalues({});".format(
        curly_braces_open, fall_constraint_val
    )
    curr_str += "\n\t\t\t\t{}".format(curly_braces_close)
    curr_str += "\n\t\t\t{}".format(curly_braces_close)
    return curr_str

# =============================================================================

def parse_xml(xml_file):
    """
    Parses given xml file and collects the desired data
    """
    parser = ET.XMLParser(resolve_entities=False, strip_cdata=False)
    xml_tree = ET.parse(xml_file, parser)
    xml_root = xml_tree.getroot()

    port_names = []

    # Get the "IO" section
    xml_io = xml_root.find("IO")
    if xml_io is None:
        print("ERROR: No mandatory 'IO' section defined in 'DEVICE' section")
        sys.exit(1)

    xml_top_io = xml_io.find("TOP_IO")
    if xml_top_io is not None:
        ports = parse_xml_io(xml_top_io)
        port_names.extend(ports)

    xml_bottom_io = xml_io.find("BOTTOM_IO")
    if xml_bottom_io is not None:
        ports = parse_xml_io(xml_bottom_io)
        port_names.extend(ports)

    xml_left_io = xml_io.find("LEFT_IO")
    if xml_left_io is not None:
        ports = parse_xml_io(xml_left_io)
        port_names.extend(ports)

    xml_right_io = xml_io.find("RIGHT_IO")
    if xml_right_io is not None:
        ports = parse_xml_io(xml_right_io)
        port_names.extend(ports)

    return port_names

# =============================================================================

def parse_xml_io(xml_io):
    """
    Parses xml and get data for mapped_name key
    """
    assert xml_io is not None
    port_names = []
    for xml_cell in xml_io.findall("CELL"):
        mapped_name = xml_cell.get("mapped_name")
        # define properties for scalar pins
        scalar_mapped_pins = vec_to_scalar(mapped_name)
        port_names.extend(scalar_mapped_pins)
    return port_names


# =============================================================================

def vec_to_scalar(port_name):
    """
    Converts given bus port into a list of its scalar port equivalents
    """
    scalar_ports = []
    if port_name is not None and ':' in port_name:
        open_brace = port_name.find('[')
        close_brace = port_name.find(']')
        if open_brace == -1 or close_brace == -1:
            print(
                'Invalid portname "{}" specified. Bus ports should contain [ ] to specify range'
                .format(port_name),
                file=sys.stderr
            )
            sys.exit(1)
        bus = port_name[open_brace + 1:close_brace]
        lsb = int(bus[:bus.find(':')])
        msb = int(bus[bus.find(':') + 1:])
        if lsb > msb:
            for i in range(msb, lsb + 1):
                curr_port_name = port_name[:open_brace] + '[' + str(i) + ']'
                scalar_ports.append(curr_port_name)
        else:
            for i in range(lsb, msb + 1):
                curr_port_name = port_name[:open_brace] + '[' + str(i) + ']'
                scalar_ports.append(curr_port_name)
    else:
        scalar_ports.append(port_name)

    return scalar_ports

# =============================================================================

if __name__ == '__main__':
    main()

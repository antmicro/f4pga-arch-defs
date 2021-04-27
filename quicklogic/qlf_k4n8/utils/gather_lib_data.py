#!/usr/bin/env python3
"""
Gather data from given lib file. This data is then used to populate JSON file
that has delay numbers for some parameters related to F2A and A2F pins.
"""
import argparse


# =============================================================================


def main():
    """
    Gather lib information from the given library file
    """
    parser = argparse.ArgumentParser(
        description='Gather lib information from the given library file.'
    )
    parser.add_argument(
        "--lib",
        "-l",
        "-L",
        type=str,
        required=True,
        help='Specify input lib file'
    )

    args = parser.parse_args()

    lib_fp = open(args.lib, newline='')

    for line in lib_fp:
        if line.find("bus ( gfpga_pad_IO_A2F") != -1:
            a2f_process_lib_data(lib_fp)
        elif line.find("bus ( gfpga_pad_IO_F2A") != -1:
            f2a_process_lib_data(lib_fp)


# =============================================================================

def f2a_process_lib_data(lib_fp):
    """
    Process F2A pin lib_data
    """
    rising_edge_cell_rise_val = set()
    rising_edge_cell_fall_val = set()
    rising_edge_rise_tran_val = set()
    rising_edge_fall_tran_val = set()
    max_transition = set()
    capacitance = set()
    for f2a_line in lib_fp:

        pin_pos = f2a_line.find("pin(\"")
        if pin_pos != -1:

            for pin_line in lib_fp:
                if pin_line.find("rising_edge") != -1:
                    rising_edge_cell_rise_val, rising_edge_cell_fall_val, \
                rising_edge_rise_tran_val, rising_edge_fall_tran_val = f2a_timing_type(
                    lib_fp, pin_line, "rising_edge",
                    rising_edge_cell_rise_val, rising_edge_cell_fall_val,
                    rising_edge_rise_tran_val, rising_edge_fall_tran_val
                    )
                elif pin_line.find("max_transition") != -1:
                    val_list = pin_line.split(' : ')
                    max_transition.add(
                        float(val_list[1].split(' ;')[0].strip())
                    )
                elif pin_line.find("capacitance") != -1:
                    val_list = pin_line.split(' : ')
                    capacitance.add(
                        float(val_list[1].split(' ;')[0].strip())
                    )
                elif pin_line.find("end of bus") != -1:
                    break

            print(
                'F2A {} least_val: {}, highest_val: {}'.format(
                    "max_transition",
                    next(iter(sorted(max_transition))),
                    sorted(max_transition).pop()
                )
            )
            print(
                'F2A {} least_val: {}, highest_val: {}'.format(
                    "capacitance", next(iter(sorted(capacitance))),
                    sorted(capacitance).pop()
                )
            )
            print(
                'F2A {} least_val: {}, highest_val: {}'.format(
                    "rising_edge_cell_rise_val",
                    next(iter(sorted(rising_edge_cell_rise_val))),
                    sorted(rising_edge_cell_rise_val).pop()
                )
            )
            print(
                'F2A {} least_val: {}, highest_val: {}'.format(
                    "rising_edge_cell_fall_val",
                    next(iter(sorted(rising_edge_cell_fall_val))),
                    sorted(rising_edge_cell_fall_val).pop()
                )
            )
            print(
                'F2A {} least_val: {}, highest_val: {}'.format(
                    "rising_edge_rise_tran_val",
                    next(iter(sorted(rising_edge_rise_tran_val))),
                    sorted(rising_edge_rise_tran_val).pop()
                )
            )
            print(
                'F2A {} least_val: {}, highest_val: {}'.format(
                    "rising_edge_fall_tran_val",
                    next(iter(sorted(rising_edge_fall_tran_val))),
                    sorted(rising_edge_fall_tran_val).pop()
                )
            )
            break

# =============================================================================

def a2f_process_lib_data(lib_fp):
    """
    Process A2F pin lib_data
    """
    setup_rising_rise_constraint_val = set()
    setup_rising_fall_constraint_val = set()
    hold_rising_rise_constraint_val = set()
    hold_rising_fall_constraint_val = set()

    max_transition = set()
    capacitance = set()
    for a2f_line in lib_fp:

        pin_pos = a2f_line.find("pin(\"")
        if pin_pos != -1:

            for pin_line in lib_fp:
                if pin_line.find("setup_rising") != -1:
                    setup_rising_rise_constraint_val, setup_rising_fall_constraint_val = a2f_timing_type(
                        lib_fp, pin_line, "setup_rising",
                        setup_rising_rise_constraint_val,
                        setup_rising_fall_constraint_val
                    )
                elif pin_line.find("hold_rising") != -1:
                    hold_rising_rise_constraint_val, hold_rising_fall_constraint_val = a2f_timing_type(
                        lib_fp, pin_line, "hold_rising",
                        hold_rising_rise_constraint_val,
                        hold_rising_fall_constraint_val
                    )
                elif pin_line.find("max_transition") != -1:
                    val_list = pin_line.split(' : ')
                    max_transition.add(
                        float(val_list[1].split(' ;')[0].strip())
                    )
                elif pin_line.find("capacitance") != -1:
                    val_list = pin_line.split(' : ')
                    capacitance.add(
                        float(val_list[1].split(' ;')[0].strip())
                    )
                elif pin_line.find("end of bus gfpga_pad_IO_A2F") != -1:
                    break

            print(
                'A2F {} least_val: {}, highest_val: {}'.format(
                    "max_transition",
                    next(iter(sorted(max_transition))),
                    sorted(max_transition).pop()
                )
            )
            print(
                'A2F {} least_val: {}, highest_val: {}'.format(
                    "capacitance", next(iter(sorted(capacitance))),
                    sorted(capacitance).pop()
                )
            )
            print(
                'A2F {} least_val: {}, highest_val: {}'.format(
                    "setup_rising_rise_constraint_val",
                    next(
                        iter(sorted(setup_rising_rise_constraint_val))
                    ),
                    sorted(setup_rising_rise_constraint_val).pop()
                )
            )
            print(
                'A2F {} least_val: {}, highest_val: {}'.format(
                    "setup_rising_fall_constraint_val",
                    next(
                        iter(sorted(setup_rising_fall_constraint_val))
                    ),
                    sorted(setup_rising_fall_constraint_val).pop()
                )
            )
            print(
                'A2F {} least_val: {}, highest_val: {}'.format(
                    "hold_rising_rise_constraint_val",
                    next(
                        iter(sorted(hold_rising_rise_constraint_val))
                    ),
                    sorted(hold_rising_rise_constraint_val).pop()
                )
            )
            print(
                'A2F {} least_val: {}, highest_val: {}'.format(
                    "hold_rising_fall_constraint_val",
                    next(
                        iter(sorted(hold_rising_fall_constraint_val))
                    ),
                    sorted(hold_rising_fall_constraint_val).pop()
                )
            )
            break

# =============================================================================

def a2f_timing_type(lib_fp, pin_line, type_str, rise_value, fall_value):
    """
    Collect A2F pin data
    """
    type_pos = pin_line.find(type_str)
    if type_pos != -1:
        for type_line in lib_fp:
            rise_pos = type_line.find("rise_constraint")
            if rise_pos != -1:
                for constraint_line in lib_fp:
                    if constraint_line.find("}") != -1:
                        break

                    if constraint_line.find('values') != -1:
                        val_set = set()
                        val_set = populate_set(constraint_line, val_set)

                        for val_line in lib_fp:
                            if val_line.find(");") != -1:
                                val_set = populate_set(val_line, val_set)
                                break

                            val_set = populate_set(val_line, val_set)

                        rise_value.add(sorted(val_set).pop())
                        #rise_value.add(next(iter(sorted(val_set))))
                        break
                break

        for type_line in lib_fp:
            fall_pos = type_line.find("fall_constraint")
            if fall_pos != -1:
                for constraint_line in lib_fp:
                    if constraint_line.find("}") != -1:
                        break

                    if constraint_line.find('values') != -1:
                        val_set = set()
                        val_set = populate_set(constraint_line, val_set)

                        for val_line in lib_fp:
                            if val_line.find(");") != -1:
                                val_set = populate_set(val_line, val_set)
                                break

                            val_set = populate_set(val_line, val_set)
                        fall_value.add(sorted(val_set).pop())
                        #fall_value.add(next(iter(sorted(val_set))))
                        break
                break

    return rise_value, fall_value

# =============================================================================

def f2a_timing_type(
    lib_fp, pin_line, type_str, rising_edge_cell_rise_val,
    rising_edge_cell_fall_val, rising_edge_rise_tran_val,
    rising_edge_fall_tran_val
):
    """
    Collect F2A pin data
    """
    type_pos = pin_line.find(type_str)
    if type_pos != -1:
        for type_line in lib_fp:
            rise_pos = type_line.find("cell_rise")
            if rise_pos != -1:
                for constraint_line in lib_fp:
                    if constraint_line.find("}") != -1:
                        break

                    if constraint_line.find('values') != -1:
                        val_set = set()
                        val_set = populate_set(
                            constraint_line, val_set
                        )

                        for val_line in lib_fp:
                            if val_line.find(");") != -1:
                                val_set = populate_set(val_line, val_set)
                                break

                            val_set = populate_set(val_line, val_set)

                        rising_edge_cell_rise_val.add(
                            sorted(val_set).pop()
                            #next(iter(sorted(val_set)))
                        )
                        break
                break

        for type_line in lib_fp:
            fall_pos = type_line.find("cell_fall")
            if fall_pos != -1:
                for constraint_line in lib_fp:
                    if constraint_line.find("}") != -1:
                        break

                    if constraint_line.find('values') != -1:
                        val_set = set()
                        val_set = populate_set(
                            constraint_line, val_set
                        )

                        for val_line in lib_fp:
                            if val_line.find(");") != -1:
                                val_set = populate_set(val_line, val_set)
                                break

                            val_set = populate_set(val_line, val_set)
                        rising_edge_cell_fall_val.add(
                            sorted(val_set).pop()
                            #next(iter(sorted(val_set)))
                        )
                        break
                break

        for type_line in lib_fp:
            fall_pos = type_line.find("rise_transition")
            if fall_pos != -1:
                for constraint_line in lib_fp:
                    if constraint_line.find("}") != -1:
                        break

                    if constraint_line.find('values') != -1:
                        val_set = set()
                        val_set = populate_set(
                            constraint_line, val_set
                        )

                        for val_line in lib_fp:
                            if val_line.find(");") != -1:
                                val_set = populate_set(val_line, val_set)
                                break

                            val_set = populate_set(val_line, val_set)
                        rising_edge_rise_tran_val.add(
                            sorted(val_set).pop()
                            #next(iter(sorted(val_set)))
                        )
                        break
                break

        for type_line in lib_fp:
            fall_pos = type_line.find("fall_transition")
            if fall_pos != -1:
                for constraint_line in lib_fp:
                    if constraint_line.find("}") != -1:
                        break

                    if constraint_line.find('values') != -1:
                        val_set = set()
                        val_set = populate_set(
                            constraint_line, val_set
                        )

                        for val_line in lib_fp:
                            if val_line.find(");") != -1:
                                val_set = populate_set(val_line, val_set)
                                break

                            val_set = populate_set(val_line, val_set)
                        rising_edge_fall_tran_val.add(
                            sorted(val_set).pop()
                            #next(iter(sorted(val_set)))
                        )
                        break
                break

    return rising_edge_cell_rise_val, rising_edge_cell_fall_val, rising_edge_rise_tran_val, rising_edge_fall_tran_val

# =============================================================================

def populate_set(line, val_set):
    """
    Collects values and put it in a set
    """
    pos = line.find("\"")
    pos1 = line.rfind("\"")
    sub = line[pos+1:pos1]
    val_list = sub.split(',')
    for val in val_list:
        val_set.add(float(val.strip()))

    return val_set



# =============================================================================

if __name__ == '__main__':
    main()
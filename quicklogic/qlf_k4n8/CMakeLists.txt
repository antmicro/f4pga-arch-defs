get_filename_component(FAMILY ${CMAKE_CURRENT_SOURCE_DIR} NAME)

add_subdirectory(techmap)

# Common VPR args for the qlf_k4n8 architecture
#
# There is no modeling of clock routing. The global clock network is implicit
# and non-configurable in the hardware so there is no reason why VPR should
# consider it. Each tile has a separate clock input multiplexer. Its selection
# is established during the VPR packing stage.
#
# TODO: The LUT buffer absorption is currently turned off as the repacker
#       inserts some LUT buffers to allow maintaining the top level IO ports.
#       With the LUT buffer absorption enabled, the patched netlist and blif
#       out of the repacker will be out of sync, causing a VPR failure. The solution
#       likely requires a revision of the repacker code to correctly and robustly
#       handle the top level I/Os.
set(VPR_ARCH_ARGS "\
    --clock_modeling ideal \
    --place_delta_delay_matrix_calculation_method dijkstra \
    --place_delay_model delta_override \
    --router_lookahead extended_map \
    --allow_dangling_combinational_nodes on \
    --absorb_buffer_luts off "
)

# copy yosys cells_sim.v to techmap directory and comment out includes
set(YOSYS_CELLS_SIM ${YOSYS_DATADIR}/quicklogic/${FAMILY_NAME}/cells_sim.v)
set(YOSYS_CELLS_SIM_LOCAL techmap/yosys_cells_sim.v)
get_file_target(YOSYS_CELLS_SIM_TARGET ${YOSYS_CELLS_SIM})
if (NOT TARGET ${YOSYS_CELLS_SIM_TARGET})
  add_file_target(FILE ${YOSYS_CELLS_SIM} ABSOLUTE)
endif ()

SET(SED_ARGS -i \"s\/\^\\\`include\/\\\/\\\/\\\`include\/\" ${YOSYS_CELLS_SIM_LOCAL})
add_custom_command(
  OUTPUT ${YOSYS_CELLS_SIM_LOCAL}
  COMMAND ${CMAKE_COMMAND} -E copy
	  ${YOSYS_CELLS_SIM}
	  ${YOSYS_CELLS_SIM_LOCAL}
  COMMAND sed ${SED_ARGS}
  DEPENDS ${YOSYS_CELLS_SIM_TARGET}
)
add_file_target(FILE ${YOSYS_CELLS_SIM_LOCAL} GENERATED)

# Define the architecture
quicklogic_define_qlf_arch(
  FAMILY   ${FAMILY}
  ARCH     qlf_k4n8
  VPR_ARGS ${VPR_ARCH_ARGS}

  ROUTE_CHAN_WIDTH 10 # Will be overriden by each device
)

add_subdirectory(devices)
include(boards.cmake)

add_subdirectory(tests)

# Define toolchain installation target
set(FAMILY_DIR ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/${FAMILY})

define_ql_toolchain_target(
  FAMILY ${FAMILY}
  ARCH qlf_k4n8
  ROUTE_CHAN_WIDTH 100
  CELLS_SIM ${FAMILY_DIR}/techmap/cells_sim.v
  VPR_ARCH_ARGS ${VPR_ARCH_ARGS}
  SYNTH_SCRIPT ${FAMILY_DIR}/yosys/synth.tcl
  CONV_SCRIPT ${FAMILY_DIR}/yosys/conv.tcl
)

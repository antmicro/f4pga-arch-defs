set(IO_MAX  ${QL_DESIGNS_DIR}/io_max/io_max.v)
set(IO1_DEMUX  ${QL_DESIGNS_DIR}/io_max/demux.v)
set(IO1_MUX  ${QL_DESIGNS_DIR}/io_max/mux.v)
set(QLF_K4N8_UMC22 qlf_k4n8-qlf_k4n8_umc22_slow)

set(ROUTE_LOG ${CMAKE_CURRENT_BINARY_DIR}/io_max_test-umc22-adder/qlf_k4n8-${QLF_K4N8_UMC22}-virt-${QLF_K4N8_UMC22}-${QLF_K4N8_UMC22}/route.log)

add_file_target(FILE ${IO_MAX} SCANNER_TYPE verilog)
add_file_target(FILE ${IO1_DEMUX} SCANNER_TYPE verilog)
add_file_target(FILE ${IO1_MUX} SCANNER_TYPE verilog)


add_fpga_target(
  NAME io_max_test-umc22-adder
  TOP io_max
  BOARD qlf_k4n8-qlf_k4n8_umc22_slow_board
  SOURCES ${IO_MAX} ${IO1_DEMUX} ${IO1_MUX}
  EXPLICIT_ADD_FILE_TARGET
  )


add_dependencies(all_qlf_k4n8_tests_adder    io_max_verify)

add_custom_target(
  io_max_verify
  COMMAND egrep -q -i "iopad \+: 1034" ${ROUTE_LOG}
  DEPENDS io_max_test-umc22-adder_route
  )

set(IO_MAX  ${QL_DESIGNS_DIR}/io_max/io_max.v)
set(IO1_DEMUX  ${QL_DESIGNS_DIR}/io_max/demux.v)
set(IO1_MUX  ${QL_DESIGNS_DIR}/io_max/mux.v)
set(QLF_K4N8_UMC22 qlf_k6n10-qlf_k6n10_gf12)

set(ROUTE_LOG ${CMAKE_CURRENT_BINARY_DIR}/io_max_test-gf12-adder/qlf_k6n10-${QLF_K4N8_UMC22}-virt-${QLF_K4N8_UMC22}-${QLF_K4N8_UMC22}/route.log)

add_fpga_target(
  NAME io_max_test-gf12-adder
  TOP io_max
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${IO_MAX} ${IO1_DEMUX} ${IO1_MUX}
  EXPLICIT_ADD_FILE_TARGET
  )


add_dependencies(all_qlf_k6n10_tests_adder    io_max_2_verify)

add_custom_target(
  io_max_2_verify
  COMMAND egrep -q -i "io \+: 1034" ${ROUTE_LOG}
  DEPENDS io_max_test-gf12-adder_route
  )

set(IO_REG_MAX  ${QL_DESIGNS_DIR}/io_reg_max/io_reg_max.v)
set(IO_DEMUX  ${QL_DESIGNS_DIR}/io_reg_max/demux.v)
set(IO_MUX  ${QL_DESIGNS_DIR}/io_reg_max/mux.v)
set(QLF_K4N8_UMC22 qlf_k6n10-qlf_k6n10_gf12)

set(ROUTE_LOG ${CMAKE_CURRENT_BINARY_DIR}/io_reg_max_test-gf12-adder/qlf_k6n10-${QLF_K4N8_UMC22}-virt-${QLF_K4N8_UMC22}-${QLF_K4N8_UMC22}/route.log)

add_fpga_target(
  NAME io_reg_max_test-gf12-adder
  TOP io_reg_max
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${IO_REG_MAX} ${IO_DEMUX} ${IO_MUX}
  EXPLICIT_ADD_FILE_TARGET
  )


add_dependencies(all_qlf_k6n10_tests_adder    io_reg_max_2_verify)

add_custom_target(
  io_reg_max_2_verify
  COMMAND egrep -q -i "io \+: 1034" ${ROUTE_LOG}
  COMMAND egrep -q -i "fle \+: 926" ${ROUTE_LOG}
  DEPENDS io_reg_max_test-gf12-adder_route
  )

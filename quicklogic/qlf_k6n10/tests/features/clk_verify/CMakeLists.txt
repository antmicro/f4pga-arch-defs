set(CURR_DIR ${QL_DESIGNS_DIR}/dct_mac)
set(QLF_K6N10_GF12 qlf_k6n10-qlf_k6n10_gf12)

#output files
set(ROUTE_LOG ${CMAKE_CURRENT_BINARY_DIR}/dct_mac_test3-gf12-adder/qlf_k6n10-${QLF_K6N10_GF12}-virt-${QLF_K6N10_GF12}-${QLF_K6N10_GF12}/route.log)

#add_file_target(FILE ${CURR_DIR}/dct_mac.v SCANNER_TYPE verilog)

add_fpga_target(
  NAME dct_mac_test3-gf12-adder
  TOP dct_mac
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${CURR_DIR}/dct_mac.v
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_qlf_k6n10_tests_adder clk0_verify)

add_custom_target(
  clk0_verify
  COMMAND egrep -q "Fmax: [6-9][0-9]." ${ROUTE_LOG} 
  DEPENDS dct_mac_test3-gf12-adder_route
  )

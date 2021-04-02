set(CURR_DIR ${QL_DESIGNS_DIR}/dct_mac)
set(QLF_K4N8_UMC22 qlf_k4n8-qlf_k4n8_umc22_slow)

#output files
set(ROUTE_LOG ${CMAKE_CURRENT_BINARY_DIR}/dct_mac_test3-umc22-adder/qlf_k4n8-${QLF_K4N8_UMC22}-virt-${QLF_K4N8_UMC22}-${QLF_K4N8_UMC22}/route.log)

add_file_target(FILE ${CURR_DIR}/dct_mac.v SCANNER_TYPE verilog)

add_fpga_target(
  NAME dct_mac_test3-umc22-adder
  TOP dct_mac
  BOARD qlf_k4n8-qlf_k4n8_umc22_slow_board
  SOURCES ${CURR_DIR}/dct_mac.v
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_qlf_k4n8_tests_adder clk_verify)

add_custom_target(
  clk_verify
  COMMAND egrep -q "Fmax: [6-9][0-9]." ${ROUTE_LOG} 
  DEPENDS dct_mac_test3-umc22-adder_bit
  )

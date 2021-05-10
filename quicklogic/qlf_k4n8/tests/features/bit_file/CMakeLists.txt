set(CURR_DIR ${QL_DESIGNS_DIR}/dct_mac)
set(QLF_K4N8_UMC22 qlf_k4n8-qlf_k4n8_umc22)

#Golden and output files
set(GOLDEN_BITSTREAM ${CMAKE_CURRENT_SOURCE_DIR}/dct_mac_golden.bit)
set(BITSTREAM ${CMAKE_CURRENT_BINARY_DIR}/dct_mac_test-umc22-adder/qlf_k4n8-${QLF_K4N8_UMC22}-virt-${QLF_K4N8_UMC22}-${QLF_K4N8_UMC22}/dct_mac.bit)

add_file_target(FILE ${CURR_DIR}/dct_mac.v SCANNER_TYPE verilog)

add_fpga_target(
  NAME dct_mac_test-umc22-adder
  TOP dct_mac
  BOARD qlf_k4n8-qlf_k4n8_umc22_board
  SOURCES ${CURR_DIR}/dct_mac.v
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_qlf_k4n8_tests_adder bit_verify)
add_custom_target(
  bit_verify
  COMMAND diff ${BITSTREAM} ${GOLDEN_BITSTREAM}
  DEPENDS dct_mac_test-umc22-adder_bit
  )

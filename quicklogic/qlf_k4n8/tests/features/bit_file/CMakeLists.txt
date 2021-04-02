set(AND2_OR ${QL_DESIGNS_DIR}/and2_or2/and2_or2.v)
set(QLF_K4N8_UMC22 qlf_k4n8-qlf_k4n8_umc22_slow)

set(BITSTREAM ${CMAKE_CURRENT_BINARY_DIR}/and2_or2_test4-umc22-adder/qlf_k4n8-${QLF_K4N8_UMC22}-virt-${QLF_K4N8_UMC22}-${QLF_K4N8_UMC22}/and2_or2.bit)

add_file_target(FILE ${AND2_OR} SCANNER_TYPE verilog)

add_fpga_target(
  NAME and2_or2_test4-umc22-adder
  TOP and2_or2
  BOARD qlf_k4n8-qlf_k4n8_umc22_slow_board
  SOURCES ${AND2_OR}
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_qlf_k4n8_tests_adder bit_verify)
add_custom_target(
  bit_verify
  COMMAND wc -l <${BITSTREAM} | grep -q 25572
  DEPENDS and2_or2_test4-umc22-adder_bit
  )

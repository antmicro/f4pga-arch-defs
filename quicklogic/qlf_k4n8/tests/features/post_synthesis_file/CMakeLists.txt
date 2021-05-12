set(COUNTER_16BIT ${QL_DESIGNS_DIR}/counter_16bit/counter_16bit.v)
set(QLF_K4N8_UMC22 qlf_k4n8-qlf_k4n8_umc22)

#Golden and output files
set(GOLDEN_BITSTREAM ${CMAKE_CURRENT_SOURCE_DIR}/top_post_synthesis_golden.v)
set(BITSTREAM ${CMAKE_CURRENT_BINARY_DIR}/counter_16bit_test2-umc22-adder/qlf_k4n8-${QLF_K4N8_UMC22}-virt-${QLF_K4N8_UMC22}-${QLF_K4N8_UMC22}/top_post_synthesis.v)

#add_file_target(FILE ${CURR_DIR}/counter_16bit.v SCANNER_TYPE verilog)

add_fpga_target(
  NAME counter_16bit_test2-umc22-adder
  TOP top
  BOARD qlf_k4n8-qlf_k4n8_umc22_board
  SOURCES ${COUNTER_16BIT}
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_qlf_k4n8_tests_adder post_synthesis_verify)
#add_dependencies(post_synthesis_verify counter_16bit_test2-umc22-adder_analysis)

add_custom_target(
  post_synthesis_verify
  COMMAND diff ${BITSTREAM} ${GOLDEN_BITSTREAM}
  DEPENDS counter_16bit_test2-umc22-adder_analysis
  )

set(JPEG_QNR ${QL_DESIGNS_DIR}/jpeg_qnr/jpeg_qnr.v)
set(FILE1 ${QL_DESIGNS_DIR}/jpeg_qnr/div_su.v)
set(FILE2 ${QL_DESIGNS_DIR}/jpeg_qnr/div_uu.v)
#add_file_target(FILE ${CURR_DIR}/div_su.v SCANNER_TYPE verilog)
#add_file_target(FILE ${CURR_DIR}/div_uu.v SCANNER_TYPE verilog)

add_fpga_target(
  NAME jpeg_qnr_test-gf12-no-adder
  TOP jpeg_qnr
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${JPEG_QNR} ${FILE1} ${FILE2} 
  EXPLICIT_ADD_FILE_TARGET
  DEFINES SYNTH_OPTS=-no_adder
  )

add_fpga_target(
  NAME jpeg_qnr_test-gf12-adder
  TOP jpeg_qnr
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${JPEG_QNR} ${FILE1} ${FILE2} 
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_qlf_k6n10_tests_no_adder jpeg_qnr_test-gf12-no-adder_route)
add_dependencies(all_qlf_k6n10_tests_adder    jpeg_qnr_test-gf12-adder_route)

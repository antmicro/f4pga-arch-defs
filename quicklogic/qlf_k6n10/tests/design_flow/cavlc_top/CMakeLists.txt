set(CAVLC_TOP ${QL_DESIGNS_DIR}/cavlc_top/cavlc_top.v)
set(FILE1 ${QL_DESIGNS_DIR}/cavlc_top/defines.v)
set(FILE2 ${QL_DESIGNS_DIR}/cavlc_top/cavlc_fsm.v)
set(FILE3 ${QL_DESIGNS_DIR}/cavlc_top/cavlc_len_gen.v)
set(FILE4 ${QL_DESIGNS_DIR}/cavlc_top/cavlc_read_levels.v)
set(FILE5 ${QL_DESIGNS_DIR}/cavlc_top/cavlc_read_run_befores.v)
set(FILE6 ${QL_DESIGNS_DIR}/cavlc_top/cavlc_read_total_coeffs.v)
set(FILE7 ${QL_DESIGNS_DIR}/cavlc_top/cavlc_read_total_zeros.v)

add_fpga_target(
  NAME cavlc_top_test-gf12-no-adder
  TOP cavlc_top
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${CAVLC_TOP} ${FILE1} ${FILE2} ${FILE3} ${FILE4} ${FILE5} ${FILE6} ${FILE7}
  EXPLICIT_ADD_FILE_TARGET
  DEFINES SYNTH_OPTS=-no_adder
  )

add_fpga_target(
  NAME cavlc_top_test-gf12-adder
  TOP cavlc_top
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${CAVLC_TOP} ${FILE1} ${FILE2} ${FILE3} ${FILE4} ${FILE5} ${FILE6} ${FILE7}
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_qlf_k6n10_tests_no_adder cavlc_top_test-gf12-no-adder_route)
add_dependencies(all_qlf_k6n10_tests_adder    cavlc_top_test-gf12-adder_route)

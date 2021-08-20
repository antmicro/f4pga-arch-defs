set(SHIFT_576 ${QL_DESIGNS_DIR}/shift_reg_576/shift_reg_576.v)

add_fpga_target(
  NAME shift_reg_576_test-gf12-no-adder
  TOP shift_reg_576
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${SHIFT_576}
  EXPLICIT_ADD_FILE_TARGET
  DEFINES SYNTH_OPTS=-no_adder
  )

add_fpga_target(
  NAME shift_reg_576_test-gf12-adder
  TOP shift_reg_576
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${SHIFT_576}
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_qlf_k6n10_tests_no_adder shift_reg_576_test-gf12-no-adder_route)
add_dependencies(all_qlf_k6n10_tests_adder    shift_reg_576_test-gf12-adder_route)

set(IO_REG_TC1 ${QL_DESIGNS_DIR}/io_reg_tc1/io_reg_tc1.v)
set(FILE1 ${QL_DESIGNS_DIR}/io_reg_tc1/demux.v)
set(FILE2 ${QL_DESIGNS_DIR}/io_reg_tc1/mux.v)


add_fpga_target(
  NAME io_reg_tc1_test-gf12-no-adder
  TOP io_reg_tc1
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${IO_REG_TC1} ${FILE1} ${FILE2}
  EXPLICIT_ADD_FILE_TARGET
  DEFINES SYNTH_OPTS=-no_adder
  )

add_fpga_target(
  NAME io_reg_tc1_test-gf12-adder
  TOP io_reg_tc1
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${IO_REG_TC1} ${FILE1} ${FILE2}
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_qlf_k6n10_tests_no_adder io_reg_tc1_test-gf12-no-adder_route)
add_dependencies(all_qlf_k6n10_tests_adder    io_reg_tc1_test-gf12-adder_route)

set(IO_TC1 ${QL_DESIGNS_DIR}/io_tc1/io_tc1.v)
set(IO_TC1_DEMUX ${QL_DESIGNS_DIR}/io_tc1/demux.v)
set(IO_TC1_MUX ${QL_DESIGNS_DIR}/io_tc1/mux.v)


add_fpga_target(
  NAME io_tc1_test-gf12-no-adder
  TOP io_tc1
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${IO_TC1} ${IO_TC1_DEMUX} ${IO_TC1_MUX}
  EXPLICIT_ADD_FILE_TARGET
  DEFINES SYNTH_OPTS=-no_adder
  )

add_fpga_target(
  NAME io_tc1_test-gf12-adder
  TOP io_tc1
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${IO_TC1} ${IO_TC1_DEMUX} ${IO_TC1_MUX}
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_qlf_k6n10_tests_adder    io_tc1_test-gf12-adder_route)

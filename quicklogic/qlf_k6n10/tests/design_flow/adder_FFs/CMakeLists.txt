set(ADD_FFs ${QL_DESIGNS_DIR}/adder_FFs/adder_FFs.v)

add_fpga_target(
  NAME adder_FFs_test-gf12-no-adder
  TOP adder_FFs
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${ADD_FFs}
  EXPLICIT_ADD_FILE_TARGET
  DEFINES SYNTH_OPTS=-no_adder
  )

add_fpga_target(
  NAME adder_FFs_test-gf12-adder
  TOP adder_FFs
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${ADD_FFs}
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_qlf_k6n10_tests_no_adder adder_FFs_test-gf12-no-adder_route)
add_dependencies(all_qlf_k6n10_tests_adder    adder_FFs_test-gf12-adder_route)

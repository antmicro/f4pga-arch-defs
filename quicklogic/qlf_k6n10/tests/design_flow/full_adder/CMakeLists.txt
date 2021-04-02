set(FULL_ADD ${QL_DESIGNS_DIR}/full_adder/full_adder.v)

add_fpga_target(
  NAME full_adder_test-gf12-no-adder
  TOP full_adder
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${FULL_ADD}
  EXPLICIT_ADD_FILE_TARGET
  DEFINES SYNTH_OPTS=-no_adder
  )

add_fpga_target(
  NAME full_adder_test-gf12-adder
  TOP full_adder
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${FULL_ADD}
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_qlf_k6n10_tests_no_adder full_adder_test-gf12-no-adder_route)
add_dependencies(all_qlf_k6n10_tests_adder    full_adder_test-gf12-adder_route)

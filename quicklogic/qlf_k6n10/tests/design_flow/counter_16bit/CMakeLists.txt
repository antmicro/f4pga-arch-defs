set(COUNT_16BIT ${QL_DESIGNS_DIR}/counter_16bit/counter_16bit.v)

add_fpga_target(
  NAME counter_16bit_test-gf12-no-adder
  TOP top
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${COUNT_16BIT}
  EXPLICIT_ADD_FILE_TARGET
  DEFINES SYNTH_OPTS=-no_adder
)

add_fpga_target(
  NAME counter_16bit_test-gf12-adder
  TOP top
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${COUNT_16BIT}
  EXPLICIT_ADD_FILE_TARGET
)

add_dependencies(all_qlf_k6n10_tests_no_adder counter_16bit_test-gf12-no-adder_route)
add_dependencies(all_qlf_k6n10_tests_adder    counter_16bit_test-gf12-adder_route)

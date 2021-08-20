set(COUNTER_4CLK ${QL_DESIGNS_DIR}/counter_4clk/counter_4clk.v)

add_fpga_target(
  NAME counter_4clk-gf12-no-adder
  TOP top
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${COUNTER_4CLK}
  EXPLICIT_ADD_FILE_TARGET
  DEFINES SYNTH_OPTS=-no_adder
)

add_fpga_target(
  NAME counter_4clk-gf12-adder
  TOP top
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${COUNTER_4CLK}
  EXPLICIT_ADD_FILE_TARGET
)

add_dependencies(all_qlf_k6n10_tests_no_adder counter_4clk-gf12-no-adder_route)
add_dependencies(all_qlf_k6n10_tests_adder    counter_4clk-gf12-adder_route)

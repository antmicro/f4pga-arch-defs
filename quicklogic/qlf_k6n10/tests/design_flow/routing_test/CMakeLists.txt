set(ROUTE_TEST ${QL_DESIGNS_DIR}/routing_test/routing_test.v)

add_fpga_target(
  NAME routing_test_test-gf12-no-adder
  TOP routing_test
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${ROUTE_TEST}
  EXPLICIT_ADD_FILE_TARGET
  DEFINES SYNTH_OPTS=-no_adder
  )

add_fpga_target(
  NAME routing_test_test-gf12-adder
  TOP routing_test
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${ROUTE_TEST}
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_qlf_k6n10_tests_no_adder routing_test_test-gf12-no-adder_route)
add_dependencies(all_qlf_k6n10_tests_adder    routing_test_test-gf12-adder_route)

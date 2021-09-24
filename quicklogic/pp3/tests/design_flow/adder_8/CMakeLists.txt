set(DESIGN_DIR ${QL_DESIGNS_DIR}/adder_8)

add_fpga_target(
  NAME adder_8-ql-jimbob4-pp3
  TOP adder_8
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/adder_8.v
  AUTO_ADD_FILE_TARGET

  ASSERT_USAGE PB-BIDIR=26,PB-LOGIC<=8
  ASSERT_TIMING fmax>=14.0
)

add_dependencies(all_ql_tests_bit   adder_8-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v adder_8-ql-jimbob4-pp3_bit_v)

add_dependencies(all_ql_tests_regression adder_8-ql-jimbob4-pp3_assert_usage)
add_dependencies(all_ql_tests_regression adder_8-ql-jimbob4-pp3_assert_timing)

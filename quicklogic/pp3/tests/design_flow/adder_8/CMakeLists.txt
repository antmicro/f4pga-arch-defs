set(DESIGN_DIR ${QL_DESIGNS_DIR}/adder_8)
add_file_target(FILE pd64.pcf)

# To much IO required
add_fpga_target(
  NAME adder_8-ql-pd64
  TOP adder_8
  BOARD pd64
  SOURCES
    ${DESIGN_DIR}/adder_8.v
  INPUT_IO_FILE pd64.pcf
  AUTO_ADD_FILE_TARGET

  ASSERT_USAGE PB-BIDIR=26,PB-LOGIC<=8
  ASSERT_TIMING fmax>=14.0
)

add_dependencies(all_ql_tests_bit   adder_8-ql-pd64_bit)
add_dependencies(all_ql_tests_bit_v adder_8-ql-pd64_bit_v)

add_dependencies(all_ql_tests_regression adder_8-ql-pd64_assert_usage)
add_dependencies(all_ql_tests_regression adder_8-ql-pd64_assert_timing)

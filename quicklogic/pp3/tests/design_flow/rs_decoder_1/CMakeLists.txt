set(DESIGN_DIR ${QL_DESIGNS_DIR}/rs_decoder_1)

add_fpga_target(
  NAME rs_decoder_1-ql-jimbob4-pp3
  TOP rs_decoder_1
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/rs_decoder_1.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET

  ASSERT_USAGE PB-CLOCK=1,PB-GMUX=1,PB-LOGIC<=27
  ASSERT_TIMING fmax>=25.0
)

add_dependencies(all_ql_tests_bit   rs_decoder_1-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v rs_decoder_1-ql-jimbob4-pp3_bit_v)

add_dependencies(all_ql_tests_regression rs_decoder_1-ql-jimbob4-pp3_assert_usage)
add_dependencies(all_ql_tests_regression rs_decoder_1-ql-jimbob4-pp3_assert_timing)

set(DESIGN_DIR ${QL_DESIGNS_DIR}/counter_16bit)

add_fpga_target(
  NAME counter_16bit-ql-jimbob4-pp3
  TOP top
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/counter_16bit.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET

  ASSERT_USAGE PB-CLOCK=1,PB-GMUX=1,PB-LOGIC<=18
  ASSERT_TIMING fmax>=20.0
)

add_dependencies(all_ql_tests_bit   counter_16bit-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v counter_16bit-ql-jimbob4-pp3_bit_v)

add_dependencies(all_ql_tests_regression counter_16bit-ql-jimbob4-pp3_assert_usage)
add_dependencies(all_ql_tests_regression counter_16bit-ql-jimbob4-pp3_assert_timing)

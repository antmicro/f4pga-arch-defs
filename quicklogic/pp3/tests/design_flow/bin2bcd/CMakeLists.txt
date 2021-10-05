set(DESIGN_DIR ${QL_DESIGNS_DIR}/bin2bcd)

add_fpga_target(
  NAME bin2bcd-ql-jimbob4-pp3
  TOP bin2bcd
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/bin2bcd.v
  AUTO_ADD_FILE_TARGET

  ASSERT_USAGE PB-BIDIR=20,PB-LOGIC<=17
  ASSERT_TIMING fmax>=13.0
)

add_dependencies(all_ql_tests_bit   bin2bcd-ql-jimbob4-pp3_bit)
#add_dependencies(all_ql_tests_bit_v bin2bcd-ql-jimbob4-pp3_bit_v) # FIXME: PCF file is required by the BIT_TO_V_CMD

add_dependencies(all_ql_tests_regression bin2bcd-ql-jimbob4-pp3_assert_usage)
add_dependencies(all_ql_tests_regression bin2bcd-ql-jimbob4-pp3_assert_timing)

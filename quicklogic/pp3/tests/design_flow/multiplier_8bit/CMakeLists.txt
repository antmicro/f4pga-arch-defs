set(DESIGN_DIR ${QL_DESIGNS_DIR}/multiplier_8bit)

add_fpga_target(
  NAME multiplier_8bit-ql-jimbob4-pp3
  TOP multiplier_8bit
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/multiplier_8bit.v
  AUTO_ADD_FILE_TARGET

  ASSERT_USAGE PB-LOGIC<=105
)

add_dependencies(all_ql_tests_bit   multiplier_8bit-ql-jimbob4-pp3_bit)
#add_dependencies(all_ql_tests_bit_v multiplier_8bit-ql-jimbob4-pp3_bit_v) # FIXME: PCF file is required by the BIT_TO_V_CMD

add_dependencies(all_ql_tests_regression multiplier_8bit-ql-jimbob4-pp3_assert_usage)

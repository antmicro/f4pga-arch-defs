set(DESIGN_DIR ${QL_DESIGNS_DIR}/unsigned_mult_50)

add_fpga_target(
  NAME unsigned_mult_50-ql-jimbob4-pp3
  TOP top
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/unsigned_mult_50.v
  AUTO_ADD_FILE_TARGET

  ASSERT_USAGE PB-LOGIC<=908
)

add_dependencies(all_pp3_tests_bit   unsigned_mult_50-ql-jimbob4-pp3_bit)
#add_dependencies(all_pp3_tests_bit_v unsigned_mult_50-ql-jimbob4-pp3_bit_v)	# FIXME: PCF file is required by the BIT_TO_V_CMD

add_dependencies(all_pp3_tests_regression unsigned_mult_50-ql-jimbob4-pp3_assert_usage)

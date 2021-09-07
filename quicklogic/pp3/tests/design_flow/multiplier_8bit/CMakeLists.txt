set(DESIGN_DIR ${QL_DESIGNS_DIR}/multiplier_8bit)

add_fpga_target(
  NAME multiplier_8bit-ql-jimbob4-pp3
  TOP multiplier_8bit
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/multiplier_8bit.v
  AUTO_ADD_FILE_TARGET
)

add_dependencies(all_ql_tests_bit   multiplier_8bit-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v multiplier_8bit-ql-jimbob4-pp3_bit_v)

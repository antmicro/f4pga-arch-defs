set(DESIGN_DIR ${QL_DESIGNS_DIR}/unsigned_mult_80)

add_fpga_target(
  NAME unsigned_mult_80-ql-jimbob4-pp3
  TOP top
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/unsigned_mult_80.v
  AUTO_ADD_FILE_TARGET
)

add_dependencies(all_ql_tests_bit   unsigned_mult_80-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v unsigned_mult_80-ql-jimbob4-pp3_bit_v)

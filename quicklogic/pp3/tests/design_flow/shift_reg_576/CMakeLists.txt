set(DESIGN_DIR ${QL_DESIGNS_DIR}/shift_reg_576)

add_fpga_target(
  NAME shift_reg_576-ql-jimbob4-pp3
  TOP shift_reg_576
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/shift_reg_576.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET
)

add_dependencies(all_ql_tests_bit   shift_reg_576-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v shift_reg_576-ql-jimbob4-pp3_bit_v)

set(DESIGN_DIR ${QL_DESIGNS_DIR}/top_120_13)

add_fpga_target(
  NAME top_120_13-ql-jimbob4-pp3
  TOP top_120_13
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/top_120_13.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET
)

add_dependencies(all_ql_tests_bit   top_120_13-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v top_120_13-ql-jimbob4-pp3_bit_v)

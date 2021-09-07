set(DESIGN_DIR ${QL_DESIGNS_DIR}/bin2bcd)

add_fpga_target(
  NAME bin2bcd-ql-jimbob4-pp3
  TOP bin2bcd
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/bin2bcd.v
  AUTO_ADD_FILE_TARGET
)

add_dependencies(all_ql_tests_bit   bin2bcd-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v bin2bcd-ql-jimbob4-pp3_bit_v)

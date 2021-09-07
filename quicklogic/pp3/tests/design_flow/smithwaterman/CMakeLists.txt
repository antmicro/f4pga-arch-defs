set(DESIGN_DIR ${QL_DESIGNS_DIR}/smithwaterman)

add_fpga_target(
  NAME smithwaterman-ql-jimbob4-pp3
  TOP smithwaterman
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/smithwaterman.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET
)

add_dependencies(all_ql_tests_bit   smithwaterman-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v smithwaterman-ql-jimbob4-pp3_bit_v)

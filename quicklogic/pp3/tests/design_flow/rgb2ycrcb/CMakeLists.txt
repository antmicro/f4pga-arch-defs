set(DESIGN_DIR ${QL_DESIGNS_DIR}/rgb2ycrcb)

add_fpga_target(
  NAME rgb2ycrcb-ql-jimbob4-pp3
  TOP top
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/rgb2ycrcb.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET
)

add_dependencies(all_ql_tests_bit   rgb2ycrcb-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v rgb2ycrcb-ql-jimbob4-pp3_bit_v)

set(DESIGN_DIR ${QL_DESIGNS_DIR}/jpeg_qnr)

add_fpga_target(
  NAME jpeg_qnr-ql-jimbob4-pp3
  TOP jpeg_qnr
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/div_su.v
    ${DESIGN_DIR}/div_uu.v
    ${DESIGN_DIR}/jpeg_qnr.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET
)

add_dependencies(all_ql_tests_bit   jpeg_qnr-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v jpeg_qnr-ql-jimbob4-pp3_bit_v)

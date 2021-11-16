set(DESIGN_DIR ${QL_DESIGNS_DIR}/sha_top)

add_fpga_target(
  NAME sha_top-ql-jimbob4-pp3
  TOP top
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/sha512.v
    ${DESIGN_DIR}/sha_top.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET
)

add_dependencies(all_pp3_tests_bit   sha_top-ql-jimbob4-pp3_bit)
add_dependencies(all_pp3_tests_bit_v sha_top-ql-jimbob4-pp3_bit_v)

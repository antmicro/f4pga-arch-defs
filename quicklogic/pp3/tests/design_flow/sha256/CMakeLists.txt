set(DESIGN_DIR ${QL_DESIGNS_DIR}/sha256)

add_fpga_target(
  NAME sha256-ql-jimbob4-pp3
  TOP sha256
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/sha256.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET
)

add_dependencies(all_ql_tests_bit   sha256-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v sha256-ql-jimbob4-pp3_bit_v)

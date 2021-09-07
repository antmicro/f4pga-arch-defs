set(DESIGN_DIR ${QL_DESIGNS_DIR}/iir)

add_fpga_target(
  NAME iir-ql-jimbob4-pp3
  TOP iir
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/iir.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET
)

add_dependencies(all_ql_tests_bit   iir-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v iir-ql-jimbob4-pp3_bit_v)

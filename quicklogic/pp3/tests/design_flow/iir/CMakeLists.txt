set(DESIGN_DIR ${QL_DESIGNS_DIR}/iir)

add_fpga_target(
  NAME iir-ql-jimbob4-pp3
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/iir.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET

  ASSERT_USAGE PB-CLOCK=2,PB-GMUX=2,PB-LOGIC<=878
)

add_dependencies(all_ql_tests_bit   iir-ql-jimbob4-pp3_bit)
#add_dependencies(all_ql_tests_bit_v iir-ql-jimbob4-pp3_bit_v)	# FIXME: List of connection types is empty (should have 1 element)

add_dependencies(all_ql_tests_regression iir-ql-jimbob4-pp3_assert_usage)

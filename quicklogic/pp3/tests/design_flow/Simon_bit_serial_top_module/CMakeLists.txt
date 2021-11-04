set(DESIGN_DIR ${QL_DESIGNS_DIR}/Simon_bit_serial_top_module)

add_fpga_target(
  NAME Simon_bit_serial_top_module-ql-jimbob4-pp3
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/Simon_bit_serial_datapath_FPGA.v
    ${DESIGN_DIR}/Simon_bit_serial_key_expansion_FPGA.v
    ${DESIGN_DIR}/Simon_bit_serial_top_module.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET

  ASSERT_USAGE PB-CLOCK=1,PB-GMUX=1,PB-LOGIC<=283
  ASSERT_TIMING fmax>=20.0
)

add_dependencies(all_pp3_tests_bit   Simon_bit_serial_top_module-ql-jimbob4-pp3_bit)
add_dependencies(all_pp3_tests_bit_v Simon_bit_serial_top_module-ql-jimbob4-pp3_bit_v)

add_dependencies(all_pp3_tests_regression Simon_bit_serial_top_module-ql-jimbob4-pp3_assert_usage)
add_dependencies(all_pp3_tests_regression Simon_bit_serial_top_module-ql-jimbob4-pp3_assert_timing)


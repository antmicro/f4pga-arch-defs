set(DESIGN_DIR ${QL_DESIGNS_DIR}/Simon_bit_serial_top_module)

add_fpga_target(
  NAME Simon_bit_serial_top_module-ql-jimbob4-pp3
  TOP Simon_bit_serial_top
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/Simon_bit_serial_datapath_FPGA.v
    ${DESIGN_DIR}/Simon_bit_serial_key_expansion_FPGA.v
    ${DESIGN_DIR}/Simon_bit_serial_top_module.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET
)

add_dependencies(all_ql_tests_bit   Simon_bit_serial_top_module-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v Simon_bit_serial_top_module-ql-jimbob4-pp3_bit_v)

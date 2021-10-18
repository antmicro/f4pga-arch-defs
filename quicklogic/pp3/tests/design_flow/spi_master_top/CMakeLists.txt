set(DESIGN_DIR ${QL_DESIGNS_DIR}/spi_master_top)

add_fpga_target(
  NAME spi_master_top-ql-jimbob4-pp3
  TOP spi_master_top
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/baud_generator.v
    ${DESIGN_DIR}/ql_clkgate_x4.v
    ${DESIGN_DIR}/ql_mux2_x2.v
    ${DESIGN_DIR}/registers.v
    ${DESIGN_DIR}/serializer_deserializer.v
    ${DESIGN_DIR}/spi_master_top.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET

  ASSERT_USAGE PB-CLOCK=2,PB-GMUX=2,PB-LOGIC<=136
)

add_dependencies(all_ql_tests_bit   spi_master_top-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v spi_master_top-ql-jimbob4-pp3_bit_v)

add_dependencies(all_ql_tests_regression spi_master_top-ql-jimbob4-pp3_assert_usage)

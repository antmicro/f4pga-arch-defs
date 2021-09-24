set(DESIGN_DIR ${QL_DESIGNS_DIR}/sdio_client_top)

add_fpga_target(
  NAME sdio_client_top-ql-jimbob4-pp3
  TOP top
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/af512x9_512x9.v
    ${DESIGN_DIR}/cmd_control.v
    ${DESIGN_DIR}/crc16.v
    ${DESIGN_DIR}/crc7.v
    ${DESIGN_DIR}/dat0_line.v
    ${DESIGN_DIR}/dat123_line.v
    ${DESIGN_DIR}/dat1_line.v
    ${DESIGN_DIR}/dat23_line.v
    ${DESIGN_DIR}/dat_control.v
    ${DESIGN_DIR}/dat_fifo.v
    ${DESIGN_DIR}/function1.v
    ${DESIGN_DIR}/function2.v
    ${DESIGN_DIR}/registers.v
    ${DESIGN_DIR}/sdio_client_top.v
    ${DESIGN_DIR}/spi_cmd_datin_line.v
    ${DESIGN_DIR}/spi_crc16.v
    ${DESIGN_DIR}/spi_dat_control.v
    ${DESIGN_DIR}/sync.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET

  ASSERT_USAGE PB-CLOCK=1,PB-GMUX=1,PB-LOGIC<=595
)

add_dependencies(all_ql_tests_bit   sdio_client_top-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v sdio_client_top-ql-jimbob4-pp3_bit_v)

add_dependencies(all_ql_tests_regression sdio_client_top-ql-jimbob4-pp3_assert_usage)

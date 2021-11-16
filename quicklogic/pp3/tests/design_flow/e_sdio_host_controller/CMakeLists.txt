set(DESIGN_DIR ${QL_DESIGNS_DIR}/e_sdio_host_controller)

add_fpga_target(
  NAME e_sdio_host_controller-ql-jimbob4-pp3
  TOP top
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/af256x18_512x9.v
    ${DESIGN_DIR}/af512x9_256x18.v
    ${DESIGN_DIR}/bipadoff_pp.v
    ${DESIGN_DIR}/e_Card_Detect.v
    ${DESIGN_DIR}/e_clock_mng_pp.v
    ${DESIGN_DIR}/e_cmd_control.v
    ${DESIGN_DIR}/e_crc16.v
    ${DESIGN_DIR}/e_dat0_line.v
    ${DESIGN_DIR}/e_dat123_line.v
    ${DESIGN_DIR}/e_dat_control.v
    ${DESIGN_DIR}/e_registers.v
    ${DESIGN_DIR}/e_rx_fifo.v
    ${DESIGN_DIR}/e_sdio_host_controller.v
    ${DESIGN_DIR}/e_sync.v
    ${DESIGN_DIR}/e_tx_fifo.v
    ${DESIGN_DIR}/pp_dcntx8.v
    ${DESIGN_DIR}/quad_buff.v
    ${DESIGN_DIR}/r256x18_256x18.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET

  ASSERT_USAGE PB-CLOCK=2,PB-GMUX=2,PB-LOGIC<=498
)

add_dependencies(all_pp3_tests_bit   e_sdio_host_controller-ql-jimbob4-pp3_bit)
#add_dependencies(all_pp3_tests_bit_v e_sdio_host_controller-ql-jimbob4-pp3_bit_v)	# FIXME: List of connection types is empty (should have 1 element)

add_dependencies(all_pp3_tests_regression e_sdio_host_controller-ql-jimbob4-pp3_assert_usage)

set(E_SDIO ${QL_DESIGNS_DIR}/e_sdio_host_controller/e_sdio_host_controller.v)

set(FILE1 ${QL_DESIGNS_DIR}/e_sdio_host_controller/af256x18_512x9.v)
set(FILE2 ${QL_DESIGNS_DIR}/e_sdio_host_controller/af512x9_256x18.v)
set(FILE3 ${QL_DESIGNS_DIR}/e_sdio_host_controller/bipadoff_pp.v)
set(FILE4 ${QL_DESIGNS_DIR}/e_sdio_host_controller/e_Card_Detect.v)
set(FILE5 ${QL_DESIGNS_DIR}/e_sdio_host_controller/e_clock_mng_pp.v)
set(FILE6 ${QL_DESIGNS_DIR}/e_sdio_host_controller/e_cmd_control.v)
set(FILE7 ${QL_DESIGNS_DIR}/e_sdio_host_controller/e_crc16.v)
set(FILE8 ${QL_DESIGNS_DIR}/e_sdio_host_controller/e_dat0_line.v)
set(FILE9 ${QL_DESIGNS_DIR}/e_sdio_host_controller/e_dat123_line.v)
set(FILE10 ${QL_DESIGNS_DIR}/e_sdio_host_controller/e_dat_control.v)
set(FILE11 ${QL_DESIGNS_DIR}/e_sdio_host_controller/e_registers.v)
set(FILE12 ${QL_DESIGNS_DIR}/e_sdio_host_controller/e_rx_fifo.v)
set(FILE13 ${QL_DESIGNS_DIR}/e_sdio_host_controller/e_sync.v)
set(FILE14 ${QL_DESIGNS_DIR}/e_sdio_host_controller/e_tx_fifo.v)
set(FILE15 ${QL_DESIGNS_DIR}/e_sdio_host_controller/pp_dcntx8.v)
set(FILE16 ${QL_DESIGNS_DIR}/e_sdio_host_controller/quad_buff.v)
set(FILE17 ${QL_DESIGNS_DIR}/e_sdio_host_controller/r256x18_256x18.v)

add_fpga_target(
  NAME e_sdio_host_controller_test-gf12-no-adder
  TOP top
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${E_SDIO} ${FILE1} ${FILE2} ${FILE3} ${FILE4} ${FILE5} ${FILE6} ${FILE7} ${FILE8} ${FILE9} ${FILE10} ${FILE11} ${FILE12} ${FILE13} ${FILE14} ${FILE15} ${FILE16} ${FILE17}
  EXPLICIT_ADD_FILE_TARGET
  DEFINES SYNTH_OPTS=-no_adder
  )

add_fpga_target(
  NAME e_sdio_host_controller_test-gf12-adder
  TOP top
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${E_SDIO} ${FILE1} ${FILE2} ${FILE3} ${FILE4} ${FILE5} ${FILE6} ${FILE7} ${FILE8} ${FILE9} ${FILE10} ${FILE11} ${FILE12} ${FILE13} ${FILE14} ${FILE15} ${FILE16} ${FILE17}
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_qlf_k6n10_tests_no_adder e_sdio_host_controller_test-gf12-no-adder_route)
add_dependencies(all_qlf_k6n10_tests_adder    e_sdio_host_controller_test-gf12-adder_route)

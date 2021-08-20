set(SDIO_CLIENT ${QL_DESIGNS_DIR}/sdio_client_top/sdio_client_top.v)
set(FILE1 ${QL_DESIGNS_DIR}/sdio_client_top/af512x9_512x9.v)
set(FILE2 ${QL_DESIGNS_DIR}/sdio_client_top/cmd_control.v)
set(FILE3 ${QL_DESIGNS_DIR}/sdio_client_top/crc16.v)
set(FILE4 ${QL_DESIGNS_DIR}/sdio_client_top/crc7.v)
set(FILE5 ${QL_DESIGNS_DIR}/sdio_client_top/dat0_line.v)
set(FILE6 ${QL_DESIGNS_DIR}/sdio_client_top/dat123_line.v)
set(FILE7 ${QL_DESIGNS_DIR}/sdio_client_top/dat1_line.v)
set(FILE8 ${QL_DESIGNS_DIR}/sdio_client_top/dat23_line.v)
set(FILE9 ${QL_DESIGNS_DIR}/sdio_client_top/dat_control.v)
set(FILE10 ${QL_DESIGNS_DIR}/sdio_client_top/dat_fifo.v)
set(FILE11 ${QL_DESIGNS_DIR}/sdio_client_top/function1.v)
set(FILE12 ${QL_DESIGNS_DIR}/sdio_client_top/function2.v)
set(FILE13 ${QL_DESIGNS_DIR}/sdio_client_top/registers.v)
set(FILE14 ${QL_DESIGNS_DIR}/sdio_client_top/spi_cmd_datin_line.v)
set(FILE15 ${QL_DESIGNS_DIR}/sdio_client_top/spi_crc16.v)
set(FILE16 ${QL_DESIGNS_DIR}/sdio_client_top/spi_dat_control.v)
set(FILE17 ${QL_DESIGNS_DIR}/sdio_client_top/sync.v)


add_fpga_target(
  NAME sdio_client_top_test-gf12-no-adder
  TOP top
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${SDIO_CLIENT} ${FILE1} ${FILE2} ${FILE3} ${FILE4} ${FILE5} ${FILE6} ${FILE7} ${FILE8} ${FILE9} ${FILE10} ${FILE11} ${FILE12} ${FILE13} ${FILE14} ${FILE15} ${FILE16} ${FILE17}
  EXPLICIT_ADD_FILE_TARGET
  DEFINES SYNTH_OPTS=-no_adder
  )

add_fpga_target(
  NAME sdio_client_top_test-gf12-adder
  TOP top
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${SDIO_CLIENT} ${FILE1} ${FILE2} ${FILE3} ${FILE4} ${FILE5} ${FILE6} ${FILE7} ${FILE8} ${FILE9} ${FILE10} ${FILE11} ${FILE12} ${FILE13} ${FILE14} ${FILE15} ${FILE16} ${FILE17}
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_qlf_k6n10_tests_no_adder sdio_client_top_test-gf12-no-adder_route)
add_dependencies(all_qlf_k6n10_tests_adder    sdio_client_top_test-gf12-adder_route)

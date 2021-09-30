set(DESIGN_DIR ${QL_DESIGNS_DIR}/design2)

add_file_target(FILE ${DESIGN_DIR}/af1024x16_1024x16.v SCANNER_TYPE verilog)
add_file_target(FILE ${DESIGN_DIR}/af512x16_512x16.v SCANNER_TYPE verilog)
add_file_target(FILE ${DESIGN_DIR}/AL4S3B_FPGA_IP.v SCANNER_TYPE verilog)
add_file_target(FILE ${DESIGN_DIR}/AL4S3B_FPGA_Registers.v SCANNER_TYPE verilog)
add_file_target(FILE ${DESIGN_DIR}/AL4S3B_FPGA_Top.v SCANNER_TYPE verilog)
add_file_target(FILE ${DESIGN_DIR}/i2s_slave_Rx_FIFOs.v SCANNER_TYPE verilog)
add_file_target(FILE ${DESIGN_DIR}/i2s_slave_rx.v SCANNER_TYPE verilog)
add_file_target(FILE ${DESIGN_DIR}/i2s_slave_w_DMA_registers.v SCANNER_TYPE verilog)
add_file_target(FILE ${DESIGN_DIR}/i2s_slave_w_DMA_StateMachine.v SCANNER_TYPE verilog)
add_file_target(FILE ${DESIGN_DIR}/i2s_slave_w_DMA.v SCANNER_TYPE verilog)
add_file_target(FILE ${DESIGN_DIR}/ir_counters.v SCANNER_TYPE verilog)
add_file_target(FILE ${DESIGN_DIR}/ir_reg_if.v SCANNER_TYPE verilog)
add_file_target(FILE ${DESIGN_DIR}/ir_rx_ctrl.v SCANNER_TYPE verilog)
add_file_target(FILE ${DESIGN_DIR}/ir_tx_ctrl.v SCANNER_TYPE verilog)
add_file_target(FILE ${DESIGN_DIR}/ir_tx_rx.v SCANNER_TYPE verilog)
add_file_target(FILE ${DESIGN_DIR}/ir_tx_rx_wrap.v SCANNER_TYPE verilog)
add_file_target(FILE ${DESIGN_DIR}/r1024x8_1024x8.v SCANNER_TYPE verilog)
add_file_target(FILE chandalar.pcf)

add_fpga_target(
  NAME design2-ql-chandalar
  BOARD chandalar
  SOURCES
    ${DESIGN_DIR}/af1024x16_1024x16.v
    ${DESIGN_DIR}/af512x16_512x16.v
    ${DESIGN_DIR}/AL4S3B_FPGA_IP.v
    ${DESIGN_DIR}/AL4S3B_FPGA_Registers.v
    ${DESIGN_DIR}/AL4S3B_FPGA_Top.v
    ${DESIGN_DIR}/i2s_slave_Rx_FIFOs.v
    ${DESIGN_DIR}/i2s_slave_rx.v
    ${DESIGN_DIR}/i2s_slave_w_DMA_registers.v
    ${DESIGN_DIR}/i2s_slave_w_DMA_StateMachine.v
    ${DESIGN_DIR}/i2s_slave_w_DMA.v
    ${DESIGN_DIR}/ir_counters.v
    ${DESIGN_DIR}/ir_reg_if.v
    ${DESIGN_DIR}/ir_rx_ctrl.v
    ${DESIGN_DIR}/ir_tx_ctrl.v
    ${DESIGN_DIR}/ir_tx_rx.v
    ${DESIGN_DIR}/ir_tx_rx_wrap.v
    ${DESIGN_DIR}/r1024x8_1024x8.v
  INPUT_IO_FILE chandalar.pcf
  EXPLICIT_ADD_FILE_TARGET
  )

add_jlink_output(
  PARENT design2-ql-chandalar
)

add_openocd_output(
  PARENT design2-ql-chandalar
)

add_dependencies(all_ql_tests_bit  design2-ql-chandalar_bit)
add_dependencies(all_ql_tests_bit_v design2-ql-chandalar_bit_v)
add_dependencies(all_ql_tests_prog design2-ql-chandalar_jlink)
add_dependencies(all_ql_tests_prog design2-ql-chandalar_openocd)


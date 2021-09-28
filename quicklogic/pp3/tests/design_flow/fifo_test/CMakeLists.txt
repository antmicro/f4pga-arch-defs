add_file_target(FILE af512x16_512x16.v SCANNER TYPE verilog)
add_file_target(FILE f1024x16_1024x16.v SCANNER TYPE verilog)
add_file_target(FILE af512x32_512x32.v SCANNER TYPE verilog)
add_file_target(FILE AL4S3B_FPGA_QL_Reserved.v SCANNER TYPE verilog)
add_file_target(FILE AL4S3B_FPGA_Registers.v SCANNER TYPE verilog)
add_file_target(FILE AL4S3B_FPGA_IP.v SCANNER TYPE verilog)
add_file_target(FILE AL4S3B_FPGA_Top.v SCANNER TYPE verilog)
add_file_target(FILE chandalar.pcf)
add_file_target(FILE jimbob4.pcf)

add_fpga_target(
  NAME fifo_test-ql-chandalar
  BOARD chandalar
  SOURCES AL4S3B_FPGA_Top.v AL4S3B_FPGA_IP.v AL4S3B_FPGA_Registers.v AL4S3B_FPGA_QL_Reserved.v af512x32_512x32.v f1024x16_1024x16.v af512x16_512x16.v
  INPUT_IO_FILE chandalar.pcf
  EXPLICIT_ADD_FILE_TARGET
  )

add_jlink_output(
  PARENT fifo_test-ql-chandalar
)

add_openocd_output(
  PARENT fifo_test-ql-chandalar
)

add_dependencies(all_ql_tests_bit  fifo_test-ql-chandalar_bit)
add_dependencies(all_ql_tests_bit_v fifo_test-ql-chandalar_bit_v)
add_dependencies(all_ql_tests_prog fifo_test-ql-chandalar_jlink)
add_dependencies(all_ql_tests_prog fifo_test-ql-chandalar_openocd)

add_fpga_target(
  NAME fifo_test-ql-jimbob4
  BOARD jimbob4
  SOURCES AL4S3B_FPGA_Top.v AL4S3B_FPGA_IP.v AL4S3B_FPGA_Registers.v AL4S3B_FPGA_QL_Reserved.v af512x32_512x32.v f1024x16_1024x16.v af512x16_512x16.v
  INPUT_IO_FILE jimbob4.pcf
  EXPLICIT_ADD_FILE_TARGET
  )

add_jlink_output(
  PARENT fifo_test-ql-jimbob4
)

add_openocd_output(
  PARENT fifo_test-ql-jimbob4
)

add_dependencies(all_ql_tests_bit  fifo_test-ql-jimbob4_bit)
add_dependencies(all_ql_tests_bit_v fifo_test-ql-jimbob4_bit_v)
add_dependencies(all_ql_tests_prog fifo_test-ql-jimbob4_jlink)
add_dependencies(all_ql_tests_prog fifo_test-ql-jimbob4_openocd)

add_fpga_target(
  NAME fifo_test-ql-jimbob4-pp3
  BOARD jimbob4-pp3
  SOURCES AL4S3B_FPGA_Top.v AL4S3B_FPGA_IP.v AL4S3B_FPGA_Registers.v AL4S3B_FPGA_QL_Reserved.v af512x32_512x32.v f1024x16_1024x16.v af512x16_512x16.v
  INPUT_IO_FILE jimbob4.pcf
  EXPLICIT_ADD_FILE_TARGET
  )

add_jlink_output(
  PARENT fifo_test-ql-jimbob4-pp3
)

add_openocd_output(
  PARENT fifo_test-ql-jimbob4-pp3
)

add_dependencies(all_ql_tests_bit  fifo_test-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v fifo_test-ql-jimbob4-pp3_bit_v)
add_dependencies(all_ql_tests_prog fifo_test-ql-jimbob4-pp3_jlink)
add_dependencies(all_ql_tests_prog fifo_test-ql-jimbob4-pp3_openocd)

add_file_target(FILE Serializer_Deserializer_Test.v SCANNER TYPE verilog)
add_file_target(FILE Serializer_Deserializer.v SCANNER TYPE verilog)
add_file_target(FILE Dma_Ctrl.v SCANNER TYPE verilog)
add_file_target(FILE Fsm_Top.v SCANNER TYPE verilog)
add_file_target(FILE AL4S3B_FPGA_QL_Reserved.v SCANNER TYPE verilog)
add_file_target(FILE AL4S3B_FPGA_Registers.v SCANNER TYPE verilog)
add_file_target(FILE AL4S3B_FPGA_IP.v SCANNER TYPE verilog)
add_file_target(FILE AL4S3B_FPGA_Top.v SCANNER TYPE verilog)
add_file_target(FILE chandalar.pcf)
add_file_target(FILE jimbob4.pcf)

add_fpga_target(
  NAME design10-ql-chandalar
  BOARD chandalar
  SOURCES AL4S3B_FPGA_Top.v AL4S3B_FPGA_IP.v AL4S3B_FPGA_QL_Reserved.v AL4S3B_FPGA_Registers.v Dma_Ctrl.v Fsm_Top.v Serializer_Deserializer.v Serializer_Deserializer_Test.v
  INPUT_IO_FILE chandalar.pcf
  EXPLICIT_ADD_FILE_TARGET
  )

add_jlink_output(
  PARENT design10-ql-chandalar
)

add_openocd_output(
  PARENT design10-ql-chandalar
)

add_dependencies(all_ql_tests_bit  design10-ql-chandalar_bit)
add_dependencies(all_ql_tests_bit_v design10-ql-chandalar_bit_v)
add_dependencies(all_ql_tests_prog design10-ql-chandalar_jlink)
add_dependencies(all_ql_tests_prog design10-ql-chandalar_openocd)

add_fpga_target(
  NAME design10-ql-jimbob4
  BOARD jimbob4
  SOURCES AL4S3B_FPGA_Top.v AL4S3B_FPGA_IP.v AL4S3B_FPGA_QL_Reserved.v AL4S3B_FPGA_Registers.v Dma_Ctrl.v Fsm_Top.v Serializer_Deserializer.v Serializer_Deserializer_Test.v
  INPUT_IO_FILE jimbob4.pcf
  EXPLICIT_ADD_FILE_TARGET
  )

add_jlink_output(
  PARENT design10-ql-jimbob4
)

add_openocd_output(
  PARENT design10-ql-jimbob4
)

add_dependencies(all_ql_tests_bit  design10-ql-jimbob4_bit)
add_dependencies(all_ql_tests_bit_v design10-ql-jimbob4_bit_v)
add_dependencies(all_ql_tests_prog design10-ql-jimbob4_jlink)
add_dependencies(all_ql_tests_prog design10-ql-jimbob4_openocd)

add_fpga_target(
  NAME design10-ql-jimbob4-pp3
  BOARD jimbob4-pp3
  SOURCES AL4S3B_FPGA_Top.v AL4S3B_FPGA_IP.v AL4S3B_FPGA_QL_Reserved.v AL4S3B_FPGA_Registers.v Dma_Ctrl.v Fsm_Top.v Serializer_Deserializer.v Serializer_Deserializer_Test.v
  INPUT_IO_FILE jimbob4.pcf
  EXPLICIT_ADD_FILE_TARGET
  )

add_jlink_output(
  PARENT design10-ql-jimbob4-pp3
)

add_openocd_output(
  PARENT design10-ql-jimbob4-pp3
)

add_dependencies(all_ql_tests_bit  design10-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v design10-ql-jimbob4-pp3_bit_v)
add_dependencies(all_ql_tests_prog design10-ql-jimbob4-pp3_jlink)
add_dependencies(all_ql_tests_prog design10-ql-jimbob4-pp3_openocd)


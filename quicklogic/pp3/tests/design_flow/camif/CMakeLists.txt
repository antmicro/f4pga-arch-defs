add_file_target(FILE camif_new.v SCANNER_TYPE verilog)
add_file_target(FILE af512x16_512x16.v SCANNER_TYPE verilog)
add_file_target(FILE chandalar.pcf)
add_file_target(FILE jimbob4.pcf)

add_fpga_target(
  NAME camif-ql-chandalar
  BOARD chandalar
  SOURCES camif_new.v af512x16_512x16.v
  INPUT_IO_FILE chandalar.pcf
  EXPLICIT_ADD_FILE_TARGET
  )

add_jlink_output(
  PARENT camif-ql-chandalar
)

add_openocd_output(
  PARENT camif-ql-chandalar
)

add_dependencies(all_ql_tests_bit  camif-ql-chandalar_bit)
add_dependencies(all_ql_tests_bit_v camif-ql-chandalar_bit_v)
add_dependencies(all_ql_tests_prog camif-ql-chandalar_jlink)
add_dependencies(all_ql_tests_prog camif-ql-chandalar_openocd)
add_dependencies(all_quick_tests camif-ql-chandalar_analysis)
add_dependencies(camif-ql-chandalar_analysis camif-ql-chandalar_bit_v)

add_fpga_target(
  NAME camif-ql-jimbob4
  BOARD jimbob4
  SOURCES camif_new.v af512x16_512x16.v
  INPUT_IO_FILE jimbob4.pcf
  EXPLICIT_ADD_FILE_TARGET
  )

add_jlink_output(
  PARENT camif-ql-jimbob4
)

add_openocd_output(
  PARENT camif-ql-jimbob4
)

add_dependencies(all_ql_tests_bit  camif-ql-jimbob4_bit)
add_dependencies(all_ql_tests_bit_v camif-ql-jimbob4_bit_v)
add_dependencies(all_ql_tests_prog camif-ql-jimbob4_jlink)
add_dependencies(all_ql_tests_prog camif-ql-jimbob4_openocd)
add_dependencies(all_quick_tests camif-ql-jimbob4_analysis)
add_dependencies(camif-ql-jimbob4_analysis camif-ql-jimbob4_bit_v)

add_fpga_target(
  NAME camif-ql-jimbob4-pp3
  BOARD jimbob4-pp3
  SOURCES camif_new.v af512x16_512x16.v
  INPUT_IO_FILE jimbob4.pcf
  EXPLICIT_ADD_FILE_TARGET
  )

add_jlink_output(
  PARENT camif-ql-jimbob4-pp3
)

add_openocd_output(
  PARENT camif-ql-jimbob4-pp3
)

add_dependencies(all_ql_tests_bit  camif-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v camif-ql-jimbob4-pp3_bit_v)
add_dependencies(all_ql_tests_prog camif-ql-jimbob4-pp3_jlink)
add_dependencies(all_ql_tests_prog camif-ql-jimbob4-pp3_openocd)
add_dependencies(all_quick_tests camif-ql-jimbob4-pp3_analysis)
add_dependencies(camif-ql-jimbob4-pp3_analysis camif-ql-jimbob4-pp3_bit_v)

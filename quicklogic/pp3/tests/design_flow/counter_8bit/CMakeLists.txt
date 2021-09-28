add_file_target(FILE counter_8bit.v SCANNER_TYPE verilog)
add_file_target(FILE chandalar.pcf)
add_file_target(FILE jimbob4.pcf)

add_fpga_target(
  NAME counter_8bit-ql-chandalar
  BOARD chandalar
  SOURCES counter_8bit.v
  INPUT_IO_FILE chandalar.pcf
  EXPLICIT_ADD_FILE_TARGET
  )

add_jlink_output(
  PARENT counter_8bit-ql-chandalar
)

add_openocd_output(
  PARENT counter_8bit-ql-chandalar
)

add_dependencies(all_ql_tests_bit  counter_8bit-ql-chandalar_bit)
add_dependencies(all_ql_tests_bit_v counter_8bit-ql-chandalar_bit_v)
add_dependencies(all_ql_tests_prog counter_8bit-ql-chandalar_jlink)
add_dependencies(all_ql_tests_prog counter_8bit-ql-chandalar_openocd)

add_fpga_target(
  NAME counter_8bit-ql-jimbob4
  BOARD jimbob4
  SOURCES counter_8bit.v
  INPUT_IO_FILE jimbob4.pcf
  EXPLICIT_ADD_FILE_TARGET
  )

add_jlink_output(
  PARENT counter_8bit-ql-jimbob4
)

add_openocd_output(
  PARENT counter_8bit-ql-jimbob4
)

add_dependencies(all_ql_tests_bit  counter_8bit-ql-jimbob4_bit)
add_dependencies(all_ql_tests_bit_v counter_8bit-ql-jimbob4_bit_v)
add_dependencies(all_ql_tests_prog counter_8bit-ql-jimbob4_jlink)
add_dependencies(all_ql_tests_prog counter_8bit-ql-jimbob4_openocd)

add_fpga_target(
  NAME counter_8bit-ql-jimbob4-pp3
  BOARD jimbob4-pp3
  SOURCES counter_8bit.v
  INPUT_IO_FILE jimbob4.pcf
  EXPLICIT_ADD_FILE_TARGET
  )

add_jlink_output(
  PARENT counter_8bit-ql-jimbob4-pp3
)

add_openocd_output(
  PARENT counter_8bit-ql-jimbob4-pp3
)

add_dependencies(all_ql_tests_bit  counter_8bit-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v counter_8bit-ql-jimbob4-pp3_bit_v)
add_dependencies(all_ql_tests_prog counter_8bit-ql-jimbob4-pp3_jlink)
add_dependencies(all_ql_tests_prog counter_8bit-ql-jimbob4-pp3_openocd)


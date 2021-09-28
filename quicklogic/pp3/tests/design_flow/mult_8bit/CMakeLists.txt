add_file_target(FILE mult_8bit.v SCANNER_TYPE verilog)
add_file_target(FILE mult_8bit_tb.v SCANNER_TYPE verilog)
add_file_target(FILE chandalar.pcf)
add_file_target(FILE jimbob4.pcf)

add_fpga_target(
  NAME mult_8bit-ql-chandalar
  BOARD chandalar
  SOURCES mult_8bit.v
  TESTBENCH_SOURCES mult_8bit_tb.v
  INPUT_IO_FILE chandalar.pcf
  EXPLICIT_ADD_FILE_TARGET
  )

add_jlink_output(
  PARENT mult_8bit-ql-chandalar
)

add_openocd_output(
  PARENT mult_8bit-ql-chandalar
)

add_dependencies(all_ql_tests_bit  mult_8bit-ql-chandalar_bit)
add_dependencies(all_ql_tests_bit_v mult_8bit-ql-chandalar_bit_v)
add_dependencies(all_ql_tests_prog mult_8bit-ql-chandalar_jlink)
add_dependencies(all_ql_tests_prog mult_8bit-ql-chandalar_openocd)
add_dependencies(all_quick_tests mult_8bit-ql-chandalar_analysis)
add_dependencies(mult_8bit-ql-chandalar_analysis mult_8bit-ql-chandalar_bit_v)
add_dependencies(all_quick_tests testbench_mult_8bit_tb)

add_fpga_target(
  NAME mult_8bit-ql-jimbob4
  BOARD jimbob4
  SOURCES mult_8bit.v
  INPUT_IO_FILE jimbob4.pcf
  EXPLICIT_ADD_FILE_TARGET
  )

add_jlink_output(
  PARENT mult_8bit-ql-jimbob4
)

add_openocd_output(
  PARENT mult_8bit-ql-jimbob4
)

add_dependencies(all_ql_tests_bit  mult_8bit-ql-jimbob4_bit)
add_dependencies(all_ql_tests_bit_v mult_8bit-ql-jimbob4_bit_v)
add_dependencies(all_ql_tests_prog mult_8bit-ql-jimbob4_jlink)
add_dependencies(all_ql_tests_prog mult_8bit-ql-jimbob4_openocd)
add_dependencies(all_quick_tests mult_8bit-ql-jimbob4_analysis)
add_dependencies(mult_8bit-ql-jimbob4_analysis mult_8bit-ql-jimbob4_bit_v)
add_dependencies(all_quick_tests testbench_mult_8bit_tb)

add_fpga_target(
  NAME mult_8bit-ql-jimbob4-pp3
  BOARD jimbob4-pp3
  SOURCES mult_8bit.v
  INPUT_IO_FILE jimbob4.pcf
  EXPLICIT_ADD_FILE_TARGET
  )

add_jlink_output(
  PARENT mult_8bit-ql-jimbob4-pp3
)

add_openocd_output(
  PARENT mult_8bit-ql-jimbob4-pp3
)

add_dependencies(all_ql_tests_bit  mult_8bit-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v mult_8bit-ql-jimbob4-pp3_bit_v)
add_dependencies(all_ql_tests_prog mult_8bit-ql-jimbob4-pp3_jlink)
add_dependencies(all_ql_tests_prog mult_8bit-ql-jimbob4-pp3_openocd)
add_dependencies(all_quick_tests mult_8bit-ql-jimbob4-pp3_analysis)
add_dependencies(mult_8bit-ql-jimbob4-pp3_analysis mult_8bit-ql-jimbob4-pp3_bit_v)
add_dependencies(all_quick_tests testbench_mult_8bit_tb)


add_file_target(FILE AL4S3B_FPGA_Top.v SCANNER_TYPE verilog)
add_file_target(FILE litex_core.v SCANNER_TYPE verilog)
add_file_target(FILE chandalar.pcf)

add_fpga_target(
  NAME soc_litex_pwm-ql-chandalar
  BOARD chandalar
  SOURCES litex_core.v AL4S3B_FPGA_Top.v
  INPUT_IO_FILE chandalar.pcf
  EXPLICIT_ADD_FILE_TARGET
)

add_jlink_output(
  PARENT soc_litex_pwm-ql-chandalar
)

add_openocd_output(
  PARENT soc_litex_pwm-ql-chandalar
)

add_dependencies(all_ql_tests_bit  soc_litex_pwm-ql-chandalar_bit)
add_dependencies(all_ql_tests_bit_v soc_litex_pwm-ql-chandalar_bit_v)
add_dependencies(all_ql_tests_prog soc_litex_pwm-ql-chandalar_jlink)
add_dependencies(all_ql_tests_prog soc_litex_pwm-ql-chandalar_openocd)

add_file_target(FILE quickfeather.pcf)

add_fpga_target(
  NAME soc_litex_pwm-ql-quickfeather
  BOARD quickfeather
  SOURCES litex_core.v AL4S3B_FPGA_Top.v
  INPUT_IO_FILE quickfeather.pcf
  EXPLICIT_ADD_FILE_TARGET
)

add_jlink_output(
  PARENT soc_litex_pwm-ql-quickfeather
)

add_openocd_output(
  PARENT soc_litex_pwm-ql-quickfeather
)

add_dependencies(all_ql_tests_bit  soc_litex_pwm-ql-quickfeather_bit)
add_dependencies(all_ql_tests_bit_v soc_litex_pwm-ql-quickfeather_bit_v)
add_dependencies(all_ql_tests_prog soc_litex_pwm-ql-quickfeather_jlink)
add_dependencies(all_ql_tests_prog soc_litex_pwm-ql-quickfeather_openocd)

add_file_target(FILE jimbob4.pcf)

add_fpga_target(
  NAME soc_litex_pwm-ql-jimbob4
  BOARD jimbob4
  SOURCES litex_core.v AL4S3B_FPGA_Top.v
  INPUT_IO_FILE jimbob4.pcf
  EXPLICIT_ADD_FILE_TARGET
)

add_jlink_output(
  PARENT soc_litex_pwm-ql-jimbob4
)

add_openocd_output(
  PARENT soc_litex_pwm-ql-jimbob4
)

add_dependencies(all_ql_tests_bit  soc_litex_pwm-ql-jimbob4_bit)
add_dependencies(all_ql_tests_bit_v soc_litex_pwm-ql-jimbob4_bit_v)
add_dependencies(all_ql_tests_prog soc_litex_pwm-ql-jimbob4_jlink)
add_dependencies(all_ql_tests_prog soc_litex_pwm-ql-jimbob4_openocd)

add_fpga_target(
  NAME soc_litex_pwm-ql-jimbob4-pp3
  BOARD jimbob4-pp3
  SOURCES litex_core.v AL4S3B_FPGA_Top.v
  INPUT_IO_FILE jimbob4.pcf
  EXPLICIT_ADD_FILE_TARGET
)

add_jlink_output(
  PARENT soc_litex_pwm-ql-jimbob4-pp3
)

add_openocd_output(
  PARENT soc_litex_pwm-ql-jimbob4-pp3
)

add_dependencies(all_ql_tests_bit  soc_litex_pwm-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v soc_litex_pwm-ql-jimbob4-pp3_bit_v)
add_dependencies(all_ql_tests_prog soc_litex_pwm-ql-jimbob4-pp3_jlink)
add_dependencies(all_ql_tests_prog soc_litex_pwm-ql-jimbob4-pp3_openocd)


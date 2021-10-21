add_file_target(FILE ram_inference.v SCANNER_TYPE verilog)
add_file_target(FILE chandalar.pcf)
add_file_target(FILE jimbob4.pcf)

add_fpga_target(
  NAME regression-ram_inference-ql-chandalar
  BOARD chandalar
  SOURCES ram_inference.v
  INPUT_IO_FILE chandalar.pcf
  EXPLICIT_ADD_FILE_TARGET
  ASSERT_USAGE PB-BIDIR=31,PB-CLOCK=1,PB-GMUX=1,PB-LOGIC<=54,PB-RAM=3
  ASSERT_TIMING fmax>30.0
)

add_dependencies(all_ql_tests_regression regression-ram_inference-ql-chandalar_assert_usage)

add_fpga_target(
  NAME regression-ram_inference-ql-jimbob4-pp3
  BOARD jimbob4-pp3
  SOURCES ram_inference.v
  INPUT_IO_FILE jimbob4.pcf
  EXPLICIT_ADD_FILE_TARGET
  ASSERT_USAGE PB-BIDIR=31,PB-CLOCK=1,PB-GMUX=1,PB-LOGIC<=54,PB-RAM=3
  ASSERT_TIMING fmax>30.0
)

add_dependencies(all_ql_tests_regression regression-ram_inference-ql-jimbob4-pp3_assert_usage)


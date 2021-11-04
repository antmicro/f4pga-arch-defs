add_file_target(FILE ext_mult.v SCANNER_TYPE verilog)
add_file_target(FILE chandalar.pcf)
add_file_target(FILE pd64.pcf)

add_fpga_target(
  NAME ext_mult-ql-chandalar
  BOARD chandalar
  SOURCES ext_mult.v
  INPUT_IO_FILE chandalar.pcf
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_eos_s3_tests ext_mult-ql-chandalar_route)
add_dependencies(ext_mult-ql-chandalar_analysis ext_mult-ql-chandalar_bit_v)


add_fpga_target(
  NAME ext_mult-ql-pd64
  BOARD pd64
  SOURCES ext_mult.v
  INPUT_IO_FILE pd64.pcf
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_pp3_tests ext_mult-ql-pd64_route)
add_dependencies(ext_mult-ql-pd64_analysis ext_mult-ql-pd64_bit_v)


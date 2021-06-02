add_file_target(FILE shift_reg.v SCANNER_TYPE verilog)

add_fpga_target(
  NAME shift_reg_12_test-umc22-adder
  TOP top
  BOARD qlf_k4n8-qlf_k4n8_umc22_slow_board
  SOURCES shift_reg.v
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_qlf_k4n8_tests_adder shift_reg_12_test-umc22-adder_bit)

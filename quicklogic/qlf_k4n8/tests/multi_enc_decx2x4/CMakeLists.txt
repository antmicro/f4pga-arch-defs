add_file_target(FILE decoder.v SCANNER_TYPE verilog)
add_file_target(FILE encoder.v SCANNER_TYPE verilog)
add_file_target(FILE topenc_decx2.v SCANNER_TYPE verilog)
add_file_target(FILE multi_enc_decx2x4.v SCANNER_TYPE verilog)
add_file_target(FILE multi_enc_decx2x4.pcf)
add_fpga_target(
  NAME multi_enc_decx2x4-umc22-no-adder
  TOP multi_enc_decx2x4
  BOARD qlf_k4n8-qlf_k4n8_umc22_board
  SOURCES decoder.v encoder.v topenc_decx2.v multi_enc_decx2x4.v
  INPUT_IO_FILE multi_enc_decx2x4.pcf
  EXPLICIT_ADD_FILE_TARGET
  DEFINES SYNTH_OPTS=-no_adder
  )

add_fpga_target(
  NAME multi_enc_decx2x4-umc22-adder
  TOP multi_enc_decx2x4
  BOARD qlf_k4n8-qlf_k4n8_umc22_board
  SOURCES decoder.v encoder.v topenc_decx2.v multi_enc_decx2x4.v
  INPUT_IO_FILE multi_enc_decx2x4.pcf
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_qlf_k4n8_tests_no_adder multi_enc_decx2x4-umc22-no-adder_route)
add_dependencies(all_qlf_k4n8_tests_adder    multi_enc_decx2x4-umc22-adder_route)

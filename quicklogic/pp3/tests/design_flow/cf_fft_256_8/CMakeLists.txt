set(DESIGN_DIR ${QL_DESIGNS_DIR}/cf_fft_256_8)
add_file_target(FILE pd64.pcf)

add_fpga_target(
  NAME cf_fft_256_8-ql-pd64
  TOP cf_fft_256_8
  BOARD pd64
  SOURCES
    ${DESIGN_DIR}/cf_fft_256_8.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET
)

add_dependencies(all_ql_tests_bit   cf_fft_256_8-ql-pd64_bit)
add_dependencies(all_ql_tests_bit_v cf_fft_256_8-ql-pd64_bit_v)

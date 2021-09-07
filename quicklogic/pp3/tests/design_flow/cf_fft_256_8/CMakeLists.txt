set(DESIGN_DIR ${QL_DESIGNS_DIR}/cf_fft_256_8)

add_fpga_target(
  NAME cf_fft_256_8-ql-jimbob4-pp3
  TOP cf_fft_256_8
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/cf_fft_256_8.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET
)

add_dependencies(all_ql_tests_bit   cf_fft_256_8-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v cf_fft_256_8-ql-jimbob4-pp3_bit_v)

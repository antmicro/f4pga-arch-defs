set(DESIGN_DIR ${QL_DESIGNS_DIR}/cf_fft_256_8)

add_fpga_target(
  NAME cf_fft_256_8-ql-pd64
  TOP cf_fft_256_8
  BOARD pd64
  SOURCES
    ${DESIGN_DIR}/cf_fft_256_8.v
  INPUT_IO_FILE pd64.pcf
  AUTO_ADD_FILE_TARGET
)

add_dependencies(all_pp3_tests_bit   cf_fft_256_8-ql-pd64_bit)
add_dependencies(all_pp3_tests_bit_v cf_fft_256_8-ql-pd64_bit_v)

add_fpga_target(
  NAME cf_fft_256_8-ql-chandalar
  BOARD chandalar
  SOURCES
    ${DESIGN_DIR}/cf_fft_256_8.v
  INPUT_IO_FILE chandalar.pcf
  AUTO_ADD_FILE_TARGET
)


add_jlink_output(
  PARENT cf_fft_256_8-ql-chandalar
)

add_openocd_output(
  PARENT cf_fft_256_8-ql-chandalar
)

add_dependencies(all_eos_s3_tests_prog  cf_fft_256_8-ql-chandalar_jlink)
add_dependencies(all_eos_s3_tests_prog  cf_fft_256_8-ql-chandalar_openocd)

add_dependencies(all_eos_s3_tests_bit   cf_fft_256_8-ql-chandalar_bit)
add_dependencies(all_eos_s3_tests_bit_v cf_fft_256_8-ql-chandalar_bit_v)

add_dependencies(cf_fft_256_8-ql-chandalar_analysis cf_fft_256_8-ql-chandalar_bit_v)


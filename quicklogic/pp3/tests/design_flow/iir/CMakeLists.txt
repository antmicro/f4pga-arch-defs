set(DESIGN_DIR ${QL_DESIGNS_DIR}/iir)

add_fpga_target(
  NAME iir-ql-jimbob4-pp3
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/iir.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET

  ASSERT_BLOCK_TYPES_ARE_USED PB-CLOCK=2,PB-GMUX=2,PB-LOGIC<=878
)

add_dependencies(all_pp3_tests_bit   iir-ql-jimbob4-pp3_bit)
add_dependencies(all_pp3_tests_bit_v iir-ql-jimbob4-pp3_bit_v)

add_dependencies(all_pp3_tests_regression iir-ql-jimbob4-pp3_assert_usage)

add_fpga_target(
  NAME iir-ql-chandalar
  BOARD chandalar
  SOURCES
    ${DESIGN_DIR}/iir.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET

  ASSERT_BLOCK_TYPES_ARE_USED PB-CLOCK=2,PB-GMUX=2,PB-LOGIC<=878
)

add_jlink_output(
  PARENT iir-ql-chandalar
)

add_openocd_output(
  PARENT iir-ql-chandalar
)

# FIXME: The EOS-S3 fabric does not provide sufficient IO count
#add_dependencies(all_eos_s3_tests_bit   iir-ql-chandalar_bit)
#add_dependencies(all_eos_s3_tests_bit_v iir-ql-chandalar_bit_v)
#add_dependencies(all_eos_s3_tests_prog  iir-ql-chandalar_jlink)
#add_dependencies(all_eos_s3_tests_prog  iir-ql-chandalar_openocd)

#add_dependencies(all_eos_s3_tests_regression iir-ql-chandalar_assert_usage)


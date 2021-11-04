set(DESIGN_DIR ${QL_DESIGNS_DIR}/rgb2ycrcb)

add_fpga_target(
  NAME rgb2ycrcb-ql-jimbob4-pp3
  TOP top
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/rgb2ycrcb.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET

  ASSERT_USAGE PB-CLOCK=1,PB-GMUX=1,PB-LOGIC<=496
  ASSERT_TIMING fmax>=10.0
)

add_dependencies(all_pp3_tests_bit   rgb2ycrcb-ql-jimbob4-pp3_bit)
#add_dependencies(all_pp3_tests_bit_v rgb2ycrcb-ql-jimbob4-pp3_bit_v)	# FIXME: List of connection types is empty (should have 1 element)

add_dependencies(all_pp3_tests_regression rgb2ycrcb-ql-jimbob4-pp3_assert_usage)
add_dependencies(all_pp3_tests_regression rgb2ycrcb-ql-jimbob4-pp3_assert_timing)

set(CURR_DIR ${QL_DESIGNS_DIR}/conv2d)
add_file_target(FILE conv2d.sdc SCANNER_TYPE)

add_fpga_target(
  NAME conv2d_test-gf12-no-adder
  TOP top
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${CURR_DIR}/conv2d.v ${CURR_DIR}/control.v ${CURR_DIR}/ksa.v ${CURR_DIR}/ksa1.v ${CURR_DIR}/tfl.v
  EXPLICIT_ADD_FILE_TARGET
  INPUT_SDC_FILE conv2d.sdc
  DEFINES SYNTH_OPTS=-no_adder
  )

add_fpga_target(
  NAME conv2d_test-gf12-adder
  TOP top
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${CURR_DIR}/conv2d.v ${CURR_DIR}/control.v ${CURR_DIR}/ksa.v ${CURR_DIR}/ksa1.v ${CURR_DIR}/tfl.v
  EXPLICIT_ADD_FILE_TARGET
  INPUT_SDC_FILE conv2d.sdc
  )

add_dependencies(all_qlf_k6n10_tests_no_adder conv2d_test-gf12-no-adder_route)
add_dependencies(all_qlf_k6n10_tests_adder    conv2d_test-gf12-adder_route)

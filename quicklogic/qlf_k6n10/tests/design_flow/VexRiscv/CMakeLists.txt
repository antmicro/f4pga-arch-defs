set(VEXRISCV ${QL_DESIGNS_DIR}/VexRiscv/VexRiscv.v)
add_file_target(FILE VexRiscv.sdc SCANNER_TYPE)
add_fpga_target(
  NAME VexRiscv_test-gf12-no-adder
  TOP VexRiscv
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${VEXRISCV}
  INPUT_SDC_FILE VexRiscv.sdc
  EXPLICIT_ADD_FILE_TARGET
  DEFINES SYNTH_OPTS=-no_adder
  )

add_fpga_target(
  NAME VexRiscv_test-gf12-adder
  TOP VexRiscv
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${VEXRISCV}
  INPUT_SDC_FILE VexRiscv.sdc
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_qlf_k6n10_tests_no_adder VexRiscv_test-gf12-no-adder_route)
add_dependencies(all_qlf_k6n10_tests_adder    VexRiscv_test-gf12-adder_route)

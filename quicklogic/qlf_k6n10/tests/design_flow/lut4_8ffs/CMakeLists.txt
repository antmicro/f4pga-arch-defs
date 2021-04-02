set(LUT4_8FF ${QL_DESIGNS_DIR}/lut4_8ffs/lut4_8ffs.v)

add_fpga_target(
  NAME lut4_8ffs_test-gf12-no-adder
  TOP lut4_8ffs
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${LUT4_8FF}
  EXPLICIT_ADD_FILE_TARGET
  DEFINES SYNTH_OPTS=-no_adder
  )

add_fpga_target(
  NAME lut4_8ffs_test-gf12-adder
  TOP lut4_8ffs
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${LUT4_8FF}
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_qlf_k6n10_tests_no_adder lut4_8ffs_test-gf12-no-adder_route)
add_dependencies(all_qlf_k6n10_tests_adder    lut4_8ffs_test-gf12-adder_route)

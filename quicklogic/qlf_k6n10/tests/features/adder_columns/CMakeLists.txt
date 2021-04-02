set(ADDER_C ${QL_DESIGNS_DIR}/adder_columns/adder_columns.v)
#add_file_target(FILE ${ADDER_C} SCANNER_TYPE verilog)

add_fpga_target(
  NAME adder_columns_test2-gf12-adder
  TOP adder_columns
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${ADDER_C}
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_qlf_k6n10_tests_adder    adder_columns_test2-gf12-adder_bit)

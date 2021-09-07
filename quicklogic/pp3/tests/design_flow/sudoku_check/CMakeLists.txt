set(DESIGN_DIR ${QL_DESIGNS_DIR}/sudoku_check)

add_fpga_target(
  NAME sudoku_check-ql-jimbob4-pp3
  TOP sudoku_check
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/fifo.v
    ${DESIGN_DIR}/pll.v
    ${DESIGN_DIR}/puz_bank3.v
    ${DESIGN_DIR}/sudoku_ans.v
    ${DESIGN_DIR}/sudoku_bin2hex.v
    ${DESIGN_DIR}/sudoku_check.v
    ${DESIGN_DIR}/sudoku_core.v
    ${DESIGN_DIR}/sudoku_hex2bin.v
    ${DESIGN_DIR}/sudoku_mask_stg2.v
    ${DESIGN_DIR}/sudoku_partials.v
    ${DESIGN_DIR}/sudoku_solution.v
    ${DESIGN_DIR}/sudoku.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET
)

add_dependencies(all_ql_tests_bit   sudoku_check-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v sudoku_check-ql-jimbob4-pp3_bit_v)

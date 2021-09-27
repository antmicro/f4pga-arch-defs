set(DESIGN_DIR ${QL_DESIGNS_DIR}/clock_tree_design)

add_fpga_target(
  NAME clock_tree_design-ql-jimbob4-pp3
  TOP clock_tree_design_pp3
  BOARD jimbob4-pp3
  SOURCES
    clock_tree_design_pp3.v
    ${DESIGN_DIR}/clock_tree_design.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET
)

add_dependencies(all_ql_tests_bit   clock_tree_design-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v clock_tree_design-ql-jimbob4-pp3_bit_v)

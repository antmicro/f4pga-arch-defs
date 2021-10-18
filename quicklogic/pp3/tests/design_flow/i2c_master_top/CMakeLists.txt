set(DESIGN_DIR ${QL_DESIGNS_DIR}/i2c_master_top)

add_fpga_target(
  NAME i2c_master_top-ql-jimbob4-pp3
  TOP i2c_master_top
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/i2c_master_defines.v
    ${DESIGN_DIR}/i2c_master_bit_ctrl.v
    ${DESIGN_DIR}/i2c_master_byte_ctrl.v
    ${DESIGN_DIR}/i2c_master_top.v
    ${DESIGN_DIR}/StateMachine.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET

  ASSERT_USAGE PB-CLOCK=2,PB-GMUX=2,PB-LOGIC<=160
)

add_dependencies(all_ql_tests_bit   i2c_master_top-ql-jimbob4-pp3_bit)
add_dependencies(all_ql_tests_bit_v i2c_master_top-ql-jimbob4-pp3_bit_v)

add_dependencies(all_ql_tests_regression i2c_master_top-ql-jimbob4-pp3_assert_usage)

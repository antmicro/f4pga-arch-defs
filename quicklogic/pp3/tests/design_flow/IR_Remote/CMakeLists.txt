set(DESIGN_DIR ${QL_DESIGNS_DIR}/IR_Remote)

add_fpga_target(
  NAME IR_Remote-ql-jimbob4-pp3
  TOP top
  BOARD jimbob4-pp3
  SOURCES
    ${DESIGN_DIR}/i2cSlaveSerialInterface.v
    ${DESIGN_DIR}/i2cSlaveTop.v
    ${DESIGN_DIR}/i2cSlave.v
    ${DESIGN_DIR}/IR_Emitter_Carrier_Generator.v
    ${DESIGN_DIR}/IR_Emitter_Interface.v
    ${DESIGN_DIR}/IR_Emitter_Modulator.v
    ${DESIGN_DIR}/IR_Emitter_Registers.v
    ${DESIGN_DIR}/r1024x9_1024x9.v
    ${DESIGN_DIR}/IR_Remote.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET

  ASSERT_USAGE PB-CLOCK=1,PB-GMUX=1,PB-LOGIC<=383
)

add_dependencies(all_ql_tests_bit   IR_Remote-ql-jimbob4-pp3_bit)
#add_dependencies(all_ql_tests_bit_v IR_Remote-ql-jimbob4-pp3_bit_v)	# FIXME: List of connection types is empty (should have 1 element)

add_dependencies(all_ql_tests_regression IR_Remote-ql-jimbob4-pp3_assert_usage)

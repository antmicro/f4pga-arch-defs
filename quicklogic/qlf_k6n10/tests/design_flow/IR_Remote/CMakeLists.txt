set(IR_TOP ${QL_DESIGNS_DIR}/IR_Remote/IR_Remote.v)
set(FILE1 ${QL_DESIGNS_DIR}/IR_Remote/i2cSlave.v)
set(FILE2 ${QL_DESIGNS_DIR}/IR_Remote/i2cSlaveTop.v)
set(FILE3 ${QL_DESIGNS_DIR}/IR_Remote/i2cSlaveSerialInterface.v)
set(FILE4 ${QL_DESIGNS_DIR}/IR_Remote/r1024x9_1024x9.v)
set(FILE5 ${QL_DESIGNS_DIR}/IR_Remote/IR_Emitter_Carrier_Generator.v)
set(FILE6 ${QL_DESIGNS_DIR}/IR_Remote/IR_Emitter_Interface.v)
set(FILE7 ${QL_DESIGNS_DIR}/IR_Remote/IR_Emitter_Modulator.v)
set(FILE8 ${QL_DESIGNS_DIR}/IR_Remote/IR_Emitter_Registers.v)


add_fpga_target(
  NAME IR_Remote_test-gf12-no-adder
  TOP top
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${IR_TOP} ${FILE1} ${FILE2} ${FILE3} ${FILE4} ${FILE5} ${FILE6} ${FILE7} ${FILE8}
  EXPLICIT_ADD_FILE_TARGET
  DEFINES SYNTH_OPTS=-no_adder
  )

add_fpga_target(
  NAME IR_Remote_test-gf12-adder
  TOP top
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${IR_TOP} ${FILE1} ${FILE2} ${FILE3} ${FILE4} ${FILE5} ${FILE6} ${FILE7} ${FILE8}
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_qlf_k6n10_tests_no_adder IR_Remote_test-gf12-no-adder_route)
add_dependencies(all_qlf_k6n10_tests_adder    IR_Remote_test-gf12-adder_route)

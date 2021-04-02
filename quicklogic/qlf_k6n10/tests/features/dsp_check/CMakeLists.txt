set(DSP  dsp_check.v)
set(QLF_K6N10_GF12 qlf_k6n10-qlf_k6n10_gf12)

set(ROUTE_LOG ${CMAKE_CURRENT_BINARY_DIR}/dsp_check_test-gf12-adder/qlf_k6n10-${QLF_K6N10_GF12}-virt-${QLF_K6N10_GF12}-${QLF_K6N10_GF12}/route.log)

add_file_target(FILE ${DSP} SCANNER_TYPE verilog)

add_fpga_target(
  NAME dsp_check_test-gf12-adder
  TOP dsp_check
  BOARD qlf_k6n10-qlf_k6n10_gf12_board
  SOURCES ${DSP}
  EXPLICIT_ADD_FILE_TARGET
  )


add_dependencies(all_qlf_k6n10_tests_adder dsp_check)

add_custom_target(
  dsp_check
  COMMAND egrep -q -i "QL_DSP \+: 10" ${ROUTE_LOG} 
  DEPENDS dsp_check_test-gf12-adder_route
  )

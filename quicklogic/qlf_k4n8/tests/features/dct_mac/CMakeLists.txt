set(CURR_DIR ${QL_DESIGNS_DIR}/dct_mac)
add_file_target(FILE ${CURR_DIR}/dct_mac.v SCANNER_TYPE verilog)

add_fpga_target(
  NAME dct_mac_test-umc22-adder
  TOP dct_mac
  BOARD qlf_k4n8-qlf_k4n8_umc22_board
  SOURCES ${CURR_DIR}/dct_mac.v
  EXPLICIT_ADD_FILE_TARGET
  )

add_dependencies(all_qlf_k4n8_tests_adder    dct_mac_test-umc22-adder_bit)
#add_dependencies(verify dct_mac_test-umc22-adder_bit)
add_test(verify ${CMAKE_COMMAND} -P ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/${FAMILY}/utils/verify.cmake)
#add_test(verify ${CMAKE_COMMAND} -E compare_files route.log route1.log
#                 RESULT_VARIABLE compare_result
#)
#if( compare_result EQUAL 0)
#    message("The files are identical.")
#elseif( compare_result EQUAL 1)
#    message("The files are different.")
#else()
#    message("Error while comparing the files.")
#endif()

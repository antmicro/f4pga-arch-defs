add_custom_target(all_ql_tests_bit_v)
add_custom_target(all_ql_tests_bit)
add_custom_target(all_ql_tests_regression)
add_custom_target(all_ql_tests_prog)

add_dependencies(all_ql_tests_prog all_ql_tests_bit)

add_custom_target(all_ql_tests)
add_dependencies(all_quicklogic_tests all_ql_tests)
add_dependencies(all_ql_tests all_ql_tests_bit)
add_dependencies(all_ql_tests all_ql_tests_bit_v)
add_dependencies(all_ql_tests all_ql_tests_regression)

add_custom_target(all_quick_tests)

# A test for LUT -> LOGIC cell techmaps
add_subdirectory(techmaps)

# Tests for packing and placing primitives. Not to be run on actual HW !
add_subdirectory(wire)
add_subdirectory(lut)
add_subdirectory(consts)

# Test designs controlled by buttons
add_subdirectory(btn_xor)
add_subdirectory(btn_ff)
add_subdirectory(btn_counter)
add_subdirectory(sdiomux_xor)

# Tests that require an external clock/data
add_subdirectory(ext_counter)
#add_subdirectory(ext_mult)		# Too big (IO)

# Global clock network tests
#add_subdirectory(gclk_counter)		# get_target_property() called with non-existent target "file_quicklogic_pp3_tests_gclk_counter_SDC_FILE".

# Test designs that use clock
#add_subdirectory(counter)		# EOS-S3 specific macro (ASSP)
#add_subdirectory(soc_clocks)		# EOS-S3 specific macro (ASSP)
#add_subdirectory(sdiomux_counter)	# EOS-S3 specific macro (ASSP)

# More complex tests/examples that use the SoC interface.
#add_subdirectory(soc_litex_pwm)	# EOS-S3 specific macro (ASSP)

# QuickLogic test suite
add_subdirectory(design_flow)

# Hardblocks tests
add_subdirectory(ram)			# EOS-S3 specific macro (ASSP)
add_subdirectory(bram)			# Routing issues
add_subdirectory(mult)			# Failed to find matching architecture model for 'MULT'

add_subdirectory(features)

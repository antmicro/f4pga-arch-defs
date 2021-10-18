set(QL_DESIGNS_DIR ../../../../designs)

add_subdirectory(adder_8)
add_subdirectory(bin2bcd)
#add_subdirectory(bin2seven) # Causes ABC9 segfault: https://github.com/QuickLogic-Corp/symbiflow-arch-defs/issues/590
add_subdirectory(clock_tree_design)
add_subdirectory(counter_8bit)
add_subdirectory(counter_32bit)
add_subdirectory(Simon_bit_serial_top_module)
add_subdirectory(top_120_13)
add_subdirectory(jpeg_qnr)
add_subdirectory(counter_16bit)
add_subdirectory(multiplier_8bit)
add_subdirectory(shift_reg_576)
add_subdirectory(IR_Remote)
add_subdirectory(e_sdio_host_controller)
add_subdirectory(i2c_master_top)
add_subdirectory(iir)
add_subdirectory(osc_alu)
add_subdirectory(rgb2ycrcb)
add_subdirectory(rs_decoder_1)
add_subdirectory(sdio_client_top)
add_subdirectory(spi_master_top)
add_subdirectory(test_logic_cell)
add_subdirectory(unsigned_mult_50)


# Designs not working for PP3:
#add_subdirectory(dct_mac)		# VPR packing requires >32GB of RAM
#add_subdirectory(sha_top)		# FIXME: The design gets mostly pruned by Yosys
#add_subdirectory(smithwaterman)	# VPR packing requires >64GB of RAM
#add_subdirectory(sudoku_check)		# FIXME: missing the "dcfifo" module
#add_subdirectory(camif)		# Packing errors (RAM)
#add_subdirectory(cavlc_top)		# FIXME: Not enough resources after packing
#add_subdirectory(cf_fft_256_8)		# Too big (IO)
#add_subdirectory(sha256)		# Too big (device overfitted)
#add_subdirectory(unsigned_mult_80)	# Too big (IO)

#Testcases for the design flow
add_subdirectory(counter)
add_subdirectory(adder_8)
add_subdirectory(bram)

# The k6n10 architecture is too large, having a lot of testcase is stalling CI.
# Testcases will be enabled after test benchmark is set up.

#add_subdirectory(and2)
#add_subdirectory(and2_latch)
#add_subdirectory(bin2bcd)
#add_subdirectory(rs_decoder_1)
#add_subdirectory(unsigned_mult_80)
#add_subdirectory(adder_64)
#add_subdirectory(top_120_13)
#add_subdirectory(multiplier_8bit)
#add_subdirectory(shift_reg_8192)
#add_subdirectory(mac_16)

#The k6n10 architecture can be scaled up to be able to run
#Ressource consuming testcases below

#add_subdirectory(multi_enc_decx2x4) #1026 IO required

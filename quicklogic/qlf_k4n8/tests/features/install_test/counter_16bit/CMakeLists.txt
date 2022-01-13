add_binary_toolchain_test(
    TEST_NAME counter_16bit
    ARCH      qlf_k4n8
    DEVICE    qlf_k4n8
    PINMAP    pinmap_qlf_k4n8_umc22.csv
    EXTRA_ARGS "-dump post_verilog"

    ENABLE_SIMULATION

    ASSERT_USAGE  io=19,clb=6
    ASSERT_TIMING fmax>=156.0
)

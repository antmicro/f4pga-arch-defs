add_binary_toolchain_test(
    TEST_NAME lut2
    ARCH      pp3
    DEVICE    ql-eos-s3
    PINMAP    PD64
    EXTRA_ARGS "-dump post_verilog"

    ENABLE_SIMULATION
)

add_binary_toolchain_test(
    TEST_NAME lut2
    ARCH      pp3
    DEVICE    ql-pp3
    PINMAP    WD30
    PCF       jimbob4.pcf
    EXTRA_ARGS "-dump post_verilog"

    ENABLE_SIMULATION
)


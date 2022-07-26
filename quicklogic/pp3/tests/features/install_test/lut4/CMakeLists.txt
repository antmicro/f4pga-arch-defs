add_binary_toolchain_test(
    TEST_NAME lut4
    ARCH      pp3
    DEVICE    ql-eos-s3
    PINMAP    PD64
    PCF       chandalar.pcf
    EXTRA_ARGS "-dump post_verilog"

    ENABLE_SIMULATION
)

add_binary_toolchain_test(
    TEST_NAME counter
    DEVICE    ql-eos-s3
    PINMAP    chandalar_pinmap.csv
    EXTRA_ARGS "-dump post_verilog"
)

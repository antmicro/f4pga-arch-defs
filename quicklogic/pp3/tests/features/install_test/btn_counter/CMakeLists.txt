add_binary_toolchain_test(
    TEST_NAME btn_counter
    DEVICE    ql-eos-s3
    PINMAP    chandalar_pinmap.csv
    EXTRA_ARGS "-dump post_verilog"
)

add_binary_toolchain_test(
    TEST_NAME btn_counter
    DEVICE    ql-pp3
    PINMAP    WD30
    PCF       jimbob4.pcf
    EXTRA_ARGS "-dump post_verilog"
)

add_binary_toolchain_test(
    TEST_NAME lut1
    DEVICE    ql-eos-s3
    PINMAP    chandalar_pinmap.csv
)

add_binary_toolchain_test(
    TEST_NAME lut1
    DEVICE    ql-pp3
    PINMAP    WD30
    PCF       jimbob4.pcf
)


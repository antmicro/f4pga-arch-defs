add_binary_toolchain_test(
    TEST_NAME wire
    DEVICE    ql-eos-s3
    PINMAP    chandalar_pinmap.csv
)

add_binary_toolchain_test(
    TEST_NAME wire
    DEVICE    ql-pp3
    PINMAP    WD30
    PCF       jimbob4.pcf
)


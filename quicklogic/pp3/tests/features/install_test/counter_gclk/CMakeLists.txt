add_binary_toolchain_test(
    TEST_NAME counter_gclk
    DEVICE    ql-eos-s3
    PINMAP    PD64
    PCF       chandalar.pcf

    ASSERT_USAGE  PB-CLOCK=1,PB-GMUX=1,PB-BIDIR=4
    ASSERT_TIMING fmax>110.0
)

add_binary_toolchain_test(
    TEST_NAME counter_gclk
    DEVICE    ql-pp3
    PINMAP    WD30
    PCF       jimbob4.pcf

    ASSERT_USAGE  PB-CLOCK=1,PB-GMUX=1,PB-BIDIR=4
    ASSERT_TIMING fmax>110.0
)

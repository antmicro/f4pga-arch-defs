add_binary_toolchain_test(
    TEST_NAME counter_gclk
    DEVICE    ql-eos-s3
    PINMAP    PD64
    PCF       chandalar.pcf
    EXTRA_ARGS "-dump post_verilog"

    ASSERT_USAGE  PB-CLOCK=1,PB-GMUX=1,PB-BIDIR=4
    ASSERT_TIMING fmax>110.0

    ASSERT_EXISTS
        "top_post_synthesis.v"
        "top_post_synthesis.sdf"
        "top.bit.v"
        "top.bit.v.pcf"
)

add_binary_toolchain_test(
    TEST_NAME counter_gclk_wd30
    DEVICE    ql-pp3
    PINMAP    WD30
    PCF       jimbob4.pcf
    EXTRA_ARGS "-dump post_verilog"

    ASSERT_USAGE  PB-CLOCK=1,PB-GMUX=1,PB-BIDIR=4
    ASSERT_TIMING fmax>110.0

    ASSERT_EXISTS
        "top_post_synthesis.v"
        "top_post_synthesis.sdf"
        "top.bit.v"
        "top.bit.v.pcf"
)

add_binary_toolchain_test(
    TEST_NAME counter_gclk_pd64
    DEVICE    ql-pp3
    PINMAP    PD64
    PCF       pd64.pcf

    ASSERT_USAGE  PB-CLOCK=1,PB-GMUX=1,PB-BIDIR=4
    ASSERT_TIMING fmax>110.0
)


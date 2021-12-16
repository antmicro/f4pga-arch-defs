add_binary_toolchain_test(
    TEST_NAME counter_gclk
    ARCH      pp3
    DEVICE    ql-eos-s3
    PINMAP    PD64
    PCF       chandalar.pcf
    EXTRA_ARGS "-dump post_verilog"

    ENABLE_SIMULATION

    CHECK_CONSTRAINTS
    ASSERT_USAGE  PB-CLOCK=1,PB-GMUX=1,PB-BIDIR=4
    ASSERT_TIMING fmax>56.0

    ASSERT_EXISTS
        "top_post_synthesis.v"
        "top_post_synthesis.no_split.v"
        "top_post_synthesis.sdf"
        "top.bit.v"
        "top.bit.v.pcf"
)

add_binary_toolchain_test(
    TEST_NAME counter_gclk
    SOURCES   "counter_gclk.v"
    ARCH      pp3
    DEVICE    ql-pp3
    PINMAP    WD30
    PCF       jimbob4.pcf
    EXTRA_ARGS "-dump post_verilog"

    ENABLE_SIMULATION

    CHECK_CONSTRAINTS
    ASSERT_USAGE  PB-CLOCK=1,PB-GMUX=1,PB-BIDIR=4
    ASSERT_TIMING fmax>56.0

    ASSERT_EXISTS
        "top_post_synthesis.v"
        "top_post_synthesis.no_split.v"
        "top_post_synthesis.sdf"
        "top.bit.v"
        "top.bit.v.pcf"
)

add_binary_toolchain_test(
    TEST_NAME counter_gclk
    SOURCES   "counter_gclk.v"
    ARCH      pp3
    DEVICE    ql-pp3
    PINMAP    PD64
    PCF       pd64.pcf
    EXTRA_ARGS "-dump post_verilog"

    ENABLE_SIMULATION

    CHECK_CONSTRAINTS
    ASSERT_USAGE  PB-CLOCK=1,PB-GMUX=1,PB-BIDIR=4
    ASSERT_TIMING fmax>40.0

    ASSERT_EXISTS
        "top_post_synthesis.v"
        "top_post_synthesis.no_split.v"
        "top_post_synthesis.sdf"
        "top.bit.v"
        "top.bit.v.pcf"
)

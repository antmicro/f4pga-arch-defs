add_binary_toolchain_test(
    TEST_NAME counter
    ARCH      pp3
    DEVICE    ql-eos-s3
    PINMAP    PD64
    PCF       chandalar.pcf
    EXTRA_ARGS "-dump post_verilog"

    # Disabled due to errors in post VPR simulation with SDF annotation
    # Most probably caused by generation of faulty timings in SDF file
    #ENABLE_SIMULATION

    ASSERT_BLOCK_TYPES_ARE_USED  PB-CLOCK=0,PB-GMUX=0,PB-BIDIR=5
    ASSERT_TIMING fmax>=30.0
    CHECK_CONSTRAINTS

    ASSERT_EXISTS
        "top_post_synthesis.v"
        "top_merged_post_synthesis.v"
        "top_post_synthesis.sdf"
        "top.bit.v"
        "top.bit.v.pcf"
)

add_binary_toolchain_test(
    TEST_NAME counter
    ARCH      pp3
    SOURCES   counter.v
    DEVICE    ql-pp3
    PINMAP    WD30
    PCF       jimbob4.pcf
    EXTRA_ARGS "-dump post_verilog"

    ENABLE_SIMULATION

    ASSERT_BLOCK_TYPES_ARE_USED  PB-CLOCK=0,PB-GMUX=0,PB-BIDIR=5
    ASSERT_TIMING fmax>=30.0
    CHECK_CONSTRAINTS

    ASSERT_EXISTS
        "top_post_synthesis.v"
        "top_merged_post_synthesis.v"
        "top_post_synthesis.sdf"
        "top.bit.v"
        "top.bit.v.pcf"
)

add_binary_toolchain_test(
    TEST_NAME counter
    ARCH      pp3
    SOURCES   counter.v
    DEVICE    ql-pp3
    PINMAP    PD64
    PCF       pd64.pcf
    EXTRA_ARGS "-dump post_verilog"

    ENABLE_SIMULATION

    ASSERT_BLOCK_TYPES_ARE_USED  PB-CLOCK=0,PB-GMUX=0,PB-BIDIR=5
    ASSERT_TIMING fmax>=30.0
    CHECK_CONSTRAINTS

    ASSERT_EXISTS
        "top_post_synthesis.v"
        "top_merged_post_synthesis.v"
        "top_post_synthesis.sdf"
        "top.bit.v"
        "top.bit.v.pcf"
)

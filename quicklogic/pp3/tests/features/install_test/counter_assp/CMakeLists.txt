add_binary_toolchain_test(
    TEST_NAME counter_assp
    DEVICE    ql-eos-s3
    PINMAP    PD64
    PCF       chandalar.pcf

    ASSERT_USAGE PB-ASSP=1,PB-GMUX=1
)

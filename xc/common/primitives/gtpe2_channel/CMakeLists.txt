prjray_generate_primitive(
    PRJRAY_DB_DIR ${PRJXRAY_DB_DIR}
    PRIMITIVE gtpe2_channel
    PRE_BUILT_PB_TYPE gtpe2_channel.pre_built.pb_type.xml
    FILTER_CLOCK_DELAYS RXUSRCLK,TXUSRCLK
)

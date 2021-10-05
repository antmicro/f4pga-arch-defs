set(DESIGN_DIR ${QL_DESIGNS_DIR}/dct_mac)

add_file_target(FILE ${DESIGN_DIR}/timescale.v SCANNER_TYPE verilog)

add_fpga_target(
  NAME dct_mac-ql-jimbob4-pp3
  TOP dct_mac
  BOARD jimbob4-pp3
  SOURCES
    timescale.v
    ${DESIGN_DIR}/dct_cos_table.v
    ${DESIGN_DIR}/dct_syn.v
    ${DESIGN_DIR}/dctub.v
    ${DESIGN_DIR}/dctu.v
    ${DESIGN_DIR}/dct.v
    ${DESIGN_DIR}/fdct.v
    ${DESIGN_DIR}/zigzag.v
    ${DESIGN_DIR}/dct_mac.v
  INPUT_IO_FILE jimbob4.pcf
  AUTO_ADD_FILE_TARGET
)

# FIXME: design requires over 32GB of RAM for packing step
#add_dependencies(all_ql_tests_bit   dct_mac-ql-jimbob4-pp3_bit)
#add_dependencies(all_ql_tests_bit_v dct_mac-ql-jimbob4-pp3_bit_v)

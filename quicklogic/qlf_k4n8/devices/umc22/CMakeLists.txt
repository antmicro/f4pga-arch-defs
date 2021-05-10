set(ARCH qlf_k4n8)

quicklogic_define_qlf_device (
  NAME     ${ARCH}_umc22
  ARCH     ${ARCH}
  FAMILY   ${ARCH}
  LAYOUT   24x24
  ARCH_XML ${QLF_FPGA_DATABASE_DIR}/${ARCH}/vpr_arch/UMC22nm_vpr.xml
  RR_GRAPH ${QLF_FPGA_DATABASE_DIR}/${ARCH}/vpr_rr_graph/UMC22nm_vpr.bin.gz

  REPACKING_RULES ${QLF_FPGA_DATABASE_DIR}/${ARCH}/vpr_arch/repacking_rules.json

  ROUTE_CHAN_WIDTH 60
)

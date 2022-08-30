project_ray_prepare_database(
  PRJRAY_ARCH zynq7
  PRJRAY_DIR ${PRJXRAY_DIR}
  PRJRAY_DB_DIR ${PRJXRAY_DB_DIR}
  PROTOTYPE_PART xc7z020clg484-1
  PARTS xc7z020clg484-1
)

set(ARCH zynq7_z020)

add_xc_arch_define(
  ARCH ${ARCH}
  FAMILY xc7
  PRJRAY_DIR ${PRJXRAY_DIR}
  PRJRAY_DB_DIR ${PRJXRAY_DB_DIR}
  PRJRAY_NAME prjxray
  PRJRAY_ARCH zynq7
  PROTOTYPE_PART xc7z020clg484-1
  YOSYS_SYNTH_SCRIPT ${f4pga-arch-defs_SOURCE_DIR}/xc7/yosys/synth.tcl
  YOSYS_CONV_SCRIPT ${f4pga-arch-defs_SOURCE_DIR}/xc7/yosys/conv.tcl
)

add_subdirectory(tiles)
add_subdirectory(devices)

get_target_property_required(VPR_ARCH_ARGS ${ARCH} VPR_ARCH_ARGS)
define_xc_toolchain_target(
  ARCH ${ARCH}
  ROUTE_CHAN_WIDTH 500
  VPR_ARCH_ARGS ${VPR_ARCH_ARGS}
)

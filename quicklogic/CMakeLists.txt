set(QLF_FPGA_DATABASE_DIR ${symbiflow-arch-defs_SOURCE_DIR}/third_party/qlfpga-symbiflow-plugins)

add_subdirectory(common)

add_subdirectory(qlf_k4n8)
add_subdirectory(qlf_k6n10)

add_subdirectory(pp3)

set(QLF_FPGA_DATABASE_DIR ${symbiflow-arch-defs_SOURCE_DIR}/third_party/qlfpga-symbiflow-plugins)

# Collective target for all Python tests
add_custom_target(all_quicklogic_python_tests)
add_dependencies(all_quicklogic_tests all_quicklogic_python_tests)


add_subdirectory(common)

add_subdirectory(qlf_k4n8)
add_subdirectory(qlf_k6n10)

add_subdirectory(pp3)

function(DEFINE_QL_TOOLCHAIN_TARGET)
  set(options)
  set(oneValueArgs ARCH CONV_SCRIPT SYNTH_SCRIPT ROUTE_CHAN_WIDTH CELLS_SIM)
  set(multiValueArgs VPR_ARCH_ARGS)

  cmake_parse_arguments(
    DEFINE_QL_TOOLCHAIN_TARGET
    "${options}"
    "${oneValueArgs}"
    "${multiValueArgs}"
    "${ARGN}"
  )

  get_target_property_required(VPR env VPR)
  get_target_property(VPR_TARGET env VPR_TARGET)
  get_target_property_required(GENFASM env GENFASM)
  get_target_property(GENFASM_TARGET env GENFASM_TARGET)

  set(ARCH ${DEFINE_QL_TOOLCHAIN_TARGET_ARCH})
  set(VPR_ARCH_ARGS ${DEFINE_QL_TOOLCHAIN_TARGET_VPR_ARCH_ARGS})
  set(ROUTE_CHAN_WIDTH ${DEFINE_QL_TOOLCHAIN_TARGET_ROUTE_CHAN_WIDTH})
  list(JOIN VPR_BASE_ARGS " " VPR_BASE_ARGS)
  string(JOIN " " VPR_ARGS ${VPR_BASE_ARGS} "--route_chan_width ${ROUTE_CHAN_WIDTH}" ${VPR_ARCH_ARGS})
  get_target_property_required(FASM_TO_BIT ${ARCH} FASM_TO_BIT)

  get_file_target(FASM_TO_BIT_TARGET ${FASM_TO_BIT})
  # Add fasm2bit to all deps, so it is installed with make install
  add_custom_target(
    "DEVICE_INSTALL_${FASM_TO_BIT_TARGET}"
    ALL
    DEPENDS ${FASM_TO_BIT}
    )

  get_file_target(CELLS_SIM_TARGET ${DEFINE_QL_TOOLCHAIN_TARGET_CELLS_SIM})
  # Add cells.sim to all deps, so it is installed with make install
  add_custom_target(
    "DEVICE_INSTALL_${CELLS_SIM_TARGET}"
    ALL
    DEPENDS ${DEFINE_QL_TOOLCHAIN_TARGET_CELLS_SIM}
    )

  set(WRAPPERS env generate_constraints pack place route synth write_bitstream write_fasm write_jlink write_bitheader write_fasm2bels generate_fasm2bels ql_symbiflow)
  set(TOOLCHAIN_WRAPPERS)

  foreach(WRAPPER ${WRAPPERS})
    set(WRAPPER_PATH "${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/toolchain_wrappers/${WRAPPER}")
    list(APPEND TOOLCHAIN_WRAPPERS ${WRAPPER_PATH})
  endforeach()

  set(VPR_COMMON_TEMPLATE "${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/toolchain_wrappers/vpr_common")
  set(VPR_COMMON "${CMAKE_CURRENT_BINARY_DIR}/vpr_common")
  configure_file(${VPR_COMMON_TEMPLATE} "${VPR_COMMON}" @ONLY)

  install(FILES ${TOOLCHAIN_WRAPPERS} ${VPR_COMMON}
          DESTINATION bin
          PERMISSIONS WORLD_EXECUTE WORLD_READ OWNER_WRITE OWNER_READ OWNER_EXECUTE GROUP_READ GROUP_EXECUTE)

  # install python scripts
  install(FILES ${FASM_TO_BIT}
          DESTINATION bin/python
          PERMISSIONS WORLD_EXECUTE WORLD_READ OWNER_WRITE OWNER_READ OWNER_EXECUTE GROUP_READ GROUP_EXECUTE)

  install(DIRECTORY ${symbiflow-arch-defs_SOURCE_DIR}/third_party/fasm
          DESTINATION bin/python)

  install(FILES ${symbiflow-arch-defs_SOURCE_DIR}/utils/split_inouts.py
          DESTINATION bin/python
          PERMISSIONS WORLD_EXECUTE WORLD_READ OWNER_WRITE OWNER_READ OWNER_EXECUTE GROUP_READ GROUP_EXECUTE)

  install(FILES ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/utils/create_ioplace.py
          DESTINATION bin/python
          PERMISSIONS WORLD_EXECUTE WORLD_READ OWNER_WRITE OWNER_READ OWNER_EXECUTE GROUP_READ GROUP_EXECUTE)

  install(FILES ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/utils/fasm2bels.py
          DESTINATION bin/python
          PERMISSIONS WORLD_EXECUTE WORLD_READ OWNER_WRITE OWNER_READ OWNER_EXECUTE GROUP_READ GROUP_EXECUTE)

  install(FILES ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/utils/connections.py
          DESTINATION bin/python
          PERMISSIONS WORLD_EXECUTE WORLD_READ OWNER_WRITE OWNER_READ OWNER_EXECUTE GROUP_READ GROUP_EXECUTE)

  install(FILES ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/utils/data_structs.py
          DESTINATION bin/python
          PERMISSIONS WORLD_EXECUTE WORLD_READ OWNER_WRITE OWNER_READ OWNER_EXECUTE GROUP_READ GROUP_EXECUTE)

  install(FILES ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/utils/timing.py
          DESTINATION bin/python
          PERMISSIONS WORLD_EXECUTE WORLD_READ OWNER_WRITE OWNER_READ OWNER_EXECUTE GROUP_READ GROUP_EXECUTE)

  install(FILES ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/utils/tile_import.py
          DESTINATION bin/python
          PERMISSIONS WORLD_EXECUTE WORLD_READ OWNER_WRITE OWNER_READ OWNER_EXECUTE GROUP_READ GROUP_EXECUTE)

  install(FILES ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/utils/utils.py
          DESTINATION bin/python
          PERMISSIONS WORLD_EXECUTE WORLD_READ OWNER_WRITE OWNER_READ OWNER_EXECUTE GROUP_READ GROUP_EXECUTE)

  install(FILES ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/utils/verilogmodule.py
          DESTINATION bin/python
          PERMISSIONS WORLD_EXECUTE WORLD_READ OWNER_WRITE OWNER_READ OWNER_EXECUTE GROUP_READ GROUP_EXECUTE)

  install(FILES ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/utils/eos_s3_iomux_config.py
          DESTINATION bin/python
          PERMISSIONS WORLD_EXECUTE WORLD_READ OWNER_WRITE OWNER_READ OWNER_EXECUTE GROUP_READ GROUP_EXECUTE)

  install(FILES ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/utils/quicklogic-fasm/quicklogic_fasm/bitstream_to_jlink.py
          DESTINATION bin/python
          PERMISSIONS WORLD_EXECUTE WORLD_READ OWNER_WRITE OWNER_READ OWNER_EXECUTE GROUP_READ GROUP_EXECUTE)

  install(FILES ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/utils/quicklogic-fasm/quicklogic_fasm/bitstream_to_header.py
	  DESTINATION bin/python
          PERMISSIONS WORLD_EXECUTE WORLD_READ OWNER_WRITE OWNER_READ OWNER_EXECUTE GROUP_READ GROUP_EXECUTE)

  install(FILES ${symbiflow-arch-defs_SOURCE_DIR}/build/quicklogic/devices/ql-eos-s3-virt/db_phy.pickle
	  DESTINATION share/arch/ql-eos-s3_wlcsp
          PERMISSIONS WORLD_READ OWNER_WRITE OWNER_READ GROUP_READ )

  install(FILES ${symbiflow-arch-defs_SOURCE_DIR}/utils/vpr_io_place.py
	  DESTINATION bin/python
          PERMISSIONS WORLD_EXECUTE WORLD_READ OWNER_WRITE OWNER_READ OWNER_EXECUTE GROUP_READ GROUP_EXECUTE)

  install(FILES ${symbiflow-arch-defs_SOURCE_DIR}/utils/vpr_place_constraints.py
          DESTINATION bin/python
          PERMISSIONS WORLD_EXECUTE WORLD_READ OWNER_WRITE OWNER_READ OWNER_EXECUTE GROUP_READ GROUP_EXECUTE)

  install(FILES ${symbiflow-arch-defs_SOURCE_DIR}/utils/eblif.py
          DESTINATION bin/python
          PERMISSIONS WORLD_EXECUTE WORLD_READ OWNER_WRITE OWNER_READ OWNER_EXECUTE GROUP_READ GROUP_EXECUTE)

  install(FILES ${symbiflow-arch-defs_SOURCE_DIR}/utils/lib/parse_pcf.py
          DESTINATION bin/python/lib)

  # install techmap
  install(DIRECTORY ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/techmap
          DESTINATION share/techmaps/quicklogic)

  install(FILES ${DEFINE_QL_TOOLCHAIN_TARGET_CELLS_SIM}
          DESTINATION share/techmaps/quicklogic/techmap)

  # install Yosys scripts
  install(FILES  ${DEFINE_QL_TOOLCHAIN_TARGET_CONV_SCRIPT} ${DEFINE_QL_TOOLCHAIN_TARGET_SYNTH_SCRIPT}
    DESTINATION share/quicklogic)

endfunction()

function(DEFINE_QL_PINMAP_CSV_INSTALL_TARGET)
  set(options)
  set(oneValueArgs PART DEVICE_TYPE BOARD DEVICE PACKAGE FABRIC_PACKAGE)
  set(multiValueArgs)

  cmake_parse_arguments(
    DEFINE_QL_PINMAP_CSV_INSTALL_TARGET
    "${options}"
    "${oneValueArgs}"
    "${multiValueArgs}"
    "${ARGN}"
  )

  set(PART ${DEFINE_QL_PINMAP_CSV_INSTALL_TARGET_PART})
  set(BOARD ${DEFINE_QL_PINMAP_CSV_INSTALL_TARGET_BOARD})
  set(DEVICE ${DEFINE_QL_PINMAP_CSV_INSTALL_TARGET_DEVICE})
  set(DEVICE_TYPE ${DEFINE_QL_PINMAP_CSV_INSTALL_TARGET_DEVICE_TYPE})
  set(PACKAGE ${DEFINE_QL_PINMAP_CSV_INSTALL_TARGET_PACKAGE})

  get_target_property_required(PINMAP ${BOARD} PINMAP)
  get_file_location(PINMAP_FILE ${PINMAP})
  get_filename_component(PINMAP_FILE_NAME ${PINMAP_FILE} NAME)
  append_file_dependency(DEPS ${PINMAP})
  add_custom_target(
    "PINMAP_INSTALL_${BOARD}_${DEVICE}_${PACKAGE}_${PINMAP_FILE_NAME}"
    ALL
    DEPENDS ${DEPS}
    )
  install(FILES ${PINMAP_FILE}
    DESTINATION "share/arch/${DEVICE}_${PACKAGE}/${PART}"
    RENAME "pinmap_${ADD_QUICKLOGIC_BOARD_FABRIC_PACKAGE}.csv")
endfunction()

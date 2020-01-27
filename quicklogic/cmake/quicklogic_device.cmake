function(DEFINE_QUICKLOGIC_DEVICE)

#  set(options )
  set(oneValueArgs DEVICE ARCH GRID_LIMIT)
  set(multiValueArgs PACKAGES)
  cmake_parse_arguments(
    DEFINE_QUICKLOGIC_DEVICE
    "${options}"
    "${oneValueArgs}"
    "${multiValueArgs}"
    ${ARGN}
  )

  set(DEVICE ${DEFINE_QUICKLOGIC_DEVICE_DEVICE})
  set(ARCH ${DEFINE_QUICKLOGIC_DEVICE_ARCH})
  set(PACKAGES ${DEFINE_QUICKLOGIC_DEVICE_PACKAGES})

  set(DEVICE_TYPE ${DEVICE}-virt)

  get_target_property_required(PYTHON3 env PYTHON3)
  get_target_property_required(PYTHON3_TARGET env PYTHON3_TARGET)

  set(TECHFILE "${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/QLAL4S3B.xml")
  set(PHY_DB_FILE "db_phy.pickle")
  set(VPR_DB_FILE "db_vpr.pickle")
  set(ARCH_XML "arch.xml")

  # Import data from the techfile
  set(DATA_IMPORT ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/utils/data_import.py)
  add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${PHY_DB_FILE}
    COMMAND ${PYTHON3} ${DATA_IMPORT}
      --techfile ${TECHFILE}
      --db ${PHY_DB_FILE}
    DEPENDS ${TECHFILE} ${DATA_IMPORT} ${PYTHON3_TARGET}
  )
  add_file_target(FILE ${PHY_DB_FILE} GENERATED)

  # Process the database, create the VPR database
  set(PREPARE_VPR_DATABASE ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/utils/prepare_vpr_database.py)

  if(NOT "${DEFINE_QUICKLOGIC_DEVICE_GRID_LIMIT}" STREQUAL "")
    separate_arguments(GRID_LIMIT_ARGS UNIX_COMMAND "--grid-limit ${DEFINE_QUICKLOGIC_DEVICE_GRID_LIMIT}")
  else()
    set(GRID_LIMIT_ARGS "")
  endif()

  add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${VPR_DB_FILE}
    COMMAND ${PYTHON3} ${PREPARE_VPR_DATABASE}
      --phy-db ${PHY_DB_FILE}
      --vpr-db ${VPR_DB_FILE}
      ${GRID_LIMIT_ARGS}
    DEPENDS ${PHY_DB_FILE} ${PREPARE_VPR_DATABASE} ${PYTHON3_TARGET}
  )
  add_file_target(FILE ${VPR_DB_FILE} GENERATED)

  # Generate the arch.xml
  set(ARCH_IMPORT ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/utils/arch_import.py)
  add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${ARCH_XML}
    COMMAND ${PYTHON3} ${ARCH_IMPORT}
      --vpr-db ${VPR_DB_FILE}
      --arch-out ${ARCH_XML}
      --device ${DEVICE}
    DEPENDS ${VPR_DB_FILE} ${ARCH_IMPORT} ${PYTHON3_TARGET}
  )
  add_file_target(FILE ${ARCH_XML} GENERATED)
 
  # Define the device type
  define_device_type(
    DEVICE_TYPE ${DEVICE_TYPE}
    ARCH ${ARCH}
    ARCH_XML ${ARCH_XML}
    UPDATE_TILES
  )

  # Define the device
  define_device(
    DEVICE ${DEVICE}
    ARCH ${ARCH}
    DEVICE_TYPE ${DEVICE_TYPE}
    PACKAGES ${PACKAGES}
    WIRE_EBLIF ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/dummy.eblif
    CACHE_PLACE_DELAY
    CACHE_ARGS
      --route_chan_width 100
      --clock_modeling route
      --allow_unrelated_clustering off
      --target_ext_pin_util 0.7
      --router_init_wirelength_abort_threshold 2
      --congested_routing_iteration_threshold 0.8
  )

endfunction()

function(QUICKLOGIC_DEFINE_DEVICE_TYPE)
  # ~~~
  # QUICKLOGIC_DEFINE_DEVICE_TYPE(
  #   ARCH <arch>
  #   DEVICE <device>
  #   PACKAGES <package> <package> ...
  #   [GRID_LIMIT <xmin>,<ymin>,<xmax>,<ymax>]
  #   PB_TYPES <pb_type> <pb_type> ...
  #   TECHFILE_NAME <techfile name>
  #   ROUTING_TIMING_FILE_NAME <routing timing CSV file>
  #   LIB_TIMING_FILES <list timing lib files [can be wildcard]>
  #   )
  # ~~~
  set(options)
  set(oneValueArgs DEVICE ARCH GRID_LIMIT TECHFILE_NAME ROUTING_TIMING_FILE_NAME)
  set(multiValueArgs PACKAGES PB_TYPES LIB_TIMING_FILES)
  cmake_parse_arguments(
    QUICKLOGIC_DEFINE_DEVICE_TYPE
    "${options}"
    "${oneValueArgs}"
    "${multiValueArgs}"
    ${ARGN}
  )

  set(TECHFILE_NAME ${QUICKLOGIC_DEFINE_DEVICE_TYPE_TECHFILE_NAME})
  set(DEVICE ${QUICKLOGIC_DEFINE_DEVICE_TYPE_DEVICE})
  set(ARCH ${QUICKLOGIC_DEFINE_DEVICE_TYPE_ARCH})
  set(GRID_LIMIT ${QUICKLOGIC_DEFINE_DEVICE_TYPE_GRID_LIMIT})
  set(PB_TYPES ${QUICKLOGIC_DEFINE_DEVICE_TYPE_PB_TYPES})
  set(ROUTING_TIMING_FILE_NAME ${QUICKLOGIC_DEFINE_DEVICE_TYPE_ROUTING_TIMING_FILE_NAME})
  set(LIB_TIMING_FILES ${QUICKLOGIC_DEFINE_DEVICE_TYPE_LIB_TIMING_FILES})

  set(DEVICE_TYPE ${DEVICE}-virt)

  get_target_property_required(PYTHON3 env PYTHON3)
  get_target_property_required(PYTHON3_TARGET env PYTHON3_TARGET)

  set(PHY_DB_FILE "db_phy.pickle")
  set(VPR_DB_FILE "db_vpr.pickle")
  set(ARCH_XML "arch.xml")

  # The techfile and routing timing file
  set(TECHFILE "${symbiflow-arch-defs_SOURCE_DIR}/third_party/${DEVICE}/Device Architecture Files/${TECHFILE_NAME}")
  set(ROUTING_TIMING "${symbiflow-arch-defs_SOURCE_DIR}/third_party/${DEVICE}/Timing Data Files/${ROUTING_TIMING_FILE_NAME}")

  # Import data from the techfile
  set(DATA_IMPORT ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/utils/data_import.py)
  add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${PHY_DB_FILE}
    COMMAND ${PYTHON3} ${DATA_IMPORT}
      --techfile ${TECHFILE}
      --routing-timing ${ROUTING_TIMING}
      --db ${PHY_DB_FILE}
    DEPENDS ${TECHFILE} ${ROUTING_TIMING} ${DATA_IMPORT} ${PYTHON3_TARGET}
  )
  add_file_target(FILE ${PHY_DB_FILE} GENERATED)

  # Process the database, create the VPR database
  set(PREPARE_VPR_DATABASE ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/utils/prepare_vpr_database.py)

  if(NOT "${GRID_LIMIT}" STREQUAL "")
    separate_arguments(GRID_LIMIT_ARGS UNIX_COMMAND "--grid-limit ${GRID_LIMIT}")
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

  # Get dependencies for arch.xml
  set(XML_DEPS "")
  foreach(PB_TYPE ${PB_TYPES})
    string(TOLOWER ${PB_TYPE} PB_TYPE_LOWER)
    set(PB_TYPE_XML ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/primitives/${PB_TYPE_LOWER}/${PB_TYPE_LOWER}.pb_type.xml)
    set(MODEL_XML   ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/primitives/${PB_TYPE_LOWER}/${PB_TYPE_LOWER}.model.xml)
    append_file_dependency(XML_DEPS ${PB_TYPE_XML})
    append_file_dependency(XML_DEPS ${MODEL_XML})
  endforeach()

  # Generate SDF files with timing data
  set(LIB_TIMING_DIR "${symbiflow-arch-defs_SOURCE_DIR}/third_party/${DEVICE}/Timing Data Files/")
  set(SDF_TIMING_DIR "sdf")

  get_target_property_required(QUICKLOGIC_TIMINGS_IMPORTER env QUICKLOGIC_TIMINGS_IMPORTER)
  get_target_property_required(QUICKLOGIC_TIMINGS_IMPORTER_TARGET env QUICKLOGIC_TIMINGS_IMPORTER_TARGET)
  
  # TODO: How to handle different timing cases that depend on a cell config?
  # For example BIDIR cells have different timings for different voltages.
  #
  # One idea is to have a different model for each in VPR.
  #
  # For now only files with the worst case scenario timings are taken.
  set(TIMING_FILES "")
  foreach(LIB ${LIB_TIMING_FILES})

    file(GLOB TIMING_FILE
      "${LIB_TIMING_DIR}/${LIB}"
    )
    list(APPEND TIMING_FILES ${TIMING_FILE})
  endforeach()

  set(SDF_FILE_TARGETS "")
  foreach(LIB_TIMING_FILE ${TIMING_FILES})

    get_filename_component(FILE_NAME ${LIB_TIMING_FILE} NAME)
    get_filename_component(FILE_TITLE ${FILE_NAME} NAME_WE)

    set(SDF_TIMING_FILE ${SDF_TIMING_DIR}/${FILE_TITLE}.sdf)

    set(IMPORTER_DIR ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/utils/quicklogic-timings-importer/quicklogic_timings_importer)
    set(IMPORTER ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/utils/quicklogic-timings-importer/quicklogic_timings_importer/quicklogic_timings_importer.py)
    add_custom_command(
      OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${SDF_TIMING_FILE}
      COMMAND ${CMAKE_COMMAND} -E make_directory ${SDF_TIMING_DIR}
      COMMAND ${CMAKE_COMMAND} -E env PYTHONPATH=${IMPORTER_DIR}:$PYTHONPATH
        ${PYTHON3} ${IMPORTER}
        ${LIB_TIMING_FILE}
        ${SDF_TIMING_FILE}
      DEPENDS ${PYTHON3} ${PYTHON3_TARGET} ${QUICKLOGIC_TIMINGS_IMPORTER_TARGET} ${LIB_TIMING_FILE}
    )

    add_file_target(FILE ${SDF_TIMING_FILE} GENERATED)
    append_file_dependency(SDF_FILE_TARGETS ${SDF_TIMING_FILE})

  endforeach()

  # Generate model and pb_type XML for RAM
  # This will generate model XML and pb_type XMLs. Since there are 4 RAMs
  # there will be one pb_type for each of them with appropriate timings. Since
  # we cannot model that in the VPR for now we simply use one for all 4 RAMs.
  set(RAM_GENERATOR ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/primitives/ram/make_rams.py)
  set(RAM_MODE_DEFS ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/primitives/ram/ram_modes.json)
  set(RAM_SDF_FILE  ${SDF_TIMING_DIR}/RAM_ss_0p990v_m040c.sdf) # FIXME: Look for the file in the step above !

  set(RAM_MODEL_XML  "ram.model.xml")
  set(RAM_PBTYPE_XML "ram.pb_type.xml")

  set(RAM_CELLS_SIM  "ram_sim.v")
  set(RAM_CELLS_MAP  "ram_map.v")

  get_file_target(RAM_SDF_FILE_TARGET ${RAM_SDF_FILE})

  add_custom_command(
      OUTPUT ${RAM_MODEL_XML} ${RAM_PBTYPE_XML} ${RAM_CELLS_SIM} ${RAM_CELLS_MAP}
      COMMAND ${PYTHON3} ${RAM_GENERATOR}
          --sdf ${RAM_SDF_FILE}
          --mode-defs ${RAM_MODE_DEFS}
          --xml-path ${CMAKE_CURRENT_BINARY_DIR}
          --vlog-path ${CMAKE_CURRENT_BINARY_DIR}
      COMMAND ${CMAKE_COMMAND} -E copy "ram_a1.pb_type.xml" ${RAM_PBTYPE_XML}
      DEPENDS ${PYTHON3} ${PYTHON3_TARGET} ${RAM_GENERATOR} ${RAM_MODE_DEFS} ${RAM_SDF_FILE_TARGET}
  )

  add_file_target(FILE ${RAM_MODEL_XML} GENERATED)
  add_file_target(FILE ${RAM_PBTYPE_XML} GENERATED)

  add_file_target(FILE ${RAM_CELLS_SIM} GENERATED)
  add_file_target(FILE ${RAM_CELLS_MAP} GENERATED)

  # Generate the arch.xml
  set(ARCH_IMPORT ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/utils/arch_import.py)
  get_file_target(RAM_MODEL_XML_TARGET ${RAM_MODEL_XML})
  get_file_target(RAM_PBTYPE_XML_TARGET ${RAM_PBTYPE_XML})

  add_custom_command(
    OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/${ARCH_XML}
    COMMAND ${PYTHON3} ${ARCH_IMPORT}
      --vpr-db ${VPR_DB_FILE}
      --arch-out ${ARCH_XML}
      --device ${DEVICE}
    DEPENDS ${VPR_DB_FILE} ${XML_DEPS} ${ARCH_IMPORT} ${PYTHON3_TARGET} ${RAM_MODEL_XML_TARGET} ${RAM_PBTYPE_XML_TARGET}
  )
  add_file_target(FILE ${ARCH_XML} GENERATED)

  # Timing import stuff
  set(UPDATE_ARCH_TIMINGS ${symbiflow-arch-defs_SOURCE_DIR}/utils/update_arch_timings.py)
  set(PYTHON_SDF_TIMING_DIR ${symbiflow-arch-defs_SOURCE_DIR}/third_party/python-sdf-timing)
  get_target_property(SDF_TIMING_TARGET env SDF_TIMING_TARGET)

  set(BELS_MAP ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/${DEVICE}-bels.json)

  set(TIMING_IMPORT
    "${CMAKE_COMMAND} -E env PYTHONPATH=${PYTHON_SDF_TIMING_DIR}:$PYTHONPATH \
    ${PYTHON3} ${UPDATE_ARCH_TIMINGS} \
        --sdf_dir ${SDF_TIMING_DIR} \
        --bels_map ${BELS_MAP} \
        --out_arch /dev/stdout \
        --input_arch /dev/stdin \
    ")

  set(TIMING_DEPS ${SDF_TIMING_TARGET} sdf_timing ${SDF_FILE_TARGETS} ${BELS_MAP})

  # Define the device type
  define_device_type(
    DEVICE_TYPE ${DEVICE_TYPE}
    ARCH ${ARCH}
    ARCH_XML ${ARCH_XML}
    SCRIPT_OUTPUT_NAME timing
    SCRIPTS TIMING_IMPORT
    SCRIPT_DEPS TIMING_DEPS
  )

  # Set the device type properties
  if(NOT "${GRID_LIMIT}" STREQUAL "")
    set_target_properties(${DEVICE_TYPE} PROPERTIES USE_ROI TRUE)
  else()
    set_target_properties(${DEVICE_TYPE} PROPERTIES USE_ROI FALSE)
  endif()

  set_target_properties(
    ${DEVICE_TYPE}
    PROPERTIES
    VPR_DB_FILE ${CMAKE_CURRENT_SOURCE_DIR}/${VPR_DB_FILE}
    CELLS_SIM ${CMAKE_CURRENT_SOURCE_DIR}/${RAM_CELLS_SIM}
    CELLS_MAP ${CMAKE_CURRENT_SOURCE_DIR}/${RAM_CELLS_MAP}
  )

endfunction()


function(QUICKLOGIC_DEFINE_DEVICE)
  # ~~~
  # QUICKLOGIC_DEFINE_DEVICE(
  #   ARCH <arch>
  #   DEVICES <device> <device> ...
  #   PACKAGES <package> <package> ...
  #   )
  # ~~~
  set(options)
  set(oneValueArgs ARCH)
  set(multiValueArgs DEVICES PACKAGES)
  cmake_parse_arguments(
    QUICKLOGIC_DEFINE_DEVICE
     "${options}"
     "${oneValueArgs}"
     "${multiValueArgs}"
     ${ARGN}
   )

  set(ARCH ${QUICKLOGIC_DEFINE_DEVICE_ARCH})
  set(DEVICES ${QUICKLOGIC_DEFINE_DEVICE_DEVICES})
  set(PACKAGES ${QUICKLOGIC_DEFINE_DEVICE_PACKAGES})

  # For each device specified
  list(LENGTH DEVICES DEVICE_COUNT)
  math(EXPR DEVICE_COUNT_N_1 "${DEVICE_COUNT} - 1")
  foreach(INDEX RANGE ${DEVICE_COUNT_N_1})
    list(GET DEVICES ${INDEX} DEVICE)

    # Include the device type subdirectory
    set(DEVICE_TYPE ${DEVICE}-virt)
    add_subdirectory(${DEVICE_TYPE})

    # Get the VPR db file to add as dependency to RR graph patch
    get_target_property_required(VPR_DB_FILE ${DEVICE_TYPE} VPR_DB_FILE)

    # RR graph patch dependencies
    set(DEVICE_RR_PATCH_DEPS "")
    append_file_dependency(DEVICE_RR_PATCH_DEPS ${VPR_DB_FILE})

    # Define the device
    define_device(
      DEVICE ${DEVICE}
      ARCH ${ARCH}
      DEVICE_TYPE ${DEVICE_TYPE}
      PACKAGES ${PACKAGES}
      WIRE_EBLIF ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/passthrough.eblif
      RR_PATCH_DEPS ${DEVICE_RR_PATCH_DEPS}
      CACHE_PLACE_DELAY
      CACHE_ARGS
        --constant_net_method route
        --clock_modeling route
        --place_delay_model delta_override
#       FIXME: Once the timing model works correctly, figure out why the route lookahead fails to find some connections.
#        --router_lookahead connection_box_map
        --router_lookahead map
        --disable_errors check_unbuffered_edges:check_route:check_place
        --suppress_warnings sum_pin_class:check_unbuffered_edges:load_rr_indexed_data_T_values:check_rr_node:trans_per_R:set_rr_graph_tool_comment
        --route_chan_width 500
        --allow_dangling_combinational_nodes on
        --allowed_tiles_for_delay_model TL-LOGIC # TODO: Make this a parameter !
    )

  endforeach()
endfunction()

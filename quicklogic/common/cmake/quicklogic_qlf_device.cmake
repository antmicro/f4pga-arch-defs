function(QUICKLOGIC_DEFINE_QLF_DEVICE)
  # ~~~
  # QUICKLOGIC_DEFINE_QLF_DEVICE(
  #   NAME <name>
  #   FAMILY <family>
  #   ARCH <arch>
  #   ARCH_XML <arch.xml>
  #   RR_GRAPH <rr_graph>
  #   [ROUTE_CHAN_WIDTH <route channel width>]
  #   )
  # ~~~
  set(options)
  set(oneValueArgs NAME FAMILY ARCH ARCH_XML LAYOUT RR_GRAPH ROUTE_CHAN_WIDTH)
  set(multiValueArgs)
  cmake_parse_arguments(
    QUICKLOGIC_DEFINE_QLF_DEVICE
     "${options}"
     "${oneValueArgs}"
     "${multiValueArgs}"
     ${ARGN}
   )

  # Get args
  set(NAME     ${QUICKLOGIC_DEFINE_QLF_DEVICE_NAME})
  set(FAMILY   ${QUICKLOGIC_DEFINE_QLF_DEVICE_FAMILY})
  set(ARCH     ${QUICKLOGIC_DEFINE_QLF_DEVICE_ARCH})
  set(ARCH_XML ${QUICKLOGIC_DEFINE_QLF_DEVICE_ARCH_XML})
  set(RR_GRAPH ${QUICKLOGIC_DEFINE_QLF_DEVICE_RR_GRAPH})

  # If ROUTE_CHAN_WIDTH is not given then use the value from the architecture
  if("${QUICKLOGIC_DEFINE_QLF_DEVICE_ROUTE_CHAN_WIDTH}" STREQUAL "")
    get_target_property_required(ROUTE_CHAN_WIDTH ${ARCH} ROUTE_CHAN_WIDTH)
  else()
    set(ROUTE_CHAN_WIDTH ${QUICKLOGIC_DEFINE_QLF_DEVICE_ROUTE_CHAN_WIDTH})
  endif()

  get_target_property_required(PYTHON3 env PYTHON3)

  # Format device name and device type name
  set(DEVICE "${ARCH}-${NAME}")
  set(DEVICE_TYPE ${DEVICE}-virt)

  set(PACKAGE ${DEVICE})

  # .......................................................

  # Link VPR arch XML
  #get_filename_component(ARCH_XML_NAME ${ARCH_XML} NAME)
  set(ARCH_XML_NAME ${DEVICE}.arch.xml)

  add_custom_command(
    OUTPUT
      ${CMAKE_CURRENT_BINARY_DIR}/${ARCH_XML_NAME}
    DEPENDS
      ${ARCH_XML}
    COMMAND
      ${CMAKE_COMMAND} -E create_symlink
        ${ARCH_XML}
        ${CMAKE_CURRENT_BINARY_DIR}/${ARCH_XML_NAME}
  )

  add_file_target(FILE ${ARCH_XML_NAME} GENERATED)

  # .......................................................

  set(RR_GRAPH_FOR_DEVICE ${DEVICE}.rr_graph.bin)

  # If the routing graph is compressed uncompress it
  if ("${RR_GRAPH}" MATCHES ".*\\.gz$")

    add_custom_command(
      OUTPUT
        ${CMAKE_CURRENT_BINARY_DIR}/${RR_GRAPH_FOR_DEVICE}
      DEPENDS
        ${RR_GRAPH}
      COMMAND
        ${CMAKE_COMMAND} -E copy
          ${RR_GRAPH}
          ${CMAKE_CURRENT_BINARY_DIR}/${RR_GRAPH_FOR_DEVICE}.gz
      COMMAND
        gunzip -v -f ${CMAKE_CURRENT_BINARY_DIR}/${RR_GRAPH_FOR_DEVICE}.gz
    )

  # If not then link it
  else ()

    add_custom_command(
      OUTPUT
        ${CMAKE_CURRENT_BINARY_DIR}/${RR_GRAPH_FOR_DEVICE}
      DEPENDS
        ${RR_GRAPH}
      COMMAND
        ${CMAKE_COMMAND} -E create_symlink
          ${RR_GRAPH}
          ${CMAKE_CURRENT_BINARY_DIR}/${RR_GRAPH_FOR_DEVICE}
    )

  endif ()

  add_file_target(FILE ${RR_GRAPH_FOR_DEVICE} GENERATED)

  # .......................................................

  add_custom_target(
    ${DEVICE_TYPE}
  )

  set_target_properties(
    ${DEVICE_TYPE}
    PROPERTIES
    TECHFILE ""
    FAMILY ${FAMILY}
    DEVICE_MERGED_FILE ${CMAKE_CURRENT_SOURCE_DIR}/${ARCH_XML_NAME}
  )

  # .......................................................

  # Define the device
  define_device(
    DEVICE ${DEVICE}
    ARCH ${ARCH}
    DEVICE_TYPE ${DEVICE_TYPE}
    PACKAGES ${PACKAGE}
    ROUTE_CHAN_WIDTH ${ROUTE_CHAN_WIDTH}

    EXT_RR_GRAPH ${CMAKE_CURRENT_BINARY_DIR}/${RR_GRAPH_FOR_DEVICE}
    NO_RR_PATCHING

    CACHE_PLACE_DELAY
    CACHE_LOOKAHEAD
    CACHE_ARGS
      --constant_net_method route
      --clock_modeling ideal # Do not route clocks
      --place_delay_model delta_override
      --place_delta_delay_matrix_calculation_method dijkstra
      --router_lookahead extended_map
      --disable_errors check_unbuffered_edges:check_route:check_place
      --suppress_warnings sum_pin_class:check_unbuffered_edges:load_rr_indexed_data_T_values:check_rr_node:trans_per_R:set_rr_graph_tool_comment
      --route_chan_width ${ROUTE_CHAN_WIDTH}

    # FIXME: Skip installation for now
    DONT_INSTALL
  )

endfunction()


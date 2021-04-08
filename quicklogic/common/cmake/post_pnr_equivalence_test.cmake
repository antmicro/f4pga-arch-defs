function(ADD_POST_PNR_EQUIVALENCE_TEST)
  set(options)
  set(oneValueArgs PARENT_NAME SCRIPT)
  set(multiValueArgs )

  cmake_parse_arguments(
    ADD_POST_PNR_EQUIVALENCE_TEST
    "${options}"
    "${oneValueArgs}"
    "${multiValueArgs}"
    "${ARGN}"
  )

  set(PARENT_NAME ${ADD_POST_PNR_EQUIVALENCE_TEST_PARENT_NAME})
  set(SCRIPT      ${ADD_POST_PNR_EQUIVALENCE_TEST_SCRIPT})

  set(DEPS)

  get_target_property_required(BOARD  ${PARENT_NAME} BOARD)
  get_target_property_required(DEVICE ${BOARD}  DEVICE)
  get_target_property_required(ARCH   ${DEVICE} ARCH)
  get_target_property_required(FAMILY ${ARCH}   FAMILY)

  # Use the default script if none is given
  if("${SCRIPT}" STREQUAL "")
    set(SCRIPT ${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/${FAMILY}/yosys/post_pnr_equiv.tcl)
  endif()

  get_target_property_required(POST_PNR_V ${PARENT_NAME} POST_PNR_V)
  get_target_property_required(EBLIF      ${PARENT_NAME} EBLIF)

  append_file_dependency(DEPS ${EBLIF})
  append_file_dependency(DEPS ${POST_PNR_V})

  # Working directory
  get_filename_component(WORK_DIR ${EBLIF} DIRECTORY)

  # Absolute paths
  get_file_location(EBLIF_LOC ${EBLIF})
  get_filename_component(EBLIF_ABS ${EBLIF_LOC} ABSOLUTE)
  get_file_location(POST_PNR_V_LOC ${POST_PNR_V})
  get_filename_component(POST_PNR_V_ABS ${POST_PNR_V_LOC} ABSOLUTE)

  # Add the target for the test
  get_target_property_required(PYTHON3 env PYTHON3)
  get_target_property_required(YOSYS env YOSYS)
  get_target_property_required(QUIET_CMD env QUIET_CMD)

  add_custom_target(
    ${PARENT_NAME}_post_pnr_equivalence_test
    COMMAND
      ${CMAKE_COMMAND} -E env
        POST_SYN_FILE=${EBLIF_ABS}
        POST_PNR_FILE=${POST_PNR_V_ABS}
        UTILS_PATH=${symbiflow-arch-defs_SOURCE_DIR}/quicklogic/qlf_k4n8/utils
        PYTHON3=${PYTHON3}
        ${QUIET_CMD} ${YOSYS} -p "tcl ${SCRIPT}" -l post_pnr_equiv.log
    WORKING_DIRECTORY
      ${WORK_DIR}
    DEPENDS
      ${YOSYS} ${QUIET_CMD} ${DEPS}
    VERBATIM
  )

endfunction()

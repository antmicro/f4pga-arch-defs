# ADD_BINARY_TOOLCHAIN_TEST
#
# This function adds a test for installed SymbiFlow toolchain (a.k.a. binary
# toolchain)
#
# Tests added require "make install" to be run upfront to install the toolchain

function(ADD_BINARY_TOOLCHAIN_TEST)

  set(options)
  set(oneValueArgs TEST_NAME DIRECTIVE DEVICE PINMAP PCF SDC EXTRA_ARGS)
  set(multiValueArgs)

  cmake_parse_arguments(
    ADD_BINARY_TOOLCHAIN_TEST
    "${options}"
    "${oneValueArgs}"
    "${multiValueArgs}"
    ${ARGN}
  )

  set(INSTALLATION_DIR_BIN "${CMAKE_INSTALL_PREFIX}/bin")

  set(TEST_NAME  ${ADD_BINARY_TOOLCHAIN_TEST_TEST_NAME})
  set(DIRECTIVE  ${ADD_BINARY_TOOLCHAIN_TEST_DIRECTIVE})
  set(DEVICE     ${ADD_BINARY_TOOLCHAIN_TEST_DEVICE})
  set(PINMAP     ${ADD_BINARY_TOOLCHAIN_TEST_PINMAP})
  set(PCF        ${ADD_BINARY_TOOLCHAIN_TEST_PCF})
  set(SDC        ${ADD_BINARY_TOOLCHAIN_TEST_SDC})
  set(EXTRA_ARGS ${ADD_BINARY_TOOLCHAIN_TEST_EXTRA_ARGS})

  set(SOURCES "${TEST_NAME}.v")

  if("${PCF}" STREQUAL "")
    set(PCF "${TEST_NAME}.pcf")
  endif()

  if("${SDC}" STREQUAL "")
    set(SDC "${TEST_NAME}.sdc")
  endif()

  if("${DIRECTIVE}" STREQUAL "")
    set(DIRECTIVE "compile")
  endif()

  set(TOOLCHAIN_COMMAND "\
    ql_symbiflow \
    -${DIRECTIVE} \
    -src ${CMAKE_CURRENT_SOURCE_DIR} \
    -d ${DEVICE} \
    -t top \
    -v ${SOURCES} \
    -P ${PINMAP} "
  )

  if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/${PCF}")
    set(TOOLCHAIN_COMMAND "${TOOLCHAIN_COMMAND} -p \"${PCF}\"")
  endif()
  if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/${SDC}")
    set(TOOLCHAIN_COMMAND "${TOOLCHAIN_COMMAND} -s \"${SDC}\"")
  endif()

  set(TOOLCHAIN_COMMAND "${TOOLCHAIN_COMMAND} ${EXTRA_ARGS}")
  separate_arguments(TOOLCHAIN_COMMAND_LIST NATIVE_COMMAND ${TOOLCHAIN_COMMAND})

  add_test(NAME quicklogic_toolchain_test_${TEST_NAME}_${DEVICE}
    COMMAND
      ${CMAKE_COMMAND} -E env
      PATH=${INSTALLATION_DIR_BIN}:$ENV{PATH}
      ${TOOLCHAIN_COMMAND_LIST}
    WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  )

endfunction()

macro(RUN CMD)
  message(STATUS "${CMD}")
  separate_arguments(CMD_LIST NATIVE_COMMAND ${CMD})
  execute_process(
    COMMAND
      ${CMAKE_COMMAND} -E env
      ${CMD_LIST}
    RESULT_VARIABLE
      CMD_RESULT
  )
  if(CMD_RESULT)
    message(FATAL_ERROR "Command \"${CMD}\" failed!")
  endif()
endmacro()

# Remove the build directory
file(REMOVE_RECURSE ${BUILD_DIR})

# Run the toolchain
set(TOOLCHAIN_COMMAND "PATH=${INSTALLATION_DIR}/bin:$ENV{PATH} ${TOOLCHAIN_COMMAND}")
run(${TOOLCHAIN_COMMAND} "")

# Assert usage and timing if any
set(PYTHONPATH ${SYMBIFLOW_DIR}/utils)
set(USAGE_UTIL  ${PYTHONPATH}/report_block_usage.py)
set(TIMING_UTIL ${PYTHONPATH}/report_timing.py)

set(PACK_LOG  ${BUILD_DIR}/pack.log)
set(ROUTE_LOG ${BUILD_DIR}/route.log)

if (NOT "${ASSERT_USAGE}" STREQUAL "")
    run("PYTHONPATH=${PYTHONPATH} python3 ${USAGE_UTIL} ${PACK_LOG} --assert_usage ${ASSERT_USAGE}")
endif ()

if (NOT "${ASSERT_TIMING}" STREQUAL "")
    run("PYTHONPATH=${PYTHONPATH} python3 ${TIMING_UTIL} ${ROUTE_LOG} --assert_timing ${ASSERT_USAGE}")
endif ()


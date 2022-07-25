macro(RUN CMD)
  message(STATUS "Running \"${CMD}\"")
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

# Verify that all required output files are generated
message(STATUS "Checking output files...")

string(REPLACE "," ";" ASSERT_EXISTS "${ASSERT_EXISTS}")
set(MISSING_FILES FALSE)

foreach(FILE ${ASSERT_EXISTS})
  file(RELATIVE_PATH FNAME ${BUILD_DIR} ${FILE})
  if(NOT EXISTS "${FILE}")
    message(STATUS "[X] '${FNAME}'")
    set(MISSING_FILES TRUE)
  else()
    message(STATUS "[V] '${FNAME}'")
  endif()
endforeach()

if(MISSING_FILES)
  message(FATAL_ERROR "Some output files are missing!")
endif()

# Assert usage and timing if any
set(PYTHONPATH ${SYMBIFLOW_DIR}/utils)
set(USAGE_UTIL  ${PYTHONPATH}/report_block_usage.py)
set(TIMING_UTIL ${PYTHONPATH}/report_timing.py)

set(BLOCK_USAGE  ${BUILD_DIR}/block_usage.json)
set(TIMING_SUMMARY ${BUILD_DIR}/timing_summary.json)

if (NOT "${ASSERT_BLOCK_TYPES_ARE_USED}" STREQUAL "")
    run("PYTHONPATH=${PYTHONPATH} python3 ${USAGE_UTIL} ${BLOCK_USAGE} --assert_usage ${ASSERT_BLOCK_TYPES_ARE_USED}")
endif ()

if (NOT "${ASSERT_TIMING}" STREQUAL "")
    run("PYTHONPATH=${PYTHONPATH} python3 ${TIMING_UTIL} ${TIMING_SUMMARY} --assert ${ASSERT_TIMING}")
endif ()

# Check if IO constraints has been correctly applied. This is done by verifying
# the original PCF file agains the one produced by fasm2bels. For this to work
# "post_verilog" dump option must be enabled for a test (i.e. provided within
# EXTRA_ARGS).
set(PCF_UTIL ${PYTHONPATH}/pcf_compare.py)
set(OUT_PCF  ${BUILD_DIR}/top.bit.v.pcf)

if (NOT "${REF_PCF}" STREQUAL "")
    run("PYTHONPATH=${PYTHONPATH} python3 ${PCF_UTIL} ${REF_PCF} ${OUT_PCF}")
endif()

# Check if post synthesis verilog has correct format
# We look for verilog escaped identifiers in ports definitions ending with
# array indexing, e.g. [0]
# MERGED_POST_VERILOG shouldn't contain such identifiers
set(MERGED_POST_VERILOG ${BUILD_DIR}/top_merged_post_implementation.v)

if (EXISTS "${MERGED_POST_VERILOG}")
    SET(GREP_ARGS "(input|output)\\s+\\\\\\S*\\[[0-9]*\\]\\s,?" "${MERGED_POST_VERILOG}")
    message(STATUS "${GREP_ARGS}")
    EXECUTE_PROCESS(
        COMMAND
        grep ${GREP_ARGS}
        OUTPUT_VARIABLE MERGED_VAL_OUT
        RESULT_VARIABLE MERGED_VAL_RES)

    if (${MERGED_VAL_RES} EQUAL 0 AND NOT "${MERGED_VAL_OUT}" STREQUAL "")
        MESSAGE(FATAL_ERROR "Found illegal escaped identifiers in ${MERGED_POST_VERILOG}: ${MERGED_VAL_OUT}")
    endif()
endif()


set(MERGED_POST_IMPL_PREFIX         top_merged_post_implementation)
set(MERGED_POST_IMPL_VERILOG        ${BUILD_DIR}/${MERGED_POST_IMPL_PREFIX}.v)
set(MERGED_POST_IMPL_OUT_VVP        ${BUILD_DIR}/${MERGED_POST_IMPL_PREFIX}.vvp)
set(MERGED_POST_IMPL_OUT_VCD        ${BUILD_DIR}/${MERGED_POST_IMPL_PREFIX}.vcd)

set(FASM2BELS_PREFIX    top.bit.v)
set(FASM2BELS_VERILOG   ${BUILD_DIR}/${FASM2BELS_PREFIX})
set(FASM2BELS_OUT_VVP   ${BUILD_DIR}/${FASM2BELS_PREFIX}.vvp)
set(FASM2BELS_OUT_VCD   ${BUILD_DIR}/${FASM2BELS_PREFIX}.vcd)

set(SPLIT_POST_IMPL_PREFIX    top_post_synthesis)
set(SPLIT_POST_IMPL_VERILOG   ${BUILD_DIR}/${SPLIT_POST_IMPL_SPLIT_PREFIX}.v)
set(SPLIT_POST_IMPL_SDF       ${BUILD_DIR}/${SPLIT_POST_IMPL_PREFIX}.sdf)
set(SPLIT_POST_IMPL_OUT_VVP   ${BUILD_DIR}/${SPLIT_POST_IMPL_SPLIT_PREFIX}.vvp)
set(SPLIT_POST_IMPL_OUT_VCD   ${BUILD_DIR}/${SPLIT_POST_IMPL_SPLIT_PREFIX}.vcd)

set(CELLS_SIM_FILE ${INSTALLATION_DIR}/share/symbiflow/techmaps/${ARCH}/cells_sim.v)
set(YOSYS_CELLS_SIM_FILE ${INSTALLATION_DIR}/share/symbiflow/techmaps/${ARCH}/yosys_cells_sim.v)

if (NOT "${SIMULATION_TEST}" STREQUAL "")
  # Post implementation simulation - merged multi-bit ports
  run("iverilog -v -gspecify -DVCD=\"${MERGED_POST_IMPL_OUT_VCD}\" -DSDF=${SPLIT_POST_IMPL_SDF} -DCLK_MHZ=0.001 -o ${MERGED_POST_IMPL_OUT_VVP} ${CELLS_SIM_FILE} ${MERGED_POST_IMPL_VERILOG} ${BUILD_DIR}/../${SIMULATION_TEST}")
  run("vvp -v -N ${MERGED_POST_IMPL_OUT_VVP} -sdf-verbose")

  # Optional post implementation simulation - split multi-bit ports
  if (EXISTS "${SPLIT_POST_IMPL_VERILOG}")
    run("iverilog -v -gspecify -DSPLIT -DVCD=\"${SPLIT_POST_IMPL_OUT_VCD}\" -DSDF=${SPLIT_POST_IMPL_SDF} -DCLK_MHZ=0.001 -o ${SPLIT_POST_IMPL_OUT_VVP} ${CELLS_SIM_FILE} ${SPLIT_POST_IMPL_VERILOG} ${BUILD_DIR}/../${SIMULATION_TEST}")
    run("vvp -v -N ${SPLIT_POST_IMPL_OUT_VVP} -sdf-verbose")
  endif()

  # Fasm2bels verilog simulation
  run("iverilog -v -gspecify -DF2B -DVCD=\"${FASM2BELS_OUT_VCD}\" -o ${FASM2BELS_OUT_VVP} ${YOSYS_CELLS_SIM_FILE} ${FASM2BELS_VERILOG} ${BUILD_DIR}/../${SIMULATION_TEST}")
  run("vvp -v -N ${FASM2BELS_OUT_VVP} -sdf-verbose")
endif()

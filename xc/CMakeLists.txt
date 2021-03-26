set(ALL_XC7_DIFF_FASM_VERILOG TRUE CACHE BOOL "Link target fasm to all_xc7_diff_fasm for Verilog/XDC inputs?")
set(ALL_XC7_DIFF_FASM_CHECK_VERILOG FALSE CACHE BOOL "Link target diff_fasm to all_xc7_diff_fasm for Verilog/XDC inputs?")
set(ALL_XC7_DIFF_FASM_INTERCHANGE TRUE CACHE BOOL "Link target diff_fasm to all_xc7_diff_fasm for interchange inputs?")

if (NOT ${PRJXRAY_CONFIG} STREQUAL "PRJXRAY_CONFIG-NOTFOUND")
  execute_process(
    COMMAND
      bash ${PRJXRAY_CONFIG}
      OUTPUT_VARIABLE PRJXRAY_DB_DIR
  )
  string(STRIP "${PRJXRAY_DB_DIR}" PRJXRAY_DB_DIR)
else ()
  set(PRJXRAY_DB_DIR "PRJXRAY_DB_DIR-NOTFOUND")
endif ()

set(PRJXRAY_DB_DIR "${PRJXRAY_DB_DIR}"
  CACHE PATH "Path to prjxray database directory")

if (${PRJXRAY_DB_DIR} STREQUAL "PRJXRAY_DB_DIR-NOTFOUND")
  message(FATAL_ERROR "Could not find the project xray database directory! Please provide it with the PRJXRAY_DB_DIR variable")
endif ()

set(XC7_TECHMAP_DIR "${symbiflow-arch-defs_SOURCE_DIR}/xc/xc7/techmap")

add_subdirectory(common)

# Create rapidwright target, and populate it with RAPIDWRIGHT_INSTALLED variable
prepare_rapidwright()

add_subdirectory(xc7)

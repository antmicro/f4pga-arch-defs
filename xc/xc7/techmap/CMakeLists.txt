add_file_target(FILE cells_sim.v)
add_file_target(FILE cells_map.v)
add_file_target(FILE carry_map.v)
add_file_target(FILE clean_carry_map.v)
add_file_target(FILE iobs.v)
add_file_target(FILE retarget.v)
add_file_target(FILE unmap.v)

get_file_target(CELLS_SIM_TARGET cells_sim.v)
get_file_target(CELLS_MAP_TARGET cells_map.v)
get_file_target(CARRY_MAP_TARGET carry_map.v)
get_file_target(CLEAN_CARRY_MAP_TARGET clean_carry_map.v)
get_file_target(IOBS_TARGET iobs.v)
get_file_target(RETARGET_TARGET retarget.v)
get_file_target(UNMAP_TARGET unmap.v)

add_dependencies(
    ${CELLS_SIM_TARGET}
    ${CELLS_MAP_TARGET}
    ${CARRY_MAP_TARGET}
    ${CLEAN_CARRY_MAP_TARGET}
    ${IOBS_TARGET}
    ${RETARGET_TARGET}
    ${UNMAP_TARGET}
)

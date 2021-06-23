yosys -import
set my_path [ file dirname [ file normalize [ info script ] ] ]

# Prepare the post synthesis design
# =====================================

# Read cell library and the design
read_verilog +/quicklogic/qlf_k4n8_cells_sim.v
read_blif -wideports $::env(POST_SYN_FILE)

# FIXME: The techmap below is a workaround for the port bit order issue
# happening when loading a BLIF: https://github.com/YosysHQ/yosys/issues/2729
techmap -max_iter 1 -map $my_path/fixup_port_indices.v

# Synthesize and flatten, split top-level ports to individual nets to match
# with post-pnr
hierarchy -check -auto-top
write_verilog equiv_top_syn_pre.v
yosys proc
flatten
splitnets -ports -format ():

# Remove unconnected ports
rmports A:top

# Store
yosys rename -top top_syn
stat
write_verilog equiv_top_syn_post.v
design -stash top_syn

# Prepare the post PnR design
# =====================================

# Read cell library and the post pnr design 
read_verilog $my_path/../techmap/cells_sim.v
read_verilog $::env(POST_PNR_FILE)

# Find the top module
hierarchy -check -auto-top

# Fixup top-level IO port names, remove unconected wires added by VPR explicitly
# and exposed by Yosys. This has to be done by the external script below.
write_json equiv_top_pnr_ios.json
exec $::env(PYTHON3) $::env(UTILS_PATH)/../../common/utils/fixup_io_names.py equiv_top_pnr_ios.json
design -reset
read_json equiv_top_pnr_ios.json

write_verilog equiv_top_pnr_pre.v

# Synthesize
yosys proc
flatten

# Store
yosys rename -top top_pnr
stat
write_verilog equiv_top_pnr_post.v
design -stash top_pnr

# Do the equivalence checking
# =====================================

# Prepare a design for equivalence checking
design -copy-from top_syn -as top_syn top_syn
design -copy-from top_pnr -as top_pnr top_pnr
stat

async2sync
equiv_make top_syn top_pnr equiv
hierarchy -top equiv
flatten
stat
write_verilog equiv_top.v

# Check the equivalence
equiv_simple -v -nogroup
equiv_status -assert

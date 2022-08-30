add_quicklogic_board(
  BOARD chandalar
  FAMILY pp3
  DEVICE ql-eos-s3
  PACKAGE wlcsp
  FABRIC_PACKAGE PD64
  USE_F4PGA_BUILD
)

add_quicklogic_board(
  BOARD quickfeather
  FAMILY pp3
  DEVICE ql-eos-s3
  PACKAGE wlcsp
  FABRIC_PACKAGE PU64
  # Quickfeather comes with eos-s3 in special QFN package which is not mass-produced.
  # This part number might not be correct, but it should work for what it's used for.
  USE_F4PGA_BUILD
)

add_quicklogic_board(
  BOARD qomu
  FAMILY pp3
  DEVICE ql-eos-s3
  PACKAGE wlcsp
  FABRIC_PACKAGE WR42
  USE_F4PGA_BUILD
)

add_quicklogic_board(
  BOARD chilkat
  FAMILY pp3
  DEVICE ql-eos-s3
  PACKAGE wlcsp
  FABRIC_PACKAGE WR42
  USE_F4PGA_BUILD
)

# This is completely irrelevant at this point.
add_quicklogic_board(
  BOARD jimbob4
  FAMILY pp3
  DEVICE ql-pp3e
  PACKAGE wlcsp
  FABRIC_PACKAGE WD30
)

add_quicklogic_board(
  BOARD chandalar
  FAMILY pp3
  DEVICE ql-eos-s3
  PACKAGE wlcsp
  FABRIC_PACKAGE PD64
  BIT_TO_V_EXTRA_ARGS "--device-name eos-s3 --package-name PD64"
)

add_quicklogic_board(
  BOARD quickfeather
  FAMILY pp3
  DEVICE ql-eos-s3
  PACKAGE wlcsp
  FABRIC_PACKAGE PU64
  BIT_TO_V_EXTRA_ARGS "--device-name eos-s3 --package-name PU64"
)

add_quicklogic_board(
  BOARD qomu
  FAMILY pp3
  DEVICE ql-eos-s3
  PACKAGE wlcsp
  FABRIC_PACKAGE WR42
  BIT_TO_V_EXTRA_ARGS "--device-name eos-s3 --package-name WR42"
)

add_quicklogic_board(
  BOARD chilkat
  FAMILY pp3
  DEVICE ql-eos-s3
  PACKAGE wlcsp
  FABRIC_PACKAGE WR42
  BIT_TO_V_EXTRA_ARGS "--device-name eos-s3 --package-name WR42"
)

add_quicklogic_board(
  BOARD jimbob4
  FAMILY pp3
  DEVICE ql-pp3e
  PACKAGE wlcsp
  FABRIC_PACKAGE WD30
  BIT_TO_V_EXTRA_ARGS "--device-name pp3e --package-name WD30"
)

add_quicklogic_board(
  BOARD jimbob4-pp3
  FAMILY pp3
  DEVICE ql-pp3
  PACKAGE wlcsp
  FABRIC_PACKAGE WD30
  BIT_TO_V_EXTRA_ARGS "--device-name pp3 --package-name WD30"
)

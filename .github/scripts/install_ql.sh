#!/usr/bin/env bash

set -e

INSTALL_DIR="$(pwd)/install"

mkdir -p $INSTALL_DIR

export CMAKE_FLAGS="-GNinja -DCMAKE_INSTALL_PREFIX=${INSTALL_DIR} -DINSTALL_FAMILIES=qlf_k4n8,pp3"

export FPGA_FAM=eos-s3
export F4PGA_INSTALL_DIR="placeholder"
export F4PGA_SHARE_DIR=${INSTALL_DIR}/share/f4pga
export F4PGA_BIN_DIR=${INSTALL_DIR}/bin/

source $(dirname "$0")/setup-and-activate.sh

echo "----------------------------------------"

pushd build
make_target install "Installing quicklogic toolchain (make install)"
popd

cp \
  packaging/"$FPGA_FAM"_environment.yml \
  packaging/requirements.txt \
  packaging/"$FPGA_FAM"_requirements.txt \
  $INSTALL_DIR/

echo "----------------------------------------"

heading "Running installed toolchain tests"
(
  pushd build
  export VPR_NUM_WORKERS=${MAX_CORES}
  export CTEST_OUTPUT_ON_FAILURE=1
  heading "Testing installed toolchain on ql_eos_s3"
  ctest -j${MAX_CORES} -R "quicklogic_toolchain_test_.*_ql-eos-s3" -VV
  echo "----------------------------------------"
  popd
)
echo "----------------------------------------"

heading "Compressing install dir (creating packages)"
(
  rm -rf build

  # Remove symbolic links and copy content of the linked files
  for file in $(find install -type l)
    do cp --remove-destination $(readlink $file) $file
  done

  du -ah install
  export GIT_HASH=$(git rev-parse --short HEAD)

  pushd install
  mkdir -p "$FPGA_FAM"_env
  mv "$FPGA_FAM"_environment.yml \
    requirements.txt \
    "$FPGA_FAM"_requirements.txt \
    "$FPGA_FAM"_env
  popd

  for device in $(ls install/share/f4pga/arch)
  do
    # Prepare packages only for QL devices
    tar -I "pixz" -cvf \
      symbiflow-arch-defs-install-ql-${GIT_HASH}.tar.xz \
      -C install share/f4pga/techmaps \
        share/f4pga/scripts \
        "$FPGA_FAM"_env
    if [[ $device = ql* ]]; then
      tar -I "pixz" -cvf symbiflow-arch-defs-$device-${GIT_HASH}.tar.xz -C install share/f4pga/arch/$device
    fi
  done

  rm -rf install
)
echo "----------------------------------------"

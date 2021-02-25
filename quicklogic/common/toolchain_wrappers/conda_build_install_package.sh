#!/bin/bash
echo -e "\e[1;34mInstallation starting for conda based symbiflow\e[0m"
echo -e "\e[1;34mQuickLogic Corporation\e[0m"

if [ -z "$INSTALL_DIR" ]
then
	echo -e "\e[1;31m\$INSTALL_DIR is not set, please set and then proceed!\e[0m"
	echo -e "\e[1;31mExample: \"export INSTALL_DIR=/<custom_location>\". \e[0m"
	exit 0
elif [ -d "$INSTALL_DIR/conda" ]; then
	echo -e "\e[1;32m $INSTALL_DIR/conda already exists, please clean up and re-install ! \e[0m"
	exit 0
else
	echo -e "\e[1;32m\$INSTALL_DIR is set to $INSTALL_DIR ! \e[0m"
fi

mkdir -p $INSTALL_DIR

wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O conda_installer.sh
bash conda_installer.sh -b -p $INSTALL_DIR/conda && rm conda_installer.sh
source "$INSTALL_DIR/conda/etc/profile.d/conda.sh"
echo "include-system-site-packages=false" >> $INSTALL_DIR/conda/pyvenv.cfg
CONDA_FLAGS="-y --override-channels -c defaults -c conda-forge"
conda update $CONDA_FLAGS -q conda
curl https://storage.googleapis.com/symbiflow-arch-defs-install/quicklogic-arch-defs-63c3d8f9.tar.gz --output arch.tar.gz
tar -C $INSTALL_DIR -xvf arch.tar.gz && rm arch.tar.gz
conda install $CONDA_FLAGS -c quicklogic-corp/label/ql yosys="0.8.0_0003_e80fb742f_20201208_122808 None" python=3.7
conda install $CONDA_FLAGS -c quicklogic-corp/label/ql yosys-plugins="1.2.0_0011_g21045a9 None"
conda install $CONDA_FLAGS -c quicklogic-corp/label/ql vtr="v8.0.0_rc2_2894_gdadca7ecf 20201008_140004"
conda install $CONDA_FLAGS -c quicklogic-corp iverilog
conda install $CONDA_FLAGS -c tfors gtkwave
conda install $CONDA_FLAGS make lxml simplejson intervaltree git pip
conda activate
pip install python-constraint
pip install serial
#pip install git+https://github.com/QuickLogic-Corp/quicklogic-fasm@2312ff0
pip install git+https://github.com/QuickLogic-Corp/quicklogic-fasm
conda deactivate
setup_file=$INSTALL_DIR/setup.sh
echo "export INSTALL_DIR=$INSTALL_DIR" >$setup_file
chmod 755 $setup_file
#adding symbiflow toolchain binaries to PATH
echo "export PATH=\"\$INSTALL_DIR/quicklogic-arch-defs/bin:\$INSTALL_DIR/quicklogic-arch-defs/bin/python:\$PATH\"" >>$setup_file
echo "source \"\$INSTALL_DIR/conda/etc/profile.d/conda.sh\"" >>$setup_file
echo "conda activate" >>$setup_file
echo "ql_symbiflow -v" >>$setup_file

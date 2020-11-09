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
CONDA_FLAGS="-y --override-channels -c defaults -c conda-forge"
conda update $CONDA_FLAGS -q conda
wget -qO- https://quicklogic-my.sharepoint.com/:u:/p/kkumar/EQro5PGhiMpBhlieiFNoiuwBdQ-lpi-3VjqvRmYow54hEA?download=1 | tar -xJ -C $INSTALL_DIR
conda install $CONDA_FLAGS -c quicklogic-corp/label/ql yosys="0.8.0_0002_gc3b38fdc 20200901_073908" python=3.7
conda install $CONDA_FLAGS -c quicklogic-corp/label/ql yosys-plugins="1.2.0_0009_g9ab211c 20201001_121833"
conda install $CONDA_FLAGS -c quicklogic-corp/label/ql vtr="v8.0.0_rc2_2894_gdadca7ecf 20201008_140004"
conda install $CONDA_FLAGS -c quicklogic-corp iverilog
conda install $CONDA_FLAGS -c tfors gtkwave
conda install $CONDA_FLAGS make lxml simplejson intervaltree git pip
conda activate
pip install python-constraint
pip install serial
pip install git+https://github.com/QuickLogic-Corp/quicklogic-fasm
conda deactivate

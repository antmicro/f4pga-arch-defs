# SymbiFlow for Quicklogic FPGAs

## Quickstart guide

### 1. Yosys with QuickLogic support installation

First, download the sources from the Antmicro's Yosys fork:

```bash
git clone https://github.com/antmicro/yosys.git -b quicklogic-rebased quicklogic-yosys
cd quicklogic-yosys
```

Build Yosys with the following commands:

```bash
cd yosys
make config-gcc
make -j$(nproc)
sudo make install
```

This will install Yosys into your `/usr/bin/` directory.

Note: If you want to build Yosys using clang, replace `make config-gcc` with `make config-clang`.

Note: Once the QuickLogic specific changes in Yosys are merged with Yosys used by mainline Symbilow, this step will be unnecessary.

### 2. SymbiFlow installation

Clone the SymbiFlow repository, make sure you're using `master+quicklogic` branch:

```bash
git clone https://github.com/antmicro/symbiflow-arch-defs -b quicklogic-upstream-rebase
```

Setup the environment:

```bash
export YOSYS=/usr/bin/yosys
# assuming default Yosys installation path
make env
cd build && make all_conda
```

### 3. Generate a bitstream for a sample design

Once the SymbiFlow environment is set up, you can perform the implementation (synthesis, placement and routing) of an example FPGA designs.

Go to the `quicklogic/tests` directory and choose a design you want to implement e.g:

```bash
cd quicklogic/tests/btn_counter
make counter-ql-chandalar_bit
```

This will generate a binary bitstream file for the design. The resulting bitstream will be written to the `top.bit` file in the working directory of the design.

Currently designs that work on hardware are:

- Designs that require external button/led connections:
	- btn_xor
	- btn_ff
	- btn_counter
	- ext_counter
- Designs demonstrating SoC - FPGA interaction:
	- counter
	- soc_clocks
	- soc_litex_pwm

For details of each of the test design please refer to its `README.md` file.

### 4. Programming the EOS S3 SoC

To ease up the programming process helper scripts were integrated with the flow.
The scripts can automatically configure the IOMUX of the SoC so that all top-level IO ports of the design are routed to the physical pads of the chip.

In order to generate the programming script, build the following target:

```bash
make counter-ql-chandalar_jlink
```

The script will contain both bitstream and IOMUX configuration.

## Naming convention

The naming convention of all build targets is: `<design_name>-<board_name>_<stage_name>`

The `<design_name>` corresponds to the name of the design.
The `<board_name>` defines the board that the design is targetted for, possible values are `ql-chandalar` and `ql-jibob4`
The last part `<stage_name>` defines the last stage of the flow that is to be executed.

The most important stages are:

- **eblif**
    Runs Yosys synthesis and generates an EBLIF file suitable for 	VPR. The output EBLIF file is named `top.eblif`

- **route**
    Runs VPR pack, place and route flow. The packed design is written to the `top.net` file. design placement and routing data is stored in the `top.place` and `top.route` files respectively. IO placement constraints for VPR are written to the `top_io.place` file.

- **fasm**
    Generates the FPGA assembly file (a.k.a. FASM) using the routed design. The FASM file is named `top.fasm`.

- **bit**
    Generates a binary bitstream file from the FASM file using the `qlfasm.py` tool. The bitstream is ready to be loaded to the FPGA.

- **jlink**
    For the conveniance of programming the EOS S3 SoC the `jlink` stage generates a command script which configures the IOMUX of the SoC and loads the bitstream to the FPGA. The script is ready to be executed via the *JLink commander* tool.

Executing a particular stage implies that all stages before it will be executed as well (if needed). They form a dependency chain.

## Adding new designs to SymbiFlow

To to add a new design to the flow, and use it as a test follow the guide:

1. Create a subfolder for your design under the `quicklogic/tests` folder.

1. Add inclusion of the folder in the `quicklogic/tests/CMakeLists.txt` by adding the following line to it:

    ```plaintext
    add_subdirectory(<your_directory_name>)
    ```

1. Add a `CMakeLists.txt` file to your design. Specify your design settings inside it:

    ```plaintext
    add_fpga_target(
      NAME            <your_design_name>
      BOARD           <target_board_name>
      SOURCES         <verilog sources list>
      INPUT_IO_FILE   <PCF file with IO constraints>
      SDC_FILE        <SDC file with timing constraints>
      )
    ```

    The design name can be anything. For available board names please refer to the `quicklogic/boards.cmake` file. Input IO constraints have to be given in the *PCF* format. The *SDC* file argument is optional. 
    Please also refer to CMake files for existing designs.
    All the files passed to `add_fpga_target` have to be added to the flow with `add_file_target` e.g:
    
    ```plaintext
    add_file_target(FILE btn_counter.v SCANNER_TYPE verilog)
    add_file_target(FILE chandalar.pcf)
    ```
    
    The verilog scanner will automatically add all the verilog dependecies explicitely included in the added file.
    
1. Once this is done go back to the SymbiFlow root directory and re-run the make env command to update build targets:

   ```bash
   make env
   ```

1. Now enter the build directory of your project and run the appropriate target as described:

   ```bash
   cd build/quicklogic/tests/<your_directory_name>
   make <your_design_name>-<target_board_name>_bit
   ```

## Known limitations

SymbiFlow support for Quicklogic FPGAs is currently under heavy development. These are known limitations of the toolchain:

1. No support for the global clock network yet. Clock signal is routed to *QCK* inputs of *LOGIC* cells via the ordinary routing network.

1. The direct connection between the "TBS" mux and the flip-flop inside the *LOGIC* cell cannot be used. The signal has to be routed around through the switchbox from the *CZ* pin to the *QDI* pin.

1. Only a single *LUT2* or *LUT3* can be packed into a LOGIC cell.
#!/usr/bin/env python3
"""
A simple script that fixes up post-pnr verilog and SDF files from VPR:

 - Removes incorrect constants "1'b0" connected to unconnected cell port,

 - Disconnects all unconnected outputs from the "DummyOut" net,

 - appends a correct prefix for  each occurrence of a binary string in round
   brackets. For example "(010101)" is converted into "(6'b010101)".

When the option "--split-ports" is given the script also breaks all references
to wide cell ports into references to individual pins.

One shortcoming of the script is that it may treat a decimal value of 10, 100
etc. as binary. Fortunately decimal literals haven't been observed to appear
in Verilog files written by VPR.
"""
import argparse
import os
import re

def main():
    pass

if __name__ == "__main__":
    main()

`timescale 1ps/1ps
(* whitebox *)
(* FASM_PARAMS="INV.ESEL=ESEL;INV.OSEL=OSEL;INV.FIXHOLD=FIXHOLD;INV.WPD=WPD;INV.DS=DS" *)
module BIDIR_CELL(
    PAD_$inp, PAD_$out,
    IE, OQI, OQE,
    IQE, IQC, IQR,
    INEN, IQIN,
    IZ, IQZ
);
    (* iopad_external_pin *)
    input  wire PAD_$inp;
    (* iopad_external_pin *)
    output wire PAD_$out;

    input  wire IE;
    input  wire OQI;
    input  wire OQE;
    input  wire IQE;
    input  wire IQC;
    input  wire IQR;
    input  wire INEN;
    input  wire IQIN;

    output wire IZ;
    output wire IQZ;

    specify
        (OQI => PAD_$out) = (0,0);
        (IE => PAD_$out) = (0,0);
        (PAD_$inp => IZ) = (0,0);
        (INEN => IZ) = (0,0);
    endspecify

    // Parameters
    parameter [0:0] ESEL    = 0;
    parameter [0:0] OSEL    = 0;
    parameter [0:0] FIXHOLD = 0;
    parameter [0:0] WPD     = 0;
    parameter [0:0] DS      = 0;

    // Behavioral model
    assign IZ = (INEN == 1'b1) ? PAD_$inp : 1'b0;
    assign PAD_$out = (IE == 1'b1) ? OQI : 1'b0;

endmodule

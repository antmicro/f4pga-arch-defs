(* whitebox *)
(* FASM_PARAMS="INV.ESEL=ESEL;INV.OSEL=OSEL;INV.FIXHOLD=FIXHOLD;INV.WPD=WPD;INV.DS=DS" *)
(* MODEL_NAME="BIDIR" *)
module BIDIR_SITE(
    I_PAD_$inp, I_DAT, I_EN,
    O_PAD_$out, O_DAT, O_EN
);
    input  wire I_PAD_$inp;
    input  wire I_EN;

    input  wire O_DAT;
    input  wire O_EN;

    (* DELAY_CONST_I_PAD_$inp="{iopath_IP_IZ}" *)
    (* DELAY_CONST_I_EN="1e-10" *)  // No timing for IE/INEN -> IZ in LIB/SDF.
    output wire I_DAT;

    (* DELAY_CONST_O_DAT="{iopath_OQI_IP}" *)
    (* DELAY_CONST_O_EN="{iopath_IE_IP}" *)
    output wire O_PAD_$out;

    // Parameters
    parameter [0:0] ESEL    = 0;
    parameter [0:0] OSEL    = 0;
    parameter [0:0] FIXHOLD = 0;
    parameter [0:0] WPD     = 0;
    parameter [0:0] DS      = 0;

    // Behavioral model
    assign I_DAT = (I_EN == 1'b1) ? I_PAD_$inp : 1'b0;
    assign O_PAD_$out = (O_EN == 1'b1) ? O_DAT : 1'b0;

endmodule

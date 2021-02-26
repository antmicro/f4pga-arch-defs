`include "../vpr_pad/vpr_ipad.sim.v"
`include "../vpr_pad/vpr_opad.sim.v"
`include "./bidir_cell.sim.v"

(* MODES="INPUT;OUTPUT;INOUT" *)
module BIDIR(
    input  wire IE,
    (* CLOCK *)
    (* clkbuf_sink *)
    input  wire IQC,
    input  wire OQI,
    input  wire OQE,
    input  wire IQE,
    input  wire IQR,
    input  wire INEN,
    input  wire IQIN,
    output wire IZ,
    output wire IQZ
);

    parameter MODE = "INPUT";

    // Input mode
    generate if (MODE == "INPUT") begin : INPUT

        (* pack="IPAD_TO_BIDIR" *)
        wire i_pad;

        (* keep *)
        VPR_IPAD inpad(i_pad);

        (* keep *)
        (* FASM_PREFIX="INTERFACE.BIDIR" *)
        BIDIR_CELL bidir(
            .I_PAD_$inp(i_pad),
            .I_DAT(IZ),
            .I_EN (INEN),
            .O_PAD_$out(),
            .O_DAT(OQI),
            .O_EN (IE)
        );

    // Output mode
    end if (MODE == "OUTPUT") begin : OUTPUT

        (* pack="BIDIR_TO_OPAD" *)
        wire o_pad;

        (* keep *)
        VPR_OPAD outpad(o_pad);

        (* keep *)
        (* FASM_PREFIX="INTERFACE.BIDIR" *)
        BIDIR_CELL bidir(
            .I_PAD_$inp(),
            .I_DAT(IZ),
            .I_EN (INEN),
            .O_PAD_$out(o_pad),
            .O_DAT(OQI),
            .O_EN (IE)
        );

    // InOut mode
    end if (MODE == "INOUT") begin : INOUT

        (* pack="IOPAD_TO_BIDIR" *)
        wire i_pad;

        (* pack="IOPAD_TO_BIDIR" *)
        wire o_pad;

        (* keep *)
        VPR_IPAD inpad(i_pad);

        (* keep *)
        VPR_OPAD outpad(o_pad);

        (* keep *)
        (* FASM_PREFIX="INTERFACE.BIDIR" *)
        BIDIR_CELL bidir(
            .I_PAD_$inp(i_pad),
            .I_DAT(IZ),
            .I_EN (INEN),
            .O_PAD_$out(o_pad),
            .O_DAT(OQI),
            .O_EN (IE)
        );

    end endgenerate

endmodule

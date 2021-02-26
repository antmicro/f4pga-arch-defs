`include "../vpr_pad/vpr_ipad.sim.v"
`include "../vpr_pad/vpr_opad.sim.v"

(* MODES="INPUT;OUTPUT" *)
module SYN_PAD(I, O);

    input  wire I;
    output wire O;

    parameter MODE="INPUT";

    // Input mode
    generate if (MODE == "INPUT") begin : INPUT
        (* keep *)
        VPR_IPAD ipad(O);

    // Output mode
    end if (MODE == "OUTPUT") begin : OUTPUT
        (* keep *)
        VPR_OPAD opad(I);

    end endgenerate
endmodule

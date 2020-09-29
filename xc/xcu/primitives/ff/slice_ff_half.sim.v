`include "fdse_or_fdre.sim.v"
`include "fdpe_or_fdce.sim.v"

(* MODES="FDSE_OR_FDRE;FDPE_OR_FDCE;LDCE_OR_LDPE" *)
module SLICE_FF_HALF(D, CE, SR, CLK, Q);
    input wire [7:0] D;
    input wire  SR;
    input wire [1:0] CE;
    input wire  CLK;
    output wire [7:0] Q;

    parameter MODE = "";

    if (MODE == "FDSE_OR_FDRE") begin
        genvar i;
        generate
            for (i = 0; i < 4; i = i+1) begin
                FDSE_OR_FDRE FDSE_OR_FDRE_1(.D(D[i*2]), .CE(CE[0]), .SR(SR), .CLK(CLK), .Q(Q[i*2]));
                FDSE_OR_FDRE FDSE_OR_FDRE_2(.D(D[i*2+1]), .CE(CE[1]), .SR(SR), .CLK(CLK), .Q(Q[i*2+1]));
            end
        endgenerate
    end else if (MODE == "FDPE_OR_FDCE") begin
        genvar i;
        generate
            for (i = 0; i < 4; i = i+1) begin
                FDPE_OR_FDCE FDPE_OR_FDCE_1(.D(D[i*2]), .CE(CE[0]), .SR(SR), .CLK(CLK), .Q(Q[i*2]));
                FDPE_OR_FDCE FDPE_OR_FDCE_2(.D(D[i*2+1]), .CE(CE[1]), .SR(SR), .CLK(CLK), .Q(Q[i*2+1]));
            end
        endgenerate
    end
endmodule

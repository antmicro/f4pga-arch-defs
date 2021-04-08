// FIXME: These techmaps are a workaround for the port bit order issue:
// https://github.com/YosysHQ/yosys/issues/2729

module adder_lut4(
   input  [0:3] in,
   input  cin,
   output lut4_out,
   output cout,
);
    parameter [0:15] LUT = 16'd0;
    parameter [0:0]  IN2_IS_CIN = 1'b0;

    adder_lut4 # (
        .LUT        (LUT),
        .IN2_IS_CIN (IN2_IS_CIN)
    ) _TECHMAP_REPLACE_ (
        .in         ({in[3], in[2], in[1], in[0]}), // <-- The fix is here
        .cin        (cin),
        .lut4_out   (lut4_out),
        .cout       (cout)
    );

endmodule

module frac_lut4_arith(
   input  [0:3] in,
   input  cin,
   output lut4_out,
   output cout,
);
    parameter [0:15] LUT = 16'd0;
    parameter [0:0]  IN2_IS_CIN = 1'b0;

    frac_lut4_arith # (
        .LUT        (LUT),
        .IN2_IS_CIN (IN2_IS_CIN)
    ) _TECHMAP_REPLACE_ (
        .in         ({in[3], in[2], in[1], in[0]}), // <-- The fix is here
        .cin        (cin),
        .lut4_out   (lut4_out),
        .cout       (cout)
    );

endmodule

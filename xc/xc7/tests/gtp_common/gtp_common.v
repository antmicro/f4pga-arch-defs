module top(
    input wire clk_p,
    input wire clk_n,
    output wire refclk,
    output wire gtrefclk0
);

wire refclk;
wire gtrefclk0;
assign gtrefclk0 = refclk;

GTPE2_COMMON #(
	.PLL0_FBDIV(3'd5),
	.PLL0_FBDIV_45(3'd4),
	.PLL0_REFCLK_DIV(1'd1)
) GTPE2_COMMON (
	.BGBYPASSB(1'd1),
	.BGMONITORENB(1'd1),
	.BGPDB(1'd1),
	.BGRCALOVRD(5'd31),
	.GTREFCLK0(gtrefclk0),
	.PLL0LOCKEN(1'd1),
	.PLL0PD(1'd0),
	.PLL0REFCLKSEL(1'd1),
	.PLL1PD(1'd1),
	.RCALENB(1'd1)
);

IBUFDS_GTE2 IBUFDS_GTE2(
	.CEB(1'd0),
	.I(clk_p),
	.IB(clk_n),
	.O(refclk)
);

endmodule

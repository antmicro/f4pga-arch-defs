`timescale 1 ns / 1 ps

`ifndef F2B
	`default_nettype none
`endif

`define STRINGIFY(x) `"x`"


module tb;

	task assert(input a);
	begin
		if (a==0) begin
			$display("******************");
			$display("* ASSERT FAILURE *");
			$display("******************");
			$dumpflush;
			$finish_and_return(-1);
		end
	end
	endtask

	reg clk;
	wire [3:0] out;
	integer i;


	`ifdef F2B
		top dut (
			.clk (clk),
			.led (out)
		);
	`else
		top dut (
			.\clk (clk),
			.\led[0] (out[0]),
			.\led[1] (out[1]),
			.\led[2] (out[2]),
			.\led[3] (out[3])
		);
	`endif

	initial begin
		clk = 1'b0;
		`ifndef F2B
			$sdf_annotate(`STRINGIFY(`SDF), dut);
		`endif
		$dumpfile(`STRINGIFY(`VCD));
		$dumpvars;
		for (i=1; i<64; i=i+1) begin
			#100 clk = 1;
			#50 assert(out === (i % 16));
			#50 clk = 0;
		end
		#25 $finish();
	end
endmodule

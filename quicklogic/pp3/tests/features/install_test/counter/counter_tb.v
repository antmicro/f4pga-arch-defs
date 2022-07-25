`timescale 1 ps / 1 ps

`default_nettype none

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


	`ifndef SPLIT
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
			#1000000 clk = 1;
			#500000 assert(out === (i % 16));
			#500000 clk = 0;
		end
		#25 $finish();
	end
endmodule

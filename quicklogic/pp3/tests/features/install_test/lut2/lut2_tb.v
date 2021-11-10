`timescale 1 ns / 1 ps
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

reg [1:0] I;
wire O;
top dut (
    .\I[0] (I[0]),
    .\I[1] (I[1]),
    .\O (O)
);

initial begin
    I = 2'b00;

    $sdf_annotate(`STRINGIFY(`SDF), dut);
    $dumpfile(`STRINGIFY(`VCD));
    $dumpvars;

    // Timing-based simulation adds a delay to propagate signals.
    #50 assert(O === 1'b0);
    #25 I = 2'b01;
    #50 assert(O === 1'b1);

    #25 I = 2'b10;
    #50 assert(O === 1'b0);

    #25 I = 2'b11;
    #50 assert(O === 1'b1);

    #25 $finish();
end

endmodule



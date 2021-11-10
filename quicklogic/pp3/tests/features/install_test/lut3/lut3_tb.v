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

reg [2:0] I;
wire O;
top dut (
    .\I[0] (I[0]),
    .\I[1] (I[1]),
    .\I[2] (I[2]),
    .\O (O)
);

initial begin
    I = 3'b000;

    $sdf_annotate(`STRINGIFY(`SDF), dut);
    $dumpfile(`STRINGIFY(`VCD));
    $dumpvars;

    // Timing-based simulation adds a delay to propagate signals.
    #25 assert(O === 1'b1);

    #25 I = 3'b001;
    #50 assert(O === 1'b1);

    #25 I = 3'b111;
    #50 assert(O === 1'b1);

    #25 I = 3'b010;
    #50 assert(O === 1'b0);

    #25 I = 3'b100;
    #50 assert(O === 1'b0);

    #25 $finish();
end

endmodule



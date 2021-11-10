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

reg [3:0] I;
wire O;
top dut (
    .\I[0] (I[0]),
    .\I[1] (I[1]),
    .\I[2] (I[2]),
    .\I[3] (I[3]),
    .\O (O)
);

initial begin
    I = 4'b0000;

    $sdf_annotate(`STRINGIFY(`SDF), dut);
    $dumpfile(`STRINGIFY(`VCD));
    $dumpvars;

    // Timing-based simulation adds a delay to propagate signals.
    #25 assert(O === 1'b1);

    #25 I = 4'b1001;
    #50 assert(O === 1'b1);

    #25 I = 4'b1010;
    #50 assert(O === 1'b1);

    #25 I = 4'b1011;
    #50 assert(O === 1'b1);

    #25 I = 4'b0101;
    #50 assert(O === 1'b0);

    #25 I = 4'b0001;
    #50 assert(O === 1'b1);

    #25 I = 4'b0100;
    #50 assert(O === 1'b1);

    #25 I = 4'b0111;
    #50 assert(O === 1'b0);

    #25 $finish();
end

endmodule



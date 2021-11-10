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

reg I;
wire O;
top dut (
    .\I[0] (I),
    .\O (O)
);

initial begin
    I = 1'b0;

    $sdf_annotate(`STRINGIFY(`SDF), dut);
    $dumpfile(`STRINGIFY(`VCD));
    $dumpvars;

    #50 assert(O === 1'b1);
    #25 I = 1'b1;

    // Timing-based simulation adds a delay to propagate signals.
    #50 assert(O === 1'b0);
    #25 $finish();
end

endmodule



module top(
    output wire [3:0] led
);
    wire Clk16;
    wire clk;

    qlal4s3b_cell_macro u_qlal4s3b_cell_macro (
        .Clk16 (Clk16),
    );

    gclkbuff u_gclkbuff_clock (
        .A(Clk16),
        .Z(clk)
    );

    reg [23:0] cnt;
    initial cnt <= 0;

    always @(posedge clk)
        cnt <= cnt + 1;

    assign led[3:0] = cnt[23:20];

endmodule

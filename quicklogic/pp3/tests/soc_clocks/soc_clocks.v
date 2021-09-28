module top(
    output wire [3:0] led
);
    wire Clk_C16;
    wire Clk_C16_Rst;
    wire Clk_C21;
    wire Clk_C21_Rst;

    wire clk0, rst0;
    wire clk1, rst1;

    qlal4s3b_cell_macro u_qlal4s3b_cell_macro (
        .Clk_C16     (Clk_C16),
        .Clk_C16_Rst (Clk_C16_Rst),
        .Clk_C21     (Clk_C21),
        .Clk_C21_Rst (Clk_C21_Rst),
    );

    gclkbuff u_gclkbuff_clock0 (.A(Clk_C16),       .Z(clk0));
    gclkbuff u_gclkbuff_reset0 (.A(Clk_C16_Rst),   .Z(rst0));

    gclkbuff u_gclkbuff_clock1 (.A(Clk_C21),       .Z(clk1));
    gclkbuff u_gclkbuff_reset1 (.A(Clk_C21_Rst),   .Z(rst1));

    reg [23:0] cnt0;
    initial cnt0 <= 0;

    always @(posedge clk0)
        if (rst0) cnt0 <= 0;
        else      cnt0 <= cnt0 + 1;

    reg [23:0] cnt1;
    initial cnt1 <= 0;

    always @(posedge clk1)
        if (rst1) cnt1 <= 0;
        else      cnt1 <= cnt1 + 1;

    assign led[3:2] = cnt1[21:20];
    assign led[1:0] = cnt0[21:20];

endmodule

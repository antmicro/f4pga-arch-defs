module top(
    output wire [3:0] led
);
    wire Clk16;
    wire Clk16_Rst;
    wire Clk21;
    wire Clk21_Rst;

    wire clk0, rst0;
    wire clk1, rst1;

    qlal4s3b_cell_macro u_qlal4s3b_cell_macro (
        .Clk16     (Clk16),
        .Clk16_Rst (Clk16_Rst),
        .Clk21     (Clk21),
        .Clk21_Rst (Clk21_Rst),
    );

    gclkbuff u_gclkbuff_clock0 (.A(Clk16),       .Z(clk0));
    gclkbuff u_gclkbuff_reset0 (.A(Clk16_Rst),   .Z(rst0));

    gclkbuff u_gclkbuff_clock1 (.A(Clk21),       .Z(clk1));
    gclkbuff u_gclkbuff_reset1 (.A(Clk21_Rst),   .Z(rst1));

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

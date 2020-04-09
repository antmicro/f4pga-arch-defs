(* blackbox *)
module RAM (
    input [10:0] A1_0,
    input [10:0] A1_1,
    input [10:0] A2_0,
    input [10:0] A2_1,
    input CLK1_0,
    input CLK1_1,
    output Almost_Empty_0, Almost_Empty_1, Almost_Full_0, Almost_Full_1,
    input ASYNC_FLUSH_0, ASYNC_FLUSH_1,CLK2_0, CLK2_1, CLK1EN_0, CLK1EN_1, CLK2EN_0,CLK2EN_1, CONCAT_EN_0, CONCAT_EN_1, CS1_0, CS1_1,CS2_0, CS2_1, DIR_0, DIR_1, FIFO_EN_0, FIFO_EN_1, P1_0, P1_1, P2_0,P2_1, PIPELINE_RD_0, PIPELINE_RD_1,
    output [3:0] POP_FLAG_0,
    output [3:0] POP_FLAG_1,
    output [3:0] PUSH_FLAG_0,
    output [3:0] PUSH_FLAG_1,
    output [17:0] RD_0,
    output [17:0] RD_1,
    input  SYNC_FIFO_0, SYNC_FIFO_1,
    input [17:0] WD_0,
    input [17:0] WD_1,
    input [1:0] WEN1_0,
    input [1:0] WEN1_1,
    input [1:0] WIDTH_SELECT1_0,
    input [1:0] WIDTH_SELECT1_1,
    input [1:0] WIDTH_SELECT2_0,
    input [1:0] WIDTH_SELECT2_1,
    input SD,DS,LS,SD_RB1,LS_RB1,DS_RB1,RMEA,RMEB,
    input [3:0] RMA,
    input [3:0] RMB,
    input TEST1A, TEST1B
    );

endmodule /* ram8k_2x1_cell_macro */

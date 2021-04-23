`include "i2c_master.v"
`include "i2c_probe.v"
`include "i2c_scan.v"
`include "simpleuart.v"

`default_nettype none

// ============================================================================

module top (
    input wire clk,

    input  wire [15:0] sw,
    output wire [15:0] led,

    input  wire rx,
    output wire tx,

    inout wire jc1,  // sda
    inout wire jc2,  // scl

    output wire jc3,  // unused
    input  wire jc4  // unused

);

  // ============================================================================
  // IOBUFs
  wire sda_i;
  wire sda_o;
  wire sda_t;

  wire scl_i;
  wire scl_o;
  wire scl_t;

  IOBUF #(
      .IOSTANDARD("LVCMOS33"),
      .DRIVE(12),
      .SLEW("SLOW")
  ) iobuf_sda (
      .I (sda_i),
      .O (sda_o),
      .T (sda_t),
      .IO(jc1)
  );

  IOBUF #(
      .IOSTANDARD("LVCMOS33"),
      .DRIVE(12),
      .SLEW("SLOW")
  ) iobuf_scl (
      .I (scl_i),
      .O (scl_o),
      .T (scl_t),
      .IO(jc2)
  );

  // ============================================================================
  // Clock buffer, reset generator
  reg  [3:0] rst_sr;
  wire       rst;
  wire       clk_g;

  initial rst_sr <= 4'hF;

  always @(posedge clk_g)
    if (sw[0]) rst_sr <= 4'hF;
    else rst_sr = {1'b0, rst_sr[3:1]};

  assign rst = rst_sr[0];

  wire clk_ibuf;
  IBUF ibuf (
      .I(clk),
      .O(clk_ibuf)
  );
  BUFG bufg (
      .I(clk_ibuf),
      .O(clk_g)
  );

  // ============================================================================
  // I2C scanner
  wire i2c_scan_trg;
  wire i2c_scan_trg_en;
  wire i2c_scan_bsy;

  // Button synchronizer
  reg [3:0] i2c_scan_trg_en_sr;
  initial i2c_scan_trg_en_sr <= 4'h0;
  always @(posedge clk_g) i2c_scan_trg_en_sr <= {sw[1], i2c_scan_trg_en_sr[3:1]};

  // The scanner
  i2c_scan #(
      .UART_PRESCALER(868),  // 115200 @100MHz
      .I2C_PRESCALER (250)  // 100kHz @100MHz
  ) i2c_scan (
      .clk(clk_g),
      .rst(rst),

      .scl_i(scl_o),
      .scl_o(scl_i),
      .scl_t(scl_t),
      .sda_i(sda_o),
      .sda_o(sda_i),
      .sda_t(sda_t),

      .rx(rx),
      .tx(tx),

      .i_trg(i2c_scan_trg & i2c_scan_trg_en_sr[0]),
      .i_bsy(i2c_scan_bsy)
  );

  // Trigger generator
  reg [32:0] trg_cnt;

  always @(posedge clk_g)
    if (rst) trg_cnt <= 0;
    else if (trg_cnt[32]) trg_cnt <= 1 * 100000000;  // 1s @100MHz
    else trg_cnt <= trg_cnt - 1;

  assign i2c_scan_trg = trg_cnt[32];

  // ============================================================================
  // I/O

  assign led[0] = rst;
  assign led[1] = i2c_scan_bsy;
  assign led[15:2] = sw[15:2];

endmodule


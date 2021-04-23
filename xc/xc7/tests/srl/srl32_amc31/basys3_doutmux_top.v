module top (
    input wire clk,

    input  wire rx,
    output wire tx,

    input  wire [15:0] sw,
    output wire [15:0] led
);

  parameter SRL_COUNT = 4;
  parameter PRESCALER = 4;

  // UART loopback
  assign tx = rx;

  // ============================================================================
  // Reset
  reg  [3:0] rst_sr;
  wire       rst;

  initial rst_sr <= 4'hF;
  always @(posedge clk)
    if (sw[0]) rst_sr <= 4'hF;
    else rst_sr <= rst_sr >> 1;

  assign rst = rst_sr[0];

  // ============================================================================
  // Clock prescaler
  reg                        [32:0] ps_cnt = 0;
  wire ps_tick = ps_cnt[32];

  always @(posedge clk)
    if (rst || ps_tick) ps_cnt <= PRESCALER - 2;
    else ps_cnt <= ps_cnt - 1;

  // ============================================================================
  // SRL32 testers

  wire sim_error = sw[2];

  wire [SRL_COUNT-1:0] srl_q31;
  wire [SRL_COUNT-1:0] error;

  genvar i;
  generate
    for (i = 0; i < SRL_COUNT; i = i + 1) begin
      wire srl_d;
      wire srl_sh;

      srl_shift_tester #(
          .FIXED_DELAY(32)
      ) tester (
          .clk   (clk),
          .rst   (rst),
          .ce    (ps_tick),
          .srl_sh(srl_sh),
          .srl_d (srl_d),
          .srl_q (srl_q31[i] ^ sim_error),
          .srl_a (),
          .error (error[i])
      );

      SRLC32E srl (
          .CLK(clk),
          .CE (srl_sh),
          .A  (5'd0),
          .D  (srl_d),
          .Q31(srl_q31[i])
      );

    end
  endgenerate

  // ============================================================================

  // Error latch
  reg [SRL_COUNT-1:0] error_lat = 0;
  always @(posedge clk)
    if (rst) error_lat <= 0;
    else error_lat <= error_lat | error;

  // ============================================================================

  // Create a non-GND/VCC source for additional LED outputs.
  // This is a side affect of the ROI disallowing GND/VCC connections to synth
  // IO pads.
  wire net_0;
  LUT2 #(
      .INIT(4'hC)
  ) lut_0 (
      .I0(|sw),
      .I1(&sw),
      .O (net_0)
  );

  // LEDs
  genvar j;
  generate
    for (j = 0; j < 8; j = j + 1) begin
      if (j < SRL_COUNT) begin
        assign led[j]   = (sw[1]) ? error_lat[j] : error[j];
        assign led[j+8] = srl_q31[j];
      end else begin
        assign led[j]   = net_0;
        assign led[j+8] = net_0;
      end
    end
  endgenerate

endmodule


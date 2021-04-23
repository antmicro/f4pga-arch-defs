module top (
    input wire clk,
    input wire [1:0] sw,
    input wire [3:0] btn,
    output wire [3:0] led,
    output wire led4_b,
    output wire led4_g,
    output wire led4_r,
    output wire led5_b,
    output wire led5_g,
    output wire led5_r
);

  localparam BITS = 4;
  localparam LOG2DELAY = 18;

  reg [BITS+LOG2DELAY-1:0] counter = 0;

  IBUF clk_ibuf (
      .I(clk),
      .O(clk_ibuf)
  );
  BUFG clk_bufg (
      .I(clk_ibuf),
      .O(clk_b)
  );

  always @(posedge clk_b) begin
    counter <= counter + 1;
  end

  assign led = counter >> LOG2DELAY;
endmodule

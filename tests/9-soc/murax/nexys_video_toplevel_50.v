`timescale 1ns / 1ps

module top (
    input clk,
    output tx,
    input rx,
    input [7:0] sw,
    output [7:0] led
);

  wire [31:0] io_gpioA_read;
  wire [31:0] io_gpioA_write;
  wire [31:0] io_gpioA_writeEnable;
  wire io_mainClk;
  wire io_jtag_tck;
  wire io_jtag_tdi;
  wire io_jtag_tdo;
  wire io_jtag_tms;
  wire io_uart_txd;
  wire io_uart_rxd;

  assign led = io_gpioA_write[7:0];
  assign io_gpioA_read[7:0] = sw;

  wire clk_bufg;
  BUFG bufg (
      .I(clk),
      .O(clk100)
  );

  // BUFGCE as divide by 2
  reg clk50_ce;
  always @(posedge clk100) clk50_ce <= !clk50_ce;

  wire clk50;
  BUFGCE bufg50 (
      .I (clk),
      .CE(clk50_ce),
      .O (clk50)
  );

  Murax murax (
      .io_asyncReset       (0),
      .io_mainClk          (clk50),
      .io_jtag_tck         (1'b0),
      .io_jtag_tdi         (1'b0),
      .io_jtag_tms         (1'b0),
      .io_gpioA_read       (io_gpioA_read),
      .io_gpioA_write      (io_gpioA_write),
      .io_gpioA_writeEnable(io_gpioA_writeEnable),
      .io_uart_txd         (tx),
      .io_uart_rxd         (rx)
  );
endmodule

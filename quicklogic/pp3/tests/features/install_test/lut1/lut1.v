module top(
  input  wire I,
  output wire O
);

  LUT1 #(.INIT(2'b01)) the_lut (
    .I0(I),
    .O(O)
  );

endmodule

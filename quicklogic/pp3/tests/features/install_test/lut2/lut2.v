module top(
  input  wire [1:0] I,
  output wire O
);

  LUT2 #(.INIT(4'b1010)) the_lut (
    .I0(I[0]),
    .I1(I[1]),
    .O(O)
  );

endmodule

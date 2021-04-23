// 4-input, xor LUT test.
module top (
    (* keep *)
    input [3:0] I,
    output O
);
  always @(I)
    case (I)
      4'b1000: O = 1;
      4'b0100: O = 1;
      4'b0010: O = 1;
      4'b0001: O = 1;
      default: O = 0;
    endcase
endmodule  // top

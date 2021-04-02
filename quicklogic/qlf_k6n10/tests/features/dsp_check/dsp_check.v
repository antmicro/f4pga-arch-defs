module dsp_check(A,B,C,out_v);
input [15:0]A;
input [159:0]B,C;
output [15:0]out_v;

wire [15:0] out_w1,out_w2,out_w3,out_w4,out_w5,out_w6,out_w7,out_w8,out_w9,out_w10;
mac_16 D1(.a(A),.b(B[15:0]),.c(C[15:0]),.out(out_w1));
mac_16 D2(.a(out_w1),.b(B[31:16]),.c(C[31:16]),.out(out_w2));
mac_16 D3(.a(out_w2),.b(B[47:32]),.c(C[47:32]),.out(out_w3));
mac_16 D4(.a(out_w3),.b(B[63:48]),.c(C[63:48]),.out(out_w4));
mac_16 D5(.a(out_w4),.b(B[79:64]),.c(C[79:64]),.out(out_w5));
mac_16 D6(.a(out_w5),.b(B[95:80]),.c(C[95:80]),.out(out_w6));
mac_16 D7(.a(out_w6),.b(B[111:96]),.c(C[111:96]),.out(out_w7));
mac_16 D8(.a(out_w7),.b(B[127:112]),.c(C[127:112]),.out(out_w8));
mac_16 D9(.a(out_w8),.b(B[143:128]),.c(C[143:128]),.out(out_w9));
mac_16 D10(.a(out_w9),.b(B[159:144]),.c(C[159:144]),.out(out_v));

endmodule

module mac_16(a, b, c, out);

   parameter DATA_WIDTH = 16;
   input [DATA_WIDTH - 1 : 0] a, b, c;
   output [DATA_WIDTH - 1 : 0] out;

   assign out = a * b + c;

endmodule












`timescale 1ns/10ps

module CANDEN(CLKIN, DYNEN, SEN, DEN, IZ);
input CLKIN, DYNEN, SEN, DEN;
output IZ;
wire CLKIN_int, DYNEN_int, SEN_int, DEN_int; 
wire mux_op0, mux_op1;

buf SEN_buf (SEN_int, SEN) ;
buf CLKIN_buf (CLKIN_int, CLKIN) ;
buf DYNEN_buf (DYNEN_int, DYNEN) ;
buf DEN_buf (DEN_int, DEN) ;

assign mux_op0 = SEN_int ? 1'b1 : 1'b0;
assign mux_op1 = DEN_int ? DYNEN_int : mux_op0;

assign IZ = CLKIN_int & SEN_int; 

specify
	if (SEN == 1'b1 && DEN == 1'b0)
	   (CLKIN => IZ) = (0,0);
   //(DYNEN => IZ) = (0,0);
   //(SEN => IZ) = (0,0);
   //(DEN => IZ) = (0,0);
endspecify

endmodule
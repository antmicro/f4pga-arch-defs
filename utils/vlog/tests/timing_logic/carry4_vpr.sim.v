module carry4_vpr (O0, O1, O2, O3, CO_CHAIN, CO0, CO1, CO2, CO3, CYINIT, CIN, DI0, DI1, DI2, DI3, S0, S1, S2, S3);
  parameter CYINIT_AX = 1'b0;
  parameter CYINIT_C0 = 1'b0;
  parameter CYINIT_C1 = 1'b0;

  output wire O0;
  output wire O1;
  output wire O2;
  output wire O3;
  output wire CO0;
  output wire CO1;
  output wire CO2;
  output wire CO3;
  (* SDF_ALIAS = "CO3" *)
  output wire CO_CHAIN;

  input wire DI0, DI1, DI2, DI3;
  input wire S0, S1, S2, S3;

  input wire CYINIT;
  input wire CIN;

  wire CI0;
  wire CI1;
  wire CI2;
  wire CI3;
  wire CI4;

  assign CI0 = (CYINIT & CYINIT_AX) | CYINIT_C1 | (CIN & (!CYINIT_AX && !CYINIT_C0 && !CYINIT_C1));
  assign CI1 = S0 ? CI0 : DI0;
  assign CI2 = S1 ? CI1 : DI1;
  assign CI3 = S2 ? CI2 : DI2;
  assign CI4 = S3 ? CI3 : DI3;

  assign CO0 = CI1;
  assign CO1 = CI2;
  assign CO2 = CI3;
  assign CO3 = CI4;

  assign O0 = CI0 ^ S0;
  assign O1 = CI1 ^ S1;
  assign O2 = CI2 ^ S2;
  assign O3 = CI3 ^ S3;

  assign CO_CHAIN = CO3;

endmodule

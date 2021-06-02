//-----------------------------------------------------//
// Design Name : Shift_reg
// File Name   : Shift_reg.v
// Function    : Shift register
//------------------------------------------------------//


module top #( parameter size = 11 ) (shift_in, clock0, shift_out);

    // Port Declaration
    input   shift_in;
    input   clock0; 
    output  shift_out;
   
    reg [ size:0 ] shift; // shift register  
   
    always @ (posedge clock0)
    begin
        shift <= { shift[size-1:0] , shift_in } ;	
    end
   
    assign shift_out = shift[size];   
   
endmodule 

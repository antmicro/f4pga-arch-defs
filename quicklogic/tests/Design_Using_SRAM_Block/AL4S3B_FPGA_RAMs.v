// -----------------------------------------------------------------------------
// title          : AL4S3B Example FPGA Register Module
// project        : Tamar2 Device
// -----------------------------------------------------------------------------
// file           : AL4S3B_FPGA_RAMs.v
// author         : SSG
// company        : QuickLogic Corp
// created        : 2020/05/27	
// last update    : 2020/05/27
// platform       : ArcticLink 4 S3B
// standard       : Verilog 2001
// -----------------------------------------------------------------------------
// description: The FPGA example IP design contains the essential logic for
//              interfacing the ASSP of the AL4S3B to registers and memory 
//              located in the programmable FPGA.
// -----------------------------------------------------------------------------
// copyright (c) 2016
// -----------------------------------------------------------------------------
// revisions  :
// date            version    author                  description
// 2020/05/27      1.0        Rakesh moolacheri     Initial Release
//
// -----------------------------------------------------------------------------
// Comments: This solution is specifically for use with the QuickLogic
//           AL4S3B device. 
// -----------------------------------------------------------------------------
//
`timescale 1ns / 10ps
module AL4S3B_FPGA_RAMs ( 

                         // AHB-To_FPGA Bridge I/F
                         //
                         WBs_ADR_i,
                         WBs_RAM1_CYC_i,
						 WBs_RAM2_CYC_i,
						 WBs_RAM3_CYC_i,
                         WBs_BYTE_STB_i,
                         WBs_WE_i,
                         WBs_STB_i,
                         WBs_DAT_i,
                         WBs_CLK_i,
                         WBs_RST_i,
                         WBs_RAM1_DAT_o,
						 WBs_RAM2_DAT_o,
						 WBs_RAM3_DAT_o,
                         WBs_ACK_o
                         );


//------Port Parameters----------------
//

parameter                ADDRWIDTH                   =   7  ;   // Allow for up to 128 registers in the FPGA
parameter                DATAWIDTH                   =  32  ;   // Allow for up to 128 registers in the FPGA

parameter                AL4S3B_DEF_REG_VALUE        = 32'hFAB_DEF_AC;


//------Port Signals-------------------
//

// AHB-To_FPGA Bridge I/F
//
input   [10:0]           WBs_ADR_i     ;  // Address Bus                to   FPGA
input                    WBs_RAM1_CYC_i;  
input                    WBs_RAM2_CYC_i;
input                    WBs_RAM3_CYC_i;
input             [3:0]  WBs_BYTE_STB_i;  // Byte Select                to   FPGA
input                    WBs_WE_i      ;  // Write Enable               to   FPGA
input                    WBs_STB_i     ;  // Strobe Signal              to   FPGA
input   [DATAWIDTH-1:0]  WBs_DAT_i     ;  // Write Data Bus             to   FPGA
input                    WBs_CLK_i     ;  // FPGA Clock               from FPGA
input                    WBs_RST_i     ;  // FPGA Reset               to   FPGA
output  [DATAWIDTH-1:0]  WBs_RAM1_DAT_o;  
output  [DATAWIDTH-1:0]  WBs_RAM2_DAT_o;  
output  [DATAWIDTH-1:0]  WBs_RAM3_DAT_o;  
output                   WBs_ACK_o     ;  // Transfer Cycle Acknowledge from FPGA



// FPGA Global Signals
//
wire                     WBs_CLK_i     ;  // Wishbone FPGA Clock
wire                     WBs_RST_i     ;  // Wishbone FPGA Reset

// Wishbone Bus Signals
//
wire    [ADDRWIDTH-1:0]  WBs_ADR_i     ;  // Wishbone Address Bus
wire                     WBs_RAM1_CYC_i;  
wire                     WBs_RAM2_CYC_i;
wire                     WBs_RAM3_CYC_i;
wire              [3:0]  WBs_BYTE_STB_i;  // Wishbone Byte   Enables
wire                     WBs_WE_i      ;  // Wishbone Write  Enable Strobe
wire                     WBs_STB_i     ;  // Wishbone Transfer      Strobe
wire    [DATAWIDTH-1:0]  WBs_DAT_i     ;  // Wishbone Write  Data Bus
 
reg                      WBs_ACK_o     ;  // Wishbone Client Acknowledge

//------Define Parameters--------------
//

//
// None at this time
//

//------Internal Signals---------------
//
wire                     FB_RAM1_Wr_Dcd    ;
wire                     FB_RAM2_Wr_Dcd    ;
wire                     FB_RAM3_Wr_Dcd    ;

wire					 WBs_ACK_o_nxt;

wire [15:0]  RAM1_Dat_out;
wire [7:0]   RAM2_Dat_out;
wire [31:0]  RAM3_Dat_out;


//------Logic Operations---------------
//

// Define the FPGA's local register write enables
//
assign FB_RAM1_Wr_Dcd    = WBs_RAM1_CYC_i & WBs_STB_i & WBs_WE_i  & (~WBs_ACK_o);
assign FB_RAM2_Wr_Dcd    = WBs_RAM2_CYC_i & WBs_STB_i & WBs_WE_i  & (~WBs_ACK_o);
assign FB_RAM3_Wr_Dcd    = WBs_RAM3_CYC_i & WBs_STB_i & WBs_WE_i  & (~WBs_ACK_o);

// Define the Acknowledge back to the host for registers
//
assign WBs_ACK_o_nxt     = (WBs_RAM1_CYC_i | WBs_RAM2_CYC_i | WBs_RAM3_CYC_i) & WBs_STB_i & (~WBs_ACK_o);


// Define the FPGA's Local Registers
//
always @( posedge WBs_CLK_i or posedge WBs_RST_i)
begin
    if (WBs_RST_i)
    begin
        WBs_ACK_o         <=  1'b0           ;
    end  
    else
    begin
        WBs_ACK_o         <=  WBs_ACK_o_nxt  ;
    end  
end

assign WBs_RAM1_DAT_o = {16'h0,RAM1_Dat_out};
assign WBs_RAM2_DAT_o = {24'h0,RAM2_Dat_out};

r512x16_512x16_r1024x8_1024x8 RAM0RAM1_INST (	
			.WA0(WBs_ADR_i[8:0]),
			.RA0(WBs_ADR_i[8:0]),
			.WD0(WBs_DAT_i[15:0]),
			.WD0_SEL(1'b1),
			.RD0_SEL(1'b1),
			.WClk0(WBs_CLK_i),
			.RClk0(WBs_CLK_i),
			.WClk0_En(1'b1),
			.RClk0_En(1'b1),
			.WEN0({FB_RAM1_Wr_Dcd,FB_RAM1_Wr_Dcd}),
			.RD0(RAM1_Dat_out),
		
			.WA1(WBs_ADR_i[9:0]),
			.RA1(WBs_ADR_i[9:0]),
			.WD1(WBs_DAT_i[7:0]),
			.WD1_SEL(1'b1),
			.RD1_SEL(1'b1),
			.WClk1(WBs_CLK_i),
			.RClk1(WBs_CLK_i),
			.WClk1_En(1'b1),
			.RClk1_En(1'b1),
			.WEN1(FB_RAM2_Wr_Dcd),
			.RD1(RAM2_Dat_out)
			);
			
assign WBs_RAM3_DAT_o = RAM3_Dat_out;

r512x32_512x32 RAM3_INST (	
			.WA(WBs_ADR_i[8:0]),
			.RA(WBs_ADR_i[8:0]),
			.WD(WBs_DAT_i[31:0]),
			.WD_SEL(1'b1),
			.RD_SEL(1'b1),
			.WClk(WBs_CLK_i),
			.RClk(WBs_CLK_i),
			.WClk_En(1'b1),
			.RClk_En(1'b1),
			.WEN({FB_RAM3_Wr_Dcd,FB_RAM3_Wr_Dcd,FB_RAM3_Wr_Dcd,FB_RAM3_Wr_Dcd}),
			.RD(RAM3_Dat_out)
			);
			
endmodule

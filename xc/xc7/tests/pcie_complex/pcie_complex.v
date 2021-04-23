module top (
    (* dont_touch = "true" *) input wire pcie_pipe_clk,
    input wire pcie_rst_n,
    (* dont_touch = "true" *) input wire pcie_clk_p,
    input wire pcie_clk_n,
    input wire pcie_rx_p,
    input wire pcie_rx_n,
    output wire pcie_tx_p,
    output wire pcie_tx_n,
    output drprdy
);
  wire pcie_refclk, pcie_gt_refclk, pcie_pll0clk;
  wire DRPCLK, DRPRDY, DRPEN, DRPWE;

  wire [15:0] DRPDI;
  wire [15:0] GTP_COMMON_DRPDI;
  wire [15:0] GTP_CHANNEL_DRPDI;
  wire [15:0] PCIE_DRPDI;

  wire [15:0] DRPDO;
  wire [15:0] GTP_COMMON_DRPDO;
  wire [15:0] GTP_CHANNEL_DRPDO;
  wire [15:0] PCIE_DRPDO;

  wire GTP_COMMON_DRPRDY, GTP_CHANNEL_DRPRDY, PCIE_DRPRDY;

  assign DRPEN  = 1'b1;
  assign DRPWE  = 1'b1;

  assign drprdy = GTP_COMMON_DRPRDY & GTP_CHANNEL_DRPRDY & PCIE_DRPRDY;

  genvar i;
  generate
    for (i = 0; i < 16; i = i + 1) begin
      assign DRPDO[i] = GTP_COMMON_DRPDO & GTP_CHANNEL_DRPDO & PCIE_DRPDO;
    end
  endgenerate

  generate
    for (i = 0; i < 16; i = i + 1) begin
      assign GTP_COMMON_DRPDI[i] = DRPDI[i];
      assign GTP_CHANNEL_DRPDI[i] = DRPDI[i];
      assign PCIE_DRPDI[i] = DRPDI[i];
    end
  endgenerate

  IBUFDS_GTE2 IBUFDS_GTE2 (
      .CEB(pcie_rst_n),
      .I  (pcie_clk_p),
      .IB (pcie_clk_n),
      .O  (pcie_refclk)
  );

  GTPE2_COMMON #(
      .BIAS_CFG(64'h0000000000050001),
      .COMMON_CFG(32'h00000000),
      .IS_DRPCLK_INVERTED(1'b0),
      .IS_GTGREFCLK0_INVERTED(1'b0),
      .IS_GTGREFCLK1_INVERTED(1'b0),
      .IS_PLL0LOCKDETCLK_INVERTED(1'b0),
      .IS_PLL1LOCKDETCLK_INVERTED(1'b0),
      .PLL0_CFG(27'h01F024C),
      .PLL0_DMON_CFG(1'b0),
      .PLL0_FBDIV(5),
      .PLL0_FBDIV_45(5),
      .PLL0_INIT_CFG(24'h00001E),
      .PLL0_LOCK_CFG(9'h1E8),
      .PLL0_REFCLK_DIV(1),
      .PLL1_CFG(27'h01F024C),
      .PLL1_DMON_CFG(1'b0),
      .PLL1_FBDIV(5),
      .PLL1_FBDIV_45(5),
      .PLL1_INIT_CFG(24'h00001E),
      .PLL1_LOCK_CFG(9'h1E8),
      .PLL1_REFCLK_DIV(1),
      .PLL_CLKOUT_CFG(8'b00000000),
      .RSVD_ATTR0(16'h0000),
      .RSVD_ATTR1(16'h0000)
  ) GTP_COMMON_INST (
      .BGBYPASSB(1'b1),
      .BGMONITORENB(1'b1),
      .BGPDB(1'b1),
      .BGRCALOVRD({1'b1, 1'b1, 1'b1, 1'b1, 1'b1}),
      .BGRCALOVRDENB(1'b1),
      .DRPADDR(8'b10101010),
      .DRPCLK(DRPCLK),
      .DRPDI(GTP_COMMON_DRPDI),
      .DRPDO(GTP_COMMON_DRPDO),
      .DRPEN(DRPEN),
      .DRPRDY(GTP_COMMON_DRPRDY),
      .DRPWE(DRPWE),
      .GTGREFCLK0(1'b0),
      .GTGREFCLK1(1'b0),
      .GTREFCLK0(pcie_refclk),
      .GTREFCLK1(1'b0),
      .PLL0OUTCLK(pcie_pll0clk),
      .PLL0OUTREFCLK(pcie_gt_refclk),
      .PLL0LOCKDETCLK(1'b0),
      .PLL0LOCKEN(1'b1),
      .PLL0REFCLKSEL({1'b0, 1'b0, 1'b1}),
      .PLL1LOCKDETCLK(1'b0),
      .PLL1LOCKEN(1'b1),
      .PLL1PD(1'b1),
      .PLL1REFCLKSEL({1'b0, 1'b0, 1'b1}),
      .PLL1RESET(1'b1),
      .PMARSVD({1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0}),
      .RCALENB(1'b1),
  );

  GTPE2_CHANNEL #(
      .ACJTAG_DEBUG_MODE(1'b0),
      .ACJTAG_MODE(1'b0),
      .ACJTAG_RESET(1'b0),
      .ADAPT_CFG0(20'b00000000000000000000),
      .ALIGN_COMMA_DOUBLE("FALSE"),
      .ALIGN_COMMA_ENABLE(10'b1111111111),
      .ALIGN_COMMA_WORD(1),
      .ALIGN_MCOMMA_DET("TRUE"),
      .ALIGN_MCOMMA_VALUE(10'b1010000011),
      .ALIGN_PCOMMA_DET("TRUE"),
      .ALIGN_PCOMMA_VALUE(10'b0101111100),
      .CBCC_DATA_SOURCE_SEL("DECODED"),
      .CFOK_CFG(43'b1001001000000000000000001000000111010000000),
      .CFOK_CFG2(7'b0100000),
      .CFOK_CFG3(7'b0100000),
      .CFOK_CFG4(1'b0),
      .CFOK_CFG5(2'b00),
      .CFOK_CFG6(4'b0000),
      .CHAN_BOND_KEEP_ALIGN("TRUE"),
      .CHAN_BOND_MAX_SKEW(7),
      .CHAN_BOND_SEQ_1_1(10'b0001001010),
      .CHAN_BOND_SEQ_1_2(10'b0001001010),
      .CHAN_BOND_SEQ_1_3(10'b0001001010),
      .CHAN_BOND_SEQ_1_4(10'b0110111100),
      .CHAN_BOND_SEQ_1_ENABLE(4'b1111),
      .CHAN_BOND_SEQ_2_1(10'b0001000101),
      .CHAN_BOND_SEQ_2_2(10'b0001000101),
      .CHAN_BOND_SEQ_2_3(10'b0001000101),
      .CHAN_BOND_SEQ_2_4(10'b0110111100),
      .CHAN_BOND_SEQ_2_ENABLE(4'b1111),
      .CHAN_BOND_SEQ_2_USE("TRUE"),
      .CHAN_BOND_SEQ_LEN(4),
      .CLK_COMMON_SWING(1'b0),
      .CLK_CORRECT_USE("TRUE"),
      .CLK_COR_KEEP_IDLE("TRUE"),
      .CLK_COR_MAX_LAT(21),
      .CLK_COR_MIN_LAT(19),
      .CLK_COR_PRECEDENCE("TRUE"),
      .CLK_COR_REPEAT_WAIT(0),
      .CLK_COR_SEQ_1_1(10'b0100011100),
      .CLK_COR_SEQ_1_2(10'b0000000000),
      .CLK_COR_SEQ_1_3(10'b0000000000),
      .CLK_COR_SEQ_1_4(10'b0000000000),
      .CLK_COR_SEQ_1_ENABLE(4'b1111),
      .CLK_COR_SEQ_2_1(10'b0000000000),
      .CLK_COR_SEQ_2_2(10'b0000000000),
      .CLK_COR_SEQ_2_3(10'b0000000000),
      .CLK_COR_SEQ_2_4(10'b0000000000),
      .CLK_COR_SEQ_2_ENABLE(4'b0000),
      .CLK_COR_SEQ_2_USE("FALSE"),
      .CLK_COR_SEQ_LEN(1),
      .DEC_MCOMMA_DETECT("TRUE"),
      .DEC_PCOMMA_DETECT("TRUE"),
      .DEC_VALID_COMMA_ONLY("FALSE"),
      .DMONITOR_CFG(24'h000B01),
      .ES_CLK_PHASE_SEL(1'b0),
      .ES_CONTROL(6'b000000),
      .ES_ERRDET_EN("FALSE"),
      .ES_EYE_SCAN_EN("FALSE"),
      .ES_HORZ_OFFSET(12'h010),
      .ES_PMA_CFG(10'b0000000000),
      .ES_PRESCALE(5'b00000),
      .ES_QUALIFIER(80'h00000000000000000000),
      .ES_QUAL_MASK(80'h00000000000000000000),
      .ES_SDATA_MASK(80'h00000000000000000000),
      .ES_VERT_OFFSET(9'b000000000),
      .FTS_DESKEW_SEQ_ENABLE(4'b1111),
      .FTS_LANE_DESKEW_CFG(4'b1111),
      .FTS_LANE_DESKEW_EN("TRUE"),
      .GEARBOX_MODE(3'b000),
      .IS_CLKRSVD0_INVERTED(1'b0),
      .IS_CLKRSVD1_INVERTED(1'b0),
      .IS_DMONITORCLK_INVERTED(1'b0),
      .IS_DRPCLK_INVERTED(1'b0),
      .IS_RXUSRCLK2_INVERTED(1'b0),
      .IS_RXUSRCLK_INVERTED(1'b0),
      .IS_SIGVALIDCLK_INVERTED(1'b0),
      .IS_TXPHDLYTSTCLK_INVERTED(1'b0),
      .IS_TXUSRCLK2_INVERTED(1'b0),
      .IS_TXUSRCLK_INVERTED(1'b0),
      .LOOPBACK_CFG(1'b0),
      .OUTREFCLK_SEL_INV(2'b11),
      .PCS_PCIE_EN("TRUE"),
      .PCS_RSVD_ATTR(48'h000000000100),
      .PD_TRANS_TIME_FROM_P2(12'h03C),
      .PD_TRANS_TIME_NONE_P2(8'h09),
      .PD_TRANS_TIME_TO_P2(8'h64),
      .PMA_LOOPBACK_CFG(1'b0),
      .PMA_RSV(32'h00000333),
      .PMA_RSV2(32'h00002040),
      .PMA_RSV3(2'b00),
      .PMA_RSV4(4'b0000),
      .PMA_RSV5(1'b0),
      .PMA_RSV6(1'b0),
      .PMA_RSV7(1'b0),
      .RXBUFRESET_TIME(5'b00001),
      .RXBUF_ADDR_MODE("FULL"),
      .RXBUF_EIDLE_HI_CNT(4'b0100),
      .RXBUF_EIDLE_LO_CNT(4'b0000),
      .RXBUF_EN("TRUE"),
      .RXBUF_RESET_ON_CB_CHANGE("TRUE"),
      .RXBUF_RESET_ON_COMMAALIGN("FALSE"),
      .RXBUF_RESET_ON_EIDLE("TRUE"),
      .RXBUF_RESET_ON_RATE_CHANGE("TRUE"),
      .RXBUF_THRESH_OVFLW(61),
      .RXBUF_THRESH_OVRD("FALSE"),
      .RXBUF_THRESH_UNDFLW(4),
      .RXCDRFREQRESET_TIME(5'b00001),
      .RXCDRPHRESET_TIME(5'b00001),
      .RXCDR_CFG(83'h0000107FE406001041010),
      .RXCDR_FR_RESET_ON_EIDLE(1'b0),
      .RXCDR_HOLD_DURING_EIDLE(1'b1),
      .RXCDR_LOCK_CFG(6'b010101),
      .RXCDR_PH_RESET_ON_EIDLE(1'b0),
      .RXDLY_CFG(16'h001F),
      .RXDLY_LCFG(9'h030),
      .RXDLY_TAP_CFG(16'h0000),
      .RXGEARBOX_EN("FALSE"),
      .RXISCANRESET_TIME(5'b00001),
      .RXLPMRESET_TIME(7'b0001111),
      .RXLPM_BIAS_STARTUP_DISABLE(1'b0),
      .RXLPM_CFG(4'b0110),
      .RXLPM_CFG1(1'b0),
      .RXLPM_CM_CFG(1'b0),
      .RXLPM_GC_CFG(9'b111100010),
      .RXLPM_GC_CFG2(3'b001),
      .RXLPM_HF_CFG(14'b00001111110000),
      .RXLPM_HF_CFG2(5'b01010),
      .RXLPM_HF_CFG3(4'b0000),
      .RXLPM_HOLD_DURING_EIDLE(1'b1),
      .RXLPM_INCM_CFG(1'b1),
      .RXLPM_IPCM_CFG(1'b0),
      .RXLPM_LF_CFG(18'b000000001111110000),
      .RXLPM_LF_CFG2(5'b01010),
      .RXLPM_OSINT_CFG(3'b100),
      .RXOOB_CFG(7'b0000110),
      .RXOOB_CLK_CFG("FABRIC"),
      .RXOSCALRESET_TIME(5'b00011),
      .RXOSCALRESET_TIMEOUT(5'b00000),
      .RXOUT_DIV(2),
      .RXPCSRESET_TIME(5'b00001),
      .RXPHDLY_CFG(24'h004020),
      .RXPH_CFG(24'h000000),
      .RXPH_MONITOR_SEL(5'b00000),
      .RXPI_CFG0(3'b000),
      .RXPI_CFG1(1'b1),
      .RXPI_CFG2(1'b1),
      .RXPMARESET_TIME(5'b00011),
      .RXPRBS_ERR_LOOPBACK(1'b0),
      .RXSLIDE_AUTO_WAIT(7),
      .RXSLIDE_MODE("PMA"),
      .RXSYNC_MULTILANE(1'b1),
      .RXSYNC_OVRD(1'b1),
      .RXSYNC_SKIP_DA(1'b0),
      .RX_BIAS_CFG(16'b0000111100110011),
      .RX_BUFFER_CFG(6'b000000),
      .RX_CLK25_DIV(4),
      .RX_CLKMUX_EN(1'b1),
      .RX_CM_SEL(2'b11),
      .RX_CM_TRIM(4'b1010),
      .RX_DATA_WIDTH(20),
      .RX_DDI_SEL(6'b000000),
      .RX_DEBUG_CFG(14'b00000000000000),
      .RX_DEFER_RESET_BUF_EN("TRUE"),
      .RX_DISPERR_SEQ_MATCH("TRUE"),
      .RX_OS_CFG(13'b0000010000000),
      .RX_SIG_VALID_DLY(10),
      .RX_XCLK_SEL("RXREC"),
      .SAS_MAX_COM(64),
      .SAS_MIN_COM(36),
      .SATA_BURST_SEQ_LEN(4'b1111),
      .SATA_BURST_VAL(3'b100),
      .SATA_EIDLE_VAL(3'b100),
      .SATA_MAX_BURST(8),
      .SATA_MAX_INIT(21),
      .SATA_MAX_WAKE(7),
      .SATA_MIN_BURST(4),
      .SATA_MIN_INIT(12),
      .SATA_MIN_WAKE(4),
      .SATA_PLL_CFG("VCO_3000MHZ"),
      .SHOW_REALIGN_COMMA("FALSE"),
      .TERM_RCAL_CFG(15'b100001000010000),
      .TERM_RCAL_OVRD(3'b000),
      .TRANS_TIME_RATE(8'h0E),
      .TST_RSV(32'h00000000),
      .TXBUF_EN("FALSE"),
      .TXBUF_RESET_ON_RATE_CHANGE("TRUE"),
      .TXDLY_CFG(16'h001F),
      .TXDLY_LCFG(9'h030),
      .TXDLY_TAP_CFG(16'h0000),
      .TXGEARBOX_EN("FALSE"),
      .TXOOB_CFG(1'b1),
      .TXOUT_DIV(2),
      .TXPCSRESET_TIME(5'b00001),
      .TXPHDLY_CFG(24'h084020),
      .TXPH_CFG(16'h0780),
      .TXPH_MONITOR_SEL(5'b00000),
      .TXPI_CFG0(2'b00),
      .TXPI_CFG1(2'b00),
      .TXPI_CFG2(2'b00),
      .TXPI_CFG3(1'b0),
      .TXPI_CFG4(1'b0),
      .TXPI_CFG5(3'b000),
      .TXPI_GREY_SEL(1'b0),
      .TXPI_INVSTROBE_SEL(1'b0),
      .TXPI_PPMCLK_SEL("TXUSRCLK2"),
      .TXPI_PPM_CFG(8'b00000000),
      .TXPI_SYNFREQ_PPM(3'b000),
      .TXPMARESET_TIME(5'b00011),
      .TXSYNC_MULTILANE(1'b1),
      .TXSYNC_OVRD(1'b1),
      .TXSYNC_SKIP_DA(1'b0),
      .TX_CLK25_DIV(4),
      .TX_CLKMUX_EN(1'b1),
      .TX_DATA_WIDTH(20),
      .TX_DEEMPH0(6'b010100),
      .TX_DEEMPH1(6'b001011),
      .TX_DRIVE_MODE("PIPE"),
      .TX_EIDLE_ASSERT_DELAY(3'b010),
      .TX_EIDLE_DEASSERT_DELAY(3'b010),
      .TX_LOOPBACK_DRIVE_HIZ("FALSE"),
      .TX_MAINCURSOR_SEL(1'b0),
      .TX_MARGIN_FULL_0(7'b1001111),
      .TX_MARGIN_FULL_1(7'b1001110),
      .TX_MARGIN_FULL_2(7'b1001101),
      .TX_MARGIN_FULL_3(7'b1001100),
      .TX_MARGIN_FULL_4(7'b1000011),
      .TX_MARGIN_LOW_0(7'b1000101),
      .TX_MARGIN_LOW_1(7'b1000110),
      .TX_MARGIN_LOW_2(7'b1000011),
      .TX_MARGIN_LOW_3(7'b1000010),
      .TX_MARGIN_LOW_4(7'b1000000),
      .TX_PREDRIVER_MODE(1'b0),
      .TX_RXDETECT_CFG(14'h0064),
      .TX_RXDETECT_REF(3'b011),
      .TX_XCLK_SEL("TXUSR"),
      .UCODEER_CLR(1'b0),
      .USE_PCS_CLK_PHASE_SEL(1'b0)
  ) GTP_CHANNEL_INST (
      .CFGRESET(1'b0),
      .CLKRSVD0(1'b0),
      .CLKRSVD1(1'b0),
      .DMONFIFORESET(1'b0),
      .DMONITORCLK(1'b0),
      .DRPADDR(8'b10101010),
      .DRPCLK(DRPCLK),
      .DRPDI(GTP_CHANNEL_DRPDI),
      .DRPDO(GTP_CHANNEL_DRPDO),
      .DRPEN(DRPEN),
      .DRPRDY(GTP_CHANNEL_DRPRDY),
      .DRPWE(DRPWE),
      .GTPRXN(pcie_rx_n),
      .GTPRXP(pcie_rx_p),
      .GTPTXN(pcie_tx_n),
      .GTPTXP(pcie_tx_p),
      .GTRESETSEL(1'b0),
      .GTRSVD({
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0
      }),
      .GTRXRESET(pcie_rst_n),
      .GTTXRESET(pcie_rst_n),
      .PCSRSVDIN({
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0,
        1'b0
      }),
      .PLL0CLK(pcie_pll0clk),
      .PLL0REFCLK(pcie_gt_refclk),
      .PLL1CLK(1'b0),
      .PLL1REFCLK(1'b0),
      .PMARSVDIN0(1'b0),
      .PMARSVDIN1(1'b0),
      .PMARSVDIN2(1'b0),
      .PMARSVDIN3(1'b0),
      .PMARSVDIN4(1'b0),
      .RX8B10BEN(1'b1),
      .RXADAPTSELTEST({
        1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0
      }),
      .RXCDRHOLD(1'b0),
      .RXCDROVRDEN(1'b0),
      .RXCDRRESETRSV(1'b0),
      .RXCHBONDEN(1'b1),
      .RXCHBONDI({1'b0, 1'b0, 1'b0, 1'b0}),
      .RXCHBONDLEVEL({1'b0, 1'b1, 1'b1}),
      .RXCHBONDMASTER(1'b1),
      .RXCHBONDSLAVE(1'b0),
      .RXCOMMADETEN(1'b1),
      .RXDDIEN(1'b0),
      .RXDFEXYDEN(1'b0),
      .RXDLYBYPASS(1'b1),
      .RXDLYEN(1'b0),
      .RXDLYOVRDEN(1'b0),
      .RXDLYSRESET(1'b0),
      .RXELECIDLEMODE({1'b0, 1'b0}),
      .RXGEARBOXSLIP(1'b0),
      .RXLPMHFHOLD(1'b0),
      .RXLPMHFOVRDEN(1'b0),
      .RXLPMLFHOLD(1'b0),
      .RXLPMLFOVRDEN(1'b0),
      .RXLPMOSINTNTRLEN(1'b0),
      .RXLPMRESET(1'b0),
      .RXMCOMMAALIGNEN(1'b1),
      .RXOOBRESET(1'b0),
      .RXOSCALRESET(1'b0),
      .RXOSHOLD(1'b0),
      .RXOSINTCFG({1'b0, 1'b0, 1'b1, 1'b0}),
      .RXOSINTEN(1'b1),
      .RXOSINTHOLD(1'b0),
      .RXOSINTID0({1'b0, 1'b0, 1'b0, 1'b0}),
      .RXOSINTNTRLEN(1'b0),
      .RXOSINTOVRDEN(1'b0),
      .RXOSINTPD(1'b0),
      .RXOSINTSTROBE(1'b0),
      .RXOSINTTESTOVRDEN(1'b0),
      .RXOSOVRDEN(1'b0),
      .RXOUTCLKSEL({1'b0, 1'b0, 1'b0}),
      .RXPCOMMAALIGNEN(1'b1),
      .RXPCSRESET(pcie_rst_n),
      .RXPHALIGN(1'b0),
      .RXPHALIGNEN(1'b0),
      .RXPHDLYPD(1'b0),
      .RXPHDLYRESET(1'b0),
      .RXPHOVRDEN(1'b0),
      .RXPMARESET(pcie_rst_n),
      .RXPRBSCNTRESET(pcie_rst_n),
      .RXRATEMODE(1'b0),
      .RXSLIDE(1'b0),
      .RXSYNCMODE(1'b1),
      .RXSYSCLKSEL({1'b0, 1'b0}),
      .SETERRSTATUS(1'b0),
      .TSTIN({
        1'b1,
        1'b1,
        1'b1,
        1'b1,
        1'b1,
        1'b1,
        1'b1,
        1'b1,
        1'b1,
        1'b1,
        1'b1,
        1'b1,
        1'b1,
        1'b1,
        1'b1,
        1'b1,
        1'b1,
        1'b1,
        1'b1,
        1'b1
      }),
      .TX8B10BBYPASS({1'b0, 1'b0, 1'b0, 1'b0}),
      .TX8B10BEN(1'b1),
      .TXBUFDIFFCTRL({1'b1, 1'b0, 1'b0}),
      .TXCHARDISPVAL({1'b0, 1'b0, 1'b0, 1'b0}),
      .TXCOMINIT(1'b0),
      .TXCOMSAS(1'b0),
      .TXCOMWAKE(1'b0),
      .TXDIFFCTRL({1'b1, 1'b1, 1'b0, 1'b0}),
      .TXDIFFPD(1'b0),
      .TXDLYBYPASS(1'b0),
      .TXDLYHOLD(1'b0),
      .TXDLYOVRDEN(1'b0),
      .TXDLYUPDOWN(1'b0),
      .TXHEADER({1'b0, 1'b0, 1'b0}),
      .TXOUTCLKSEL({1'b0, 1'b1, 1'b1}),
      .TXPCSRESET(1'b0),
      .TXPDELECIDLEMODE(1'b0),
      .TXPHALIGNEN(1'b1),
      .TXPHDLYPD(1'b0),
      .TXPHDLYRESET(1'b0),
      .TXPHDLYTSTCLK(1'b0),
      .TXPHOVRDEN(1'b0),
      .TXPIPPMEN(1'b0),
      .TXPIPPMOVRDEN(1'b0),
      .TXPIPPMPD(1'b0),
      .TXPIPPMSEL(1'b0),
      .TXPIPPMSTEPSIZE({1'b0, 1'b0, 1'b0, 1'b0, 1'b0}),
      .TXPISOPD(1'b0),
      .TXPMARESET(1'b0),
      .TXPOLARITY(1'b0),
      .TXPOSTCURSORINV(1'b0),
      .TXPRECURSORINV(1'b0),
      .TXRATEMODE(1'b0),
      .TXSEQUENCE({1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0, 1'b0}),
      .TXSTARTSEQ(1'b0),
      .TXSWING(1'b0),
      .TXSYNCMODE(1'b1),
      .TXSYSCLKSEL({1'b0, 1'b0}),
  );

  PCIE_2_1 #(
      .AER_BASE_PTR(12'h000),
      .AER_CAP_ECRC_CHECK_CAPABLE("FALSE"),
      .AER_CAP_ECRC_GEN_CAPABLE("FALSE"),
      .AER_CAP_ID(16'h0001),
      .AER_CAP_MULTIHEADER("FALSE"),
      .AER_CAP_NEXTPTR(12'h000),
      .AER_CAP_ON("FALSE"),
      .AER_CAP_OPTIONAL_ERR_SUPPORT(24'h000000),
      .AER_CAP_PERMIT_ROOTERR_UPDATE("FALSE"),
      .AER_CAP_VERSION(4'h1),
      .ALLOW_X8_GEN2("FALSE"),
      .BAR0(32'hFFF00000),
      .BAR1(32'h00000000),
      .BAR2(32'h00000000),
      .BAR3(32'h00000000),
      .BAR4(32'h00000000),
      .BAR5(32'h00000000),
      .CAPABILITIES_PTR(8'h40),
      .CARDBUS_CIS_POINTER(32'h00000000),
      .CFG_ECRC_ERR_CPLSTAT(0),
      .CLASS_CODE(24'h058000),
      .CMD_INTX_IMPLEMENTED("FALSE"),
      .CPL_TIMEOUT_DISABLE_SUPPORTED("FALSE"),
      .CPL_TIMEOUT_RANGES_SUPPORTED(4'h2),
      .CRM_MODULE_RSTS(7'h00),
      .DEV_CAP2_ARI_FORWARDING_SUPPORTED("FALSE"),
      .DEV_CAP2_ATOMICOP32_COMPLETER_SUPPORTED("FALSE"),
      .DEV_CAP2_ATOMICOP64_COMPLETER_SUPPORTED("FALSE"),
      .DEV_CAP2_ATOMICOP_ROUTING_SUPPORTED("FALSE"),
      .DEV_CAP2_CAS128_COMPLETER_SUPPORTED("FALSE"),
      .DEV_CAP2_ENDEND_TLP_PREFIX_SUPPORTED("FALSE"),
      .DEV_CAP2_EXTENDED_FMT_FIELD_SUPPORTED("FALSE"),
      .DEV_CAP2_LTR_MECHANISM_SUPPORTED("FALSE"),
      .DEV_CAP2_MAX_ENDEND_TLP_PREFIXES(2'h0),
      .DEV_CAP2_NO_RO_ENABLED_PRPR_PASSING("FALSE"),
      .DEV_CAP2_TPH_COMPLETER_SUPPORTED(2'h0),
      .DEV_CAP_ENABLE_SLOT_PWR_LIMIT_SCALE("TRUE"),
      .DEV_CAP_ENABLE_SLOT_PWR_LIMIT_VALUE("TRUE"),
      .DEV_CAP_ENDPOINT_L0S_LATENCY(0),
      .DEV_CAP_ENDPOINT_L1_LATENCY(7),
      .DEV_CAP_EXT_TAG_SUPPORTED("FALSE"),
      .DEV_CAP_FUNCTION_LEVEL_RESET_CAPABLE("FALSE"),
      .DEV_CAP_MAX_PAYLOAD_SUPPORTED(2),
      .DEV_CAP_PHANTOM_FUNCTIONS_SUPPORT(0),
      .DEV_CAP_ROLE_BASED_ERROR("TRUE"),
      .DEV_CAP_RSVD_14_12(0),
      .DEV_CAP_RSVD_17_16(0),
      .DEV_CAP_RSVD_31_29(0),
      .DEV_CONTROL_AUX_POWER_SUPPORTED("FALSE"),
      .DEV_CONTROL_EXT_TAG_DEFAULT("FALSE"),
      .DISABLE_ASPM_L1_TIMER("FALSE"),
      .DISABLE_BAR_FILTERING("FALSE"),
      .DISABLE_ERR_MSG("FALSE"),
      .DISABLE_ID_CHECK("FALSE"),
      .DISABLE_LANE_REVERSAL("TRUE"),
      .DISABLE_LOCKED_FILTER("FALSE"),
      .DISABLE_PPM_FILTER("FALSE"),
      .DISABLE_RX_POISONED_RESP("FALSE"),
      .DISABLE_RX_TC_FILTER("FALSE"),
      .DISABLE_SCRAMBLING("FALSE"),
      .DNSTREAM_LINK_NUM(8'h00),
      .DSN_BASE_PTR(12'h100),
      .DSN_CAP_ID(16'h0003),
      .DSN_CAP_NEXTPTR(12'h000),
      .DSN_CAP_ON("TRUE"),
      .DSN_CAP_VERSION(4'h1),
      .ENABLE_MSG_ROUTE(11'h000),
      .ENABLE_RX_TD_ECRC_TRIM("FALSE"),
      .ENDEND_TLP_PREFIX_FORWARDING_SUPPORTED("FALSE"),
      .ENTER_RVRY_EI_L0("TRUE"),
      .EXIT_LOOPBACK_ON_EI("TRUE"),
      .EXPANSION_ROM(32'h00000000),
      .EXT_CFG_CAP_PTR(6'h3F),
      .EXT_CFG_XP_CAP_PTR(10'h3FF),
      .HEADER_TYPE(8'h00),
      .INFER_EI(5'h00),
      .INTERRUPT_PIN(8'h00),
      .INTERRUPT_STAT_AUTO("TRUE"),
      .IS_SWITCH("FALSE"),
      .LAST_CONFIG_DWORD(10'h3FF),
      .LINK_CAP_ASPM_OPTIONALITY("FALSE"),
      .LINK_CAP_ASPM_SUPPORT(1),
      .LINK_CAP_CLOCK_POWER_MANAGEMENT("FALSE"),
      .LINK_CAP_DLL_LINK_ACTIVE_REPORTING_CAP("FALSE"),
      .LINK_CAP_L0S_EXIT_LATENCY_COMCLK_GEN1(7),
      .LINK_CAP_L0S_EXIT_LATENCY_COMCLK_GEN2(7),
      .LINK_CAP_L0S_EXIT_LATENCY_GEN1(7),
      .LINK_CAP_L0S_EXIT_LATENCY_GEN2(7),
      .LINK_CAP_L1_EXIT_LATENCY_COMCLK_GEN1(7),
      .LINK_CAP_L1_EXIT_LATENCY_COMCLK_GEN2(7),
      .LINK_CAP_L1_EXIT_LATENCY_GEN1(7),
      .LINK_CAP_L1_EXIT_LATENCY_GEN2(7),
      .LINK_CAP_LINK_BANDWIDTH_NOTIFICATION_CAP("FALSE"),
      .LINK_CAP_MAX_LINK_SPEED(4'h2),
      .LINK_CAP_MAX_LINK_WIDTH(6'h04),
      .LINK_CAP_RSVD_23(0),
      .LINK_CAP_SURPRISE_DOWN_ERROR_CAPABLE("FALSE"),
      .LINK_CONTROL_RCB(0),
      .LINK_CTRL2_DEEMPHASIS("FALSE"),
      .LINK_CTRL2_HW_AUTONOMOUS_SPEED_DISABLE("FALSE"),
      .LINK_CTRL2_TARGET_LINK_SPEED(4'h2),
      .LINK_STATUS_SLOT_CLOCK_CONFIG("TRUE"),
      .LL_ACK_TIMEOUT(15'h0000),
      .LL_ACK_TIMEOUT_EN("FALSE"),
      .LL_ACK_TIMEOUT_FUNC(0),
      .LL_REPLAY_TIMEOUT(15'h0000),
      .LL_REPLAY_TIMEOUT_EN("FALSE"),
      .LL_REPLAY_TIMEOUT_FUNC(1),
      .LTSSM_MAX_LINK_WIDTH(6'h04),
      .MPS_FORCE("FALSE"),
      .MSIX_BASE_PTR(8'h9C),
      .MSIX_CAP_ID(8'h11),
      .MSIX_CAP_NEXTPTR(8'h00),
      .MSIX_CAP_ON("FALSE"),
      .MSIX_CAP_PBA_BIR(0),
      .MSIX_CAP_PBA_OFFSET(29'h00000000),
      .MSIX_CAP_TABLE_BIR(0),
      .MSIX_CAP_TABLE_OFFSET(29'h00000000),
      .MSIX_CAP_TABLE_SIZE(11'h000),
      .MSI_BASE_PTR(8'h48),
      .MSI_CAP_64_BIT_ADDR_CAPABLE("FALSE"),
      .MSI_CAP_ID(8'h05),
      .MSI_CAP_MULTIMSGCAP(0),
      .MSI_CAP_MULTIMSG_EXTENSION(0),
      .MSI_CAP_NEXTPTR(8'h60),
      .MSI_CAP_ON("TRUE"),
      .MSI_CAP_PER_VECTOR_MASKING_CAPABLE("FALSE"),
      .N_FTS_COMCLK_GEN1(255),
      .N_FTS_COMCLK_GEN2(255),
      .N_FTS_GEN1(255),
      .N_FTS_GEN2(255),
      .PCIE_BASE_PTR(8'h60),
      .PCIE_CAP_CAPABILITY_ID(8'h10),
      .PCIE_CAP_CAPABILITY_VERSION(4'h2),
      .PCIE_CAP_DEVICE_PORT_TYPE(4'h0),
      .PCIE_CAP_NEXTPTR(8'h00),
      .PCIE_CAP_ON("TRUE"),
      .PCIE_CAP_RSVD_15_14(0),
      .PCIE_CAP_SLOT_IMPLEMENTED("FALSE"),
      .PCIE_REVISION(2),
      .PL_AUTO_CONFIG(0),
      .PL_FAST_TRAIN("TRUE"),
      .PM_ASPML0S_TIMEOUT(15'h0000),
      .PM_ASPML0S_TIMEOUT_EN("FALSE"),
      .PM_ASPML0S_TIMEOUT_FUNC(0),
      .PM_ASPM_FASTEXIT("FALSE"),
      .PM_BASE_PTR(8'h40),
      .PM_CAP_AUXCURRENT(0),
      .PM_CAP_D1SUPPORT("FALSE"),
      .PM_CAP_D2SUPPORT("FALSE"),
      .PM_CAP_DSI("FALSE"),
      .PM_CAP_ID(8'h01),
      .PM_CAP_NEXTPTR(8'h48),
      .PM_CAP_ON("TRUE"),
      .PM_CAP_PMESUPPORT(5'h0F),
      .PM_CAP_PME_CLOCK("FALSE"),
      .PM_CAP_RSVD_04(0),
      .PM_CAP_VERSION(3),
      .PM_CSR_B2B3("FALSE"),
      .PM_CSR_BPCCEN("FALSE"),
      .PM_CSR_NOSOFTRST("TRUE"),
      .PM_DATA0(8'h00),
      .PM_DATA1(8'h00),
      .PM_DATA2(8'h00),
      .PM_DATA3(8'h00),
      .PM_DATA4(8'h00),
      .PM_DATA5(8'h00),
      .PM_DATA6(8'h00),
      .PM_DATA7(8'h00),
      .PM_DATA_SCALE0(2'h0),
      .PM_DATA_SCALE1(2'h0),
      .PM_DATA_SCALE2(2'h0),
      .PM_DATA_SCALE3(2'h0),
      .PM_DATA_SCALE4(2'h0),
      .PM_DATA_SCALE5(2'h0),
      .PM_DATA_SCALE6(2'h0),
      .PM_DATA_SCALE7(2'h0),
      .PM_MF("FALSE"),
      .RBAR_BASE_PTR(12'h000),
      .RBAR_CAP_CONTROL_ENCODEDBAR0(5'h00),
      .RBAR_CAP_CONTROL_ENCODEDBAR1(5'h00),
      .RBAR_CAP_CONTROL_ENCODEDBAR2(5'h00),
      .RBAR_CAP_CONTROL_ENCODEDBAR3(5'h00),
      .RBAR_CAP_CONTROL_ENCODEDBAR4(5'h00),
      .RBAR_CAP_CONTROL_ENCODEDBAR5(5'h00),
      .RBAR_CAP_ID(16'h0015),
      .RBAR_CAP_INDEX0(3'h0),
      .RBAR_CAP_INDEX1(3'h0),
      .RBAR_CAP_INDEX2(3'h0),
      .RBAR_CAP_INDEX3(3'h0),
      .RBAR_CAP_INDEX4(3'h0),
      .RBAR_CAP_INDEX5(3'h0),
      .RBAR_CAP_NEXTPTR(12'h000),
      .RBAR_CAP_ON("FALSE"),
      .RBAR_CAP_SUP0(32'h00000001),
      .RBAR_CAP_SUP1(32'h00000001),
      .RBAR_CAP_SUP2(32'h00000001),
      .RBAR_CAP_SUP3(32'h00000001),
      .RBAR_CAP_SUP4(32'h00000001),
      .RBAR_CAP_SUP5(32'h00000001),
      .RBAR_CAP_VERSION(4'h1),
      .RBAR_NUM(3'h0),
      .RECRC_CHK(0),
      .RECRC_CHK_TRIM("FALSE"),
      .ROOT_CAP_CRS_SW_VISIBILITY("FALSE"),
      .RP_AUTO_SPD(2'h1),
      .RP_AUTO_SPD_LOOPCNT(5'h1F),
      .SELECT_DLL_IF("FALSE"),
      .SLOT_CAP_ATT_BUTTON_PRESENT("FALSE"),
      .SLOT_CAP_ATT_INDICATOR_PRESENT("FALSE"),
      .SLOT_CAP_ELEC_INTERLOCK_PRESENT("FALSE"),
      .SLOT_CAP_HOTPLUG_CAPABLE("FALSE"),
      .SLOT_CAP_HOTPLUG_SURPRISE("FALSE"),
      .SLOT_CAP_MRL_SENSOR_PRESENT("FALSE"),
      .SLOT_CAP_NO_CMD_COMPLETED_SUPPORT("FALSE"),
      .SLOT_CAP_PHYSICAL_SLOT_NUM(13'h0000),
      .SLOT_CAP_POWER_CONTROLLER_PRESENT("FALSE"),
      .SLOT_CAP_POWER_INDICATOR_PRESENT("FALSE"),
      .SLOT_CAP_SLOT_POWER_LIMIT_SCALE(0),
      .SLOT_CAP_SLOT_POWER_LIMIT_VALUE(8'h00),
      .SPARE_BIT0(0),
      .SPARE_BIT1(0),
      .SPARE_BIT2(0),
      .SPARE_BIT3(0),
      .SPARE_BIT4(0),
      .SPARE_BIT5(0),
      .SPARE_BIT6(0),
      .SPARE_BIT7(0),
      .SPARE_BIT8(0),
      .SPARE_BYTE0(8'h00),
      .SPARE_BYTE1(8'h00),
      .SPARE_BYTE2(8'h00),
      .SPARE_BYTE3(8'h00),
      .SPARE_WORD0(32'h00000000),
      .SPARE_WORD1(32'h00000000),
      .SPARE_WORD2(32'h00000000),
      .SPARE_WORD3(32'h00000000),
      .SSL_MESSAGE_AUTO("FALSE"),
      .TECRC_EP_INV("FALSE"),
      .TL_RBYPASS("FALSE"),
      .TL_RX_RAM_RADDR_LATENCY(0),
      .TL_RX_RAM_RDATA_LATENCY(2),
      .TL_RX_RAM_WRITE_LATENCY(0),
      .TL_TFC_DISABLE("FALSE"),
      .TL_TX_CHECKS_DISABLE("FALSE"),
      .TL_TX_RAM_RADDR_LATENCY(0),
      .TL_TX_RAM_RDATA_LATENCY(2),
      .TL_TX_RAM_WRITE_LATENCY(0),
      .TRN_DW("TRUE"),
      .TRN_NP_FC("TRUE"),
      .UPCONFIG_CAPABLE("TRUE"),
      .UPSTREAM_FACING("TRUE"),
      .UR_ATOMIC("FALSE"),
      .UR_CFG1("TRUE"),
      .UR_INV_REQ("TRUE"),
      .UR_PRS_RESPONSE("TRUE"),
      .USER_CLK2_DIV2("TRUE"),
      .USER_CLK_FREQ(3),
      .USE_RID_PINS("FALSE"),
      .VC0_CPL_INFINITE("TRUE"),
      .VC0_RX_RAM_LIMIT(13'h07FF),
      .VC0_TOTAL_CREDITS_CD(850),
      .VC0_TOTAL_CREDITS_CH(72),
      .VC0_TOTAL_CREDITS_NPD(8),
      .VC0_TOTAL_CREDITS_NPH(4),
      .VC0_TOTAL_CREDITS_PD(64),
      .VC0_TOTAL_CREDITS_PH(4),
      .VC0_TX_LASTPACKET(29),
      .VC_BASE_PTR(12'h000),
      .VC_CAP_ID(16'h0002),
      .VC_CAP_NEXTPTR(12'h000),
      .VC_CAP_ON("FALSE"),
      .VC_CAP_REJECT_SNOOP_TRANSACTIONS("FALSE"),
      .VC_CAP_VERSION(4'h1),
      .VSEC_BASE_PTR(12'h000),
      .VSEC_CAP_HDR_ID(16'h1234),
      .VSEC_CAP_HDR_LENGTH(12'h018),
      .VSEC_CAP_HDR_REVISION(4'h1),
      .VSEC_CAP_ID(16'h000B),
      .VSEC_CAP_IS_LINK_VISIBLE("TRUE"),
      .VSEC_CAP_NEXTPTR(12'h000),
      .VSEC_CAP_ON("FALSE"),
      .VSEC_CAP_VERSION(4'h1)
  ) PCIE_INST (
      .DLRSTN(1'b1),
      .DRPADDR(8'b10101010),
      .DRPCLK(DRPCLK),
      .DRPDI(PCIE_DRPDI),
      .DRPDO(PCIE_DRPDO),
      .DRPEN(DRPEN),
      .DRPRDY(PCIE_DRPRDY),
      .DRPWE(DRPWE),
      .FUNCLVLRSTN(1'b1),
      .LL2SENDASREQL1(1'b0),
      .LL2SENDENTERL1(1'b0),
      .LL2SENDENTERL23(1'b0),
      .LL2SENDPMACK(1'b0),
      .LL2SUSPENDNOW(1'b0),
      .LL2TLPRCV(1'b0),
      .PIPECLK(pcie_pipe_clk),
      .PLRSTN(1'b1),
      .SYSRSTN(pcie_rst_n),
      .TL2ASPMSUSPENDCREDITCHECK(1'b0),
      .TL2PPMSUSPENDREQ(1'b0),
      .TLRSTN(1'b1),
      .TRNRFCPRET(1'b1),
      .TRNTDLLPSRCRDY(1'b0),
      .USERCLK(pcie_pipe_clk),
      .USERCLK2(pcie_pipe_clk),
  );

endmodule

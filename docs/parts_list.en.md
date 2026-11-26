[日本語](parts_list.md) | English

# PHOTON GLASS parts list

This is a list of all the parts used on the main board (OG19AWv2) and the camera board (OG19_PC-3). For each part, it summarises the following.

- Whether it is the same as the original part
- Datasheets
- Whether the pins of the schematic symbol (pin name → pad) match the pinout in the datasheet

Stock for every part number has been checked in the JLCPCB parts library (as of 2026-10-15). However, the hand-soldered VR1, SW_MAIN and SW_SUB / UP / DOWN have been changed to parts bought from Akizuki Denshi and aitendo, to match the order list (2026-10-20 version) (they are not covered by the JLCPCB stock check).

- JLCPCB assembly: **13** rows (main) / **6** rows (camera)
- Hand-soldered: **7** parts (main board)
- Schematic symbol mismatches: **0**

## Main board OG19AWv2

Rows whose "Assembly" column says "Hand-soldered" are not included in the BOM / CPL

| Ref | Original part | Part used | Assembly | Schematic symbol check | Documents |
|---|---|---|---|---|---|
| PCM5102A<br>Audio DAC | TI PCM5102A (TSSOP-20)<br>Same | `PCM5102APWR`<br>Texas Instruments · `C107671` · Stock 5,831 | JLCPCB assembly | Match<br>All 20 pins, from 1 CPVDD to 20 DVDD, match the TI datasheet and the JLCPCB symbol | [Datasheet](https://www.lcsc.com/datasheet/lcsc_datasheet_2409291903_Texas-Instruments-PCM5102APWR_C107671.pdf) [LCSC](https://www.lcsc.com/product-detail/adcs-dacs-special-purpose_texas-instruments-pcm5102apwr_C107671.html) [TI](https://www.ti.com/lit/ds/symlink/pcm5102a.pdf) |
| PAM8304<br>Speaker amplifier | Diodes PAM8304 (MSOP-8)<br>Same | `PAM8304ASR`<br>Diodes Incorporated · `C581342` · Stock 2,684 | JLCPCB assembly | Match<br>1 OUT+ / 2 PVDD / 3 VDD / 4 IN− / 5 IN+ / 6 SD / 7 GND / 8 OUT− match | [Datasheet](https://www.lcsc.com/datasheet/lcsc_datasheet_2006092117_Diodes-Incorporated-PAM8304ASR_C581342.pdf) [LCSC](https://www.lcsc.com/product-detail/audio-amplifiers_diodes-incorporated-pam8304asr_C581342.html) [Diodes](https://www.diodes.com/assets/Datasheets/PAM8304.pdf) |
| CN1<br>3.5mm headphone jack | Switchcraft 35RASMT4BHNTRX (out of stock)<br>Substitute | `SJ-43516-SMT-TR`<br>CUI · `C4992780` · Stock 136 | JLCPCB assembly | Match, with caveats<br>A 4-pole (TRRS) part. Ring2 is connected to the sleeve (AGND), so with a stereo plug it works the same as the original. Note 1 | [Datasheet](https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2401261118_CUI-SJ-43516-SMT-TR_C4992780.pdf) [LCSC](https://www.lcsc.com/product-detail/audio-connectors-headphones_cui-sj-43516-smt-tr_C4992780.html) [Original: Switchcraft](https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2401261118_Switchcraft-35RASMT4BHNTRX_C4992744.pdf) |
| CN2<br>Camera FFC, 22-pin | Hirose FH12-22S-0.5SH<br>Same | `FH12-22S-0.5SH(55)`<br>HRS(Hirose) · `C597981` · Stock 684 | JLCPCB assembly | Match<br>Both the part and the symbol are unchanged from the original design. The order of pads 1–22 matches the JLCPCB part data | [Datasheet](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_HRS-Hirose-FH12-22S-0-5SH-55_C597981.pdf) [LCSC](https://www.lcsc.com/product-detail/ffc-fpc-flat-flexible-connector-assemblies_hrs-hirose-fh12-22s-0-5sh-55_C597981.html) |
| CN3<br>HDMI Type-A | Amphenol 10029449 series<br>Same series | `10029449-111RLF`<br>Amphenol ICC · `C427307` · Stock 1,556 | JLCPCB assembly | Match<br>Pins 1–19 match the HDMI standard assignment (18 +5V, 19 HPD). The four shell legs are GND | [Datasheet](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Amphenol-ICC-10029449-111RLF_C427307.pdf) [LCSC](https://www.lcsc.com/product-detail/hdmi-connectors_amphenol-icc-10029449-111rlf_C427307.html) |
| U\$1<br>Raspberry Pi 40-pin connection (mounted on the top side) | Samtec SSW-120-02-G-D (5 in stock, about \$10)<br>Substitute | `2.54-2*20P`<br>BOOMELE(Boom Precision Elec) · `C5124634` · Stock 8,734 | JLCPCB assembly | Match<br>A generic socket of the same shape (8.5mm high). 1 3.3V / 2 5V … 40 GPIO21 match the standard pinout. In Eagle it is placed reversed, as a mirror image of the pinout for stacking the Pi upside down; the real part is mounted on the top side (Top in the CPL as well) | [Datasheet](https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2401111126_BOOMELE-Boom-Precision-Elec-2-54-2-20P_C5124634.pdf) [LCSC](https://www.lcsc.com/product-detail/female-headers_boomele-boom-precision-elec-2-54-2-20p_C5124634.html) [Original: Samtec](https://www.samtec.com/products/ssw) |
| U\$3<br>Status RGB LED | Kingbright KPF-3236SURKMGKPBC (not listed at JLC)<br>Substitute | `S6-3528RGBTA`<br>TUOZHAN · `C2843672` · Stock 7,379 | JLCPCB assembly | Match, with caveats<br>The pinout follows the datasheet. The order of the colours changes, so the software needs to be changed. Note 3 | [Datasheet](https://www.lcsc.com/datasheet/lcsc_datasheet_2109061230_TUOZHAN-S6-3528RGBTA_C2843672.pdf) [LCSC](https://www.lcsc.com/product-detail/rgb-leds_tuozhan-s6-3528rgbta_C2843672.html) |
| VR1<br>Volume control (dual-gang) | ALPS RK10J (no specific part number)<br>Substitute | `R1001G16T2B-B10K`<br>aitendo (part on the order list) | Hand-soldered | Match, with caveats<br>Electrically equivalent to RK10J12E002L: dual-gang, 10kΩ, B taper, 270° rotation. Only the dial diameter and thickness differ. Note 2 | [aitendo](https://www.aitendo.com/product/20676) |
| SW_SUB, SW_UP, SW_DOWN<br>Side-push switches | ALPS SKHH side-push (no specific part number)<br>Same series | `SKHHLPA010`<br>Akizuki Denshi · `107193` (part on the order list) | Hand-soldered | Match, with caveats<br>A different variant from SKHHLQA010, with a different stem length and operating force. This is the part actually fitted. Note 4 | [Akizuki Denshi](https://akizukidenshi.com/catalog/g/g107193/) |
| SW_MAIN<br>Main switch (bottom side) | Akizuki P-03647 = Cosland DTS-63-N-V (6.2mm square, 7mm high)<br>Same series | `P-03646`<br>Cosland TS-0606-F-N-RED · Akizuki Denshi (part on the order list) | Hand-soldered | Match<br>A part that Akizuki sells as part of the DTS-63 series. Compatible with DTS-63K-V in both footprint and overall height | [Akizuki Denshi](https://akizukidenshi.com/catalog/g/g103646/) [Original: Akizuki](https://akizukidenshi.com/goodsaffix/ts-0606_20200714.pdf) |
| SPK, 5V<br>2-pin connectors (vertical) | JST S2B-XH-A (horizontal)<br>Substitute | `B2B-XH-A(LF)(SN)`<br>JST · `C158012` · Stock 241,489 | Hand-soldered | Match<br>Changed to the vertical type (plugged in from above). Same pads. Pin 1 = square pad (5V / SPK+). Placed 0.5mm lower so that the connector body stays within the board | [Datasheet](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_JST-B2B-XH-A-LF-SN_C158012.pdf) [LCSC](https://lcsc.com/product-detail/wire-to-board-connector_jst-b2b-xh-a-lf-sn_C158012.html) |
| C2–C4, C7–C11<br>Decoupling capacitors 0.1µF | 0603 0.1µF<br>Same | `CC0603KRX7R9BB104`<br>YAGEO · `C14663` · Stock 51,101,481 | JLCPCB assembly | Match<br>Same value and size (50V X7R) | [Datasheet](https://www.lcsc.com/datasheet/lcsc_datasheet_2211101700_YAGEO-CC0603KRX7R9BB104_C14663.pdf) [LCSC](https://www.lcsc.com/product-detail/multilayer-ceramic-capacitors-mlcc-smd-smt_yageo-cc0603krx7r9bb104_C14663.html) |
| C1<br>2.2µF | 0603 2.2µF<br>Same | `CL10A225KO8NNNC`<br>Samsung Electro-Mechanics · `C23630` · Stock 3,546,419 | JLCPCB assembly | Match<br>Same value and size (16V X5R) | [Datasheet](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Samsung-Electro-Mechanics-CL10A225KO8NNNC_C23630.pdf) [LCSC](https://www.lcsc.com/product-detail/multilayer-ceramic-capacitors-mlcc-smd-smt_samsung-electro-mechanics-cl10a225ko8nnnc_C23630.html) |
| C5, C6<br>DAC output filter 2200pF | 0603 2200pF<br>Same | `0603B222K500NT`<br>FH (Guangdong Fenghua Advanced Tech) · `C1604` · Stock 991,140 | JLCPCB assembly | Match<br>Same value and size (X7R). If sound quality is the priority, the C0G part C33353 can also be used | [Datasheet](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_FH--Guangdong-Fenghua-Advanced-Tech-0603B222K500NT_C1604.pdf) [LCSC](https://www.lcsc.com/product-detail/multilayer-ceramic-capacitors-mlcc-smd-smt_fh-guangdong-fenghua-advanced-tech-0603b222k500nt_C1604.html) |
| R1–R4<br>470Ω | 0603 470Ω<br>Same | `0603WAF4700T5E`<br>UNI-ROYAL(Uniroyal Elec) · `C23179` · Stock 5,713,240 | JLCPCB assembly | Match | [Datasheet](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010116_UNI-ROYAL-Uniroyal-Elec-0603WAF4700T5E_C23179.pdf) [LCSC](https://www.lcsc.com/product-detail/chip-resistor-surface-mount_uni-royal-uniroyal-elec-0603waf4700t5e_C23179.html) |
| R5, R6<br>470kΩ | 0603 470kΩ<br>Same | `0603WAF4703T5E`<br>UNI-ROYAL(Uniroyal Elec) · `C23178` · Stock 1,321,083 | JLCPCB assembly | Match | [Datasheet](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010116_UNI-ROYAL-Uniroyal-Elec-0603WAF4703T5E_C23178.pdf) [LCSC](https://www.lcsc.com/product-detail/chip-resistor-surface-mount_uni-royal-uniroyal-elec-0603waf4703t5e_C23178.html) |
| R7–R9<br>LED current limiting | 0603 40Ω<br>Substitute | `0603WAF402JT5E`<br>UNI-ROYAL(Uniroyal Elec) · `C23047` · Stock 24,004 | JLCPCB assembly | Match<br>JLCPCB has no part of exactly 40Ω in stock, so 40.2Ω ±1% is used (a 0.5% difference, within the part tolerance) | [Datasheet](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010116_UNI-ROYAL-Uniroyal-Elec-0603WAF402JT5E_C23047.pdf) [LCSC](https://www.lcsc.com/product-detail/chip-resistor-surface-mount_uni-royal-uniroyal-elec-0603waf402jt5e_C23047.html) |

## Camera board OG19_PC-3

All parts are assembled by JLCPCB

| Ref | Original part | Part used | Assembly | Schematic symbol check | Documents |
|---|---|---|---|---|---|
| CN1<br>HDMI Type-A | Amphenol 10029449 series<br>Same series | `10029449-111RLF`<br>Amphenol ICC · `C427307` · Stock 1,556 | JLCPCB assembly | Match<br>Same as on the main board | [Datasheet](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_Amphenol-ICC-10029449-111RLF_C427307.pdf) [LCSC](https://www.lcsc.com/product-detail/hdmi-connectors_amphenol-icc-10029449-111rlf_C427307.html) |
| CN2<br>Camera FFC, 22-pin | Hirose FH12-22S-0.5SH<br>Same | `FH12-22S-0.5SH(55)`<br>HRS(Hirose) · `C597981` · Stock 684 | JLCPCB assembly | Match, with caveats<br>The pad numbers are in the reverse order of the real part's (as in the original design). Note 5 | [Datasheet](https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_HRS-Hirose-FH12-22S-0-5SH-55_C597981.pdf) [LCSC](https://www.lcsc.com/product-detail/ffc-fpc-flat-flexible-connector-assemblies_hrs-hirose-fh12-22s-0-5sh-55_C597981.html) |
| SW1<br>Tactile switch | ALPS SKRTLBE010<br>Same | `SKRTLBE010`<br>ALPSALPINE · `C127481` · Stock 2,106 | JLCPCB assembly | Match<br>Terminals ① and ③ (common) = GND, ② (switch side) = SW1 signal | [Datasheet](https://www.lcsc.com/datasheet/lcsc_datasheet_1809041613_ALPSALPINE-SKRTLBE010_C127481.pdf) [LCSC](https://www.lcsc.com/product-detail/tactile-switches_alpsalpine-skrtlbe010_C127481.html) |
| GND (part name)<br>Indicator LED | 0603 chip LED (no colour specified)<br>Substitute | `KT-0603R`<br>Hubei KENTO Elec · `C2286` · Stock 7,890,022 | JLCPCB assembly | Match<br>Red chosen. Symbol A → JLC pin 1 (anode), C → pin 2 (cathode) | [Datasheet](https://www.lcsc.com/datasheet/lcsc_datasheet_1810231112_Hubei-KENTO-Elec-KT-0603R_C2286.pdf) [LCSC](https://www.lcsc.com/product-detail/led-indication-discrete_hubei-kento-elec-kt-0603r_C2286.html) |
| R1, R2<br>10kΩ | 0603 10kΩ<br>Same | `0603WAF1002T5E`<br>UNI-ROYAL(Uniroyal Elec) · `C25804` · Stock 32,676,170 | JLCPCB assembly | Match | [Datasheet](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010045_UNI-ROYAL-Uniroyal-Elec-0603WAF1002T5E_C25804.pdf) [LCSC](https://www.lcsc.com/product-detail/chip-resistor-surface-mount_uni-royal-uniroyal-elec-0603waf1002t5e_C25804.html) |
| R3<br>1kΩ | 0603 1kΩ<br>Same | `0603WAF1001T5E`<br>UNI-ROYAL(Uniroyal Elec) · `C21190` · Stock 24,612,269 | JLCPCB assembly | Match | [Datasheet](https://www.lcsc.com/datasheet/lcsc_datasheet_2206010130_UNI-ROYAL-Uniroyal-Elec-0603WAF1001T5E_C21190.pdf) [LCSC](https://www.lcsc.com/product-detail/chip-resistor-surface-mount_uni-royal-uniroyal-elec-0603waf1001t5e_C21190.html) |

## Parts to hand-solder (bought separately)

These seven parts have been left out of the JLCPCB BOM and CPL, so the board comes with only their pads and holes. Buy the same part numbers, for example from the suppliers below.

- `R1001G16T2B-B10K` × 1<br>VR1 — volume control (dual-gang) · [aitendo](https://www.aitendo.com/product/20676)
- `SKHHLPA010` × 3<br>SW_SUB, SW_UP, SW_DOWN — side-push switches · [Akizuki Denshi 107193](https://akizukidenshi.com/catalog/g/g107193/)
- `P-03646` × 1<br>SW_MAIN — main switch (bottom side), Cosland TS-0606-F-N-RED · [Akizuki Denshi 103646](https://akizukidenshi.com/catalog/g/g103646/)
- `B2B-XH-A(LF)(SN)` × 2<br>SPK, 5V — 2-pin connectors (vertical) · [C158012](https://lcsc.com/product-detail/wire-to-board-connector_jst-b2b-xh-a-lf-sn_C158012.html)

## Notes

1. **CN1 headphone jack**: The schematic symbol (5 pins) is unchanged from the original; only the assignment to the terminals of the real part has changed.

   | Schematic pin | Connected circuit | Original Switchcraft | New CUI SJ-43516 | Behaviour |
   |---|---|---|---|---|
   | `P$3` | Left channel (via VR1-A) | 3 Tip | #2 Tip | Touches the tip of the plug |
   | `P$2` | Right channel (via VR1-B) | 2 Ring | #3 Ring1 | Touches the ring of the plug |
   | `P$1` | AGND | 1 Sleeve | #1 Sleeve + #4 Ring2 | The sleeve of a stereo plug touches both |
   | `P$5` | To the speaker amplifier (R4) | 5 Tip SW (normally closed) | #5 Tip SW (normally closed) | Connected to Tip with no plug inserted; opens when a plug is inserted |
   | `P$4` | To the speaker amplifier (R3) | 4 Ring SW (normally closed) | #6 Ring SW (normally closed) | Connected to Ring with no plug inserted; opens when a plug is inserted |

   The original is for 3-pole (TRS) plugs; the substitute is for 4-pole (TRRS) plugs.

   - Mapping: the original pins (P\$1 sleeve / P\$2 ring / P\$3 tip / P\$4 ring SW / P\$5 tip SW) are assigned to `#1 / #3 / #2 / #6 / #5` of the substitute, respectively.
   - Ring2 (#4) is connected to AGND, the same as the sleeve, so an ordinary stereo plug can be used just as with the original.
   - The tip SW and ring SW are both of the "normally closed" type, which opens when a plug is inserted, and behave the same as the original.

2. **VR1 volume control**:

   - The order list uses `R1001G16T2B-B10K` (aitendo). It is electrically equivalent to `RK10J12E002L`, the part chosen at first (dual-gang, 10kΩ, B taper, 270° rotation); only the dial diameter and thickness differ. The next two points are the results of checking `RK10J12E002L`.
   - The order of the terminals matches. In the datasheet, the order from the left is "1 common / ② R1 wiper / 2 R2 wiper / 3 R2 end / ③ R1 end", which corresponds to `1AB / 2B / 2A / 3A / 3B` in Eagle.
   - The resistance taper is "3B" (B = linear). Volume controls generally use an A taper (logarithmic). If the original part had an A taper, the way the volume changes will be different.

3. **U\$3 RGB LED**: Because the order of the colours differs from the original, the colour assignments in the schematic have been swapped. The assignments on the 40-pin header are as follows, and the software needs to be changed accordingly.

   - Pin 19 (GPIO10) → **blue**
   - Pin 21 (GPIO9) → **red**
   - Pin 23 (GPIO11) → **green**

4. **SW_SUB / UP / DOWN**: Because the original part number is unknown, SKHHLQA010, with a button length of 8.35mm, was chosen at first. The order list uses SKHHLPA010 (a different variant from SKHHLQA010, with a different stem length and operating force). The footprint is shared, so you may change to SKHHLMA010 (3.85mm) or SKHHLUA010 (5.85mm) when hand-soldering.

5. **Camera board CN2**: The Eagle pad numbers are in the reverse order of the real part's pin numbers (pin 22 of the real part sits at pad "1"). This comes from the original design (the "reverse" in the file name) and has not been changed this time. The part sits according to the shape of the pads, so it is mounted the same way as on the original board.

6. The datasheet for the **original Kingbright RGB LED** is not listed, because no URL for it could be found on the official site.

Sources: manufacturers' datasheets, LCSC / JLCPCB part data (EasyEDA footprints and symbols). Eagle data checked: `2019-06-27_OG19AWv2_JLC`, `2019-05-28_OG19_PC-3_reverse_JLC`.

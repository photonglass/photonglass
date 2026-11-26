[日本語](JLCPCB_ORDERING.md) | English

# Ordering from JLCPCB

This guide explains how to order the two boards from [JLCPCB](https://jlcpcb.com/), all the way to "PCB fabrication + parts assembly (PCBA)".
The names of the items on the screens are as of 2026. They may have changed; if so, choose the closest item.

## Files to use
| Board | Gerbers (PCB fabrication) | BOM (bill of materials) | CPL (component placement) |
|---|---|---|---|
| Main board | [`main-board/gerber/OG19AWv2_main_gerber.zip`](main-board/gerber/OG19AWv2_main_gerber.zip) | [`main-board/jlcpcb-assembly/BOM.csv`](main-board/jlcpcb-assembly/BOM.csv) | [`main-board/jlcpcb-assembly/CPL.csv`](main-board/jlcpcb-assembly/CPL.csv) |
| Camera board | [`camera-board/gerber/OG19_PC-3_camera_gerber.zip`](camera-board/gerber/OG19_PC-3_camera_gerber.zip) | [`camera-board/jlcpcb-assembly/BOM.csv`](camera-board/jlcpcb-assembly/BOM.csv) | [`camera-board/jlcpcb-assembly/CPL.csv`](camera-board/jlcpcb-assembly/CPL.csv) |

- Upload the Gerber zip **as it is, without extracting it**. It contains 11 files: copper, solder mask, silkscreen and paste stencil (top and bottom), outline, and drill data (plated/non-plated).
- The "Stock" column in the BOM shows the stock when it was made (2026-10-14). Check the stock on screen when you order.

Add each board as a separate order (in the same cart).

## 1. PCB fabrication settings
1. Log in to jlcpcb.com and open "Order now" (or "Instant Quote") on the top page.
2. Upload the Gerber zip with "Add gerber file". The board size and number of layers are read automatically.
   - It is OK if it shows 79 × 42 mm for the main board and 39.3 × 17.2 mm for the camera board.
3. Use the settings below. Items not listed can be left at their defaults.

| Item | Setting |
|---|---|
| Base Material | FR-4 |
| Layers | 2 |
| PCB Qty | 5 (the minimum) |
| PCB Thickness | 1.6 mm |
| PCB Color | Any colour you like (colours other than green may take a little longer) |
| Surface Finish | HASL (with lead) or LeadFree HASL. ENIG makes soldering of the HDMI and camera connectors more reliable, but costs more |
| Mark on PCB (formerly "Remove Order Number") | Whether to put marks such as the order number or a serial number (2D barcode) on the board. If you do not want them, choose "Remove Mark". The options and charges change from time to time, so check the explanation on screen |

The minimum trace width and spacing are 0.1524 mm (6 mil) and the minimum hole size is 0.305 mm, which are within the standard specifications.

## 2. PCB assembly settings
1. Turn on "PCB Assembly" at the bottom of the same screen.
2. Use the settings below.

| Item | Main board | Camera board |
|---|---|---|
| PCBA Type | Economic (Standard is also fine) | Economic |
| Assembly Side | **Top Side** | **Top Side** |
| PCBA Qty | 2–5 (as many as you need) | 2–5 |
| Tooling holes | Added by JLCPCB | Added by JLCPCB |

3. Click "NEXT" and check the board images, then click "NEXT" again.
4. Upload the **BOM** and the **CPL**, and click "Process BOM & CPL".

## 3. Checking the parts (BOM screen)
Every part has a JLCPCB part number (LCSC number), so the parts are matched automatically. Check that every row has a "✓".

| What to check | Details |
|---|---|
| Out-of-stock parts (shown in red) | Search for another part with the same value and the same footprint and substitute it. For resistors and capacitors, anything with the same value and size (0603) will do |
| U$1 on the main board (40-pin socket) | A through-hole part. **Having it assembled adds a THT (manual assembly) charge.** To keep the cost down, untick its row and solder it yourself when the boards arrive (buy the socket separately; the order list uses FH-2x20SG from Akizuki Denshi, 100085) |
| "Extended" parts | Each type incurs an extra charge (a setup fee for the part). None of these parts has an alternative, so leave them as they are |

### Parts not to be assembled (hand-soldered)
The following parts of the main board affect the feel of the controls and the outer shape, so they have been left out of the BOM. Buy them separately and solder them yourself to the boards when they arrive.

| Part | Part number | Where to buy |
|---|---|---|
| VR1 volume control | R1001G16T2B-B10K | aitendo |
| SW_SUB / SW_UP / SW_DOWN | ALPS SKHHLPA010 | Akizuki Denshi (107193) |
| SW_MAIN | P-03646 (Cosland TS-0606-F-N-RED) | Akizuki Denshi |
| SPK / 5V connectors (vertical) | JST B2B-XH-A(LF)(SN) | Akizuki Denshi (112247) |

The part numbers and where to buy them follow the order list (2026-10-20 version). LCSC also stocks the same JST B2B-XH-A(LF)(SN) (C158012), and it can be bought "parts only" together with the JLCPCB order (JLCPCB's Parts → Order Parts, or LCSC.com).

If you did not have U$1 (the 40-pin socket) assembled, also buy the FH-2x20SG female pin socket (2×20, 40 pins; Akizuki Denshi, 100085) and fit it in the same way ("3. Checking the parts (BOM screen)" above).

## 4. Checking part orientation (preview screen)
Clicking "NEXT" shows a preview with the parts placed on the board. **This is the most important step.** If the orientation or position of a part is wrong, click the part and rotate or move it to correct it.

For ICs, check that the pin 1 mark (a dot or notch) lines up with the pin 1 mark on the board's silkscreen.

| Board | Part | What to check |
|---|---|---|
| Main | PCM5102A (TSSOP-20) | Position of pin 1 |
| Main | PAM8304 (MSOP-8) | Position of pin 1 |
| Main | U$3 RGB LED | Position of pin 1 (the cut corner). Whether all six leads sit on the pads |
| Main | CN1 headphone jack | Whether the socket faces outward from the board (the right edge) |
| Main | CN3 HDMI | Whether the opening faces outward from the board |
| Main | CN2 camera connector | Whether the outline of the part lines up with the silkscreen frame |
| Main | U$1 40-pin socket | Only if you had it assembled. Whether it is on the top side (Top) |
| Camera | CN1 HDMI | Whether the opening faces the edge of the board |
| Camera | CN2 camera connector | Whether the opening faces the edge on the camera side |
| Camera | SW1 tactile switch | Whether the part you press faces the edge of the board (the shutter side) |

If you are unsure about a part, you can also ask on this screen for a JLCPCB engineer to check it after you order. If they find an orientation problem after the order, JLCPCB will contact you by email to confirm.

## 5. Placing the order
1. Click "NEXT", check the quote, and click "SAVE TO CART".
2. Add the other board to the cart in the same way.
3. In the cart, choose a shipping method and pay. Delivery usually takes about 1–3 weeks.

## When the boards arrive
1. Fit the hand-soldered parts (the table above, plus FH-2x20SG if you did not have U$1 assembled).
2. Mount the main board on the Raspberry Pi Zero 2 W and check that it works with [`software/test/hw_test.py`](../software/test/hw_test.py) (for preparing the Raspberry Pi, see [`docs/SETUP_RASPBERRY_PI.en.md`](../docs/SETUP_RASPBERRY_PI.en.md); for the overall flow, see [`docs/BUILD_GUIDE.en.md`](../docs/BUILD_GUIDE.en.md)).
3. For the orientation of the speaker connector, see [`main-board/images/speaker_connector_orientation.png`](main-board/images/speaker_connector_orientation.png).

## About the Gerbers
The Gerbers were made from the Eagle data (`eagle/*.brd`) with the script [`tools/gerbgen.py`](tools/gerbgen.py). The GND pours were calculated according to the Eagle settings, and 0 clearance violations between nets and 0 unconnected items have been confirmed.
If you modify the Eagle data, you can regenerate them with the same script (requires Python 3 and `pip install shapely Hershey-Fonts`).
```bash
python hardware/tools/gerbgen.py hardware/main-board/eagle/OG19AWv2_main.brd out/main/files OG19AWv2_main
python hardware/tools/gerbgen.py hardware/camera-board/eagle/OG19_PC-3_camera.brd out/camera/files OG19_PC-3_camera
```
This produces zips such as `out/main/OG19AWv2_main_gerber.zip`.
You can also make them with KiCad (`kicad/`) or the CAM output of Fusion / Eagle, but the extent of the GND pours (the clearance from the board edge and holes) and the shape of the silkscreen text will differ slightly from those made by this script. In that case, check the contents in JLCPCB's Gerber viewer before ordering.

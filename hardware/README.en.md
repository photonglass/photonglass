[日本語](README.md) | English

# Boards

| Board | Role | Size |
|---|---|---|
| [`main-board/`](main-board) OG19AWv2 | Plugs into the 40-pin header of the Raspberry Pi Zero 2 W. Audio output (PCM5102A + PAM8304), speaker connector, four buttons, RGB LED, headphone jack, power connector (5V), HDMI to the camera board | 79 × 42 mm, 2 layers |
| [`camera-board/`](camera-board) OG19 PC-3 | The board inside the camera unit. Connects the camera (Adafruit 3508 Zero Spy Camera, standard-lens version; see ["Required parts" in `enclosure/camera-unit`](../enclosure/camera-unit/README.en.md#required-parts)) and carries the camera button (shutter) and an LED. Connects to the main board with an HDMI cable | 39.3 × 17.2 mm, 2 layers |

## Opening the files
| Software | File to open | How |
|---|---|---|
| **KiCad 9 or later** | `kicad/*.kicad_pro` | Double-click to open it. If you open and save it in KiCad 10, the files are converted to the new format and can no longer be opened in KiCad 9 |
| **Fusion** (formerly Eagle) | `eagle/*.sch` / `*.brd` | In Fusion, choose the `.sch` file with "File → Open"; the schematic and board open together as an electronics design |
| Eagle 9.x | `eagle/*.sch` / `*.brd` | Open them as they are (sales and support of Eagle ended in June 2026, so for new work use KiCad or Fusion) |

Of the Eagle and KiCad component libraries, jst-xh (the `5V` and `SPK` connectors on the main board) comes from yuhki50's [eagle-pcb-library](https://github.com/yuhki50/eagle-pcb-library) (MIT License).

## Making the boards at JLCPCB
Each board's folder contains all the files needed to order it (Gerbers, BOM and CPL).
For how to order, see **[`JLCPCB_ORDERING.en.md`](JLCPCB_ORDERING.en.md)** (PCB fabrication settings, assembly settings, checking part orientation, and the parts to solder by hand).

For the orientation of the speaker connector, see [`main-board/images/speaker_connector_orientation.png`](main-board/images/speaker_connector_orientation.png).

## Changes from the original design (OTON GLASS ver5)
- Parts that were out of stock were replaced with parts that can be bought from JLCPCB (headphone jack, RGB LED, pin socket, nearest resistor values, etc.). For details, see [`docs/parts_list.en.md`](../docs/parts_list.en.md).
- Main board: removed the step in the top edge, made the left and right corners symmetrical chamfers, aligned the fronts of the HDMI connector and the headphone jack, brought the buttons out to the edge of the board, added vias that were missing, etc.
- **The mapping between RGB LED colours and GPIOs has changed**: GPIO9 = red, GPIO11 = green, GPIO10 = blue.

## Revision history
| Revision (as printed on the silkscreen) | Changes |
|---|---|
| Main board `2026 / PB-4`, camera board `2026 / PC-4` | Changed the name on the silkscreen to "PHOTON GLASS" (the previous revision had "OTONGLASS" on the main board and "OTON GLASS" on the camera board). Added the repository URL (`github.com/photonglass/photonglass`) and the licence (`CERN-OHL-S v2`) to the top side of the main board (on 2026-11-25, this text and "PHOTON GLASS / 2026 / PB-4" were enlarged to a height of 1.0 mm and a stroke width of 0.16 mm; JLCPCB's minimum is 1.0 mm high and 0.153 mm stroke width). **The copper, holes, solder mask, stencil and outline are the same as the previous revision**; only the top silkscreen (`.GTO`) has changed. Removed the LCSC numbers of the old parts for the hand-soldered components (VR1, SW_MAIN, SW_SUB/UP/DOWN) that remained in the design data, and replaced them with the part numbers (`MPN`) and suppliers (`SUPPLIER`) of the parts actually used |
| Main board `2019 / PB-3`, camera board `2019 / PC-3` | The first revision, which adapted the original design for JLCPCB ("Changes from the original design" above) |

The camera board is small and also has rows of GND vias on its back, leaving no room for the URL, so the URL and licence are on the main board only.

## Testing after assembly
Running [`software/test/hw_test.py`](../software/test/hw_test.py) on the Raspberry Pi checks the LED → buttons → speaker → camera, in that order.
How to prepare the Raspberry Pi and run the test is described in [`docs/SETUP_RASPBERRY_PI.en.md`](../docs/SETUP_RASPBERRY_PI.en.md).

[日本語](README.md) | English

# KiCad 9 project (main board)

Double-click `OG19AWv2_main.kicad_pro` to open the schematic and the board.
It was made by importing the Eagle data in `../eagle/` into KiCad 9.0.
It can also be opened in KiCad 10 or later, but saving it converts the files to the new format, and they can then no longer be opened in KiCad 9.

## Comparison with the Eagle version (2026-11-12)
| Item | Result |
|---|---|
| Connections (50 nets, all pads) | Match across all three: the Eagle version, the schematic and the board |
| Traces / vias / outline | 632 / 125 / 79 × 42 mm, the same as the Eagle version |
| Copper pours | AGND and DGND on both sides (4 in total), filled |
| DRC (clearance, unrouted) | 0 errors |

### Fixes made after importing
- Aligned the net names on the board with those in the schematic (Eagle names such as `N$1` were changed to KiCad-style names).
- Changed the default clearance from 0.2 to **0.15 mm** (to match the original design's minimum spacing of 6 mil = 0.1524 mm).
- Fixed the mapping between the schematic symbols and the board footprints (`R0603` → `R0603_334`, `C0603` → `C0603_334`).
- Aligned the "Value" of the board footprints with the schematic (three buttons and two connectors).

### Differences in reference designators
Because KiCad requires reference designators to be "letters + number", a `0` has been added to some of them. The JLCPCB BOM/CPL and the documentation keep the names used in the Eagle version.
| Eagle / BOM and CPL | KiCad |
|---|---|
| PCM5102A | PCM5102A0 |
| SW_MAIN / SW_SUB / SW_UP / SW_DOWN | SW_MAIN0 / SW_SUB0 / SW_UP0 / SW_DOWN0 |
| SPK | SPK0 |
| 5V | UNK5V0 |

### Remaining warnings (not a problem)
- Unused pins are unconnected: the unused GPIOs and GNDs of the Raspberry Pi's 40-pin header, and pins 11, 17 and 19 of the HDMI connector (CN3). As in the original design.
- `UNK_HOLE_0/1`: mounting holes (non-plated). Reported as "extra footprints" because they have no symbol in the schematic.
- Only one thermal spoke on the top side for pin 25 (AGND) of the 40-pin header: not a problem, because it is connected to the bottom side by a trace.
- A short 0.9 mm stub of trace near VR1: it was in the original design.
- Overlapping silkscreen and text size: inherited as they were from the Eagle silkscreen settings (JLCPCB adjusts these automatically).

## DRC results (2026-11-25, when the silkscreen text was enlarged)
Run in KiCad 9.0.8 with all severities (errors and warnings) and the check against the schematic enabled.
| Item | Result |
|---|---|
| Errors | 1 (the "thermal of pin 25 on the 40-pin header" above; it was there before) |
| Warnings | 83 (128 before the change; no new ones) |
| Unrouted | 0 |
| Check against the schematic | 26 (differences in how net names are written, and the mounting holes; the same as before the change) |

At that time, the following two things were fixed.
- Set the top silkscreen text "github.com/photonglass/photonglass / CERN-OHL-S v2" and "PHOTON GLASS / 2026 / PB-4" to a text height of 1.0 mm and a stroke width of 0.16 mm (JLCPCB's minimum is 1.0 mm high and 0.153 mm stroke width). The Eagle data has been fixed in the same way.
- Eagle's zero-width guide lines (eight horizontal and vertical lines dividing up the whole board) had been imported into KiCad as top silkscreen (0.1 mm wide), so they were moved to the User.Drawings layer, which is not printed. The script that makes the Gerbers from the Eagle data does not output these lines, so they were never in the zip in `../gerber/`. They were printed only when Gerbers were exported from KiCad.

## Exporting Gerbers
Export with "File → Fabrication Outputs → Gerbers" and "Drill Files", and put them together in one zip.
If you do not modify the board, use the zip in `../gerber/` as it is.
The zip in `../gerber/` was made from the Eagle data with a script (["About the Gerbers" in `../../JLCPCB_ORDERING.en.md`](../../JLCPCB_ORDERING.en.md#about-the-gerbers)). If you export from KiCad, the extent of the GND pours (the clearance from the board edge and holes) and the shape of the silkscreen text will differ slightly from this zip.

[日本語](README.md) | English

# KiCad 9 project (camera board)

Double-click `OG19_PC-3_camera.kicad_pro` to open the schematic and the board.
It was made by importing the Eagle data in `../eagle/` into KiCad 9.0.
It can also be opened in KiCad 10 or later, but saving it converts the files to the new format, and they can then no longer be opened in KiCad 9.

## Comparison with the Eagle version (2026-11-12)
| Item | Result |
|---|---|
| Connections (16 nets, all pads) | Match across all three: the Eagle version, the schematic and the board |
| Traces / vias / outline | 201 / 52 / 39.3 × 17.2 mm, the same as the Eagle version |
| DRC (clearance, unrouted) | 0 errors (GND pour filled) |

### Fixes made after importing
- Aligned the net names on the board with those in the schematic (Eagle names such as `N$1` were changed to KiCad-style names).
- Changed the default clearance from 0.2 to **0.15 mm** (to match the original design's minimum spacing of 6 mil = 0.1524 mm).
- Fixed the mapping between the schematic symbols and the board footprints (`R0603` → `R0603_348`, `CHIPLED_0603` → `CHIPLED_0603_259`).
- The reference designator of the status LED has changed from `GND` to **`GND0`** because of KiCad's rules (it remains `GND` in the JLCPCB BOM/CPL).

### Remaining warnings (not a problem)
- Pins 17 (DDC/CEC GND) and 19 (HPD) of the HDMI connector (CN1) are unconnected: as in the original design.
- `UNK_HOLE_0/1`: the board's mounting holes (non-plated). Reported as "extra footprints" because they have no symbol in the schematic.
- Size and thickness of the silkscreen text: inherited as they were from the Eagle text settings.
- Power pins not driven (ERC): because there is no PWR_FLAG in the schematic. This does not affect operation.

## Exporting Gerbers
Export with "File → Fabrication Outputs → Gerbers" and "Drill Files", and put them together in one zip.
If you do not modify the board, use the zip in `../gerber/` as it is.
The zip in `../gerber/` was made from the Eagle data with a script (["About the Gerbers" in `../../JLCPCB_ORDERING.en.md`](../../JLCPCB_ORDERING.en.md#about-the-gerbers)). If you export from KiCad, the extent of the GND pours (the clearance from the board edge and holes) and the shape of the silkscreen text will differ slightly from this zip.

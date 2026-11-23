# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright (C) OTON GLASS Inc.
"""L-shaped USB-A plug cover (cable exits to the RIGHT) for the PHOTON GLASS power cable (CadQuery).

Covers a board-mount right-angle USB-A plug (Chang Enn USB-4AM103AS, Akizuki 102236) whose pins are
hand-soldered to two AWG24 wires, and clamps the wires for strain relief.

Frame (mm): x = plug axis (plug tip x=0, shell rear face x=18.8), y = across the plug (+-6.0),
z = plug thickness (shell 0..4.5). The plug's L-bent pins are bent straight back (+x), cut to L_PIN and soldered.
The wires turn 90 deg right behind the plug; the cable is clamped sideways between ridges on the slot floor and
the flat underside of the lid (the slot is as deep as the cable).
Parts: BASE (open top; plug pocket with crush ribs and rear stops, solder-joint cavity, cable slot, screw boss) and
LID (crush ribs, cable ridge, 1 screw WILCO FXB-1430EB). The plug and the lid are bonded with 2-part epoxy (see README).
"Right" = seen from the lid side (screw head up) with the plug tip pointing TOWARD you, the cable leaves to the right.
The geometry is built with the exit on +y and mirrored at export (exit on -y).
usage: python usb_plug_cover.py OUTDIR
"""
import sys, os
import cadquery as cq

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'; os.makedirs(OUT, exist_ok=True)

# ---- plug (from the USB-4AM103 drawing) ----
PLUG_W, PLUG_T, PLUG_REAR = 12.0, 4.5, 18.8   # shell width / thickness, tip-to-rear-face length
CLR = 0.1                       # clearance around the plug shell (crush ribs take it up)
RIB = 0.25                      # crush-rib protrusion into the pocket (-> ~0.15 mm interference)
# ---- how far the plug sticks out of the battery's USB port when fully inserted (measured) ----
PROTRUDE = 7.5                  # measured: rear face of the plug .. face of the port
GAP = 1.7                       # gap between the cover front and the port
# ---- cable ----
CABLE_D = 2.0                   # max cable diameter (two-core cable, or the red/black pair bundled)
# ---- cover ----
X0 = PLUG_REAR - PROTRUDE + GAP # front face (only the rear part of the plug is covered)
YO = 8.0                        # half width outside
ZS = PLUG_T + CLR               # split plane (top of the plug + clearance)
FLOOR_REAR = -0.8               # rear cavity floor: the pins are bent straight back, so the joints stay ~within the plug thickness
WALL = 1.2
ZB = FLOOR_REAR - WALL          # bottom face
LID_T = 1.3
R_V = 2.0                       # vertical edge round
CHAMFER = 0.6                   # outer edges of the bottom and of the lid top
# ---- rear section (built for the exit on +y) ----
L_PIN = 1.0                     # the bent-back pins are cut to this length behind the plug's rear face
L_XC = PLUG_REAR + L_PIN + 1.4  # cable slot centre (x): pin + wire bend
L_WALL = 0.9                    # wall behind the slot (2 perimeters of a 0.4 mm nozzle)
SLOT_W = CABLE_D + 0.2
L_X1 = L_XC + SLOT_W / 2 + L_WALL   # rear face -> cover 10.2 mm long, sticks out ~12 mm from the port
L_YE = 11.0                     # outer face on the exit side (the cover widens there)
L_XE0 = L_XC - SLOT_W / 2 - 1.8 # where the widened part starts (1.8 mm wall in front of the slot)
L_RIDGES = (7.6, 9.8)           # y of the ridges on the slot floor
L_LID_RIDGE = (8.4, 9.0)        # y of the ridge under the lid (between the floor ridges)
# ---- screw: WILCO FXB-1430EB (M1.4 x 3.0 low-head B-tite), 1 pc ----
# It sits in the rear corner on the side AWAY from the cable exit: the only place where a boss fits beside the
# plug, the pins and the wires without changing the outer shape. The head counterbore stays inside the flat top
# of the lid (clear of the 0.6 mm chamfer and the corner round).
PILOT_D, CLEAR_D, HEAD_D, HEAD_H = 1.2, 1.6, 3.5, 0.5
SCREW_LEN = 3.0
SCREW = (L_X1 - CHAMFER - HEAD_D / 2 - 0.1, -(YO - CHAMFER - HEAD_D / 2 - 0.1))   # (20.75, -5.55); 0.1 mm inside the flat top
BOSS_D = PILOT_D + 2 * 0.6      # 0.6 mm wall around the pilot hole
PILOT_Z0 = ZS + LID_T - HEAD_H - SCREW_LEN - 0.4   # screw tip + 0.4 mm


def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane().box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))
def zcyl(x, y, d, z0, z1):
    return cq.Workplane().circle(d / 2).extrude(z1 - z0).translate((x, y, z0))
def yr(s, a, b):                # y-range a..b on side s (+1 / -1)
    return (a, b) if s > 0 else (-b, -a)

PY = PLUG_W / 2 + CLR           # pocket half width
RIB_X = (X0 + 1.2, PLUG_REAR - 1.0)            # x of the crush ribs (side walls and lid)
# GLUE KEYS: grooves around the shell between the ribs. The plug is bonded with 2-part epoxy (sanded shell);
# the epoxy fills these grooves and becomes a mechanical key, so the cover can't slide off when unplugging.
KEY_X, KEY_W, KEY_D = (X0 + 2.4, X0 + 3.6), 0.6, 0.4


def outline(z0, z1):
    """Cover footprint extruded from z0 to z1, vertical edges rounded."""
    pts = [(X0, -YO), (L_X1, -YO), (L_X1, L_YE), (L_XE0, L_YE), (L_XE0, YO), (X0, YO), (X0, -YO)]
    sk = cq.Sketch().polygon(pts).vertices().fillet(R_V)   # round in 2D (a 3D fillet of the inner corner fails)
    return cq.Workplane().placeSketch(sk).extrude(z1 - z0).translate((0, 0, z0))


def build():
    # ================= BASE =================
    base = outline(ZB, ZS).faces('<Z').edges().chamfer(CHAMFER)
    # plug pocket (shell sits on z=-CLR/2 floor) and rear cavity for the bent-back pins / solder joints
    base = base.cut(box(X0 - 1, PLUG_REAR + CLR, -PY, PY, -CLR / 2, ZS + 1))
    base = base.cut(box(PLUG_REAR + CLR - 0.01, L_XC + SLOT_W / 2, -6.8, 6.8, FLOOR_REAR, ZS + 1))
    # REAR STOPS: the plug's rear face bears on these when it is pushed into the port (it can no longer slide back).
    # They sit outside the outer pins (y +-3.5); 1.2 mm deep so the wire and the cable turning behind the plug clear them.
    for s in (1, -1):
        ya, yb = yr(s, 4.7, 6.9)
        base = base.union(box(PLUG_REAR + CLR, PLUG_REAR + CLR + 1.2, ya, yb, FLOOR_REAR - 0.01, ZS))
    # SCREW BOSS in the rear corner away from the exit (joins the rear stop, the side wall and the rear wall)
    base = base.union(zcyl(SCREW[0], SCREW[1], BOSS_D, FLOOR_REAR - 0.01, ZS))
    base = base.union(box(SCREW[0], L_X1, -YO, SCREW[1], FLOOR_REAR - 0.01, ZS)
                      .intersect(outline(FLOOR_REAR - 0.01, ZS)))                                # fill to the walls
    # CRUSH RIBS on both side walls: vertical half-round ribs that squeeze the shell (stops the wobble across)
    for rx in RIB_X:
        for s in (1, -1):
            base = base.union(zcyl(rx, s * (PY + 0.4 - RIB), 0.8, -CLR / 2, ZS).intersect(box(rx - 1, rx + 1, -YO, YO, -1, ZS)))
    # glue-key grooves: floor (across y) and both side walls (vertical)
    for kx in KEY_X:
        base = base.cut(box(kx - KEY_W / 2, kx + KEY_W / 2, -PY + 0.6, PY - 0.6, -CLR / 2 - KEY_D, 0.01))
        for s in (1, -1):
            ya, yb = yr(s, PY - 0.01, PY + KEY_D)
            base = base.cut(box(kx - KEY_W / 2, kx + KEY_W / 2, ya, yb, -CLR / 2, ZS + 1))
    # cable slot: runs sideways (+y) through the side wall, exactly CABLE_D deep, so the flat lid closes it
    SLOT_Z0 = ZS - CABLE_D
    base = base.cut(box(L_XC - SLOT_W / 2, L_XC + SLOT_W / 2, 6.79, L_YE + 1, SLOT_Z0, ZS + 1))
    for ry in L_RIDGES:
        base = base.union(box(L_XC - SLOT_W / 2, L_XC + SLOT_W / 2, ry - 0.3, ry + 0.3, SLOT_Z0 - 0.01, SLOT_Z0 + 0.3))
    # screw pilot hole
    base = base.cut(zcyl(SCREW[0], SCREW[1], PILOT_D, PILOT_Z0, ZS + 1))

    # ================= LID =================
    lid = outline(ZS, ZS + LID_T).faces('>Z').edges().chamfer(CHAMFER)
    lid = lid.cut(zcyl(SCREW[0], SCREW[1], CLEAR_D, ZS - 1, ZS + LID_T + 1))
    lid = lid.cut(zcyl(SCREW[0], SCREW[1], HEAD_D, ZS + LID_T - HEAD_H, ZS + LID_T + 1))
    # glue-key grooves under the lid
    for kx in KEY_X:
        lid = lid.cut(box(kx - KEY_W / 2, kx + KEY_W / 2, -PY + 0.6, PY - 0.6, ZS - 0.01, ZS + KEY_D))
    # CRUSH RIBS under the lid: press the plug down onto the floor (stops the wobble up/down)
    for rx in RIB_X:
        lid = lid.union(box(rx - 0.3, rx + 0.3, -4.5, 4.5, ZS - RIB, ZS + 0.01))
    # one low ridge under the lid between the floor ridges of the cable slot (pinches the cable into a wave)
    xa = L_XC - SLOT_W / 2 + 0.1
    lid = lid.union(box(xa, xa + 0.6, L_LID_RIDGE[0], L_LID_RIDGE[1], ZS - 0.3, ZS + 0.01))
    return base, lid


def export(prefix, base, lid):
    for name, part in ((f'{prefix}_base', base), (f'{prefix}_lid', lid)):
        assert part.val().isValid(), name
        cq.exporters.export(part, f'{OUT}/{name}.step')
        cq.exporters.export(part, f'{OUT}/{name}.stl', tolerance=0.02, angularTolerance=0.1)
        print(name, round(part.val().Volume(), 1), (lambda b: [round(v, 2) for v in (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)])(part.val().BoundingBox()))
    # print orientation: base as modelled (bottom on bed); lid flipped (outer face on bed)
    cq.exporters.export(base.translate((0, 0, -ZB)), f'{OUT}/{prefix}_base_print.stl', tolerance=0.02, angularTolerance=0.1)
    cq.exporters.export(lid.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, ZS + LID_T)), f'{OUT}/{prefix}_lid_print.stl',
                        tolerance=0.02, angularTolerance=0.1)


if __name__ == '__main__':
    b, l = build()
    export('usb_cover_L_right', b.mirror('XZ'), l.mirror('XZ'))

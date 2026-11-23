# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright (C) OTON GLASS Inc.
"""USB-A plug cover for the PHOTON GLASS power cable (CadQuery).

Covers a board-mount right-angle USB-A plug (Chang Enn USB-4AM103AS, Akizuki 102236) whose pins are
hand-soldered to two AWG24 wires, and clamps the wires for strain relief.

Frame (mm): x = plug axis (plug tip x=0, shell rear face x=18.8), y = across the plug (+-6.0),
z = plug thickness (shell 0..4.5). The plug's L-bent pins are bent straight back (+x) before soldering.
Parts: BASE (open top; plug pocket with crush ribs and rear stops, solder-joint cavity, cable clamp slot) and
LID (crush ribs, cable clamp, hooks at the front, 2 screws WILCO FXB-1430EB at the rear).
The cover front is set from the measured protrusion of the plug out of the battery's port (PROTRUDE). Assembly: drop the lid 1.4 mm behind its final position, slide it
forward so the hooks catch, then screw. The plug is bonded with 2-part epoxy (see README).

Variants (cable exit):
  straight : the cable leaves straight back (files usb_cover_base / usb_cover_lid)
  left     : L-shape, the cable leaves sideways to the LEFT  (files usb_cover_L_left_*)
  right    : L-shape, the cable leaves sideways to the RIGHT (files usb_cover_L_right_*)
  Left/right = seen from the lid side (lid up) with the plug tip pointing toward you (left = +y).
  The L-shape is short (about 12 mm): the bent-back pins are cut to 1.5 mm, the wires turn 90 deg right
  behind the plug and the cable is clamped sideways between ridges on the slot floor and the flat underside of
  the lid (the slot is as deep as the cable). There is no room for the rear screws, so the L lid is held by the
  front hooks and bonded with the same epoxy that fills the cavity.
usage: python usb_plug_cover.py OUTDIR [straight|left|right|all]
"""
import sys, os
import cadquery as cq

OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'; os.makedirs(OUT, exist_ok=True)
ARG = sys.argv[2] if len(sys.argv) > 2 else 'straight'
assert ARG in ('straight', 'left', 'right', 'all'), ARG

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
X1 = 34.5                       # rear face
YO = 8.0                        # half width outside
ZS = PLUG_T + CLR               # split plane (top of the plug + clearance)
FLOOR_REAR = -0.8               # rear cavity floor: the pins are bent straight back, so the joints stay ~within the plug thickness
WALL = 1.2
ZB = FLOOR_REAR - WALL          # bottom face
LID_T = 1.3
R_V = 2.0                       # vertical edge round
# ---- screws: WILCO FXB-1430EB (M1.4 x 3.0 low-head B-tite) ----
PILOT_D, CLEAR_D, HEAD_D, HEAD_H = 1.2, 1.6, 3.5, 0.5
SCREWS = [(29.0, 6.0), (29.0, -6.0)]
# ---- hooks (front of the lid) ----
SLIDE = 1.4
UX0, UX1 = X0 + 1.0, X0 + 2.2   # undercut in the base cheek (hook foot sits here)
LEG1 = UX1 + 1.2                # leg spans UX1..LEG1
HY0, HY1 = 6.15, 6.9            # hook thickness across y (mirrored to -y)
HZ0, HZ1, UZ1 = 3.3, 3.85, 3.9  # hook bottom, foot top, undercut roof

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

# ---- L-shape (side exit) rear section; built for the LEFT exit (+y), mirrored for the right ----
L_XC = PLUG_REAR + 4.1          # cable slot centre (x): pins cut to 1.5 mm + solder joint + wire bend
L_X1 = L_XC + (CABLE_D + 0.2) / 2 + 1.2   # rear face (1.2 mm wall behind the slot) -> cover ~12 mm long
L_YE = 11.0                     # outer face on the exit side (the cover widens there)
L_XE0 = L_XC - (CABLE_D + 0.2) / 2 - 1.8  # where the widened part starts (1.8 mm wall in front of the slot)
L_SCREWS = []                   # no room for screws: hooks + epoxy
L_RIDGES = (7.6, 9.8)           # y of the ridges on the slot floor
L_LID_RIDGE = (8.4, 9.0)        # y of the ridge under the lid (between the floor ridges)


def outline(L, z0, z1):
    """Cover footprint extruded from z0 to z1, vertical edges rounded."""
    if not L:
        return box(X0, X1, -YO, YO, z0, z1).edges('|Z').fillet(R_V)
    pts = [(X0, -YO), (L_X1, -YO), (L_X1, L_YE), (L_XE0, L_YE), (L_XE0, YO), (X0, YO), (X0, -YO)]
    sk = cq.Sketch().polygon(pts).vertices().fillet(R_V)   # round in 2D (a 3D fillet of the inner corner fails)
    return cq.Workplane().placeSketch(sk).extrude(z1 - z0).translate((0, 0, z0))


def build(L):
    xr = L_X1 if L else X1
    screws = L_SCREWS if L else SCREWS
    SLOT_W = CABLE_D + 0.2
    # ================= BASE =================
    base = outline(L, ZB, ZS).faces('<Z').edges().chamfer(0.6)
    # plug pocket (shell sits on z=-CLR/2 floor) and rear cavity for the bent-back pins / solder joints
    base = base.cut(box(X0 - 1, PLUG_REAR + CLR, -PY, PY, -CLR / 2, ZS + 1))
    cav_x1 = L_XC + SLOT_W / 2 if L else 26.0
    base = base.cut(box(PLUG_REAR + CLR - 0.01, cav_x1, -6.8, 6.8, FLOOR_REAR, ZS + 1))
    # REAR STOPS: the plug's rear face bears on these when it is pushed into the port (it can no longer slide back).
    # They sit outside the outer pins (y +-3.5) and their solder joints (~1.8 mm with heat-shrink).
    for s in (1, -1):
        ya, yb = yr(s, 4.7, 6.9)
        base = base.union(box(PLUG_REAR + CLR, PLUG_REAR + CLR + 1.6, ya, yb, FLOOR_REAR - 0.01, ZS))
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
    if not L:
        # cable zone (jacket end, wires split to the two pins)
        base = base.cut(box(25.99, 30.0, -3.5, 3.5, FLOOR_REAR, ZS + 1))
        # cable exit slot (U-shaped, open top) with two ridges on the floor; the lid tongue (one ridge) pinches the cable into a wave
        SLOT_Z0 = 0.0
        base = base.cut(box(29.99, X1 + 1, -SLOT_W / 2, SLOT_W / 2, SLOT_Z0, ZS + 1))
        for rx in (31.0, 33.2):
            base = base.union(box(rx - 0.3, rx + 0.3, -SLOT_W / 2, SLOT_W / 2, SLOT_Z0 - 0.01, SLOT_Z0 + 0.3))
    else:
        # L-shape: the slot runs sideways (+y) through the side wall. It is exactly CABLE_D deep, so the flat
        # underside of the lid closes it (no tongue -> the lid can still slide 1.4 mm onto the hooks).
        SLOT_Z0 = ZS - CABLE_D
        base = base.cut(box(L_XC - SLOT_W / 2, L_XC + SLOT_W / 2, 6.79, L_YE + 1, SLOT_Z0, ZS + 1))
        for ry in L_RIDGES:
            base = base.union(box(L_XC - SLOT_W / 2, L_XC + SLOT_W / 2, ry - 0.3, ry + 0.3, SLOT_Z0 - 0.01, SLOT_Z0 + 0.3))
    # screw pilots
    for sx, sy in screws:
        base = base.cut(zcyl(sx, sy, PILOT_D, ZS - 3.6, ZS + 1))
    # hook channels (open top) and undercuts in the front cheeks
    for s in (1, -1):
        ya, yb = yr(s, 6.0, 7.0)
        base = base.cut(box(UX1, LEG1 + SLIDE + 0.05, ya, yb, HZ0 - 0.1, ZS + 1))
        base = base.cut(box(UX0 - 0.1, UX1 + 0.01, ya, yb, HZ0 - 0.1, UZ1))

    # ================= LID =================
    lid = outline(L, ZS, ZS + LID_T).faces('>Z').edges().chamfer(0.6)
    for sx, sy in screws:
        lid = lid.cut(zcyl(sx, sy, CLEAR_D, ZS - 1, ZS + LID_T + 1))
        lid = lid.cut(zcyl(sx, sy, HEAD_D, ZS + LID_T - HEAD_H, ZS + LID_T + 1))
    # glue-key grooves under the lid
    for kx in KEY_X:
        lid = lid.cut(box(kx - KEY_W / 2, kx + KEY_W / 2, -PY + 0.6, PY - 0.6, ZS - 0.01, ZS + KEY_D))
    # CRUSH RIBS under the lid: press the plug down onto the floor (stops the wobble up/down)
    for rx in RIB_X:
        lid = lid.union(box(rx - 0.3, rx + 0.3, -4.5, 4.5, ZS - RIB, ZS + 0.01))
    if not L:
        # clamp tongue in the exit slot: flat at the cable's top (CABLE_D) with one ridge between the floor ridges
        TW = SLOT_W - 0.2
        lid = lid.union(box(30.5, X1, -TW / 2, TW / 2, SLOT_Z0 + CABLE_D + 0.3, ZS + 0.01))
        lid = lid.union(box(31.8, 32.4, -TW / 2, TW / 2, SLOT_Z0 + CABLE_D, ZS + 0.01))
    else:
        # one low ridge under the lid between the floor ridges. It sits on the front half of the slot so that it
        # still drops into the slot when the lid is placed SLIDE mm behind (+x) its final position.
        xa = L_XC - SLOT_W / 2 + 0.1
        lid = lid.union(box(xa, xa + 0.6, L_LID_RIDGE[0], L_LID_RIDGE[1], ZS - 0.3, ZS + 0.01))
    # hooks: leg + foot
    for s in (1, -1):
        ya, yb = yr(s, HY0, HY1)
        lid = lid.union(box(UX1 + 0.05, LEG1, ya, yb, HZ0, ZS + 0.01))
        lid = lid.union(box(UX0 + 0.05, UX1 + 0.06, ya, yb, HZ0, HZ1))
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


if ARG in ('straight', 'all'):
    export('usb_cover', *build(False))
if ARG in ('left', 'right', 'all'):
    b, l = build(True)
    if ARG in ('left', 'all'):
        export('usb_cover_L_left', b, l)
    if ARG in ('right', 'all'):
        export('usb_cover_L_right', b.mirror('XZ'), l.mirror('XZ'))

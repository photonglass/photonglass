# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright (C) OTON GLASS Inc.
"""Assembly model: USB-A plug (USB-4AM103AS, pins bent straight back) + wires + cable + screw inside the L-shaped
cover (cable exits to the right).

Reads the cover parts from ../step/ (made by usb_plug_cover.py) and writes
  OUTDIR/usb_plug_with_cover_L_right.step  (colored assembly, one body per part)
  OUTDIR/usb_plug_with_cover_L_right.stl   (everything merged, for viewing)
The plug is modelled from the maker's drawing (shell 12.0 x 4.5 x 18.8 mm, 4 contacts, pitch 2.5/2.0/2.5).
Its internal details (insulator, contact shapes) are simplified. Same frame as usb_plug_cover.py.
usage: python usb_plug_assembly.py OUTDIR
"""
import sys, os
import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
STEP_DIR = os.path.join(HERE, '..', 'step')
OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'; os.makedirs(OUT, exist_ok=True)

W, T, L, SH = 12.0, 4.5, 18.8, 0.3          # shell width / thickness / length / sheet thickness
Z0 = -0.05                                  # the plug sits on the pocket floor
PIN_Y = (-3.5, -1.0, 1.0, 3.5)              # contact positions (pin 1 .. 4 as seen from above, tip away)
PIN_Z = 1.0                                 # height where the pins leave the rear face (bent straight back)
L_PIN = 1.0                                 # L-shape: pin length left behind the rear face (= usb_plug_cover.L_PIN)
L_XC = L + L_PIN + 1.4                      # L-shape: cable slot centre (= usb_plug_cover.L_XC)
SCREW_X, SCREW_Y = 20.75, 5.55              # screw position after mirroring (= usb_plug_cover.SCREW, mirrored)

def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane().box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))

# metal shell: rectangular tube, open at the tip, two latch windows on top and bottom
shell = box(0, L, -W / 2, W / 2, Z0, Z0 + T).cut(box(-1, L + 1, -W / 2 + SH, W / 2 - SH, Z0 + SH, Z0 + T - SH))
for yc in (-2.5, 2.5):
    shell = shell.cut(box(3.0, 5.6, yc - 1.0, yc + 1.0, Z0 - 1, Z0 + T + 1))
# insulator: tongue in the lower half (contacts face up), full block at the rear
ins = box(0.6, L, -W / 2 + SH, W / 2 - SH, Z0 + SH, Z0 + 2.2).union(box(13.0, L, -W / 2 + SH, W / 2 - SH, Z0 + SH, Z0 + T - SH))
# contacts on the tongue (outer two longer = power: VBUS / GND)
contacts = None
for i, y in enumerate(PIN_Y):
    x0 = 1.0 if i in (0, 3) else 1.5
    c = box(x0, 9.5, y - 0.5, y + 0.5, Z0 + 2.2, Z0 + 2.3)
    contacts = c if contacts is None else contacts.union(c)
# pins: outer two bent straight back (soldered), inner two cut short
def make_pins(outer):
    pins = None
    for i, y in enumerate(PIN_Y):
        ln = outer if i in (0, 3) else 0.6
        p = box(L, L + ln, y - 0.3, y + 0.3, PIN_Z - 0.15, PIN_Z + 0.15)
        pins = p if pins is None else pins.union(p)
    return pins

# wires (red on pin 1 side, black on pin 4 side), heat-shrink over the joints, 2 mm cable to the rear
def seg(a, b, d):
    v = cq.Vector(*b) - cq.Vector(*a)
    return cq.Workplane(cq.Plane(origin=a, xDir=(0, 0, 1) if abs(v.normalized().z) < 0.9 else (1, 0, 0), normal=v.normalized().toTuple())).circle(d / 2).extrude(v.Length)
def make_shrink(x1):
    return seg((19.4, -3.5, PIN_Z), (x1, -3.5, PIN_Z), 1.8).union(seg((19.4, 3.5, PIN_Z), (x1, 3.5, PIN_Z), 1.8))


def poly(pts, d):
    """Wire along a polyline (with small balls at the bends)."""
    w = None
    for a, b in zip(pts, pts[1:]):
        p = seg(a, b, d)
        w = p if w is None else w.union(p)
    for c in pts[1:-1]:
        w = w.union(cq.Workplane().sphere(d / 2).translate(c))
    return w


def wiring():
    """Returns (red, black, cable). Built for the exit on +y and mirrored (exit on -y = right)."""
    # pins cut to L_PIN, the wires turn 90 deg right behind the plug and rise to the cable, which runs sideways
    # in a slot as deep as the cable (top flush with the lid).
    CZ = 4.6 - 1.0                                   # cable centre (ZS - CABLE_D / 2)
    XF, XN = L_XC + 0.55, L_XC - 0.55                # far / near wire run (side by side in the slot band)
    xe = L + L_PIN + 0.4                             # end of the solder joint
    far = poly([(19.6, -3.5, PIN_Z), (xe, -3.5, PIN_Z), (XF, -3.5 + (XF - xe), PIN_Z), (XF, 3.5, PIN_Z), (XF, 5.0, CZ - 0.2)], 1.04)
    near = poly([(19.6, 3.5, PIN_Z), (xe, 3.5, PIN_Z), (XN, 4.2, 1.8), (XN, 5.0, CZ - 0.2)], 1.04)
    cable = seg((L_XC, 4.8, CZ), (L_XC, 28.0, CZ), 2.0)
    m = lambda w: w.mirror('XZ')
    return m(near), m(far), m(cable)                  # after mirroring the red pin (pin 1) is on the exit side


def make():
    base = cq.importers.importStep(os.path.join(STEP_DIR, 'usb_cover_L_right_base.step'))
    lid = cq.importers.importStep(os.path.join(STEP_DIR, 'usb_cover_L_right_lid.step'))
    red, blk, cable = wiring()
    pins = make_pins(L_PIN).mirror('XZ')
    shrink = make_shrink(L + L_PIN + 0.4).mirror('XZ')
    # screw FXB-1430EB: head 3.5 x 0.5 in the lid counterbore, M1.4 x 3.0 shank into the base boss
    sx, sy, ztop = SCREW_X, SCREW_Y, 4.6 + 1.3
    screw = (cq.Workplane().circle(1.75).extrude(0.5).translate((sx, sy, ztop - 0.5))
             .union(cq.Workplane().circle(0.7).extrude(3.0).translate((sx, sy, ztop - 0.5 - 3.0))))
    asm = cq.Assembly(name='usb_plug_with_cover_L_right')
    for name, part, col in (('cover_base', base, (0.24, 0.26, 0.29)), ('cover_lid', lid, (0.35, 0.38, 0.41)),
                            ('plug_shell', shell, (0.78, 0.80, 0.82)), ('plug_insulator', ins, (0.95, 0.95, 0.95)),
                            ('plug_contacts', contacts, (0.85, 0.70, 0.25)), ('plug_pins', pins, (0.85, 0.70, 0.25)),
                            ('heat_shrink', shrink, (0.1, 0.1, 0.1)), ('wire_red', red, (0.82, 0.2, 0.18)),
                            ('wire_black', blk, (0.12, 0.12, 0.12)), ('cable', cable, (0.12, 0.12, 0.12)),
                            ('screw', screw, (0.6, 0.6, 0.65))):
        asm.add(part, name=name, color=cq.Color(*col))
    asm.export(os.path.join(OUT, 'usb_plug_with_cover_L_right.step'))
    merged = base.union(lid).union(shell).union(ins).union(contacts).union(pins).union(shrink).union(red).union(blk).union(cable).union(screw)
    cq.exporters.export(merged, os.path.join(OUT, 'usb_plug_with_cover_L_right.stl'), tolerance=0.02, angularTolerance=0.1)
    print('ok', round(merged.val().Volume(), 1))


if __name__ == '__main__':
    make()

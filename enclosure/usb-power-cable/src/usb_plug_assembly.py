# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2019-2026 OTON GLASS open hardware contributors
"""Assembly model: USB-A plug (USB-4AM103AS, pins bent straight back) + wires + cable inside the cover.

Reads the cover parts from ../step/ (made by usb_plug_cover.py) and writes, for each variant,
  OUTDIR/usb_plug_with_cover[_L_left|_L_right].step  (colored assembly, one body per part)
  OUTDIR/usb_plug_with_cover[_L_left|_L_right].stl   (everything merged, for viewing)
The plug is modelled from the maker's drawing (shell 12.0 x 4.5 x 18.8 mm, 4 contacts, pitch 2.5/2.0/2.5).
Its internal details (insulator, contact shapes) are simplified. Same frame as usb_plug_cover.py.
usage: python usb_plug_assembly.py OUTDIR [straight|left|right|all]
"""
import sys, os
import cadquery as cq

HERE = os.path.dirname(os.path.abspath(__file__))
STEP_DIR = os.path.join(HERE, '..', 'step')
OUT = sys.argv[1] if len(sys.argv) > 1 else 'out'; os.makedirs(OUT, exist_ok=True)
ARG = sys.argv[2] if len(sys.argv) > 2 else 'straight'
assert ARG in ('straight', 'left', 'right', 'all'), ARG

W, T, L, SH = 12.0, 4.5, 18.8, 0.3          # shell width / thickness / length / sheet thickness
Z0 = -0.05                                  # the plug sits on the pocket floor
PIN_Y = (-3.5, -1.0, 1.0, 3.5)              # contact positions (pin 1 .. 4 as seen from above, tip away)
PIN_Z = 1.0                                 # height where the pins leave the rear face (bent straight back)

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


def wiring(variant):
    """Returns (red, black, cable)."""
    if variant == 'straight':
        red = poly([(19.6, -3.5, PIN_Z), (25.0, -3.5, PIN_Z), (27.6, -0.4, PIN_Z)], 1.04)
        blk = poly([(19.6, 3.5, PIN_Z), (25.0, 3.5, PIN_Z), (27.6, 0.4, PIN_Z)], 1.04)
        return red, blk, seg((27.5, 0, 1.0), (50.0, 0, 1.0), 2.0)
    # L-shape, built for the left exit (+y): pins cut to 1.5 mm, the wires turn 90 deg right behind the plug and
    # rise to the cable, which runs sideways in a slot as deep as the cable (top flush with the lid).
    CZ = 4.6 - 1.0                                   # cable centre (ZS - CABLE_D / 2)
    far = poly([(19.6, -3.5, PIN_Z), (21.6, -3.5, PIN_Z), (23.45, -1.65, PIN_Z), (23.45, 3.5, PIN_Z), (23.45, 5.0, CZ - 0.2)], 1.04)
    near = poly([(19.6, 3.5, PIN_Z), (21.6, 3.5, PIN_Z), (22.35, 4.2, 1.8), (22.35, 5.0, CZ - 0.2)], 1.04)
    cable = seg((22.9, 4.8, CZ), (22.9, 28.0, CZ), 2.0)
    if variant == 'left':
        return far, near, cable                       # pin 1 (red, -y) is the far one
    m = lambda w: w.mirror('XZ')
    return m(near), m(far), m(cable)                  # right: mirrored; the red pin is now on the exit side


def make(variant):
    prefix = {'straight': 'usb_cover', 'left': 'usb_cover_L_left', 'right': 'usb_cover_L_right'}[variant]
    suffix = {'straight': '', 'left': '_L_left', 'right': '_L_right'}[variant]
    base = cq.importers.importStep(os.path.join(STEP_DIR, prefix + '_base.step'))
    lid = cq.importers.importStep(os.path.join(STEP_DIR, prefix + '_lid.step'))
    red, blk, cable = wiring(variant)
    # straight: outer pins 3.2 mm long; L: cut to 1.5 mm (short heat-shrink)
    pins = make_pins(3.2 if variant == 'straight' else 1.5)
    shrink = make_shrink(23.4 if variant == 'straight' else 21.2)
    asm = cq.Assembly(name='usb_plug_with_cover' + suffix)
    for name, part, col in (('cover_base', base, (0.24, 0.26, 0.29)), ('cover_lid', lid, (0.35, 0.38, 0.41)),
                            ('plug_shell', shell, (0.78, 0.80, 0.82)), ('plug_insulator', ins, (0.95, 0.95, 0.95)),
                            ('plug_contacts', contacts, (0.85, 0.70, 0.25)), ('plug_pins', pins, (0.85, 0.70, 0.25)),
                            ('heat_shrink', shrink, (0.1, 0.1, 0.1)), ('wire_red', red, (0.82, 0.2, 0.18)),
                            ('wire_black', blk, (0.12, 0.12, 0.12)), ('cable', cable, (0.12, 0.12, 0.12))):
        asm.add(part, name=name, color=cq.Color(*col))
    asm.export(os.path.join(OUT, f'usb_plug_with_cover{suffix}.step'))
    merged = base.union(lid).union(shell).union(ins).union(contacts).union(pins).union(shrink).union(red).union(blk).union(cable)
    cq.exporters.export(merged, os.path.join(OUT, f'usb_plug_with_cover{suffix}.stl'), tolerance=0.02, angularTolerance=0.1)
    print('ok', variant, round(merged.val().Volume(), 1))
    return dict(base=base, lid=lid, shell=shell, ins=ins, contacts=contacts, pins=pins, shrink=shrink, red=red, blk=blk, cable=cable)


if __name__ == '__main__':
    for v in (('straight', 'left', 'right') if ARG == 'all' else (ARG,)):
        make(v)

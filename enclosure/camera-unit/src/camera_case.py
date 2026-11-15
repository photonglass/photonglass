# SPDX-License-Identifier: GPL-3.0-only
# Copyright (C) 2019-2026 OTON GLASS open hardware contributors
"""OTON GLASS camera unit enclosure (v6) - FDM 3D-printable, parametric (CadQuery).
Coordinates: mm, same frame as the camera board placed component-side down (board z 3.4..5.0).
Parts: body (tube with shutter flexure), nose (camera lid), tail (end cap, snap ring), tail_loose, sled (board/camera carrier)
usage: python camera_case.py OUTPUT_DIR
"""

import math, sys, os
import cadquery as cq

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
X_SPLIT, X_TAIL, X_L, X_R = -1.0, 46.3, -10.8, 47.5
Y_F, Y_N, Y_B = -1.4, 3.9, 19.2          # outer: wide front, narrow front, back
Z_B, Z_T = -4.8, 7.6
W = 1.2; R_O = 2.0; R_I = R_O - W
CLR = 0.15
_dx, _dy = 0.580, 0.815
def x_diag(y, outer=True):               # board-parallel diagonal (outer: 0.4 + W from board edge, inner: 0.4)
    p = (20.904, -0.928) if outer else (19.926, -0.232)
    return p[0] + (y - p[1]) / _dy * _dx


def section(x, y0, y1, z0, z1, r):
    """rounded rectangle in the plane X = x"""
    P = lambda y, z: cq.Vector(x, y, z)
    k = r * (1 - 1 / math.sqrt(2))
    e = [cq.Edge.makeLine(P(y0 + r, z0), P(y1 - r, z0)),
         cq.Edge.makeThreePointArc(P(y1 - r, z0), P(y1 - k, z0 + k), P(y1, z0 + r)),
         cq.Edge.makeLine(P(y1, z0 + r), P(y1, z1 - r)),
         cq.Edge.makeThreePointArc(P(y1, z1 - r), P(y1 - k, z1 - k), P(y1 - r, z1)),
         cq.Edge.makeLine(P(y1 - r, z1), P(y0 + r, z1)),
         cq.Edge.makeThreePointArc(P(y0 + r, z1), P(y0 + k, z1 - k), P(y0, z1 - r)),
         cq.Edge.makeLine(P(y0, z1 - r), P(y0, z0 + r)),
         cq.Edge.makeThreePointArc(P(y0, z0 + r), P(y0 + k, z0 + k), P(y0 + r, z0))]
    return cq.Wire.assembleEdges(e)
def loft(*ws): return cq.Workplane().add(cq.Solid.makeLoft(list(ws), True))
def box(x0, x1, y0, y1, z0, z1): return cq.Workplane().box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))
def cylx(x0, x1, y, z, r): return cq.Workplane('YZ').circle(r).extrude(x1 - x0).translate((x0, y, z))

def outer_sec(x, front, shrink=0.0): return section(x, front + shrink, Y_B - shrink, Z_B + shrink, Z_T - shrink, R_O)
def inner_sec(x, front, grow=0.0): return section(x, front - grow, Y_B - W + grow, Z_B + W - grow, Z_T - W + grow, R_I + max(grow, 0))

def tube_solid(sec, xa, xb, fw, fn, dw_x, dn_x):
    """union of wide prism, ruled transition across the diagonal, narrow prism"""
    a = loft(sec(xa, fw), sec(dw_x, fw)); b = loft(sec(dw_x, fw), sec(dn_x, fn)); c = loft(sec(dn_x, fn), sec(xb, fn))
    return a.union(b).union(c)

# ---------------- BODY ----------------
outer = tube_solid(outer_sec, X_SPLIT, X_TAIL, Y_F, Y_N, x_diag(Y_F), x_diag(Y_N))
# inner step at 45 deg (prints without support), set back from the board's 55-deg diagonal
_xi0 = x_diag(Y_F + W, False)
inner = tube_solid(lambda x, f: inner_sec(x, f), X_SPLIT - 1, X_TAIL + 1, Y_F + W, Y_N + W,
                   _xi0, _xi0 + (Y_N - Y_F))
body = outer.cut(inner)
inside = inner.intersect(box(X_SPLIT, X_TAIL, -9, 30, -9, 12))
def inside_only(s): return s.intersect(outer)
# board rails (above / below the board edge), lead-in at x 6.0
rails = (box(6.0, 19.4, Y_F + W - 0.1, 0.6, 5.1, 5.5)
         .union(box(14.8, 19.0, Y_F + W - 0.1, 0.6, 2.9, 3.3))
         .union(box(10.6, 43.6, 16.8, Y_B - W + 0.1, 5.1, 5.5)))
body = body.union(inside_only(rails))
# HDMI: support under CN1 and backstop behind it (plug insertion force)
def wedge_x(x0, x1, y0, y1, z0, z1):      # block whose -x end is a 45-deg ramp rising from the floor
    h = z1 - z0
    return (cq.Workplane('XZ').polyline([(x0, z0), (x1, z0), (x1, z1), (x0 + h, z1)]).close()
            .extrude(-(y1 - y0)).translate((0, y0, 0)))
# HDMI opening: the receptacle mouth (Type A, measured from CN1's model) + 0.3 clearance, 45-deg lead-in
HDMI_MOUTH = [(27.4, -2.38), (41.4, -2.38), (41.4, 0.55), (39.9, 1.18), (38.52, 2.17),
              (30.28, 2.17), (28.9, 1.18), (27.4, 0.55)]
def mouth(o, y):
    return cq.Workplane('XZ', origin=(0, y, 0)).polyline(HDMI_MOUTH).close().offset2D(o)
body = body.cut(mouth(0.3, Y_N - 1).extrude(-(W + 1.3)))
lead = (cq.Workplane('XZ', origin=(0, Y_N - 0.01, 0)).polyline(HDMI_MOUTH).close().offset2D(0.8)
        .workplane(offset=-0.51).polyline(HDMI_MOUTH).close().offset2D(0.3).loft())
body = body.cut(lead)
# shutter flexure (v4 form): tab x 2.5..13.5 free on three sides, hinge on the -x side thinned to 0.8
TAB = (2.5, 13.5, -2.2, 4.6); SLOT = 0.6
ring = box(TAB[0], TAB[1] + SLOT, Y_F - 1, Y_F + W + 0.05, TAB[2] - SLOT, TAB[3] + SLOT).cut(
    box(TAB[0] - 1, TAB[1], Y_F - 2, Y_F + W + 1, TAB[2], TAB[3]))
body = body.cut(ring)
body = body.cut(box(TAB[0], TAB[0] + 3.0, Y_F + 0.8, Y_F + W + 0.05, TAB[2], TAB[3]))          # thin hinge
body = body.union(box(8.8, 10.8, Y_F + W - 0.05, 0.1, 0.7, 2.7))                            # nub on SW1 plunger
key = (cq.Workplane('XZ').center(9.8, 1.4).rect(6.0, 6.0).extrude(0.6).edges('|Y').fillet(1.0)
       .faces('<Y').chamfer(0.45).translate((0, Y_F, 0)))
body = body.union(key)
body = body.cut(cq.Workplane().sphere(16.25).translate((9.8, Y_B + 16.25 - 0.5, 1.4)))   # pinch dimple
# dovetail rail on the head side (-z) for a temple clip adapter
dove = (cq.Workplane('YZ').polyline([(8.5, Z_B + 0.01), (14.5, Z_B + 0.01), (15.2, Z_B - 1.2), (7.8, Z_B - 1.2)]).close()
        .extrude(38.0).translate((4.0, 0, 0)))
dove = dove.cut(cq.Workplane('XZ').polyline([(3.9, Z_B - 1.3), (5.3, Z_B - 1.3), (3.9, Z_B + 0.1)]).close().extrude(-30).translate((0, -5, 0)))
body = body.union(dove)
# all-round snap groove inside the tail end (45-deg flanks)
GR = (45.3, 45.7, 45.8, 46.2)
body = body.cut(loft(inner_sec(GR[0], Y_N + W, 0.0), inner_sec(GR[1], Y_N + W, 0.4))
                .union(loft(inner_sec(GR[1], Y_N + W, 0.4), inner_sec(GR[2], Y_N + W, 0.4)))
                .union(loft(inner_sec(GR[2], Y_N + W, 0.4), inner_sec(GR[3], Y_N + W, 0.0))))

# ---------------- screws: WILCO FXB-1430EB (M1.4 x 3.0 low-head B-tite) ----------------
PILOT, CLEAR, HEAD_D = 0.6, 0.8, 3.5

# ---------------- NOSE = camera lid (screwed to the sled's camera bulkhead) ----------------
NOSE = dict(f=4.4, b=17.2, zb=-4.3, zt=6.8)
nose_out = section(X_L, NOSE['f'], NOSE['b'], NOSE['zb'], NOSE['zt'], R_O)
nose = loft(nose_out, outer_sec(X_SPLIT, Y_F))
nose = nose.faces('<X').chamfer(0.6)
def nose_inner(sh):
    return loft(section(X_L + W, NOSE['f'] + W + sh, NOSE['b'] - W - sh, NOSE['zb'] + W + sh, NOSE['zt'] - W - sh, R_I),
                inner_sec(X_SPLIT + 0.01, Y_F + W, -sh))
nose_in = nose_inner(0.0)
SEAT = -4.5                                   # camera back (tape) seat; Zero Spy Camera 8.6 x 8.6 x 5.2 (+tape)
CAMC = (11.5, 1.22)                           # optical axis (y, z), same as the predecessor
cav = box(-9.8, SEAT + 0.1, CAMC[0] - 4.5, CAMC[0] + 4.5, CAMC[1] - 4.5, CAMC[1] + 4.5)      # module + 0.2
cav = cav.union(nose_in.intersect(box(SEAT, X_SPLIT + 1, -9, 30, -9, 12)))
cav = cav.union(nose_in.intersect(box(-8.6, X_SPLIT + 1, -9, CAMC[0] - 4.3, -9, 12)))       # flex exits on the front side
nose = nose.cut(cav)
nose = nose.cut(cylx(X_L - 1, -9.0, CAMC[0], CAMC[1], 1.5))
nose = nose.cut(cq.Workplane('YZ').circle(2.2).workplane(offset=0.7).circle(1.5).loft().translate((X_L, CAMC[0], CAMC[1])))
XS = -3.25                                    # nose screws: one on the back face, one on the head side
def ycyl(x, z, r, y0, y1): return cq.Workplane('XZ').center(x, z).circle(r).extrude(-(y1 - y0)).translate((0, y0, 0))
def zcyl(x, y, r, z0, z1): return cq.Workplane().circle(r).extrude(z1 - z0).translate((x, y, z0))
nose = nose.cut(ycyl(XS, CAMC[1], CLEAR, 16.0, 21)).cut(ycyl(XS, CAMC[1], HEAD_D / 2, 18.35, 21))
nose = nose.cut(zcyl(XS, CAMC[0], CLEAR, -7, -2.0)).cut(zcyl(XS, CAMC[0], HEAD_D / 2, -7, -4.3))

# ---------------- TAIL: end cap with an all-round snap bead (only the cap is tuned; body groove fixed) ----------------
def make_tail(clr, bead, wall=0.6):
    """clr: gap between spigot and body bore; bead: how far the snap bead reaches into the groove"""
    t = loft(outer_sec(X_TAIL, Y_N), outer_sec(X_R, Y_N, shrink=1.0))
    spig = loft(inner_sec(45.1, Y_N + W, -clr), inner_sec(X_TAIL + 0.01, Y_N + W, -clr))
    bore = loft(inner_sec(45.0, Y_N + W, -clr - wall), inner_sec(X_TAIL + 0.1, Y_N + W, -clr - wall))
    def bead_ring(h):     # 45-deg flanks, peak 45.7..45.8 = flat bottom of the body groove
        a0, a1 = 45.7 - (h + clr) - 0.02, 45.8 + (h + clr) + 0.02
        return (loft(inner_sec(a0, Y_N + W, -clr), inner_sec(45.7 - 0.02, Y_N + W, h))
                .union(loft(inner_sec(45.7 - 0.02, Y_N + W, h), inner_sec(45.8 + 0.02, Y_N + W, h)))
                .union(loft(inner_sec(45.8 + 0.02, Y_N + W, h), inner_sec(a1, Y_N + W, -clr))))
    # full-height bead on the four flat sides (they flex like beams between the corners), low bead on the corners
    sides = (box(40, 50, Y_N + W + 2.0, Y_B - W - 2.0, -9, 12).union(box(40, 50, -9, 30, Z_B + W + 2.0, Z_T - W - 2.0)))
    b = bead_ring(bead).intersect(sides).union(bead_ring(0.05))
    t = t.union(spig.union(b).cut(bore))
    return t
tail = make_tail(0.05, 0.30)
tail_loose = make_tail(0.10, 0.20)

# ---------------- SLED: board screwed on top, camera taped to its bulkhead, screwed to the body ----------------
BH = [(8.6, 15.2), (43.9, 11.9)]                  # board NPTH holes (dia 1.6)
SB, ST = -3.27, 3.35                              # flat print face / board seat
beam = box(-2.0, 43.8, 16.3, Y_B - W - CLR, SB, ST)
blk = box(2.6, 6.3, 13.0, Y_B - W - CLR, SB, ST)
arm = box(42.8, 45.0, 10.6, 16.5, SB, ST)
boss1 = cq.Workplane().circle(1.5).extrude(ST - SB).translate((BH[0][0], BH[0][1], SB))
shr = nose_inner(CLR)
bulk = shr.intersect(box(SEAT, -2.0, CAMC[0] - 4.9, 30, SB, 12))       # front side left open for the flex
sled = beam.union(blk).union(arm).union(boss1)
sled = sled.cut(cq.Workplane('YZ').polyline([(17.15, SB - 0.1), (Y_B, SB - 0.1), (Y_B, SB + 0.75)]).close().extrude(60).translate((-5, 0, 0)))
sled = sled.intersect(shr.union(box(X_SPLIT, 50, -9, 30, -9, 12)))      # stay inside the lid for x < -1
sled = sled.union(bulk)
for (x, y) in BH:
    sled = sled.cut(zcyl(x, y, PILOT, ST - 2.6, ST + 0.1))
SCR_BACK = [(4.4, 0.0), (43.0, 0.2)]
for (x, z) in SCR_BACK:
    sled = sled.cut(ycyl(x, z, PILOT, Y_B - W - CLR - 2.4, Y_B))
    body = body.cut(ycyl(x, z, CLEAR, Y_B - W - 0.5, Y_B + 1)).cut(ycyl(x, z, HEAD_D / 2, Y_B - 0.4, Y_B + 1))
sled = sled.cut(ycyl(XS, CAMC[1], PILOT, 14.6, 18.5)).cut(zcyl(XS, CAMC[0], PILOT, SB - 1, -0.6))

for name, p in (('body', body), ('nose', nose), ('tail', tail), ('tail_loose', tail_loose), ('sled', sled)):
    cq.exporters.export(p, f'{OUT}/{name}.step')
    cq.exporters.export(p, f'{OUT}/{name}.stl', tolerance=0.02, angularTolerance=0.1)
    print(name, p.val().isValid(), round(p.val().Volume(), 1))

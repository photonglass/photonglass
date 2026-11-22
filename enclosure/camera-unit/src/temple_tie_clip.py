# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright (C) OTON GLASS Inc.
"""Zip-tie attachment for the OG19 camera unit v6 (body coordinate frame).
Top: dovetail shoe on the body's rail (rail x 4..42), slid on from the lens end; closed -x end seats on the rail's
45-deg ramp, a sprung tongue's barb drops behind the rail's +x end.
Bottom: 45-deg V-saddle along x that centres any temple 3..7 mm tall, and two tunnels across (y) for zip ties
that wrap the temple. Printed as modelled (+z up, saddle face on the bed): no supports.
usage: tie_clip.py OUTDIR [TIE_W TIE_T]
"""
import sys, os
import cadquery as cq

OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
TIE_W = float(sys.argv[2]) if len(sys.argv) > 2 else 2.5
TIE_T = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
CLR = 0.15; YC = 11.5; Z_FACE = -4.8
def box(x0, x1, y0, y1, z0, z1): return cq.Workplane().box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))

X0, X1 = 4.0, 44.0
ZS_TOP, ZS_SLOT = Z_FACE - 0.05, -6.0 - CLR
TUN_H, TUN_W = TIE_T + 0.3, TIE_W + 0.5
ZT1 = ZS_SLOT - 0.6                    # tunnel roof (0.6 under the dovetail slot floor)
ZT0 = ZT1 - TUN_H                      # tunnel floor = saddle top
SAD_D = 1.5                            # saddle depth (45-deg flanks, 3 mm flat top)
Z0 = ZT0 - SAD_D                       # bed face
YS0, YS1 = 6.0, 17.0

shoe = box(X0, X1, YS0, YS1, Z0, ZS_TOP).edges('|X').edges('<Z').chamfer(0.4)
slot = (cq.Workplane('YZ').polyline([(8.5 - CLR, ZS_TOP + 0.1), (14.5 + CLR, ZS_TOP + 0.1), (14.5 + CLR, Z_FACE),
                                     (15.2 + CLR, ZS_SLOT), (7.8 - CLR, ZS_SLOT), (8.5 - CLR, Z_FACE)]).close()
        .extrude(X1 - X0 + 2).translate((X0 - 1, 0, 0)))
shoe = shoe.cut(slot)
wedge = (cq.Workplane('XZ').polyline([(X0, -5.01), (X0, ZS_SLOT - 0.05), (5.19, ZS_SLOT - 0.05)]).close()
         .extrude(-(YS1 - YS0)).translate((0, YS0, 0)))
shoe = shoe.union(wedge.intersect(box(X0, X1, YS0, YS1, Z0, ZS_TOP)))
# sprung tongue (root at the -x end, free at the +x end); open underneath so it can be pressed to release
# sized for a 0.4 mm nozzle: slits 0.8 (= 2 lines), tongue 1.0 thick, barb 0.6 tall (4-5 layers)
TG = (33.0, X1, 9.0, 14.0); SLIT, TONGUE_T, BARB_H = 0.8, 1.0, 0.6
shoe = shoe.cut(box(TG[0] + SLIT, X1 + 1, TG[2] - SLIT, TG[2], Z0 - 1, ZS_SLOT + 0.01))
shoe = shoe.cut(box(TG[0] + SLIT, X1 + 1, TG[3], TG[3] + SLIT, Z0 - 1, ZS_SLOT + 0.01))
shoe = shoe.cut(box(TG[0] + SLIT, X1 + 1, TG[2], TG[3], Z0 - 1, ZS_SLOT - TONGUE_T))
barb = (cq.Workplane('XZ').polyline([(42.2, ZS_SLOT - 0.01), (42.2, ZS_SLOT + BARB_H), (42.8, ZS_SLOT + BARB_H), (42.8 + BARB_H + 0.2, ZS_SLOT - 0.01)])
        .close().extrude(-(TG[3] - TG[2])).translate((0, TG[2], 0)))
shoe = shoe.union(barb)
# V-saddle along x
sad = (cq.Workplane('YZ').polyline([(YC - 1.5 - SAD_D - 0.01, Z0 - 0.01), (YC + 1.5 + SAD_D + 0.01, Z0 - 0.01),
                                    (YC + 1.5, ZT0), (YC - 1.5, ZT0)]).close().extrude(X1 - X0 + 2).translate((X0 - 1, 0, 0)))
shoe = shoe.cut(sad)
# tie tunnels across the part (they open into the saddle's flat top, so the tie bears on the temple)
for xc in (9.5, 28.5):
    t = box(xc - TUN_W / 2, xc + TUN_W / 2, YS0 - 1, YS1 + 1, ZT0 - 0.01, ZT1)
    shoe = shoe.cut(t)
    for ye, s in ((YS0, 1), (YS1, -1)):                      # 45-deg lead-in at both mouths
        lead = (cq.Workplane('XY').polyline([(xc - TUN_W / 2 - 0.5, ye), (xc + TUN_W / 2 + 0.5, ye),
                                             (xc + TUN_W / 2, ye + s * 0.5), (xc - TUN_W / 2, ye + s * 0.5)]).close()
                .extrude(ZT1 - ZT0 + 0.01).translate((0, 0, ZT0 - 0.005)))
        shoe = shoe.cut(lead)
NAME = 'tie_clip'
cq.exporters.export(shoe, f'{OUT}/{NAME}.step')
cq.exporters.export(shoe, f'{OUT}/{NAME}.stl', tolerance=0.02, angularTolerance=0.1)
print(NAME, shoe.val().isValid(), round(shoe.val().Volume(), 1), 'z', round(Z0, 2), '..', ZS_TOP, 'tunnel', round(ZT0, 2), round(ZT1, 2))

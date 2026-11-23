# SPDX-License-Identifier: CERN-OHL-S-2.0
# Copyright (C) OTON GLASS Inc.
"""Eagle .brd (2-layer) -> Gerber RS-274X + Excellon for JLCPCB.

Copper pours are computed here (Eagle semantics: isolate = design clearance,
orphans removed, thermals on pads, solid vias, tRestrict/bRestrict honoured).

The gerber zips in hardware/*/gerber/ are made with this script.
usage:  pip install shapely Hershey-Fonts
        python hardware/tools/gerbgen.py hardware/main-board/eagle/OG19AWv2_main.brd OUTDIR/files OG19AWv2_main
        (writes the 11 files to OUTDIR/files and OUTDIR/OG19AWv2_main_gerber.zip)
"""
import math, re, sys, os, zipfile, xml.etree.ElementTree as ET
from shapely.geometry import (Point, LineString, Polygon, MultiPolygon, box, GeometryCollection)
from shapely.ops import unary_union, polygonize, split
from shapely.geometry.polygon import orient
from shapely import affinity

ARC_STEP = math.radians(4)
CLR = 0.1524          # mdWireWire / mdWirePad (6 mil)
HOLE_CLR = 0.508      # copper to NPTH / board edge (mdCopperDimension 20 mil)
THERM_GAP = 0.254     # slThermalIsolate 10 mil
THERM_W = 0.3
MIN_SILK = 0.12

def mil(v):
    v = str(v)
    if v.endswith('mil'): return float(v[:-3]) * 0.0254
    if v.endswith('mm'): return float(v[:-2])
    return float(v)

def parse_rot(s):
    s = s or 'R0'
    m = re.match(r'(S?)(M?)R([\d.]+)', s)
    return bool(m.group(1)), bool(m.group(2)), float(m.group(3))

def arc_pts(x1, y1, x2, y2, curve):
    c = math.radians(float(curve))
    if abs(c) < 1e-9: return [(x1, y1), (x2, y2)]
    dx, dy = x2 - x1, y2 - y1
    d = math.hypot(dx, dy)
    r = d / (2 * math.sin(abs(c) / 2))
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    h = math.sqrt(max(r * r - (d / 2) ** 2, 0))
    nx, ny = -dy / d, dx / d
    s = 1 if (c > 0) == (abs(c) < math.pi) else -1
    cx, cy = mx + s * nx * h, my + s * ny * h
    a1 = math.atan2(y1 - cy, x1 - cx)
    n = max(2, int(abs(c) / ARC_STEP) + 1)
    pts = [(cx + r * math.cos(a1 + c * i / n), cy + r * math.sin(a1 + c * i / n)) for i in range(n + 1)]
    pts[0], pts[-1] = (x1, y1), (x2, y2)
    return pts

def path_from_vertices(vs):
    pts = []
    for i, v in enumerate(vs):
        nv = vs[(i + 1) % len(vs)]
        seg = arc_pts(float(v.get('x')), float(v.get('y')), float(nv.get('x')), float(nv.get('y')), v.get('curve') or 0)
        pts.extend(seg[:-1])
    return pts

class Xf:
    """Element transform: rotate, then mirror X (Eagle semantics), then translate."""
    def __init__(self, x=0, y=0, rot=None):
        self.x, self.y = x, y
        self.spin, self.mir, self.ang = parse_rot(rot)
    def pt(self, x, y):
        a = math.radians(self.ang)
        x, y = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
        if self.mir: x = -x
        return self.x + x, self.y + y
    def geom(self, g):
        g = affinity.rotate(g, self.ang, origin=(0, 0))
        if self.mir: g = affinity.scale(g, -1, 1, origin=(0, 0))
        return affinity.translate(g, self.x, self.y)

ID = Xf()

def fracture(p):
    """Split a polygon with holes into hole-free polygons (dark-only Gerber regions)."""
    if p.is_empty: return []
    if not p.interiors: return [p]
    hx = p.interiors[0].centroid.x
    b = p.bounds
    cutter = LineString([(hx, b[1] - 1), (hx, b[3] + 1)])
    out = []
    for q in split(p, cutter).geoms:
        if isinstance(q, Polygon): out += fracture(q)
    return out

# ------------------------------------------------------------------ text
_font = None
def font():
    global _font
    if _font is None:
        from HersheyFonts import HersheyFonts
        _font = HersheyFonts(); _font.load_default_font('futural')
    return _font

def text_geom(s, x, y, size, ratio, rot, align, mirror_extra=False):
    spin, mir, ang = parse_rot(rot)
    mir = mir ^ mirror_extra
    w = max(size * (ratio if ratio is not None else 8) / 100, MIN_SILK)
    cap = max(size - w, size * 0.6)
    k = cap / 21.0
    lines = s.split('\n')
    pitch = size * 1.5
    strokes, widths = [], []
    for li, line in enumerate(lines):
        segs = list(font().lines_for_text(line))
        xs = [p[0] for sgm in segs for p in sgm] or [0]
        widths.append((max(xs) - min(xs)) * k if segs else 0)
        oy = (len(lines) - 1 - li) * pitch
        for (ax, ay), (bx, by) in segs:
            strokes.append(((ax * k, (9 - ay) * k + oy), (bx * k, (9 - by) * k + oy)))
    W = max(widths) if widths else 0
    H = cap + (len(lines) - 1) * pitch
    al = (align or 'bottom-left')
    if al == 'center': al = 'center-center'
    va, ha = al.split('-')
    if not spin and 90 < (ang % 360) <= 270:
        ang = (ang - 180) % 360
        va = {'bottom': 'top', 'top': 'bottom', 'center': 'center'}[va]
        ha = {'left': 'right', 'right': 'left', 'center': 'center'}[ha]
    ox = {'left': 0, 'center': -W / 2, 'right': -W}[ha]
    oy = {'bottom': 0, 'center': -H / 2, 'top': -H}[va]
    gs = [LineString([(a[0] + ox, a[1] + oy), (b[0] + ox, b[1] + oy)]).buffer(w / 2) for a, b in strokes]
    g = unary_union(gs) if gs else GeometryCollection()
    g = affinity.rotate(g, ang, origin=(0, 0))
    if mir: g = affinity.scale(g, -1, 1, origin=(0, 0))
    return affinity.translate(g, x, y)

# ------------------------------------------------------------------ board
TOP_SILK, BOT_SILK = {'21', '25'}, {'22', '26'}
FLIP = {'1': '16', '16': '1', '21': '22', '22': '21', '25': '26', '26': '25', '29': '30', '30': '29',
        '31': '32', '32': '31', '41': '42', '42': '41', '39': '40', '40': '39', '51': '52', '52': '51'}

class Gen:
    def __init__(self, path):
        self.r = ET.parse(path).getroot()
        dr = {p.get('name'): p.get('value') for p in self.r.iter('param')}
        self.rv_pad, self.rmin_pad, self.rmax_pad = float(dr['rvPadTop']), mil(dr['rlMinPadTop']), mil(dr['rlMaxPadTop'])
        self.rv_via, self.rmin_via, self.rmax_via = float(dr['rvViaOuter']), mil(dr['rlMinViaOuter']), mil(dr['rlMaxViaOuter'])
        self.via_stop_limit = mil(dr['mlViaStopLimit'])
        self.copper = {'1': [], '16': []}     # (net, geom, kind)
        self.silk = {'t': [], 'b': []}
        self.mask = {'t': [], 'b': []}
        self.paste = {'t': [], 'b': []}
        self.restrict = {'1': [], '16': []}
        self.pth, self.npth = [], []
        self.outline_lines = []
        self.polys = []
        self.build()

    def ring(self, drill, rv, mn, mx):
        return min(max(drill * rv, mn), mx)

    def gfx(self, el, xf, layer_map):
        lay = el.get('layer')
        if xf.mir: lay = FLIP.get(lay, lay)
        side = 't' if lay in TOP_SILK else 'b' if lay in BOT_SILK else None
        if side is None and not (el.tag == 'polygon' and lay in ('41', '42')):
            return None
        tag = el.tag
        if tag == 'wire':
            if float(el.get('width')) == 0 and xf is ID:
                return None  # zero-width drafting guide lines (not printable)
            w = max(float(el.get('width')), MIN_SILK)
            pts = arc_pts(float(el.get('x1')), float(el.get('y1')), float(el.get('x2')), float(el.get('y2')), el.get('curve') or 0)
            g = LineString(pts).buffer(w / 2)
        elif tag == 'circle':
            x, y, r, w = float(el.get('x')), float(el.get('y')), float(el.get('radius')), float(el.get('width'))
            g = Point(x, y).buffer(r) if w == 0 else Point(x, y).buffer(r + w / 2).difference(Point(x, y).buffer(max(r - w / 2, 0)))
        elif tag == 'rectangle':
            x1, y1, x2, y2 = (float(el.get(k)) for k in ('x1', 'y1', 'x2', 'y2'))
            g = box(min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2))
            _, _, a = parse_rot(el.get('rot'))
            if a: g = affinity.rotate(g, a, origin='center')
        elif tag == 'polygon':
            pts = path_from_vertices(el.findall('vertex'))
            g = Polygon(pts).buffer(float(el.get('width') or 0) / 2)
        else:
            return None
        g = xf.geom(g)
        if lay in ('41', '42'):
            self.restrict['1' if lay == '41' else '16'].append(g); return None
        self.silk[side].append(g)

    def text(self, s, x, y, el, layer, extra_mirror=False):
        side = 't' if layer in TOP_SILK else 'b' if layer in BOT_SILK else None
        if side is None or not s: return
        g = text_geom(s, x, y, float(el.get('size')), float(el.get('ratio')) if el.get('ratio') else None,
                      el.get('rot'), el.get('align'), extra_mirror)
        self.silk[side].append(g)

    def build(self):
        r = self.r
        board = r.find('drawing/board')
        pkgs = {(lib.get('name'), p.get('name')): p for lib in board.find('libraries') for p in lib.iter('package')}
        padnet = {}
        for sig in r.iter('signal'):
            for c in sig.iter('contactref'):
                padnet[(c.get('element'), c.get('pad'))] = sig.get('name')
        for el in board.find('plain'):
            lay = el.get('layer')
            if el.tag == 'wire' and lay == '20':
                self.outline_lines.append(arc_pts(float(el.get('x1')), float(el.get('y1')), float(el.get('x2')), float(el.get('y2')), el.get('curve') or 0))
            elif el.tag == 'hole':
                self.npth.append((float(el.get('x')), float(el.get('y')), float(el.get('drill'))))
            elif el.tag == 'text':
                self.text(el.text, float(el.get('x')), float(el.get('y')), el, lay)
            else:
                self.gfx(el, ID, None)
        for e in board.find('elements'):
            pk = pkgs[(e.get('library'), e.get('package'))]
            xf = Xf(float(e.get('x')), float(e.get('y')), e.get('rot'))
            attrs = {a.get('name'): a for a in e.findall('attribute')}
            for el in pk:
                if el.tag == 'smd':
                    dx, dy = float(el.get('dx')), float(el.get('dy'))
                    g = box(-dx / 2, -dy / 2, dx / 2, dy / 2)
                    _, _, pa = parse_rot(el.get('rot'))
                    g = affinity.translate(affinity.rotate(g, pa, origin=(0, 0)), float(el.get('x')), float(el.get('y')))
                    g = xf.geom(g)
                    lay = el.get('layer', '1')
                    if xf.mir: lay = FLIP[lay]
                    net = padnet.get((e.get('name'), el.get('name')))
                    self.copper[lay].append((net, g, 'smd'))
                    side = 't' if lay == '1' else 'b'
                    if el.get('stop') != 'no': self.mask[side].append(g)
                    if el.get('cream') != 'no': self.paste[side].append(g)
                elif el.tag == 'pad':
                    d = float(el.get('drill'))
                    dia = max(float(el.get('diameter') or 0), d + 2 * self.ring(d, self.rv_pad, self.rmin_pad, self.rmax_pad))
                    shape = el.get('shape') or 'round'
                    if shape == 'square':
                        g = box(-dia / 2, -dia / 2, dia / 2, dia / 2)
                    elif shape == 'octagon':
                        R = dia / 2 / math.cos(math.radians(22.5))
                        g = Polygon([(R * math.cos(math.radians(22.5 + 45 * i)), R * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)])
                    elif shape == 'long':
                        g = LineString([(-dia / 2, 0), (dia / 2, 0)]).buffer(dia / 2)
                    else:
                        g = Point(0, 0).buffer(dia / 2)
                    _, _, pa = parse_rot(el.get('rot'))
                    g = affinity.translate(affinity.rotate(g, pa, origin=(0, 0)), float(el.get('x')), float(el.get('y')))
                    g = xf.geom(g)
                    net = padnet.get((e.get('name'), el.get('name')))
                    for lay in ('1', '16'): self.copper[lay].append((net, g, 'pad'))
                    for s in ('t', 'b'): self.mask[s].append(g)
                    x, y = xf.pt(float(el.get('x')), float(el.get('y')))
                    self.pth.append((x, y, d))
                elif el.tag == 'hole':
                    x, y = xf.pt(float(el.get('x')), float(el.get('y')))
                    self.npth.append((x, y, float(el.get('drill'))))
                    for s in ('t', 'b'): self.mask[s].append(Point(x, y).buffer(float(el.get('drill')) / 2))
                elif el.tag == 'text':
                    t = el.text or ''
                    key = t[1:].upper() if t.startswith('>') else None
                    if key in ('NAME', 'VALUE') and key in attrs:
                        continue
                    s = e.get('name') if key == 'NAME' else (e.get('value') or '') if key == 'VALUE' else t
                    lay = el.get('layer')
                    if xf.mir: lay = FLIP.get(lay, lay)
                    x, y = xf.pt(float(el.get('x')), float(el.get('y')))
                    sp, tm, ta = parse_rot(el.get('rot'))
                    tot = ta + xf.ang
                    fake = ET.Element('text', size=el.get('size'), rot=('S' if sp else '') + ('M' if (tm ^ xf.mir) else '') + f'R{tot % 360:g}', align=el.get('align') or 'bottom-left')
                    if el.get('ratio'): fake.set('ratio', el.get('ratio'))
                    self.text(s, x, y, fake, lay)
                else:
                    self.gfx(el, xf, None)
            for name, a in attrs.items():
                if a.get('display') == 'off' or a.get('x') is None: continue
                if name == 'NAME': s = e.get('name')
                elif name == 'VALUE': s = e.get('value') or ''
                else: s = a.get('value') or ''
                disp = a.get('display') or 'value'
                if disp == 'name': s = name
                elif disp == 'both': s = f'{name}={s}'
                self.text(s, float(a.get('x')), float(a.get('y')), a, a.get('layer'))
        for sig in r.iter('signal'):
            net = sig.get('name')
            for w in sig.findall('wire'):
                lay = w.get('layer')
                if lay not in ('1', '16'): continue
                pts = arc_pts(float(w.get('x1')), float(w.get('y1')), float(w.get('x2')), float(w.get('y2')), w.get('curve') or 0)
                self.copper[lay].append((net, LineString(pts).buffer(float(w.get('width')) / 2), 'wire'))
            for v in sig.findall('via'):
                d = float(v.get('drill'))
                dia = max(float(v.get('diameter') or 0), d + 2 * self.ring(d, self.rv_via, self.rmin_via, self.rmax_via))
                x, y = float(v.get('x')), float(v.get('y'))
                g = Point(x, y).buffer(dia / 2)
                for lay in ('1', '16'): self.copper[lay].append((net, g, 'via'))
                self.pth.append((x, y, d))
                if d >= self.via_stop_limit:
                    for s in ('t', 'b'): self.mask[s].append(g)
            for p in sig.findall('polygon'):
                self.polys.append((net, p))
        self.board = unary_union([Polygon(p) for p in polygonize(unary_union([LineString(l) for l in self.outline_lines]))])

    def pour(self):
        inner = self.board.buffer(-HOLE_CLR)
        holes = unary_union([Point(x, y).buffer(d / 2 + HOLE_CLR) for x, y, d in self.npth]) if self.npth else GeometryCollection()
        done = {'1': [], '16': []}
        for net, p in self.polys:
            lay = p.get('layer')
            w = float(p.get('width') or 0)
            iso = max(CLR, float(p.get('isolate') or 0))
            area = Polygon(path_from_vertices(p.findall('vertex'))).buffer(w / 2).intersection(inner)
            other = [g for n, g, k in self.copper[lay] if n != net] + [g for n, g in done[lay] if n != net]
            obst = unary_union([g.buffer(iso) for g in other] + [holes] + self.restrict[lay])
            base = area.difference(obst)
            same = [(g, k) for n, g, k in self.copper[lay] if n == net]
            if p.get('thermals') != 'no':
                cuts = []
                for g, k in same:
                    if k not in ('smd', 'pad'): continue
                    ring = g.buffer(THERM_GAP).difference(g)
                    c = g.centroid; b = g.bounds; L = max(b[2] - b[0], b[3] - b[1]) + 2 * THERM_GAP + 1
                    sp = unary_union([box(c.x - L, c.y - THERM_W / 2, c.x + L, c.y + THERM_W / 2),
                                      box(c.x - THERM_W / 2, c.y - L, c.x + THERM_W / 2, c.y + L)])
                    cuts.append(ring.difference(sp))
                base = base.difference(unary_union(cuts))
            base = base.buffer(-w / 2).buffer(w / 2) if w > 0 else base
            base = base.buffer(0)
            if p.get('orphans') != 'yes':
                anchors = unary_union([g for g, k in same])
                parts = list(base.geoms) if hasattr(base, 'geoms') else [base]
                base = unary_union([q for q in parts if not q.is_empty and q.intersects(anchors)])
            done[lay].append((net, base))
        self.pours = done
        for lay in ('1', '16'):
            for net, g in done[lay]:
                self.copper[lay].append((net, g, 'pour'))

    def check(self):
        report = []
        for lay in ('1', '16'):
            by = {}
            for n, g, k in self.copper[lay]:
                by.setdefault(n, []).append(g)
            nets = {n: unary_union(gs) for n, gs in by.items()}
            names = [n for n in nets if n is not None]
            for i, a in enumerate(names):
                for b in names[i + 1:]:
                    d = nets[a].distance(nets[b])
                    if d < CLR - 0.005: report.append(f'L{lay} clearance {a}-{b} {d:.3f}mm')
        unconnected = []
        nets = {n for lay in self.copper for n, g, k in self.copper[lay] if n}
        for n in sorted(nets):
            comps = []
            for lay in ('1', '16'):
                u = unary_union([g for nn, g, k in self.copper[lay] if nn == n])
                for q in (u.geoms if hasattr(u, 'geoms') else [u]):
                    if not q.is_empty: comps.append((lay, q))
            parent = list(range(len(comps)))
            def find(i):
                while parent[i] != i: parent[i] = parent[parent[i]]; i = parent[i]
                return i
            bridges = [g for nn, g, k in self.copper['1'] if nn == n and k in ('pad', 'via')]
            for b in bridges:
                c = b.centroid
                idx = [i for i, (lay, q) in enumerate(comps) if q.contains(c)]
                for i in idx[1:]: parent[find(i)] = find(idx[0])
            padroots = set()
            for lay in ('1', '16'):
                for nn, g, k in self.copper[lay]:
                    if nn == n and k in ('smd', 'pad'):
                        c = g.representative_point()
                        for i, (l2, q) in enumerate(comps):
                            if l2 == lay and q.contains(c): padroots.add(find(i))
            if len(padroots) > 1: unconnected.append((n, len(padroots)))
        return report, unconnected

    @staticmethod
    def fmt(v): return f'{int(round(v * 1e6))}'

    def region_gerber(self, geom, function, extra=''):
        polys = []
        for g in (geom.geoms if hasattr(geom, 'geoms') else [geom]):
            if isinstance(g, Polygon) and not g.is_empty: polys.append(g)
            elif isinstance(g, MultiPolygon): polys.extend(g.geoms)
        out = ['%FSLAX46Y46*%', '%MOMM*%', f'%TF.FileFunction,{function}*%', '%TF.GenerationSoftware,claude-eagle2gerber,1.0*%',
               '%ADD10C,0.100*%', 'G01*', '%LPD*%']
        for p in polys:
            for q in fracture(p):
                out += self._region(orient(q, 1.0).exterior.coords)
        out.append(extra)
        out.append('M02*')
        return '\n'.join(l for l in out if l) + '\n'

    def _region(self, coords):
        c = list(coords)
        o = ['G36*', f'X{self.fmt(c[0][0])}Y{self.fmt(c[0][1])}D02*']
        o += [f'X{self.fmt(x)}Y{self.fmt(y)}D01*' for x, y in c[1:]]
        o.append('G37*')
        return o

    def outline_gerber(self):
        out = ['%FSLAX46Y46*%', '%MOMM*%', '%TF.FileFunction,Profile,NP*%', '%ADD10C,0.100*%', 'D10*', 'G01*']
        for l in self.outline_lines:
            out.append(f'X{self.fmt(l[0][0])}Y{self.fmt(l[0][1])}D02*')
            out += [f'X{self.fmt(x)}Y{self.fmt(y)}D01*' for x, y in l[1:]]
        out.append('M02*')
        return '\n'.join(out) + '\n'

    def drill(self, items, plated):
        tools = sorted({round(d, 3) for _, _, d in items})
        out = ['M48', f'; {"PTH" if plated else "NPTH"} drill file', 'METRIC,TZ',
               f'; #@! TF.FileFunction,{"Plated" if plated else "NonPlated"},1,2,{"PTH" if plated else "NPTH"}']
        for i, d in enumerate(tools, 1): out.append(f'T{i}C{d:.3f}')
        out += ['%', 'G90', 'G05']
        for i, d in enumerate(tools, 1):
            out.append(f'T{i}')
            for x, y, dd in items:
                if round(dd, 3) == d: out.append(f'X{x:.3f}Y{y:.3f}')
        out.append('M30')
        return '\n'.join(out) + '\n'

    def write(self, outdir, base):
        os.makedirs(outdir, exist_ok=True)
        files = {}
        cu = {lay: unary_union([g for n, g, k in self.copper[lay]]) for lay in ('1', '16')}
        files[f'{base}.GTL'] = self.region_gerber(cu['1'], 'Copper,L1,Top')
        files[f'{base}.GBL'] = self.region_gerber(cu['16'], 'Copper,L2,Bot')
        files[f'{base}.GTS'] = self.region_gerber(unary_union(self.mask['t']), 'Soldermask,Top')
        files[f'{base}.GBS'] = self.region_gerber(unary_union(self.mask['b']), 'Soldermask,Bot')
        files[f'{base}.GTP'] = self.region_gerber(unary_union(self.paste['t']), 'Paste,Top')
        files[f'{base}.GBP'] = self.region_gerber(unary_union(self.paste['b']), 'Paste,Bot')
        for s, ext, fn in (('t', 'GTO', 'Legend,Top'), ('b', 'GBO', 'Legend,Bot')):
            g = unary_union(self.silk[s]).intersection(self.board)
            g = g.difference(unary_union(self.mask[s]).buffer(0.1))
            files[f'{base}.{ext}'] = self.region_gerber(g, fn)
        files[f'{base}.GKO'] = self.outline_gerber()
        files[f'{base}-PTH.DRL'] = self.drill(self.pth, True)
        files[f'{base}-NPTH.DRL'] = self.drill(self.npth, False)
        for fn, txt in files.items():
            open(os.path.join(outdir, fn), 'w').write(txt)
        zp = os.path.join(os.path.dirname(outdir.rstrip('/')), f'{base}_gerber.zip')
        with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
            for fn in files: z.write(os.path.join(outdir, fn), fn)
        return zp, files

if __name__ == '__main__':
    brd, outdir, base = sys.argv[1:4]
    g = Gen(brd)
    g.pour()
    rep, unc = g.check()
    print('board bounds', [round(v, 2) for v in g.board.bounds], 'PTH', len(g.pth), 'NPTH', len(g.npth))
    print('clearance issues:', rep)
    print('unconnected nets:', unc)
    zp, files = g.write(outdir, base)
    print('zip', zp)

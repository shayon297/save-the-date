"""Botanical line art for the save-the-date, restricted to the floral brief's
florist's selection: cream garden roses and spray roses, peony, olive / bay laurel foliage.
Draped fabric at the top corners echoes the chuppah."""
import math, random, sys

def f(v): return f"{v:.1f}".rstrip("0").rstrip(".")

def rot(x, y, a):
    c, s = math.cos(a), math.sin(a)
    return x * c - y * s, x * s + y * c


class Flora:
    def __init__(self, seed):
        self.r = random.Random(seed)
        self.out = []

    def path(self, d, cls): self.out.append(f'<path class="{cls}" d="{d}"/>')

    # ---------- petals ----------
    def petal(self, cx, cy, ang, r0, L, W, tip="rose"):
        """Closed petal lobe from base radius r0 outward. tip: rose (soft point / notch),
        peony (ruffled 3-bump), anemone (rounded)."""
        r = self.r
        L *= r.uniform(0.94, 1.06); W *= r.uniform(0.92, 1.08)
        def P(x, y):
            X, Y = rot(x, y, ang); return (cx + X, cy + Y)
        b = P(r0, 0)
        d = f"M{f(b[0])} {f(b[1])}"
        c1 = P(r0 + 0.2 * L, -0.7 * W); c2 = P(r0 + 0.78 * L, -0.72 * W); tl = P(r0 + 0.94 * L, -0.34 * W)
        d += f"C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(tl[0])} {f(tl[1])}"
        tr = P(r0 + 0.94 * L, 0.34 * W)
        if tip == "rose":      # two rolled corners with a shallow notch between
            a1 = P(r0 + 1.04 * L, -0.2 * W); m = P(r0 + 0.97 * L, 0); a2 = P(r0 + 1.04 * L, 0.2 * W)
            d += f"Q{f(a1[0])} {f(a1[1])} {f(m[0])} {f(m[1])}Q{f(a2[0])} {f(a2[1])} {f(tr[0])} {f(tr[1])}"
        elif tip == "peony":   # frilled edge
            n = 3
            for i in range(n):
                ya = -0.34 * W + 0.68 * W * i / n; yb = -0.34 * W + 0.68 * W * (i + 1) / n
                cp = P(r0 + L * (1.02 + 0.07 * r.random()), (ya + yb) / 2)
                e = P(r0 + (0.9 if i < n - 1 else 0.94) * L, yb)
                d += f"Q{f(cp[0])} {f(cp[1])} {f(e[0])} {f(e[1])}"
        else:                  # anemone: single rounded tip
            cp = P(r0 + 1.12 * L, 0)
            d += f"Q{f(cp[0])} {f(cp[1])} {f(tr[0])} {f(tr[1])}"
        c3 = P(r0 + 0.78 * L, 0.72 * W); c4 = P(r0 + 0.2 * L, 0.7 * W)
        d += f"C{f(c3[0])} {f(c3[1])} {f(c4[0])} {f(c4[1])} {f(b[0])} {f(b[1])}Z"
        self.path(d, "p")
        if L > 16:
            s0 = P(r0 + 0.1 * L, 0); s1 = P(r0 + 0.5 * L, r.uniform(-0.1, 0.1) * W); s2 = P(r0 + 0.82 * L, r.uniform(-0.08, 0.08) * W)
            self.path(f"M{f(s0[0])} {f(s0[1])}Q{f(s1[0])} {f(s1[1])} {f(s2[0])} {f(s2[1])}", "v")

    # ---------- blooms ----------
    def rose(self, cx, cy, R):
        """Garden rose seen from above: two rings of broad cupped petals around a furled spiral."""
        r = self.r
        a0 = r.uniform(0, math.tau)
        for i in range(6):
            self.petal(cx, cy, a0 + i * math.tau / 6 + r.uniform(-0.1, 0.1), 0.34 * R, 0.66 * R, 0.78 * R, "rose")
        for i in range(5):
            self.petal(cx, cy, a0 + math.pi / 5 + i * math.tau / 5 + r.uniform(-0.1, 0.1), 0.18 * R, 0.5 * R, 0.62 * R, "rose")
        # furled centre: wrapped petals as overlapping cupped arcs, tightening inward
        base = r.uniform(0, math.tau)
        for k in range(5):
            rad = 0.34 * R * (1 - k * 0.17)
            a = base + k * 1.9
            span = 3.3 - k * 0.25
            p0 = (cx + rad * math.cos(a), cy + rad * math.sin(a))
            m1 = (cx + rad * 1.25 * math.cos(a + span * 0.33), cy + rad * 1.25 * math.sin(a + span * 0.33))
            m2 = (cx + rad * 1.25 * math.cos(a + span * 0.66), cy + rad * 1.25 * math.sin(a + span * 0.66))
            p1 = (cx + rad * 0.85 * math.cos(a + span), cy + rad * 0.85 * math.sin(a + span))
            self.path(f"M{f(p0[0])} {f(p0[1])}C{f(m1[0])} {f(m1[1])} {f(m2[0])} {f(m2[1])} {f(p1[0])} {f(p1[1])}", "l")
        # tight spiral core
        d = ""; n = 22
        for i in range(n + 1):
            t = i / n
            rad = 0.02 * R + 0.1 * R * t
            a = base + t * 2.2 * math.tau
            x, y = cx + rad * math.cos(a), cy + rad * math.sin(a)
            d += ("M" if i == 0 else "L") + f"{f(x)} {f(y)}"
        self.path(d, "l")

    def peony(self, cx, cy, R):
        """Loose, ruffled peony with a visible golden stamen centre."""
        r = self.r
        a0 = r.uniform(0, math.tau)
        for i in range(8):
            self.petal(cx, cy, a0 + i * math.tau / 8 + r.uniform(-0.12, 0.12), 0.3 * R, 0.68 * R, 0.8 * R, "peony")
        for i in range(6):
            self.petal(cx, cy, a0 + math.pi / 6 + i * math.tau / 6 + r.uniform(-0.12, 0.12), 0.14 * R, 0.48 * R, 0.62 * R, "peony")
        for i in range(16):
            a = r.uniform(0, math.tau); l = R * r.uniform(0.1, 0.22)
            x1, y1 = cx + 0.03 * R * math.cos(a), cy + 0.03 * R * math.sin(a)
            x2, y2 = cx + l * math.cos(a), cy + l * math.sin(a)
            self.path(f"M{f(x1)} {f(y1)}L{f(x2)} {f(y2)}", "g")
            self.out.append(f'<circle class="gd" cx="{f(x2)}" cy="{f(y2)}" r="1.1"/>')

    def anemone(self, cx, cy, R):
        """Anemone: rounded petals around a dark centre ringed with stamens."""
        r = self.r
        a0 = r.uniform(0, math.tau)
        for i in range(7):
            self.petal(cx, cy, a0 + i * math.tau / 7 + r.uniform(-0.08, 0.08), 0.14 * R, 0.8 * R, 0.66 * R, "anemone")
        self.out.append(f'<circle class="k" cx="{f(cx)}" cy="{f(cy)}" r="{f(0.15 * R)}"/>')
        for i in range(12):
            a = i * math.tau / 12 + r.uniform(-0.1, 0.1)
            self.out.append(f'<circle class="kd" cx="{f(cx + 0.25 * R * math.cos(a))}" cy="{f(cy + 0.25 * R * math.sin(a))}" r="1.1"/>')

    def spray_roses(self, cx, cy, ang, L):
        """Spray rose: a short branched stem carrying three small open roses and a bud."""
        def P(px, py):
            X, Y = rot(px, py, ang); return (cx + X, cy + Y)
        tips = [(0.9 * L, -0.42 * L), (1.0 * L, 0.08 * L), (0.62 * L, 0.5 * L), (0.36 * L, -0.3 * L)]
        for i, (tx, ty) in enumerate(tips):
            t = P(tx, ty); m = P(tx * 0.5, ty * 0.5 + (0.04 * L if i % 2 else -0.04 * L))
            self.path(f"M{f(cx)} {f(cy)}Q{f(m[0])} {f(m[1])} {f(t[0])} {f(t[1])}", "s2")
        for tx, ty, R in tips[0:3:1] and [(tips[0][0], tips[0][1], 0.3 * L), (tips[1][0], tips[1][1], 0.27 * L), (tips[2][0], tips[2][1], 0.24 * L)]:
            t = P(tx, ty); self.rose(t[0], t[1], R)
        t = P(*tips[3]); self.rosebud(t[0], t[1], ang - 1.1, 0.24 * L)
        s = P(0.3 * L, 0.06 * L)
        self.leaf_outline(s[0], s[1], ang + 1.3, 0.3 * L, 0.16 * L, serrate=True, veins=False)

    def rosebud(self, cx, cy, ang, L):
        """Rose bud: tight furled bud with five long sepals reaching past the tip."""
        r = self.r
        W = 0.4 * L
        def P(x, y):
            X, Y = rot(x, y, ang); return (cx + X, cy + Y)
        b = P(0, 0); t = P(L, 0)
        c1 = P(0.25 * L, -0.85 * W); c2 = P(0.8 * L, -0.55 * W); c3 = P(0.8 * L, 0.55 * W); c4 = P(0.25 * L, 0.85 * W)
        self.path(f"M{f(b[0])} {f(b[1])}C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(t[0])} {f(t[1])}C{f(c3[0])} {f(c3[1])} {f(c4[0])} {f(c4[1])} {f(b[0])} {f(b[1])}Z", "p")
        for k in (-0.3, 0.25):
            s0 = P(0.05 * L, 0); s1 = P(0.5 * L, k * W); s2 = P(0.92 * L, k * 0.4 * W)
            self.path(f"M{f(s0[0])} {f(s0[1])}Q{f(s1[0])} {f(s1[1])} {f(s2[0])} {f(s2[1])}", "v")
        # calyx cup + sepals
        for k in (-1.0, -0.4, 0.4, 1.0):
            s0 = P(0.02 * L, k * 0.35 * W); s1 = P(0.6 * L, k * 1.0 * W); s2 = P(1.15 * L, k * 0.9 * W)
            self.path(f"M{f(s0[0])} {f(s0[1])}Q{f(s1[0])} {f(s1[1])} {f(s2[0])} {f(s2[1])}", "l")
        s0 = P(0.05 * L, 0); s1 = P(0.7 * L, r.uniform(-0.1, 0.1) * W); s2 = P(1.2 * L, r.uniform(-0.15, 0.15) * W)
        self.path(f"M{f(s0[0])} {f(s0[1])}Q{f(s1[0])} {f(s1[1])} {f(s2[0])} {f(s2[1])}", "l")

    # ---------- foliage ----------
    def leaf_outline(self, x, y, ang, L, W, serrate=False, veins=True):
        r = self.r
        def P(px, py):
            X, Y = rot(px, py, ang); return (x + X, y + Y)
        b = P(0, 0); t = P(L, 0)
        if not serrate:
            c1 = P(0.22 * L, -0.55 * W); c2 = P(0.72 * L, -0.5 * W); c3 = P(0.72 * L, 0.5 * W); c4 = P(0.22 * L, 0.55 * W)
            d = f"M{f(b[0])} {f(b[1])}C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(t[0])} {f(t[1])}C{f(c3[0])} {f(c3[1])} {f(c4[0])} {f(c4[1])} {f(b[0])} {f(b[1])}Z"
        else:
            # ovate rose leaflet with a toothed margin: sample the smooth edge, add small teeth
            n = 7
            def edge(side):
                pts = []
                for i in range(1, n + 1):
                    u = i / (n + 1)
                    half = W * 0.55 * math.sin(math.pi * u ** 0.8) * (1.0 - 0.15 * u)
                    pts.append((u * L, side * half))
                return pts
            d = f"M{f(b[0])} {f(b[1])}"
            for (px, py) in edge(-1):
                tooth = P(px - 0.035 * L, py - 0.09 * W); e = P(px, py)
                d += f"Q{f(tooth[0])} {f(tooth[1])} {f(e[0])} {f(e[1])}"
            d += f"L{f(t[0])} {f(t[1])}"
            for (px, py) in reversed(edge(1)):
                tooth = P(px + 0.035 * L, py + 0.09 * W); e = P(px, py)
                d += f"Q{f(tooth[0])} {f(tooth[1])} {f(e[0])} {f(e[1])}"
            d += f"L{f(b[0])} {f(b[1])}Z"
        self.path(d, "p")
        m1 = P(0.5 * L, r.uniform(-0.05, 0.05) * W); m2 = P(0.92 * L, 0)
        self.path(f"M{f(b[0])} {f(b[1])}Q{f(m1[0])} {f(m1[1])} {f(m2[0])} {f(m2[1])}", "v")
        if veins and L > 20:
            for tt in (0.28, 0.5, 0.7):
                for side in (-1, 1):
                    v0 = P(tt * L, 0); v1 = P((tt + 0.16) * L, side * 0.3 * W * (1 - tt * 0.6))
                    self.path(f"M{f(v0[0])} {f(v0[1])}L{f(v1[0])} {f(v1[1])}", "v")

    def rose_leaflets(self, x, y, ang, L):
        """Compound rose leaf: short stalk, then a terminal leaflet with an opposite pair."""
        def P(px, py):
            X, Y = rot(px, py, ang); return (x + X, y + Y)
        s = P(0.45 * L, 0)
        self.path(f"M{f(x)} {f(y)}L{f(s[0])} {f(s[1])}", "s2")
        self.leaf_outline(s[0], s[1], ang, 0.55 * L, 0.3 * L, serrate=True, veins=False)
        pair = P(0.3 * L, 0)
        self.leaf_outline(pair[0], pair[1], ang - 0.95, 0.42 * L, 0.24 * L, serrate=True, veins=False)
        self.leaf_outline(pair[0], pair[1], ang + 0.95, 0.42 * L, 0.24 * L, serrate=True, veins=False)

    def laurel_sprig(self, pts, L=24, pairs=5, taper=True):
        """Bay laurel / olive: straight-ish stem with opposite pairs of smooth elliptic leaves."""
        segs = self.stem(pts, cls="s2")
        for k in range(pairs):
            t = 0.12 + 0.8 * k / max(1, pairs - 1)
            x, y, a = self.at(segs, t)
            sz = L * (1 - 0.35 * t if taper else 1)
            for side in (-1, 1):
                self.leaf_outline(x, y, a + side * 0.75 + self.r.uniform(-0.1, 0.1), sz, sz * 0.36, serrate=False, veins=False)
        x, y, a = self.at(segs, 0.995)
        self.leaf_outline(x, y, a, L * 0.7, L * 0.25, serrate=False, veins=False)

    # ---------- stems ----------
    def catmull(self, pts):
        segs = []
        P = [pts[0]] + pts + [pts[-1]]
        for i in range(1, len(P) - 2):
            p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
            c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
            segs.append((p1, c1, c2, p2))
        return segs

    @staticmethod
    def bez(seg, t):
        p0, c1, c2, p1 = seg
        u = 1 - t
        x = u**3 * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t**3 * p1[0]
        y = u**3 * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t**3 * p1[1]
        dx = 3 * u * u * (c1[0] - p0[0]) + 6 * u * t * (c2[0] - c1[0]) + 3 * t * t * (p1[0] - c2[0])
        dy = 3 * u * u * (c1[1] - p0[1]) + 6 * u * t * (c2[1] - c1[1]) + 3 * t * t * (p1[1] - c2[1])
        return x, y, math.atan2(dy, dx)

    def stem(self, pts, cls="s"):
        segs = self.catmull(pts)
        d = f"M{f(pts[0][0])} {f(pts[0][1])}" + "".join(
            f"C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(p1[0])} {f(p1[1])}" for (_, c1, c2, p1) in segs)
        self.path(d, cls)
        return segs

    def at(self, segs, t):
        n = len(segs); i = min(int(t * n), n - 1)
        return self.bez(segs[i], t * n - i)

    def rose_stem_foliage(self, segs, ts, L, side0=1):
        side = side0
        for t in ts:
            x, y, a = self.at(segs, t)
            self.rose_leaflets(x, y, a + side * 1.05 + self.r.uniform(-0.12, 0.12), L)
            side = -side

    def svg(self, w, h, x0=0, y0=0):
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {w} {h}">' + "".join(self.out) + "</svg>"


def drape(F, x0, y0, w, tie_y, hem_y, side):
    """Tied-back fabric hanging from the top edge (the draped chuppah)."""
    r = F.r
    k = 7
    tie_x = x0 + (w * 0.55 if side > 0 else w * 0.45)
    hem_pts = []
    for i in range(k):
        t = i / (k - 1)
        sx = x0 + t * w
        c1 = (sx + side * r.uniform(-4, 6), y0 + (tie_y - y0) * 0.35)
        c2 = (tie_x + (sx - tie_x) * 0.35 + side * r.uniform(-3, 3), y0 + (tie_y - y0) * 0.8)
        tx = tie_x + (sx - tie_x) * 0.12
        d = f"M{f(sx)} {f(y0)}C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(tx)} {f(tie_y)}"
        hx = tie_x + (t - 0.5) * w * 0.8 + side * 6 + r.uniform(-5, 5)
        hy = hem_y + r.uniform(-30, 12) - abs(t - 0.5) * 30
        c3 = (tx + (hx - tx) * 0.1 + r.uniform(-4, 4), tie_y + (hy - tie_y) * 0.4)
        c4 = (hx + r.uniform(-8, 8), tie_y + (hy - tie_y) * 0.82)
        d += f"C{f(c3[0])} {f(c3[1])} {f(c4[0])} {f(c4[1])} {f(hx)} {f(hy)}"
        F.path(d, "d")
        hem_pts.append((hx, hy))
    hp = hem_pts if side > 0 else hem_pts[::-1]
    d = f"M{f(hp[0][0])} {f(hp[0][1])}"
    for (ax, ay), (bx, by) in zip(hp, hp[1:]):
        d += f"Q{f((ax+bx)/2 + r.uniform(-3,3))} {f(max(ay,by)+4)} {f(bx)} {f(by)}"
    F.path(d, "d")
    for i in range(3):
        px = tie_x + side * r.uniform(-12, 14)
        ln = (hem_y - tie_y) * r.uniform(0.35, 0.7)
        F.path(f"M{f(px)} {f(tie_y+10)}q{f(r.uniform(-8,8))} {f(ln*0.5)} {f(r.uniform(-6,6))} {f(ln)}", "d")
    F.path(f"M{f(tie_x-9)} {f(tie_y-4)}Q{f(tie_x)} {f(tie_y-10)} {f(tie_x+9)} {f(tie_y-4)}", "d")
    F.path(f"M{f(tie_x-10)} {f(tie_y+3)}Q{f(tie_x)} {f(tie_y+9)} {f(tie_x+10)} {f(tie_y+3)}", "d")
    for i in range(3):
        gx = x0 + w * r.uniform(0.15, 0.85)
        F.path(f"M{f(gx)} {f(y0)}q{f(side*3)} 18 {f(side*1)} 40", "d")
    return (tie_x, tie_y)


def top_left(seed):
    """Full-height left-edge garland, packed dense: a tied drape at the
    top, a long serpentine vine with leaflets every ~7% of its length, and
    thirteen blooms (roses, peonies, buds, a spray) plus four extra laurel
    branches filling the gaps between them. Still hugs the edge."""
    F = Flora(seed)
    tie = drape(F, 6, 0, 78, 150, 300, +1)
    main = F.stem([(tie[0], tie[1] - 4), (58, 175), (86, 215), (58, 255), (82, 295),
                   (54, 335), (80, 375), (52, 415), (78, 455), (50, 495), (76, 535),
                   (52, 575), (78, 615), (54, 655), (66, 685)])
    ts = [0.05 + 0.07 * i for i in range(14)]
    F.rose_stem_foliage(main, ts, 26, side0=-1)
    F.rose(60, 148, 38)
    F.rosebud(102, 190, math.radians(-50), 16)
    F.peony(78, 238, 30)
    F.rosebud(42, 283, math.radians(140), 18)
    F.rose(88, 328, 32)
    F.spray_roses(44, 373, math.radians(-150), 26)
    F.peony(76, 418, 28)
    F.rosebud(38, 460, math.radians(150), 16)
    F.rose(84, 503, 32)
    F.rosebud(102, 546, math.radians(-40), 16)
    F.spray_roses(48, 590, math.radians(-160), 28)
    F.peony(74, 633, 30)
    F.rose(44, 670, 26)
    F.laurel_sprig([(70, 210), (96, 232), (108, 256)], L=16, pairs=3)
    F.laurel_sprig([(64, 300), (92, 318), (104, 342)], L=16, pairs=3)
    F.laurel_sprig([(58, 440), (86, 456), (100, 480)], L=16, pairs=3)
    F.laurel_sprig([(60, 560), (88, 578), (102, 602)], L=16, pairs=3)
    return F.svg(175, 715, x0=-18, y0=-10)


def top_right(seed):
    """Mirror of top_left, so both edges carry equal weight down the card."""
    F = Flora(seed)
    tie = drape(F, 216, 0, 78, 150, 300, -1)
    main = F.stem([(tie[0], tie[1] - 4), (242, 175), (214, 215), (242, 255), (218, 295),
                   (246, 335), (220, 375), (248, 415), (222, 455), (250, 495), (224, 535),
                   (248, 575), (222, 615), (246, 655), (234, 685)])
    ts = [0.05 + 0.07 * i for i in range(14)]
    F.rose_stem_foliage(main, ts, 26, side0=1)
    F.rose(240, 148, 38)
    F.rosebud(198, 190, math.radians(230), 16)
    F.peony(222, 238, 30)
    F.rosebud(258, 283, math.radians(40), 18)
    F.rose(212, 328, 32)
    F.spray_roses(256, 373, math.radians(330), 26)
    F.peony(224, 418, 28)
    F.rosebud(262, 460, math.radians(30), 16)
    F.rose(216, 503, 32)
    F.rosebud(198, 546, math.radians(220), 16)
    F.spray_roses(252, 590, math.radians(340), 28)
    F.peony(226, 633, 30)
    F.rose(256, 670, 26)
    F.laurel_sprig([(230, 210), (204, 232), (192, 256)], L=16, pairs=3)
    F.laurel_sprig([(236, 300), (208, 318), (196, 342)], L=16, pairs=3)
    F.laurel_sprig([(242, 440), (214, 456), (200, 480)], L=16, pairs=3)
    F.laurel_sprig([(240, 560), (212, 578), (198, 602)], L=16, pairs=3)
    return F.svg(175, 715, x0=143, y0=-10)


def bottom_left(seed):
    """Rising counter-accent from the bottom-left, mirroring bottom_right —
    now a full extra vine, not just a sprig, so it balances the density
    of the top corners."""
    F = Flora(seed)
    main = F.stem([(6, 720), (34, 670), (10, 620), (36, 570), (14, 520), (38, 470), (26, 430)])
    F.rose_stem_foliage(main, [0.08, 0.24, 0.4, 0.56, 0.72, 0.88], 22, side0=1)
    F.rosebud(50, 440, math.radians(255), 22)
    F.rose(56, 490, 30)
    F.peony(30, 545, 26)
    F.rosebud(58, 600, math.radians(255), 20)
    F.rose(28, 655, 28)
    F.laurel_sprig([(20, 660), (46, 646), (60, 626)], L=16, pairs=3)
    F.laurel_sprig([(16, 560), (44, 548), (58, 528)], L=16, pairs=3)
    return F.svg(160, 340, x0=-20, y0=390)


def bottom_right(seed):
    """Mirror of bottom_left."""
    F = Flora(seed)
    main = F.stem([(294, 720), (266, 670), (290, 620), (264, 570), (286, 520), (262, 470), (274, 430)])
    F.rose_stem_foliage(main, [0.08, 0.24, 0.4, 0.56, 0.72, 0.88], 22, side0=-1)
    F.rosebud(250, 440, math.radians(285), 22)
    F.rose(244, 490, 30)
    F.peony(270, 545, 26)
    F.rosebud(242, 600, math.radians(285), 20)
    F.rose(272, 655, 28)
    F.laurel_sprig([(280, 660), (254, 646), (240, 626)], L=16, pairs=3)
    F.laurel_sprig([(284, 560), (256, 548), (242, 528)], L=16, pairs=3)
    return F.svg(160, 340, x0=160, y0=390)


if __name__ == "__main__":
    out = sys.argv[1]
    open(out + "/flora-tl.svg", "w").write(top_left(3))
    open(out + "/flora-tr.svg", "w").write(top_right(5))
    open(out + "/flora-bl.svg", "w").write(bottom_left(7))
    open(out + "/flora-br.svg", "w").write(bottom_right(9))
    print("ok")

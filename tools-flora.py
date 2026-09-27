"""Procedural botanical line art: rose, peony, buds, leaves on a flowing stem."""
import math, random, sys

def f(v): return f"{v:.1f}".rstrip("0").rstrip(".")

def rot(x, y, a):
    c, s = math.cos(a), math.sin(a)
    return x * c - y * s, x * s + y * c

class Flora:
    def __init__(self, seed):
        self.r = random.Random(seed)
        self.out = []

    # ---------- primitives ----------
    def petal(self, cx, cy, ang, r0, L, W, bumps=2, fill=True):
        r = self.r
        L *= r.uniform(0.92, 1.08); W *= r.uniform(0.9, 1.1)
        pts = []
        def P(x, y):
            X, Y = rot(x, y, ang); return (cx + X, cy + Y)
        b = P(r0, 0)
        d = [f"M{f(b[0])} {f(b[1])}"]
        c1 = P(r0 + 0.28 * L, -0.62 * W); c2 = P(r0 + 0.82 * L, -0.66 * W); tl = P(r0 + 0.96 * L, -0.28 * W)
        d.append(f"C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(tl[0])} {f(tl[1])}")
        # ruffled tip: n bumps from tl to tr
        tr = P(r0 + 0.96 * L, 0.28 * W)
        n = bumps
        for i in range(n):
            t0, t1 = i / n, (i + 1) / n
            ya = -0.28 * W + 0.56 * W * t0; yb = -0.28 * W + 0.56 * W * t1
            ym = (ya + yb) / 2
            cp = P(r0 + L * (1.0 + 0.06 * r.uniform(0.6, 1.2)), ym)
            e = P(r0 + 0.96 * L - (0.03 * L if i < n - 1 else 0), yb)
            d.append(f"Q{f(cp[0])} {f(cp[1])} {f(e[0])} {f(e[1])}")
        c3 = P(r0 + 0.82 * L, 0.66 * W); c4 = P(r0 + 0.28 * L, 0.62 * W)
        d.append(f"C{f(c3[0])} {f(c3[1])} {f(c4[0])} {f(c4[1])} {f(b[0])} {f(b[1])}Z")
        cls = "p" if fill else "l"
        self.out.append(f'<path class="{cls}" d="{"".join(d)}"/>')
        # a soft crease line inside the petal
        if L > 18 and r.random() < 0.7:
            s0 = P(r0 + 0.15 * L, 0); s1 = P(r0 + 0.5 * L, r.uniform(-0.12, 0.12) * W); s2 = P(r0 + 0.8 * L, r.uniform(-0.1, 0.1) * W)
            self.out.append(f'<path class="v" d="M{f(s0[0])} {f(s0[1])}Q{f(s1[0])} {f(s1[1])} {f(s2[0])} {f(s2[1])}"/>')

    def spiral_centre(self, cx, cy, rmax, turns=2.2):
        r = self.r
        n = int(turns * 7)
        a0 = r.uniform(0, math.tau)
        for i in range(n):
            t = i / n
            rad = rmax * (0.18 + 0.82 * t)
            a = a0 + t * turns * math.tau
            span = 1.5 - 0.5 * t
            p0 = (cx + rad * math.cos(a), cy + rad * math.sin(a))
            p1 = (cx + rad * 1.18 * math.cos(a + span / 2), cy + rad * 1.18 * math.sin(a + span / 2))
            p2 = (cx + rad * math.cos(a + span), cy + rad * math.sin(a + span))
            self.out.append(f'<path class="l" d="M{f(p0[0])} {f(p0[1])}Q{f(p1[0])} {f(p1[1])} {f(p2[0])} {f(p2[1])}"/>')

    def rose(self, cx, cy, R):
        r = self.r
        rings = [(9, 0.42 * R, 0.62 * R, 0.55 * R, 1), (7, 0.22 * R, 0.5 * R, 0.5 * R, 1), (5, 0.08 * R, 0.34 * R, 0.4 * R, 1)]
        for n, r0, L, W, bumps in rings:
            a0 = r.uniform(0, math.tau)
            for i in range(n):
                a = a0 + i * math.tau / n + r.uniform(-0.12, 0.12)
                self.petal(cx, cy, a, r0, L, W, bumps)
        self.spiral_centre(cx, cy, 0.2 * R)

    def peony(self, cx, cy, R):
        r = self.r
        rings = [(12, 0.5 * R, 0.55 * R, 0.5 * R, 3), (10, 0.3 * R, 0.5 * R, 0.46 * R, 3), (8, 0.14 * R, 0.4 * R, 0.4 * R, 2), (6, 0.04 * R, 0.26 * R, 0.3 * R, 2)]
        for n, r0, L, W, bumps in rings:
            a0 = r.uniform(0, math.tau)
            for i in range(n):
                a = a0 + i * math.tau / n + r.uniform(-0.15, 0.15)
                self.petal(cx, cy, a, r0, L, W, bumps)

    def bud(self, cx, cy, ang, L):
        r = self.r
        W = 0.42 * L
        def P(x, y):
            X, Y = rot(x, y, ang); return (cx + X, cy + Y)
        b = P(0, 0); t = P(L, 0)
        c1 = P(0.3 * L, -0.9 * W); c2 = P(0.85 * L, -0.5 * W); c3 = P(0.85 * L, 0.5 * W); c4 = P(0.3 * L, 0.9 * W)
        self.out.append(f'<path class="p" d="M{f(b[0])} {f(b[1])}C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(t[0])} {f(t[1])}C{f(c3[0])} {f(c3[1])} {f(c4[0])} {f(c4[1])} {f(b[0])} {f(b[1])}Z"/>')
        for k in (-0.35, 0.3):
            s0 = P(0.1 * L, 0); s1 = P(0.55 * L, k * W); s2 = P(0.9 * L, k * 0.5 * W)
            self.out.append(f'<path class="v" d="M{f(s0[0])} {f(s0[1])}Q{f(s1[0])} {f(s1[1])} {f(s2[0])} {f(s2[1])}"/>')
        # sepals
        for k in (-1, 0, 1):
            s0 = P(0, 0); s1 = P(0.45 * L, k * 0.9 * W); s2 = P(0.7 * L, k * 1.15 * W)
            self.out.append(f'<path class="l" d="M{f(s0[0])} {f(s0[1])}Q{f(s1[0])} {f(s1[1])} {f(s2[0])} {f(s2[1])}"/>')

    def leaf(self, x, y, ang, L, W):
        r = self.r
        L *= r.uniform(0.9, 1.1); W *= r.uniform(0.9, 1.1)
        def P(px, py):
            X, Y = rot(px, py, ang); return (x + X, y + Y)
        b = P(0, 0); t = P(L, 0)
        c1 = P(0.25 * L, -0.55 * W); c2 = P(0.72 * L, -0.5 * W); c3 = P(0.72 * L, 0.5 * W); c4 = P(0.25 * L, 0.55 * W)
        self.out.append(f'<path class="p" d="M{f(b[0])} {f(b[1])}C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(t[0])} {f(t[1])}C{f(c3[0])} {f(c3[1])} {f(c4[0])} {f(c4[1])} {f(b[0])} {f(b[1])}Z"/>')
        m1 = P(0.5 * L, r.uniform(-0.06, 0.06) * W); m2 = P(0.9 * L, 0)
        self.out.append(f'<path class="v" d="M{f(b[0])} {f(b[1])}Q{f(m1[0])} {f(m1[1])} {f(m2[0])} {f(m2[1])}"/>')
        if L > 22:
            for tt in (0.3, 0.55):
                for side in (-1, 1):
                    v0 = P(tt * L, 0); v1 = P((tt + 0.2) * L, side * 0.32 * W)
                    self.out.append(f'<path class="v" d="M{f(v0[0])} {f(v0[1])}Q{f((v0[0]+v1[0])/2)} {f((v0[1]+v1[1])/2 + side*1.5)} {f(v1[0])} {f(v1[1])}"/>')

    # ---------- stems ----------
    def catmull(self, pts):
        """Catmull-Rom through pts -> list of cubic segments (p0, c1, c2, p1)."""
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
        self.out.append(f'<path class="{cls}" d="{d}"/>')
        return segs

    def at(self, segs, t):
        n = len(segs); i = min(int(t * n), n - 1)
        return self.bez(segs[i], t * n - i)

    def leaves_along(self, segs, ts, size, side0=1, spread=0.95, taper=True):
        side = side0
        for k, t in enumerate(ts):
            x, y, a = self.at(segs, t)
            sz = size * ((1 - 0.45 * t) if taper else 1)
            ang = a + side * spread + self.r.uniform(-0.15, 0.15)
            self.leaf(x, y, ang, sz, sz * 0.42)
            side = -side

    def svg(self, w, h):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">'
                + "".join(self.out) + "</svg>")


def drape(F, x0, y0, w, tie_y, hem_y, side):
    """Tied-back curtain hanging from the top edge. side=+1 hangs on the left edge (tie pulls right)."""
    r = F.r
    k = 7
    tie_x = x0 + (w * 0.55 if side > 0 else w * 0.45)
    hem_pts = []
    for i in range(k):
        t = i / (k - 1)
        sx = x0 + t * w
        # upper fall: sway outward then converge into the tie
        c1 = (sx + side * r.uniform(-4, 6), y0 + (tie_y - y0) * 0.35)
        c2 = (tie_x + (sx - tie_x) * 0.35 + side * r.uniform(-3, 3), y0 + (tie_y - y0) * 0.8)
        tx = tie_x + (sx - tie_x) * 0.12
        d = f"M{f(sx)} {f(y0)}C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(tx)} {f(tie_y)}"
        # lower fall: flare out below the tie to a soft hem
        hx = tie_x + (t - 0.5) * w * 0.8 + side * 6 + r.uniform(-5, 5)
        hy = hem_y + r.uniform(-30, 12) - abs(t - 0.5) * 30
        c3 = (tx + (hx - tx) * 0.1 + r.uniform(-4, 4), tie_y + (hy - tie_y) * 0.4)
        c4 = (hx + r.uniform(-8, 8), tie_y + (hy - tie_y) * 0.82)
        d += f"C{f(c3[0])} {f(c3[1])} {f(c4[0])} {f(c4[1])} {f(hx)} {f(hy)}"
        F.out.append(f'<path class="d" d="{d}"/>')
        hem_pts.append((hx, hy))
    # soft hem
    hp = hem_pts if side > 0 else hem_pts[::-1]
    d = f"M{f(hp[0][0])} {f(hp[0][1])}"
    for (ax, ay), (bx, by) in zip(hp, hp[1:]):
        d += f"Q{f((ax+bx)/2 + r.uniform(-3,3))} {f(max(ay,by)+4)} {f(bx)} {f(by)}"
    F.out.append(f'<path class="d" d="{d}"/>')
    # partial inner folds below the tie
    for i in range(3):
        px = tie_x + side * r.uniform(-12, 14)
        ln = (hem_y - tie_y) * r.uniform(0.35, 0.7)
        F.out.append(f'<path class="d" d="M{f(px)} {f(tie_y+10)}q{f(r.uniform(-8,8))} {f(ln*0.5)} {f(r.uniform(-6,6))} {f(ln)}"/>')
    # tie: a small gathered knot
    F.out.append(f'<path class="d" d="M{f(tie_x-9)} {f(tie_y-4)}Q{f(tie_x)} {f(tie_y-10)} {f(tie_x+9)} {f(tie_y-4)}"/>')
    F.out.append(f'<path class="d" d="M{f(tie_x-10)} {f(tie_y+3)}Q{f(tie_x)} {f(tie_y+9)} {f(tie_x+10)} {f(tie_y+3)}"/>')
    # a few short gathers near the top
    for i in range(3):
        gx = x0 + w * r.uniform(0.15, 0.85)
        F.out.append(f'<path class="d" d="M{f(gx)} {f(y0)}q{f(side*3)} 18 {f(side*1)} 40"/>')
    return (tie_x, tie_y)


def top_left(seed):
    F = Flora(seed)
    tie = drape(F, 8, 0, 110, 210, 420, +1)
    # cascade hanging from the tie, spilling down and inward
    main = F.stem([(tie[0], tie[1] - 6), (80, 270), (104, 340), (112, 430), (94, 520), (66, 600)])
    F.leaves_along(main, [0.1, 0.2, 0.32, 0.44, 0.56, 0.68, 0.8, 0.9], 42, side0=-1, taper=False)
    br = F.stem([(104, 342), (140, 328), (172, 300)])
    F.leaves_along(br, [0.4, 0.75], 30, side0=1)
    F.bud(172, 300, math.radians(-40), 26)
    F.rose(84, 266, 54)
    br2 = F.stem([(110, 470), (140, 500), (150, 540)])
    F.leaves_along(br2, [0.4], 28, side0=-1)
    F.peony(150, 560, 40)
    return F.svg(300, 720)


def top_right(seed):
    F = Flora(seed)
    tie = drape(F, 182, 0, 110, 190, 380, -1)
    main = F.stem([(tie[0], tie[1] - 6), (206, 240), (182, 300), (168, 360), (186, 420)])
    F.leaves_along(main, [0.12, 0.28, 0.46, 0.64, 0.84], 40, side0=1, taper=False)
    F.rose(208, 238, 50)
    br = F.stem([(176, 330), (140, 350), (110, 380)])
    F.leaves_along(br, [0.45], 30, side0=-1)
    F.bud(110, 380, math.radians(215), 26)
    return F.svg(300, 720)


def bottom_right(seed):
    F = Flora(seed)
    main = F.stem([(286, 720), (266, 640), (240, 590), (222, 540), (224, 480), (240, 430)])
    F.leaves_along(main, [0.1, 0.22, 0.36, 0.5, 0.64, 0.78], 42, side0=1)
    br = F.stem([(242, 592), (206, 600), (176, 626)])
    F.leaves_along(br, [0.45], 30, side0=-1)
    F.peony(164, 640, 44)
    F.bud(240, 430, math.radians(-70), 30)
    br2 = F.stem([(226, 520), (256, 508), (278, 486)])
    F.leaves_along(br2, [0.5], 26, side0=1)
    F.bud(278, 486, math.radians(-40), 22)
    return F.svg(300, 720)


def left_spray(seed):
    F = Flora(seed)
    # main stem rising from bottom-left, bending inward then back out
    main = F.stem([(40, 700), (58, 600), (95, 500), (120, 400), (110, 300), (130, 210), (168, 140)])
    F.leaves_along(main, [0.08, 0.16, 0.25, 0.34, 0.44, 0.53, 0.63, 0.72, 0.8], 58, side0=1)
    # side branch with a peony
    br = F.stem([(96, 498), (140, 470), (185, 455), (222, 430)])
    F.leaves_along(br, [0.25, 0.5, 0.72], 40, side0=-1)
    F.peony(240, 418, 58)
    # second side branch: bud + small leaves
    br2 = F.stem([(112, 372), (70, 340), (46, 300)])
    F.leaves_along(br2, [0.35, 0.65], 34, side0=1)
    F.bud(46, 300, math.radians(-115), 30)
    # a bud near the top
    br3 = F.stem([(128, 232), (170, 250), (205, 262)])
    F.leaves_along(br3, [0.4], 30, side0=-1)
    F.bud(205, 262, math.radians(15), 28)
    # main bloom: rose at the tip
    F.rose(176, 118, 64)
    return F.svg(300, 720)


def right_spray(seed):
    F = Flora(seed)
    main = F.stem([(262, 0), (245, 90), (208, 180), (180, 280), (196, 380), (176, 470), (140, 540)])
    F.leaves_along(main, [0.08, 0.17, 0.26, 0.35, 0.45, 0.54, 0.64, 0.73, 0.81], 56, side0=-1)
    br = F.stem([(206, 184), (160, 200), (118, 214), (82, 238)])
    F.leaves_along(br, [0.28, 0.52, 0.74], 38, side0=1)
    F.peony(64, 254, 54)
    br2 = F.stem([(190, 300), (232, 322), (258, 360)])
    F.leaves_along(br2, [0.35, 0.65], 32, side0=-1)
    F.bud(258, 360, math.radians(58), 30)
    br3 = F.stem([(188, 448), (150, 440), (120, 426)])
    F.leaves_along(br3, [0.45], 28, side0=1)
    F.bud(120, 426, math.radians(200), 26)
    F.rose(132, 560, 60)
    return F.svg(300, 720)


if __name__ == "__main__":
    out = sys.argv[1]
    open(out + "/flora-tl.svg", "w").write(top_left(3))
    open(out + "/flora-tr.svg", "w").write(top_right(5))
    open(out + "/flora-br.svg", "w").write(bottom_right(9))
    print("ok")

"""Botanical line art for the save-the-date, restricted to the floral brief's
florist's selection: cream garden roses and spray roses, peony, olive / bay laurel foliage.
Full-height drapes echo the chuppah."""
import math, random, sys

PREC = 1

def f(v):
    return f"{v:.{PREC}f}".rstrip("0").rstrip(".") if PREC else str(round(v))

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
        # each rose varies: open (more, wider outer petals) through tight (fewer, cupped)
        openness = r.uniform(0.85, 1.15)
        n_out, n_in = r.choice([(5, 4), (6, 5), (7, 5), (6, 4), (7, 6)])
        for i in range(n_out):
            self.petal(cx, cy, a0 + i * math.tau / n_out + r.uniform(-0.14, 0.14), 0.34 * R, 0.66 * R * openness, 0.78 * R * (6 / n_out) ** 0.5, "rose")
        for i in range(n_in):
            self.petal(cx, cy, a0 + math.pi / n_in + i * math.tau / n_in + r.uniform(-0.12, 0.12), 0.18 * R, 0.5 * R, 0.62 * R * (5 / n_in) ** 0.5, "rose")
        # furled centre: wrapped petals as overlapping cupped arcs, tightening inward
        base = r.uniform(0, math.tau)
        for k in range(r.choice([3, 4, 5])):
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

    def blossom(self, cx, cy, R):
        """A simple flat five-petal blossom — small, quick, and visually
        distinct from the rose/peony/anemone silhouettes; good filler."""
        r = self.r
        a0 = r.uniform(0, math.tau)
        n = 5
        for i in range(n):
            a = a0 + i * math.tau / n + r.uniform(-0.06, 0.06)
            nx, ny = -math.sin(a), math.cos(a)
            w = R * r.uniform(0.5, 0.62)
            tx, ty = cx + R * math.cos(a), cy + R * math.sin(a)
            c1 = (cx + 0.55 * R * math.cos(a) + w * nx, cy + 0.55 * R * math.sin(a) + w * ny)
            c2 = (cx + 0.55 * R * math.cos(a) - w * nx, cy + 0.55 * R * math.sin(a) - w * ny)
            self.path(f"M{f(cx)} {f(cy)}Q{f(c1[0])} {f(c1[1])} {f(tx)} {f(ty)}Q{f(c2[0])} {f(c2[1])} {f(cx)} {f(cy)}Z", "p")
        self.out.append(f'<circle class="gd" cx="{f(cx)}" cy="{f(cy)}" r="{f(R * 0.2)}"/>')

    def narcissus(self, cx, cy, R):
        """Narcissus: six pointed perianth petals around a ruffled trumpet cup."""
        r = self.r
        a0 = r.uniform(0, math.tau)
        for i in range(6):
            a = a0 + i * math.tau / 6 + r.uniform(-0.05, 0.05)
            nx, ny = -math.sin(a), math.cos(a)
            w = R * 0.34
            tip = (cx + R * math.cos(a), cy + R * math.sin(a))
            m = (cx + 0.5 * R * math.cos(a), cy + 0.5 * R * math.sin(a))
            c1 = (m[0] + w * nx, m[1] + w * ny); c2 = (m[0] - w * nx, m[1] - w * ny)
            self.path(f"M{f(cx)} {f(cy)}C{f(c1[0])} {f(c1[1])} {f(c1[0] + 0.3*(tip[0]-c1[0]))} {f(c1[1] + 0.3*(tip[1]-c1[1]))} {f(tip[0])} {f(tip[1])}"
                      f"C{f(c2[0] + 0.3*(tip[0]-c2[0]))} {f(c2[1] + 0.3*(tip[1]-c2[1]))} {f(c2[0])} {f(c2[1])} {f(cx)} {f(cy)}Z", "p")
            self.path(f"M{f(cx)} {f(cy)}L{f(m[0] + 0.5*(tip[0]-m[0]))} {f(m[1] + 0.5*(tip[1]-m[1]))}", "v")
        # trumpet: a scalloped ring
        cr = R * 0.3; n = 10; d = ""
        for i in range(n + 1):
            a = i * math.tau / n
            rr = cr * (1.0 if i % 2 == 0 else 0.84)
            d += ("M" if i == 0 else "L") + f"{f(cx + rr * math.cos(a))} {f(cy + rr * math.sin(a))}"
        self.path(d + "Z", "p")
        self.out.append(f'<circle class="gd" cx="{f(cx)}" cy="{f(cy)}" r="{f(cr * 0.35)}"/>')

    def violet(self, cx, cy, R):
        """Violet: five uneven petals — two upright, two side, one broad lower lip."""
        r = self.r
        rot0 = r.uniform(-0.5, 0.5)
        spec = [(-1.95, 0.85, 0.5), (-1.2, 0.85, 0.5), (-0.1, 0.8, 0.52), (-3.05, 0.8, 0.52), (1.57, 1.05, 0.7)]
        for a, L, W in spec:
            a += rot0
            nx, ny = -math.sin(a), math.cos(a)
            tip = (cx + R * L * math.cos(a), cy + R * L * math.sin(a))
            m = (cx + 0.55 * R * L * math.cos(a), cy + 0.55 * R * L * math.sin(a))
            w = R * W * 0.6
            self.path(f"M{f(cx)} {f(cy)}Q{f(m[0] + w*nx)} {f(m[1] + w*ny)} {f(tip[0])} {f(tip[1])}Q{f(m[0] - w*nx)} {f(m[1] - w*ny)} {f(cx)} {f(cy)}Z", "p")
        lip = (cx + 0.5 * R * math.cos(1.57 + rot0), cy + 0.5 * R * math.sin(1.57 + rot0))
        for k in (-0.25, 0, 0.25):
            e = (cx + 0.75 * R * math.cos(1.57 + rot0 + k), cy + 0.75 * R * math.sin(1.57 + rot0 + k))
            self.path(f"M{f(cx)} {f(cy)}L{f(e[0])} {f(e[1])}", "v")
        self.out.append(f'<circle class="gd" cx="{f(cx)}" cy="{f(cy)}" r="{f(R * 0.12)}"/>')

    def hyacinth(self, cx, cy, ang, L):
        """Hyacinth: a short spike of small star florets, densest at the base."""
        r = self.r
        def P(px, py):
            X, Y = rot(px, py, ang); return (cx + X, cy + Y)
        e = P(L, 0)
        self.path(f"M{f(cx)} {f(cy)}L{f(e[0])} {f(e[1])}", "s2")
        n = r.randint(7, 11)
        for i in range(n):
            t = 0.2 + 0.8 * i / (n - 1)
            spread = L * 0.26 * (1 - 0.6 * t)
            side = 1 if i % 2 else -1
            p = P(L * t, side * spread * r.uniform(0.5, 1.0))
            fr = L * 0.11 * (1 - 0.45 * t)
            a0 = r.uniform(0, math.tau)
            d = ""
            for k in range(13):
                a = a0 + k * math.tau / 12
                rr = fr if k % 2 == 0 else fr * 0.45
                d += ("M" if k == 0 else "L") + f"{f(p[0] + rr * math.cos(a))} {f(p[1] + rr * math.sin(a))}"
            self.path(d + "Z", "p")

    def rose_side(self, cx, cy, ang, R):
        """A rose seen in profile: calyx, a cupped bowl of overlapping front
        petals, and rolled petal edges at the rim — a different silhouette
        from the face-on roses."""
        r = self.r
        def P(px, py):
            X, Y = rot(px, py, ang - math.pi / 2); return (cx + X, cy + Y)
        # calyx
        for k in (-1, 1):
            a = P(0, 0); b = P(k * 0.55 * R, -0.05 * R); c = P(k * 0.9 * R, 0.35 * R)
            self.path(f"M{f(a[0])} {f(a[1])}Q{f(b[0])} {f(b[1])} {f(c[0])} {f(c[1])}", "l")
        # bowl outline
        L0 = P(-0.75 * R, -0.35 * R); R0 = P(0.75 * R, -0.35 * R)
        b1 = P(-0.9 * R, -0.95 * R); b2 = P(0.9 * R, -0.95 * R); base = P(0, -0.08 * R)
        self.path(f"M{f(base[0])} {f(base[1])}Q{f(b1[0])} {f(b1[1])} {f(L0[0])} {f(L0[1] )}", "l")
        # front petals: three overlapping cups
        for k, (x0, w, h) in enumerate([(-0.42, 0.62, 1.05), (0.42, 0.62, 1.05), (0.0, 0.7, 0.9)]):
            x0 *= R; w *= R; h *= R
            s = P(x0 - w, -0.35 * R - 0.1 * h); e = P(x0 + w, -0.35 * R - 0.1 * h)
            c1 = P(x0 - w * 1.05, -0.35 * R + 0.55 * h); c2 = P(x0 + w * 1.05, -0.35 * R + 0.55 * h)
            topc = P(x0, -0.35 * R - 0.45 * h + r.uniform(-0.06, 0.06) * R)
            self.path(f"M{f(s[0])} {f(s[1])}C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(e[0])} {f(e[1])}"
                      f"Q{f(topc[0])} {f(topc[1])} {f(s[0])} {f(s[1])}Z", "p")
        # rolled rim edges
        for x0 in (-0.5, 0.05, 0.55):
            a = P((x0 - 0.18) * R, -1.12 * R); b = P(x0 * R, -1.28 * R); c = P((x0 + 0.2) * R, -1.1 * R)
            self.path(f"M{f(a[0])} {f(a[1])}Q{f(b[0])} {f(b[1])} {f(c[0])} {f(c[1])}", "l")

    def olive_sprig(self, pts, L=20, pairs=4):
        """Olive: slender pointed leaves (narrower than laurel) with a few olives."""
        segs = self.stem(pts, cls="s2")
        for k in range(pairs):
            t = 0.1 + 0.85 * k / max(1, pairs - 1)
            x, y, a = self.at(segs, t)
            sz = L * (1 - 0.25 * t)
            side = 1 if k % 2 else -1
            self.leaf_outline(x, y, a + side * 0.55 + self.r.uniform(-0.12, 0.12), sz, sz * 0.2, serrate=False, veins=False)
            if self.r.random() < 0.45:
                ox, oy = x + 6 * math.cos(a - side * 1.2), y + 6 * math.sin(a - side * 1.2)
                self.out.append(f'<ellipse class="ol" cx="{f(ox)}" cy="{f(oy)}" rx="3.2" ry="4.4" transform="rotate({f(math.degrees(a))} {f(ox)} {f(oy)})"/>')

    def bloom(self, kind, cx, cy, ang, R):
        """Dispatch to a bloom type by name, sized/oriented uniformly so callers can pick randomly."""
        if kind == "rose": self.rose(cx, cy, R)
        elif kind == "rose_side": self.rose_side(cx, cy, ang, R * 0.62)
        elif kind == "peony": self.peony(cx, cy, R * 0.92)
        elif kind == "anemone": self.anemone(cx, cy, R * 0.85)
        elif kind == "blossom": self.blossom(cx, cy, R * 0.55)
        elif kind == "bud": self.rosebud(cx, cy, ang, R * 0.62)
        elif kind == "narcissus": self.narcissus(cx, cy, R * 0.7)
        elif kind == "violet": self.violet(cx, cy, R * 0.42)
        elif kind == "hyacinth": self.hyacinth(cx, cy, ang, R * 1.1)

    def scatter_blooms(self, segs, n, side0, t_range=(0.05, 0.96), size_range=(22, 40),
                        offset_range=(10, 22),
                        types=("rose", "rose", "rose", "rose_side", "rose_side", "peony", "peony", "anemone",
                               "narcissus", "hyacinth", "violet", "violet", "blossom", "bud", "bud")):
        """Place n blooms along a stem at jittered (non-periodic) intervals, each a
        randomly chosen type/size, offset slightly to the outer side of the stem so
        the sequence and silhouette read as varied rather than a repeating cycle."""
        r = self.r
        t0, t1 = t_range
        order = list(types)
        pool = []
        for i in range(n):
            t = t0 + (t1 - t0) * (i + r.uniform(0.12, 0.88)) / n
            x, y, a = self.at(segs, t)
            side = side0 if r.random() < 0.78 else -side0
            off = r.uniform(*offset_range)
            px = x + off * math.cos(a + side * math.pi / 2)
            py = y + off * math.sin(a + side * math.pi / 2)
            if not pool:
                pool = list(order); r.shuffle(pool)
            kind = pool.pop()
            R = r.uniform(*size_range)
            self.bloom(kind, px, py, a + r.uniform(-0.5, 0.5), R)

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


def drape(F, x0, y0, w, tie_y, hem_y, side=1):
    """A tied-back curtain (left side; the right is the mirror image). The fabric hangs
    from the full width of the rod, its inner edge sweeps in a curve to a tie near the
    frame, then falls and flares into a full skirt at the hem. Folds have uneven widths
    and every other one is shaded, so the cloth reads as having volume.
    Returns the inner edge as two cubic segments (rod->tie, tie->hem)."""
    r = F.r
    k = 10
    ts = sorted([0.0, 1.0] + [(i + r.uniform(-0.3, 0.3)) / (k - 1) for i in range(1, k - 1)])
    tie_x = x0 + 0.24 * w                  # pulled to the side, toward the frame
    bundle = 0.2 * w                       # width of the gathered folds at the tie
    span = tie_y - y0
    strands = []
    for t in ts:
        sx = x0 + t * w
        tx = tie_x + (t - 0.5) * bundle
        c1 = (sx + r.uniform(-1.5, 1.5), y0 + span * (0.5 + 0.12 * t))       # falls straight, then sweeps
        c2 = (tx + (sx - tx) * (0.25 + 0.25 * t), tie_y - span * 0.16)       # inner folds belly outward
        hx = x0 + 0.02 * w + t * 1.12 * w + r.uniform(-2, 2)                # skirt spreads as it pools
        hy = hem_y - 4 + r.uniform(-4, 5) - 6 * math.sin(math.pi * t)
        c3 = (tx + (hx - tx) * 0.05, tie_y + (hy - tie_y) * 0.35)
        c4 = (tx + (hx - tx) * 0.55, hy - (hy - tie_y) * 0.12)                # bends outward onto the floor
        strands.append(((sx, y0), c1, c2, (tx, tie_y), c3, c4, (hx, hy)))

    def fwd(st):
        return (f"C{f(st[1][0])} {f(st[1][1])} {f(st[2][0])} {f(st[2][1])} {f(st[3][0])} {f(st[3][1])}"
                f"C{f(st[4][0])} {f(st[4][1])} {f(st[5][0])} {f(st[5][1])} {f(st[6][0])} {f(st[6][1])}")

    def back(st):
        return (f"C{f(st[5][0])} {f(st[5][1])} {f(st[4][0])} {f(st[4][1])} {f(st[3][0])} {f(st[3][1])}"
                f"C{f(st[2][0])} {f(st[2][1])} {f(st[1][0])} {f(st[1][1])} {f(st[0][0])} {f(st[0][1])}")

    a, b = strands[0], strands[-1]
    # whole fabric, then shading on alternate folds
    F.path(f"M{f(a[0][0])} {f(a[0][1])}L{f(b[0][0])} {f(b[0][1])}{fwd(b)}L{f(a[6][0])} {f(a[6][1])}{back(a)}Z", "fab")
    for i in range(0, k - 1, 2):        # shadowed folds, of uneven depth like heavy satin
        p, q = strands[i], strands[i + 1]
        op = r.uniform(0.06, 0.17)
        F.out.append(f'<path class="fabd" style="opacity:{op:.2f}" d="M{f(p[0][0])} {f(p[0][1])}{fwd(p)}L{f(q[6][0])} {f(q[6][1])}{back(q)}Z"/>')
    for i, st in enumerate(strands):    # edges drawn firmly, interior folds lightly
        F.path(f"M{f(st[0][0])} {f(st[0][1])}{fwd(st)}", "d" if i in (0, k - 1) else "d2")
    # hem: soft scallops between the fold ends
    d = f"M{f(a[6][0])} {f(a[6][1])}"
    for p, q in zip(strands, strands[1:]):
        (ax, ay), (bx, by) = p[6], q[6]
        d += f"Q{f((ax + bx) / 2)} {f(max(ay, by) + 5)} {f(bx)} {f(by)}"
    F.path(d, "d")
    # fabric pooled on the floor: a few soft folds lying along the hem
    for j in range(4):
        u0 = r.uniform(0.0, 0.5); u1 = u0 + r.uniform(0.3, 0.5)
        xa, xb = x0 + u0 * 1.1 * w, x0 + min(u1, 1.0) * 1.1 * w
        ya = hem_y - r.uniform(6, 18)
        F.path(f"M{f(xa)} {f(ya + 4)}Q{f((xa + xb) / 2)} {f(ya - 6)} {f(xb)} {f(ya + 2)}", "d2")
    # tie-back: a fabric band wrapped round the gathered folds
    tx0 = tie_x - bundle / 2 - 6; tx1 = tie_x + bundle / 2 + 6
    F.path(f"M{f(tx0)} {f(tie_y-6)}Q{f(tie_x)} {f(tie_y-2)} {f(tx1)} {f(tie_y-6)}L{f(tx1)} {f(tie_y+5)}"
           f"Q{f(tie_x)} {f(tie_y+9)} {f(tx0)} {f(tie_y+5)}Z", "p")
    F.path(f"M{f(tx0+2)} {f(tie_y-0.5)}Q{f(tie_x)} {f(tie_y+3.5)} {f(tx1-2)} {f(tie_y-0.5)}", "v")
    return (b[0], b[1], b[2], b[3]), (b[3], b[4], b[5], b[6])


STYLE = ("<style>"
         ".p{fill:#fbf8f0;stroke:#7f8a4e;stroke-width:1;stroke-linejoin:round}"
         ".l,.s,.s2{fill:none;stroke:#7f8a4e;stroke-width:1;stroke-linecap:round}"
         ".s{stroke-width:1.3}"
         ".g{fill:none;stroke:#b0975a;stroke-width:.8}.gd{fill:#b0975a}"
         ".k{fill:#5f6a3a}.kd{fill:#7f8a4e}"
         ".v{fill:none;stroke:#7f8a4e;stroke-width:.7;stroke-linecap:round;opacity:.7}"
         ".d{fill:none;stroke:#7f8a4e;stroke-width:1.05;stroke-linecap:round}"
         ".fab{fill:#eeeede}"   # opaque, so the swag tucks cleanly behind the drapes
         ".fabd{fill:#7f8a4e;opacity:.1}"
         ".d2{fill:none;stroke:#7f8a4e;stroke-width:.75;stroke-linecap:round;opacity:.5}"
         ".ol{fill:#d9dcc2;stroke:#7f8a4e;stroke-width:.8}"
         "</style>")

def svg_doc(F, W, H):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
            + STYLE + "".join(F.out) + "</svg>")


def tall_drape(W, H, w, tie_frac, hem_pad, k, seed):
    """One full-height curtain (left side; the right is the same image mirrored),
    tied back low toward the frame so the fabric pools at the hem, with a garland
    laid along its inner edge: the fullest cluster where the fabric gathers at the
    rod, a few larger blooms spaced below, and buds toward the hem. Blooms sit on the
    fabric (nudged outward from the edge) so nothing spills toward the text.
    k scales flower size for the slimmer phone version."""
    F = Flora(seed)
    x0 = 0.5                                # flush with the image edge, so the fabric meets the frame
    tie_y, hem_y = H * tie_frac, H - hem_pad
    upper, lower = drape(F, x0, 0, w, tie_y, hem_y)
    # sample the inner edge, spacing points by height so t along the garland ~ height
    n_up = max(3, round(18 * tie_frac)); n_lo = 18 - n_up
    edge = [Flora.bez(upper, i / n_up)[:2] for i in range(n_up)] + [Flora.bez(lower, i / n_lo)[:2] for i in range(n_lo + 1)]
    edge[0] = (edge[0][0] - 2, 4)
    segs = F.stem(edge, cls="s2")
    F.rose_stem_foliage(segs, [0.02 + 0.045 * i for i in range(22)], 21 * k, side0=-1)
    tf = tie_y / hem_y                      # the tie's height, as a fraction
    def t_at(frac):                      # garland position at a given fraction of the height
        best, bt = 1e9, 0.5
        for i in range(401):
            t = i / 400
            dy = abs(F.at(segs, t)[1] - frac * hem_y)
            if dy < best: best, bt = dy, t
        return bt
    plan = [  # (height, kind, size) — a full cluster at the rod, open roses down the sweep, a cluster at the low tie
        (0.008, "rose", 34), (0.030, "peony", 27), (0.052, "rose", 22), (0.074, "rose_side", 18),
        (0.17, "rose", 18), (0.28, "rose_side", 15), (0.38, "rose", 17),
        (0.64, "rose", 16),   # nothing between 0.40 and 0.62 of the height: the event titles sit there
        (tf - 0.035, "rose_side", 17), (tf - 0.012, "peony", 22), (tf + 0.012, "rose", 24),
        (tf + 0.09, "rose", 15),
    ]
    for h, kind, R in plan:
        t = min(max(t_at(h), 0.005), 0.995)
        x, y, a = F.at(segs, t)
        R *= k
        off = R * 0.85                       # toward the card edge, onto the fabric
        x, y = x + off * math.cos(a + math.pi / 2), y + off * math.sin(a + math.pi / 2)
        F.bloom(kind, x, y, a + F.r.uniform(-0.4, 0.4), R)
    for t in (0.06, 0.12, 0.33, 0.56, tf + 0.05):
        x, y, a = F.at(segs, t)
        L = 30 * k
        F.laurel_sprig([(x, y), (x - 0.5 * L * math.cos(a - 0.6), y + 0.5 * L), (x - L * math.cos(a - 0.5), y + L)],
                       L=12 * k, pairs=3)
    return svg_doc(F, W, H)


def swag(W=1000, H=100):
    """The top of the two curtains: from each side curtain's inner edge the fabric
    sweeps up and across to meet the other at the top centre, so the opening between
    them is a round arch (as in the satin-drapery reference). Folds are nested arches
    pulled toward each corner. Spans exactly between the side curtains' inner edges
    (script.js sets that) and stretches to fit (preserveAspectRatio none)."""
    F = Flora(11)
    K = 0.5523                            # cubic approximation of a quarter ellipse
    cx = W / 2

    def left(k):                          # quarter arch from (k*cx, 0) down to (0, k*H)
        a, b = k * cx, k * H
        return f"M{f(a)} 0C{f(a * (1 - K))} 0 0 {f(b * (1 - K))} 0 {f(b)}"

    def right(k):                         # mirror image, from (W - k*cx, 0) down to (W, k*H)
        a, b = k * cx, k * H
        return f"M{f(W - a)} 0C{f(W - a * (1 - K))} 0 {f(W)} {f(b * (1 - K))} {f(W)} {f(b)}"

    # fabric: everything above the arch whose apex is the top centre
    F.path(f"M0 0L{f(W)} 0L{f(W)} {f(H)}C{f(W)} {f(H * (1 - K))} {f(cx + cx * K)} 0 {f(cx)} 0"
           f"C{f(cx - cx * K)} 0 0 {f(H * (1 - K))} 0 {f(H)}Z", "fab")
    ks = [0.22, 0.4, 0.58, 0.76, 0.9]
    for i in range(0, len(ks) - 1, 2):    # shade alternate bands
        k0, k1 = ks[i], ks[i + 1]
        for side, fn in ((1, left), (-1, right)):
            a0, b0, a1, b1 = k0 * cx, k0 * H, k1 * cx, k1 * H
            if side == 1:
                d = (f"M{f(a0)} 0C{f(a0 * (1 - K))} 0 0 {f(b0 * (1 - K))} 0 {f(b0)}L0 {f(b1)}"
                     f"C0 {f(b1 * (1 - K))} {f(a1 * (1 - K))} 0 {f(a1)} 0Z")
            else:
                d = (f"M{f(W - a0)} 0C{f(W - a0 * (1 - K))} 0 {f(W)} {f(b0 * (1 - K))} {f(W)} {f(b0)}L{f(W)} {f(b1)}"
                     f"C{f(W)} {f(b1 * (1 - K))} {f(W - a1 * (1 - K))} 0 {f(W - a1)} 0Z")
            F.path(d, "fabd")
    for k in ks:
        F.path(left(k), "d2"); F.path(right(k), "d2")
    F.path(left(1.0), "d"); F.path(right(1.0), "d")   # the arch's edge
    doc = svg_doc(F, W, H).replace('<svg ', '<svg preserveAspectRatio="none" ', 1)
    return doc.replace("<style>", "<style>path{vector-effect:non-scaling-stroke}", 1)


if __name__ == "__main__":
    out = sys.argv[1]
    for name, svg in (("drape-wide", tall_drape(160, 1720, 86, 0.76, 8, 1.0, 4)),
                      ("drape-narrow", tall_drape(84, 2020, 46, 0.76, 8, 0.55, 4))):
        open(f"{out}/{name}.svg", "w").write(svg)
        print(name, len(svg) // 1024, "KB")
    open(f"{out}/swag.svg", "w").write(swag())
    print("swag")

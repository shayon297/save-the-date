"""Recolour the watercolour rose arch (a stock image with a transparent background) for the card:
pink roses become varied shades of ivory/cream, leaves are softened toward the olive palette.
Usage: python3 tools-rose-arch.py OUT.png [WIDTH] SOURCE.webp, then save as assets/rose-arch.webp."""
from PIL import Image
import numpy as np, sys
src = sys.argv[3] if len(sys.argv) > 3 else "rose-arch-source.webp"
W = int(sys.argv[2]) if len(sys.argv) > 2 else 1400
im = Image.open(src).convert("RGBA")
im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
arr = np.asarray(im).astype(float)
rgb, a = arr[..., :3] / 255, arr[..., 3]
r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
mx, mn = rgb.max(-1), rgb.min(-1)
sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
pink = np.clip((r - g - 0.005) / 0.07, 0, 1) * np.clip(sat / 0.05, 0, 1)
lum = 0.3 * r + 0.59 * g + 0.11 * b
t = np.clip((lum - 0.3) / 0.7, 0, 1) ** 0.65
# warm sand shadows -> soft cream mid-tones -> ivory highlights
shadow = np.array([188, 168, 132.0]) / 255
mid = np.array([236, 224, 198.0]) / 255
light = np.array([255, 252, 243.0]) / 255
lo = shadow[None, None] + (mid - shadow)[None, None] * np.clip(t / 0.55, 0, 1)[..., None]
hi = mid[None, None] + (light - mid)[None, None] * np.clip((t - 0.55) / 0.45, 0, 1)[..., None]
ivory = np.where((t < 0.55)[..., None], lo, hi)

# give each rose its own shade of cream: find the roses (blobs of rose colour) and tint each one
from collections import deque
step = 6
small = pink[::step, ::step] > 0.35
seen = np.zeros_like(small, bool); cents = []
for y0 in range(small.shape[0]):
    for x0 in range(small.shape[1]):
        if small[y0, x0] and not seen[y0, x0]:
            q = deque([(y0, x0)]); seen[y0, x0] = True; pts = []
            while q:
                y, x = q.popleft(); pts.append((y, x))
                for dy, dx in ((1,0),(-1,0),(0,1),(0,-1)):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < small.shape[0] and 0 <= xx < small.shape[1] and small[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True; q.append((yy, xx))
            if len(pts) > 12:
                p = np.array(pts); cents.append((p[:, 0].mean() * step, p[:, 1].mean() * step))
# shades: (multiplier on the cream, applied mostly in the mid-tones and shadows)
tints = [np.array(v) for v in ([1.0, 1.0, 1.0],          # warm ivory
                               [1.0, 0.975, 0.93],       # champagne
                               [1.0, 0.965, 0.955],      # soft blush cream
                               [1.0, 0.99, 0.9],         # butter
                               [0.985, 0.99, 1.0])]      # pearl
order = sorted(range(len(cents)), key=lambda i: cents[i][1])
choice = {}
seq = [0, 2, 1, 4, 3, 1, 0, 3, 2, 4, 1, 0]
for k, i in enumerate(order): choice[i] = seq[k % len(seq)]
if cents:
    yy, xx = np.mgrid[0:pink.shape[0], 0:pink.shape[1]]
    C = np.array(cents)
    d = (yy[..., None] - C[None, None, :, 0]) ** 2 + (xx[..., None] - C[None, None, :, 1]) ** 2
    near = d.argmin(-1)
    mult = np.stack([tints[choice[i]] for i in range(len(cents))])[near]
    depth = (1 - t)[..., None] * 0.7 + 0.3          # stronger in the shadows, gentle in highlights
    ivory = ivory * (1 - depth + depth * mult)
print(len(cents), "roses")
out = rgb * (1 - pink[..., None]) + ivory * pink[..., None]
leaf = 1 - pink
grey = out.mean(-1, keepdims=True)
out = out * (1 - 0.25 * leaf[..., None]) + grey * (0.25 * leaf[..., None])
Image.fromarray(np.dstack([(out.clip(0, 1) * 255), a]).astype("uint8"), "RGBA").save(sys.argv[1], optimize=True)

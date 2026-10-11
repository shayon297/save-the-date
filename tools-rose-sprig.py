"""Builds assets/rose-sprig.webp from the recoloured arch (.ba/arch-ivory.png or a path given):
the three centre roses, cut cleanly, with one complete leafy vine from the arch tucked
behind each outer rose so every visible leaf ends naturally."""
import sys
from PIL import Image
import numpy as np
src = sys.argv[1] if len(sys.argv) > 1 else ".ba/arch-ivory.png"
im = Image.open(src); H = im.size[1]

# three centre roses
x0 = 530
a = np.asarray(im.crop((x0, 0, 870, int(H * 0.2)))).astype(float)
rgb, al = a[..., :3], a[..., 3]
X = np.arange(a.shape[1])[None, :] + x0
cream = (rgb[..., 0] > 175) & (rgb[..., 0] - rgb[..., 1] < 30) & (rgb[..., 1] > 160) & (al > 30)
roses = cream & (X >= 548) & (X <= 852)
keep = np.zeros_like(roses)
for x in range(roses.shape[1]):
    ys = np.where(roses[:, x])[0]
    if len(ys): keep[ys.min():ys.max() + 1, x] = True
for _ in range(2):
    k = keep.copy(); k[1:] |= keep[:-1]; k[:-1] |= keep[1:]; k[:, 1:] |= keep[:, :-1]; k[:, :-1] |= keep[:, 1:]; keep = k
al[~keep] = 0
notcream = ~((rgb[..., 0] > 165) & (rgb[..., 0] - rgb[..., 1] < 32) & (rgb[..., 1] > 150))
al[notcream & (rgb[..., 1] > rgb[..., 0])] = 0
c = (~notcream) & (al > 30)
for x in range(a.shape[1]):
    ys = np.where(c[:, x])[0]
    if len(ys): al[ys.max() + 1:, x] = 0
a[..., 3] = al
r = Image.fromarray(a.clip(0, 255).astype("uint8"), "RGBA"); r = r.crop(r.getbbox())
ra = np.asarray(r).astype(float); h = ra.shape[0]
dark = ra[..., :3].mean(-1) < 200
ra[int(h * 0.82):, :, 3][dark[int(h * 0.82):, :]] = 0
roses = Image.fromarray(ra.clip(0, 255).astype("uint8"), "RGBA"); roses = roses.crop(roses.getbbox())

# one leafy vine from the arch's right side (ends naturally in leaf tips)
v = np.asarray(im.crop((1255, 250, 1398, 340))).astype(float)
vr = v[..., :3]
v[..., 3][(vr[..., 0] > 175) & (vr[..., 0] - vr[..., 1] < 30) & (vr[..., 1] > 160)] = 0
vine = Image.fromarray(v.astype("uint8"), "RGBA"); vine = vine.crop(vine.getbbox())
v = np.asarray(vine).astype(float); v[:12, :40, 3] = 0; v[58:, :16, 3] = 0
vine = Image.fromarray(v.astype("uint8"), "RGBA"); vine = vine.crop(vine.getbbox())

rw, rh = roses.size; vw, vh = vine.size; tuck = 46
W = rw + 2 * (vw - tuck); Hc = max(rh, vh + 30)
canvas = Image.new("RGBA", (W, Hc), (0, 0, 0, 0))
ry = (Hc - rh) // 2; vy = ry + int(rh * 0.42) - vh // 2
canvas.alpha_composite(vine, (W - vw, vy))
canvas.alpha_composite(vine.transpose(Image.FLIP_LEFT_RIGHT), (0, vy))
canvas.alpha_composite(roses, ((W - rw) // 2, ry))
canvas = canvas.crop(canvas.getbbox())
canvas.save("assets/rose-sprig.webp", "WEBP", quality=90, method=6)
print("rose-sprig", canvas.size)

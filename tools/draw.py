# -*- coding: utf-8 -*-
"""draw.py — every picture on the site, computed. numpy + PIL, no photographs.

    python3 tools/draw.py            # all
    python3 tools/draw.py hero cards # some

The long-exposure pictures splat millions of points along road curves into a float
buffer, bloom it with an FFT Gaussian, and tone-map. The data pictures read
build/series.json and build/facts.json, so they redraw with the numbers.
"""
import hashlib, json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "build", "img")
os.makedirs(OUT, exist_ok=True)
RNG = np.random.default_rng(20260923)
DIN = "/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf"
DINA = "/System/Library/Fonts/Supplemental/DIN Alternate Bold.ttf"
THAI = "/System/Library/Fonts/ThonburiUI.ttc"
MONO = "/System/Library/Fonts/Menlo.ttc"


def font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception:
        return ImageFont.load_default()


# ------------------------------------------------------------------ the light engine
class Film:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.buf = np.zeros((h * w, 3), np.float64)

    def splat(self, xs, ys, col, wt=1.0):
        xs = np.asarray(xs, float); ys = np.asarray(ys, float)
        wt = np.broadcast_to(np.asarray(wt, float), xs.shape)
        ok = (xs >= 0) & (xs < self.w - 1) & (ys >= 0) & (ys < self.h - 1) & np.isfinite(xs) & np.isfinite(ys)
        xs, ys, wt = xs[ok], ys[ok], wt[ok]
        x0 = np.floor(xs).astype(np.int64); y0 = np.floor(ys).astype(np.int64)
        fx = xs - x0; fy = ys - y0
        n = self.w * self.h
        for dx, dy, ww in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
            idx = (y0 + dy) * self.w + (x0 + dx)
            acc = np.bincount(idx, weights=ww * wt, minlength=n)
            for c in range(3):
                if col[c]:
                    self.buf[:, c] += acc * col[c]

    def glow(self, x, y, r, col, amt=1.0):
        """a soft disc, for lamps and bokeh"""
        yy, xx = np.mgrid[-int(3 * r):int(3 * r) + 1, -int(3 * r):int(3 * r) + 1]
        g = np.exp(-(xx ** 2 + yy ** 2) / (2 * r * r)) * amt
        self.splat((x + xx).ravel(), (y + yy).ravel(), col, g.ravel())

    def image(self, exposure=1.0, bloom=((4, .5), (16, .3), (55, .07)), gamma=1 / 2.2, bg=None):
        img = self.buf.reshape(self.h, self.w, 3).copy()
        if bg is not None:
            img += bg
        acc = img.copy()
        for s, a in bloom:
            acc += a * blur(img, s)
        out = 1 - np.exp(-acc * exposure)
        out = np.clip(out, 0, 1) ** gamma
        return Image.fromarray((out * 255).astype(np.uint8))


def blur(img, sigma):
    h, w, _ = img.shape
    ph, pw = h + int(4 * sigma), w + int(4 * sigma)
    fy = np.fft.fftfreq(ph)[:, None]; fx = np.fft.rfftfreq(pw)[None, :]
    k = np.exp(-2 * (math.pi * sigma) ** 2 * (fx ** 2 + fy ** 2))
    out = np.empty_like(img)
    for c in range(3):
        F = np.fft.rfft2(img[:, :, c], s=(ph, pw))
        out[:, :, c] = np.fft.irfft2(F * k, s=(ph, pw))[:h, :w]
    return np.maximum(out, 0)


def sky(w, h, horizon, top=(0.002, 0.004, 0.016), low=(0.016, 0.011, 0.016), ground=(0.002, 0.002, 0.003)):
    y = np.linspace(0, 1, h)[:, None, None]
    t = np.clip(y / max(horizon / h, 1e-3), 0, 1) ** 2
    g = np.clip((y - horizon / h) * 12, 0, 1)
    c = np.array(top) * (1 - t) + np.array(low) * t
    return (c * (1 - g) + np.array(ground) * g) * np.ones((1, w, 1))


def hexcol(h, k=1.0):
    h = h.lstrip("#")
    return tuple(k * int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


HEAD = (1.0, 0.92, 0.78)
TAIL = (1.0, 0.12, 0.06)
AMBER = (1.0, 0.62, 0.12)
GREEN = (0.1, 0.85, 0.45)
BLUE = (0.25, 0.55, 1.0)


# ------------------------------------------------------------------ hero: the off-ramp at night
def persp_trails(film, cam, lanes, n=160000, zr=(6, 900)):
    W, H = film.w, film.h
    f, cx, hz, ch = cam
    for lane in lanes:
        path, col, amt, jit, cars = lane
        for car in range(cars):
            u = RNG.random(n)
            z = 1 / (1 / zr[0] + u * (1 / zr[1] - 1 / zr[0]))
            got = path(z)
            x, y, keep = got[:3]
            wz = got[3] if len(got) > 3 else np.ones_like(z)
            j = RNG.normal(0, jit)
            # a car's trail covers only part of the run, and the lights come in pairs
            a, b = sorted(RNG.random(2))
            if RNG.random() < .5:
                a, b = 0, 1
            m = keep & (u >= a) & (u <= b)
            for side in (-0.75, 0.75):
                sx = cx + f * (x[m] + j + side) / z[m]
                sy = hz + f * (ch - y[m]) / z[m]
                film.splat(sx, sy, col, wz[m] * amt * (0.7 + 30 / z[m]) / cars)


def hero(name="hero.jpg", W=2000, H=1125, ramp=True):
    W = int(os.environ.get("DRAW_W", W)); H = int(W * 9 / 16)
    film = Film(W, H)
    f, cx, hz, ch = W * 0.62, W * 0.47, H * 0.40, 16.0
    cam = (f, cx, hz, ch)
    road = lambda z: 26 * np.sin(z / 300.0) - 6 + 0.00002 * z * z
    lanes = []
    for i, off in enumerate((-12.5, -9.0, -5.5)):             # towards us: headlights
        lanes.append((lambda z, o=off: (road(z) + o, np.zeros_like(z), np.ones_like(z, bool)), HEAD, 1.9, .35, 7))
    for i, off in enumerate((1.5, 5.0, 8.5)):                 # away: tail lights
        lanes.append((lambda z, o=off: (road(z) + o, np.zeros_like(z), np.ones_like(z, bool)), TAIL, 3.4, .35, 7))
    if ramp:
        z0 = 16.0
        def rp(z, o=0.0):
            t = np.clip(z - z0, 0, None)
            x = road(z) + 8.5 + o * np.clip(t / 60, 0, 1) + 0.0010 * t ** 2 + 0.01 * t
            y = np.minimum(0.00035 * t ** 2, 11)
            fade = np.clip((360 - z) / 120, 0, 1)
            return x, y, (z > z0) & (z < 360), fade * fade * (3 - 2 * fade)
        lanes.append((lambda z: rp(z), AMBER, 3.6, .3, 9))
        lanes.append((lambda z: rp(z, 3.4), AMBER, 2.4, .3, 6))
    persp_trails(film, cam, lanes, n=140000)

    # sodium lamps along both verges, and on the ramp
    for z in np.arange(22, 900, 34.0):
        for side in (-17.5, -2.0, 13.5):
            x = road(z) + side
            sx = cx + f * x / z; sy = hz + f * (ch - 11) / z
            r = max(0.9, 60 / z)
            film.glow(sx, sy, r, AMBER, 4.0 * min(1, 40 / z) + 0.4)
            # the pool of light on the tarmac
            px = cx + f * x / z; py = hz + f * ch / z
            film.glow(px, py, r * 5, (0.5, 0.28, 0.06), 0.03 * min(1, 60 / z))
    # the city on the horizon
    k = 1400
    xs = RNG.uniform(0, W, k); ys = hz - np.abs(RNG.normal(0, H * .004, k)) - RNG.exponential(H * .002, k)
    tint = RNG.random(k)
    film.splat(xs[tint < .6], ys[tint < .6], AMBER, RNG.exponential(.25, (tint < .6).sum()))
    film.splat(xs[tint >= .6], ys[tint >= .6], HEAD, RNG.exponential(.18, (tint >= .6).sum()))
    for _ in range(18):
        film.glow(RNG.uniform(0, W), hz - RNG.uniform(2, H * .02), RNG.uniform(1.5, 3.5), AMBER, RNG.uniform(.2, .6))
    # stars
    k = 900
    film.splat(RNG.uniform(0, W, k), RNG.uniform(0, hz * .8, k), (0.8, 0.85, 1.0), RNG.exponential(.12, k))
    img = film.image(exposure=1.25, bg=sky(W, H, hz))

    if ramp:  # the green sign over the gore
        z = 150.0
        x = road(z) + 18.0
        sx = cx + f * x / z; sy = hz + f * (ch - 14) / z
        d = ImageDraw.Draw(img, "RGBA")
        sw, sh = int(W * .085), int(W * .041)
        box = (sx - sw / 2, sy - sh, sx + sw / 2, sy)
        d.rounded_rectangle(box, 10, fill=(8, 110, 62, 255), outline=(235, 245, 238, 255), width=4)
        d.rectangle((sx - 2, sy, sx + 2, sy + sh * 1.2), fill=(34, 38, 44, 255))
        k = sw / 190
        fnt = font(DIN, int(46 * k))
        d.text((sx - sw / 2 + 18 * k, sy - sh + 14 * k), "EXIT", font=fnt, fill=(240, 248, 242, 255))
        ax, ay = sx + 48 * k, sy - 26 * k
        d.line((ax - 18 * k, ay + 18 * k, ax + 22 * k, ay - 22 * k), fill=(240, 248, 242, 255), width=max(2, int(8 * k)))
        d.polygon([(ax + 30 * k, ay - 30 * k), (ax + 4 * k, ay - 26 * k), (ax + 26 * k, ay - 4 * k)], fill=(240, 248, 242, 255))
        g = img.filter(ImageFilter.GaussianBlur(18))
        img = Image.blend(img, Image.fromarray(np.maximum(np.asarray(img), np.asarray(g))), .35)
    img.save(os.path.join(OUT, name), quality=84, optimize=True, progressive=True)
    return img


# ------------------------------------------------------------------ the cloverleaf, from above
def cloverleaf(name="band-ramp.jpg", W=2000, H=750):
    film = Film(W, H)
    cx, cy, s = W * 0.5, H * 0.5, H * 0.34
    n = 60000
    def put(px, py, col, amt, jit=.012, cars=5):
        for _ in range(cars):
            j = RNG.normal(0, jit)
            film.splat(cx + s * (px + j), cy + s * (py + j * .5), col, amt / cars)
    t = np.linspace(-3.2, 3.2, n)
    for off, col in ((-.11, HEAD), (-.06, HEAD), (.06, TAIL), (.11, TAIL)):
        put(t * 1.0, np.full(n, off), col, 0.9)                 # the east-west road
        put(np.full(n, off), t * .6, col, 0.9)                  # north-south
    th = np.linspace(0, 1.5 * math.pi, n)
    R = .42
    for qx, qy, a0 in ((1, 1, math.pi), (-1, 1, -math.pi / 2), (-1, -1, 0), (1, -1, math.pi / 2)):
        ox, oy = qx * (R + .16), qy * (R + .16)
        put(ox + R * np.cos(th + a0), oy + R * np.sin(th + a0), AMBER, 2.6, .01, 6)
    # outer ramps, the long way round
    for qx, qy in ((1, 1), (-1, -1), (1, -1), (-1, 1)):
        u = np.linspace(0, 1, n)
        px = qx * (0.2 + 1.3 * u - 0.55 * u ** 2)
        py = qy * (0.2 + 0.08 + 1.3 * (1 - u) ** 2 * 0 + 0.9 * u ** 1.6)
        put(px, py * 0.62, GREEN, 1.3, .008, 4)
    for x in np.linspace(-3, 3, 29):
        for y in (-.2, .2):
            film.glow(cx + s * x, cy + s * y, 1.6, AMBER, .5)
    img = film.image(exposure=1.3, bloom=((3, .5), (14, .3), (40, .05)), bg=np.array((0.002, 0.003, 0.007)) * np.ones((H, W, 3)))
    img.save(os.path.join(OUT, name), quality=84, optimize=True, progressive=True)


# ------------------------------------------------------------------ bitcoin in baht, as a trail
def ridge(name="band-markets.jpg", W=2000, H=750):
    S = json.load(open(os.path.join(ROOT, "build", "series.json")))
    pts = S["btc_thb"]
    ys = np.log10(np.array([p[1] for p in pts]))
    n0 = len(pts)
    x = np.linspace(W * .03, W * .97, n0)
    y = H * .86 - (ys - ys.min()) / (ys.max() - ys.min()) * H * .66
    film = Film(W, H)
    # interpolate densely so the line is continuous
    k = 30
    xi = np.interp(np.linspace(0, n0 - 1, n0 * k), np.arange(n0), x)
    yi = np.interp(np.linspace(0, n0 - 1, n0 * k), np.arange(n0), y)
    film.splat(xi, yi, AMBER, 2.2)
    film.splat(xi, yi - 1, HEAD, 0.9)
    # the fill below it: vertical fibres, fading with depth
    sel = np.arange(0, len(xi), 3)
    t = np.linspace(0, 1, 40)[None, :]
    dd = (H - yi[sel])[:, None] * t
    film.splat(np.repeat(xi[sel], 40), (yi[sel][:, None] + dd).ravel(), (0.8, 0.35, 0.05), (0.012 * np.exp(-dd / (H * .25))).ravel())
    # the halvings, as green posts
    import datetime as dt
    d0 = dt.date.fromisoformat(pts[0][0]); d1 = dt.date.fromisoformat(pts[-1][0])
    for hd in ("2020-05-11", "2024-04-20"):
        fx_ = W * .03 + (dt.date.fromisoformat(hd) - d0).days / (d1 - d0).days * W * .94
        film.splat(np.full(900, fx_), np.linspace(H * .12, H * .92, 900), GREEN, .5)
    img = film.image(exposure=1.1, bg=np.array((0.005, 0.007, 0.014)) * np.ones((H, W, 3)))
    d = ImageDraw.Draw(img)
    fnt = font(DIN, 30)
    for yr in range(d0.year + 1, d1.year + 1):
        fx_ = W * .03 + (dt.date(yr, 1, 1) - d0).days / (d1 - d0).days * W * .94
        d.text((fx_ + 6, H - 44), str(yr), font=fnt, fill=(120, 130, 140))
        d.line((fx_, H - 50, fx_, H - 14), fill=(60, 66, 76), width=1)
    img.save(os.path.join(OUT, name), quality=84, optimize=True, progressive=True)


# ------------------------------------------------------------------ stablecoins to chains, as fibres
def fibres(name="band-networks.jpg", W=2000, H=750):
    Fx = json.load(open(os.path.join(ROOT, "build", "facts.json")))
    film = Film(W, H)
    CH = {"Tron": "#ff4d4d", "Ethereum": "#8ea2ff", "BSC": "#f3ba2f", "Solana": "#19fb9b", "Base": "#2f6bff",
          "Arbitrum": "#28a0f0", "Hyperliquid L1": "#97fce4", "Plasma": "#c9a0ff", "TON": "#34a6ff", "Polygon": "#8247e5"}
    flows = []
    for a in Fx["stable"]["top"][:2]:
        for c, v, sh in a["chains"][:5]:
            flows.append((a["symbol"], c, v))
    total = sum(v for _, _, v in flows)
    left = {}
    y = H * .1
    for sym in ("USDT", "USDC"):
        tot = sum(v for s, _, v in flows if s == sym)
        left[sym] = [y, tot]
        y += tot / total * H * .74 + H * .06
    right = {}
    chains = []
    for _, c, v in flows:
        if c not in chains: chains.append(c)
    chains.sort(key=lambda c: -sum(v for _, cc, v in flows if cc == c))
    y = H * .08
    for c in chains:
        tot = sum(v for _, cc, v in flows if cc == c)
        right[c] = [y, tot]
        y += tot / total * H * .74 + H * .025
    xl, xr = W * .12, W * .88
    ly = {k: v[0] for k, v in left.items()}; ry = {k: v[0] for k, v in right.items()}
    for s, c, v in sorted(flows, key=lambda z: -z[2]):
        h = v / total * H * .74
        y0 = ly[s]; y1 = ry[c]; ly[s] += h; ry[c] += h
        col = hexcol(CH.get(c, "#cccccc"))
        m = max(3, int(h / 7))
        i = np.arange(m)[:, None]
        f0 = y0 + h * (i + .5) / m; f1 = y1 + h * (i + .5) / m
        t = np.linspace(0, 1, 2600)[None, :]
        e = t * t * (3 - 2 * t)
        xs = np.broadcast_to(xl + (xr - xl) * t, (m, 2600))
        ys = f0 + (f1 - f0) * e
        wt = np.broadcast_to(0.9 * (0.5 + 0.5 * RNG.random((m, 1))), (m, 2600))
        film.splat(xs.ravel(), ys.ravel(), col, wt.ravel())
    img = film.image(exposure=1.3, bloom=((2.5, .6), (10, .35), (40, .06)), bg=np.array((0.002, 0.003, 0.008)) * np.ones((H, W, 3)))
    d = ImageDraw.Draw(img)
    fb = font(DIN, 44); fs = font(DIN, 30)
    for s, (y0, tot) in left.items():
        d.text((W * .02, y0 + tot / total * H * .37 - 22), s, font=fb, fill=(240, 240, 235))
    for c, (y0, tot) in right.items():
        hh = tot / total * H * .74
        if hh > 14:
            d.text((xr + 14, y0 + hh / 2 - 16), c, font=fs, fill=(220, 225, 230))
    img.save(os.path.join(OUT, name), quality=84, optimize=True, progressive=True)


# ------------------------------------------------------------------ the checkpoint: lanes into gates
def tollgate(name="band-rules.jpg", W=2000, H=750):
    film = Film(W, H)
    f, cx, hz, ch = W * 0.55, W * 0.5, H * 0.30, 7.0
    gz = 220.0
    lanes = []
    gates = np.linspace(-26, 26, 12)
    for g in gates:
        for src in (-5, -1.5, 1.5, 5):
            if RNG.random() < .35: continue
            def path(z, g=g, src=src):
                t = np.clip((z - 20) / (gz - 20), 0, 1)
                e = t * t * (3 - 2 * t)
                x = src * 1.4 + (g - src * 1.4) * e
                t2 = np.clip((z - gz) / 260, 0, 1)
                e2 = t2 * t2 * (3 - 2 * t2)
                x = np.where(z > gz, g + (src * 1.2 - g) * e2, x)
                return x, np.zeros_like(z), np.ones_like(z, bool)
            lanes.append((path, TAIL if src > 0 else AMBER, 0.55, .15, 3))
    persp_trails(film, (f, cx, hz, ch), lanes, n=90000, zr=(12, 900))
    # the booths, lit
    for g in gates:
        for dz in (0,):
            z = gz + dz
            sx = cx + f * (g + 2.2) / z; sy = hz + f * (ch - 3) / z
            film.glow(sx, sy, 2.5, GREEN, 2.2)
            film.glow(sx, hz + f * (ch - 6.5) / z, 1.8, HEAD, 1.2)
    # the canopy
    xs = np.linspace(-32, 32, 5000)
    film.splat(cx + f * xs / gz, np.full(5000, hz + f * (ch - 8) / gz), HEAD, .5)
    img = film.image(exposure=1.2, bloom=((3, .5), (14, .3), (45, .05)), bg=sky(W, H, hz))
    img.save(os.path.join(OUT, name), quality=84, optimize=True, progressive=True)


# ------------------------------------------------------------------ cards, in thin-film colour
def holo(name="band-cards.jpg", W=2000, H=750):
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    img = np.zeros((H, W, 3)) + np.array((0.02, 0.025, 0.04))
    cards = [(-18, W * .20, H * .55), (-7, W * .38, H * .50), (4, W * .56, H * .52), (14, W * .74, H * .48)]
    cw, chh = 560, 353
    for i, (ang, ox, oy) in enumerate(cards):
        a = math.radians(ang)
        u = (xx - ox) * math.cos(a) + (yy - oy) * math.sin(a)
        v = -(xx - ox) * math.sin(a) + (yy - oy) * math.cos(a)
        r = 26
        qx = np.maximum(np.abs(u) - (cw / 2 - r), 0); qy = np.maximum(np.abs(v) - (chh / 2 - r), 0)
        sd = np.sqrt(qx ** 2 + qy ** 2) - r
        mask = np.clip(0.5 - sd, 0, 1)
        # thickness field: slow waves, different per card
        t = 380 + 160 * np.sin(u / 97 + i) + 120 * np.sin(v / 61 - 2 * i) + 90 * np.sin((u + v) / 143 + i * 1.7)
        col = np.stack([0.5 + 0.5 * np.cos(4 * math.pi * 1.33 * t / lam + i) for lam in (650, 540, 460)], -1)
        base = hexcol(("#0b6b43", "#1b1f2a", "#2a1f3d", "#3a2a12")[i])
        film = 0.35 * col + 0.65 * np.array(base) * 1.4
        spec = np.exp(-((u + v * .6 - 60) / 180) ** 2) * .35
        film = film + spec[..., None]
        # the chip
        chip = (np.abs(u + cw * .30) < 38) & (np.abs(v + 18) < 28)
        film[chip] = np.array((0.85, 0.68, 0.32)) * (0.9 + 0.1 * np.sin(v[chip] / 3))[:, None]
        # the number, as dots
        for k in range(16):
            dotu = -cw * .36 + k * 26 + (k // 4) * 14
            dots = (u - dotu) ** 2 + (v - 70) ** 2 < 36
            film[dots] = (0.92, 0.94, 0.95)
        shade = np.clip(1 - np.maximum(sd + 30, 0) / 60, 0, 1)
        img = img * (1 - 0.45 * shade[..., None] * (1 - mask[..., None])) * 1
        img = img * (1 - mask[..., None]) + film * mask[..., None]
    img = np.clip(img, 0, 1) ** (1 / 1.25)
    Image.fromarray((img * 255).astype(np.uint8)).save(os.path.join(OUT, name), quality=84, optimize=True, progressive=True)


# ------------------------------------------------------------------ the net
def web(name="band-scams.jpg", W=2000, H=750):  # stylecheck: allow — code: image file name
    film = Film(W, H)
    cx, cy = W * .62, H * .45
    spokes = 22
    ang = np.sort(RNG.uniform(0, 2 * math.pi, spokes))
    L = np.array([W * .9] * spokes)
    for a in ang:
        t = np.linspace(0, 1, 9000)
        film.splat(cx + t * W * .9 * math.cos(a), cy + t * W * .9 * math.sin(a) * .8, (0.8, 0.2, 0.2), .35)
    r = 18
    th = 0.0
    pts_x, pts_y = [], []
    while r < W * .8:
        for i in range(spokes):
            a0, a1 = ang[i], ang[(i + 1) % spokes] + (2 * math.pi if i == spokes - 1 else 0)
            t = np.linspace(0, 1, 400)
            sag = 1 - 0.08 * np.sin(math.pi * t)
            x0, y0 = math.cos(a0) * r, math.sin(a0) * r * .8
            x1, y1 = math.cos(a1) * (r + 3), math.sin(a1) * (r + 3) * .8
            xs = (x0 + (x1 - x0) * t) * sag; ys = (y0 + (y1 - y0) * t) * sag
            film.splat(cx + xs, cy + ys, (1.0, 0.25, 0.22), .25 * (1 + 60 / r))
            pts_x.append(cx + x0); pts_y.append(cy + y0)
        r *= 1.16
    # a few nodes caught in it
    idx = RNG.choice(len(pts_x), 40, replace=False)
    for i in idx:
        film.glow(pts_x[i], pts_y[i], 4, AMBER, 1.3)
    img = film.image(exposure=1.1, bg=np.array((0.012, 0.004, 0.006)) * np.ones((H, W, 3)))
    img.save(os.path.join(OUT, name), quality=84, optimize=True, progressive=True)


# ------------------------------------------------------------------ a chain of hashes from the genesis block
GENESIS = "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f"


# ------------------------------------------------------------------ frost over the exit: an exchange that stops withdrawals
def dendrite(L, depth=3):
    """one arm of a six-fold ice crystal: segments (x0, y0, x1, y1) from the centre along +x"""
    segs = [(0.0, 0.0, L, 0.0)]
    if depth == 0:
        return segs
    for k in range(1, 6):
        at = L * k / 6
        bl = L * .42 * (1 - k / 7)
        for s in (1, -1):
            a = s * math.pi / 3
            c, d = math.cos(a), math.sin(a)
            for x0, y0, x1, y1 in dendrite(bl, depth - 1):
                segs.append((at + x0 * c - y0 * d, x0 * d + y0 * c, at + x1 * c - y1 * d, x1 * d + y1 * c))
    return segs


def frost(name="band-frozen.jpg", W=2000, H=750):
    film = Film(W, H)
    ICE = (0.55, 0.82, 1.0)
    # the exit lane, faint, running under the ice
    t = np.linspace(0, 1, 60000)
    film.splat(W * (.05 + .9 * t), H * (.82 - .34 * t ** 1.6), AMBER, .05)
    film.splat(W * (.05 + .9 * t), H * (.86 - .34 * t ** 1.6), TAIL, .04)
    PX, PY, PW = [], [], []
    for _ in range(17):
        cx, cy = RNG.uniform(.3, 1.05) ** .7 * W, RNG.uniform(-.1, 1.1) * H
        L = RNG.uniform(30, 190) * (1.6 if cx > W * .55 else 1)
        rot = RNG.uniform(0, math.pi / 3)
        seg = np.array(dendrite(L, 2 if L < 90 else 3))
        n = np.maximum(8, (np.hypot(seg[:, 2] - seg[:, 0], seg[:, 3] - seg[:, 1]) * 3).astype(int))
        u = np.concatenate([np.linspace(0, 1, k) for k in n])
        s = np.repeat(np.arange(len(seg)), n)
        xs = seg[s, 0] + (seg[s, 2] - seg[s, 0]) * u
        ys = seg[s, 1] + (seg[s, 3] - seg[s, 1]) * u
        wt = .09 * (60 / L) ** .5
        for i in range(6):
            a = rot + i * math.pi / 3
            c, d = math.cos(a), math.sin(a)
            PX.append(cx + xs * c - ys * d); PY.append(cy + xs * d + ys * c); PW.append(np.full(len(xs), wt))
        film.glow(cx, cy, 3, (0.8, 0.92, 1.0), .5)
    film.splat(np.concatenate(PX), np.concatenate(PY), ICE, np.concatenate(PW))
    img = film.image(exposure=1.0, bloom=((3, .5), (14, .3), (50, .08)),
                     bg=np.array((0.003, 0.007, 0.016)) * np.ones((H, W, 3)))
    img.save(os.path.join(OUT, name), quality=84, optimize=True, progressive=True)


def chain(name="band-history.jpg", W=2000, H=750):
    img = Image.new("RGB", (W, H), (6, 8, 14))
    d = ImageDraw.Draw(img)
    h = bytes.fromhex(GENESIS)
    cell = 11
    bw = 8 * cell
    cols = W // (bw + 22) + 1
    rows = 5
    y0 = 40
    fnt = font(MONO, 16)
    for r in range(rows):
        for c in range(cols):
            x = 20 + c * (bw + 22) + (r % 2) * 40
            y = y0 + r * (4 * cell + 96)
            for i, b in enumerate(h):
                gx, gy = i % 8, i // 8
                v = b / 255
                col = (int(255 * (0.15 + 0.85 * v)), int(255 * (0.35 + 0.5 * v * v)), int(255 * (0.1 + 0.25 * (1 - v)))) if b & 1 else \
                      (int(30 + 60 * v), int(140 + 110 * v), int(110 + 80 * v))
                if b == 0:
                    col = (22, 26, 34)
                d.rectangle((x + gx * cell, y + gy * cell, x + gx * cell + cell - 2, y + gy * cell + cell - 2), fill=col)
            d.text((x, y + 4 * cell + 8), h.hex()[:10], font=fnt, fill=(90, 100, 110))
            if c < cols - 1:
                d.line((x + bw + 2, y + 2 * cell, x + bw + 20, y + 2 * cell), fill=(60, 70, 80), width=2)
            h = hashlib.sha256(hashlib.sha256(h).digest()).digest()
    g = img.filter(ImageFilter.GaussianBlur(6))
    img = Image.fromarray(np.clip(np.asarray(img, float) + 0.6 * np.asarray(g, float), 0, 255).astype(np.uint8))
    img.save(os.path.join(OUT, name), quality=84, optimize=True, progressive=True)


# ------------------------------------------------------------------ avalanche: one character in, half the bits out
def avalanche(name="band-how.jpg", W=2000, H=750):
    cell = 7
    cols, rows = 256, H // cell
    img = np.zeros((rows * cell, cols * cell, 3), np.uint8) + np.array((6, 8, 14), np.uint8)
    prev = None
    for r in range(rows):
        dg = hashlib.sha256(("offrampt %d" % r).encode()).digest()
        bits = np.unpackbits(np.frombuffer(dg, np.uint8))
        for c in range(cols):
            b = bits[c]
            flip = prev is not None and prev[c] != b
            col = (255, 170, 40) if flip and b else (255, 90, 70) if flip else (30, 160, 100) if b else (16, 22, 30)
            img[r * cell:(r + 1) * cell - 1, c * cell:(c + 1) * cell - 1] = col
        prev = bits
    im = Image.fromarray(img).resize((W, H), Image.NEAREST)
    g = im.filter(ImageFilter.GaussianBlur(8))
    im = Image.fromarray(np.clip(np.asarray(im, float) * .55 + .35 * np.asarray(g, float), 0, 255).astype(np.uint8))
    im.save(os.path.join(OUT, name), quality=84, optimize=True, progressive=True)


# ------------------------------------------------------------------ words, as signs
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def signs(name="band-words.jpg", W=2000, H=750):
    """Thai needs shaping, which this PIL lacks, so the browser sets the type and PIL only saves it."""
    import subprocess, tempfile
    words = [("สินทรัพย์ดิจิทัล", "th", "#2fd27f"), ("STABLECOIN", "en", "#ffb13b"), ("บัญชีม้า", "th", "#ff5a5f"),
             ("SEED PHRASE", "en", "#fff1d6"), ("พร้อมเพย์", "th", "#5aa9ff"), ("NETWORK", "en", "#2fd27f"),
             ("คริปโทเคอร์เรนซี", "th", "#ffb13b"), ("OFF-RAMP", "en", "#ffb13b"), ("กระเป๋าเงินดิจิทัล", "th", "#fff1d6"),
             ("P2P", "en", "#ff5a5f"), ("KYC", "en", "#5aa9ff"), ("ภาษี", "th", "#2fd27f"), ("GAS", "en", "#fff1d6"),
             ("บิตคอยน์", "th", "#ffb13b"), ("USDT", "en", "#2fd27f"), ("ADDRESS", "en", "#5aa9ff"), ("เหรียญคงที่", "th", "#b69cff"),
             ("LEDGER", "en", "#b69cff"), ("แลกเงิน", "th", "#ff5a5f"), ("BAHT", "en", "#2fd27f")]
    spans = []
    for i, (w, lang, col) in enumerate(words * 2):
        size = int(RNG.uniform(64, 118))
        fam = "'Sukhumvit Set','Thonburi'" if lang == "th" else "'DIN Condensed'"
        wt = 600 if lang == "th" else 700
        spans.append('<span style="font-family:%s;font-weight:%d;font-size:%dpx;color:%s;text-shadow:0 0 12px %s,0 0 36px %s,0 0 80px %s">%s</span>'
                     % (fam, wt, size, col, col, col, col + "88", w))
    doc = ('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:#06080e;width:%dpx;height:%dpx;overflow:hidden}'
           'div{display:flex;flex-wrap:wrap;gap:18px 64px;align-items:baseline;padding:26px 30px;line-height:1.15}</style><div>%s</div>' % (W, H, "".join(spans)))
    tmp = tempfile.mkdtemp()
    hp = os.path.join(tmp, "w.html"); pp = os.path.join(tmp, "w.png")
    open(hp, "w", encoding="utf-8").write(doc)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--window-size=%d,%d" % (W, H), "--screenshot=" + pp, "file://" + hp], capture_output=True, timeout=120)
    Image.open(pp).convert("RGB").crop((0, 0, W, H)).save(os.path.join(OUT, name), quality=84, optimize=True, progressive=True)


# ------------------------------------------------------------------ addresses, by network
def glyphs(name="band-tools.jpg", W=2000, H=750):
    img = Image.new("RGB", (W, H), (6, 8, 14))
    d = ImageDraw.Draw(img)
    fnt = font(MONO, 22)
    kinds = [("bc1q", "023456789acdefghjklmnpqrstuvwxyz", AMBER), ("0x", "0123456789abcdef", BLUE),
             ("T", "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz", (1, .3, .25)),
             ("", "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz", GREEN)]
    y = 10
    i = 0
    while y < H:
        x = RNG.uniform(-300, 0)
        while x < W:
            pre, alpha, col = kinds[RNG.integers(0, 4)]
            n = {"bc1q": 38, "0x": 40, "T": 33, "": 43}[pre]
            s = pre + "".join(alpha[RNG.integers(0, len(alpha))] for _ in range(n))
            k = RNG.uniform(.25, 1)
            d.text((x, y), s, font=fnt, fill=tuple(int(255 * v * k) for v in col))
            x += d.textlength(s, font=fnt) + 40
        y += 34; i += 1
    g = img.filter(ImageFilter.GaussianBlur(7))
    a = np.asarray(img, float) * .7 + np.asarray(g, float) * .8
    Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(os.path.join(OUT, name), quality=84, optimize=True, progressive=True)


def card(src="hero.jpg"):
    im = Image.open(os.path.join(OUT, src)).convert("RGB")
    w, h = im.size
    im = im.resize((1200, int(1200 * h / w)), Image.LANCZOS).crop((0, 20, 1200, 650))
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle((0, 380, 1200, 630), fill=(4, 6, 10, 170))
    d.rounded_rectangle((60, 420, 110, 470), 8, fill=(8, 110, 62), outline=(235, 245, 238), width=3)
    d.line((74, 456, 96, 434), fill=(240, 248, 242), width=5)
    d.polygon([(100, 430), (86, 432), (98, 444)], fill=(240, 248, 242))
    d.text((128, 404), "OFFRAMPT", font=font(DIN, 92), fill=(240, 244, 240))
    d.text((64, 510), "Crypto in Thailand, and the ways out to baht.", font=font(DINA, 40), fill=(255, 190, 90))
    d.text((64, 566), "offrampt.net", font=font(DINA, 30), fill=(170, 180, 186))
    im.save(os.path.join(OUT, "card.jpg"), quality=86, optimize=True)


def card_th():
    """the Thai share card: the browser sets the Thai line, since this PIL cannot shape Thai"""
    import subprocess, tempfile, base64
    src = os.path.join(OUT, "card.jpg")
    b64 = base64.b64encode(open(src, "rb").read()).decode()
    doc = ('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;width:1200px;height:630px;overflow:hidden;background:#000}'
           'img{position:absolute;inset:0}div{position:absolute;left:0;right:0;top:500px;height:130px;background:#04060a}'
           'p{position:absolute;left:64px;top:498px;margin:0;font:600 44px "Sukhumvit Set","Thonburi";color:#ffbe5a}'
           'span{position:absolute;left:64px;top:566px;font:700 30px "DIN Alternate";color:#aab4ba}</style>'
           '<img src="data:image/jpeg;base64,%s"><div></div><p>คริปโตในไทย และทางออกสู่เงินบาท</p><span>offrampt.net/th</span>' % b64)
    tmp = tempfile.mkdtemp()
    hp, pp = os.path.join(tmp, "c.html"), os.path.join(tmp, "c.png")
    open(hp, "w", encoding="utf-8").write(doc)
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    "--window-size=1200,630", "--screenshot=" + pp, "file://" + hp], capture_output=True, timeout=120)
    Image.open(pp).convert("RGB").crop((0, 0, 1200, 630)).save(os.path.join(OUT, "card-th.jpg"), quality=86, optimize=True)


JOBS = {"hero": hero, "ramp": cloverleaf, "markets": ridge, "networks": fibres, "rules": tollgate, "cards": holo,
        "scams": web, "history": chain, "how": avalanche, "words": signs, "tools": glyphs, "frozen": frost, "card": card, "card_th": card_th}  # stylecheck: allow — code: page keys

if __name__ == "__main__":
    want = sys.argv[1:] or list(JOBS)
    for k in want:
        JOBS[k]()
        print("  drew", k)

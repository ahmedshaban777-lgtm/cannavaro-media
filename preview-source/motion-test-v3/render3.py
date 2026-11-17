#!/usr/bin/env python3
"""Cannavaro 2D motion test v3 - quiet luxury direction.
Charcoal stage, thin cream linework, one orange thread connecting
site -> content -> ads, star motif, CANNAVARO finale. Silent.
Usage: python3 render3.py [out_dir] [start_frame] [end_frame]
"""
import math, os, sys
from PIL import Image, ImageDraw, ImageFont

SS = 2
W, H = 1920, 1080
FPS = 30
DUR = 10.5
NFRAMES = int(FPS * DUR)

CREAM = (255, 246, 236)
INK = (22, 22, 24)
ORANGE = (255, 77, 0)

HERE = os.path.dirname(os.path.abspath(__file__))
ANTON = os.path.join(HERE, "anton-latin.woff2")
CAIRO = os.path.join(HERE, "cairo-arabic-full.ttf")

def sc(v): return int(round(v * SS))
def clamp(v, a=0.0, b=1.0): return max(a, min(b, v))
def lerp(a, b, p): return a + (b - a) * p
def prog(t, a, b): return clamp((t - a) / (b - a))
def eo(p): return 1 - (1 - p) ** 3
def eio(p): return 4*p*p*p if p < 0.5 else 1 - (-2*p + 2) ** 3 / 2
def eo_back(p, s=1.2): return 1 + (s + 1) * (p - 1) ** 3 + s * (p - 1) ** 2

def cr(c, a): return (c[0], c[1], c[2], int(a))

STAR_BASE = [(30,0),(36,22),(58,30),(36,38),(30,60),(24,38),(2,30),(24,22)]
def star_pts(cx, cy, r, rot):
    pts = [((x-30)/30.0*r, (y-30)/30.0*r) for x, y in STAR_BASE]
    rr = math.radians(rot); c, s = math.cos(rr), math.sin(rr)
    return [(sc(cx + x*c - y*s), sc(cy + x*s + y*c)) for x, y in pts]

def qbez(p0, p1, p2, n=48):
    out = []
    for i in range(n + 1):
        u = i / n
        x = (1-u)**2*p0[0] + 2*(1-u)*u*p1[0] + u*u*p2[0]
        y = (1-u)**2*p0[1] + 2*(1-u)*u*p1[1] + u*u*p2[1]
        out.append((x, y))
    return out

def draw_partial(d, pts, p, color, width):
    if p <= 0: return
    n = max(2, int(len(pts) * clamp(p)))
    seg = [(sc(x), sc(y)) for x, y in pts[:n]]
    if len(seg) >= 2:
        d.line(seg, fill=color, width=sc(width), joint="curve")

def poly_progress_draw(d, pts, p, color, width):
    """pts: polyline; draw first p fraction by arc length."""
    if p <= 0: return
    lens = [0.0]
    for i in range(1, len(pts)):
        lens.append(lens[-1] + math.dist(pts[i-1], pts[i]))
    total = lens[-1]; target = total * clamp(p)
    seg = [pts[0]]
    for i in range(1, len(pts)):
        if lens[i] <= target:
            seg.append(pts[i])
        else:
            f = (target - lens[i-1]) / max(1e-6, lens[i] - lens[i-1])
            seg.append((lerp(pts[i-1][0], pts[i][0], f), lerp(pts[i-1][1], pts[i][1], f)))
            break
    if len(seg) >= 2:
        d.line([(sc(x), sc(y)) for x, y in seg], fill=color, width=sc(width), joint="curve")

# ------------------------------------------------------------------- layers
def make_base():
    im = Image.new("RGBA", (sc(W), sc(H)), INK + (255,))
    return im

_vig = None
_grain = []
def vignette():
    global _vig
    if _vig is None:
        m = Image.new("L", (480, 270), 0)
        px = m.load()
        for y in range(270):
            for x in range(480):
                dx = (x - 240) / 240.0; dy = (y - 135) / 135.0
                r = math.sqrt(dx*dx + dy*dy)
                px[x, y] = int(clamp((r - 0.72) / 0.55) * 120)
        _vig = m.resize((sc(W), sc(H)), Image.BILINEAR)
    return _vig

def grain_layers():
    global _grain
    if not _grain:
        for _ in range(6):
            _grain.append(Image.frombytes("L", (sc(W)//2, sc(H)//2), os.urandom(sc(W)*sc(H)//4)).resize((sc(W), sc(H)), Image.NEAREST))
    return _grain

def finish(im, n):
    im = im.convert("RGB")
    g = grain_layers()[n % 6].point(lambda v: int(v / 255 * 14))
    im = Image.composite(Image.new("RGB", im.size, (255, 255, 255)), im, g)
    black = Image.new("RGB", im.size, (0, 0, 0))
    im = Image.composite(black, im, vignette())
    return im.resize((W, H), Image.LANCZOS)

# ------------------------------------------------------------------- pieces
def draw_window(alpha, perim_p, content_p):
    """thin-line browser window, progressive perimeter reveal."""
    lay = Image.new("RGBA", (sc(W), sc(H)), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay, "RGBA")
    x0, y0, x1, y1 = 210, 280, 830, 620
    per = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
    poly_progress_draw(d, per, perim_p, cr(CREAM, 235 * alpha), 3)
    if content_p > 0:
        ca = alpha * eo(content_p)
        # top dots
        for i, col in enumerate([ORANGE, CREAM, CREAM]):
            cx = 250 + i * 34
            d.ellipse([sc(cx-7), sc(302-7), sc(cx+7), sc(302+7)], fill=cr(col, 220 * ca))
        d.line([sc(210), sc(330), sc(830), sc(330)], fill=cr(CREAM, 90 * ca), width=sc(2))
        # hero block
        d.rounded_rectangle([sc(250), sc(370), sc(520), sc(560)], radius=sc(16), fill=cr(ORANGE, 215 * ca))
        # text lines
        for i, wln in enumerate([250, 210, 160]):
            yy = 392 + i * 56
            d.rounded_rectangle([sc(560), sc(yy), sc(560 + wln), sc(yy + 22)], radius=sc(11), fill=cr(CREAM, 130 * ca))
    return lay

def draw_card(cx, cy, w, h, rot, a, play=False):
    card = Image.new("RGBA", (sc(w + 80), sc(h + 80)), (0, 0, 0, 0))
    d = ImageDraw.Draw(card, "RGBA")
    d.rounded_rectangle([sc(40), sc(40), sc(40 + w), sc(40 + h)], radius=sc(18),
                        outline=cr(CREAM, 210 * a), width=sc(3), fill=cr(CREAM, 14 * a))
    if play:
        pts = [(sc(40 + w/2 - 16), sc(40 + h/2 - 22)), (sc(40 + w/2 - 16), sc(40 + h/2 + 22)), (sc(40 + w/2 + 24), sc(40 + h/2))]
        d.polygon(pts, fill=cr(ORANGE, 230 * a))
    else:
        for i, wln in enumerate([w - 90, w - 140]):
            yy = 40 + 52 + i * 44
            d.rounded_rectangle([sc(80), sc(yy), sc(80 + wln), sc(yy + 18)], radius=sc(9), fill=cr(CREAM, 120 * a))
        d.ellipse([sc(80), sc(40 + h - 58), sc(116), sc(40 + h - 22)], fill=cr(ORANGE, 200 * a))
    card = card.rotate(rot, resample=Image.BICUBIC, center=(sc((w + 80) / 2), sc((h + 80) / 2)))
    lay = Image.new("RGBA", (sc(W), sc(H)), (0, 0, 0, 0))
    lay.alpha_composite(card, (sc(cx - (w + 80) / 2), sc(cy - (h + 80) / 2)))
    return lay

def draw_bars(alpha, ps):
    lay = Image.new("RGBA", (sc(W), sc(H)), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay, "RGBA")
    base_y = 620
    heights = [130, 200, 95, 250, 165]
    for i, hh in enumerate(heights):
        p = eo(ps[i])
        if p <= 0: continue
        x0 = 1615 + i * 56
        col = ORANGE if i == 3 else CREAM
        aa = (235 if i == 3 else 185) * alpha
        hnow = hh * p
        d.rounded_rectangle([sc(x0), sc(base_y - hnow), sc(x0 + 36), sc(base_y)], radius=sc(9), fill=cr(col, aa))
    return lay

def word_layer(word, size, weight):
    f = ImageFont.truetype(CAIRO, sc(size), layout_engine=ImageFont.Layout.RAQM)
    f.set_variation_by_axes([weight])
    tmp = Image.new("RGBA", (10, 10)); td = ImageDraw.Draw(tmp)
    bb = td.textbbox((0, 0), word, font=f)
    wl = Image.new("RGBA", (bb[2] - bb[0] + sc(40), bb[3] - bb[1] + sc(40)), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wl)
    wd.text((sc(20) - bb[0], sc(20) - bb[1]), word, font=f, fill=CREAM + (255,))
    return wl

_grad = None
def reveal_mask(lay_size, p, feather=70):
    global _grad
    if _grad is None or _grad.size[1] != lay_size[1]:
        _grad = Image.linear_gradient("L").resize((8, lay_size[1]))
    hh = lay_size[1]
    fv = max(1.0, 255 * sc(feather) / hh)
    vb = 255 - (255 + fv) * clamp(p)   # at p=1 the feather band sits above the layer -> full opacity
    m = _grad.point(lambda v: int(clamp((v - vb) / fv) * 255))
    return m.resize(lay_size)

# ------------------------------------------------------------------- scenes
# stage positions
WIN_C = (520, 450)
CARDS = [(1030, 428, -3), (1245, 452, 2), (1460, 424, -2)]
THREAD1 = qbez((838, 450), (880, 400), (928, 434))
THREAD2 = qbez((1568, 468), (1590, 520), (1620, 560))
SWEEP = qbez((260, 380), (960, 300), (1660, 380), n=90)

def render_frame(t, fonts, n):
    f_word, f_kick, f_anton, w_caches = fonts
    im = make_base()
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov, "RGBA")

    # S0 hairline + twinkle star
    lp = eo(prog(t, 0.15, 0.85)); lf = 1 - prog(t, 1.35, 1.75)
    if lf > 0 and lp > 0:
        x_to = lerp(560, 1360, lp)
        d.line([sc(560), sc(540), sc(x_to), sc(540)], fill=cr(ORANGE, 235 * lf), width=sc(2))
    sp = eo_back(prog(t, 0.9, 1.05)); sf = 1 - prog(t, 1.5, 1.9)
    if sf > 0 and sp > 0:
        d.polygon(star_pts(1360, 540, 26 * sp, 15), fill=cr(ORANGE, 240 * sf))

    # global fade for act elements
    gf = 1 - prog(t, 7.9, 8.5)

    # S1 window
    if gf > 0:
        perim_p = eo(prog(t, 1.15, 2.15)); content_p = prog(t, 2.15, 2.55)
        if perim_p > 0:
            ov.alpha_composite(draw_window(gf, perim_p, content_p))

        # S2 thread + cards
        th1 = eo(prog(t, 2.7, 3.6))
        if th1 > 0:
            draw_partial(d, THREAD1, th1, cr(ORANGE, 210 * gf), 2)
        for i, (cx, cy, rot) in enumerate(CARDS):
            cp = eo(prog(t, 3.3 + i * 0.15, 3.3 + i * 0.15 + 0.5))
            if cp > 0:
                cy2 = cy + (1 - cp) * 26
                ov.alpha_composite(draw_card(cx, cy2, 200, 150, rot, cp * gf, play=(i == 1)))

        # S3 thread + bars
        th2 = eo(prog(t, 4.6, 5.5))
        if th2 > 0:
            draw_partial(d, THREAD2, th2, cr(ORANGE, 210 * gf), 2)
        bps = [prog(t, 5.2 + i * 0.1, 5.2 + i * 0.1 + 0.55) for i in range(5)]
        if any(p > 0 for p in bps):
            ov.alpha_composite(draw_bars(gf, bps))

    im.alpha_composite(ov)

    # words (own layer so reveal masks compose cleanly)
    wl = Image.new("RGBA", im.size, (0, 0, 0, 0))
    specs = [
        ("مواقع", 2.5, 3.1, None, 4.3),
        ("محتوى", 4.3, 4.9, None, 6.3),
        ("إعلانات", 6.3, 6.9, None, None),
    ]
    for i, (wtext, a0, a1, _u, dim_at) in enumerate(specs):
        rp = prog(t, a0, a1)
        if rp <= 0 or gf <= 0: continue
        wim = w_caches[i]
        alpha = 1.0
        if dim_at is not None:
            alpha = 1 - prog(t, dim_at, dim_at + 0.5)
        m = reveal_mask(wim.size, eo(rp))
        piece = wim.copy(); piece.putalpha(Image.composite(piece.getchannel("A"), Image.new("L", wim.size, 0), m))
        if alpha < 1:
            piece.putalpha(piece.getchannel("A").point(lambda v: int(v * alpha * gf)))
        else:
            piece.putalpha(piece.getchannel("A").point(lambda v: int(v * gf)))
        wl.alpha_composite(piece, (sc(960) - wim.size[0] // 2, sc(830) - wim.size[1] // 2))
        # dash under word
        dp = eo(prog(t, a1, a1 + 0.25))
        if dp > 0:
            dd = ImageDraw.Draw(wl, "RGBA")
            half = 34 * dp
            dd.rounded_rectangle([sc(960 - half), sc(965), sc(960 + half), sc(971)],
                                 radius=sc(3), fill=cr(ORANGE, 230 * alpha * gf))
    im.alpha_composite(wl)

    # S4 finale
    sw = eo(prog(t, 7.9, 8.7))
    f4 = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d4 = ImageDraw.Draw(f4, "RGBA")
    if sw > 0:
        draw_partial(d4, SWEEP, sw, cr(ORANGE, 200 * (1 - prog(t, 8.7, 9.2))), 2)
    star_p = eo_back(prog(t, 8.3, 8.6))
    if star_p > 0:
        pulse = 1 + 0.045 * math.sin((t - 8.6) * 2.2) if t > 8.6 else 1
        rot = (t - 8.3) * 8
        d4.polygon(star_pts(960, 340, 36 * star_p * pulse, rot), fill=cr(ORANGE, 245))
    im.alpha_composite(f4)

    # CANNAVARO staggered rise
    word = "CANNAVARO"
    t0, stag, dur = 8.55, 0.045, 0.55
    widths = [f_anton.getlength(ch) for ch in word]
    total_w = sum(widths)
    xcur = sc(960) - total_w / 2
    nm = Image.new("RGBA", im.size, (0, 0, 0, 0))
    nd = ImageDraw.Draw(nm, "RGBA")
    for i, ch in enumerate(word):
        p = eo(prog(t, t0 + i * stag, t0 + i * stag + dur))
        ps = eo(prog(t, t0 + i * stag + 0.07, t0 + i * stag + 0.07 + dur))
        if p <= 0: continue
        yy = sc(530) + (1 - p) * sc(46)
        yys = sc(530) + (1 - ps) * sc(46)
        if ps > 0:
            nd.text((xcur + sc(6), yys + sc(6)), ch, font=f_anton, fill=cr(ORANGE, 255 * ps))
        nd.text((xcur, yy), ch, font=f_anton, fill=cr(CREAM, 255 * p))
        xcur += widths[i]
    im.alpha_composite(nm)

    # kicker
    kp = prog(t, 9.35, 9.95)
    if kp > 0:
        ktxt = "وكالة دعاية وتسويق رقمي"
        bb = d.textbbox((0, 0), ktxt, font=f_kick)
        kw = bb[2] - bb[0]
        kl = Image.new("RGBA", im.size, (0, 0, 0, 0))
        kd = ImageDraw.Draw(kl)
        kd.text((sc(960) - kw // 2 - bb[0], sc(800) - bb[1]), ktxt, font=f_kick,
                fill=cr(CREAM, 255 * eio(kp)))
        im.alpha_composite(kl)

    return finish(im, n)

# ------------------------------------------------------------------- main
def load_fonts():
    f_word = ImageFont.truetype(CAIRO, sc(112), layout_engine=ImageFont.Layout.RAQM)
    f_word.set_variation_by_axes([900])
    f_kick = ImageFont.truetype(CAIRO, sc(56), layout_engine=ImageFont.Layout.RAQM)
    f_kick.set_variation_by_axes([700])
    f_anton = ImageFont.truetype(ANTON, sc(172))
    w_caches = [word_layer(w, 112, 900) for w in ("مواقع", "محتوى", "إعلانات")]
    return (f_word, f_kick, f_anton, w_caches)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "frames3"
    n0 = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    n1 = int(sys.argv[3]) if len(sys.argv) > 3 else NFRAMES
    os.makedirs(out, exist_ok=True)
    fonts = load_fonts()
    for n in range(n0, min(n1, NFRAMES)):
        t = n / FPS
        render_frame(t, fonts, n).save(os.path.join(out, "%04d.png" % n))
        if n % 30 == 0:
            print("frame", n, "/", NFRAMES, flush=True)
    print("done", n0, min(n1, NFRAMES), flush=True)

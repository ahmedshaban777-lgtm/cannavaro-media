#!/usr/bin/env python3
"""Cannavaro full ad v1 (v4) - quiet luxury direction, complete film.
All 8 site services in the site's own phrasing, thread motif, waveform
scene, light-sweep CANNAVARO finale, CTA. Silent picture track; audio
is synthesized separately by audio4.py and muxed.
Usage: python3 render4.py [out_dir] [start_frame] [end_frame]
"""
import math, os, sys
from PIL import Image, ImageDraw, ImageFont

SS = 2
W, H = 1920, 1080
FPS = 30
DUR = 21.0
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
        out.append(((1-u)**2*p0[0] + 2*(1-u)*u*p1[0] + u*u*p2[0],
                    (1-u)**2*p0[1] + 2*(1-u)*u*p1[1] + u*u*p2[1]))
    return out

def draw_partial(d, pts, p, color, width):
    if p <= 0: return
    n = max(2, int(len(pts) * clamp(p)))
    seg = [(sc(x), sc(y)) for x, y in pts[:n]]
    if len(seg) >= 2:
        d.line(seg, fill=color, width=sc(width), joint="curve")

def poly_progress_draw(d, pts, p, color, width):
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

# ------------------------------------------------------------------- finish
_vig = None
_grain = None
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
    if _grain is None:
        _grain = [Image.frombytes("L", (sc(W)//2, sc(H)//2), os.urandom(sc(W)*sc(H)//4)).resize((sc(W), sc(H)), Image.NEAREST) for _ in range(6)]
    return _grain

def finish(im, n):
    im = im.convert("RGB")
    g = grain_layers()[n % 6].point(lambda v: int(v / 255 * 14))
    im = Image.composite(Image.new("RGB", im.size, (255, 255, 255)), im, g)
    im = Image.composite(Image.new("RGB", im.size, (0, 0, 0)), im, vignette())
    return im.resize((W, H), Image.LANCZOS)

# ------------------------------------------------------------------- pieces
def draw_window(alpha, perim_p, content_p):
    lay = Image.new("RGBA", (sc(W), sc(H)), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay, "RGBA")
    x0, y0, x1, y1 = 210, 280, 830, 620
    poly_progress_draw(d, [(x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0)], perim_p, cr(CREAM, 235*alpha), 3)
    if content_p > 0:
        ca = alpha * eo(content_p)
        for i, col in enumerate([ORANGE, CREAM, CREAM]):
            cx = 250 + i * 34
            d.ellipse([sc(cx-7), sc(295), sc(cx+7), sc(309)], fill=cr(col, 220*ca))
        d.line([sc(210), sc(330), sc(830), sc(330)], fill=cr(CREAM, 90*ca), width=sc(2))
        d.rounded_rectangle([sc(250), sc(370), sc(520), sc(560)], radius=sc(16), fill=cr(ORANGE, 215*ca))
        for i, wln in enumerate([250, 210, 160]):
            yy = 392 + i * 56
            d.rounded_rectangle([sc(560), sc(yy), sc(560+wln), sc(yy+22)], radius=sc(11), fill=cr(CREAM, 140*ca))
        # small cart hint bottom right (stores)
        d.rounded_rectangle([sc(660), sc(536), sc(790), sc(572)], radius=sc(10), outline=cr(CREAM, 120*ca), width=sc(2))
    return lay

def draw_card(cx, cy, w, h, rot, a, play=False):
    card = Image.new("RGBA", (sc(w+80), sc(h+80)), (0, 0, 0, 0))
    d = ImageDraw.Draw(card, "RGBA")
    d.rounded_rectangle([sc(40), sc(40), sc(40+w), sc(40+h)], radius=sc(18),
                        outline=cr(CREAM, 210*a), width=sc(3), fill=cr(CREAM, 14*a))
    if play:
        pts = [(sc(40+w/2-16), sc(40+h/2-22)), (sc(40+w/2-16), sc(40+h/2+22)), (sc(40+w/2+24), sc(40+h/2))]
        d.polygon(pts, fill=cr(ORANGE, 230*a))
    else:
        for i, wln in enumerate([w-90, w-140]):
            yy = 40 + 52 + i * 44
            d.rounded_rectangle([sc(80), sc(yy), sc(80+wln), sc(yy+18)], radius=sc(9), fill=cr(CREAM, 120*a))
        d.ellipse([sc(80), sc(40+h-58), sc(116), sc(40+h-22)], fill=cr(ORANGE, 200*a))
    card = card.rotate(rot, resample=Image.BICUBIC, center=(sc((w+80)/2), sc((h+80)/2)))
    lay = Image.new("RGBA", (sc(W), sc(H)), (0, 0, 0, 0))
    lay.alpha_composite(card, (sc(cx-(w+80)/2), sc(cy-(h+80)/2)))
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
        d.rounded_rectangle([sc(x0), sc(base_y-hh*p), sc(x0+36), sc(base_y)], radius=sc(9), fill=cr(col, aa))
    return lay

WAVE_ENV = [math.sin(i*1.4)*0.55 + math.sin(i*0.6+1.3)*0.45 for i in range(28)]
def draw_wave(alpha, line_p, bars_p):
    lay = Image.new("RGBA", (sc(W), sc(H)), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay, "RGBA")
    x0, x1, yc = 520, 1400, 440
    if line_p > 0:
        xe = lerp(x0, x1, eo(line_p))
        d.line([sc(x0), sc(yc), sc(xe), sc(yc)], fill=cr(CREAM, 200*alpha), width=sc(2))
    nb = 28
    for i in range(nb):
        p = eo(clamp(bars_p * 1.25 - i * 0.018))
        if p <= 0: continue
        x = x0 + 30 + i * ((x1 - x0 - 60) / (nb - 1))
        hh = (12 + abs(WAVE_ENV[i]) * 82) * p
        col = ORANGE if i in (6, 14, 21) else CREAM
        aa = (230 if col is ORANGE else 165) * alpha
        d.rounded_rectangle([sc(x-3), sc(yc-hh), sc(x+3), sc(yc+hh)], radius=sc(3), fill=cr(col, aa))
    return lay

def word_layer(word, size, weight):
    f = ImageFont.truetype(CAIRO, sc(size), layout_engine=ImageFont.Layout.RAQM)
    f.set_variation_by_axes([weight])
    tmp = Image.new("RGBA", (10, 10)); td = ImageDraw.Draw(tmp)
    bb = td.textbbox((0, 0), word, font=f)
    wl = Image.new("RGBA", (bb[2]-bb[0]+sc(40), bb[3]-bb[1]+sc(40)), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wl)
    wd.text((sc(20)-bb[0], sc(20)-bb[1]), word, font=f, fill=CREAM+(255,))
    return wl

_grads = {}
def reveal_mask(lay_size, p, feather=70):
    key = lay_size[1]
    if key not in _grads:
        _grads[key] = Image.linear_gradient("L").resize((8, lay_size[1]))
    fv = max(1.0, 255 * sc(feather) / lay_size[1])
    vb = 255 - (255 + fv) * clamp(p)
    return _grads[key].point(lambda v: int(clamp((v - vb) / fv) * 255)).resize(lay_size)

def paste_word(im, wim, cx, cy, p, alpha):
    if p <= 0 or alpha <= 0: return
    m = reveal_mask(wim.size, eo(p))
    piece = wim.copy()
    piece.putalpha(Image.composite(piece.getchannel("A"), Image.new("L", wim.size, 0), m))
    if alpha < 1:
        piece.putalpha(piece.getchannel("A").point(lambda v: int(v * alpha)))
    im.alpha_composite(piece, (sc(cx) - wim.size[0]//2, sc(cy) - wim.size[1]//2))

def dash(im, cx, y, p, alpha=1.0):
    if p <= 0 or alpha <= 0: return
    d = ImageDraw.Draw(im, "RGBA")
    half = 34 * eo(p)
    d.rounded_rectangle([sc(cx-half), sc(y), sc(cx+half), sc(y+6)], radius=sc(3), fill=cr(ORANGE, 230*alpha))

# ------------------------------------------------------------------- stage
CARDS = [(1030, 428, -3), (1245, 452, 2), (1460, 424, -2)]
THREAD1 = qbez((838, 450), (880, 400), (928, 434))
THREAD2 = qbez((1568, 468), (1590, 520), (1620, 560))

def render_frame(t, fonts, name_lay, n):
    f_kick, f_anton, f_cta, W = fonts
    im = Image.new("RGBA", (sc(1920), sc(1080)), INK + (255,))
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov, "RGBA")

    # S0 hairline + twinkle star
    lp = eo(prog(t, 0.15, 0.8)); lf = 1 - prog(t, 1.3, 1.7)
    if lf > 0 and lp > 0:
        d.line([sc(560), sc(540), sc(lerp(560, 1360, lp)), sc(540)], fill=cr(ORANGE, 235*lf), width=sc(2))
    sp = eo_back(prog(t, 0.85, 1.0)); sf = 1 - prog(t, 1.45, 1.85)
    if sf > 0 and sp > 0:
        d.polygon(star_pts(1360, 540, 26*sp, 15), fill=cr(ORANGE, 240*sf))

    # hero elements: dim when waveform arrives, gone before quick cards
    hero_dim = 1 - 0.88 * prog(t, 7.6, 8.5)
    hero_a = hero_dim * (1 - prog(t, 10.0, 10.5))

    if hero_a > 0:
        perim_p = eo(prog(t, 1.2, 2.2))
        if perim_p > 0:
            ov.alpha_composite(draw_window(hero_a, perim_p, prog(t, 2.2, 2.6)))
        th1 = eo(prog(t, 2.8, 3.7)) * hero_a
        if th1 > 0:
            draw_partial(d, THREAD1, th1, cr(ORANGE, 210), 2)
        for i, (cx, cy, rot) in enumerate(CARDS):
            cp = eo(prog(t, 3.4 + i*0.15, 3.4 + i*0.15 + 0.5))
            if cp > 0:
                ov.alpha_composite(draw_card(cx, cy + (1-cp)*26, 200, 150, rot, cp*hero_a, play=(i == 1)))
        th2 = eo(prog(t, 4.7, 5.6)) * hero_a
        if th2 > 0:
            draw_partial(d, THREAD2, th2, cr(ORANGE, 210), 2)
        bps = [prog(t, 5.3 + i*0.1, 5.3 + i*0.1 + 0.55) for i in range(5)]
        if any(p > 0 for p in bps):
            ov.alpha_composite(draw_bars(hero_a, bps))

    # S4 waveform scene
    wave_a = 1 - prog(t, 10.2, 10.7)
    wlp = eo(prog(t, 8.6, 9.2)); wbp = prog(t, 8.95, 9.7)
    if wave_a > 0 and wlp > 0:
        ov.alpha_composite(draw_wave(wave_a, wlp, wbp))
    im.alpha_composite(ov)

    # ---- words
    wl = Image.new("RGBA", im.size, (0, 0, 0, 0))
    # hero words: (cache, reveal a0-a1, fade-out f0-f1)
    for idx, (a0, a1, f0, f1) in enumerate([(2.5, 3.15, 4.0, 4.4),
                                            (4.45, 5.1, 6.15, 6.55),
                                            (6.6, 7.25, 9.0, 9.4),
                                            (9.7, 10.35, 10.55, 10.95)]):
        rp = prog(t, a0, a1)
        fa = 1 - prog(t, f0, f1)
        if rp > 0 and fa > 0:
            paste_word(wl, W[idx], 960, 830, rp, fa)
            if idx < 3:
                dash(wl, 960, 965, prog(t, a1, a1 + 0.25), fa)
            else:
                dash(wl, 960, 965, prog(t, a1, a1 + 0.25), fa)
    # S5 quick service cards
    qa = prog(t, 11.0, 11.35) * (1 - prog(t, 11.7, 11.95))
    if qa > 0:
        paste_word(wl, W[4], 960, 500, min(1.0, prog(t, 11.0, 11.35) * 1.6), qa)
        dash(wl, 960, 640, prog(t, 11.3, 11.5), qa)
    qb = prog(t, 12.05, 12.4) * (1 - prog(t, 12.8, 13.05))
    if qb > 0:
        paste_word(wl, W[5], 960, 500, min(1.0, prog(t, 12.05, 12.4) * 1.6), qb)
        dash(wl, 960, 640, prog(t, 12.35, 12.55), qb)
    im.alpha_composite(wl)

    # ---- S6 pull-in: closing vignette
    close_p = eio(prog(t, 13.1, 14.05))
    if close_p > 0:
        m = Image.new("L", (480, 270), 0)
        px = m.load()
        hole = 1.6 * (1 - close_p)
        for yy in range(270):
            for xx in range(480):
                dx = (xx - 240) / 240.0; dy = (yy - 135) / 135.0
                r = math.sqrt(dx*dx + dy*dy)
                px[xx, yy] = int(clamp((r - hole) / 0.35) * 255)
        m = m.resize(im.size, Image.BILINEAR)
        im.paste(Image.new("RGBA", im.size, (10, 10, 12, 255)), (0, 0), m)

    # ---- S7 name finale: light sweep reveal
    swp = eo(prog(t, 14.1, 15.45))
    if swp > 0:
        nl_w = name_lay.size[0]
        xf = lerp(-sc(120), nl_w + sc(120), swp)
        m = Image.linear_gradient("L").rotate(90).resize((nl_w, 8))  # 0 left -> 255 right? we need reveal left-to-right
        # build sweep mask: visible where x < xf (feather 90)
        fv = 255 * sc(90) / nl_w
        # gradient v(x) = 255*x/nl_w ; want alpha 255 when x <= xf-fvzone
        vxf = 255 * xf / nl_w
        m = m.point(lambda v: int(clamp((vxf - v) / fv) * 255)).resize(name_lay.size)
        piece = name_lay.copy()
        piece.putalpha(Image.composite(piece.getchannel("A"), Image.new("L", name_lay.size, 0), m))
        nx = sc(960) - nl_w // 2
        im.alpha_composite(piece, (nx, sc(470) - name_lay.size[1]//2))
        # light band at front
        if swp < 1:
            band = Image.new("RGBA", (sc(140), sc(700)), (0, 0, 0, 0))
            bd = ImageDraw.Draw(band)
            for i in range(140):
                aa = int(175 * (1 - abs(i - 70) / 70) ** 2)
                bd.line([sc(i), 0, sc(i), sc(700)], fill=(255, 130, 45, aa))
            im.alpha_composite(band, (nx + int(xf) - sc(70), sc(170)))
    # star by the O
    stp = eo_back(prog(t, 15.55, 15.9))
    if stp > 0:
        d2 = ImageDraw.Draw(im, "RGBA")
        pulse = 1 + 0.05 * math.sin((t - 15.9) * 2.4) if t > 15.9 else 1
        d2.polygon(star_pts(1352, 372, 40 * stp * pulse, (t - 15.55) * 8), fill=cr(ORANGE, 245))
    # kicker
    kp = prog(t, 16.4, 17.0)
    if kp > 0:
        ktxt = "وكالة دعاية وتسويق رقمي"
        tmp = Image.new("RGBA", (10, 10)); td = ImageDraw.Draw(tmp)
        bb = td.textbbox((0, 0), ktxt, font=f_kick)
        kw = bb[2] - bb[0]
        kl = Image.new("RGBA", im.size, (0, 0, 0, 0))
        kd = ImageDraw.Draw(kl)
        kd.text((sc(960) - kw//2 - bb[0], sc(700) - bb[1]), ktxt, font=f_kick, fill=cr(CREAM, 255 * eio(kp)))
        im.alpha_composite(kl)

    # ---- S8 CTA
    cp = prog(t, 17.9, 18.5)
    if cp > 0:
        ctxt = "خلّينا نتكلم"
        tmp = Image.new("RGBA", (10, 10)); td = ImageDraw.Draw(tmp)
        bb = td.textbbox((0, 0), ctxt, font=f_cta)
        kw = bb[2] - bb[0]
        cl = Image.new("RGBA", im.size, (0, 0, 0, 0))
        cd = ImageDraw.Draw(cl)
        cd.text((sc(960) - kw//2 - bb[0], sc(830) - bb[1]), ctxt, font=f_cta, fill=cr(CREAM, 255 * eio(cp)))
        im.alpha_composite(cl)
        pulse = 0.72 + 0.28 * math.sin((t - 18.5) * 3.0) if t > 18.5 else 1
        dash(im, 960, 905, prog(t, 18.3, 18.6), pulse)

    return finish(im, n)

# ------------------------------------------------------------------- main
def load_fonts():
    f_kick = ImageFont.truetype(CAIRO, sc(56), layout_engine=ImageFont.Layout.RAQM)
    f_kick.set_variation_by_axes([700])
    f_cta = ImageFont.truetype(CAIRO, sc(64), layout_engine=ImageFont.Layout.RAQM)
    f_cta.set_variation_by_axes([700])
    f_anton = ImageFont.truetype(ANTON, sc(240))
    words = [word_layer(w, 100, 900) for w in
             ("مواقع ومتاجر", "محتوى وهوية", "حملات ممولة", "تعليق صوتي",
              "إدارة السوشيال ميديا", "السيو والتحليلات")]
    # name layer with trailing orange shadow
    word = "CANNAVARO"
    tmp = Image.new("RGBA", (10, 10)); td = ImageDraw.Draw(tmp)
    widths = [td.textlength(ch, font=f_anton) for ch in word]
    total_w = int(sum(widths))
    name_lay = Image.new("RGBA", (total_w + sc(80), sc(340)), (0, 0, 0, 0))
    nd = ImageDraw.Draw(name_lay)
    xcur = sc(20)
    for i, ch in enumerate(word):
        nd.text((xcur + sc(7), sc(27)), ch, font=f_anton, fill=ORANGE + (255,))
        nd.text((xcur, sc(20)), ch, font=f_anton, fill=CREAM + (255,))
        xcur += widths[i]
    return (f_kick, f_anton, f_cta, words[0], words[1], words[2], name_lay, words)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "frames4"
    n0 = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    n1 = int(sys.argv[3]) if len(sys.argv) > 3 else NFRAMES
    os.makedirs(out, exist_ok=True)
    f = load_fonts()
    fonts = (f[0], f[1], f[2], f[7])  # f_kick, f_anton, f_cta, word caches
    name_lay = f[6]
    for n in range(n0, min(n1, NFRAMES)):
        t = n / FPS
        render_frame(t, fonts, name_lay, n).save(os.path.join(out, "%04d.png" % n))
        if n % 30 == 0:
            print("frame", n, "/", NFRAMES, flush=True)
    print("done", n0, min(n1, NFRAMES), flush=True)

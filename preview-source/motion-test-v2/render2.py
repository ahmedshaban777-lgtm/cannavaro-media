#!/usr/bin/env python3
"""Cannavaro 2D motion test v2 - stronger kinetic direction.
Closeup UI scenes (web/content/ads), kinetic Arabic type, band-wipe
transitions, ink finale with per-letter CANNAVARO drop. Silent.
Usage: python3 render2.py [out_dir] [start_frame] [end_frame]
"""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFont

SS = 2
W, H = 1920, 1080
FPS = 30
DUR = 10.2
NFRAMES = int(FPS * DUR)

CREAM = (255, 246, 236)
INK = (20, 20, 20)
ORANGE = (255, 77, 0)
YELLOW = (255, 210, 63)
MINT = (158, 230, 184)
LAV = (201, 188, 255)
PINK = (255, 179, 199)

HERE = os.path.dirname(os.path.abspath(__file__))
ANTON = os.path.join(HERE, "anton-latin.woff2")
CAIRO = os.path.join(HERE, "cairo-arabic.woff2")

def sc(v): return int(round(v * SS))
def clamp(v, a=0.0, b=1.0): return max(a, min(b, v))
def lerp(a, b, p): return a + (b - a) * p
def prog(t, a, b): return clamp((t - a) / (b - a))
def eo_cubic(p): return 1 - (1 - p) ** 3
def eio_cubic(p): return 4*p*p*p if p < 0.5 else 1 - (-2*p + 2) ** 3 / 2
def eo_back(p, s=1.70158): return 1 + (s + 1) * (p - 1) ** 3 + s * (p - 1) ** 2

STAR_BASE = [(30,0),(36,22),(58,30),(36,38),(30,60),(24,38),(2,30),(24,22)]
def star_poly(cx, cy, r, rot):
    pts = [((x-30)/30.0*r, (y-30)/30.0*r) for x, y in STAR_BASE]
    rr = math.radians(rot); c, s = math.cos(rr), math.sin(rr)
    return [(cx + x*c - y*s, cy + x*s + y*c) for x, y in pts]

def draw_star_img(img, cx, cy, r, rot, fill=ORANGE, outline=INK, ow=3):
    d = ImageDraw.Draw(img)
    pts = [(sc(x), sc(y)) for x, y in star_poly(cx, cy, r, rot)]
    d.polygon(pts, fill=fill)
    for i in range(len(pts)):
        d.line([pts[i], pts[(i+1) % len(pts)]], fill=outline, width=sc(ow))

def rrect(d, box, rad, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=rad, fill=fill, outline=outline, width=width)

# ---------------------------------------------------------------- backgrounds
def make_bg(dark=False, phase=0.0):
    base = INK + (255,) if dark else CREAM + (255,)
    im = Image.new("RGBA", (sc(W), sc(H)), base)
    d = ImageDraw.Draw(im, "RGBA")
    if dark:
        glows = [(1650, 150, 280, ORANGE, 34), (220, 700, 320, LAV, 22)]
        waves = [(240, (255,210,63), 46), (430, (158,230,184), 40),
                 (630, (201,188,255), 38), (800, (255,179,199), 32)]
    else:
        glows = [(1640, 120, 260, ORANGE, 26), (200, 640, 300, LAV, 20)]
        waves = [(240, YELLOW, 76), (420, MINT, 66), (610, LAV, 61), (790, PINK, 51)]
    for (gx, gy, r, col, a) in glows:
        glow = Image.new("RGBA", (sc(r*2), sc(r*2)), (0,0,0,0))
        ImageDraw.Draw(glow).ellipse([0, 0, sc(r*2), sc(r*2)], fill=col+(a,))
        im.alpha_composite(glow, (sc(gx-r), sc(gy-r)))
    for wy, col, a in waves:
        pts = [(sc(x), sc(wy + 28*math.sin((x+wy+phase)/160.0))) for x in range(-40, W+41, 20)]
        d.line(pts, fill=col+(a,), width=sc(3))
    return im

# ---------------------------------------------------------------- big vector props
def draw_browser(img, x0, y0, s, t):
    """Big closeup browser. s = scale vs v1 card size (320x230)."""
    d = ImageDraw.Draw(img)
    w, h = 320*s, 230*s
    rrect(d, [sc(x0), sc(y0), sc(x0+w), sc(y0+h)], sc(24*s), fill=(255,255,255), outline=INK, width=sc(7*s))
    d.rounded_rectangle([sc(x0), sc(y0), sc(x0+w), sc(y0+56*s)], radius=sc(24*s), fill=YELLOW, outline=INK, width=sc(7*s))
    d.rectangle([sc(x0), sc(y0+30*s), sc(x0+w), sc(y0+56*s)], fill=YELLOW)
    d.line([sc(x0), sc(y0+56*s), sc(x0+w), sc(y0+56*s)], fill=INK, width=sc(7*s))
    for i, col in enumerate([ORANGE, MINT, INK]):
        cx = x0 + 34*s + i*34*s
        d.ellipse([sc(cx-9*s), sc(y0+19*s), sc(cx+9*s), sc(y0+37*s)], fill=col, outline=INK, width=sc(3*s))
    # loading bar under top bar, fills over first 1.2s
    lp = eo_cubic(prog(t, 0.1, 1.3))
    rrect(d, [sc(x0+150*s), sc(y0+22*s), sc(x0+150*s+130*s), sc(y0+34*s)], sc(6*s), fill=(230,224,214))
    if lp > 0:
        rrect(d, [sc(x0+150*s), sc(y0+22*s), sc(x0+(150+130*lp)*s), sc(y0+34*s)], sc(6*s), fill=ORANGE)
    # content bars sliding in staggered
    bars = [(28, 84, 264, 22, INK), (28, 122, 212, 20, (90,90,90)), (28, 158, 236, 18, (90,90,90))]
    for i, (bx, by, bw, bh, col) in enumerate(bars):
        p = eo_cubic(prog(t, 0.35 + i*0.22, 0.75 + i*0.22))
        if p > 0:
            rrect(d, [sc(x0+bx*s), sc(y0+by*s), sc(x0+(bx+bw*p)*s), sc(y0+(by+bh)*s)], sc(bh/2*s), fill=col)
    # orange button pops
    bp = eo_back(prog(t, 1.15, 1.5), 1.5)
    if bp > 0:
        bw2, bh2 = 120*s*bp, 36*s*bp
        rrect(d, [sc(x0+28*s), sc(y0+186*s), sc(x0+28*s+bw2), sc(y0+186*s+bh2)], sc(18*s*bp), fill=ORANGE, outline=INK, width=sc(5*s))

def draw_post(img, x0, y0, s, t, rot=0.0):
    """Big social post card. Drawn on own layer for rotation."""
    w, h = 280*s, 240*s
    im = Image.new("RGBA", (sc(w+80*s), sc(h+80*s)), (0,0,0,0))
    d = ImageDraw.Draw(im)
    ox, oy = 40*s, 40*s
    rrect(d, [sc(ox), sc(oy), sc(ox+w), sc(oy+h)], sc(26*s), fill=MINT, outline=INK, width=sc(7*s))
    rrect(d, [sc(ox+24*s), sc(oy+24*s), sc(ox+130*s), sc(oy+110*s)], sc(14*s), fill=ORANGE, outline=INK, width=sc(5*s))
    tri = [(sc(ox+66*s), sc(oy+52*s)), (sc(ox+66*s), sc(oy+82*s)), (sc(ox+94*s), sc(oy+67*s))]
    d.polygon(tri, fill=CREAM)
    for i in range(3):
        d.line([tri[i], tri[(i+1) % 3]], fill=INK, width=sc(4*s))
    rrect(d, [sc(ox+148*s), sc(oy+34*s), sc(ox+256*s), sc(oy+56*s)], sc(11*s), fill=INK)
    rrect(d, [sc(ox+148*s), sc(oy+70*s), sc(ox+224*s), sc(oy+90*s)], sc(10*s), fill=(90,90,90))
    # heart pops
    hp = eo_back(prog(t, 0.2, 0.5), 2.0)
    if hp > 0:
        r = 20*s*hp
        d.ellipse([sc(ox+46*s-r), sc(oy+170*s-r), sc(ox+46*s+r), sc(oy+170*s+r)], fill=PINK, outline=INK, width=sc(5*s))
    rrect(d, [sc(ox+84*s), sc(oy+158*s), sc(ox+250*s), sc(oy+182*s)], sc(12*s), fill=INK)
    if rot:
        im = im.rotate(-rot, expand=True, resample=Image.BICUBIC)
    return im

def draw_megaphone(img, x0, y0, s, rot=0.0):
    """Site illustration megaphone, parameterized."""
    im = Image.new("RGBA", (sc(220*s), sc(200*s)), (0,0,0,0))
    d = ImageDraw.Draw(im)
    def P(x, y): return (sc(x*s), sc(y*s))
    rrect(d, [P(10, 68), P(36, 102)], sc(8*s), fill=INK)
    horn = [P(36, 60), P(122, 34), P(122, 134), P(36, 108)]
    d.polygon(horn, fill=PINK)
    for i in range(4):
        d.line([horn[i], horn[(i+1) % 4]], fill=INK, width=sc(4*s))
    rrect(d, [P(42, 106), P(58, 148)], sc(7*s), fill=ORANGE, outline=INK, width=sc(4*s))
    d.ellipse([P(112, 74), P(132, 94)], fill=YELLOW, outline=INK, width=sc(4*s))
    if rot:
        im = im.rotate(-rot, expand=True, resample=Image.BICUBIC)
    out = Image.new("RGBA", img.size, (0,0,0,0))
    out.alpha_composite(im, (sc(x0), sc(y0)))
    img.alpha_composite(out)

def paste_blur(img, layer, x, y, blur_dx=0, blur_dy=0):
    """Paste layer with cheap directional motion blur."""
    if blur_dx or blur_dy:
        for k, a in [(3, 0.18), (2, 0.28), (1, 0.45)]:
            l2 = layer.copy()
            ch = l2.getchannel("A").point(lambda v: int(v * a))
            l2.putalpha(ch)
            img.alpha_composite(l2, (sc(x) - int(blur_dx*k), sc(y) - int(blur_dy*k)))
    img.alpha_composite(layer, (sc(x), sc(y)))

# ---------------------------------------------------------------- kinetic word
def kinetic_word(img, t, t0, word_font, word, caption_font, caption, block_col,
                 cx=520, cy=470, text_col=INK, block_h_ratio=0.62):
    """Colored block expands, word clip-reveals up, caption slides after."""
    d = ImageDraw.Draw(img)
    bbox = d.textbbox((0,0), word, font=word_font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    # clamp block inside left/right margins
    left = max(sc(120), sc(cx) - (tw + sc(70))//2)
    left = min(left, sc(W) - sc(120) - (tw + sc(70)))
    wcx = left + (tw + sc(70))//2   # effective word-block center
    # block
    bp = eo_back(prog(t, t0, t0+0.38), 1.1)
    if bp > 0:
        bh = th * block_h_ratio
        bw = (tw + sc(70)) * bp
        by = sc(cy) + th//2 - int(bh)//2
        rrect(d, [left, by, left + int(bw), by + int(bh)], sc(14), fill=block_col)
    # word clip reveal (from bottom of its box)
    wp = eo_cubic(prog(t, t0+0.14, t0+0.62))
    if wp > 0:
        wl = Image.new("RGBA", img.size, (0,0,0,0))
        ImageDraw.Draw(wl).text((wcx-tw//2, sc(cy)-bbox[1]), word, font=word_font, fill=text_col)
        mask = Image.new("L", img.size, 0)
        mh = int((th + sc(80)) * wp)
        ImageDraw.Draw(mask).rectangle([wcx-tw//2-sc(20), sc(cy)-sc(40)+ (th+sc(80)) - mh,
                                        wcx+tw//2+sc(20), sc(cy)-sc(40)+th+sc(80)], fill=255)
        wl.putalpha(Image.composite(wl.getchannel("A"), Image.new("L", img.size, 0), mask))
        img.alpha_composite(wl)
    # caption
    cp = eo_cubic(prog(t, t0+0.5, t0+0.9))
    if cp > 0:
        cl = Image.new("RGBA", img.size, (0,0,0,0))
        cd = ImageDraw.Draw(cl)
        cb = cd.textbbox((0,0), caption, font=caption_font)
        cd.text((wcx-(cb[2]-cb[0])//2, sc(cy)+th//2+int(th*block_h_ratio)//2+sc(46)-cb[1] + int((1-cp)*sc(24))),
                caption, font=caption_font, fill=text_col+(int(220*cp),))
        img.alpha_composite(cl)

# ---------------------------------------------------------------- scenes
def scene_web(t):
    im = make_bg(phase=t*14)
    # closeup browser, cropped by right/bottom edges, slight drift
    bx = 830 + 10*math.sin(t*0.9)
    by = 330 + 8*math.sin(t*1.2)
    draw_browser(im, bx, by, 4.4, t)
    return im

def scene_content(t):
    im = make_bg(phase=40+t*14)
    # three big posts snap-stacking, cropped right
    specs = [(830, 210, -7, 0.0), (1100, 380, 4, 0.35), (940, 590, -2, 0.7)]
    for (x, y, r, dt) in specs:
        p = eo_back(prog(t, dt, dt+0.45), 1.3)
        if p > 0:
            card = draw_post(im, 0, 0, 2.6, t, rot=lerp(r*2.2, r, p))
            paste_blur(im, card, x + (1-p)*160, y + (1-p)*40,
                       blur_dx=int((1-p)*sc(60)), blur_dy=0) if p < 1 else im.alpha_composite(card, (sc(x), sc(y)))
    return im

def scene_ads(t):
    im = make_bg(phase=80+t*14)
    # megaphone closeup left, cropped
    draw_megaphone(im, -30, 430, 4.2, rot=-8 + 2*math.sin(t*1.4))
    # sound star particles from mouth (deterministic)
    rnd = random.Random(11)
    for i in range(7):
        life = (t*0.9 + i/7.0) % 1.0
        px = 540 + life*300 + rnd.uniform(-16, 16)
        py = 760 - life*230 + rnd.uniform(-14, 14)
        pr = (1-life)*26 + 6
        col = [ORANGE, YELLOW, MINT][i % 3]
        draw_star_img(im, px, py, pr, life*180, fill=col, outline=INK, ow=2)
    # chart bars growing, right side cropped
    heights = [0.45, 0.7, 0.55, 0.9, 1.0]
    for i, hh in enumerate(heights):
        p = eo_back(prog(t, 0.25 + i*0.16, 0.75 + i*0.16), 1.1)
        if p > 0:
            bx = 1060 + i*150
            bh = 420 * hh * p
            col = ORANGE if i % 2 == 0 else INK
            rrect(ImageDraw.Draw(im), [sc(bx), sc(930-bh), sc(bx+92), sc(930)], sc(20), fill=col)
    # baseline
    ImageDraw.Draw(im).line([sc(1020), sc(930), sc(1900), sc(930)], fill=INK, width=sc(8))
    return im

def scene_finale(t, fonts):
    f_anton_big, f_anton_sub, f_cairo_kick, arabic_kick, f_cairo_word = fonts
    im = make_bg(dark=True, phase=120+t*10)
    d = ImageDraw.Draw(im)
    word = "CANNAVARO"
    fnt = f_anton_big
    # per-letter metrics
    letters = list(word)
    widths = [d.textlength(ch, font=fnt) for ch in letters]
    spacing = sc(6)
    total_w = int(sum(widths) + spacing*(len(letters)-1))
    x_start = sc(W)//2 - total_w//2
    base_y = sc(430)
    # shadow pass then ink pass, per letter with stagger
    for pass_i, (col, extra_delay, off_max) in enumerate([(ORANGE, 0.13, (26, 26)), ((244,239,230), 0.0, (0, 0))]):
        x = x_start
        for i, ch in enumerate(letters):
            lt0 = 0.15 + i*0.055 + extra_delay
            p = eo_back(prog(t, lt0, lt0+0.5), 1.25)
            if p > 0:
                drop = (1-p) * sc(420)
                if pass_i == 0:
                    op = eo_cubic(prog(t, lt0, lt0+0.6))
                    ox, oy = lerp(off_max[0], 10, op), lerp(off_max[1], 10, op)
                else:
                    ox, oy = 0, 0
                d.text((x + sc(ox), base_y - drop + sc(oy)), ch, font=fnt, fill=col)
            x += int(widths[i]) + spacing
    # kicker
    ka = prog(t, 0.9, 1.35)
    if ka > 0:
        kl = Image.new("RGBA", im.size, (0,0,0,0))
        kd = ImageDraw.Draw(kl)
        kb = kd.textbbox((0,0), arabic_kick, font=f_cairo_kick)
        kd.text((sc(960)-(kb[2]-kb[0])//2, sc(250)-kb[1]), arabic_kick, font=f_cairo_kick,
                fill=(244,239,230, int(200*ka)))
        im.alpha_composite(kl)
    # sub
    sa = prog(t, 1.25, 1.65)
    if sa > 0:
        sl = Image.new("RGBA", im.size, (0,0,0,0))
        sd = ImageDraw.Draw(sl)
        sub = "M E D I A   •   C O N T E N T   •   W E B"
        sb = sd.textbbox((0,0), sub, font=f_anton_sub)
        sd.text((sc(960)-(sb[2]-sb[0])//2, base_y + d.textbbox((0,0), word, font=fnt)[3] + sc(120)), sub, font=f_anton_sub,
                fill=(244,239,230, int(210*sa)))
        im.alpha_composite(sl)
    # orange swash under word (anchored to measured glyph bottom)
    wb = d.textbbox((0,0), word, font=fnt)
    sw = prog(t, 1.15, 1.6)
    if sw > 0:
        rnd = random.Random(7)
        wl = Image.new("RGBA", im.size, (0,0,0,0))
        wd = ImageDraw.Draw(wl)
        x0, x1 = x_start + sc(10), x_start + total_w - sc(10)
        yb = base_y + wb[3] + sc(34)
        for pas in range(2):
            pts = []
            off = pas*sc(8) - sc(4)
            for i in range(61):
                fx = i/60.0
                pts.append((lerp(x0, x1, fx), yb + off + sc(7)*math.sin(fx*math.pi*3.2 + pas*1.7) + sc(rnd.uniform(-2,2))))
            cut = int(len(pts) * sw)
            if cut > 1:
                wd.line(pts[:cut], fill=ORANGE+(235,), width=sc(20), joint="curve")
        im.alpha_composite(wl)
    # star: spins in from top-right, sticks by final O, then bursts already happened at land
    star_p = eo_back(prog(t, 0.75, 1.25), 1.3)
    if star_p > 0:
        tx, ty = x_start + total_w + sc(40), base_y + sc(10)
        sx = lerp(sc(W)+sc(160), tx, star_p)/SS
        sy = lerp(-sc(160), ty, star_p)/SS
        draw_star_img(im, sx, sy, 66, (t*160) % 360, fill=ORANGE, outline=(244,239,230), ow=3)
    # burst particles when star lands
    bp = prog(t, 1.25, 1.9)
    if 0 < bp < 1:
        rnd = random.Random(3)
        for i in range(12):
            ang = i/12.0 * 2*math.pi + rnd.uniform(-0.2, 0.2)
            dist = eo_cubic(bp) * rnd.uniform(90, 190)
            px = (x_start + total_w + sc(40))/SS + math.cos(ang)*dist
            py = (base_y + sc(10))/SS + math.sin(ang)*dist*0.8 + 30*bp*bp
            r = (1-bp) * rnd.uniform(8, 18)
            col = [ORANGE, YELLOW, MINT, PINK][i % 4]
            if r > 1:
                draw_star_img(im, px, py, r, bp*120, fill=col, outline=col, ow=1)
    return im

# ---------------------------------------------------------------- transitions
S1 = (0.0, 2.3); T1 = (2.3, 2.85)
S2 = (2.85, 5.05); T2 = (5.05, 5.6)
S3 = (5.6, 7.5); T3 = (7.5, 8.1)
S4 = (8.1, DUR)

WORDS = [
    # scene, word, caption, block color, t0 offset within scene
    ("web", "مواقع", "W E B S I T E S", MINT, 0.35),
    ("content", "محتوى", "C O N T E N T", YELLOW, 0.35),
    ("ads", "إعلانات", "C A M P A I G N S", LAV, 0.35),
]

def band(im, p, main_col, trail_cols, direction=1):
    """Skewed colored band sweeping across; p 0..1."""
    d = ImageDraw.Draw(im)
    skew = 240
    bw = W*0.62
    travel = W + 2*bw + 2*skew + 200
    lead = -bw - skew - 100 + eio_cubic(p) * travel
    if direction < 0:
        lead = W + bw + skew + 100 - eio_cubic(p) * travel
    bands = [(0, bw, main_col)] + [( -60*(i+1)*direction, bw*0.24, c) for i, c in enumerate(trail_cols)]
    for off, wdt, col in bands:
        x = lead + off
        pts = [(sc(x), 0), (sc(x+wdt), 0), (sc(x+wdt-skew), sc(H)), (sc(x-skew), sc(H))]
        d.polygon(pts, fill=col)

LETTER_LANDS = [8.1 + 0.15 + i*0.055 + 0.5 for i in range(9)]
def shake(t):
    """Decaying impulses when finale letters land."""
    dx = dy = 0.0
    for lt in LETTER_LANDS + [8.1+1.25]:
        dt = t - lt
        if 0 < dt < 0.22:
            amp = 9 * (1 - dt/0.22)
            dx += amp * math.sin(dt*90)
            dy += amp * math.cos(dt*70) * 0.6
    return dx, dy

def render_frame(t, fonts, bgs):
    f_anton_big, f_anton_sub, f_cairo_kick, arabic_kick, f_cairo_word = fonts
    # pick scene
    if t < T1[0]:
        im = scene_web(t - S1[0]); cam = 1.0 + 0.05*prog(t, *S1)
        spec = WORDS[0]; lt = t - S1[0]
    elif t < T1[1]:
        p = prog(t, *T1)
        im = scene_web(t - S1[0]) if p < 0.5 else scene_content(t - T1[1])
        band(im, p, ORANGE, [YELLOW], direction=1)
        return finalize(im, 1.04, t)
    elif t < T2[0]:
        im = scene_content(t - S2[0]); cam = 1.0 + 0.05*prog(t, *S2)
        spec = WORDS[1]; lt = t - S2[0]
    elif t < T2[1]:
        p = prog(t, *T2)
        im = scene_content(t - S2[0]) if p < 0.5 else scene_ads(t - T2[1])
        band(im, p, MINT, [LAV], direction=-1)
        return finalize(im, 1.04, t)
    elif t < T3[0]:
        im = scene_ads(t - S3[0]); cam = 1.0 + 0.05*prog(t, *S3)
        spec = WORDS[2]; lt = t - S3[0]
    elif t < T3[1]:
        p = prog(t, *T3)
        im = scene_ads(t - S3[0]) if p < 0.5 else scene_finale(t - T3[1], fonts)
        band(im, p, INK, [ORANGE], direction=1)
        return finalize(im, 1.04, t)
    else:
        lt4 = t - S4[0]
        im = scene_finale(lt4, fonts)
        dx, dy = shake(t)
        return finalize(im, 1.03 + 0.012*prog(t, S4[0], DUR), t, shake_xy=(dx, dy))
    # word overlays for scenes 1-3
    _, word, caption, block_col, dt0 = spec
    kinetic_word(im, lt, dt0, f_cairo_word, word, f_anton_sub, caption, block_col, cx=470, cy=430)
    return finalize(im, cam, t)

def finalize(im, cam, t, shake_xy=(0,0)):
    eff = cam + 0.02
    tw, thh = int(W*eff), int(H*eff)
    im2 = im.resize((tw, thh), Image.LANCZOS).convert("RGB")
    cx = max(0, min((tw - W)//2 + int(shake_xy[0]), tw - W))
    cy = max(0, min((thh - H)//2 + int(shake_xy[1]), thh - H))
    return im2.crop((cx, cy, cx + W, cy + H))

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "frames2")
    n0 = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    n1 = int(sys.argv[3]) if len(sys.argv) > 3 else NFRAMES
    os.makedirs(out, exist_ok=True)
    import arabic_reshaper
    from bidi.algorithm import get_display
    def shaped(s): return get_display(arabic_reshaper.reshape(s))
    f_anton_big = ImageFont.truetype(ANTON, sc(300))
    f_anton_sub = ImageFont.truetype(ANTON, sc(48))
    f_cairo_kick = ImageFont.truetype(CAIRO, sc(58))
    f_cairo_word = ImageFont.truetype(CAIRO, sc(300))
    f_cairo_word.set_variation_by_axes([900])
    fonts = (f_anton_big, f_anton_sub, f_cairo_kick, shaped("وكالة دعاية وتسويق رقمي"), f_cairo_word)
    # patch scene words through shaping
    global WORDS
    WORDS = [(s, shaped(w), c, b, dt) for (s, w, c, b, dt) in WORDS]
    for n in range(n0, min(n1, NFRAMES)):
        t = n / FPS
        render_frame(t, fonts, None).save(os.path.join(out, "%04d.png" % n))
        if n % 30 == 0:
            print("frame", n, "/", NFRAMES, flush=True)
    print("done", n0, n1)

if __name__ == "__main__":
    main()

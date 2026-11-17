#!/usr/bin/env python3
"""Cannavaro 2D motion test - PIL frame renderer.
Renders an ~8s motion-graphics preview in the Cannavaro concept-a brand
(cream/ink/orange/mint/lavender, Anton + Cairo fonts, sparkle star).
"""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFont

SS = 2                      # supersample factor
W, H = 1920, 1080           # logical canvas
FPS = 30
DUR = 8.7
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
def ease_out_cubic(p): return 1 - (1 - p) ** 3
def ease_in_out_cubic(p): return 4*p*p*p if p < 0.5 else 1 - (-2*p + 2) ** 3 / 2
def ease_out_back(p, s=1.70158):
    return 1 + (s + 1) * (p - 1) ** 3 + s * (p - 1) ** 2

# ---------------------------------------------------------------- helpers
def rot_pts(pts, cx, cy, deg):
    r = math.radians(deg); c, s = math.cos(r), math.sin(r)
    return [(cx + (x-cx)*c - (y-cy)*s, cy + (x-cx)*s + (y-cy)*c) for x, y in pts]

STAR_BASE = [(30,0),(36,22),(58,30),(36,38),(30,60),(24,38),(2,30),(24,22)]
def star_poly(cx, cy, r, rot):
    pts = [((x-30)/30.0*r, (y-30)/30.0*r) for x, y in STAR_BASE]
    rr = math.radians(rot); c, s = math.cos(rr), math.sin(rr)
    return [(cx + x*c - y*s, cy + x*s + y*c) for x, y in pts]

def draw_star(img, cx, cy, r, rot, fill=ORANGE, outline=INK, ow=3):
    d = ImageDraw.Draw(img)
    pts = [(sc(x), sc(y)) for x, y in star_poly(cx, cy, r, rot)]
    d.polygon(pts, fill=fill, outline=outline)
    # thicken outline
    for i in range(len(pts)):
        d.line([pts[i], pts[(i+1) % len(pts)]], fill=outline, width=sc(ow))

def rrect(d, box, rad, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=rad, fill=fill, outline=outline, width=width)

def paste_layer(base, layer, cx, cy, scale=1.0, rot=0.0, alpha=1.0):
    """Paste RGBA layer centered at (cx,cy) logical, scaled/rotated."""
    if scale != 1.0:
        layer = layer.resize((max(1,int(layer.width*scale)), max(1,int(layer.height*scale))), Image.LANCZOS)
    if rot:
        layer = layer.rotate(-rot, expand=True, resample=Image.BICUBIC)
    if alpha < 1.0:
        a = layer.getchannel("A").point(lambda v: int(v * alpha))
        layer = layer.copy(); layer.putalpha(a)
    base.alpha_composite(layer, (sc(cx) - layer.width//2, sc(cy) - layer.height//2))

# ---------------------------------------------------------------- cards
def card_post():
    w, h = 280, 240
    im = Image.new("RGBA", (sc(w+40), sc(h+40)), (0,0,0,0))
    d = ImageDraw.Draw(im)
    x0, y0 = sc(20), sc(20)
    rrect(d, [x0, y0, x0+sc(w), y0+sc(h)], sc(26), fill=MINT, outline=INK, width=sc(7))
    # media thumb with play button
    rrect(d, [x0+sc(24), y0+sc(24), x0+sc(130), y0+sc(110)], sc(14), fill=ORANGE, outline=INK, width=sc(5))
    tri = [(x0+sc(66), y0+sc(52)), (x0+sc(66), y0+sc(82)), (x0+sc(94), y0+sc(67))]
    d.polygon(tri, fill=CREAM, outline=INK)
    for i in range(3):
        d.line([tri[i], tri[(i+1) % 3]], fill=INK, width=sc(4))
    # text bars
    rrect(d, [x0+sc(148), y0+sc(34), x0+sc(256), y0+sc(56)], sc(11), fill=INK)
    rrect(d, [x0+sc(148), y0+sc(70), x0+sc(224), y0+sc(90)], sc(10), fill=(90,90,90))
    # bottom row: heart + bar
    d.ellipse([x0+sc(26), y0+sc(150), x0+sc(66), y0+sc(190)], fill=PINK, outline=INK, width=sc(5))
    rrect(d, [x0+sc(84), y0+sc(158), x0+sc(250), y0+sc(182)], sc(12), fill=INK)
    return im

def card_browser():
    w, h = 320, 230
    im = Image.new("RGBA", (sc(w+40), sc(h+40)), (0,0,0,0))
    d = ImageDraw.Draw(im)
    x0, y0 = sc(20), sc(20)
    rrect(d, [x0, y0, x0+sc(w), y0+sc(h)], sc(24), fill=(255,255,255), outline=INK, width=sc(7))
    # top bar
    d.rounded_rectangle([x0, y0, x0+sc(w), y0+sc(56)], radius=sc(24), fill=YELLOW, outline=INK, width=sc(7))
    d.rectangle([x0, y0+sc(30), x0+sc(w), y0+sc(56)], fill=YELLOW)
    d.line([x0, y0+sc(56), x0+sc(w), y0+sc(56)], fill=INK, width=sc(7))
    for i, col in enumerate([ORANGE, MINT, INK]):
        cx = x0+sc(34)+i*sc(34)
        d.ellipse([cx-sc(9), y0+sc(19), cx+sc(9), y0+sc(37)], fill=col, outline=INK, width=sc(3))
    # content bars + button
    rrect(d, [x0+sc(28), y0+sc(84), x0+sc(292), y0+sc(106)], sc(11), fill=INK)
    rrect(d, [x0+sc(28), y0+sc(122), x0+sc(240), y0+sc(142)], sc(10), fill=(90,90,90))
    rrect(d, [x0+sc(28), y0+sc(164), x0+sc(148), y0+sc(200)], sc(18), fill=ORANGE, outline=INK, width=sc(5))
    return im

def card_phone(t=0.0):
    w, h = 170, 290
    im = Image.new("RGBA", (sc(w+40), sc(h+40)), (0,0,0,0))
    d = ImageDraw.Draw(im)
    x0, y0 = sc(20), sc(20)
    rrect(d, [x0, y0, x0+sc(w), y0+sc(h)], sc(30), fill=LAV, outline=INK, width=sc(7))
    rrect(d, [x0+sc(16), y0+sc(18), x0+sc(w-16), y0+sc(h-18)], sc(20), fill=CREAM, outline=INK, width=sc(4))
    # voice waveform
    base_h = [0.35, 0.62, 0.95, 0.55, 1.0, 0.72, 0.42]
    maxh = 120.0; cy = y0 + sc(150); bx = x0 + sc(38)
    for i, bh in enumerate(base_h):
        amp = bh * (0.72 + 0.28 * math.sin(t*3.0 + i*1.35))
        hh = sc(maxh * amp / 2)
        col = ORANGE if i % 3 == 1 else INK
        d.rounded_rectangle([bx - sc(6), cy - hh, bx + sc(6), cy + hh], radius=sc(6), fill=col)
        bx += sc(17)
    rrect(d, [x0+sc(45), y0+sc(h-46), x0+sc(w-45), y0+sc(h-30)], sc(8), fill=INK)
    return im

# ---------------------------------------------------------------- shop
SHOP_CX, SHOP_CY = 960, 600
def shop_strokes():
    """Return list of polylines (logical coords) making the storefront outline."""
    strokes = []
    # 1. sign board
    strokes.append([(870,386),(1050,386),(1050,462),(870,462),(870,386)])
    # 2. awning trapezoid + stripes
    strokes.append([(748,478),(1172,478),(1144,566),(776,566),(748,478)])
    for x in (830, 912, 994, 1076):
        strokes.append([(x,478),(x-18,566)])
    # 3. body
    strokes.append([(776,566),(1144,566),(1144,806),(776,806),(776,566)])
    # 4. door
    strokes.append([(928,668),(992,668),(992,806),(928,806),(928,668)])
    # 5. window + cross
    strokes.append([(806,636),(894,636),(894,716),(806,716),(806,636)])
    strokes.append([(850,636),(850,716)])
    strokes.append([(806,676),(894,676)])
    return strokes

def draw_shop(img, p, fill_p, lw=7):
    d = ImageDraw.Draw(img)
    # fills fade in under the outline
    if fill_p > 0:
        ov = Image.new("RGBA", img.size, (0,0,0,0))
        dd = ImageDraw.Draw(ov)
        a = int(255 * fill_p)
        # awning stripes
        xs = [748, 830, 912, 994, 1076, 1172]
        for i in range(5):
            col = ORANGE if i % 2 == 0 else (255,255,255)
            dd.polygon([(sc(xs[i]),sc(478)),(sc(xs[i+1]),sc(478)),
                        (sc(xs[i+1]-18),sc(566)),(sc(xs[i]-18),sc(566))], fill=col+(a,))
        dd.rectangle([sc(872),sc(388),sc(1048),sc(460)], fill=YELLOW+(a,))
        dd.rectangle([sc(808),sc(638),sc(892),sc(714)], fill=MINT+(int(a*0.85),))
        dd.rectangle([sc(930),sc(670),sc(990),sc(804)], fill=ORANGE+(a,))
        img.alpha_composite(ov)
        draw_star(img, 960, 424, 22, 12, fill=INK, outline=INK, ow=1) if fill_p > 0.9 else None
    # progressive outline
    strokes = shop_strokes()
    segs = []
    total = 0.0
    for st in strokes:
        L = 0.0
        for i in range(len(st)-1):
            L += math.dist(st[i], st[i+1])
        segs.append(L); total += L
    remain = p * total
    for st, L in zip(strokes, segs):
        if remain <= 0: break
        if remain >= L:
            d.line([(sc(x),sc(y)) for x,y in st], fill=INK, width=sc(lw), joint="curve")
            remain -= L
        else:
            pts = [st[0]]; left = remain
            for i in range(len(st)-1):
                seg = math.dist(st[i], st[i+1])
                if left >= seg:
                    pts.append(st[i+1]); left -= seg
                else:
                    f = left/seg
                    pts.append((lerp(st[i][0],st[i+1][0],f), lerp(st[i][1],st[i+1][1],f)))
                    break
            if len(pts) > 1:
                d.line([(sc(x),sc(y)) for x,y in pts], fill=INK, width=sc(lw), joint="curve")
            break

# ---------------------------------------------------------------- background
def make_bg():
    im = Image.new("RGBA", (sc(W), sc(H)), CREAM + (255,))
    d = ImageDraw.Draw(im, "RGBA")
    # soft glows
    for (gx, gy, r, col, a) in [(1640, 120, 260, ORANGE, 26), (200, 640, 300, LAV, 20)]:
        glow = Image.new("RGBA", (sc(r*2), sc(r*2)), (0,0,0,0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse([0, 0, sc(r*2), sc(r*2)], fill=col+(a,))
        im.alpha_composite(glow, (sc(gx-r), sc(gy-r)))
    # wavy lines
    waves = [(240, YELLOW, 76), (420, MINT, 66), (610, LAV, 61), (790, PINK, 51)]
    for wy, col, a in waves:
        pts = []
        for x in range(-40, W+41, 20):
            pts.append((sc(x), sc(wy + 28*math.sin((x+wy)/160.0))))
        d.line(pts, fill=col+(a,), width=sc(3))
    return im

# ---------------------------------------------------------------- layout data
CARDS = [
    # name, scatter(x,y,rot), organized(x,y,rot), pop window
    ("post",    (300, 320, -13), (470, 600, 0), (0.25, 0.80)),
    ("browser", (1560, 250, 9),  (1400, 400, 0), (0.40, 0.95)),
    ("phone",   (1640, 820, 16), (1450, 780, 0), (0.55, 1.10),
)]
SHOP_DRAW = (1.0, 2.7)
FILL_IN = (2.55, 2.95)
ORG_T = (2.8, 3.9)
CLUSTER_OUT = (4.55, 5.35)
WORD_T = (5.0, 6.3)
SHADOW_DELAY = 0.24
KICK_T = (6.3, 6.9)
SUB_T = (6.55, 7.15)
SWASH_T = (6.35, 7.05)
STAR_FLY = (5.5, 6.2)
STAR_HOME = (170, 170)

def render_frame(t, bg, fonts, cache):
    im = bg.copy()
    f_anton_big, f_anton_sub, f_cairo_kick, arabic_kick = fonts
    d = ImageDraw.Draw(im)

    # ---- cluster (shop + cards)
    cluster_live = t < ORG_T[1]
    if cluster_live:
        layer = Image.new("RGBA", im.size, (0,0,0,0))
        draw_shop(layer, prog(t, *SHOP_DRAW), prog(t, *FILL_IN))
        for name, (sx, sy, sr), (ox, oy, orr), (pa, pb) in CARDS:
            pop = ease_out_back(prog(t, pa, pb), 1.4)
            if pop <= 0: continue
            op = ease_out_back(prog(t, *ORG_T), 0.9)
            x, y = lerp(sx, ox, op), lerp(sy, oy, op)
            r = lerp(sr, orr, op)
            if t < ORG_T[0]:
                r += 2.2*math.sin(t*2.1 + hash(name) % 7)
                y += 8*math.sin(t*1.7 + hash(name) % 11)
            card = {"post": card_post, "browser": card_browser,
                    "phone": lambda: card_phone(t)}[name]()
            paste_layer(layer, card, x, y, scale=max(0.001, pop), rot=r)
        im.alpha_composite(layer)
        if t >= ORG_T[1] - 1.0/FPS:  # cache at final organized state
            cache["cluster"] = layer
    else:
        if "cluster" not in cache:
            layer = Image.new("RGBA", im.size, (0,0,0,0))
            draw_shop(layer, 1.0, 1.0)
            for name, _, (ox, oy, orr), _ in CARDS:
                card = {"post": card_post, "browser": card_browser,
                        "phone": lambda: card_phone(0)}[name]()
                paste_layer(layer, card, ox, oy, rot=orr)
            cache["cluster"] = layer
        op = ease_in_out_cubic(prog(t, *CLUSTER_OUT))
        s = lerp(1.0, 0.5, op)
        a = lerp(1.0, 0.25, op)
        # scale about cluster centroid (960,610), drift down to y~860
        lay = cache["cluster"]
        lay2 = lay.resize((int(lay.width*s), int(lay.height*s)), Image.LANCZOS)
        ch = lay2.getchannel("A").point(lambda v: int(v*a))
        lay2.putalpha(ch)
        bob = (1-op)*0 + op*8*math.sin(t*1.6)
        cx_from, cy_from = 960, 610
        cx_to, cy_to = 960, 610 + lerp(0, 300, op) + bob
        px = int(sc(cx_to) - sc(cx_from)*s)
        py = int(sc(cy_to) - sc(cy_from)*s)
        im.alpha_composite(lay2, (px, py))

    # ---- wordmark
    wp = ease_out_cubic(prog(t, *WORD_T))
    if wp > 0:
        rise = (1 - wp) * 150
        wa = clamp((t - WORD_T[0]) / 0.5)
        sp = ease_out_cubic(prog(t, WORD_T[0]+SHADOW_DELAY, WORD_T[1]+SHADOW_DELAY))
        offx = lerp(34, 10, sp); offy = lerp(36, 10, sp)
        word = "CANNAVARO"
        bbox = d.textbbox((0,0), word, font=f_anton_big)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        wcx, wcy = W//2, 470
        tl = Image.new("RGBA", im.size, (0,0,0,0))
        td = ImageDraw.Draw(tl)
        # orange shadow trails in
        if sp > 0:
            td.text((sc(wcx)-tw//2+sc(offx), sc(wcy+rise)-th//2+sc(offy)-bbox[1]),
                    word, font=f_anton_big, fill=ORANGE+(int(255*wa),))
        td.text((sc(wcx)-tw//2, sc(wcy+rise)-th//2-bbox[1]),
                word, font=f_anton_big, fill=INK+(int(255*wa),))
        im.alpha_composite(tl)
        cache["word_rect"] = (wcx, wcy, tw/SS, th/SS)

        # kicker (Arabic) above
        ka = prog(t, *KICK_T)
        if ka > 0:
            kl = Image.new("RGBA", im.size, (0,0,0,0))
            kd = ImageDraw.Draw(kl)
            kb = kd.textbbox((0,0), arabic_kick, font=f_cairo_kick)
            kd.text((sc(wcx)-(kb[2]-kb[0])//2, sc(300)-kb[1]),
                    arabic_kick, font=f_cairo_kick, fill=INK+(int(190*ka),))
            im.alpha_composite(kl)
        # sub line
        sa = prog(t, *SUB_T)
        if sa > 0:
            sl = Image.new("RGBA", im.size, (0,0,0,0))
            sd = ImageDraw.Draw(sl)
            sub = "M E D I A   •   C O N T E N T   •   W E B"
            sb = sd.textbbox((0,0), sub, font=f_anton_sub)
            sd.text((sc(wcx)-(sb[2]-sb[0])//2, sc(660)-sb[1]),
                    sub, font=f_anton_sub, fill=INK+(int(200*sa),))
            im.alpha_composite(sl)
        # scribble swash under wordmark
        sw = prog(t, *SWASH_T)
        if sw > 0:
            rnd = random.Random(7)
            wl = Image.new("RGBA", im.size, (0,0,0,0))
            wd = ImageDraw.Draw(wl)
            x0, x1 = sc(wcx) - tw//2 + sc(14), sc(wcx) + tw//2 - sc(14)
            yb = sc(wcy) + th//2 + sc(30)
            for pas in range(2):
                pts = []
                off = pas*sc(8) - sc(4)
                for i in range(61):
                    fx = i/60.0
                    x = lerp(x0, x1, fx)
                    y = yb + off + sc(7)*math.sin(fx*math.pi*3.2 + pas*1.7) + sc(rnd.uniform(-2,2))
                    pts.append((x, y))
                cut = int(len(pts) * sw)
                if cut > 1:
                    wd.line(pts[:cut], fill=MINT+(225,), width=sc(20), joint="curve")
            im.alpha_composite(wl)

    # ---- sparkle star
    s_in = ease_out_back(prog(t, 0.15, 0.65), 1.6)
    if s_in > 0:
        fly = ease_in_out_cubic(prog(t, *STAR_FLY))
        sx, sy = STAR_HOME
        if fly > 0 and "word_rect" in cache:
            wcx, wcy, ww, wh = cache["word_rect"]
            tx, ty = wcx + ww/2 + 46, wcy - wh/2 - 20
            sx, sy = lerp(STAR_HOME[0], tx, fly), lerp(STAR_HOME[1], ty, fly)
        rot = (t * 55) % 360
        r = 64 * s_in * (1 + 0.05*math.sin(t*4))
        draw_star(im, sx, sy, r, rot)

    return im.convert("RGB").resize((W, H), Image.LANCZOS)

def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "frames")
    os.makedirs(out, exist_ok=True)
    import arabic_reshaper
    from bidi.algorithm import get_display
    arabic_kick = get_display(arabic_reshaper.reshape("وكالة دعاية وتسويق رقمي"))
    fonts = (
        ImageFont.truetype(ANTON, sc(220)),
        ImageFont.truetype(ANTON, sc(46)),
        ImageFont.truetype(CAIRO, sc(58)),
        arabic_kick,
    )
    bg = make_bg()
    cache = {}
    for n in range(NFRAMES):
        t = n / FPS
        frame = render_frame(t, bg, fonts, cache)
        frame.save(os.path.join(out, "%04d.png" % n))
        if n % 30 == 0:
            print("frame", n, "/", NFRAMES, flush=True)
    print("done")

if __name__ == "__main__":
    main()

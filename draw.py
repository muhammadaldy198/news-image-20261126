#!/usr/bin/env python3
"""Render THE WORLD — news-image-20261126 v2 broadsheet (35 stories, 7 regions).
Fresh authoring for v2: JSON -> PIL, fixed slot budget, text-box audit log.
Deterministic: no random, no time, no network. Render with office venv python3.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 12
GUT = 8
PAPER = (247, 243, 234)
INK = (26, 26, 26)
RED = (179, 38, 30)
NAVY = (30, 42, 68)
NAVY2 = (18, 30, 52)
GOLD = (201, 162, 39)
GREY = (90, 88, 82)
LIGHT = (232, 228, 218)
SEA = (214, 222, 228)
LAND = (196, 190, 174)

FDIR = "/usr/share/fonts/truetype/noto"

def F(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)

DISPLAY_BLACK = lambda s: F("NotoSerifDisplay-Black.ttf", s)
DISPLAY_BOLD = lambda s: F("NotoSerifDisplay-Bold.ttf", s)
SERIF_BOLD = lambda s: F("NotoSerif-Bold.ttf", s)
SERIF = lambda s: F("NotoSerif-Regular.ttf", s)
SANS_BOLD = lambda s: F("NotoSans-Bold.ttf", s)
SANS = lambda s: F("NotoSans-Regular.ttf", s)
MONO = lambda s: F("NotoSansMono-Regular.ttf", s)
MONO_BOLD = lambda s: F("NotoSansMono-Bold.ttf", s)

BOXES = []

def T(d, x, y, s, font, fill=INK, anchor="la"):
    """Draw text, log its bbox for the overlap audit. Returns (w, h)."""
    bbox = d.textbbox((x, y), s, font=font, anchor=anchor)
    d.text((x, y), s, font=font, fill=fill, anchor=anchor)
    BOXES.append([bbox[0], bbox[1], bbox[2], bbox[3], s[:40]])
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def wrap(d, s, font, max_w):
    """Greedy word wrap; returns list of lines, each fitting max_w."""
    words, lines, cur = s.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def fit_lines(d, s, font, max_w, max_lines, what):
    lines = wrap(d, s, font, max_w)
    assert len(lines) <= max_lines, f"OVERFLOW {what}: {len(lines)} lines: {s!r}"
    return lines

def rule(d, x0, y0, x1, y1, fill=INK, w=1):
    d.line([(x0, y0), (x1, y1)], fill=fill, width=w)

# Pixel budget: one table controls every y. Must sum to 1024.
BUDGET = [
    ("kicker", 14), ("masthead", 78), ("strap", 16), ("heroes", 238),
    ("numbers", 34), ("minis", 192), ("also_on", 214), ("map", 128),
    ("timeline", 28), ("date_check", 48), ("ticker", 22), ("footer", 12),
]
assert sum(h for _, h in BUDGET) == 1024, sum(h for _, h in BUDGET)
Y = {}
_y = 0
for _name, _h in BUDGET:
    Y[_name] = _y
    _y += _h

def main():
    here = os.path.dirname(os.path.abspath(__file__))
    data = json.load(open(os.path.join(here, "stories.json")))
    meta = data["meta"]
    im = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(im)

    # ---- kicker ----
    y = Y["kicker"]
    T(d, MARGIN, y + 2, "EST. 2026 · ONE DAY, ONE PAGE", SANS_BOLD(9), GREY)
    T(d, W - MARGIN, y + 2, "PRICE: FREE · NO. 331", SANS_BOLD(9), GREY, anchor="ra")
    rule(d, MARGIN, y + 13, W - MARGIN, y + 13, INK, 1)

    # ---- masthead ----
    y = Y["masthead"]
    # left ear
    d.rectangle([MARGIN, y + 8, MARGIN + 168, y + 70], outline=INK, width=1)
    T(d, MARGIN + 8, y + 12, "THURSDAY", SANS_BOLD(11), INK)
    T(d, MARGIN + 8, y + 27, "26 NOVEMBER 2026", SANS_BOLD(11), INK)
    T(d, MARGIN + 8, y + 44, "BRUSSELS · SEOUL", SANS(9), GREY)
    T(d, MARGIN + 8, y + 56, "NEW YORK · BOLOGNA", SANS(9), GREY)
    # right ear
    d.rectangle([W - MARGIN - 168, y + 8, W - MARGIN, y + 70], outline=INK, width=1)
    T(d, W - MARGIN - 160, y + 12, "35 DATED STORIES", SANS_BOLD(11), INK)
    T(d, W - MARGIN - 160, y + 27, "9 REGIONS", SANS_BOLD(11), INK)
    T(d, W - MARGIN - 160, y + 42, "ALL DATED", SANS_BOLD(11), RED)
    T(d, W - MARGIN - 160, y + 57, "EVERY STORY SOURCED", SANS(9), GREY)
    # title
    T(d, W // 2, y - 4, "THE WORLD", DISPLAY_BLACK(62), INK, anchor="ma")
    T(d, W // 2, y + 64, "Thursday, 26 November 2026", SERIF(12), GREY, anchor="ma")
    rule(d, MARGIN, y + 77, W - MARGIN, y + 77, INK, 2)

    # ---- strap ----
    y = Y["strap"]
    T(d, W // 2, y + 2, meta["strap"], SANS_BOLD(11), RED, anchor="ma")
    rule(d, MARGIN, y + 15, W - MARGIN, y + 15, INK, 1)

    heroes(d, data, Y["heroes"])
    numbers(d, data, Y["numbers"])
    minis(d, data, Y["minis"])
    also_on(d, data, Y["also_on"])
    world_map(d, data, Y["map"])
    timeline(d, data, Y["timeline"])
    date_check(d, data, Y["date_check"])
    ticker(d, data, Y["ticker"])

    # ---- footer ----
    y = Y["footer"]
    T(d, W // 2, y + 1, meta["footer"], SANS(8), GREY, anchor="ma")

    out = os.path.join(here, "entry.png")
    im.save(out, "PNG")
    with open(os.path.join(here, "boxes.json"), "w") as f:
        json.dump(BOXES, f)
    print(f"wrote {out} {os.path.getsize(out)} bytes, {len(BOXES)} text boxes")

# ---------------- heroes ----------------
def hero_cols():
    cw = (W - 2 * MARGIN - 2 * GUT) / 3
    return [MARGIN + i * (cw + GUT) for i in range(3)], cw

def heroes(d, data, y0):
    xs, cw = hero_cols()
    for hero, x in zip(data["heroes"], xs):
        x = int(x)
        w = int(cw)
        # tag line
        T(d, x, y0 + 2, hero["tag"], SANS_BOLD(10), RED)
        T(d, x + w, y0 + 2, hero["when"] + " · " + hero["ver"], SANS_BOLD(9), GREY, anchor="ra")
        rule(d, x, y0 + 16, x + w, y0 + 16, INK, 1)
        # headline: max 3 lines
        lines = fit_lines(d, hero["headline"], DISPLAY_BOLD(20), w, 3, "hero headline")
        yy = y0 + 20
        for ln in lines:
            T(d, x, yy, ln, DISPLAY_BOLD(20), INK)
            yy += 23
        # art: fixed slot 100px
        ay = y0 + 20 + 3 * 23 + 4
        if hero["n"] == 1:
            art_council(d, x, ay, w, 100, hero["banner"])
        elif hero["n"] == 2:
            art_bok(d, x, ay, w, 100, hero["banner"])
        else:
            art_parade(d, x, ay, w, 100, hero["banner"])
        # deck: max 3 lines
        dy = ay + 100 + 5
        dlines = fit_lines(d, hero["deck"], SERIF(11), w, 3, "hero deck")
        for ln in dlines:
            T(d, x, dy, ln, SERIF(11), INK)
            dy += 13
        # source line
        T(d, x, y0 + 238 - 12, hero["place"] + " — " + hero["source"], SANS(8), GREY)

def star(d, cx, cy, r, fill):
    import math
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)

def art_council(d, x, y, w, h, banner):
    # dusk-navy sky
    for i in range(h):
        t = i / h
        d.line([(x, y + i), (x + w, y + i)],
               fill=(int(NAVY2[0] + t * 14), int(NAVY2[1] + t * 16), int(NAVY2[2] + t * 22)))
    # ring of 12 gold stars
    cx, cy = x + w // 2, y + 42
    import math
    for k in range(12):
        ang = -math.pi / 2 + k * math.pi / 6
        star(d, cx + 62 * math.cos(ang), cy + 30 * math.sin(ang), 5, GOLD)
    # Europa building: glass block, lit windows
    bx, by, bw, bh = x + w // 2 - 58, y + 30, 116, 52
    d.rectangle([bx, by, bx + bw, by + bh], fill=(52, 68, 96), outline=(210, 210, 200))
    for r in range(4):
        for c in range(8):
            wx, wy = bx + 8 + c * 13, by + 7 + r * 11
            d.rectangle([wx, wy, wx + 8, wy + 6],
                        fill=GOLD if (r + c) % 3 else (150, 170, 200))
    # lantern roof
    d.polygon([(bx + 20, by), (bx + bw - 20, by), (bx + bw // 2, by - 12)], fill=GOLD)
    # flags row
    flag_cols = [(0, 51, 153), (0, 87, 184), (0, 0, 0)]
    for i, fc in enumerate(flag_cols):
        fx = x + 14 + i * 22
        d.line([(fx, y + h - 26), (fx, y + h - 12)], fill=(220, 220, 210), width=2)
        d.rectangle([fx, y + h - 26, fx + 16, y + h - 17], fill=fc)
    d.rectangle([x + 90, y + h - 26, x + 106, y + h - 17], fill=(255, 215, 0))
    d.rectangle([x + 90, y + h - 22, x + 106, y + h - 17], fill=(0, 87, 184))
    # crowd silhouettes
    for i in range(9):
        px = x + 150 + i * 18
        d.ellipse([px, y + h - 24, px + 9, y + h - 15], fill=(12, 18, 30))
        d.rectangle([px - 1, y + h - 15, px + 10, y + h - 4], fill=(12, 18, 30))
    # red banner bar
    d.rectangle([x, y + h - 14, x + w, y + h], fill=RED)
    T(d, x + w // 2, y + h - 12, banner, SANS_BOLD(10), (255, 255, 255), anchor="ma")

def art_bok(d, x, y, w, h, banner):
    for i in range(h):
        t = i / h
        d.line([(x, y + i), (x + w, y + i)],
               fill=(int(NAVY2[0] + t * 10), int(NAVY2[1] + t * 12), int(NAVY2[2] + t * 18)))
    # gold chip, centre-left
    cx, cy, cw, ch = x + 26, y + 18, 96, 56
    d.rectangle([cx, cy, cx + cw, cy + ch], fill=(44, 58, 84), outline=GOLD, width=2)
    d.rectangle([cx + 30, cy + 16, cx + 66, cy + 40], fill=(24, 34, 58), outline=GOLD)
    for k in range(5):
        d.line([(cx - 8, cy + 8 + k * 10), (cx, cy + 8 + k * 10)], fill=GOLD, width=2)
        d.line([(cx + cw, cy + 8 + k * 10), (cx + cw + 8, cy + 8 + k * 10)], fill=GOLD, width=2)
    # circuit traces
    d.line([(cx + 8, cy + 48), (cx + 8, cy + 62), (cx + 30, cy + 62)], fill=GOLD, width=2)
    d.line([(cx + cw - 8, cy + 48), (cx + cw - 8, cy + 62), (cx + cw - 30, cy + 62)], fill=GOLD, width=2)
    # rising red chart + arrow
    pts = [(x + 150, y + 66), (x + 185, y + 52), (x + 215, y + 56), (x + 250, y + 34),
           (x + 285, y + 38), (x + 312, y + 16)]
    d.line(pts, fill=(230, 60, 45), width=4)
    d.polygon([(x + 312, y + 16), (x + 300, y + 14), (x + 308, y + 28)], fill=(230, 60, 45))
    for px, py in pts:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=(255, 255, 255))
    # factory silhouette right
    d.rectangle([x + 268, y + 66, x + 318, y + 86], fill=(12, 18, 30))
    d.rectangle([x + 276, y + 52, x + 284, y + 66], fill=(12, 18, 30))
    d.rectangle([x + 292, y + 58, x + 300, y + 66], fill=(12, 18, 30))
    for wx in (272, 282, 292, 302):
        d.rectangle([wx, y + 70, wx + 5, y + 76], fill=GOLD)
    # red banner bar
    d.rectangle([x, y + h - 14, x + w, y + h], fill=RED)
    T(d, x + w // 2, y + h - 12, banner, SANS_BOLD(10), (255, 255, 255), anchor="ma")

def art_parade(d, x, y, w, h, banner):
    # storm-grey dusk sky (balloons GROUNDED — never flying)
    for i in range(h):
        t = i / h
        d.line([(x, y + i), (x + w, y + i)],
               fill=(int(70 + t * 30), int(78 + t * 26), int(96 + t * 22)))
    # storm clouds
    for cx, cy, cr in [(x + 60, y + 12, 26), (x + 120, y + 8, 32), (x + 200, y + 14, 28),
                       (x + 270, y + 10, 30)]:
        d.ellipse([cx - cr, cy - cr // 2, cx + cr, cy + cr // 2], fill=(52, 58, 72))
    # street + buildings
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(58, 56, 52))
    for bx, bw, bh in [(x + 6, 34, 34), (x + 300, 22, 26)]:
        d.rectangle([bx, y + h - 22 - bh, bx + bw, y + h - 22], fill=(40, 42, 50))
        for wy in range(y + h - 22 - bh + 5, y + h - 24, 9):
            for wx in range(bx + 5, bx + bw - 4, 9):
                d.rectangle([wx, wy, wx + 4, wy + 5], fill=(200, 180, 90))
    # GROUNDED balloon 1: big sagging balloon held low, ropes to stakes
    d.ellipse([x + 52, y + 34, x + 150, y + 74], fill=(196, 60, 48))
    d.ellipse([x + 66, y + 40, x + 104, y + 58], fill=(220, 110, 95))
    d.line([(x + 70, y + 72), (x + 58, y + h - 22)], fill=(230, 230, 220), width=2)
    d.line([(x + 132, y + 72), (x + 146, y + h - 22)], fill=(230, 230, 220), width=2)
    d.polygon([(x + 54, y + h - 22), (x + 62, y + h - 22), (x + 58, y + h - 30)], fill=(120, 110, 90))
    d.polygon([(x + 142, y + h - 22), (x + 150, y + h - 22), (x + 146, y + h - 30)], fill=(120, 110, 90))
    # sandbags
    for sx in (x + 66, x + 78, x + 128, x + 140):
        d.ellipse([sx, y + h - 28, sx + 14, y + h - 20], fill=(110, 96, 70))
    # GROUNDED balloon 2: half-deflated, lying low on the right
    d.ellipse([x + 196, y + 48, x + 292, y + 76], fill=(58, 110, 180))
    d.ellipse([x + 210, y + 52, x + 252, y + 66], fill=(110, 160, 210))
    d.line([(x + 214, y + 74), (x + 206, y + h - 22)], fill=(230, 230, 220), width=2)
    d.line([(x + 272, y + 74), (x + 282, y + h - 22)], fill=(230, 230, 220), width=2)
    # crew figures holding ropes
    for px in (x + 160, x + 176, x + 296, x + 308):
        d.ellipse([px, y + h - 40, px + 8, y + h - 32], fill=(16, 16, 16))
        d.rectangle([px - 1, y + h - 32, px + 9, y + h - 22], fill=(16, 16, 16))
    # red banner bar
    d.rectangle([x, y + h - 14, x + w, y + h], fill=RED)
    T(d, x + w // 2, y + h - 12, banner, SANS_BOLD(10), (255, 255, 255), anchor="ma")

# ---------------- numbers ----------------
def numbers(d, data, y0):
    d.rectangle([MARGIN, y0 + 1, W - MARGIN, y0 + 33], outline=INK, width=1)
    cw = (W - 2 * MARGIN) / 6
    for i, row in enumerate(data["numbers"]):
        x = MARGIN + i * cw
        if i:
            rule(d, int(x), y0 + 5, int(x), y0 + 29, GREY, 1)
        T(d, int(x + cw / 2), y0 + 3, row["value"], SERIF_BOLD(16), RED, anchor="ma")
        T(d, int(x + cw / 2), y0 + 22, row["label"], SANS(8), GREY, anchor="ma")

# ---------------- minis ----------------
def mini_cols():
    cw = (W - 2 * MARGIN - 4 * GUT) / 5
    return [MARGIN + i * (cw + GUT) for i in range(5)], cw

def minis(d, data, y0):
    xs, cw = mini_cols()
    row_h = 96
    for idx, mini in enumerate(data["minis"]):
        r, c = divmod(idx, 5)
        x = int(xs[c])
        w = int(cw)
        y = y0 + r * row_h
        art_mini(d, mini["n"], x, y, w, 30)
        T(d, x, y + 32, mini["tag"], SANS_BOLD(9), RED)
        T(d, x + w, y + 32, mini["when"], SANS_BOLD(8), GREY, anchor="ra")
        lines = fit_lines(d, mini["headline"], SERIF_BOLD(12), w, 2, "mini headline")
        yy = y + 45
        for ln in lines:
            T(d, x, yy, ln, SERIF_BOLD(12), INK)
            yy += 14
        dlines = fit_lines(d, mini["deck"], SERIF(9), w, 2, "mini deck")
        yy = y + 45 + 2 * 14 + 2
        for ln in dlines:
            T(d, x, yy, ln, SERIF(9), INK)
            yy += 11
        if r == 0:
            rule(d, x, y + row_h - 2, x + w, y + row_h - 2, LIGHT, 1)

def art_mini(d, n, x, y, w, h):
    if n == 4:  # tennis court
        d.rectangle([x, y, x + w, y + h], fill=(46, 110, 62))
        d.rectangle([x, y, x + w, y + 4], fill=(240, 240, 230))
        d.line([(x + w // 2, y + 4), (x + w // 2, y + h)], fill=(240, 240, 230), width=1)
        d.ellipse([x + w - 26, y + 8, x + w - 10, y + 24], fill=(210, 220, 60))
    elif n == 5:  # refinery + flame
        d.rectangle([x, y, x + w, y + h], fill=(40, 36, 44))
        for tx in (x + 12, x + 40, x + 68):
            d.rectangle([tx, y + 12, tx + 14, y + h], fill=(70, 66, 76))
        d.polygon([(x + 110, y + 26), (x + 122, y + 6), (x + 134, y + 26)], fill=(240, 120, 30))
        d.ellipse([x + 116, y + 14, x + 128, y + 26], fill=(250, 200, 60))
        d.rectangle([x + 150, y + 18, x + w - 8, y + h], fill=(70, 66, 76))
    elif n == 6:  # missile over mountains
        d.rectangle([x, y, x + w, y + h], fill=(52, 60, 78))
        d.polygon([(x, y + h), (x + 50, y + 8), (x + 100, y + h)], fill=(38, 44, 58))
        d.polygon([(x + 90, y + h), (x + 150, y + 14), (x + w, y + h)], fill=(30, 36, 50))
        d.rectangle([x + w // 2 - 3, y + 2, x + w // 2 + 3, y + 20], fill=(235, 235, 225))
        d.polygon([(x + w // 2 - 3, y + 2), (x + w // 2 + 3, y + 2), (x + w // 2, y - 4)],
                  fill=(230, 60, 45))
    elif n == 7:  # fire on road
        d.rectangle([x, y, x + w, y + h], fill=(60, 58, 54))
        d.rectangle([x, y + h - 8, x + w, y + h], fill=(30, 30, 28))
        d.polygon([(x + 20, y + h - 8), (x + 40, y + 2), (x + 60, y + h - 8)], fill=(240, 120, 30))
        d.polygon([(x + 110, y + h - 8), (x + 128, y + 8), (x + 146, y + h - 8)], fill=(250, 180, 40))
        d.ellipse([x + 150, y + 4, x + 180, y + 16], fill=(120, 118, 112))
    elif n == 8:  # falling chart
        d.rectangle([x, y, x + w, y + h], fill=(28, 34, 52))
        pts = [(x + 8, y + 8), (x + 50, y + 12), (x + 95, y + 10), (x + 140, y + 18),
               (x + 180, y + 24)]
        d.line(pts, fill=(230, 60, 45), width=3)
        d.polygon([(x + 180, y + 24), (x + 168, y + 22), (x + 176, y + 12)], fill=(230, 60, 45))
        for px, py in pts:
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 255, 255))
    elif n == 9:  # mine shaft + lamp
        d.rectangle([x, y, x + w, y + h], fill=(92, 70, 44))
        d.rectangle([x + 20, y, x + 60, y + h], fill=(40, 28, 18))
        d.line([(x + 40, y), (x + 40, y + h)], fill=(200, 170, 90), width=2)
        d.ellipse([x + 110, y + 8, x + 126, y + 24], fill=(250, 210, 80))
        d.rectangle([x + 150, y + 16, x + w - 10, y + 22], fill=(60, 44, 28))
    elif n == 10:  # ballot box
        d.rectangle([x, y, x + w, y + h], fill=(120, 40, 36))
        d.rectangle([x + 60, y + 10, x + 130, y + h - 4], fill=(170, 52, 44))
        d.rectangle([x + 60, y + 10, x + 130, y + 16], fill=(120, 40, 36))
        d.rectangle([x + 86, y + 2, x + 104, y + 12], fill=(245, 243, 234))
        d.ellipse([x + 150, y + 8, x + 168, y + 26], fill=(255, 215, 0))
    elif n == 11:  # shopping bag
        d.rectangle([x, y, x + w, y + h], fill=(200, 60, 50))
        d.rectangle([x + 70, y + 8, x + 120, y + 26], fill=(245, 243, 234))
        d.line([(x + 80, y + 8), (x + 80, y + 2), (x + 110, y + 2), (x + 110, y + 8)],
               fill=(245, 243, 234), width=2)
        d.rectangle([x + 150, y + 10, x + 180, y + 22], fill=(255, 215, 0))
    elif n == 12:  # pumpjack
        d.rectangle([x, y, x + w, y + h], fill=(210, 170, 90))
        d.ellipse([x + 150, y + 4, x + 172, y + 26], fill=(250, 220, 120))
        d.polygon([(x + 20, y + h), (x + 90, y + 6), (x + 110, y + h)], fill=(50, 44, 38))
        d.rectangle([x + 120, y + 10, x + 170, y + 16], fill=(50, 44, 38))
    else:  # tube train
        d.rectangle([x, y, x + w, y + h], fill=(30, 34, 48))
        d.rounded_rectangle([x + 55, y + 4, x + 135, y + h - 2], radius=8, fill=(200, 40, 36))
        d.rectangle([x + 65, y + 10, x + 125, y + 18], fill=(180, 210, 230))
        d.ellipse([x + 88, y + 20, x + 102, y + 34], fill=(255, 255, 255))

# ---------------- also-on ----------------
def also_on(d, data, y0):
    T(d, MARGIN, y0 + 1, "ALSO ON — THURSDAY 26 NOVEMBER", SANS_BOLD(11), INK)
    T(d, W - MARGIN, y0 + 1, "WED = 25 NOV · THU = TODAY", SANS_BOLD(9), GREY, anchor="ra")
    rule(d, MARGIN, y0 + 15, W - MARGIN, y0 + 15, INK, 1)
    cw = (W - 2 * MARGIN - GUT) / 2
    pitch = 18
    for i, s in enumerate(data["also_on"]):
        col, row = divmod(i, 11)
        x = MARGIN + col * (cw + GUT)
        y = y0 + 18 + row * pitch
        # number in red, then headline + trimmed deck on one line
        num = f"{s['n']}."
        T(d, x, y, num, SERIF_BOLD(10), RED)
        nx = x + d.textlength(num + " ", font=SERIF_BOLD(10))
        head = s["headline"]
        # fit "headline — deck" into the column, reserving room for when-label
        avail = x + cw - nx - 30
        deck_words = s["deck"].split()
        deck = s["deck"]
        while deck_words:
            trial = head + " — " + deck
            if d.textlength(trial, font=SERIF(10)) <= avail:
                break
            deck_words = deck_words[:-1]
            deck = " ".join(deck_words) + "…"
        else:
            trial = head
        T(d, nx, y, trial, SERIF(10), INK)
        # when-label at right edge of the column
        T(d, x + cw, y, s["when"], SANS_BOLD(8), GREY, anchor="ra")

# ---------------- map ----------------
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 73), (-75, 72),
     (-65, 60), (-55, 52), (-60, 45), (-70, 42), (-75, 35), (-80, 25), (-90, 21),
     (-97, 16), (-105, 20), (-115, 28), (-125, 40), (-140, 60), (-155, 58), (-168, 66)],
    # South America
    [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-35, -8), (-40, -20), (-50, -30),
     (-60, -35), (-70, -45), (-73, -50), (-70, -30), (-70, -18), (-77, -12), (-80, -5), (-80, 10)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59), (18, 56),
     (21, 55), (24, 58), (28, 60), (30, 62), (30, 70), (25, 71), (18, 69), (12, 65),
     (5, 60), (-5, 58), (-10, 54), (-10, 44), (-10, 36)],
    # Africa
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31), (35, 28), (43, 12),
     (51, 11), (48, 0), (40, -10), (35, -20), (30, -30), (20, -35), (15, -30),
     (12, -18), (9, -1), (9, 4), (-8, 4), (-13, 8), (-17, 15)],
    # Asia
    [(30, 70), (40, 68), (55, 68), (70, 72), (90, 75), (110, 77), (130, 72), (150, 70),
     (170, 66), (178, 65), (170, 60), (160, 55), (150, 45), (140, 40), (130, 35),
     (127, 33), (122, 30), (115, 22), (108, 12), (105, 8), (100, 8), (95, 15),
     (90, 22), (85, 20), (80, 13), (77, 8), (72, 20), (66, 25), (60, 25), (55, 26),
     (50, 28), (48, 30), (44, 29), (40, 32), (35, 36), (30, 36), (30, 42), (30, 62), (30, 70)],
    # Australia
    [(113, -22), (114, -30), (115, -35), (120, -34), (129, -32), (137, -35), (140, -38),
     (145, -38), (150, -37), (153, -32), (153, -27), (146, -19), (142, -11), (137, -12),
     (132, -12), (126, -14), (122, -17), (118, -20), (113, -22)],
]

def world_map(d, data, y0):
    mx0, my0, mw, mh = MARGIN, y0 + 14, 624, 108
    T(d, MARGIN, y0 + 1, "THE WORLD AT A GLANCE — 16 PINS", SANS_BOLD(10), INK)
    T(d, mx0 + mw, y0 + 1, "PINS COLOUR-CODED BY REGION", SANS(8), GREY, anchor="ra")
    d.rectangle([mx0, my0, mx0 + mw, my0 + mh], fill=SEA, outline=INK, width=1)

    def proj(lon, lat):
        return (mx0 + (lon + 170) / 360 * mw, my0 + (75 - lat) / 130 * mh)

    for poly in CONTINENTS:
        d.polygon([proj(lon, lat) for lon, lat in poly], fill=LAND, outline=(120, 114, 100))
    for pin in data["map_pins"]:
        px, py = proj(pin["lon"], pin["lat"])
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=tuple(pin["c"]), outline=(255, 255, 255))
        lx, ly = px + pin["dx"], py + pin["dy"]
        anchor = "ra" if pin["dx"] < 0 else "la"
        T(d, lx, ly, pin["name"], SANS_BOLD(8), INK, anchor=anchor)
    # right panel: legend + by region (colour chips match the map pins)
    rx = mx0 + mw + 12
    rw = W - MARGIN - rx
    T(d, rx, y0 + 1, "HOW SURE", SANS_BOLD(10), RED)
    rule(d, rx, y0 + 15, rx + rw, y0 + 15, INK, 1)
    leg = ["CONFIRMED = decided or happened · REPORTED = named source",
           "EXPECTED = due, not yet taken · WED = Wed 25 Nov"]
    yy = y0 + 19
    for ln in leg:
        T(d, rx, yy, ln, SANS(9), INK)
        yy += 12
    T(d, rx, yy + 3, "BY REGION — 35 STORIES", SANS_BOLD(10), RED)
    rule(d, rx, yy + 17, rx + rw, yy + 17, INK, 1)
    yy += 21
    REGION_COLOURS = {"Europe": (29, 78, 216), "N. America": (14, 116, 144),
                      "Asia": (15, 118, 110), "Middle East": (194, 65, 12),
                      "Africa": (21, 128, 61), "Oceania": (126, 34, 206),
                      "Caribbean": (3, 105, 161), "S. America": (190, 24, 93),
                      "Space": (101, 163, 13)}
    for i, r in enumerate(data["by_region"]):
        col, row = divmod(i, 5)
        cx = rx + col * 180
        cy = yy + row * 12
        d.rectangle([cx, cy + 1, cx + 8, cy + 9], fill=REGION_COLOURS[r["region"]])
        T(d, cx + 12, cy, f"{r['region']} {r['count']}", SANS(9), INK)

# ---------------- timeline ----------------
def timeline(d, data, y0):
    rule(d, MARGIN, y0 + 2, W - MARGIN, y0 + 2, INK, 1)
    cw = (W - 2 * MARGIN) / 5
    for i, item in enumerate(data["timeline"]):
        x = MARGIN + i * cw
        T(d, int(x + cw / 2), y0 + 7, item["t"] + "  " + item["what"], MONO_BOLD(9), INK,
          anchor="ma")
    rule(d, MARGIN, y0 + 26, W - MARGIN, y0 + 26, INK, 1)

# ---------------- date check ----------------
def date_check(d, data, y0):
    d.rectangle([MARGIN, y0 + 2, W - MARGIN, y0 + 46], outline=RED, width=2)
    T(d, MARGIN + 8, y0 + 5, "DATE CHECK", SANS_BOLD(10), RED)
    lines = fit_lines(d, data["date_check"], SERIF(10), W - 2 * MARGIN - 92, 3, "date check")
    yy = y0 + 5
    for ln in lines:
        T(d, MARGIN + 92, yy, ln, SERIF(10), INK)
        yy += 13

# ---------------- ticker ----------------
def ticker(d, data, y0):
    d.rectangle([MARGIN, y0 + 1, W - MARGIN, y0 + 21], fill=NAVY)
    size = 10
    while size >= 8 and d.textlength(data["ticker"], font=MONO(size)) > W - 2 * MARGIN - 16:
        size -= 1
    T(d, W // 2, y0 + 5, data["ticker"], MONO(size), (255, 255, 255), anchor="ma")

if __name__ == "__main__":
    main()

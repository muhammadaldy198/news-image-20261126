#!/usr/bin/env python3
"""news-image-20261126 v3 — one-page broadsheet, 1024x1024, PIL render.
Fresh rewrite (Sari, 26 Nov 2026). JSON -> PIL, one budget table, no
silent truncation: every wrap asserts fit. Text boxes and art boxes are
logged to boxes.json (DRAW_LOG=1) so verify.py can check text-vs-text
AND text-vs-art overlap.
"""
import json
import os
import sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as f:
    DATA = json.load(f)

W = H = 1024
MARGIN = 12
GUTTER = 8
INNER = W - 2 * MARGIN  # 1000

PAPER = (247, 243, 234)
INK = (20, 20, 20)
GREY = (90, 88, 82)
LIGHT_GREY = (212, 208, 198)
RED = (179, 38, 30)
GOLD = (201, 162, 39)
NAVY_TOP = (18, 30, 52)
NAVY_BOT = (36, 62, 92)
MIDNAVY = (58, 86, 122)
SKY_STORM = (96, 116, 140)
MAP_LAND = (205, 200, 185)
MAP_SEA = (226, 231, 233)

FONT_DIR = "/usr/share/fonts/truetype/noto"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


F_BLACK = lambda s: font("NotoSerifDisplay-Black.ttf", s)
F_SDBOLD = lambda s: font("NotoSerifDisplay-Bold.ttf", s)
F_SERIF = lambda s: font("NotoSerif-Regular.ttf", s)
F_SERIFB = lambda s: font("NotoSerif-Bold.ttf", s)
F_SERIFI = lambda s: font("NotoSerif-Italic.ttf", s)
F_SANS = lambda s: font("NotoSans-Regular.ttf", s)
F_SANSB = lambda s: font("NotoSans-Bold.ttf", s)
F_SANSSB = lambda s: font("NotoSans-SemiBold.ttf", s)
F_MONO = lambda s: font("NotoSansMono-Regular.ttf", s)
F_MONOB = lambda s: font("NotoSansMono-Bold.ttf", s)

# ---- one budget table: (name, height); must sum to 1024 ----
BUDGET = [
    ("kicker", 16),
    ("masthead", 76),
    ("rule", 2),
    ("region_strip", 20),
    ("gap", 6),
    ("heroes", 196),
    ("gap", 6),
    ("minis1", 96),
    ("gap", 4),
    ("minis2", 96),
    ("gap", 6),
    ("also_header", 16),
    ("also_on", 209),
    ("gap", 6),
    ("map_row", 137),
    ("gap", 6),
    ("timeline", 24),
    ("gap", 4),
    ("ticker", 20),
    ("gap", 4),
    ("datecheck", 60),
    ("gap", 4),
    ("footer", 10),
]
assert sum(h for _, h in BUDGET) == 1024, sum(h for _, h in BUDGET)
Y = {}
_y = 0
for _name, _h in BUDGET:
    Y.setdefault(_name, []).append(_y)
    _y += _h
# y positions (first occurrence)
YY = {n: v[0] for n, v in Y.items()}

TEXT_BOXES = []  # (x0, y0, x1, y1, kind)
ART_BOXES = []  # (x0, y0, x1, y1, kind)


def txt(d, x, y, s, f, fill=INK, anchor="la", kind="text"):
    d.text((x, y), s, font=f, fill=fill, anchor=anchor)
    bb = d.textbbox((x, y), s, font=f, anchor=anchor)
    TEXT_BOXES.append((bb[0], bb[1], bb[2], bb[3], kind))
    return bb


def artbox(x0, y0, x1, y1, kind):
    ART_BOXES.append((x0, y0, x1, y1, kind))


def wrap(d, s, f, width):
    """Greedy wrap; returns lines that fit width."""
    words = s.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=f) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_lines(d, s, f, width, max_lines, what):
    lines = wrap(d, s, f, width)
    assert len(lines) <= max_lines, f"TRUNC {what}: {len(lines)}>{max_lines}: {s!r}"
    return lines


def draw_lines(d, x, y, lines, f, lh, fill=INK, kind="text"):
    for ln in lines:
        txt(d, x, y, ln, f, fill=fill, kind=kind)
        y += lh
    return y


def col_x(i, ncols, total=INNER):
    w = (total - (ncols - 1) * GUTTER) / ncols
    return MARGIN + i * (w + GUTTER), w


def hline(d, y, x0=MARGIN, x1=W - MARGIN, fill=INK, width=1):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)

# ---------------- hero art scenes (each >=5 layered elements) ----------------

def hero1_art(d, x0, y0, w, h):
    """Brussels: dusk-navy sky, 12 gold stars, Europa building, flags, crowd."""
    artbox(x0, y0, x0 + w, y0 + h, "hero_art")
    for i in range(h):
        t = i / max(1, h - 1)
        c = tuple(int(NAVY_TOP[k] + (NAVY_BOT[k] - NAVY_TOP[k]) * t) for k in range(3))
        d.line([(x0, y0 + i), (x0 + w, y0 + i)], fill=c)
    cx, cy, r = x0 + w // 2, y0 + 34, 26
    for k in range(12):
        import math
        a = math.pi * 2 * k / 12 - math.pi / 2
        sx, sy = cx + r * math.cos(a), cy + r * math.sin(a)
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=GOLD)
    # Europa building: grey block, lit windows
    bx, by, bw, bh = x0 + 28, y0 + h - 52, w - 56, 52
    d.rectangle([bx, by, bx + bw, by + bh], fill=(74, 82, 96))
    d.rectangle([bx, by, bx + bw, by + 6], fill=(52, 58, 70))
    for r_ in range(3):
        for c_ in range(9):
            wx = bx + 8 + c_ * ((bw - 16) // 9)
            wy = by + 12 + r_ * 12
            d.rectangle([wx, wy, wx + 7, wy + 6],
                        fill=(255, 214, 120) if (r_ + c_) % 3 else (150, 160, 175))
    # flags on poles
    for fx, fc in [(x0 + 14, (0, 51, 153)), (x0 + w - 22, (200, 16, 46))]:
        d.line([(fx, y0 + h - 52), (fx, y0 + h - 78)], fill=(230, 230, 220), width=2)
        d.rectangle([fx, y0 + h - 78, fx + 14, y0 + h - 68], fill=fc)
    # crowd silhouettes
    for i, px in enumerate(range(x0 + 8, x0 + w - 8, 14)):
        ph = 8 + (i % 3) * 2
        d.ellipse([px, y0 + h - ph - 4, px + 7, y0 + h - ph + 3], fill=(12, 14, 20))
        d.rectangle([px - 1, y0 + h - ph + 3, px + 8, y0 + h], fill=(12, 14, 20))


def hero2_art(d, x0, y0, w, h):
    """Seoul chip boom: dusk-navy, gold chip + circuit traces, rising chart,
    factory in MID-navy (lighter than sky) with LIT windows — no dark-on-dark."""
    artbox(x0, y0, x0 + w, y0 + h, "hero_art")
    for i in range(h):
        t = i / max(1, h - 1)
        c = tuple(int(NAVY_TOP[k] + (NAVY_BOT[k] - NAVY_TOP[k]) * t) for k in range(3))
        d.line([(x0, y0 + i), (x0 + w, y0 + i)], fill=c)
    # circuit traces
    for ty in (y0 + 14, y0 + 26, y0 + h - 18):
        d.line([(x0 + 8, ty), (x0 + w - 8, ty)], fill=(90, 130, 170), width=1)
        for tx in range(x0 + 30, x0 + w - 20, 44):
            d.ellipse([tx - 2, ty - 2, tx + 2, ty + 2], fill=(120, 165, 205))
    # gold chip, centre-left
    cx, cy, cw, ch = x0 + 96, y0 + 30, 92, 52
    for px in range(cx - 10, cx + cw + 10, 12):
        d.line([(px, cy - 8), (px, cy)], fill=GOLD, width=3)
        d.line([(px, cy + ch), (px, cy + ch + 8)], fill=GOLD, width=3)
    d.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=6, fill=(176, 138, 28),
                        outline=(232, 196, 90), width=2)
    d.rounded_rectangle([cx + 26, cy + 14, cx + cw - 26, cy + ch - 14], radius=3,
                        fill=(120, 92, 16))
    txt(d, cx + cw // 2, cy + 16, "3.25%", F_SANSB(15), fill=(255, 240, 190),
        anchor="ma", kind="art_label")
    # rising red chart, right
    pts = [(x0 + w - 118, y0 + h - 22), (x0 + w - 92, y0 + h - 44),
           (x0 + w - 66, y0 + h - 36), (x0 + w - 40, y0 + h - 62),
           (x0 + w - 16, y0 + h - 74)]
    d.line(pts, fill=(235, 70, 60), width=3)
    d.ellipse([pts[-1][0] - 3, pts[-1][1] - 3, pts[-1][0] + 3, pts[-1][1] + 3],
              fill=(255, 120, 110))
    # factory silhouette in MID-navy with lit windows (readable, not dark-on-dark)
    fx, fy = x0 + w - 118, y0 + h - 20
    d.rectangle([fx, fy - 14, fx + 104, fy], fill=MIDNAVY)
    d.rectangle([fx + 8, fy - 26, fx + 22, fy - 14], fill=MIDNAVY)
    d.rectangle([fx + 78, fy - 30, fx + 88, fy - 14], fill=MIDNAVY)
    for wx in range(fx + 6, fx + 100, 14):
        d.rectangle([wx, fy - 10, wx + 6, fy - 4], fill=(255, 214, 120))


def hero3_art(d, x0, y0, w, h):
    """Macy's postponed: storm sky, rain, RED balloon TETHERED to pegs +
    sandbags, BLUE balloon DEFLATED flat on the ground, crew holding ropes.
    No balloon flies."""
    artbox(x0, y0, x0 + w, y0 + h, "hero_art")
    for i in range(h):
        t = i / max(1, h - 1)
        c = tuple(int(SKY_STORM[k] + ((70, 82, 100)[k] - SKY_STORM[k]) * t)
                  for k in range(3))
        d.line([(x0, y0 + i), (x0 + w, y0 + i)], fill=c)
    # clouds
    for cx, cy, cr in [(x0 + 40, y0 + 12, 22), (x0 + 150, y0 + 8, 26),
                       (x0 + 260, y0 + 14, 20)]:
        d.ellipse([cx - cr, cy - 8, cx + cr, cy + 8], fill=(120, 138, 160))
    # rain streaks
    for rx in range(x0 + 6, x0 + w - 6, 18):
        d.line([(rx, y0 + 26), (rx - 4, y0 + 44)], fill=(170, 190, 205), width=1)
    # buildings, left + right edges
    d.rectangle([x0, y0 + h - 46, x0 + 34, y0 + h], fill=(58, 66, 80))
    d.rectangle([x0 + w - 34, y0 + h - 40, x0 + w, y0 + h], fill=(58, 66, 80))
    for wy in range(y0 + h - 40, y0 + h - 6, 10):
        d.rectangle([x0 + 6, wy, x0 + 12, wy + 5], fill=(255, 214, 120))
        d.rectangle([x0 + w - 28, wy, x0 + w - 22, wy + 5], fill=(255, 214, 120))
    # red balloon, tethered low over the street
    bx, by = x0 + w // 2 - 10, y0 + 26
    d.ellipse([bx - 34, by, bx + 34, by + 30], fill=(179, 38, 30))
    d.ellipse([bx - 34, by, bx + 34, by + 12], fill=(205, 60, 50))
    d.polygon([(bx - 34, by + 14), (bx - 42, by + 26), (bx - 30, by + 24)],
              fill=(179, 38, 30))
    # ropes down to ground pegs + sandbags
    gy = y0 + h - 4
    for px in (bx - 26, bx + 26):
        d.line([(px, by + 28), (px - 6, gy)], fill=(240, 235, 220), width=2)
        d.polygon([(px - 12, gy), (px, gy - 6), (px + 2, gy)], fill=(90, 80, 60))
    d.ellipse([bx - 52, gy - 8, bx - 30, gy], fill=(120, 105, 70))
    d.ellipse([bx + 30, gy - 8, bx + 52, gy], fill=(120, 105, 70))
    # blue balloon DEFLATED flat on the ground, right
    d.ellipse([x0 + w - 108, gy - 7, x0 + w - 52, gy], fill=(40, 90, 160))
    d.ellipse([x0 + w - 100, gy - 9, x0 + w - 60, gy - 3], fill=(70, 130, 200))
    # crew figures holding ropes
    for px in (bx - 58, bx + 58):
        d.ellipse([px - 3, gy - 22, px + 3, gy - 16], fill=(20, 20, 24))
        d.rectangle([px - 4, gy - 16, px + 4, gy], fill=(20, 20, 24))


# ---------------- mini art strips (16px tall, pictorial, 2-3 colours) ----------------

def mini_art(d, n, x0, y0, w, h=16):
    artbox(x0, y0, x0 + w, y0 + h, "mini_art")
    if n == 4:  # tennis court
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(46, 125, 70))
        d.rectangle([x0 + 8, y0 + 2, x0 + w - 8, y0 + h - 2], outline=(240, 240, 230), width=1)
        d.line([(x0 + w // 2, y0 + 2), (x0 + w // 2, y0 + h - 2)], fill=(240, 240, 230), width=1)
        d.ellipse([x0 + w - 30, y0 + 4, x0 + w - 22, y0 + 12], fill=(220, 230, 60))
    elif n == 5:  # refinery + flame
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(52, 48, 44))
        for tx in (x0 + 12, x0 + 30, x0 + 52):
            d.rectangle([tx, y0 + 6, tx + 6, y0 + h], fill=(30, 28, 26))
        d.polygon([(x0 + w - 34, y0 + 2), (x0 + w - 26, y0 + 10), (x0 + w - 42, y0 + 10)],
                  fill=(255, 140, 40))
        d.ellipse([x0 + w - 32, y0 + 8, x0 + w - 28, y0 + 12], fill=(255, 200, 80))
    elif n == 6:  # missile
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(58, 66, 76))
        d.polygon([(x0 + 20, y0 + 8), (x0 + 52, y0 + 8), (x0 + 62, y0 + 4),
                   (x0 + 52, y0 + 12), (x0 + 20, y0 + 12)], fill=(200, 205, 210))
        d.polygon([(x0 + 20, y0 + 8), (x0 + 12, y0 + 3), (x0 + 12, y0 + 13)],
                  fill=(179, 38, 30))
        for sx in range(x0 + 70, x0 + w - 8, 12):
            d.ellipse([sx, y0 + 6, sx + 5, y0 + 10], fill=(255, 200, 90))
    elif n == 7:  # fire
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(40, 36, 32))
        for fx in (x0 + 16, x0 + 44, x0 + 74, x0 + 104, x0 + 134, x0 + 162):
            d.polygon([(fx, y0 + 2), (fx + 5, y0 + 10), (fx + 10, y0 + 2),
                       (fx + 5, y0 + h)], fill=(255, 120, 30))
        d.rectangle([x0, y0 + h - 3, x0 + w, y0 + h], fill=(120, 30, 20))
    elif n == 8:  # falling chart
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(28, 32, 48))
        d.line([(x0 + 8, y0 + 3), (x0 + 50, y0 + 6), (x0 + 95, y0 + 5),
                (x0 + 140, y0 + 11), (x0 + w - 10, y0 + 13)], fill=(235, 70, 60), width=2)
        d.polygon([(x0 + w - 18, y0 + 9), (x0 + w - 8, y0 + 13), (x0 + w - 14, y0 + 15)],
                  fill=(235, 70, 60))
    elif n == 9:  # mine shaft
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(96, 70, 44))
        d.rectangle([x0 + w // 2 - 14, y0, x0 + w // 2 + 14, y0 + h], fill=(30, 20, 14))
        d.line([(x0 + w // 2 - 14, y0), (x0 + w // 2 + 14, y0)], fill=(255, 220, 120), width=2)
        d.ellipse([x0 + w // 2 - 3, y0 + 5, x0 + w // 2 + 3, y0 + 11], fill=(255, 220, 120))
    elif n == 10:  # ballot box
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(36, 62, 92))
        d.rectangle([x0 + 70, y0 + 5, x0 + 122, y0 + h - 2], fill=(240, 240, 235))
        d.rectangle([x0 + 82, y0 + 5, x0 + 110, y0 + 7], fill=(36, 62, 92))
        d.rectangle([x0 + 84, y0 - 0, x0 + 108, y0 + 5], fill=(255, 255, 255))
        d.line([(x0 + 84, y0 + 2), (x0 + 92, y0 + 8), (x0 + 106, y0 - 2)],
               fill=(179, 38, 30), width=2)
    elif n == 11:  # shopping bag
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(179, 38, 30))
        d.rectangle([x0 + 76, y0 + 4, x0 + 116, y0 + h - 1], fill=(255, 255, 255))
        d.arc([x0 + 84, y0 - 2, x0 + 108, y0 + 10], 180, 360, fill=(255, 255, 255), width=2)
        d.rectangle([x0 + 84, y0 + 8, x0 + 108, y0 + 10], fill=(179, 38, 30))
    elif n == 12:  # pumpjack
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(44, 44, 40))
        d.line([(x0 + 30, y0 + h), (x0 + 90, y0 + 3)], fill=(200, 170, 90), width=3)
        d.line([(x0 + 90, y0 + 3), (x0 + 150, y0 + 6)], fill=(200, 170, 90), width=3)
        d.line([(x0 + 150, y0 + 6), (x0 + 150, y0 + h)], fill=(200, 170, 90), width=2)
        d.ellipse([x0 + w - 40, y0 + 4, x0 + w - 28, y0 + 12], fill=(255, 200, 80))
    else:  # 13: tube train
        d.rectangle([x0, y0, x0 + w, y0 + h], fill=(140, 20, 20))
        d.rounded_rectangle([x0 + 60, y0 + 2, x0 + 132, y0 + h - 2], radius=4,
                            fill=(230, 230, 225))
        d.rectangle([x0 + 68, y0 + 4, x0 + 96, y0 + 8], fill=(30, 60, 120))
        d.rectangle([x0 + 100, y0 + 4, x0 + 124, y0 + 8], fill=(30, 60, 120))
        d.ellipse([x0 + w - 26, y0 + 4, x0 + w - 14, y0 + 12], outline=(255, 255, 255), width=2)
        d.line([(x0 + w - 20, y0 + 4), (x0 + w - 20, y0 + 12)], fill=(255, 255, 255), width=2)

# ---------------- schematic world map ----------------

CONTINENTS = {
    "asia": [(32, 70), (40, 68), (50, 69), (60, 69), (70, 72), (80, 73), (90, 75),
             (100, 77), (110, 74), (120, 73), (130, 72), (140, 72), (150, 70),
             (160, 69), (170, 66), (178, 65), (170, 60), (162, 56), (158, 52),
             (150, 59), (142, 55), (140, 50), (135, 45), (130, 42), (127, 40),
             (122, 38), (120, 32), (115, 25), (110, 20), (108, 12), (105, 9),
             (100, 7), (98, 12), (95, 16), (92, 20), (90, 22), (88, 22), (85, 19),
             (82, 17), (80, 13), (78, 8), (76, 10), (74, 20), (72, 20), (70, 24),
             (66, 25), (62, 25), (58, 26), (56, 26), (54, 26), (52, 25), (50, 29),
             (48, 30), (44, 29), (42, 27), (40, 25), (38, 20), (36, 18), (35, 15),
             (34, 12), (35, 20), (38, 25), (40, 30), (42, 35), (40, 40), (38, 45),
             (35, 50), (32, 55), (30, 60), (32, 65), (32, 70)],
    "namerica": [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
                 (-80, 73), (-75, 72), (-70, 62), (-65, 60), (-60, 55), (-55, 47),
                 (-60, 45), (-70, 42), (-75, 38), (-80, 32), (-85, 30), (-90, 29),
                 (-97, 26), (-105, 22), (-110, 24), (-115, 29), (-120, 34),
                 (-125, 40), (-125, 49), (-130, 55), (-140, 60), (-155, 58),
                 (-165, 60), (-168, 66)],
    "samerica": [(-80, 10), (-75, 11), (-70, 12), (-62, 10), (-55, 6), (-50, 4),
                 (-44, -3), (-35, -8), (-38, -15), (-40, -22), (-48, -28),
                 (-55, -35), (-62, -41), (-68, -50), (-70, -55), (-73, -50),
                 (-73, -40), (-73, -30), (-75, -20), (-80, -12), (-81, -5),
                 (-80, 2), (-80, 10)],
    "europe": [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (3, 53), (8, 57),
               (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 62),
               (32, 70), (40, 68), (44, 66), (40, 60), (35, 55), (30, 50),
               (28, 45), (23, 40), (20, 40), (15, 44), (12, 44), (8, 44),
               (3, 43), (0, 40), (-2, 37), (-6, 36), (-10, 36)],
    "africa": [(-6, 35), (0, 36), (10, 37), (11, 34), (20, 32), (30, 31), (32, 31),
               (35, 28), (37, 22), (40, 15), (43, 11), (48, 11), (51, 10),
               (48, 5), (42, 0), (40, -5), (38, -10), (35, -18), (32, -25),
               (28, -32), (20, -35), (16, -30), (14, -22), (12, -15), (12, -8),
               (9, 4), (4, 6), (-8, 5), (-13, 8), (-17, 12), (-17, 15), (-15, 20),
               (-12, 25), (-10, 30), (-6, 35)],
    "australia": [(114, -22), (114, -30), (116, -35), (120, -34), (125, -32),
                  (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
                  (145, -38), (150, -37), (153, -32), (153, -27), (150, -22),
                  (146, -19), (142, -11), (140, -17), (136, -15), (132, -12),
                  (130, -13), (126, -14), (122, -17), (118, -20), (114, -22)],
    "japan": [(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (141, 41),
              (143, 43), (141, 45), (140, 42), (138, 38), (134, 34), (131, 32)],
    "uk": [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (-2, 51),
           (-5, 50)],
    "nz": [(167, -45), (170, -42), (173, -40), (176, -38), (178, -37), (176, -40),
           (173, -43), (170, -46), (167, -45)],
}

# Display nudges for pins that would collide at this scale (true lon/lat kept
# in stories.json; leader line joins true spot to nudged pin).
PIN_NUDGE = {1: (4, -12), 2: (20, 12), 5: (-10, -8), 6: (-13, -9),
              7: (18, 16), 9: (-15, -11), 10: (-18, 12), 13: (-14, -10),
              22: (12, 10), 23: (-16, -10), 33: (-14, 10), 38: (17, 12)}
REGION_COLOR = {"Europe": (0, 51, 153), "N. America": (179, 38, 30),
                "Middle East": (120, 72, 20), "East Asia": (176, 138, 28),
                "SE Asia": (30, 120, 80), "South Asia": (140, 40, 120),
                "Africa": (20, 110, 140), "Latin America": (200, 90, 20),
                "Oceania": (60, 90, 160), "Global": (90, 90, 90)}


def project(mx0, my0, mw, mh, lon, lat):
    x = mx0 + (lon + 168) / 360 * mw
    y = my0 + (72 - lat) / 128 * mh
    return x, y


def paint_map(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], fill=MAP_SEA, outline=INK, width=1)
    for name in ("asia", "namerica", "samerica", "europe", "africa",
                 "australia", "japan", "uk", "nz"):
        pts = [project(x0, y0, w, h, lon, lat) for lon, lat in CONTINENTS[name]]
        d.polygon(pts, fill=MAP_LAND, outline=(150, 145, 130))
    txt(d, x0 + 6, y0 + 4, "THE WORLD IN ONE LOOK — 25 NUMBERED PINS",
        F_SANSB(10), fill=INK, kind="map_title")
    stories = {s["n"]: s for s in
               DATA["heroes"] + DATA["minis"] + DATA["also"]}
    for pin in DATA["pins"]:
        px, py = project(x0, y0, w, h, pin["lon"], pin["lat"])
        nx, ny = PIN_NUDGE.get(pin["n"], (0, 0))
        cx, cy = px + nx, py + ny
        if (nx, ny) != (0, 0):
            d.line([(px, py), (cx, cy)], fill=GREY, width=1)
            d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=GREY)
        col = REGION_COLOR[stories[pin["n"]]["region"]]
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=col, outline=(255, 255, 255),
                  width=1)
        txt(d, cx, cy - 5, str(pin["n"]), F_SANSB(8), fill=(255, 255, 255),
            anchor="ma", kind="pin_number")
        if pin["label"]:
            lx, ly = cx + pin["dx"], cy + pin["dy"]
            anchor = "ra" if pin["dx"] < 0 else "la"
            txt(d, lx, ly, pin["label"], F_SANSB(9), fill=INK, anchor=anchor,
                kind="pin_label")


# ---------------- main render ----------------

def render(out_path):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    heroes = DATA["heroes"]
    minis = DATA["minis"]
    also = DATA["also"]
    all_stories = heroes + minis + also
    assert [s["n"] for s in all_stories] == list(range(1, 41)), "story numbers 1..40"
    from collections import Counter
    counts = Counter(s["region"] for s in all_stories)
    assert len(counts) == 10, counts
    assert max(counts.values()) <= 7, counts

    # kicker
    txt(d, MARGIN, YY["kicker"] + 2,
        "EUROPE DECIDES  ·  KOREA HIKES TO 3.25%  ·  AMERICA STOPS TRADING",
        F_MONOB(11), fill=RED, kind="kicker")
    txt(d, W - MARGIN, YY["kicker"] + 2, "No. 40 — 26 NOV 2026", F_MONO(10),
        fill=GREY, anchor="ra", kind="kicker")

    # masthead
    my = YY["masthead"]
    txt(d, MARGIN, my + 8, "THURSDAY", F_SANSB(13), fill=INK, kind="masthead")
    txt(d, MARGIN, my + 26, "26 NOVEMBER 2026", F_SANSB(13), fill=INK, kind="masthead")
    txt(d, MARGIN, my + 46, "PRICE: ONE DAY", F_SANS(10), fill=GREY, kind="masthead")
    txt(d, W // 2, my - 2, "THE WORLD", F_BLACK(58), fill=INK, anchor="ma",
        kind="masthead")
    txt(d, W - MARGIN, my + 8, "40 DATED STORIES", F_SANSB(13), fill=INK,
        anchor="ra", kind="masthead")
    txt(d, W - MARGIN, my + 26, "10 REGIONS", F_SANSB(13), fill=INK, anchor="ra",
        kind="masthead")
    txt(d, W - MARGIN, my + 46, "ALL DATED · ALL SOURCED", F_SANS(10), fill=GREY,
        anchor="ra", kind="masthead")
    hline(d, YY["rule"] + 1, width=2)

    # region strip
    order = sorted(counts, key=lambda r: (-counts[r], r))
    strip = "  ·  ".join(f"{r.upper()} {counts[r]}" for r in order)
    txt(d, MARGIN, YY["region_strip"] + 4, strip, F_MONOB(10), fill=INK,
        kind="region_strip")

    # heroes
    hy = YY["heroes"]
    painters = [hero1_art, hero2_art, hero3_art]
    for i, h in enumerate(heroes):
        x0, cw = col_x(i, 3)
        x0, cw = int(x0), int(cw)
        painters[i](d, x0, hy, cw, 92)
        ty = hy + 92 + 5
        txt(d, x0, ty, f"{h['tag']} — {h['city'].upper()} · {h['status']}",
            F_SANSB(10), fill=RED, kind="hero_tag")
        hl = fit_lines(d, h["headline"], F_SDBOLD(17), cw, 2, f"hero{i+1} headline")
        y2 = draw_lines(d, x0, ty + 13, hl, F_SDBOLD(17), 19, kind="hero_headline")
        dl = fit_lines(d, h["deck"], F_SERIF(12), cw, 3, f"hero{i+1} deck")
        draw_lines(d, x0, y2 + 2, dl, F_SERIF(12), 14, kind="hero_deck")

    # minis (2 rows of 5). Text zone ends at card_top+72; art strip starts
    # at +78: a hard 6px gap, enforced by construction and by verify.py.
    for row, batch in enumerate((minis[:5], minis[5:])):
        myy = YY["minis1"] if row == 0 else YY["minis2"]
        for i, m in enumerate(batch):
            x0, cw = col_x(i, 5)
            x0, cw = int(x0), int(cw)
            txt(d, x0, myy + 4, m["tag"], F_SANSB(9), fill=RED, kind="mini_tag")
            hl = fit_lines(d, m["headline"], F_SERIFB(13), cw, 2,
                           f"mini{m['n']} headline")
            draw_lines(d, x0, myy + 16, hl, F_SERIFB(13), 15, kind="mini_headline")
            dl = fit_lines(d, m["deck"], F_SERIF(11), cw, 2, f"mini{m['n']} deck")
            y2 = draw_lines(d, x0, myy + 46, dl, F_SERIF(11), 13, kind="mini_deck")
            assert y2 <= myy + 72, f"mini{m['n']} deck bottom {y2} > {myy + 72}"
            mini_art(d, m["n"], x0, myy + 80, cw, 14)

    # also-on
    ay = YY["also_header"]
    txt(d, MARGIN, ay + 2, "ALSO ON — THE REST OF THE DAY, IN BRIEF",
        F_SANSB(11), fill=INK, kind="also_header")
    txt(d, W - MARGIN, ay + 2, "WED = 25 NOV · THU = TODAY · FRI = TOMORROW",
        F_SANS(10), fill=GREY, anchor="ra", kind="also_header")
    oy = YY["also_on"]
    for col in range(3):
        x0, cw = col_x(col, 3)
        x0, cw = int(x0), int(cw)
        for r in range(9):
            s = also[col * 9 + r]
            by = oy + r * 23
            head = f"{s['n']} · {s['headline']}"
            fit_lines(d, head, F_SERIFB(11), cw, 1, f"also{s['n']} headline")
            txt(d, x0, by, head, F_SERIFB(11), fill=INK, kind="also_headline")
            txt(d, x0 + cw, by, s["day"], F_SANSB(9), fill=RED, anchor="ra",
                kind="also_day")
            fit_lines(d, s["deck"], F_SERIF(10), cw, 1, f"also{s['n']} deck")
            txt(d, x0, by + 12, s["deck"], F_SERIF(10), fill=GREY, kind="also_deck")

    # map row: map left, numbers right
    mry = YY["map_row"]
    map_w = 660
    paint_map(d, MARGIN, mry, map_w, 137)
    nx0 = MARGIN + map_w + GUTTER
    nw = W - MARGIN - nx0
    d.rectangle([nx0, mry, nx0 + nw, mry + 137], outline=INK, width=1)
    txt(d, nx0 + 8, mry + 5, "THE DAY IN NUMBERS", F_SANSB(11), fill=INK,
        kind="numbers_title")
    for i, num in enumerate(DATA["numbers"]):
        ry = mry + 24 + i * 18
        txt(d, nx0 + 8, ry, num["l"], F_SANS(10), fill=GREY, kind="numbers_label")
        txt(d, nx0 + nw - 8, ry - 3, num["v"], F_SERIFB(15), fill=INK,
            anchor="ra", kind="numbers_value")
    txt(d, nx0 + 8, mry + 126, "Sources: BoK · Reuters · Dow Jones · BEA · Fed",
        F_SANS(8), fill=GREY, kind="numbers_foot")

    # timeline
    ty = YY["timeline"]
    d.rectangle([MARGIN, ty, W - MARGIN, ty + 24], fill=(232, 228, 218),
                outline=INK, width=1)
    tl = "   ".join(f"{t}  {label.upper()}" for t, label in DATA["timeline"])
    txt(d, MARGIN + 8, ty + 6, "UTC  " + tl, F_MONOB(10), fill=INK, kind="timeline")

    # ticker
    tky = YY["ticker"]
    d.rectangle([MARGIN, tky, W - MARGIN, tky + 20], fill=INK)
    txt(d, MARGIN + 8, tky + 5, DATA["ticker"], F_MONO(10), fill=(247, 243, 234),
        kind="ticker")

    # date check
    dcy = YY["datecheck"]
    d.rectangle([MARGIN, dcy, W - MARGIN, dcy + 60], outline=INK, width=1)
    txt(d, MARGIN + 8, dcy + 4, "DATE CHECK", F_SANSB(10), fill=RED,
        kind="datecheck_title")
    for i, line in enumerate(DATA["datecheck"]):
        fit_lines(d, line, F_SANS(9), INNER - 16, 1, f"datecheck{i}")
        txt(d, MARGIN + 8, dcy + 17 + i * 10, line, F_SANS(9), fill=INK,
            kind="datecheck")

    # footer
    txt(d, W // 2, YY["footer"] + 1,
        "THE WORLD — one day, one page. All stories dated 26 November 2026 unless marked WED / FRI.",
        F_SANS(9), fill=GREY, anchor="ma", kind="footer")

    img.save(out_path, "PNG")
    if os.environ.get("DRAW_LOG") == "1":
        with open(os.path.join(HERE, "boxes.json"), "w", encoding="utf-8") as f:
            json.dump({"text": TEXT_BOXES, "art": ART_BOXES}, f)
    return out_path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "entry.png")
    render(out)
    print("wrote", out)

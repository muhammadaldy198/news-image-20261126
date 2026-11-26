#!/usr/bin/env python3
"""news-image-20261126 v1 — MORNING EDITION. Renders stories.json to entry.png.
Own code, written fresh in this session. JSON -> PIL, explicit slots, one
budget table. No network, no randomness, no time dependence.
"""
import json, sys, hashlib
from PIL import Image, ImageDraw, ImageFont

W = 1024
MARGIN = 12
GUT = 8
FONTDIR = "/usr/share/fonts/truetype/noto/"
PAPER = (247, 243, 234)
INK = (26, 26, 26)
RED = (179, 38, 30)
NAVY = (18, 30, 52)
NAVY2 = (36, 62, 92)
GRAY = (107, 107, 107)
LIGHT = (239, 234, 224)
RULE = (26, 26, 26)

BUDGET = [
    ("kicker", 14), ("masthead", 80), ("deck", 22), ("numbers", 30),
    ("region", 16), ("timeline", 28), ("heroes", 254), ("minis", 210),
    ("alsoon", 140), ("map", 146), ("datecheck", 50), ("ticker", 22),
    ("footer", 12),
]
assert sum(h for _, h in BUDGET) == W, sum(h for _, h in BUDGET)
Y = {}
_y = 0
for _name, _h in BUDGET:
    Y[_name] = _y
    _y += _h

def F(name, size):
    return ImageFont.truetype(FONTDIR + name, size)

F_BLACK = lambda s: F("NotoSerifDisplay-Black.ttf", s)
F_DBOLD = lambda s: F("NotoSerifDisplay-Bold.ttf", s)
F_SBOLD = lambda s: F("NotoSerif-Bold.ttf", s)
F_SERIF = lambda s: F("NotoSerif-Regular.ttf", s)
F_SANSB = lambda s: F("NotoSans-Bold.ttf", s)
F_SANS = lambda s: F("NotoSans-Regular.ttf", s)
F_MONO = lambda s: F("NotoSansMono-Regular.ttf", s)
F_MONOB = lambda s: F("NotoSansMono-Bold.ttf", s)

BOXES = []  # (x0, y0, x1, y1, what) for overlap verification

def logbox(x0, y0, x1, y1, what):
    BOXES.append([int(x0), int(y0), int(x1), int(y1), what])

def text(d, x, y, s, font, fill=INK, anchor_left=True):
    d.text((x, y), s, font=font, fill=fill)
    b = d.textbbox((x, y), s, font=font)
    logbox(b[0], b[1], b[2], b[3], s[:40])
    return b

def text_c(d, cx, y, s, font, fill=INK):
    w = d.textlength(s, font=font)
    return text(d, cx - w / 2, y, s, font, fill)

def wrap(font, s, width, d):
    words = s.split(" ")
    lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if d.textlength(trial, font=font) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines

def fit(font, s, width, max_lines, d, what=""):
    lines = wrap(font, s, width, d)
    assert len(lines) <= max_lines, f"OVERFLOW {what}: {len(lines)} > {max_lines}: {s!r}"
    return lines

def para(d, x, y, lines, font, fill=INK, lh=None):
    if lh is None:
        lh = font.size + 3
    for ln in lines:
        text(d, x, y, ln, font, fill)
        y += lh
    return y

def hline(d, x0, x1, y, fill=RULE, width=1):
    d.line([(x0, y), (x1, y)], fill=fill, width=width)

def vline(d, x, y0, y1, fill=RULE, width=1):
    d.line([(x, y0), (x, y1)], fill=fill, width=width)

def region_counts(data):
    regions = {"EUROPE": 0, "ASIA": 0, "N. AMERICA": 0, "MIDDLE EAST": 0,
               "OCEANIA": 0, "AFRICA": 0}
    place_region = {
        "BRUSSELS": "EUROPE", "BOLOGNA": "EUROPE", "MADRID": "EUROPE",
        "SAMARA": "EUROPE", "MOSCOW": "EUROPE",
        "SEOUL": "ASIA", "SEOUL · TOKYO": "ASIA", "YAMANASHI": "ASIA",
        "JIUQUAN": "ASIA",
        "NEW YORK": "N. AMERICA", "WASHINGTON": "N. AMERICA",
        "BOSTON": "N. AMERICA", "DENVER": "N. AMERICA",
        "HORMUZ": "MIDDLE EAST", "GAZA CITY": "MIDDLE EAST",
        "CANBERRA": "OCEANIA",
    }
    for s in data["heroes"] + data["minis"] + data["also_on"]:
        regions[place_region[s["place"]]] += 1
    return regions

def main():
    data = json.load(open("stories.json"))
    meta = data["meta"]
    img = Image.new("RGB", (W, W), PAPER)
    d = ImageDraw.Draw(img)
    x0, x1 = MARGIN, W - MARGIN

    # ---- kicker ----
    y = Y["kicker"]
    text_c(d, W / 2, y + 1, "T H E   W O R L D   I N   O N E   D A Y", F_SANSB(10), GRAY)

    # ---- masthead ----
    y = Y["masthead"]
    hline(d, x0, x1, y + 2, width=2)
    # left ear
    d.rectangle([x0, y + 8, x0 + 128, y + 68], outline=RULE, width=1)
    text(d, x0 + 6, y + 12, "THURSDAY", F_SANSB(11))
    text(d, x0 + 6, y + 26, "26 NOV 2026", F_SANSB(13))
    text(d, x0 + 6, y + 44, "MORNING EDITION", F_SANS(10), GRAY)
    # right ear
    d.rectangle([x1 - 128, y + 8, x1, y + 68], outline=RULE, width=1)
    text(d, x1 - 122, y + 12, "22 DATED STORIES", F_SANSB(11))
    text(d, x1 - 122, y + 26, "6 REGIONS", F_SANSB(13))
    text(d, x1 - 122, y + 44, "ALL FROM THU 26 NOV", F_SANS(10), GRAY)
    # title
    text_c(d, W / 2, y + 0, "THE WORLD", F_BLACK(54))
    text_c(d, W / 2, y + 58, "Thursday, 26 November 2026", F_SBOLD(13))
    hline(d, x0, x1, y + 77, width=2)

    # ---- deck bar ----
    y = Y["deck"]
    d.rectangle([x0, y + 2, x1, y + 20], fill=RED)
    text_c(d, W / 2, y + 5, meta["deck"], F_SANSB(13), (255, 255, 255))

    # ---- numbers strip ----
    y = Y["numbers"]
    cells = data["numbers"]
    cw = (x1 - x0) / len(cells)
    for i, c in enumerate(cells):
        cx = x0 + i * cw
        text_c(d, cx + cw / 2, y + 1, c["value"], F_SBOLD(16))
        text_c(d, cx + cw / 2, y + 21, c["label"], F_SANS(8), GRAY)
        if i:
            vline(d, cx, y + 3, y + 27, fill=(200, 195, 185))
    hline(d, x0, x1, y + 29, fill=(200, 195, 185))

    # ---- region strip ----
    y = Y["region"]
    rc = region_counts(data)
    parts = "  ·  ".join(f"{k} {v}" for k, v in rc.items())
    strip = parts + "   —   No verified Africa story today" if rc["AFRICA"] == 0 else parts
    strip += "   |   HOW SURE: CONFIRMED 2+ outlets · REPORTED single wire · EXPECTED due, not taken"
    lines = fit(F_SANSB(10), strip, x1 - x0, 1, d, "region strip")
    text(d, x0, y + 3, lines[0], F_SANSB(10))

    # ---- timeline ----
    y = Y["timeline"]
    tl = data["timeline"]
    tw = (x1 - x0) / len(tl)
    for i, t in enumerate(tl):
        cx = x0 + i * tw
        d.rectangle([cx + 2, y + 5, cx + 9, y + 12], fill=RED)
        text(d, cx + 13, y + 2, t["utc"], F_MONOB(10), RED)
        lines = fit(F_SANS(9), t["text"], tw - 6, 1, d, "timeline " + t["utc"])
        text(d, cx + 2, y + 15, lines[0], F_SANS(9), GRAY)
        if i:
            vline(d, cx - 2, y + 2, y + 26, fill=(200, 195, 185))
    hline(d, x0, x1, y + 27, fill=(200, 195, 185))

    draw_heroes(d, data, x0, x1)
    draw_minis(d, data, x0, x1)
    draw_alsoon(d, data, x0, x1)
    draw_map(d, data, x0, x1)
    draw_datecheck(d, data, x0, x1)
    draw_ticker_footer(d, data, x0, x1)

    img.save("entry.png", format="PNG")
    json.dump(BOXES, open("boxes.json", "w"))
    print("wrote entry.png", img.size)

# ---------------- heroes ----------------

def banner(d, x, y, w, s, size=14):
    d.rectangle([x, y, x + w, y + 22], fill=RED)
    text_c(d, x + w / 2, y + 4, s, F_SANSB(size), (255, 255, 255))

def art_council(d, x, y, w, h):
    for i in range(5):
        t0 = i / 5
        c = tuple(int(NAVY[k] + (NAVY2[k] - NAVY[k]) * t0) for k in range(3))
        d.rectangle([x, y + i * h / 5, x + w, y + (i + 1) * h / 5], fill=c)
    # gold stars arc
    import math
    for k in range(12):
        ang = math.pi * (0.15 + 0.7 * k / 11)
        sx = x + w - 52 + 34 * math.cos(ang)
        sy = y + 26 + 20 * math.sin(ang)
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(242, 193, 78))
    # Europa building mass
    bx, by, bw, bh = x + 58, y + 42, 212, 82
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=10, fill=(52, 78, 110))
    d.rectangle([bx, by + 18, bx + bw, by + 22], fill=(70, 98, 132))
    for r in range(3):
        for c in range(9):
            wx = bx + 12 + c * 22
            wy = by + 32 + r * 16
            d.rectangle([wx, wy, wx + 12, wy + 9], fill=(242, 193, 78))
    # flag poles row
    flag_cols = [(179, 38, 30), (255, 255, 255), (36, 62, 92), (242, 193, 78),
                 (179, 38, 30), (255, 255, 255), (36, 62, 92), (242, 193, 78), (179, 38, 30)]
    for i, fc in enumerate(flag_cols):
        fx = x + 24 + i * 32
        d.line([(fx, y + h - 34), (fx, y + h - 52)], fill=(200, 200, 200), width=1)
        d.rectangle([fx, y + h - 52, fx + 18, y + h - 42], fill=fc)
    # crowd silhouettes
    for i in range(7):
        cx = x + 30 + i * 42
        d.ellipse([cx - 7, y + h - 30, cx + 7, y + h - 16], fill=(12, 20, 36))
        d.rectangle([cx - 12, y + h - 16, cx + 12, y + h - 6], fill=(12, 20, 36))
    banner(d, x, y + h - 22, w, "€70BN ON THE TABLE")

def art_bok(d, x, y, w, h):
    for i in range(4):
        c = (214 - i * 4, 222 - i * 4, 230 - i * 4)
        d.rectangle([x, y + i * h / 4, x + w, y + (i + 1) * h / 4], fill=c)
    # chip
    cx, cy, cs = x + 26, y + 28, 74
    d.rectangle([cx - 8, cy - 8, cx + cs + 8, cy + cs + 8], fill=(40, 52, 72))
    for k in range(6):
        d.rectangle([cx - 14, cy + 6 + k * 11, cx - 8, cy + 10 + k * 11], fill=(242, 193, 78))
        d.rectangle([cx + cs + 8, cy + 6 + k * 11, cx + cs + 14, cy + 10 + k * 11], fill=(242, 193, 78))
    d.rectangle([cx + 22, cy + 22, cx + cs - 22, cy + cs - 22], outline=(242, 193, 78), width=2)
    d.line([(cx + 10, cy + cs / 2), (cx + cs - 10, cy + cs / 2)], fill=(120, 130, 140), width=1)
    d.line([(cx + 10, cy + 14), (cx + cs - 10, cy + 14)], fill=(90, 105, 125), width=1)
    d.line([(cx + 10, cy + cs - 14), (cx + cs - 10, cy + cs - 14)], fill=(90, 105, 125), width=1)
    # rising chart
    pts = [(x + 130, y + 118), (x + 165, y + 108), (x + 195, y + 112),
           (x + 225, y + 88), (x + 258, y + 66), (x + 295, y + 34)]
    d.line(pts, fill=RED, width=4)
    for p in pts:
        d.ellipse([p[0] - 4, p[1] - 4, p[0] + 4, p[1] + 4], fill=RED)
    for i, bh in enumerate([18, 26, 22, 34, 44]):
        bx = x + 140 + i * 30
        d.rectangle([bx, y + 128 - bh, bx + 18, y + 128], fill=(120, 130, 140))
    # factory silhouette
    d.rectangle([x + 252, y + 96, x + 312, y + 128], fill=(90, 100, 112))
    d.rectangle([x + 262, y + 78, x + 270, y + 96], fill=(90, 100, 112))
    d.rectangle([x + 282, y + 84, x + 290, y + 96], fill=(90, 100, 112))
    for i in range(3):
        d.ellipse([x + 258 + i * 10, y + 66 - i * 4, x + 264 + i * 10, y + 72 - i * 4],
                  fill=(200, 205, 210))
    banner(d, x, y + h - 22, w, "3.25% EXPECTED")

def art_thanksgiving(d, x, y, w, h):
    for i in range(5):
        t0 = i / 5
        c = tuple(int(NAVY[k] + (NAVY2[k] - NAVY[k]) * t0) for k in range(3))
        d.rectangle([x, y + i * h / 5, x + w, y + (i + 1) * h / 5], fill=c)
    # parade balloons
    for (bx, by, br, bc) in [(x + 60, y + 34, 20, (179, 38, 30)),
                             (x + 268, y + 28, 24, (242, 193, 78)),
                             (x + 170, y + 20, 15, (70, 130, 180))]:
        d.ellipse([bx - br, by - br, bx + br, by + br], fill=bc)
        d.line([(bx, by + br), (bx, by + br + 22)], fill=(220, 220, 220), width=1)
    # confetti
    for (px, py, pc) in [(x + 40, y + 70, (242, 193, 78)), (x + 300, y + 70, (255, 255, 255)),
                         (x + 120, y + 60, (179, 38, 30)), (x + 230, y + 80, (242, 193, 78)),
                         (x + 90, y + 90, (255, 255, 255)), (x + 290, y + 95, (179, 38, 30))]:
        d.rectangle([px, py, px + 4, py + 4], fill=pc)
    # glowing table + turkey
    d.ellipse([x + 104, y + 96, x + 224, y + 132], fill=(120, 74, 40))
    d.ellipse([x + 128, y + 88, x + 200, y + 118], fill=(160, 100, 52))
    d.ellipse([x + 150, y + 80, x + 178, y + 100], fill=(190, 130, 70))
    d.line([(x + 132, y + 92), (x + 118, y + 78)], fill=(220, 180, 120), width=3)
    d.line([(x + 196, y + 92), (x + 210, y + 78)], fill=(220, 180, 120), width=3)
    # candles
    for cx in (x + 112, x + 216):
        d.rectangle([cx, y + 96, cx + 4, y + 112], fill=(240, 230, 200))
        d.ellipse([cx - 1, y + 90, cx + 5, y + 97], fill=(242, 193, 78))
    # exchange floor band
    d.rectangle([x, y + h - 34, x + w, y + h - 22], fill=(12, 20, 36))
    for i, cc in enumerate([(40, 160, 80), (179, 38, 30), (40, 160, 80), (179, 38, 30)]):
        d.rectangle([x + 20 + i * 78, y + h - 30, x + 44 + i * 78, y + h - 26], fill=cc)
    banner(d, x, y + h - 22, w, "MARKETS DARK")

ART = {"council": art_council, "bok": art_bok, "thanksgiving": art_thanksgiving}

def draw_heroes(d, data, x0, x1):
    y = Y["heroes"]
    cw = (x1 - x0 - 2 * GUT) / 3
    for i, s in enumerate(data["heroes"]):
        x = x0 + i * (cw + GUT)
        ART[s["art"]](d, x, y, cw, 150)
        tag = f"{s['n']} · {s['place']} · {s['tag']} · {s['ver']}"
        text(d, x, y + 156, tag, F_SANSB(11), RED)
        hl = fit(F_DBOLD(19), s["headline"], cw, 2, d, "hero headline " + str(s["n"]))
        para(d, x, y + 172, hl, F_DBOLD(19), INK, 21)
        dk = fit(F_SERIF(12), s["deck"], cw, 2, d, "hero deck " + str(s["n"]))
        para(d, x, y + 216, dk, F_SERIF(12), INK, 14)
        text(d, x, y + 244, "Source: " + s["source"], F_SANS(9), GRAY)
        if i:
            vline(d, x - GUT / 2 - 1, y, y + 252, fill=(200, 195, 185))

# ---------------- minis ----------------

def mini_art(d, key, x, y, w, h, banner_text):
    if key == "parade":
        d.rectangle([x, y, x + w, y + h], fill=(168, 200, 226))
        for (bx, by, br, bc) in [(x + 24, y + 26, 13, (179, 38, 30)),
                                 (x + 52, y + 18, 16, (242, 193, 78)),
                                 (x + 80, y + 30, 11, (70, 130, 180))]:
            d.ellipse([bx - br, by - br, bx + br, by + br], fill=bc)
            d.line([(bx, by + br), (bx, by + br + 14)], fill=(255, 255, 255), width=1)
        d.rectangle([x, y + h - 18, x + w, y + h], fill=(90, 90, 90))
        for i in range(6):
            d.ellipse([x + 8 + i * 15, y + h - 14, x + 12 + i * 15, y + h - 10], fill=(255, 255, 255))
    elif key == "davis":
        d.rectangle([x, y, x + w, y + h], fill=(46, 125, 70))
        d.rectangle([x + 6, y + 6, x + w - 6, y + h - 6], outline=(255, 255, 255), width=2)
        d.line([(x + w / 2, y + 6), (x + w / 2, y + h - 6)], fill=(255, 255, 255), width=2)
        for yy in range(y + 8, y + h - 6, 6):
            d.point((x + w / 2, yy), fill=(255, 255, 255))
        d.ellipse([x + 66, y + 30, x + 80, y + 44], fill=(220, 230, 60))
    elif key == "asia":
        d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
        for i, bh in enumerate([52, 40, 30, 20]):
            d.rectangle([x + 12 + i * 20, y + h - 20 - bh, x + 26 + i * 20, y + h - 20], fill=RED)
        d.polygon([(x + 78, y + 14), (x + 94, y + 14), (x + 86, y + 34)], fill=RED)
        d.rectangle([x + 82, y + 34, x + 90, y + 62], fill=RED)
    elif key == "tamura":
        d.rectangle([x, y, x + w, y + h], fill=(226, 232, 238))
        d.rectangle([x + 34, y + 62, x + 65, y + h - 14], fill=(26, 26, 26))
        d.line([(x + 50, y + 62), (x + 50, y + 46)], fill=(26, 26, 26), width=2)
        d.ellipse([x + 46, y + 42, x + 54, y + 50], fill=(26, 26, 26))
        d.line([(x + 70, y + 40), (x + 88, y + 22)], fill=(40, 160, 80), width=4)
        d.polygon([(x + 88, y + 22), (x + 78, y + 24), (x + 86, y + 32)], fill=(40, 160, 80))
    elif key == "spain":
        d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
        d.rectangle([x, y, x + w, y + 12], fill=(179, 38, 30))
        d.rectangle([x, y + 12, x + w, y + 24], fill=(242, 193, 78))
        d.rectangle([x, y + 24, x + w, y + 30], fill=(179, 38, 30))
        d.rectangle([x + 28, y + 48, x + 71, y + h - 12], fill=(240, 240, 240), outline=(26, 26, 26), width=2)
        d.rectangle([x + 40, y + 48, x + 59, y + 54], fill=(26, 26, 26))
        d.rectangle([x + 44, y + 34, x + 55, y + 48], fill=(255, 255, 255), outline=(26, 26, 26), width=1)
    elif key == "friday":
        d.rectangle([x, y, x + w, y + h], fill=(240, 234, 224))
        d.rectangle([x + 28, y + 34, x + 72, y + h - 10], fill=RED)
        d.arc([x + 38, y + 18, x + 62, y + 44], 180, 360, fill=(26, 26, 26), width=3)
        d.ellipse([x + 76, y + 16, x + 94, y + 34], outline=(26, 26, 26), width=2)
        d.line([(x + 85, y + 25), (x + 85, y + 18)], fill=(26, 26, 26), width=2)
        d.line([(x + 85, y + 25), (x + 91, y + 28)], fill=(26, 26, 26), width=2)
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(26, 26, 26))
    bl = fit(F_SANSB(9), banner_text, w - 4, 1, d, "mini banner " + banner_text)
    text_c(d, x + w / 2, y + h - 13, bl[0], F_SANSB(9), (255, 255, 255))

def draw_minis(d, data, x0, x1):
    y = Y["minis"]
    cw = (x1 - x0 - 2 * GUT) / 3
    for i, s in enumerate(data["minis"]):
        col, row = i % 3, i // 3
        x = x0 + col * (cw + GUT)
        yy = y + row * 105
        mini_art(d, s["art"], x, yy + 3, 99, 99, s["banner"])
        tx = x + 107
        tw = cw - 107
        tag = f"{s['n']} · {s['place']} · {s['tag']} · {s['ver']}"
        text(d, tx, yy + 4, tag, F_SANSB(10), RED)
        hl = fit(F_DBOLD(13), s["headline"], tw, 2, d, "mini headline " + str(s["n"]))
        para(d, tx, yy + 19, hl, F_DBOLD(13), INK, 16)
        dk = fit(F_SERIF(11), s["deck"], tw, 3, d, "mini deck " + str(s["n"]))
        para(d, tx, yy + 52, dk, F_SERIF(11), INK, 13)
        text(d, tx, yy + 92, "Source: " + s["source"], F_SANS(9), GRAY)
        if col:
            vline(d, x - GUT / 2 - 1, yy, yy + 102, fill=(200, 195, 185))
    hline(d, x0, x1, y + 208, fill=(200, 195, 185))

# ---------------- also on ----------------

def draw_alsoon(d, data, x0, x1):
    y = Y["alsoon"]
    text(d, x0, y + 2, "ALSO ON — WEDNESDAY 25 NOVEMBER", F_SANSB(12))
    text(d, x1 - 150, y + 2, "13 MORE DATED BRIEFS", F_SANS(10), GRAY)
    hline(d, x0, x1, y + 17, width=1)
    items = data["also_on"]
    colw = (x1 - x0 - GUT) / 2
    for r in range(7):
        yy = y + 20 + r * 17
        for c in range(2):
            idx = r + c * 7
            if idx >= len(items):
                continue
            s = items[idx]
            xx = x0 + c * (colw + GUT)
            segs = [(f"{s['n']} · ", F_SANSB(11), RED),
                    (f"{s['place']} — ", F_SANSB(11), INK),
                    (s["headline"], F_SANS(11), INK),
                    (": " + s["deck"], F_SANS(11), GRAY)]
            total = sum(d.textlength(t, font=f) for t, f, _ in segs)
            assert total + 3 <= colw, f"ALSO-ON OVERFLOW #{s['n']}: {total:.0f} > {colw:.0f}"
            cx = xx
            for t, f, col in segs:
                text(d, cx, yy, t, f, col)
                cx += d.textlength(t, font=f) + 1

# ---------------- map ----------------

CONTINENTS = {
    "N America": [(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-60, 60),
                  (-55, 47), (-70, 42), (-75, 35), (-80, 26), (-90, 21), (-97, 16),
                  (-105, 20), (-115, 28), (-125, 40), (-125, 49), (-140, 60), (-165, 60)],
    "S America": [(-80, 10), (-60, 8), (-50, 0), (-35, -8), (-40, -20), (-48, -28),
                  (-58, -35), (-65, -41), (-70, -52), (-73, -40), (-72, -20), (-80, -5)],
    "Europe": [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59),
               (18, 56), (21, 55), (24, 60), (28, 62), (30, 70), (25, 71), (18, 69),
               (12, 65), (5, 58), (-5, 50), (-10, 43)],
    "Africa": [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
               (43, 12), (51, 11), (48, 0), (40, -10), (35, -18), (28, -26), (20, -35),
               (15, -27), (12, -18), (9, -1), (8, 4), (-8, 5), (-15, 12)],
    "Asia": [(30, 70), (40, 68), (55, 70), (70, 72), (90, 75), (110, 76), (130, 72),
             (160, 70), (178, 66), (170, 60), (162, 55), (158, 50), (142, 45), (140, 38),
             (130, 33), (127, 35), (122, 30), (120, 22), (110, 20), (105, 8), (100, 8),
             (95, 15), (90, 22), (80, 8), (77, 8), (72, 20), (66, 25), (60, 25),
             (55, 26), (50, 30), (48, 30), (44, 29), (40, 36), (35, 36), (30, 36)],
    "Australia": [(113, -22), (114, -30), (115, -35), (124, -33), (130, -32), (137, -35),
                  (140, -38), (147, -39), (150, -37), (153, -32), (153, -27), (146, -19),
                  (142, -11), (137, -12), (132, -12), (126, -14), (122, -17), (114, -22)],
    "Greenland": [(-45, 60), (-30, 68), (-20, 70), (-25, 76), (-40, 80), (-55, 76), (-58, 70), (-52, 64)],
    "UK": [(-5, 50), (-3, 53), (-5, 56), (-2, 58), (-1, 57), (0, 53)],
    "Japan": [(130, 31), (133, 34), (137, 35), (140, 38), (141, 42), (143, 44), (140, 40), (136, 35), (132, 33)],
}

def draw_map(d, data, x0, x1):
    y = Y["map"]
    text(d, x0, y + 2, "WHERE IT HAPPENED · SCENES 1–22", F_SANSB(12))
    my0, my1 = y + 18, y + 150
    d.rectangle([x0, my0, x1, my1], fill=(232, 237, 242), outline=RULE, width=1)

    def proj(lon, lat):
        return (x0 + (lon + 180) / 360 * (x1 - x0),
                my0 + (85 - lat) / 145 * (my1 - my0))
    for pts in CONTINENTS.values():
        d.polygon([proj(lo, la) for lo, la in pts], fill=(216, 209, 196),
                  outline=(160, 150, 135))
    # Indonesia dots
    for lo, la in [(95, 0), (102, -2), (110, -7), (113, -1), (119, -3), (125, -1), (131, -3)]:
        px, py = proj(lo, la)
        d.ellipse([px - 2, py - 1, px + 2, py + 1], fill=(216, 209, 196),
                  outline=(160, 150, 135))
    for p in data["map_pins"]:
        px, py = proj(p["lon"], p["lat"])
        px += p.get("px", 0)
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=RED, outline=(255, 255, 255), width=1)
        text_c(d, px, py - 6, str(p["n"]), F_SANSB(9), (255, 255, 255))
        lx, ly = px + p["dx"], py + p["dy"]
        text(d, lx, ly, p["label"], F_SANSB(10), INK)

# ---------------- date check / ticker / footer ----------------

def draw_datecheck(d, data, x0, x1):
    y = Y["datecheck"]
    d.rectangle([x0, y + 2, x0 + 4, y + 48], fill=RED)
    text(d, x0 + 10, y + 3, data["date_check"]["title"], F_SANSB(11), RED)
    body = fit(F_SERIF(10), data["date_check"]["body"], x1 - x0 - 10, 3, d, "date check")
    para(d, x0 + 10, y + 17, body, F_SERIF(10), INK, 11)

def draw_ticker_footer(d, data, x0, x1):
    y = Y["ticker"]
    d.rectangle([x0, y + 2, x1, y + 20], fill=(26, 26, 26))
    lines = fit(F_MONO(10), data["ticker"], x1 - x0 - 8, 1, d, "ticker")
    text_c(d, W / 2, y + 5, lines[0], F_MONO(10), (255, 255, 255))
    y = Y["footer"]
    text(d, x0, y + 1, data["meta"]["sources_line"], F_SANS(9), GRAY)

if __name__ == "__main__":
    main()

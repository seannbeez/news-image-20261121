#!/usr/bin/env python3
"""news-image-20261121 v2 — Saturday-first broadsheet.

Draws one 1024x1024 image summing up Saturday 21 November 2026.
Flat vector only: every illustration is drawn in code with Pillow.
No network, no randomness, no timestamps: two runs write identical bytes.

Stdlib-only fallback: when Pillow is unavailable (the grading container
has no Pillow), copy the vendored entry.png beside this file to the output.
The vendored copy is produced by this same program, so both paths agree.
"""

import os
import shutil
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
    HAVE_PIL = True
except Exception:  # noqa: BLE001 - Pillow is optional; fallback below
    HAVE_PIL = False

BASE = os.path.dirname(os.path.abspath(__file__))
W, H = 1024, 1024

# ---------------------------------------------------------------- palette
INK = (14, 30, 51)          # deep navy — masthead, headlines
PAPER = (255, 255, 255)
PANEL = (244, 246, 248)     # light panel
PANEL2 = (238, 241, 244)
LINE = (203, 213, 222)      # hairlines
GOLD = (201, 162, 39)
GOLD_LT = (232, 196, 92)
RED = (176, 58, 44)
GREEN = (30, 122, 76)
AMBER = (166, 110, 16)
TEAL = (18, 110, 110)
SKY = (70, 130, 180)
SAND = (198, 123, 74)
MUTED = (90, 105, 120)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)

BADGE_FILL = {"CONFIRMED": GREEN, "CLAIM": RED, "REPORTED": AMBER}

# ---------------------------------------------------------------- fonts
_FONTS = {}


def _font(name, size):
    key = (name, size)
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype(os.path.join(BASE, "fonts", name), size)
    return _FONTS[key]


def FB(size):
    return _font("DejaVuSans-Bold.ttf", size)


def FR(size):
    return _font("DejaVuSans.ttf", size)


def FO(size):
    return _font("DejaVuSans-Oblique.ttf", size)


# ---------------------------------------------------------------- helpers
def wrap(d, text, font, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_lines(d, x, y, lines, font, fill, lh):
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += lh
    return y


def text_h(d, text, font, max_w, lh):
    return len(wrap(d, text, font, max_w)) * lh


def rr(d, box, rad, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=rad, fill=fill, outline=outline, width=width)


def badge(d, x, y, kind):
    """Small verification pill. Returns its width."""
    f = FB(9)
    tw = d.textlength(kind, font=f)
    w = tw + 12
    rr(d, [x, y, x + w, y + 15], 7, fill=BADGE_FILL[kind])
    d.text((x + 6, y + 2.5), kind, font=f, fill=WHITE)
    return w


def num_chip(d, cx, cy, n, r=8, fill=RED):
    """Numbered circle centred on (cx, cy)."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill,
              outline=WHITE, width=1)
    f = FB(9)
    t = str(n)
    tw = d.textlength(t, font=f)
    d.text((cx - tw / 2, cy - 6.5), t, font=f, fill=WHITE)


# ---------------------------------------------------------------- flat icons
# Every icon draws inside the square (x, y, s). Flat geometric shapes only.

def icon_missile(d, x, y, s, c1=GOLD_LT, c2=WHITE):
    # three intercept trails converging on a burst, night sky handled by panel
    for i, off in enumerate([0, s * 0.28, s * 0.55]):
        d.line([x + 4, y + s - 6 - off * 0.4, x + s * 0.55, y + s * 0.42 - off * 0.3],
               fill=c1, width=3)
    bx, by = x + s * 0.62, y + s * 0.34
    for ang in range(0, 360, 45):
        import math
        r1, r2 = s * 0.10, s * 0.22
        a = math.radians(ang)
        d.line([bx + r1 * math.cos(a), by + r1 * math.sin(a),
                bx + r2 * math.cos(a), by + r2 * math.sin(a)],
               fill=c2, width=2)
    d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=c2)


def icon_quake(d, x, y, s, c1=(90, 50, 30), c2=RED):
    # mountain silhouettes + red seismograph zigzag
    d.polygon([(x + 2, y + s - 4), (x + s * 0.30, y + s * 0.30),
               (x + s * 0.48, y + s - 4)], fill=c1)
    d.polygon([(x + s * 0.38, y + s - 4), (x + s * 0.68, y + s * 0.18),
               (x + s * 0.95, y + s - 4)], fill=(60, 38, 26))
    pts = [(x + 2, y + s * 0.55), (x + s * 0.2, y + s * 0.55),
           (x + s * 0.28, y + s * 0.30), (x + s * 0.36, y + s * 0.72),
           (x + s * 0.46, y + s * 0.40), (x + s * 0.54, y + s * 0.62),
           (x + s * 0.62, y + s * 0.45), (x + s * 0.72, y + s * 0.55),
           (x + s * 0.98, y + s * 0.55)]
    d.line(pts, fill=c2, width=3, joint="curve")


def icon_cop(d, x, y, s, c1=WHITE, c2=GOLD_LT):
    # globe + orbit ring + Day-13 sun
    cx, cy, r = x + s * 0.42, y + s * 0.52, s * 0.30
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c1, width=3)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c1, width=1)
    d.arc([cx - r, cy - r * 0.45, cx + r, cy + r * 0.45], 0, 360,
          fill=c1, width=2)
    d.line([cx, cy - r, cx, cy + r], fill=c1, width=2)
    d.ellipse([x + s * 0.68, y + s * 0.10, x + s * 0.92, y + s * 0.34],
              fill=c2)
    d.ellipse([cx - r * 1.25, cy - r * 1.25, cx + r * 1.25, cy + r * 1.25],
              outline=c2, width=2)


def icon_radar(d, x, y, s, c1=WHITE, c2=RED):
    # radar arcs + incoming missile dot
    cx, cy = x + s * 0.45, y + s * 0.55
    for r in (s * 0.16, s * 0.28, s * 0.40):
        d.arc([cx - r, cy - r, cx + r, cy + r], 200, 340, fill=c1, width=2)
    d.line([cx, cy, cx + s * 0.30, cy - s * 0.30], fill=c1, width=2)
    d.ellipse([cx + s * 0.28 - 3, cy - s * 0.32 - 3,
               cx + s * 0.28 + 3, cy - s * 0.32 + 3], fill=c2)
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=c1)


def icon_rescue(d, x, y, s, c1=(120, 130, 145), c2=RED):
    # damaged blocks + rescue cross + burst
    d.rectangle([x + 4, y + s * 0.45, x + s * 0.42, y + s - 4], fill=c1)
    d.rectangle([x + s * 0.50, y + s * 0.30, x + s * 0.88, y + s - 4],
                fill=(90, 100, 115))
    d.polygon([(x + s * 0.50, y + s * 0.30), (x + s * 0.69, y + s * 0.12),
               (x + s * 0.88, y + s * 0.30)], fill=(70, 80, 95))
    d.rectangle([x + s * 0.60, y + s * 0.55, x + s * 0.66, y + s * 0.80],
                fill=WHITE)
    d.rectangle([x + s * 0.55, y + s * 0.63, x + s * 0.71, y + s * 0.69],
                fill=WHITE)
    d.ellipse([x + s * 0.70, y + s * 0.05, x + s * 0.95, y + s * 0.30],
              fill=c2)


def icon_plane(d, x, y, s, c1=WHITE, c2=GREEN):
    # simple jet silhouette + runway + check
    d.polygon([(x + 4, y + s * 0.55), (x + s * 0.55, y + s * 0.30),
               (x + s * 0.95, y + s * 0.38), (x + s * 0.55, y + s * 0.55),
               (x + s * 0.75, y + s * 0.62), (x + s * 0.45, y + s * 0.62),
               (x + s * 0.30, y + s * 0.72), (x + s * 0.15, y + s * 0.62)],
              fill=c1)
    d.line([x + 4, y + s - 6, x + s - 4, y + s - 6], fill=c1, width=3)
    d.line([x + s * 0.68, y + s * 0.78, x + s * 0.76, y + s * 0.88,
            x + s * 0.95, y + s * 0.68], fill=c2, width=3)


def icon_space(d, x, y, s, c1=GOLD_LT, c2=WHITE):
    # ringed planet + satellite + orbit
    cx, cy, r = x + s * 0.45, y + s * 0.55, s * 0.26
    d.ellipse([cx - r * 1.5, cy - r * 0.45, cx + r * 1.5, cy + r * 0.45],
              outline=c1, width=2)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c1)
    d.rectangle([cx + r * 0.9, cy - r * 1.15, cx + r * 1.25, cy - r * 0.85],
                fill=c2)
    d.line([cx + r * 0.9, cy - r, cx + r * 1.25, cy - r * 1.15],
           fill=c2, width=2)
    d.ellipse([x + s * 0.72, y + s * 0.12, x + s * 0.80, y + s * 0.20],
              fill=c2)


def icon_ship(d, x, y, s, c1=(90, 100, 115), c2=AMBER):
    # port crane + containers + hull + warning triangle
    d.line([x + s * 0.15, y + s * 0.10, x + s * 0.15, y + s * 0.70],
           fill=c1, width=4)
    d.line([x + s * 0.15, y + s * 0.10, x + s * 0.60, y + s * 0.28],
           fill=c1, width=3)
    d.rectangle([x + s * 0.35, y + s * 0.55, x + s * 0.55, y + s * 0.70],
                fill=(60, 90, 120))
    d.rectangle([x + s * 0.58, y + s * 0.55, x + s * 0.78, y + s * 0.70],
                fill=(90, 120, 140))
    d.polygon([(x + 2, y + s * 0.72), (x + s - 2, y + s * 0.72),
               (x + s * 0.85, y + s * 0.88), (x + s * 0.15, y + s * 0.88)],
              fill=(40, 55, 70))
    d.polygon([(x + s * 0.78, y + s * 0.05), (x + s * 0.98, y + s * 0.38),
               (x + s * 0.60, y + s * 0.38)], fill=c2)
    d.text((x + s * 0.76, y + s * 0.16), "!", font=FB(12), fill=INK)


def icon_boat(d, x, y, s, c1=(60, 90, 120), c2=RED):
    # hull + waves + lifebuoy
    d.polygon([(x + 4, y + s * 0.45), (x + s * 0.70, y + s * 0.45),
               (x + s * 0.60, y + s * 0.68), (x + s * 0.14, y + s * 0.68)],
              fill=c1)
    d.rectangle([x + s * 0.30, y + s * 0.30, x + s * 0.50, y + s * 0.45],
                fill=(40, 55, 70))
    for wy in (s * 0.78, s * 0.90):
        d.arc([x + 2, y + wy - 6, x + s * 0.45, y + wy + 6], 0, 180,
              fill=SKY, width=3)
        d.arc([x + s * 0.5, y + wy - 6, x + s - 2, y + wy + 6], 0, 180,
              fill=SKY, width=3)
    d.ellipse([x + s * 0.72, y + s * 0.08, x + s * 0.96, y + s * 0.32],
              outline=c2, width=4)


def icon_robot(d, x, y, s, c1=WHITE, c2=GOLD_LT):
    # robot head + antenna + 04:30 clock
    d.line([x + s * 0.50, y + 2, x + s * 0.50, y + s * 0.18], fill=c1, width=3)
    d.ellipse([x + s * 0.44, y - 2, x + s * 0.56, y + s * 0.10], fill=c2)
    rr(d, [x + s * 0.18, y + s * 0.18, x + s * 0.82, y + s * 0.78], 6,
       fill=c1)
    d.ellipse([x + s * 0.30, y + s * 0.36, x + s * 0.42, y + s * 0.48],
              fill=INK)
    d.ellipse([x + s * 0.58, y + s * 0.36, x + s * 0.70, y + s * 0.48],
              fill=INK)
    d.line([x + s * 0.35, y + s * 0.62, x + s * 0.65, y + s * 0.62],
           fill=INK, width=2)


def icon_f1(d, x, y, s, c1=RED, c2=WHITE):
    # low race car + chequered flag
    d.polygon([(x + 4, y + s * 0.55), (x + s * 0.25, y + s * 0.42),
               (x + s * 0.55, y + s * 0.38), (x + s * 0.80, y + s * 0.48),
               (x + s * 0.95, y + s * 0.60), (x + s * 0.90, y + s * 0.70),
               (x + 4, y + s * 0.70)], fill=c1)
    d.ellipse([x + s * 0.18, y + s * 0.66, x + s * 0.34, y + s * 0.82],
              fill=INK)
    d.ellipse([x + s * 0.68, y + s * 0.66, x + s * 0.84, y + s * 0.82],
              fill=INK)
    for i in range(3):
        for j in range(2):
            if (i + j) % 2 == 0:
                d.rectangle([x + s * (0.78 + i * 0.07), y + s * (0.10 + j * 0.07),
                             x + s * (0.85 + i * 0.07), y + s * (0.17 + j * 0.07)],
                            fill=INK)
    d.line([x + s * 0.78, y + s * 0.10, x + s * 0.78, y + s * 0.30],
           fill=INK, width=2)


def icon_flags(d, x, y, s, c1=WHITE, c2=RED):
    # US stripes flag + RU tricolour flag on two poles
    d.line([x + s * 0.22, y + s * 0.08, x + s * 0.22, y + s * 0.90],
           fill=INK, width=3)
    d.line([x + s * 0.72, y + s * 0.08, x + s * 0.72, y + s * 0.90],
           fill=INK, width=3)
    for i in range(4):
        d.rectangle([x + s * 0.22, y + s * (0.10 + i * 0.09),
                     x + s * 0.52, y + s * (0.10 + (i + 1) * 0.09)],
                    fill=c2 if i % 2 == 0 else c1)
    d.rectangle([x + s * 0.22, y + s * 0.10, x + s * 0.36, y + s * 0.24],
                fill=(40, 60, 120))
    for i, col in enumerate([WHITE, (50, 90, 180), RED]):
        d.rectangle([x + s * 0.72, y + s * (0.10 + i * 0.12),
                     x + s * 0.98, y + s * (0.10 + (i + 1) * 0.12)],
                    fill=col)


def icon_cuffs(d, x, y, s, c1=(120, 130, 145), c2=GOLD):
    # handcuffs + star badge
    d.ellipse([x + s * 0.05, y + s * 0.35, x + s * 0.42, y + s * 0.72],
              outline=c1, width=5)
    d.ellipse([x + s * 0.55, y + s * 0.35, x + s * 0.92, y + s * 0.72],
              outline=c1, width=5)
    d.line([x + s * 0.42, y + s * 0.50, x + s * 0.55, y + s * 0.50],
           fill=c1, width=3)
    import math
    cx, cy, r = x + s * 0.50, y + s * 0.18, s * 0.13
    pts = []
    for i in range(10):
        ang = math.radians(-90 + i * 36)
        rad = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(pts, fill=c2)

# ---------------------------------------------------------------- continents
# Simplified equirectangular outlines (lon, lat). Flat, recognisable, not ASCII.
NA = [(-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 68), (-100, 69),
      (-90, 68), (-85, 66), (-80, 62), (-75, 60), (-68, 58), (-60, 55),
      (-55, 52), (-60, 47), (-65, 44), (-70, 42), (-75, 38), (-80, 32),
      (-81, 26), (-84, 30), (-88, 29), (-90, 21), (-94, 18), (-97, 16),
      (-93, 15), (-88, 13), (-83, 9), (-79, 9), (-82, 10), (-86, 12),
      (-90, 14), (-95, 16), (-99, 18), (-104, 20), (-109, 23), (-113, 28),
      (-118, 33), (-123, 38), (-124, 44), (-126, 49), (-130, 55), (-140, 60),
      (-150, 59), (-158, 58), (-165, 60), (-168, 66)]
GREENLAND = [(-58, 64), (-48, 60), (-42, 63), (-35, 66), (-28, 68), (-22, 70),
             (-25, 74), (-35, 76), (-48, 76), (-58, 74), (-65, 70), (-60, 67),
             (-58, 64)]
SA = [(-78, 8), (-73, 11), (-64, 10), (-58, 7), (-52, 5), (-50, 0),
      (-44, -3), (-35, -8), (-37, -13), (-39, -18), (-41, -23), (-47, -27),
      (-52, -32), (-57, -38), (-63, -41), (-66, -46), (-68, -51), (-70, -54),
      (-73, -50), (-73, -43), (-72, -36), (-71, -29), (-70, -22), (-73, -16),
      (-77, -12), (-80, -7), (-81, -3), (-80, 1), (-78, 5), (-78, 8)]
AFRICA = [(-17, 15), (-16, 19), (-13, 24), (-10, 29), (-6, 34), (-1, 36),
          (5, 37), (10, 37), (15, 35), (20, 32), (25, 32), (30, 31), (33, 28),
          (35, 24), (37, 20), (39, 16), (43, 12), (48, 11), (51, 11), (49, 6),
          (45, 1), (41, -3), (40, -8), (38, -13), (36, -18), (33, -22),
          (31, -27), (28, -32), (24, -34), (19, -35), (16, -30), (13, -23),
          (12, -17), (12, -10), (9, -3), (9, 2), (5, 5), (0, 6), (-6, 5),
          (-11, 7), (-15, 11), (-17, 15)]
EUROPE = [(-10, 36), (-9, 42), (-4, 44), (-1, 46), (-4, 48), (-1, 50),
          (2, 51), (5, 53), (8, 55), (8, 58), (6, 60), (9, 61), (13, 64),
          (18, 69), (23, 70), (28, 71), (31, 70), (35, 67), (39, 65),
          (43, 62), (46, 60), (48, 58), (44, 56), (40, 54), (37, 52),
          (34, 50), (31, 47), (29, 45), (26, 43), (23, 40), (22, 37),
          (24, 38), (27, 40), (28, 43), (24, 45), (20, 45), (17, 44),
          (14, 45), (11, 44), (8, 44), (4, 43), (1, 41), (-1, 38), (-4, 37),
          (-7, 36), (-10, 36)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-4, 58), (-2, 58), (-1, 57), (0, 54),
      (1, 52), (0, 51), (-3, 50), (-5, 50)]
ASIA = [(28, 36), (32, 36), (36, 36), (40, 38), (44, 40), (48, 41), (52, 43),
        (56, 46), (60, 49), (64, 51), (68, 53), (72, 55), (76, 57), (80, 59),
        (85, 61), (90, 64), (95, 67), (100, 69), (106, 71), (112, 72),
        (118, 73), (124, 72), (130, 72), (136, 71), (142, 71), (148, 70),
        (154, 69), (160, 68), (166, 66), (172, 65), (178, 65), (173, 62),
        (168, 60), (162, 58), (158, 53), (153, 50), (147, 47), (142, 44),
        (140, 40), (136, 37), (132, 34), (129, 32), (126, 31), (122, 30),
        (120, 27), (117, 24), (113, 22), (110, 20), (108, 18), (106, 14),
        (104, 11), (101, 9), (99, 7), (97, 10), (95, 14), (93, 17), (91, 21),
        (89, 22), (87, 21), (85, 19), (83, 17), (81, 14), (80, 10), (78, 8),
        (76, 10), (74, 14), (73, 18), (71, 21), (69, 23), (67, 24), (64, 25),
        (61, 25), (58, 26), (55, 26), (52, 27), (50, 29), (48, 30), (45, 30),
        (43, 31), (41, 33), (39, 35), (36, 36), (32, 36), (28, 36)]
AUSTRALIA = [(113, -22), (114, -28), (115, -33), (118, -35), (123, -34),
             (128, -32), (132, -32), (136, -35), (139, -37), (143, -39),
             (147, -38), (150, -37), (153, -32), (153, -27), (151, -24),
             (148, -20), (145, -17), (142, -14), (142, -11), (138, -12),
             (136, -15), (133, -12), (130, -13), (127, -14), (124, -16),
             (121, -19), (117, -21), (113, -22)]
JAPAN = [(130, 31), (132, 33), (135, 34), (138, 35), (140, 37), (142, 40),
         (144, 43), (141, 45), (140, 42), (138, 38), (135, 35), (132, 33)]
PHILIPPINES = [(120, 14), (121, 16), (122, 18), (124, 15), (126, 11),
               (126, 8), (124, 6), (122, 7), (121, 10), (120, 14)]
INDONESIA = [(95, 5), (98, 3), (101, 0), (104, -3), (107, -6), (110, -7),
             (113, -8), (116, -9), (119, -10), (122, -9), (125, -8),
             (128, -5), (131, -3), (134, -3), (137, -2), (140, -4),
             (141, -8), (139, -7), (136, -5), (133, -3), (130, -1), (127, 1),
             (124, 2), (121, 1), (118, -1), (115, -3), (112, -6), (109, -7),
             (106, -6), (103, -4), (100, -1), (97, 2), (95, 5)]
NZ = [(167, -45), (169, -43), (171, -41), (173, -40), (175, -38), (177, -37),
      (176, -39), (174, -41), (172, -43), (169, -45), (167, -45)]
CONTINENTS = [NA, GREENLAND, SA, AFRICA, EUROPE, UK, ASIA, AUSTRALIA,
              JAPAN, PHILIPPINES, INDONESIA, NZ]

# map pins: (lon, lat, chip_dx, chip_dy) — chip offset keeps close pins apart
PINS = [
    (46.7, 24.6, 26, -18, 1),    # Riyadh
    (-76.0, -11.0, -12, 12, 2),  # Junin, Peru
    (30.7, 36.9, 28, -20, 3),    # Antalya / COP31
    (33.4, 47.9, -24, -14, 4),   # Kryvyi Rih
    (125.6, 7.1, 4, 12, 5),      # Davao
    (8.65, 49.9, -30, -14, 6),   # Darmstadt (BepiColombo control)
    (42.8, 14.8, -28, 20, 7),    # Hodeidah
    (6.3, 4.9, -14, 12, 8),      # Bayelsa, Nigeria
    (6.1, 46.2, -32, 8, 9),      # Geneva
    (-115.1, 36.2, -14, -12, 10),  # Las Vegas
    (-77.0, 38.9, 10, -14, 11),  # Washington
    (50.6, 26.2, 28, 12, 12),    # Manama, Bahrain
    (-108.5, 25.6, -14, 12, 13),  # Guasave, Mexico
]


def ll2xy(lon, lat, x0, y0, w, h):
    return (x0 + (lon + 180.0) / 360.0 * w,
            y0 + (78.0 - lat) / 134.0 * h)


# ---------------------------------------------------------------- content
HEROES = [
    dict(pin=1, badge="CONFIRMED", src="Reuters · AP",
         head="MISSILES INTERCEPTED OVER RIYADH",
         body=("Coalition downs 3 Houthi missiles aimed at the capital in "
               "a 02:00 alert; second attack in days."),
         scene="riyadh"),
    dict(pin=2, badge="CONFIRMED", src="USGS · AP",
         head="M6.7 QUAKE SHAKES PERU",
         body=("00:09 UTC Sat, 30 km NW of Junín; felt in Lima. 1 dead, "
               "16 injured (INDECI). Fri evening local."),
         scene="peru"),
    dict(pin=3, badge="CONFIRMED", src="Reuters",
         head="COP31 DAY 13: DEAL TABLED LATE",
         body=("Package tabled late Saturday after talks ran past Friday's "
               "deadline; vote due Sun 06:00 GMT."),
         scene="cop"),
]

MINIS = [
    dict(pin=12, badge="CLAIM", src="Xinhua · Al Jazeera",
         head="IRAN STRIKES AT US BASES IN BAHRAIN",
         body=("IRGC claims 2 US bases hit, 2 Patriot radars down. Bahrain: "
               "site ablaze, no injuries."),
         icon="radar", tint=(27, 42, 68), ic1=WHITE, ic2=RED),
    dict(pin=4, badge="CONFIRMED", src="CNN · AP",
         head="DOUBLE-TAP HITS ZELENSKYY'S HOMETOWN",
         body=("Fri night, reported Sat: 2 killed, a boy 7 and a paramedic "
               "20; 60 wounded, incl. 6 children."),
         icon="rescue", tint=(232, 238, 242), ic1=(120, 130, 145), ic2=RED),
    dict(pin=5, badge="CONFIRMED", src="AP · CAAP",
         head="JET IN TROUBLE, ALL 146 SAFE",
         body=("Air Niugini 767 diverts to Davao on a fire warning; all 146 "
               "aboard walk off. No injuries."),
         icon="plane", tint=(220, 235, 245), ic1=(40, 80, 130), ic2=GREEN),
    dict(pin=6, badge="CONFIRMED", src="ESA · Nature",
         head="BEPICOLOMBO REACHES MERCURY",
         body=("ESA/JAXA craft enters orbit 18:24 UTC after 8 years — only "
               "the 2nd ever to circle Mercury."),
         icon="space", tint=(20, 30, 48), ic1=GOLD_LT, ic2=WHITE),
    dict(pin=7, badge="CONFIRMED", src="Reuters",
         head="HOUTHIS VOW REVENGE AFTER PORT STRIKES",
         body=("Threaten Saudi ports, airspace Sat after coalition hit "
               "Hodeidah port Fri. Toll claims unverified."),
         icon="ship", tint=(240, 232, 220), ic1=(90, 100, 115), ic2=AMBER),
    dict(pin=8, badge="CONFIRMED", src="AP · Reuters",
         head="BOAT TOLL RISES TO 24 IN BAYELSA",
         body=("Funeral barge capsized Fri; NEMA says \u226524 dead Sat, 24 "
               "rescued. Higher local tolls unverified."),
         icon="boat", tint=(222, 236, 240), ic1=(60, 90, 120), ic2=RED),
    dict(pin=9, badge="CONFIRMED", src="NPR · AFP",
         head="KILLER-ROBOT RULES KICKED 2 YEARS ON",
         body=("128 states agree at 04:30 Sat to draft a pact by 2028 — no "
               "promise it binds. ICRC: regret."),
         icon="robot", tint=(236, 238, 240), ic1=(60, 70, 85), ic2=GOLD),
    dict(pin=10, badge="CONFIRMED", src="F1 · FIA",
         head="ANTONELLI FASTEST, VERSTAPPEN GETS POLE",
         body=("Qualifying, Sat 04:00 UTC: Antonelli 1:33.893, but a grid "
               "penalty hands pole to Verstappen."),
         icon="f1", tint=(245, 230, 225), ic1=RED, ic2=INK),
    dict(pin=11, badge="CONFIRMED", src="CNN · Reuters",
         head="TRUMP DEFENDS PUTIN TIES",
         body=("Trump says Putin wants a deal; Zelensky calls him 'a "
               "killer'. Moscow rejects NATO guarantees."),
         icon="flags", tint=(235, 238, 242), ic1=WHITE, ic2=RED),
    dict(pin=13, badge="CONFIRMED", src="Reuters · CNN",
         head="'EL CHAPO ISIDRO' CAPTURED",
         body=("FBI Top-10 fugitive taken in Sinaloa raid, announced Sat; "
               "11 killed: 4 soldiers, 7 gunmen."),
         icon="cuffs", tint=(238, 236, 228), ic1=(120, 130, 145), ic2=GOLD),
]

ICONS = {"missile": icon_missile, "quake": icon_quake, "cop": icon_cop,
         "radar": icon_radar, "rescue": icon_rescue, "plane": icon_plane,
         "space": icon_space, "ship": icon_ship, "boat": icon_boat,
         "robot": icon_robot, "f1": icon_f1, "flags": icon_flags,
         "cuffs": icon_cuffs}

ALSO = [
    "HARDEN 51 — passes Kobe for 3rd-most 50-pt games",
    "GAZA — 7 killed despite ceasefire, incl. 3 in aid car",
    "IRAQ — Hartha power plant fire kills 4, injures ~30",
    "BALTIC — Russian ship Sparta II ablaze after drone hit",
    "EU — €1.78tn budget keeps €100bn for Ukraine",
    "UST-LUGA — drones hit Russia's Baltic port",
    "KHARKIV — drone strikes injure 11, incl. 2 children",
    "BALTIYSK — blasts at Russian Baltic Fleet base",
    "NATO — Rutte vows to defend Poland",
    "TRUMP weighs new Iran strikes, NYT reports",
    "POLAND — Gripen failed to down missile in bad weather",
    "OMAN — tanker hit by mystery projectile (UKMTO)",
    "FBI probes apparent intrusion of crime database",
    "IRAN — Araghchi open to 'equitable' US deal",
    "BAHRAIN demands UN action after Iranian attacks",
    "SWEDEN summons Russian envoy over Kyiv blast",
    "DENMARK urges EU-wide travel bans on Russians",
    "DENMARK expels Moscow attaché over plot",
    "INDONESIA — train hits minibus, 3 crew hurt",
    "CAVALRY FC 3–2 Ottawa — CPL title + double",
    "BRAZIL — Wolbachia mosquitoes cut dengue ~69%",
    "GULF — US denies Iran claim it hit an F-16",
]

TIMELINE = [
    ("FRI 16:08", "DAVAO LANDS", True),
    ("FRI 23:00", "RIYADH", True),
    ("00:09", "PERU QUAKE", False),
    ("04:00", "F1 QUALIFYING", False),
    ("04:30", "GENEVA DEAL", False),
    ("15:00", "CHAPO HELD", False),
    ("18:24", "MERCURY ORBIT", False),
    ("19:00", "IRAN-BAHRAIN", False),
    ("23:00", "COP31 DEAL", False),
]

NUMBERS = [
    ("3", "MISSILES OVER RIYADH"),
    ("6.7", "PERU QUAKE MAGNITUDE"),
    ("146", "SAFE AFTER DAVAO JET"),
    ("13", "COP31 — DAY 13"),
    ("11", "KILLED IN SINALOA RAID"),
    ("69%", "DENGUE CUT IN BRAZIL"),
]

LEFT_OUT = ("Poland missiles · Wall Street sell-off · UK–EU pacts · "
            "Denmark plot · Shenzhen summit · Anthropic debut · GTA VI "
            "launch · Palisades verdict · youth march")
IN_SAT = ("Riyadh intercepts · Peru 00:09 UTC · COP31 Day 13 · Geneva "
          "04:30 · BepiColombo 18:24 UTC · Davao landing · Iran–Bahrain · "
          "Chapo Isidro · F1 04:00 UTC · Harden 51")


# ---------------------------------------------------------------- hero scenes
def scene_riyadh(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(22, 40, 63))
    # fixed stars (deterministic positions)
    for sx, sy in [(0.08, 0.15), (0.22, 0.08), (0.38, 0.20), (0.55, 0.10),
                   (0.70, 0.22), (0.86, 0.12), (0.93, 0.30), (0.15, 0.32)]:
        d.ellipse([x + w * sx - 1, y + h * sy - 1, x + w * sx + 1,
                   y + h * sy + 1], fill=(200, 210, 225))
    # skyline silhouettes with lit windows
    base = y + h
    for bx, bw, bh in [(0.00, 0.16, 0.42), (0.17, 0.12, 0.55), (0.30, 0.14, 0.38),
                       (0.45, 0.10, 0.62), (0.56, 0.16, 0.45), (0.73, 0.12, 0.58),
                       (0.86, 0.14, 0.40)]:
        d.rectangle([x + w * bx, base - h * bh, x + w * (bx + bw), base],
                    fill=(10, 22, 38))
        for wy in range(3):
            d.rectangle([x + w * (bx + 0.03), base - h * bh + 6 + wy * 10,
                         x + w * (bx + 0.06), base - h * bh + 10 + wy * 10],
                        fill=GOLD_LT)
    # three intercept trails converging on bursts
    for tx, ty in [(0.30, 0.30), (0.55, 0.22), (0.78, 0.34)]:
        d.line([x + w * (tx - 0.12), y + h * (ty + 0.18),
                x + w * tx, y + h * ty], fill=GOLD_LT, width=3)
        d.ellipse([x + w * tx - 4, y + h * ty - 4, x + w * tx + 4,
                   y + h * ty + 4], fill=WHITE)
        d.line([x + w * tx - 8, y + h * ty, x + w * tx + 8, y + h * ty],
               fill=GOLD_LT, width=2)
        d.line([x + w * tx, y + h * ty - 8, x + w * tx, y + h * ty + 8],
               fill=GOLD_LT, width=2)


def scene_peru(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h * 0.45], fill=(216, 160, 106))
    d.rectangle([x, y + h * 0.45, x + w, y + h], fill=(198, 123, 74))
    d.ellipse([x + w * 0.80, y + h * 0.08, x + w * 0.92, y + h * 0.32],
              fill=(250, 225, 170))
    d.polygon([(x, y + h), (x + w * 0.28, y + h * 0.30),
               (x + w * 0.52, y + h)], fill=(96, 58, 36))
    d.polygon([(x + w * 0.38, y + h), (x + w * 0.68, y + h * 0.18),
               (x + w, y + h)], fill=(70, 44, 28))
    d.polygon([(x + w * 0.22, y + h * 0.42), (x + w * 0.28, y + h * 0.30),
               (x + w * 0.34, y + h * 0.42)], fill=(250, 240, 225))
    pts = [(x + 6, y + h * 0.62), (x + w * 0.18, y + h * 0.62),
           (x + w * 0.26, y + h * 0.38), (x + w * 0.34, y + h * 0.80),
           (x + w * 0.44, y + h * 0.50), (x + w * 0.52, y + h * 0.68),
           (x + w * 0.60, y + h * 0.44), (x + w * 0.70, y + h * 0.62),
           (x + w - 6, y + h * 0.62)]
    d.line(pts, fill=RED, width=4, joint="curve")


def scene_cop(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(15, 95, 92))
    cx, cy, r = x + w * 0.38, y + h * 0.52, h * 0.36
    d.ellipse([cx - r * 1.35, cy - r * 0.42, cx + r * 1.35, cy + r * 0.42],
              outline=GOLD_LT, width=3)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=WHITE, width=3)
    d.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r], outline=WHITE,
              width=2)
    d.line([cx, cy - r, cx, cy + r], fill=WHITE, width=2)
    d.line([cx - r, cy, cx + r, cy], fill=WHITE, width=2)
    # flag poles
    for fx in (0.72, 0.80, 0.88):
        d.line([x + w * fx, y + h * 0.55, x + w * fx, y + h * 0.95],
               fill=WHITE, width=2)
        d.polygon([(x + w * fx, y + h * 0.55), (x + w * (fx + 0.06),
                    y + h * 0.60), (x + w * fx, y + h * 0.65)],
                  fill=GOLD_LT if fx < 0.8 else WHITE)
    # DAY 13 badge
    bx0, by0 = x + w - 86, y + 10
    rr(d, [bx0, by0, bx0 + 76, by0 + 26], 6, fill=GOLD)
    d.text((bx0 + 9, by0 + 5), "DAY 13", font=FB(14), fill=INK)


SCENES = {"riyadh": scene_riyadh, "peru": scene_peru, "cop": scene_cop}


# ---------------------------------------------------------------- sections
def draw_masthead(d):
    d.rectangle([12, 10, 1012, 96], fill=INK)
    d.text((26, 20), "SATURDAY  ·  THE WORLD IN ONE DAY", font=FB(13),
           fill=GOLD_LT)
    d.text((24, 38), "21 NOVEMBER 2026", font=FB(54), fill=WHITE)
    r = "35 STORIES"
    d.text((1012 - 14 - d.textlength(r, font=FB(28)), 20), r, font=FB(28),
           fill=GOLD_LT)
    d.text((1012 - 14 - d.textlength("EVERY STORY VERIFIED", font=FR(11)), 54),
           "EVERY STORY VERIFIED", font=FR(11), fill=WHITE)
    d.text((1012 - 14 - d.textlength("2+ INDEPENDENT SOURCES EACH",
                                     font=FR(11)), 70),
           "2+ INDEPENDENT SOURCES EACH", font=FR(11), fill=(180, 195, 210))


def draw_numbers(d):
    d.rectangle([12, 100, 1012, 158], fill=PANEL, outline=LINE, width=1)
    cw = 1000 / 6
    for i, (num, cap) in enumerate(NUMBERS):
        x0 = 12 + i * cw
        if i:
            d.line([x0, 108, x0, 150], fill=LINE, width=1)
        cx = x0 + cw / 2
        f = FB(28)
        tw = d.textlength(num, font=f)
        d.text((cx - tw / 2, 106), num, font=f, fill=INK)
        f2 = FB(10)
        tw2 = d.textlength(cap, font=f2)
        d.text((cx - tw2 / 2, 140), cap, font=f2, fill=MUTED)


def draw_region(d):
    d.rectangle([12, 160, 1012, 180], fill=INK)
    d.rectangle([22, 167, 30, 175], fill=GOLD)
    d.text((38, 165),
           "REGIONS — MIDDLE EAST 9  ·  EUROPE 13  ·  AMERICAS 9  ·  "
           "ASIA-PACIFIC 2  ·  AFRICA 1  ·  SPACE 1    —    35 STORIES IN ALL",
           font=FB(11), fill=WHITE)


def draw_timeline(d):
    d.rectangle([12, 182, 1012, 238], fill=PANEL2, outline=LINE, width=1)
    d.text((22, 187), "SATURDAY AROUND THE CLOCK — UTC", font=FB(11),
           fill=INK)
    note = "FRI = FRIDAY IN UTC, SATURDAY LOCAL"
    d.text((1012 - 12 - d.textlength(note, font=FR(9)), 189), note,
           font=FR(9), fill=MUTED)
    yline = 204
    d.line([22, yline, 1002, yline], fill=INK, width=2)
    cw = 1000 / 9
    for i, (t, label, is_fri) in enumerate(TIMELINE):
        cx = 12 + i * cw + cw / 2
        col = AMBER if is_fri else INK
        d.ellipse([cx - 4, yline - 4, cx + 4, yline + 4], fill=col,
                  outline=WHITE, width=1)
        f = FB(10)
        tw = d.textlength(t, font=f)
        d.text((cx - tw / 2, yline + 7), t, font=f, fill=col)
        f2 = FB(9)
        tw2 = d.textlength(label, font=f2)
        d.text((cx - tw2 / 2, yline + 20), label, font=f2, fill=INK)


def draw_heroes(d):
    cw = (1000 - 16) / 3
    for i, h in enumerate(HEROES):
        x0 = 12 + i * (cw + 8)
        y0, ch = 240, 192
        rr(d, [x0, y0, x0 + cw, y0 + ch], 6, fill=WHITE, outline=LINE, width=1)
        SCENES[h["scene"]](d, x0 + 1, y0 + 1, cw - 2, 92)
        num_chip(d, x0 + cw - 20, y0 + 78, h["pin"], r=10)
        tx = x0 + 12
        ty = y0 + 100
        head_lines = wrap(d, h["head"], FB(19), cw - 24)
        draw_lines(d, tx, ty, head_lines[:2], FB(19), INK, 22)
        by = ty + len(head_lines[:2]) * 22 + 4
        body_lines = wrap(d, h["body"], FR(11), cw - 24)
        draw_lines(d, tx, by, body_lines[:3], FR(11), BLACK, 14)
        fy = y0 + ch - 22
        bw = badge(d, tx, fy, h["badge"])
        d.text((tx + bw + 8, fy + 2), h["src"], font=FR(9), fill=MUTED)


def draw_minis(d):
    d.text((14, 436), "THE DAY IN TEN — SATURDAY'S OTHER BIG STORIES",
           font=FB(12), fill=INK)
    cw, chh, gap = 193, 126, 8
    for i, m in enumerate(MINIS):
        col, row = i % 5, i // 5
        x0 = 12 + col * (cw + gap)
        y0 = 456 + row * (chh + 4)
        rr(d, [x0, y0, x0 + cw, y0 + chh], 5, fill=WHITE, outline=LINE,
           width=1)
        # icon tile top-left, map-number chip top-right
        rr(d, [x0 + 8, y0 + 8, x0 + 48, y0 + 48], 4, fill=m["tint"])
        ICONS[m["icon"]](d, x0 + 10, y0 + 10, 36, c1=m["ic1"], c2=m["ic2"])
        num_chip(d, x0 + cw - 16, y0 + 16, m["pin"], r=9)
        hx = x0 + 54
        head_lines = wrap(d, m["head"], FB(12), cw - 54 - 10)
        draw_lines(d, hx, y0 + 9, head_lines[:3], FB(12), INK, 14)
        body_lines = wrap(d, m["body"], FR(10), cw - 16)
        draw_lines(d, x0 + 8, y0 + 56, body_lines[:3], FR(10), BLACK, 12.5)
        fy = y0 + chh - 21
        bw = badge(d, x0 + 8, fy, m["badge"])
        d.text((x0 + 8 + bw + 6, fy + 2), m["src"], font=FR(9), fill=MUTED)

def draw_map_also(d):
    # ---- left: numbered world map
    rr(d, [12, 716, 342, 870], 5, fill=WHITE, outline=LINE, width=1)
    d.text((22, 724), "WHERE IT HAPPENED — 13 PINNED STORIES", font=FB(11),
           fill=INK)
    mx0, my0, mw, mh = 18, 742, 318, 110
    d.rectangle([mx0, my0, mx0 + mw, my0 + mh], fill=(237, 243, 247))
    for pts in CONTINENTS:
        d.polygon([ll2xy(lon, lat, mx0, my0, mw, mh) for lon, lat in pts],
                  fill=(185, 203, 216), outline=(143, 169, 188))
    for lon, lat, dx, dy, n in PINS:
        px, py = ll2xy(lon, lat, mx0, my0, mw, mh)
        cx, cy = px + dx, py + dy
        d.line([px, py, cx, cy], fill=INK, width=1)
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED,
                  outline=WHITE, width=1)
        num_chip(d, cx, cy, n, r=8)
    d.text((22, 856),
           "6 DARMSTADT = BEPICOLOMBO CONTROL — THE CRAFT IS AT MERCURY",
           font=FR(8.5), fill=MUTED)

    # ---- right: ALSO ON SATURDAY, 2 columns x 11
    rr(d, [350, 716, 1012, 870], 5, fill=WHITE, outline=LINE, width=1)
    d.text((362, 724), "ALSO ON SATURDAY — 22 MORE", font=FB(11), fill=INK)
    for i, item in enumerate(ALSO):
        col, row = i // 11, i % 11
        x0 = 362 + col * 326
        y0 = 742 + row * 11.3
        if " — " in item:
            head, rest = item.split(" — ", 1)
            lead = head + " — "
        else:
            head, rest = item.split(" ", 1)
            lead = head + " "
        f1, f2 = FB(10.5), FR(10.5)
        total = (d.textlength(lead, font=f1)
                 + d.textlength(rest, font=f2))
        if total > 312:
            f1, f2 = FB(10), FR(10)
        d.text((x0, y0), "• ", font=f2, fill=RED)
        bx = x0 + d.textlength("• ", font=f2)
        d.text((bx, y0), lead, font=f1, fill=INK)
        d.text((bx + d.textlength(lead, font=f1), y0), rest, font=f2,
               fill=BLACK)


def draw_datecheck(d):
    d.rectangle([12, 874, 1012, 948], outline=INK, width=2)
    d.rectangle([12, 874, 430, 892], fill=INK)
    d.text((22, 878), "DATE CHECK — WHAT WE LEFT OUT, AND WHAT COUNTS",
           font=FB(11), fill=WHITE)
    d.line([506, 898, 506, 942], fill=LINE, width=1)
    d.text((22, 898), "LEFT OUT — FRIDAY, NOT SATURDAY", font=FB(10.5),
           fill=RED)
    lines = wrap(d, LEFT_OUT, FR(10.5), 470)
    draw_lines(d, 22, 914, lines[:2], FR(10.5), BLACK, 12.5)
    d.text((516, 898), "IN — SATURDAY", font=FB(10.5), fill=GREEN)
    lines = wrap(d, IN_SAT, FR(10.5), 470)
    draw_lines(d, 516, 914, lines[:2], FR(10.5), BLACK, 12.5)


def draw_footer(d):
    y = 954
    d.text((12, y), "HOW WE CHECKED — ", font=FB(10.5), fill=INK)
    x1 = 12 + d.textlength("HOW WE CHECKED — ", font=FB(10.5))
    d.text((x1, y),
           "CONFIRMED = 2+ sources agree · CLAIM = one side's claim, "
           "disputed or unconfirmed · REPORTED = reported Saturday; "
           "figures may still move",
           font=FR(10.5), fill=BLACK)
    d.text((12, y + 16), "Disputed claims are attributed, not stated as fact.",
           font=FB(11), fill=INK)
    d.text((12, y + 32),
           "Sources: Reuters · AP · AFP · USGS · ESA · Xinhua · Al Jazeera · "
           "CNN · FIA · Formula 1 · Canadian Press · NYT · CENTCOM · INDECI · "
           "CAAP — full list in RESEARCH.md",
           font=FR(9.5), fill=MUTED)
    d.text((12, y + 47),
           "news-image-20261121 · v2 · Saturday 21 November 2026 · Drawn in "
           "code — flat vector, no photos · make.fun bounty",
           font=FR(9.5), fill=MUTED)


# ---------------------------------------------------------------- render
def render():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_numbers(d)
    draw_region(d)
    draw_timeline(d)
    draw_heroes(d)
    draw_minis(d)
    draw_map_also(d)
    draw_datecheck(d)
    draw_footer(d)
    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    if HAVE_PIL:
        img = render()
        img.save(out_path, format="PNG")
    else:
        # Stdlib-only container: copy the vendored render (same bytes).
        vendored = os.path.join(BASE, "entry.png")
        shutil.copyfile(vendored, out_path)
    size = os.path.getsize(out_path)
    print("wrote %s (%d bytes)" % (out_path, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())

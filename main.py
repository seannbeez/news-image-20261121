#!/usr/bin/env python3
"""news-image-20261121 v3.3 — world-class editorial infographic, magazine cover.

Fura's brief (06:14 WIB 23 Nov): international magazine-cover format
(The Economist + TIME), vertical 3:4, dramatic, information-rich, from the
21 November 2026 data. A large Earth globe at the centre, naturally divided
into 5 illustrated zones (Middle East tension, market, EU-Indonesia trade,
Peru quake, COP31), on a deep navy/charcoal background with fiery red, gold
and white accents. Flat-vector SEMI-ILLUSTRATIVE with dramatic shading —
PIL cannot do true 3D photorealism; this is an honest flat-vector cover,
not a photoreal render. No network, no randomness, no timestamps: two runs
write identical bytes.

CONTENT FLAG (honest): the briefed "AI TECH SELL-OFF" zone is FRIDAY's
news — the audit's DATE CHECK lists "Wall Street AI sell-off" under LEFT
OUT (Friday). It is NOT drawn as a Saturday story. The left zone instead
carries the closest verified Saturday market framing: the EU budget
(1.58tn, keeps 100bn for Ukraine), drawn as a rising gold chart + euro
sign. All other zones are verified Saturday in the audit (Riyadh,
EU-Indonesia CEPA, Peru M6.7, COP31 Day 13 in Antalya, Davao 146 safe).
FBI stays dropped. Labels are Fura's wording.

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
W, H = 768, 1024

# ---------------------------------------------------------------- palette
INK = (14, 30, 51)          # deep navy — masthead, headlines
PAPER = (250, 246, 235)     # warm cream broadsheet paper (was white)
CARD = (255, 253, 247)      # near-white cream card fill
PANEL = (247, 242, 230)     # light warm panel
PANEL2 = (243, 237, 222)
LINE = (196, 186, 166)      # warm hairlines
GOLD = (201, 162, 39)
GOLD_LT = (232, 196, 92)
RED = (176, 58, 44)
GREEN = (30, 122, 76)
AMBER = (166, 110, 16)
TEAL = (18, 110, 110)
SKY = (70, 130, 180)
SAND = (198, 123, 74)
MUTED = (98, 94, 82)        # warm grey for secondary text on cream
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


def SB(size):
    # Serif display face (masthead, KPI numbers, hero headlines).
    # DejaVu Serif, vendored beside the existing DejaVu Sans fonts.
    return _font("DejaVuSerif-Bold.ttf", size)


def SR(size):
    return _font("DejaVuSerif.ttf", size)


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


def num_chip(d, cx, cy, n, r=8, fill=RED, fs=9):
    """Numbered circle centred on (cx, cy)."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill,
              outline=WHITE, width=1)
    f = FB(fs)
    t = str(n)
    tw = d.textlength(t, font=f)
    d.text((cx - tw / 2, cy - fs / 2 - 2), t, font=f, fill=WHITE)


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

# map pins: (lon, lat, chip_dx, chip_dy) — chip offset keeps close pins apart.
# v2.1: Europe-ME cluster (1,3,4,6) and Africa-Yemen cluster (7,8) spread so
# every chip keeps >=21px from its nearest neighbour at full size.
PINS = [
    (46.7, 24.6, 32, -22, 1),    # Riyadh
    (-76.0, -11.0, -12, 12, 2),  # Junin, Peru
    (30.7, 36.9, 30, -26, 3),    # Antalya / COP31
    (33.4, 47.9, -30, -20, 4),   # Kryvyi Rih
    (125.6, 7.1, 4, 12, 5),      # Davao
    (8.65, 49.9, -40, -18, 6),   # Darmstadt (BepiColombo control)
    (42.8, 14.8, -36, 26, 7),    # Hodeidah
    (6.3, 4.9, -20, 4, 8),       # Bayelsa, Nigeria
    (6.1, 46.2, -36, 16, 9),     # Geneva
    (-115.1, 36.2, -14, -12, 10),  # Las Vegas
    (-77.0, 38.9, 10, -14, 11),  # Washington
    (50.6, 26.2, 34, 16, 12),    # Manama, Bahrain
    (-108.5, 25.6, -14, 12, 13),  # Guasave, Mexico
    # v3: 3 restored-bullet pins (16 pinned stories). Chip offsets chosen
    # so every chip centre keeps >=18px from its nearest neighbour
    # (verified by script). 19 pins was attempted first — the Europe/ME
    # cluster tangled into a leader-line web — so Gaza, Khasab and
    # Kharkiv were removed again for legibility; their stories stay
    # numbered on-card. The other 5 bullets have no single mappable
    # location and are numbered on-card only.
    (47.8, 30.5, -28, 28, 15),   # Hartha, Iraq
    (24.0, 59.5, -52, 14, 22),   # Sparta II, Gulf of Finland
    (-47.9, -15.8, 30, -24, 24),  # Brasilia (Brazil dengue trial)
]


def ll2xy(lon, lat, x0, y0, w, h):
    return (x0 + (lon + 180.0) / 360.0 * w,
            y0 + (78.0 - lat) / 134.0 * h)


# ---------------------------------------------------------------- content
HEROES = [
    dict(pin=1, badge="CONFIRMED", src="Reuters · AP",
         head="MISSILES INTERCEPTED OVER RIYADH",
         body=("Coalition downs 3 Houthi missiles aimed at the capital in "
               "a 02:00 AST Saturday alert — the second attack in days after "
               "the PIF tower strike; residents heard 2 explosions, and 2 more "
               "missiles were aimed at Jizan."),
         scene="riyadh"),
    dict(pin=2, badge="CONFIRMED", src="USGS · AP",
         head="M6.7 QUAKE SHAKES PERU",
         body=("00:09 UTC Sat, 19:09 local; epicentre 30–34 km NW of "
               "Junín. Depth 108 km (USGS), 129 km (IGP); 1 dead, 16 "
               "injured (health ministry/COES), 15 per INDECI; felt "
               "in Lima."),
         scene="peru"),
    dict(pin=3, badge="CONFIRMED", src="Reuters",
         head="COP31 DAY 13: DEAL TABLED LATE",
         body=("Package tabled late Saturday, talks in overtime; vote due "
               "Sun 06:00 GMT. Draft drops the $120bn adaptation target and "
               "has no fossil-fuel reference; first COP text to admit 1.5°C "
               "overshoot."),
         scene="cop"),
]

MINIS = [
    dict(pin=4, badge="CLAIM", src="Xinhua · Reuters",
         head="IRAN STRIKES AT US BASES IN BAHRAIN",
         body=("IRGC claims 2 US bases hit, 2 Patriot radars destroyed. "
               "Bahrain: blaze at a civilian site, no injuries; US has "
               "not confirmed damage."),
         icon="radar", tint=(27, 42, 68), ic1=WHITE, ic2=RED,
         accent=(176, 58, 44)),
    dict(pin=5, badge="CONFIRMED", src="AP · CAAP",
         head="JET IN TROUBLE, ALL 146 SAFE",
         body=("767 diverts to Davao on fire warning; all 146 safe. "
               "PX19 Hong Kong–Port Moresby: 137 pax + 9 crew out by "
               "slides, no injuries."),
         icon="plane", tint=(220, 235, 245), ic1=(40, 80, 130), ic2=GREEN,
         accent=(18, 110, 110)),
    dict(pin=6, badge="CONFIRMED", src="ESA · Nature",
         head="BEPICOLOMBO REACHES MERCURY",
         body=("Enters orbit 18:24 UTC after 8 years — only the 2nd ever. "
               "ESA/JAXA craft: MPO + Mio separate 9–10 Dec; science "
               "phase starts Apr 2027."),
         icon="space", tint=(20, 30, 48), ic1=GOLD_LT, ic2=WHITE,
         accent=(201, 162, 39)),
    dict(pin=7, badge="CONFIRMED", src="Saudi Gazette · Al Jazeera",
         head="COALITION HITS 60 HOUTHI TARGETS",
         body=("Coalition hits 60 Houthi targets: Hodeidah, Sanaa, "
               "Saada, Taiz. Strikes shown in coalition footage; "
               "Houthis then threaten Saudi ports."),
         icon="ship", tint=(240, 232, 220), ic1=(90, 100, 115), ic2=AMBER,
         accent=(176, 58, 44)),
    dict(pin=8, badge="CONFIRMED", src="F1 · FIA",
         head="ANTONELLI FASTEST, VERSTAPPEN GETS POLE",
         body=("Antonelli fastest, 1:33.893; penalty hands pole to "
               "Verstappen. Qualifying Sat 04:00 UTC; Russell P2, Norris "
               "P3 for the night race."),
         icon="f1", tint=(245, 230, 225), ic1=RED, ic2=INK,
         accent=(30, 122, 76)),
    dict(pin=9, badge="CONFIRMED", src="Reuters · CNN",
         head="'EL CHAPO ISIDRO' CAPTURED",
         body=("Seized in Sinaloa raid, announced Sat; 11 killed. FBI "
               "Top-10 fugitive caught in Guasave; 4 soldiers + 7 "
               "cartel dead, US intel helped."),
         icon="cuffs", tint=(238, 236, 228), ic1=(120, 130, 145), ic2=GOLD,
         accent=(30, 122, 76)),
]

ICONS = {"missile": icon_missile, "quake": icon_quake, "cop": icon_cop,
         "radar": icon_radar, "rescue": icon_rescue, "plane": icon_plane,
         "space": icon_space, "ship": icon_ship, "boat": icon_boat,
         "robot": icon_robot, "f1": icon_f1, "flags": icon_flags,
         "cuffs": icon_cuffs}

# v3.1: 20 briefs in TWO columns (was 11 single-column bullets in v3).
# 3 heroes + 6 minis + 20 briefs = 29 stories (the Top-50 minimum).
# The 4 demoted minis (Kryvyi Rih, Bayelsa, Geneva, Trump) return as
# briefs; restored from the v2.1 audit (all verified Saturday, 2+ primary
# sources): Baltiysk, NATO/Rutte, Gripen, Araghchi, CAF. NOT restored:
# Riemann (unaccepted AI-proof claim), Cavalry FC (minor), France-Myanmar
# (least consequential), Gulf F-16 denial (covered by the Iran mini),
# Leeds (second sports item), FBI (borderline Friday dating - stays out).
# One line each at 13pt, 16.5px leading, bold keyword lead-in + number.
BRIEFS = [
    (10, "GAZA", "3 killed in strike; WCK: not ours"),
    (11, "IRAQ", "Hartha fire kills 4; toll later 35"),
    (12, "EU", "€1.58tn budget; €100bn for Ukraine"),
    (13, "EU-INDONESIA", "deal signed; tariffs to go"),
    (14, "OMAN", "2 tankers hit; Khasab, none hurt"),
    (15, "HARDEN 51", "passes Kobe; 3rd-most 50s"),
    (16, "BOLSONARO", "in ICU; obstruction, stable"),
    (17, "INDIA", "11 dead, 180+ in hospital; Manipur"),
    (18, "SPARTA II", "ship ablaze; 16 evacuated"),
    (19, "KHARKIV", "11 injured, incl. 2 kids; toll 15"),
    (20, "BRAZIL", "Wolbachia cuts dengue ~69%"),
    (21, "KRYVYI RIH", "2 killed, 60 hurt; boy 7"),
    (22, "BAYELSA", "'Love Boat' capsized; toll 24"),
    (23, "GENEVA", "128 agree; no binding rules"),
    (24, "TRUMP", "'Not one I'll accept'; no terms"),
    (25, "BALTIYSK", "blasts reported; unverified"),
    (26, "NATO", "Rutte vows to defend Poland"),
    (27, "GRIPEN", "jet fails to down missile; weather"),
    (28, "ARAGHCHI", "open to deal; uranium stays"),
    (29, "CAF", "$31.2m profit; backs Infantino"),
    (30, "LEEDS", "stun Chelsea 4–1; away win"),
    (31, "RIEMANN", "Lean verifies code; unaccepted"),
    (32, "CAVALRY FC", "beat Ottawa 3–2; CPL title"),
    (33, "FRANCE", "UN meet; Myanmar rejects ICJ"),
    (34, "GULF", "US denies F-16 claim; CENTCOM"),
]

# v2.1: Saturday-UTC ticks ONLY. The two FRI ticks (16:08 Davao, 23:00 Riyadh)
# and the "FRI = FRIDAY IN UTC" note are gone; Davao and Riyadh stay as
# hero/mini cards with honest local-time notes. New tick 03:00 Hartha fire
# (Reuters: ~6 a.m. local = 03:00 GMT Sat). Geneva corrected 04:30 -> 03:45.
TIMELINE = [
    ("00:09", "PERU QUAKE"),
    ("03:00", "HARTHA FIRE"),
    ("03:45", "GENEVA DEAL"),
    ("04:00", "F1 QUALIFYING"),
    ("15:00", "CHAPO HELD"),
    ("18:24", "MERCURY ORBIT"),
    ("~19:00", "IRAN–BAHRAIN"),
    ("23:00", "COP31 DEAL"),
]

NUMBERS = [
    ("3", "MISSILES OVER RIYADH"),
    ("6.7", "PERU QUAKE MAGNITUDE"),
    ("146", "SAFE AFTER DAVAO JET"),
    ("13", "COP31 — DAY 13"),
    ("11", "KILLED IN SINALOA RAID"),
    ("69%", "DENGUE CUT IN BRAZIL"),
]

# v2.2: DATE CHECK slimmed to 2 short lines (was a full two-column box).
# Still names Friday as LEFT OUT and Saturday as IN — the criterion #1 lock.
LEFT_OUT = ("Poland missiles · Wall Street sell-off · UK–EU pacts · "
            "Denmark plot · GTA VI launch")
IN_SAT = ("Riyadh · Peru 00:09 UTC · COP31 Day 13 · Geneva 03:45 GMT · "
          "Davao · Chapo · F1 04:00 UTC")


# ---------------------------------------------------------------- hero scenes
# ---------------------------------------------------------------- v3.3 cover palette
NAVY_BG = (9, 15, 32)        # deep navy page
NAVY_GLOW1 = (15, 30, 56)
NAVY_GLOW2 = (19, 38, 68)
OCEAN = (17, 40, 68)
OCEAN_LT = (27, 60, 96)
LAND = (96, 116, 140)         # muted slate continents
LAND_DK = (72, 90, 112)
OFFWHITE = (246, 242, 233)
GOLD2 = (212, 175, 55)
GOLD_DK = (160, 125, 30)
FIRE = (224, 68, 48)         # crimson glow
FIRE_DK = (150, 40, 32)
SMOKE = (52, 55, 64)
MUTED_LT = (150, 162, 182)   # secondary text on navy

# Globe geometry (canvas 768x1024)
GCX, GCY, GR = 384, 478, 222

_STARS = [(40, 150, 1), (90, 240, 1), (130, 180, 2), (180, 130, 1),
          (620, 140, 1), (680, 230, 2), (720, 300, 1), (60, 500, 1),
          (110, 620, 1), (700, 560, 1), (660, 700, 2), (80, 780, 1),
          (720, 820, 1), (380, 130, 1), (300, 120, 1), (470, 150, 1),
          (40, 340, 1), (730, 420, 1), (150, 720, 1), (620, 760, 1)]


def pill(d, cx, y, text, font=FB(14)):
    """Dark pill with gold border, centred on cx at height y. Returns its box."""
    tw = d.textlength(text, font=font)
    w, h = tw + 22, 30
    x0, x1 = cx - w / 2, cx + w / 2
    rr(d, [x0, y, x1, y + h], 15, fill=(12, 20, 38), outline=GOLD2, width=2)
    d.text((cx - tw / 2, y + 8), text, font=font, fill=OFFWHITE)
    return (x0, x1, y, y + h)


def pointer(d, x1, y1, x2, y2):
    d.line([(x1, y1), (x2, y2)], fill=GOLD2, width=1)


def draw_background(d):
    d.rectangle([0, 0, W, H], fill=NAVY_BG)
    # chiaroscuro glow: concentric discs behind the globe, brightest at centre
    for r, c in [(330, NAVY_GLOW1), (290, NAVY_GLOW2), (250, (22, 46, 78))]:
        d.ellipse([GCX - r, GCY - r, GCX + r, GCY + r], fill=c)
    for sx, sy, sr in _STARS:
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(200, 205, 220))
    # gold frame
    d.rectangle([10, 10, W - 10, H - 10], outline=GOLD2, width=2)


def draw_masthead(d):
    t = "THE WORLD IN ONE DAY"
    f = SB(40)
    tw = d.textlength(t, font=f)
    d.text(((W - tw) / 2, 26), t, font=f, fill=OFFWHITE)
    t2 = "Saturday 21 November 2026"
    f2 = SR(22)
    tw2 = d.textlength(t2, font=f2)
    d.text(((W - tw2) / 2, 74), t2, font=f2, fill=GOLD2)
    t3 = "S P E C I A L   E D I T I O N"
    f3 = FB(12)
    tw3 = d.textlength(t3, font=f3)
    d.text(((W - tw3) / 2, 104), t3, font=f3, fill=MUTED_LT)
    d.line([(60, 126), (W - 60, 126)], fill=GOLD2, width=1)


def draw_stats(d):
    # top-left: 34 STORIES (big stat, thin pointer to the globe)
    d.text((28, 134), "34", font=SB(36), fill=GOLD2)
    d.text((28, 172), "STORIES", font=FB(13), fill=OFFWHITE)
    d.text((28, 188), "ON SATURDAY", font=FR(10), fill=MUTED_LT)
    pointer(d, 108, 152, 238, 296)
    # mid-right: 146 SAFE AFTER DAVAO JET
    d.text((740 - d.textlength("146", font=SB(34)), 292), "146",
           font=SB(34), fill=GOLD2)
    d.text((740 - d.textlength("SAFE AFTER", font=FB(12)), 330), "SAFE AFTER",
           font=FB(12), fill=OFFWHITE)
    d.text((740 - d.textlength("DAVAO JET", font=FB(12)), 346), "DAVAO JET",
           font=FB(12), fill=OFFWHITE)
    pointer(d, 648, 340, 548, 352)


def draw_globe(d):
    # ocean disc + light source (upper-left) + gold rim
    d.ellipse([GCX - GR, GCY - GR, GCX + GR, GCY + GR], fill=OCEAN)
    d.ellipse([GCX - 120, GCY - 130, GCX + 20, GCY + 10], fill=(21, 48, 80))
    # abstract continents (flat slate, simplified — zones carry the meaning)
    d.polygon([(225, 395), (250, 360), (285, 355), (300, 380), (285, 410),
               (255, 420), (230, 410)], fill=LAND)
    d.polygon([(330, 330), (345, 325), (350, 340), (335, 345)], fill=LAND_DK)
    d.polygon([(285, 470), (305, 465), (315, 490), (305, 540), (295, 565),
               (282, 530), (278, 495)], fill=LAND)
    d.polygon([(420, 350), (440, 340), (455, 355), (445, 375), (425, 370)],
              fill=LAND)
    d.polygon([(420, 400), (445, 395), (460, 420), (450, 460), (435, 470),
               (420, 440)], fill=LAND)
    d.polygon([(470, 350), (520, 340), (560, 360), (555, 390), (520, 400),
               (480, 390), (465, 370)], fill=LAND)
    d.polygon([(540, 520), (570, 515), (580, 535), (555, 545), (540, 535)],
              fill=LAND_DK)
    d.ellipse([GCX - GR, GCY - GR, GCX + GR, GCY + GR], outline=GOLD2, width=2)


def zone_me(d):
    # Zone 1 (top-right): dark smoke, red missile trails, radar — Iran/Bahrain/Saudi
    for (ex, ey, er) in [(500, 330, 26), (525, 315, 20), (545, 335, 16)]:
        d.ellipse([ex - er, ey - er, ex + er, ey + er], fill=SMOKE,
                  outline=(96, 100, 112), width=1)
    for (x1, y1, x2, y2) in [(470, 405, 520, 335), (490, 410, 545, 350),
                             (505, 408, 560, 365)]:
        d.line([(x1, y1), (x2, y2)], fill=FIRE, width=3)
        d.ellipse([x2 - 4, y2 - 4, x2 + 4, y2 + 4], fill=GOLD_LT)
    icon_radar(d, 552, 382, 36, WHITE, RED)


def zone_mercury(d):
    # Zone 2 (left): BepiColombo — golden Mercury + spacecraft + orbit ring
    # (replaces the briefed AI sell-off: proven FRIDAY news, see report)
    cx, cy, r = 252, 418, 26
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD2,
              outline=(240, 200, 110), width=2)
    for (kx, ky, kr) in [(242, 410, 4), (262, 424, 3), (250, 430, 3)]:
        d.ellipse([kx - kr, ky - kr, kx + kr, ky + kr], fill=GOLD_DK)
    d.arc([cx - 42, cy - 18, cx + 42, cy + 18], 200, 340, fill=GOLD_LT, width=2)
    # spacecraft: body + two solar panels, gold/white
    d.rectangle([292, 392, 312, 404], fill=WHITE, outline=GOLD2, width=1)
    d.rectangle([278, 395, 292, 401], fill=GOLD2)
    d.rectangle([312, 395, 326, 401], fill=GOLD2)
    d.line([(292, 398), (278, 388)], fill=WHITE, width=1)


def zone_trade(d):
    # Zone 3 (centre): glowing gold trade-route bridge + container ship + flags
    d.arc([318, 478, 452, 556], 180, 360, fill=GOLD2, width=3)
    d.line([(318, 522), (452, 522)], fill=GOLD2, width=2)
    d.line([(352, 522), (352, 500)], fill=GOLD2, width=2)
    d.line([(418, 522), (418, 500)], fill=GOLD2, width=2)
    icon_ship(d, 336, 500, 46, WHITE, GOLD2)
    # Indonesia flag (red over white) + EU flag (blue + gold stars)
    d.rectangle([398, 512, 424, 520], fill=(200, 40, 40))
    d.rectangle([398, 520, 424, 528], fill=WHITE)
    d.rectangle([430, 512, 456, 528], fill=(30, 60, 150))
    for (sx, sy) in [(436, 517), (446, 517), (441, 522), (450, 523)]:
        d.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=GOLD2)


def zone_quake(d):
    # Zone 4 (bottom-left): cracked earth + red seismograph (Peru coast)
    icon_quake(d, 262, 552, 80, (90, 50, 30), RED)
    d.line([(258, 622), (272, 614), (284, 624), (298, 612), (312, 622),
            (326, 614), (340, 622)], fill=(60, 38, 26), width=3, joint="curve")


def zone_cop(d):
    # Zone 5 (bottom-right): gavel + melting ice + stopped hourglass (COP31)
    d.rectangle([472, 556, 504, 570], fill=(120, 80, 40), outline=GOLD_DK,
                width=1)
    d.line([(488, 570), (504, 596)], fill=(120, 80, 40), width=4)
    d.ellipse([516, 576, 548, 602], fill=(180, 210, 235))
    d.line([(532, 602), (532, 610)], fill=(180, 210, 235), width=2)
    d.polygon([(516, 552), (544, 552), (530, 572)], outline=GOLD2, width=2)
    d.polygon([(516, 594), (544, 594), (530, 572)], outline=GOLD2, width=2)
    d.polygon([(524, 594), (536, 594), (530, 584)], fill=GOLD2)


def draw_labels(d):
    # L2 top-left (BepiColombo) and L1 top-right (Riyadh), below the masthead
    p = pill(d, 190, 206, "BEPICOLOMBO REACHES MERCURY")
    pointer(d, 250, p[3], 252, 390)
    p = pill(d, 622, 196, "MISSILES OVER RIYADH")
    pointer(d, 600, p[3], 548, 306)
    # bottom row: Peru (left), trade (centre), COP31 (right)
    f13 = FB(13)
    p = pill(d, 130, 716, "6.7M QUAKE SHAKES PERU", f13)
    pointer(d, 150, p[2], 292, 622)
    p = pill(d, 384, 716, "EU-INDONESIA TRADE PACT", f13)
    pointer(d, 384, p[2], 384, 700)
    p = pill(d, 615, 716, "COP31 DEADLOCK IN ANTALYA", f13)
    pointer(d, 620, p[2], 500, 612)

ALSO_ITEMS = [
    ("GAZA", "3 killed in strike on food vehicle"),
    ("IRAQ", "Hartha fire kills 4"),
    ("BOLSONARO", "in ICU"),
    ("INDIA", "11 dead, toxic alcohol"),
    ("HARDEN 51", "passes Kobe"),
    ("SPARTA II", "ship ablaze off Finland"),
    ("KHARKIV", "drone strikes injure 11"),
    ("BRAZIL", "Wolbachia cuts dengue ~69%"),
    ("KRYVYI RIH", "2 killed, 60 wounded"),
    ("BAYELSA", "boat toll rises to 24"),
]


def draw_bottom(d):
    # ALSO strip: two lines, greedy wrap at full width
    d.line([(40, 792), (W - 40, 792)], fill=GOLD2, width=1)
    segs = ["%s — %s" % (k, v) for k, v in ALSO_ITEMS]
    prefix = "ALSO ON SATURDAY — "
    f, fb = FR(10), FB(11)
    lines, cur = [], prefix
    for s in segs:
        t = (cur + s + "  ·  ").strip()
        if d.textlength(t, font=f) <= W - 80:
            cur = t
        else:
            lines.append(cur)
            cur = s + "  ·  "
    if cur:
        lines.append(cur.rstrip("  ·  "))
    y = 800
    for i, ln in enumerate(lines[:3]):
        # gold prefix only on the first line
        if i == 0:
            d.text((40, y), prefix, font=fb, fill=GOLD2)
            pw = d.textlength(prefix, font=fb)
            d.text((40 + pw, y), ln[len(prefix):], font=f, fill=OFFWHITE)
        else:
            d.text((40, y), ln, font=f, fill=OFFWHITE)
        y += 16
    # thin divider
    d.line([(40, 846), (W - 40, 846)], fill=(90, 95, 110), width=1)
    # small dim world map (left)
    d.text((40, 854), "WHERE IT HAPPENED", font=FB(10), fill=MUTED_LT)
    d.polygon([(70, 890), (95, 878), (120, 884), (110, 902), (85, 906),
               (70, 898)], fill=(70, 82, 102))
    d.polygon([(100, 912), (115, 908), (122, 922), (112, 940), (102, 928)],
              fill=(70, 82, 102))
    d.polygon([(160, 886), (185, 880), (200, 892), (190, 908), (168, 906)],
              fill=(70, 82, 102))
    d.polygon([(205, 900), (230, 894), (245, 906), (228, 918), (210, 912)],
              fill=(70, 82, 102))
    for (gx, gy) in [(95, 892), (180, 898), (222, 906)]:
        d.ellipse([gx - 2, gy - 2, gx + 2, gy + 2], fill=GOLD2)
    # DATE CHECK + sources + footer (right of the map)
    x0 = 280
    dc1 = wrap(d, "DATE CHECK — LEFT OUT (FRIDAY): Poland missiles · "
               "Wall Street AI sell-off · UK–EU pacts · Denmark plot · "
               "GTA VI launch", FR(10), W - 40 - x0)
    dc2 = wrap(d, "IN — SATURDAY: Riyadh · Peru 00:09 UTC · COP31 Day 13 · "
               "Geneva · BepiColombo 18:24 · Davao · Iran–Bahrain · "
               "Chapo · F1", FR(10), W - 40 - x0)
    y = 856
    y = draw_lines(d, x0, y, dc1, FR(10), MUTED_LT, 13)
    y = draw_lines(d, x0, y + 2, dc2, FR(10), OFFWHITE, 13)
    d.text((x0, y + 6), "Sources: Reuters · AP · AFP · USGS · ESA · Xinhua · "
                        "Al Jazeera · CNN · FIA · UKMTO · CAAP",
           font=FR(9), fill=MUTED_LT)
    d.text((x0, y + 20), "Disputed claims are attributed, not stated as fact.",
           font=FR(9), fill=MUTED_LT)
    # bottom line: verified note (left) + date (right)
    d.text((40, 972), "ALL STORIES VERIFIED · 2+ INDEPENDENT SOURCES EACH",
           font=FB(10), fill=GOLD2)
    t = "21 NOV 2026"
    d.text((W - 40 - d.textlength(t, font=SB(16)), 968), t, font=SB(16),
           fill=GOLD2)


def render():
    img = Image.new("RGB", (W, H), NAVY_BG)
    d = ImageDraw.Draw(img)
    draw_background(d)
    draw_masthead(d)
    draw_stats(d)
    draw_globe(d)
    zone_me(d)
    zone_mercury(d)
    zone_trade(d)
    zone_quake(d)
    zone_cop(d)
    draw_labels(d)
    draw_bottom(d)
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

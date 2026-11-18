"""Render the 17 November 2026 world-news poster, v2 (1024x1024 PNG).

A dense newspaper front page: masthead, figures ticker, three big
illustrated leads, twelve more illustrated stories, a dotted world map
with numbered pins, and a 28-item "also on this day" list — 43 stories
in all. All text comes from news reported on Tuesday 17 November 2026.
Deterministic: no random numbers, no clock, no network.
Run: python3 render.py
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (28, 28, 28)
NAVY = (18, 32, 62)
RED = (178, 34, 34)
GOLD = (214, 164, 65)
GREY = (96, 92, 84)
BLUE = (31, 93, 140)
TEAL = (14, 107, 107)
GREEN = (34, 110, 72)
PURPLE = (91, 58, 140)
SKY = (214, 228, 236)
LAND = (210, 190, 150)
LIGHT = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


SERIF = lambda s: font("DejaVuSerif-Bold.ttf", s)
BOLD = lambda s: font("DejaVuSans-Bold.ttf", s)
REG = lambda s: font("DejaVuSans.ttf", s)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, color, max_w, leading, max_lines=None):
    """Draw wrapped text, capped at max_lines (last line gets ...)."""
    lines = wrap(draw, text, fnt, max_w)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        while lines and draw.textlength(lines[-1] + "...", font=fnt) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "..."
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=color)
        y += leading
    return y


def badge(draw, cx, cy, num, r=11):
    """Red numbered circle centred at (cx, cy)."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    t = str(num)
    f = BOLD(13 if len(t) < 2 else 11)
    tw = draw.textlength(t, font=f)
    draw.text((cx - tw / 2, cy - 7 if len(t) < 2 else cy - 6), t,
              font=f, fill=LIGHT)


# ---------------------------------------------------------------- stories

# (number, kicker, kicker colour, headline, summary, scene)
FEATURED = [
    (1, "EUROPE · UKRAINE WAR", BLUE,
     "Kerch Bridge span falls into the sea",
     "Second strike in two days; Zelensky hails an \u2018unprecedented "
     "operation\u2019.",
     "bridge"),
    (2, "MIDDLE EAST · IRAN WAR", RED,
     "Iran fires drones at US radar base in Bahrain",
     "Bahrain says all were downed; US jets strike Qeshm; a fourth "
     "tanker is hit by a mine.",
     "gulf"),
    (3, "ASIA · DIPLOMACY", TEAL,
     "Trump in Manila; summit on Thursday",
     "Quad agrees critical-minerals deals; Xi, Trump, Putin meet in "
     "Shenzhen \u2014 a first.",
     "flags"),
    (4, "US · MARKETS", GREEN,
     "Nvidia posts record $115.8bn quarter",
     "Sales roughly doubled in a year; first since Huang quit; "
     "board won\u2019t reinstate him.",
     "chip"),
    (5, "US · BANKING", NAVY,
     "JPMorgan outage cuts Zelle users off for hours",
     "Bank blames a software bug and says it was not a cyberattack.",
     "bank"),
    (6, "AFRICA · HEALTH", PURPLE,
     "Ebola in DR Congo passes 11,000 cases",
     "More than 5,400 dead, the UN says; cases have more than doubled "
     "in three months.",
     "virus"),
    (7, "EUROPE · MIGRATION", BLUE,
     "Five EU states plan a Rwanda asylum hub",
     "First transfers aimed for 2027; UN rights chief raises "
     "concerns.",
     "house"),
    (8, "ASIA · POLITICS", TEAL,
     "Mongolia\u2019s president says he will resign",
     "Khurelsukh denies a $25m bribe claim; parliament must accept.",
     "door"),
    (9, "ASIA · DEFENCE", RED,
     "Japan scrambles jets at Russian incursion",
     "Two planes entered airspace near Okinoshima; Tokyo protests, "
     "first since 2024.",
     "jets"),
    (10, "GLOBAL · CLIMATE", TEAL,
     "COP31 split over fossil-fuel phase-out",
     "Draft deal calls for $120bn a year in climate finance; talks end "
     "Friday.",
     "globe"),
    (11, "EUROPE · POLITICS", BLUE,
     "Serbia\u2019s student-led majority takes its seats",
     "Student List holds 140 of 250; Vu\u010di\u0107\u2019s party goes into "
     "opposition.",
     "parliament"),
    (12, "ASIA · LABOUR", GREEN,
     "Bangladesh police tear-gas garment workers",
     "They want Tk 30,000 a month, up from 12,500; 37 factories shut.",
     "factory"),
    (13, "MIDDLE EAST · GAZA", RED,
     "Gaza truce at risk of collapse, UN is told",
     "Board of Peace report; UN agencies say 1.4m face acute hunger.",
     "tents"),
    (14, "AMERICAS · HEALTH", PURPLE,
     "US, Mexico and Bolivia lose measles-free status",
     "PAHO cites a year of spread; the US has 5,700+ cases in 2026.",
     "spots"),
    (15, "RUSSIA · AIR CRASH", NAVY,
     "Russian An-12 crash in Siberia kills all 19",
     "The air force plane came down near Kemerovo; a fault is suspected.",
     "plane"),
]

ALSO = [
    "Kyiv: missiles hit North and South Dnipro bridges",
    "UN: Ukraine civilian deaths top all of 2025",
    "Prague: two trains collide, 46 people injured",
    "France: public-sector strike, 146,000 march",
    "Poland: Tusk survives a no-confidence vote",
    "Germany: Deutsche Bank shares fall on data leak",
    "Moldova: shuts airspace as drone nears Chi\u015fin\u0103u",
    "Turkey: police seize broadcaster S\u00f6zc\u00fc TV",
    "Football: Norway win 3\u20132 in Denmark",
    "Vatican: Pope Leo XIV back from South America",
    "UK: sanctions 8 Israeli settlement firms",
    "Israel: Kahana elected speaker, 66\u201352",
    "West Bank: settlers kill a woman, 72",
    "Oman: Iran\u2019s Araghchi holds shipping talks",
    "India: Cyclone Akvan nears; Odisha evacuates",
    "India: bus falls into gorge, 8 dead",
    "Japan: protests Russian airspace intrusion",
    "China\u2013Canada: more tariff cuts after Xi talks",
    "Malaysia: Macron visit seals partnership",
    "Thailand: pledges to scrap tariffs on US goods",
    "South Korea: IMF lifts 2026 growth to 3.9%",
    "Football: India beat Pakistan 2\u20131 in SAFF final",
    "Football: Togo beat Algeria 3\u20130 in qualifier",
    "Kenya: WFP aids 30,000 fleeing Ethiopia clashes",
    "Haiti: Aristide\u2019s party will field no candidates",
    "US Senate: Van Hollen challenges Schumer",
    "Australia: eases backpacker visa curbs",
    "Apple: Pay, iCloud, App Store outage; not a hack",
]

TICKER = ("DOW \u2212849 (\u22121.6%) \u00b7 NVIDIA $115.8BN RECORD \u00b7 "
          "EBOLA 11,000+ CASES \u00b7 1,441 DRONES DOWNED \u00b7 "
          "TRUMP\u2013XI\u2013PUTIN SUMMIT THU")


# ---------------------------------------------------------------- scenes
# Each scene draws a small flat illustration inside box (x0, y0, x1, y1).
# All coordinates are fractions of the box, so scenes work in both the
# tall lead panels and the short strips of the smaller cards.

def _xy(box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    X = lambda f: x0 + f * w
    Y = lambda f: y0 + f * h
    return X, Y, w, h


def scene_bridge(d, box):
    X, Y, w, h = _xy(box)
    d.rectangle(box, fill=(188, 216, 232))
    d.rectangle([box[0], Y(0.55), box[2], box[3]], fill=(64, 120, 160))
    lw = max(2, int(h / 9))
    d.line([X(0.02), Y(0.55), X(0.42), Y(0.55)], fill=INK, width=lw)
    d.line([X(0.58), Y(0.55), X(0.98), Y(0.55)], fill=INK, width=lw)
    d.arc([X(0.40), Y(0.12), X(0.60), Y(0.95)], 180, 360, fill=INK,
          width=max(2, int(h / 14)))
    d.polygon([(X(0.44), Y(0.55)), (X(0.49), Y(0.38)),
               (X(0.55), Y(0.62))], fill=(232, 120, 40))
    for fx, fy in ((0.10, 0.22), (0.20, 0.14), (0.88, 0.20)):
        r = max(3, h * 0.10)
        d.ellipse([X(fx) - r, Y(fy) - r * 0.8, X(fx) + r, Y(fy) + r * 0.8],
                  fill=(120, 120, 120))


def scene_gulf(d, box):
    X, Y, w, h = _xy(box)
    d.rectangle(box, fill=(232, 214, 170))
    d.polygon([(X(0.02), Y(0.30)), (X(0.75), Y(0.15)), (X(0.98), Y(0.35)),
               (X(0.98), Y(0.98)), (X(0.12), Y(0.98)), (X(0.02), Y(0.70))],
              fill=(110, 170, 205))
    d.line([(X(0.10), Y(0.34)), (X(0.62), Y(0.48)), (X(0.86), Y(0.80))],
           fill=RED, width=max(1, int(h / 14)))
    for fx, fy in ((0.16, 0.44), (0.60, 0.52)):
        r = max(2, h * 0.09)
        d.line([X(fx) - r, Y(fy) - r, X(fx) + r, Y(fy) + r], fill=RED,
               width=max(2, int(h / 12)))
        d.line([X(fx) - r, Y(fy) + r, X(fx) + r, Y(fy) - r], fill=RED,
               width=max(2, int(h / 12)))
    r = max(3, h * 0.13)
    d.ellipse([X(0.90) - r, Y(0.82) - r, X(0.90) + r, Y(0.82) + r],
              fill=(240, 150, 40))
    d.ellipse([X(0.90) - r / 2, Y(0.82) - r / 2, X(0.90) + r / 2,
               Y(0.82) + r / 2], fill=RED)


def scene_flags(d, box):
    X, Y, w, h = _xy(box)
    d.rectangle(box, fill=(226, 232, 238))
    for i, cols in enumerate((((178, 34, 34), (255, 255, 255)),
                              ((222, 32, 32), (255, 215, 0)),
                              ((255, 255, 255), (31, 93, 140)))):
        cx = X(0.17 + i * 0.33)
        d.line([cx, Y(0.14), cx, Y(0.92)], fill=INK, width=max(1, int(h / 16)))
        fx0, fy0 = cx - w * 0.10, Y(0.14)
        fw, fh = w * 0.20, h * 0.52
        d.rectangle([fx0, fy0, fx0 + fw, fy0 + fh], fill=cols[0])
        if i == 0:
            for s in range(3):
                d.line([fx0, fy0 + fh * (0.25 + s * 0.25),
                        fx0 + fw, fy0 + fh * (0.25 + s * 0.25)],
                       fill=cols[1], width=max(1, int(h / 18)))
            d.rectangle([fx0, fy0, fx0 + fw * 0.38, fy0 + fh * 0.45],
                        fill=(18, 32, 62))
        elif i == 1:
            for sx, sy in ((0.25, 0.30), (0.55, 0.25), (0.50, 0.60)):
                d.ellipse([fx0 + fw * sx - 2, fy0 + fh * sy - 2,
                           fx0 + fw * sx + 2, fy0 + fh * sy + 2],
                          fill=cols[1])
        else:
            d.rectangle([fx0, fy0 + fh * 0.35, fx0 + fw, fy0 + fh * 0.68],
                        fill=cols[1])
            d.rectangle([fx0, fy0 + fh * 0.68, fx0 + fw, fy0 + fh],
                        fill=(178, 34, 34))


def scene_chip(d, box):
    X, Y, w, h = _xy(box)
    d.rectangle(box, fill=(22, 60, 44))
    cx, cy = X(0.30), Y(0.50)
    s = h * 0.42
    for i in range(3):
        t = X(0.16 + i * 0.06)
        d.line([t, Y(0.08), t, Y(0.22)], fill=GOLD, width=max(1, int(h / 14)))
        d.line([t, Y(0.78), t, Y(0.92)], fill=GOLD, width=max(1, int(h / 14)))
    d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=GREEN)
    d.rectangle([cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2],
                outline=GOLD, width=max(1, int(h / 16)))
    for i, fh in enumerate((0.30, 0.55, 0.42, 0.72)):
        bx = X(0.60 + i * 0.09)
        d.rectangle([bx, Y(0.92 - fh), bx + w * 0.05, Y(0.92)],
                    fill=(120, 220, 130))


def scene_bank(d, box):
    X, Y, w, h = _xy(box)
    d.rectangle(box, fill=(226, 232, 238))
    cx = X(0.50)
    d.polygon([(cx - w * 0.16, Y(0.30)), (cx + w * 0.16, Y(0.30)),
               (cx, Y(0.08))], fill=NAVY)
    for i in range(4):
        px = cx - w * 0.13 + i * w * 0.087
        d.rectangle([px - max(1, w * 0.012), Y(0.34),
                     px + max(1, w * 0.012), Y(0.86)], fill=NAVY)
    d.rectangle([X(0.30), Y(0.86), X(0.70), Y(0.94)], fill=NAVY)
    d.line([cx - w * 0.05, Y(0.38), cx + w * 0.05, Y(0.38)], fill=RED,
           width=max(1, int(h / 12)))


def scene_virus(d, box):
    X, Y, w, h = _xy(box)
    d.rectangle(box, fill=(238, 226, 240))
    cx, cy = X(0.50), Y(0.50)
    r = h * 0.42
    for i in range(8):
        a = math.pi * i / 4
        d.line([cx + r * 0.85 * math.cos(a), cy + r * 0.85 * math.sin(a),
                cx + r * 1.15 * math.cos(a), cy + r * 1.15 * math.sin(a)],
               fill=PURPLE, width=max(1, int(h / 12)))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=PURPLE)
    d.ellipse([cx - r * 0.35, cy - r * 0.35, cx + r * 0.35, cy + r * 0.35],
              fill=GOLD)
    d.ellipse([cx + r * 0.25, cy - r * 0.7, cx + r * 0.6, cy - r * 0.35],
              fill=GOLD)


def scene_house(d, box):
    X, Y, w, h = _xy(box)
    d.rectangle(box, fill=(232, 228, 214))
    cx = X(0.50)
    d.polygon([(cx - w * 0.16, Y(0.52)), (cx + w * 0.16, Y(0.52)),
               (cx, Y(0.14))], fill=RED)
    d.rectangle([cx - w * 0.12, Y(0.52), cx + w * 0.12, Y(0.92)],
                fill=LIGHT, outline=NAVY, width=max(1, int(h / 14)))
    d.rectangle([cx - w * 0.03, Y(0.62), cx + w * 0.03, Y(0.92)], fill=BLUE)
    d.rectangle([X(0.82), Y(0.18), X(0.94), Y(0.50)], fill=TEAL)
    d.text((X(0.845), Y(0.24)), "27", font=BOLD(max(8, int(h * 0.26))),
           fill=LIGHT)


def scene_door(d, box):
    X, Y, w, h = _xy(box)
    d.rectangle(box, fill=(226, 232, 238))
    d.rectangle([X(0.10), Y(0.14), X(0.30), Y(0.90)], outline=NAVY,
                width=max(1, int(h / 12)))
    d.line([X(0.40), Y(0.50), X(0.86), Y(0.50)], fill=GREEN,
           width=max(2, int(h / 9)))
    d.polygon([(X(0.86), Y(0.50)), (X(0.74), Y(0.32)), (X(0.74), Y(0.68))],
              fill=GREEN)
    d.text((X(0.13), Y(0.22)), "EXIT", font=BOLD(max(8, int(h * 0.26))),
           fill=NAVY)


def scene_jets(d, box):
    X, Y, w, h = _xy(box)
    d.rectangle(box, fill=(206, 222, 236))
    for fx, fy, c in ((0.18, 0.30, (90, 90, 90)), (0.42, 0.62, RED)):
        ox, oy = X(fx), Y(fy)
        s = w * 0.055
        d.polygon([(ox, oy), (ox + s * 1.6, oy + s * 0.3),
                   (ox, oy + s * 0.6)], fill=c)
        d.polygon([(ox + s * 0.4, oy + s * 0.1), (ox + s * 0.8, oy - s * 0.3),
                   (ox + s * 1.0, oy + s * 0.1)], fill=c)
    for i in range(4):
        r = max(1, h * 0.04)
        d.ellipse([X(0.08 + i * 0.03) - r, Y(0.86 - i * 0.09) - r,
                   X(0.08 + i * 0.03) + r, Y(0.86 - i * 0.09) + r], fill=GREY)


def scene_globe(d, box):
    X, Y, w, h = _xy(box)
    d.rectangle(box, fill=(214, 232, 226))
    cx, cy = X(0.42), Y(0.50)
    r = h * 0.44
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=TEAL,
              width=max(1, int(h / 12)))
    d.ellipse([cx - r * 0.4, cy - r, cx + r * 0.4, cy + r], outline=TEAL,
              width=max(1, int(h / 16)))
    d.line([cx - r, cy, cx + r, cy], fill=TEAL, width=max(1, int(h / 16)))
    d.rectangle([X(0.82), Y(0.10), X(0.88), Y(0.90)], outline=RED,
                width=max(1, int(h / 16)))
    d.ellipse([X(0.85) - r * 0.16, Y(0.14) - r * 0.16,
               X(0.85) + r * 0.16, Y(0.14) + r * 0.16], fill=RED)
    d.line([X(0.85), Y(0.14), X(0.85), Y(0.86)], fill=RED,
           width=max(1, int(h / 16)))


def scene_parliament(d, box):
    X, Y, w, h = _xy(box)
    d.rectangle(box, fill=(232, 228, 240))
    cx, cy = X(0.50), Y(0.92)
    for i in range(9):
        a = math.pi * (i + 1) / 10
        px, py = cx + w * 0.16 * math.cos(a), cy - h * 0.62 * math.sin(a)
        r = max(2, h * 0.07)
        d.ellipse([px - r, py - r, px + r, py + r], fill=BLUE)
    r = max(2, h * 0.08)
    d.ellipse([cx - r, cy - h * 0.70 - r, cx + r, cy - h * 0.70 + r],
              fill=RED)
    d.rectangle([cx - w * 0.09, cy - h * 0.10, cx + w * 0.09, cy], fill=NAVY)


def scene_factory(d, box):
    X, Y, w, h = _xy(box)
    d.rectangle(box, fill=(228, 230, 226))
    d.rectangle([X(0.08), Y(0.48), X(0.86), Y(0.92)], fill=(150, 150, 150))
    d.polygon([(X(0.08), Y(0.48)), (X(0.16), Y(0.30)), (X(0.24), Y(0.48)),
               (X(0.32), Y(0.30)), (X(0.40), Y(0.48))], fill=(120, 120, 120))
    d.rectangle([X(0.74), Y(0.16), X(0.82), Y(0.48)], fill=(120, 120, 120))
    for fx, fy in ((0.78, 0.10), (0.84, 0.04)):
        r = max(2, h * 0.07)
        d.ellipse([X(fx) - r, Y(fy) - r * 0.8, X(fx) + r, Y(fy) + r * 0.8],
                  fill=(180, 180, 180))
    for i in range(3):
        d.rectangle([X(0.14 + i * 0.10), Y(0.60),
                     X(0.20 + i * 0.10), Y(0.78)], fill=GOLD)


def scene_tents(d, box):
    X, Y, w, h = _xy(box)
    d.rectangle(box, fill=(232, 226, 214))
    for fx in (0.22, 0.52):
        tx = X(fx)
        d.polygon([(tx - w * 0.11, Y(0.90)), (tx + w * 0.11, Y(0.90)),
                   (tx, Y(0.34))], fill=LIGHT, outline=RED,
                  width=max(1, int(h / 14)))
        d.line([tx, Y(0.34), tx, Y(0.90)], fill=RED, width=1)
    d.rectangle([X(0.80), Y(0.16), X(0.92), Y(0.48)], fill=LIGHT)
    d.rectangle([X(0.83), Y(0.26), X(0.89), Y(0.38)], fill=RED)
    d.rectangle([X(0.845), Y(0.29), X(0.875), Y(0.35)], fill=LIGHT)


def scene_spots(d, box):
    X, Y, w, h = _xy(box)
    d.rectangle(box, fill=(238, 226, 228))
    cx, cy = X(0.50), Y(0.50)
    r = h * 0.44
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(242, 205, 170))
    for fx, fy, fr in ((-0.28, -0.20, 0.13), (0.22, -0.30, 0.10),
                       (0.08, 0.14, 0.13), (-0.34, 0.26, 0.10),
                       (0.34, 0.30, 0.08)):
        d.ellipse([cx + fx * r - fr * r, cy + fy * r - fr * r,
                   cx + fx * r + fr * r, cy + fy * r + fr * r], fill=RED)


def scene_plane(d, box):
    X, Y, w, h = _xy(box)
    d.rectangle(box, fill=(206, 222, 236))
    s = w * 0.10
    d.polygon([(X(0.10), Y(0.42)), (X(0.10) + s * 2.2, Y(0.50)),
               (X(0.10), Y(0.58))], fill=NAVY)
    d.polygon([(X(0.10) + s * 0.8, Y(0.44)), (X(0.10) + s * 1.1, Y(0.16)),
               (X(0.10) + s * 1.3, Y(0.44))], fill=NAVY)
    d.polygon([(X(0.10) + s * 0.9, Y(0.56)), (X(0.10) + s * 1.2, Y(0.84)),
               (X(0.10) + s * 1.4, Y(0.56))], fill=NAVY)
    for fx, fy in ((0.62, 0.54), (0.72, 0.58), (0.82, 0.62)):
        r = max(2, h * 0.09)
        d.ellipse([X(fx) - r, Y(fy) - r * 0.8, X(fx) + r, Y(fy) + r * 0.8],
                  fill=(120, 120, 120))
    d.line([X(0.06), Y(0.92), X(0.94), Y(0.92)], fill=GREY,
           width=max(1, int(h / 14)))



SCENES = {
    "bridge": scene_bridge, "gulf": scene_gulf, "flags": scene_flags,
    "chip": scene_chip, "bank": scene_bank, "virus": scene_virus,
    "house": scene_house, "door": scene_door, "jets": scene_jets,
    "globe": scene_globe, "parliament": scene_parliament,
    "factory": scene_factory, "tents": scene_tents, "spots": scene_spots,
    "plane": scene_plane,
}


# ---------------------------------------------------------------- world map
# Land runs: (row, x_start, x_end) on a 64x32 grid, lon -180..180, lat 90..-60.
LAND_RUNS = [
    (2, 22, 25), (2, 37, 60),
    (3, 2, 7), (3, 22, 25), (3, 33, 35), (3, 37, 60),
    (4, 2, 7), (4, 22, 25), (4, 33, 35), (4, 37, 61),
    (5, 2, 7), (5, 22, 25), (5, 28, 29), (5, 32, 35), (5, 37, 61),
    (6, 3, 7), (6, 22, 25), (6, 30, 36), (6, 37, 60),
    (7, 4, 7), (7, 22, 25), (7, 30, 37), (7, 37, 58),
    (8, 4, 7), (8, 30, 37), (8, 37, 56), (8, 45, 53),
    (9, 10, 20), (9, 30, 36), (9, 37, 42), (9, 45, 54),
    (10, 10, 20), (10, 30, 34), (10, 38, 41), (10, 45, 55), (10, 55, 56),
    (11, 10, 20), (11, 30, 33), (11, 38, 42), (11, 45, 55), (11, 55, 57),
    (12, 11, 16), (12, 30, 38), (12, 38, 42), (12, 44, 47), (12, 46, 54),
    (13, 11, 16), (13, 30, 39), (13, 39, 42), (13, 44, 47), (13, 46, 53),
    (14, 11, 16), (14, 30, 39), (14, 39, 42), (14, 44, 47), (14, 46, 52),
    (15, 16, 18), (15, 30, 38), (15, 39, 41), (15, 44, 46), (15, 47, 51),
    (16, 16, 18), (16, 31, 38), (16, 40, 41), (16, 44, 46), (16, 48, 50),
    (17, 18, 25), (17, 31, 37), (17, 40, 41), (17, 45, 46), (17, 48, 50),
    (18, 18, 25), (18, 31, 37), (18, 45, 45), (18, 48, 49),
    (19, 18, 24), (19, 32, 37), (19, 49, 53),
    (20, 19, 24), (20, 32, 36), (20, 50, 55),
    (21, 19, 23), (21, 32, 36), (21, 51, 54),
    (22, 19, 23), (22, 33, 36), (22, 52, 58),
    (23, 20, 23), (23, 33, 35), (23, 52, 59),
    (24, 20, 22), (24, 33, 35), (24, 52, 59),
    (25, 20, 22), (25, 33, 34), (25, 52, 58),
    (26, 20, 21), (26, 33, 34), (26, 53, 58), (26, 61, 62),
    (27, 20, 21), (27, 33, 34), (27, 53, 57), (27, 61, 62),
    (28, 20, 21), (28, 62, 62),
    (29, 20, 21), (29, 62, 62),
    (30, 20, 20),
]

# Story number -> (x, y) pin position on the 1024 canvas.
PINS = {
    1: (206, 861), 2: (218, 899), 3: (272, 905), 4: (72, 877),
    5: (114, 868), 6: (186, 928), 7: (201, 933), 8: (259, 865),
    9: (279, 880), 10: (191, 879), 11: (186, 863), 12: (246, 893),
    13: (203, 894), 14: (97, 887), 15: (243, 855),
}


def draw_map(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=SKY)
    d.rectangle([x0, y0, x1, y1], outline=GREY)
    land = set()
    for row, a, b in LAND_RUNS:
        for x in range(a, b + 1):
            land.add((row, x))
    for row, x in land:
        px = x0 + (x + 0.5) * (x1 - x0) / 64
        py = y0 + (row + 0.5) * (y1 - y0) / 32
        d.ellipse([px - 1.6, py - 1.6, px + 1.6, py + 1.6], fill=LAND)
    for num, (px, py) in PINS.items():
        badge(d, px, py, num, r=8)


# ---------------------------------------------------------------- layout

def draw_big_card(d, x, y, w, story):
    num, kicker, kcolor, head, summ, scene = story
    SCENES[scene](d, (x + 6, y + 6, x + w - 6, y + 90))
    badge(d, x + 17, y + 17, num, r=11)
    d.text((x + 6, y + 96), kicker, font=BOLD(13), fill=kcolor)
    para(d, x + 6, y + 112, head, BOLD(23), INK, w - 12, 26, max_lines=2)
    para(d, x + 6, y + 166, summ, REG(13), (58, 56, 50), w - 12, 16,
         max_lines=2)


def draw_small_card(d, x, y, w, story):
    num, kicker, kcolor, head, summ, scene = story
    SCENES[scene](d, (x + 6, y + 4, x + w - 6, y + 32))
    badge(d, x + 17, y + 18, num, r=10)
    d.text((x + 6, y + 36), kicker, font=BOLD(11), fill=kcolor)
    para(d, x + 6, y + 48, head, BOLD(17), INK, w - 12, 18, max_lines=2)
    para(d, x + 6, y + 86, summ, REG(12), (58, 56, 50), w - 12, 12.5,
         max_lines=2)


def draw_poster():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, H - 1], outline=INK, width=4)

    # Top strip: tagline left, story count right.
    d.text((24, 5), "THE WORLD\u2019S NEWS IN ONE PICTURE", font=BOLD(14),
           fill=RED)
    right = "43 STORIES \u00b7 6 CONTINENTS \u00b7 ALL FROM TUESDAY"
    d.text((W - 24 - d.textlength(right, font=BOLD(12)), 6), right,
           font=BOLD(12), fill=GREY)

    # Masthead.
    d.rectangle([4, 24, W - 5, 112], fill=NAVY)
    d.text((28, 42), "Tuesday 17 November 2026", font=SERIF(52),
           fill=LIGHT)
    d.line([28, 100, W - 28, 100], fill=GOLD, width=2)

    # Figures ticker.
    d.rectangle([4, 112, W - 5, 136], fill=RED)
    tsize = 15
    while d.textlength(TICKER, font=BOLD(tsize)) > W - 48 and tsize > 10:
        tsize -= 1
    tw = d.textlength(TICKER, font=BOLD(tsize))
    d.text(((W - tw) / 2, 118), TICKER, font=BOLD(tsize), fill=LIGHT)

    # Three big leads.
    cols = [24, 354, 684]
    for i, story in enumerate(FEATURED[:3]):
        draw_big_card(d, cols[i], 136, 316, story)

    # Twelve more stories, four rows of three.
    for r in range(4):
        for c in range(3):
            story = FEATURED[3 + r * 3 + c]
            draw_small_card(d, cols[c], 346 + r * 112, 316, story)

    # Bottom: map left, also-list right.
    d.text((24, 796), "WHERE IT HAPPENED", font=BOLD(14), fill=NAVY)
    d.text((336, 796), "ALSO ON TUESDAY 17 NOVEMBER", font=BOLD(14),
           fill=RED)
    d.line([24, 814, 320, 814], fill=INK, width=1)
    d.line([336, 814, 1000, 814], fill=INK, width=1)
    draw_map(d, 24, 820, 320, 994)

    for col in range(2):
        items = ALSO[col * 14:(col + 1) * 14]
        x = 336 + col * 332
        for i, item in enumerate(items):
            yy = 822 + i * 12.6
            n = 16 + col * 14 + i
            d.text((x, yy), str(n), font=BOLD(11), fill=RED)
            d.text((x + 22, yy), item, font=REG(11.5), fill=INK)

    # Footer.
    d.line([24, 998, 1000, 998], fill=GREY, width=1)
    d.text((24, 1000),
           "Every story here happened or was first reported on Tuesday "
           "17 November 2026. Disputed claims are attributed.",
           font=REG(11), fill=GREY)
    d.text((24, 1011),
           "Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 Al "
           "Jazeera \u00b7 UN News \u00b7 WHO. Original drawings.",
           font=REG(11), fill=GREY)
    return img


if __name__ == "__main__":
    poster = draw_poster()
    poster.save("entry.png", format="PNG", optimize=True)
    print("wrote entry.png", poster.size)

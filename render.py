"""Render the 17 November 2026 world-news poster, v3 (1024x1024 PNG).

Theory: MAXIMUM DENSITY. The densest legible front page possible:
24 illustrated mini-cards in a 6x4 grid plus a 36-item also-list,
a dotted world map and a figures box — 60 stories in all. Same news
as v2 (verified 17 Nov 2026), plus extra items corroborated from the
day's digests. Deterministic: no random numbers, no clock, no network.
Run: python3 render.py
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (250, 246, 236)
INK = (24, 24, 24)
NAVY = (16, 30, 58)
RED = (176, 30, 30)
GOLD = (206, 158, 60)
GREY = (100, 96, 88)
BLUE = (28, 88, 138)
TEAL = (12, 102, 102)
GREEN = (32, 106, 68)
PURPLE = (88, 54, 136)
SKY = (216, 230, 238)
SAND = (212, 192, 152)
LIGHT = (255, 255, 255)
FAINT = (58, 56, 50)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"


def load(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


SERIF = lambda s: load("DejaVuSerif-Bold.ttf", s)
BOLD = lambda s: load("DejaVuSans-Bold.ttf", s)
PLAIN = lambda s: load("DejaVuSans.ttf", s)


def split_words(draw, text, fnt, max_w):
    """Greedy wrap; returns list of lines."""
    out, cur = [], ""
    for word in text.split():
        nxt = (cur + " " + word).strip()
        if draw.textlength(nxt, font=fnt) <= max_w:
            cur = nxt
        else:
            if cur:
                out.append(cur)
            cur = word
    if cur:
        out.append(cur)
    return out


def block(draw, x, y, text, fnt, color, max_w, leading, cap=None):
    """Draw wrapped paragraph, optionally capped with an ellipsis."""
    lines = split_words(draw, text, fnt, max_w)
    if cap is not None and len(lines) > cap:
        lines = lines[:cap]
        while lines and draw.textlength(lines[-1] + "...", font=fnt) > max_w:
            lines[-1] = lines[-1][:-1]
        lines[-1] = lines[-1].rstrip() + "..."
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=color)
        y += leading
    return y


def disc(draw, cx, cy, num, r=9):
    """Numbered red disc centred at (cx, cy)."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
    t = str(num)
    f = BOLD(12 if len(t) < 2 else 10)
    tw = draw.textlength(t, font=f)
    draw.text((cx - tw / 2, cy - 7 if len(t) < 2 else cy - 6), t,
              font=f, fill=LIGHT)


# ------------------------------------------------------------------ stories
# (number, kicker, kicker colour, headline, summary, scene key)
FEATURED = [
    (1, "EUROPE · UKRAINE WAR", BLUE,
     "Kerch Bridge span falls into the sea",
     "Second strike in two days; Zelensky hails an \u2018unprecedented "
     "operation\u2019.", "bridge"),
    (2, "MIDDLE EAST · IRAN WAR", RED,
     "Iran fires drones at US radar base in Bahrain",
     "Bahrain says all were downed; US jets strike Qeshm; a fourth "
     "tanker is hit by a mine.", "gulf"),
    (3, "ASIA · DIPLOMACY", TEAL,
     "Trump in Manila; summit on Thursday",
     "Quad agrees critical-minerals deals; Xi, Trump, Putin meet in "
     "Shenzhen \u2014 a first.", "flags"),
    (4, "US · MARKETS", GREEN,
     "Nvidia posts record $115.8bn quarter",
     "Sales roughly doubled in a year; first since Huang quit; board "
     "won\u2019t reinstate him.", "chip"),
    (5, "US · BANKING", NAVY,
     "JPMorgan outage cuts Zelle users off for hours",
     "Bank blames a software bug and says it was not a cyberattack.",
     "bank"),
    (6, "AFRICA · HEALTH", PURPLE,
     "Ebola in DR Congo passes 11,000 cases",
     "More than 5,400 dead, the UN says; cases have more than doubled "
     "in three months.", "virus"),
    (7, "EUROPE · MIGRATION", BLUE,
     "Five EU states plan a Rwanda asylum hub",
     "First transfers aimed for 2027; UN rights chief raises concerns.",
     "house"),
    (8, "ASIA · POLITICS", TEAL,
     "Mongolia\u2019s president says he will resign",
     "Khurelsukh denies a $25m bribe claim; parliament must accept.",
     "door"),
    (9, "ASIA · DEFENCE", RED,
     "Japan scrambles jets at Russian incursion",
     "Two planes entered airspace near Okinoshima; Tokyo protests, "
     "first since 2024.", "jets"),
    (10, "GLOBAL · CLIMATE", TEAL,
     "COP31 split over fossil-fuel phase-out",
     "Draft deal calls for $120bn a year in climate finance; talks end "
     "Friday.", "globe"),
    (11, "EUROPE · POLITICS", BLUE,
     "Serbia\u2019s student-led majority takes its seats",
     "Student List holds 140 of 250; Vu\u010di\u0107\u2019s party goes into "
     "opposition.", "parliament"),
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
    (16, "US · POLITICS", NAVY,
     "Pentagon fails its audit for a ninth straight year",
     "The Defence Department cannot account for its books again.",
     "ledger"),
    (17, "US · COURTS", RED,
     "Expert: Epstein death was murder, not suicide",
     "Forensic review of the medical examiner\u2019s file, he says.",
     "gavel"),
    (18, "ISRAEL · POLITICS", BLUE,
     "Eisenkot wins Knesset speaker vote, 66\u201352",
     "Kahana of his Yashar party takes the chair; E1 tender halted.",
     "ballot"),
    (19, "YEMEN · WAR", RED,
     "Houthis push army back from Red Sea coast",
     "Government troops fall back to defend Aden; Saudi strike kills "
     "seven in Hudaydah.", "ship"),
    (20, "ASIA · WEATHER", TEAL,
     "Cyclone Akvan nears India; Odisha evacuates",
     "Storms and floods threaten the east coast; bus crash kills 8 in "
     "Uttarakhand.", "storm"),
    (21, "ASIA · TECH", GREEN,
     "Singapore seeks trusted access to AI chips",
     "Wants US assurances after new export curbs on data-centre sales.",
     "satellite"),
    (22, "EUROPE · STRIKES", BLUE,
     "France faces second nationwide strike in a week",
     "Unions demand higher wages; 146,000 marched on Saturday.",
     "protest"),
    (23, "GLOBAL · ENERGY", GREEN,
     "Oil torn between Mideast exports and tanker attacks",
     "Prices waver as a fourth tanker is mined in the Strait of Hormuz.",
     "oil"),
    (24, "US · TECH", NAVY,
     "FEMA tests the emergency alert nationwide",
     "One-minute TV and radio test at 2:20pm ET; phones excluded.",
     "antenna"),
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
    "Israeli AG halts E1 settlement tender",
    "West Bank: settlers kill a woman, 72",
    "Oman: Iran\u2019s Araghchi holds shipping talks",
    "India: bus falls into gorge, 8 dead",
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
    "Depardieu drops appeal, admits sex assault charge",
    "Iraq militia warns troops over Jurf al-Sakhar",
    "Trump team seeks Kim meeting at APEC",
    "EU charges Temu over illegal product sales",
    "Le Pen promises earlier retirement if elected",
    "Stocks fall with Nvidia in focus; dollar dips",
    "Websites hacked to steal crypto, target iPhones",
    "South Florida flood watch: up to 10 in of rain",
    "Pope Leo struck near eye by object in Peru",
    "China seeks Asia-Pacific cooperation blueprint",
]

TICKER = ("DOW \u2212849 (\u22121.6%) \u00b7 NVIDIA $115.8BN RECORD \u00b7 "
          "EBOLA 11,000+ CASES \u00b7 1,441 DRONES DOWNED \u00b7 "
          "TRUMP\u2013XI\u2013PUTIN SUMMIT THU")

FIGURES = [
    ("1,441", "drones downed over Crimea"),
    ("$115.8bn", "Nvidia\u2019s record quarter"),
    ("11,000+", "Ebola cases in DR Congo"),
    ("146,000", "march in France\u2019s protests"),
    ("$120bn", "COP31 climate finance ask"),
    ("5,400+", "Ebola deaths, UN says"),
]

# ------------------------------------------------------------------ scenes
# Each painter draws a flat mini-illustration inside box (x0, y0, x1, y1).
# u(f)/v(f) map 0..1 fractions of the box to pixels.


def _fr(box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    return (lambda f: x0 + f * w), (lambda f: y0 + f * h), w, h


def s_bridge(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(186, 214, 232))
    d.rectangle([box[0], v(0.62), box[2], box[3]], fill=(70, 124, 162))
    lw = max(2, int(h / 10))
    d.rectangle([u(0.06), v(0.58), u(0.44), v(0.66)], fill=INK)
    d.rectangle([u(0.56), v(0.58), u(0.94), v(0.66)], fill=INK)
    d.rectangle([u(0.14), v(0.30), u(0.17), v(0.62)], fill=INK)
    d.rectangle([u(0.83), v(0.30), u(0.86), v(0.62)], fill=INK)
    d.line([u(0.155), v(0.30), u(0.50), v(0.62)], fill=INK, width=max(1, lw // 2))
    d.line([u(0.845), v(0.30), u(0.50), v(0.62)], fill=INK, width=max(1, lw // 2))
    d.polygon([(u(0.47), v(0.62)), (u(0.50), v(0.44)), (u(0.53), v(0.62))],
              fill=(228, 116, 40))
    d.ellipse([u(0.60), v(0.70), u(0.68), v(0.78)], fill=LIGHT)


def s_gulf(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(236, 218, 172))
    d.polygon([(u(0.04), v(0.28)), (u(0.70), v(0.12)), (u(0.96), v(0.30)),
               (u(0.96), v(0.96)), (u(0.10), v(0.96)), (u(0.04), v(0.66))],
              fill=(104, 166, 202))
    d.line([u(0.12), v(0.36), u(0.58), v(0.52), u(0.84), v(0.82)],
           fill=RED, width=max(1, int(h / 12)))
    for fx, fy in ((0.20, 0.46), (0.58, 0.54)):
        r = max(2, h * 0.10)
        d.line([u(fx) - r, v(fy) - r, u(fx) + r, v(fy) + r], fill=RED,
               width=max(2, int(h / 11)))
        d.line([u(fx) - r, v(fy) + r, u(fx) + r, v(fy) - r], fill=RED,
               width=max(2, int(h / 11)))
    d.ellipse([u(0.86), v(0.78), u(0.94), v(0.86)], fill=(240, 150, 40))
    d.ellipse([u(0.88), v(0.80), u(0.92), v(0.84)], fill=RED)


def s_flags(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(228, 234, 240))
    for i, (c1, c2) in enumerate((((178, 34, 34), (255, 255, 255)),
                                  ((222, 32, 32), (255, 215, 0)),
                                  ((255, 255, 255), (31, 93, 140)))):
        cx = u(0.17 + i * 0.33)
        d.line([cx, v(0.16), cx, v(0.92)], fill=INK, width=max(1, int(h / 15)))
        fx0, fy0 = cx - w * 0.10, v(0.16)
        fw, fh = w * 0.20, h * 0.50
        d.rectangle([fx0, fy0, fx0 + fw, fy0 + fh], fill=c1)
        if i == 0:
            for s in range(3):
                d.line([fx0, fy0 + fh * (0.25 + s * 0.25),
                        fx0 + fw, fy0 + fh * (0.25 + s * 0.25)],
                       fill=c2, width=max(1, int(h / 17)))
            d.rectangle([fx0, fy0, fx0 + fw * 0.38, fy0 + fh * 0.45],
                        fill=(18, 32, 62))
        elif i == 1:
            for sx, sy in ((0.25, 0.30), (0.55, 0.25), (0.50, 0.60)):
                d.ellipse([fx0 + fw * sx - 2, fy0 + fh * sy - 2,
                           fx0 + fw * sx + 2, fy0 + fh * sy + 2], fill=c2)
        else:
            d.rectangle([fx0, fy0 + fh * 0.35, fx0 + fw, fy0 + fh * 0.68],
                        fill=c2)
            d.rectangle([fx0, fy0 + fh * 0.68, fx0 + fw, fy0 + fh],
                        fill=(178, 34, 34))


def s_chip(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(20, 58, 42))
    cx, cy = u(0.30), v(0.50)
    s = h * 0.40
    for i in range(3):
        t = u(0.15 + i * 0.06)
        d.line([t, v(0.08), t, v(0.22)], fill=GOLD, width=max(1, int(h / 13)))
        d.line([t, v(0.78), t, v(0.92)], fill=GOLD, width=max(1, int(h / 13)))
    d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=GREEN)
    d.rectangle([cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2],
                outline=GOLD, width=max(1, int(h / 15)))
    for i, fh in enumerate((0.28, 0.52, 0.40, 0.68)):
        bx = u(0.58 + i * 0.09)
        d.rectangle([bx, v(0.92 - fh), bx + w * 0.05, v(0.92)],
                    fill=(120, 220, 130))


def s_bank(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(228, 234, 240))
    cx = u(0.50)
    d.polygon([(cx - w * 0.16, v(0.30)), (cx + w * 0.16, v(0.30)),
               (cx, v(0.08))], fill=NAVY)
    for i in range(4):
        px = cx - w * 0.13 + i * w * 0.087
        d.rectangle([px - max(1, w * 0.012), v(0.34),
                     px + max(1, w * 0.012), v(0.86)], fill=NAVY)
    d.rectangle([u(0.30), v(0.86), u(0.70), v(0.94)], fill=NAVY)
    d.line([cx - w * 0.05, v(0.40), cx + w * 0.05, v(0.40)], fill=RED,
           width=max(1, int(h / 11)))


def s_virus(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(240, 228, 242))
    cx, cy = u(0.50), v(0.50)
    r = h * 0.40
    for i in range(8):
        a = math.pi * i / 4
        d.line([cx + r * 0.85 * math.cos(a), cy + r * 0.85 * math.sin(a),
                cx + r * 1.15 * math.cos(a), cy + r * 1.15 * math.sin(a)],
               fill=PURPLE, width=max(1, int(h / 11)))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=PURPLE)
    d.ellipse([cx - r * 0.35, cy - r * 0.35, cx + r * 0.35, cy + r * 0.35],
              fill=GOLD)


def s_house(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(234, 230, 216))
    cx = u(0.50)
    d.polygon([(cx - w * 0.16, v(0.52)), (cx + w * 0.16, v(0.52)),
               (cx, v(0.14))], fill=RED)
    d.rectangle([cx - w * 0.12, v(0.52), cx + w * 0.12, v(0.92)],
                fill=LIGHT, outline=NAVY, width=max(1, int(h / 13)))
    d.rectangle([cx - w * 0.03, v(0.62), cx + w * 0.03, v(0.92)], fill=BLUE)
    d.rectangle([u(0.82), v(0.18), u(0.94), v(0.50)], fill=TEAL)
    d.text((u(0.845), v(0.24)), "27", font=BOLD(max(8, int(h * 0.24))),
           fill=LIGHT)


def s_door(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(228, 234, 240))
    d.rectangle([u(0.10), v(0.14), u(0.30), v(0.90)], outline=NAVY,
                width=max(1, int(h / 11)))
    d.line([u(0.40), v(0.50), u(0.86), v(0.50)], fill=GREEN,
           width=max(2, int(h / 8)))
    d.polygon([(u(0.86), v(0.50)), (u(0.74), v(0.32)), (u(0.74), v(0.68))],
              fill=GREEN)
    d.text((u(0.13), v(0.22)), "EXIT", font=BOLD(max(8, int(h * 0.24))),
           fill=NAVY)


def s_jets(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(208, 224, 238))
    for fx, fy, c in ((0.18, 0.30, (90, 90, 90)), (0.42, 0.62, RED)):
        ox, oy = u(fx), v(fy)
        s = w * 0.055
        d.polygon([(ox, oy), (ox + s * 1.6, oy + s * 0.3),
                   (ox, oy + s * 0.6)], fill=c)
        d.polygon([(ox + s * 0.4, oy + s * 0.1), (ox + s * 0.8, oy - s * 0.3),
                   (ox + s * 1.0, oy + s * 0.1)], fill=c)
    for i in range(4):
        r = max(1, h * 0.04)
        d.ellipse([u(0.08 + i * 0.03) - r, v(0.86 - i * 0.09) - r,
                   u(0.08 + i * 0.03) + r, v(0.86 - i * 0.09) + r], fill=GREY)


def s_globe(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(216, 234, 228))
    cx, cy = u(0.42), v(0.50)
    r = h * 0.42
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=TEAL,
              width=max(1, int(h / 11)))
    d.ellipse([cx - r * 0.4, cy - r, cx + r * 0.4, cy + r], outline=TEAL,
              width=max(1, int(h / 15)))
    d.line([cx - r, cy, cx + r, cy], fill=TEAL, width=max(1, int(h / 15)))
    d.rectangle([u(0.82), v(0.10), u(0.88), v(0.90)], outline=RED,
                width=max(1, int(h / 15)))
    d.ellipse([u(0.85) - r * 0.16, v(0.14) - r * 0.16,
               u(0.85) + r * 0.16, v(0.14) + r * 0.16], fill=RED)
    d.line([u(0.85), v(0.14), u(0.85), v(0.86)], fill=RED,
           width=max(1, int(h / 15)))


def s_parliament(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(234, 230, 242))
    cx, cy = u(0.50), v(0.92)
    for i in range(9):
        a = math.pi * (i + 1) / 10
        px, py = cx + w * 0.16 * math.cos(a), cy - h * 0.62 * math.sin(a)
        r = max(2, h * 0.07)
        d.ellipse([px - r, py - r, px + r, py + r], fill=BLUE)
    r = max(2, h * 0.08)
    d.ellipse([cx - r, cy - h * 0.70 - r, cx + r, cy - h * 0.70 + r],
              fill=RED)
    d.rectangle([cx - w * 0.09, cy - h * 0.10, cx + w * 0.09, cy], fill=NAVY)


def s_factory(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(230, 232, 228))
    d.rectangle([u(0.08), v(0.48), u(0.86), v(0.92)], fill=(150, 150, 150))
    d.polygon([(u(0.08), v(0.48)), (u(0.16), v(0.30)), (u(0.24), v(0.48)),
               (u(0.32), v(0.30)), (u(0.40), v(0.48))], fill=(120, 120, 120))
    d.rectangle([u(0.74), v(0.16), u(0.82), v(0.48)], fill=(120, 120, 120))
    for fx, fy in ((0.78, 0.10), (0.84, 0.04)):
        r = max(2, h * 0.07)
        d.ellipse([u(fx) - r, v(fy) - r * 0.8, u(fx) + r, v(fy) + r * 0.8],
                  fill=(180, 180, 180))
    for i in range(3):
        d.rectangle([u(0.14 + i * 0.10), v(0.60),
                     u(0.20 + i * 0.10), v(0.78)], fill=GOLD)


def s_tents(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(234, 228, 216))
    for fx in (0.22, 0.52):
        tx = u(fx)
        d.polygon([(tx - w * 0.11, v(0.90)), (tx + w * 0.11, v(0.90)),
                   (tx, v(0.34))], fill=LIGHT, outline=RED,
                  width=max(1, int(h / 13)))
        d.line([tx, v(0.34), tx, v(0.90)], fill=RED, width=1)
    d.rectangle([u(0.80), v(0.16), u(0.92), v(0.48)], fill=LIGHT)
    d.rectangle([u(0.83), v(0.26), u(0.89), v(0.38)], fill=RED)
    d.rectangle([u(0.845), v(0.29), u(0.875), v(0.35)], fill=LIGHT)


def s_spots(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(240, 228, 230))
    cx, cy = u(0.50), v(0.50)
    r = h * 0.42
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(242, 205, 170))
    for fx, fy, fr in ((-0.28, -0.20, 0.13), (0.22, -0.30, 0.10),
                       (0.08, 0.14, 0.13), (-0.34, 0.26, 0.10),
                       (0.34, 0.30, 0.08)):
        d.ellipse([cx + fx * r - fr * r, cy + fy * r - fr * r,
                   cx + fx * r + fr * r, cy + fy * r + fr * r], fill=RED)


def s_plane(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(208, 224, 238))
    s = w * 0.10
    d.polygon([(u(0.10), v(0.42)), (u(0.10) + s * 2.2, v(0.50)),
               (u(0.10), v(0.58))], fill=NAVY)
    d.polygon([(u(0.10) + s * 0.8, v(0.44)), (u(0.10) + s * 1.1, v(0.16)),
               (u(0.10) + s * 1.3, v(0.44))], fill=NAVY)
    d.polygon([(u(0.10) + s * 0.9, v(0.56)), (u(0.10) + s * 1.2, v(0.84)),
               (u(0.10) + s * 1.4, v(0.56))], fill=NAVY)
    for fx, fy in ((0.62, 0.54), (0.72, 0.58), (0.82, 0.62)):
        r = max(2, h * 0.09)
        d.ellipse([u(fx) - r, v(fy) - r * 0.8, u(fx) + r, v(fy) + r * 0.8],
                  fill=(120, 120, 120))
    d.line([u(0.06), v(0.92), u(0.94), v(0.92)], fill=GREY,
           width=max(1, int(h / 13)))


def s_ledger(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(232, 228, 214))
    d.rectangle([u(0.16), v(0.14), u(0.84), v(0.88)], fill=LIGHT,
                outline=NAVY, width=max(1, int(h / 13)))
    for i in range(4):
        yy = v(0.28 + i * 0.15)
        d.line([u(0.24), yy, u(0.62), yy], fill=GREY, width=max(1, int(h / 16)))
    d.line([u(0.70), v(0.28), u(0.70), v(0.73)], fill=GREY,
           width=max(1, int(h / 16)))
    for i in range(4):
        yy = v(0.28 + i * 0.15)
        d.line([u(0.72), yy, u(0.78), yy], fill=RED, width=max(1, int(h / 13)))
    d.text((u(0.24), v(0.76)), "?", font=BOLD(max(8, int(h * 0.30))),
           fill=RED)


def s_gavel(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(228, 222, 206))
    d.rectangle([u(0.20), v(0.30), u(0.80), v(0.48)], fill=(120, 82, 40))
    d.rectangle([u(0.30), v(0.48), u(0.70), v(0.56)], fill=(90, 60, 28))
    d.line([u(0.50), v(0.56), u(0.50), v(0.86)], fill=(90, 60, 28),
           width=max(2, int(h / 10)))
    d.ellipse([u(0.38), v(0.84), u(0.62), v(0.94)], fill=(120, 82, 40))
    d.text((u(0.14), v(0.12)), "\u00a7", font=BOLD(max(8, int(h * 0.30))),
           fill=NAVY)


def s_ballot(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(228, 234, 240))
    d.rectangle([u(0.30), v(0.34), u(0.70), v(0.90)], fill=LIGHT,
                outline=NAVY, width=max(1, int(h / 13)))
    d.line([u(0.30), v(0.34), u(0.70), v(0.34)], fill=NAVY,
           width=max(1, int(h / 10)))
    for i in range(3):
        yy = v(0.46 + i * 0.13)
        d.rectangle([u(0.36), yy, u(0.44), yy + h * 0.07], outline=GREY,
                    width=max(1, int(h / 16)))
        d.line([u(0.48), yy + h * 0.035, u(0.64), yy + h * 0.035],
               fill=GREY, width=max(1, int(h / 18)))
    d.line([u(0.37), v(0.50), u(0.40), v(0.54), u(0.43), v(0.47)],
           fill=RED, width=max(2, int(h / 10)))
    d.text((u(0.74), v(0.44)), "66", font=BOLD(max(8, int(h * 0.28))),
           fill=RED)
    d.text((u(0.74), v(0.66)), "52", font=BOLD(max(8, int(h * 0.28))),
           fill=BLUE)


def s_ship(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(208, 224, 238))
    d.rectangle([box[0], v(0.66), box[2], box[3]], fill=(70, 124, 162))
    d.polygon([(u(0.10), v(0.66)), (u(0.90), v(0.66)), (u(0.80), v(0.80)),
               (u(0.20), v(0.80))], fill=(60, 60, 60))
    d.rectangle([u(0.55), v(0.44), u(0.72), v(0.66)], fill=(200, 200, 200))
    d.rectangle([u(0.58), v(0.36), u(0.62), v(0.44)], fill=(60, 60, 60))
    for fx in (0.16, 0.30):
        r = max(2, h * 0.08)
        d.ellipse([u(fx) - r, v(0.20) - r, u(fx) + r, v(0.20) + r],
                  fill=(240, 150, 40))
    d.line([u(0.82), v(0.16), u(0.88), v(0.34)], fill=RED,
           width=max(1, int(h / 12)))


def s_storm(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(206, 220, 234))
    d.rectangle([box[0], v(0.58), box[2], box[3]], fill=(70, 124, 162))
    cx, cy = u(0.30), v(0.30)
    r = h * 0.42
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(60, 60, 60),
              width=max(1, int(h / 12)))
    d.ellipse([cx - r * 0.55, cy - r * 0.55, cx + r * 0.55, cy + r * 0.55],
              outline=(60, 60, 60), width=max(1, int(h / 12)))
    d.ellipse([cx - r * 0.18, cy - r * 0.18, cx + r * 0.18, cy + r * 0.18],
              fill=(240, 220, 120))
    for fx in (0.55, 0.68, 0.81, 0.94):
        d.arc([u(fx) - w * 0.05, v(0.62), u(fx) + w * 0.05, v(0.86)],
              180, 360, fill=LIGHT, width=max(1, int(h / 12)))


def s_satellite(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(96, 128, 168))
    cx, cy = u(0.50), v(0.46)
    d.rectangle([cx - w * 0.09, cy - h * 0.14, cx + w * 0.09, cy + h * 0.14],
                fill=(240, 240, 240))
    d.polygon([(cx - w * 0.32, cy - h * 0.08), (cx - w * 0.11, cy - h * 0.08),
               (cx - w * 0.11, cy + h * 0.08), (cx - w * 0.32, cy + h * 0.08)],
              fill=(31, 93, 140))
    d.polygon([(cx + w * 0.11, cy - h * 0.08), (cx + w * 0.32, cy - h * 0.08),
               (cx + w * 0.32, cy + h * 0.08), (cx + w * 0.11, cy + h * 0.08)],
              fill=(31, 93, 140))
    for sx, sy in ((-0.30, -0.30), (0.34, 0.28), (-0.34, 0.30)):
        d.ellipse([u(0.50 + sx) - 2, v(0.46 + sy) - 2,
                   u(0.50 + sx) + 2, v(0.46 + sy) + 2], fill=GOLD)
    d.line([cx, cy + h * 0.14, cx, v(0.86)], fill=GOLD,
           width=max(1, int(h / 14)))


def s_protest(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(234, 228, 216))
    for i, fx in enumerate((0.20, 0.38, 0.56, 0.74)):
        px = u(fx)
        d.ellipse([px - w * 0.035, v(0.30), px + w * 0.035, v(0.40)],
                  fill=INK)
        d.rectangle([px - w * 0.02, v(0.40), px + w * 0.02, v(0.78)],
                    fill=INK)
        d.line([px, v(0.78), px - w * 0.04, v(0.92)], fill=INK,
               width=max(1, int(h / 16)))
        d.line([px, v(0.78), px + w * 0.04, v(0.92)], fill=INK,
               width=max(1, int(h / 16)))
        if i % 2 == 0:
            d.rectangle([u(fx - 0.10), v(0.14), u(fx + 0.10), v(0.26)],
                        fill=RED)
    d.line([u(0.06), v(0.94), u(0.94), v(0.94)], fill=GREY,
           width=max(1, int(h / 14)))


def s_oil(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(228, 224, 210))
    d.rectangle([u(0.14), v(0.40), u(0.34), v(0.88)], fill=(60, 60, 60))
    d.polygon([(u(0.14), v(0.40)), (u(0.24), v(0.16)), (u(0.34), v(0.40))],
              fill=(60, 60, 60))
    d.line([u(0.44), v(0.30), u(0.78), v(0.30)], fill=INK,
           width=max(1, int(h / 12)))
    d.line([u(0.78), v(0.30), u(0.78), v(0.88)], fill=INK,
           width=max(1, int(h / 12)))
    d.line([u(0.52), v(0.30), u(0.52), v(0.44)], fill=INK,
           width=max(1, int(h / 14)))
    d.ellipse([u(0.62), v(0.52), u(0.72), v(0.62)], fill=RED)
    d.ellipse([u(0.80), v(0.66), u(0.88), v(0.74)], fill=GOLD)


def s_antenna(d, box):
    u, v, w, h = _fr(box)
    d.rectangle(box, fill=(216, 230, 238))
    cx = u(0.50)
    d.line([cx, v(0.86), cx, v(0.16)], fill=INK, width=max(2, int(h / 10)))
    for i in range(3):
        yy = v(0.30 + i * 0.16)
        d.line([cx - w * (0.05 + i * 0.05), yy, cx + w * (0.05 + i * 0.05),
                yy], fill=INK, width=max(1, int(h / 14)))
    for a, c in ((-0.45, RED), (0.45, RED), (-0.28, GOLD), (0.28, GOLD)):
        px, py = cx + a * w * 0.5, v(0.14)
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=c)
    d.rectangle([u(0.30), v(0.86), u(0.70), v(0.94)], fill=NAVY)


SCENES = {
    "bridge": s_bridge, "gulf": s_gulf, "flags": s_flags, "chip": s_chip,
    "bank": s_bank, "virus": s_virus, "house": s_house, "door": s_door,
    "jets": s_jets, "globe": s_globe, "parliament": s_parliament,
    "factory": s_factory, "tents": s_tents, "spots": s_spots,
    "plane": s_plane, "ledger": s_ledger, "gavel": s_gavel,
    "ballot": s_ballot, "ship": s_ship, "storm": s_storm,
    "satellite": s_satellite, "protest": s_protest, "oil": s_oil,
    "antenna": s_antenna,
}

# ---------------------------------------------------------------- world map
# Continents as ellipses in (lon, lat); dots sampled on a 4-degree grid.
CONTINENTS = [
    (-100, 48, 36, 20), (-155, 64, 12, 8), (-90, 15, 12, 6),
    (-42, 74, 10, 6), (-60, -10, 14, 24),
    (12, 52, 16, 10), (18, 2, 18, 28), (100, 48, 50, 18),
    (112, -2, 16, 7), (134, -25, 15, 9),
]

# story number -> (lon, lat)
PINS = {
    1: (33.5, 45.3), 2: (50.5, 26.2), 3: (121.0, 14.6), 4: (-121.9, 37.4),
    5: (-74.0, 40.7), 6: (23.0, -2.9), 7: (30.0, -2.0), 8: (106.9, 47.9),
    9: (132.0, 34.0), 10: (30.7, 36.9), 11: (20.9, 44.8), 12: (90.4, 23.8),
}


def draw_map(d, x0, y0, x1, y1):
    d.rectangle([x0, y0, x1, y1], fill=SKY)
    d.rectangle([x0, y0, x1, y1], outline=GREY)
    lon0, lon1, lat0, lat1 = -180.0, 180.0, 75.0, -55.0

    def px(lon):
        return x0 + (lon - lon0) / (lon1 - lon0) * (x1 - x0)

    def py(lat):
        return y0 + (lat0 - lat) / (lat0 - lat1) * (y1 - y0)

    lon = -180.0
    while lon <= 180.0:
        lat = -56.0
        while lat <= 76.0:
            inside = False
            for cx, cy, rx, ry in CONTINENTS:
                if ((lon - cx) / rx) ** 2 + ((lat - cy) / ry) ** 2 <= 1.0:
                    inside = True
                    break
            if inside:
                d.ellipse([px(lon) - 1.8, py(lat) - 1.8,
                           px(lon) + 1.8, py(lat) + 1.8], fill=SAND)
            lat += 4.0
        lon += 4.0
    for num, (lon, lat) in PINS.items():
        disc(d, px(lon), py(lat), num, r=7)


# ---------------------------------------------------------------- layout

def mini_card(d, x, y, w, h, story):
    num, kicker, kcolor, head, summ, scene = story
    SCENES[scene](d, (x + 4, y + 3, x + w - 4, y + 29))
    disc(d, x + 13, y + 16, num, r=9)
    d.text((x + 4, y + 33), kicker, font=BOLD(9), fill=kcolor)
    block(d, x + 4, y + 44, head, BOLD(13), INK, w - 8, 14, cap=2)
    block(d, x + 4, y + 74, summ, PLAIN(9.5), FAINT, w - 8, 11, cap=2)


def draw_poster():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, H - 1], outline=INK, width=4)

    # Top strip.
    d.text((16, 5), "THE WORLD\u2019S NEWS IN ONE PICTURE", font=BOLD(13),
           fill=RED)
    right = "60 STORIES \u00b7 6 CONTINENTS \u00b7 ALL FROM TUESDAY"
    d.text((W - 16 - d.textlength(right, font=BOLD(11)), 6), right,
           font=BOLD(11), fill=GREY)

    # Masthead.
    d.rectangle([4, 22, W - 5, 100], fill=NAVY)
    d.text((24, 36), "Tuesday 17 November 2026", font=SERIF(46),
           fill=LIGHT)
    d.line([24, 90, W - 24, 90], fill=GOLD, width=2)

    # Figures ticker.
    d.rectangle([4, 100, W - 5, 122], fill=RED)
    ts = 14
    while d.textlength(TICKER, font=BOLD(ts)) > W - 40 and ts > 9:
        ts -= 1
    tw = d.textlength(TICKER, font=BOLD(ts))
    d.text(((W - tw) / 2, 106), TICKER, font=BOLD(ts), fill=LIGHT)

    # 24 mini-cards, 6 columns x 4 rows.
    cw, ch, gx, gy = 158, 104, 8, 8
    x0, y0 = 18, 130
    for i, story in enumerate(FEATURED):
        cx = x0 + (i % 6) * (cw + gx)
        cy = y0 + (i // 6) * (ch + gy)
        mini_card(d, cx, cy, cw, ch, story)

    # Section headers.
    d.text((16, 578), "WHERE IT HAPPENED", font=BOLD(14), fill=NAVY)
    d.text((350, 578), "ALSO ON TUESDAY 17 NOVEMBER", font=BOLD(14),
           fill=RED)
    d.line([16, 596, 330, 596], fill=INK, width=1)
    d.line([350, 596, 1008, 596], fill=INK, width=1)

    # Map left, also-list right (2 columns x 18).
    draw_map(d, 16, 604, 330, 784)
    for col in range(2):
        items = ALSO[col * 18:(col + 1) * 18]
        x = 350 + col * 330
        for i, item in enumerate(items):
            yy = 606 + i * 20.5
            n = 25 + col * 18 + i
            d.text((x, yy), str(n), font=BOLD(12), fill=RED)
            d.text((x + 24, yy), item, font=PLAIN(12), fill=INK)

    # Figures box under the map.
    d.rectangle([16, 796, 330, 994], outline=GREY)
    d.text((28, 804), "BY THE NUMBERS", font=BOLD(13), fill=NAVY)
    for i, (fig, label) in enumerate(FIGURES):
        yy = 830 + i * 27
        d.text((28, yy), fig, font=BOLD(14), fill=RED)
        d.text((104, yy + 1), label, font=PLAIN(11.5), fill=INK)

    # Footer.
    d.line([16, 1002, 1008, 1002], fill=GREY, width=1)
    d.text((16, 1006),
           "Every story here happened or was first reported on Tuesday "
           "17 November 2026. Disputed claims are attributed.",
           font=PLAIN(10.5), fill=GREY)
    d.text((16, 1017),
           "Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 BBC \u00b7 Al "
           "Jazeera \u00b7 UN News \u00b7 WHO. Original drawings.",
           font=PLAIN(10.5), fill=GREY)
    return img


if __name__ == "__main__":
    poster = draw_poster()
    poster.save("entry.png", format="PNG", optimize=True)
    print("wrote entry.png", poster.size)

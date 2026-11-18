"""Render the 17 November 2026 world-news poster, v4 (1024x1024 PNG).

Theory: HERO-LED. The opposite of density: one huge dramatic lead
illustration, six big stories with large headlines and large pictures,
and a short also-line — 13 stories, maximum visual impact and maximum
readability at small size. Same verified 17 Nov 2026 news as v2.
Deterministic: no random numbers, no clock, no network.
Run: python3 render.py
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 244, 234)
INK = (22, 22, 22)
NAVY = (14, 28, 54)
RED = (178, 32, 32)
GOLD = (212, 164, 62)
GREY = (98, 94, 86)
BLUE = (30, 90, 138)
TEAL = (12, 104, 104)
GREEN = (34, 108, 70)
PURPLE = (90, 56, 138)
LIGHT = (255, 255, 255)
DIM = (60, 58, 52)

FDIR = "/usr/share/fonts/truetype/dejavu/"


class Poster:
    def __init__(self):
        self.img = Image.new("RGB", (W, H), PAPER)
        self.d = ImageDraw.Draw(self.img)

    def fnt(self, name, size):
        return ImageFont.truetype(FDIR + name, size)

    def serif(self, s):
        return self.fnt("DejaVuSerif-Bold.ttf", s)

    def bold(self, s):
        return self.fnt("DejaVuSans-Bold.ttf", s)

    def plain(self, s):
        return self.fnt("DejaVuSans.ttf", s)

    def wrap(self, text, fnt, max_w):
        lines, cur = [], ""
        for word in text.split():
            trial = (cur + " " + word).strip()
            if self.d.textlength(trial, font=fnt) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, text, fnt, color, max_w, leading, cap=None):
        lines = self.wrap(text, fnt, max_w)
        if cap is not None and len(lines) > cap:
            lines = lines[:cap]
            while lines and self.d.textlength(lines[-1] + "...", font=fnt) > max_w:
                lines[-1] = lines[-1][:-1]
            lines[-1] = lines[-1].rstrip() + "..."
        for ln in lines:
            self.d.text((x, y), ln, font=fnt, fill=color)
            y += leading
        return y

    def numdisc(self, cx, cy, num, r=13):
        d = self.d
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED)
        t = str(num)
        f = self.bold(15 if len(t) < 2 else 12)
        tw = d.textlength(t, font=f)
        d.text((cx - tw / 2, cy - 8 if len(t) < 2 else cy - 7), t,
               font=f, fill=LIGHT)


# ------------------------------------------------------------------ hero
# One big painted scene: dusk over the Gulf, tankers on the sea, jets
# and missile trails in the sky, two explosions. Painted with bands,
# arcs and polygons — no photo, no network.

def paint_hero(p, x0, y0, x1, y1):
    d = p.d
    # Dusk sky in five horizontal bands.
    bands = [(196, 82, 52), (214, 112, 58), (232, 146, 74),
             (242, 178, 104), (246, 205, 138)]
    bh = (y1 - y0) * 0.58 / len(bands)
    for i, c in enumerate(bands):
        d.rectangle([x0, y0 + i * bh, x1, y0 + (i + 1) * bh + 1], fill=c)
    horizon = y0 + (y1 - y0) * 0.58
    # Sun low on the horizon.
    sx, sy, sr = x0 + (x1 - x0) * 0.68, horizon - 18, 42
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(250, 226, 140))
    d.ellipse([sx - sr * 0.55, sy - sr * 0.55, sx + sr * 0.55,
               sy + sr * 0.55], fill=(252, 240, 180))
    # Sea.
    d.rectangle([x0, horizon, x1, y1], fill=(18, 62, 112))
    d.rectangle([x0, horizon, x1, horizon + 6], fill=(240, 200, 120))
    for i, fy in enumerate((0.68, 0.78, 0.88)):
        yy = y0 + (y1 - y0) * fy
        d.arc([x0 + 40 + i * 90, yy - 14, x0 + 260 + i * 90, yy + 14],
              180, 360, fill=(120, 170, 210), width=4)
    # Tankers: dark hulls with superstructures, one burning.
    for tx, twd, burning in ((0.08, 0.30, False), (0.48, 0.34, True)):
        hx0 = x0 + (x1 - x0) * tx
        hx1 = hx0 + (x1 - x0) * twd
        hy = y0 + (y1 - y0) * 0.74
        d.polygon([(hx0, hy), (hx1, hy), (hx1 - 18, hy + 34),
                   (hx0 + 18, hy + 34)], fill=(28, 28, 30))
        d.rectangle([hx0 + (hx1 - hx0) * 0.62, hy - 26,
                     hx0 + (hx1 - hx0) * 0.78, hy], fill=(52, 52, 54))
        d.rectangle([hx0 + (hx1 - hx0) * 0.66, hy - 40,
                     hx0 + (hx1 - hx0) * 0.72, hy - 26], fill=(52, 52, 54))
        if burning:
            bx, by = hx0 + (hx1 - hx0) * 0.30, hy - 6
            for rr, c in ((34, (240, 150, 40)), (22, (250, 190, 60)),
                          (12, (252, 230, 120))):
                pts = []
                for k in range(12):
                    a = math.pi * k / 6
                    r = rr if k % 2 == 0 else rr * 0.55
                    pts.append((bx + r * math.cos(a), by + r * math.sin(a)))
                d.polygon(pts, fill=c)
            for i in range(4):
                r = 8 + i * 4
                d.ellipse([bx - r, by - 46 - i * 12, bx + r, by - 30 - i * 12],
                          fill=(90, 90, 90))
    # Jets in the sky + missile trails.
    for jx, jy in ((0.16, 0.16), (0.38, 0.10)):
        ox, oy = x0 + (x1 - x0) * jx, y0 + (y1 - y0) * jy
        s = 26
        d.polygon([(ox, oy), (ox + s * 1.8, oy + s * 0.35),
                   (ox, oy + s * 0.7)], fill=(30, 30, 32))
        d.polygon([(ox + s * 0.5, oy + s * 0.1), (ox + s * 0.9, oy - s * 0.4),
                   (ox + s * 1.1, oy + s * 0.1)], fill=(30, 30, 32))
    for tx0, ty0, tx1, ty1 in ((0.52, 0.06, 0.72, 0.34),
                               (0.60, 0.04, 0.86, 0.30)):
        d.arc([x0 + (x1 - x0) * tx0, y0 + (y1 - y0) * ty0,
               x0 + (x1 - x0) * tx1, y0 + (y1 - y0) * ty1],
              200, 340, fill=LIGHT, width=3)
    # Missile heads at the ends of the trails.
    for fx, fy in ((0.714, 0.152), (0.852, 0.128)):
        px, py = x0 + (x1 - x0) * fx, y0 + (y1 - y0) * fy
        d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=RED)
    # Second explosion, small, far right.
    ex, ey = x0 + (x1 - x0) * 0.90, y0 + (y1 - y0) * 0.44
    for rr, c in ((26, (240, 150, 40)), (16, (250, 190, 60)),
                  (8, (252, 230, 120))):
        pts = []
        for k in range(12):
            a = math.pi * k / 6
            r = rr if k % 2 == 0 else rr * 0.55
            pts.append((ex + r * math.cos(a), ey + r * math.sin(a)))
        d.polygon(pts, fill=c)


# ------------------------------------------------------------------ cards
# Big illustrated cards. Each painter draws inside box (x0, y0, x1, y1)
# using fractions of the box.

def frac(box):
    x0, y0, x1, y1 = box
    w, h = x1 - x0, y1 - y0
    return (lambda f: x0 + f * w), (lambda f: y0 + f * h), w, h


def paint_bridge(p, box):
    d = p.d
    u, v, w, h = frac(box)
    d.rectangle(box, fill=(188, 216, 232))
    d.rectangle([box[0], v(0.60), box[2], box[3]], fill=(64, 120, 160))
    d.rectangle([u(0.06), v(0.56), u(0.44), v(0.64)], fill=INK)
    d.rectangle([u(0.56), v(0.56), u(0.94), v(0.64)], fill=INK)
    d.rectangle([u(0.13), v(0.26), u(0.17), v(0.60)], fill=INK)
    d.rectangle([u(0.83), v(0.26), u(0.87), v(0.60)], fill=INK)
    d.line([u(0.15), v(0.26), u(0.50), v(0.60)], fill=INK, width=4)
    d.line([u(0.85), v(0.26), u(0.50), v(0.60)], fill=INK, width=4)
    d.polygon([(u(0.46), v(0.60)), (u(0.50), v(0.42)), (u(0.54), v(0.60))],
              fill=(228, 116, 40))
    for fx, fy in ((0.08, 0.18), (0.24, 0.10), (0.90, 0.16)):
        r = 7
        d.ellipse([u(fx) - r, v(fy) - r, u(fx) + r, v(fy) + r],
                  fill=(120, 120, 120))
    d.ellipse([u(0.62), v(0.70), u(0.70), v(0.78)], fill=LIGHT)


def paint_flags(p, box):
    d = p.d
    u, v, w, h = frac(box)
    d.rectangle(box, fill=(228, 234, 240))
    for i, (c1, c2) in enumerate((((178, 34, 34), (255, 255, 255)),
                                  ((222, 32, 32), (255, 215, 0)),
                                  ((255, 255, 255), (31, 93, 140)))):
        cx = u(0.17 + i * 0.33)
        d.line([cx, v(0.12), cx, v(0.92)], fill=INK, width=5)
        fx0, fy0 = cx - w * 0.11, v(0.12)
        fw, fh = w * 0.22, h * 0.52
        d.rectangle([fx0, fy0, fx0 + fw, fy0 + fh], fill=c1)
        if i == 0:
            for s in range(3):
                d.line([fx0, fy0 + fh * (0.25 + s * 0.25),
                        fx0 + fw, fy0 + fh * (0.25 + s * 0.25)],
                       fill=c2, width=3)
            d.rectangle([fx0, fy0, fx0 + fw * 0.38, fy0 + fh * 0.45],
                        fill=(18, 32, 62))
        elif i == 1:
            for sx, sy in ((0.25, 0.30), (0.55, 0.25), (0.50, 0.60)):
                d.ellipse([fx0 + fw * sx - 3, fy0 + fh * sy - 3,
                           fx0 + fw * sx + 3, fy0 + fh * sy + 3], fill=c2)
        else:
            d.rectangle([fx0, fy0 + fh * 0.35, fx0 + fw, fy0 + fh * 0.68],
                        fill=c2)
            d.rectangle([fx0, fy0 + fh * 0.68, fx0 + fw, fy0 + fh],
                        fill=(178, 34, 34))


def paint_chip(p, box):
    d = p.d
    u, v, w, h = frac(box)
    d.rectangle(box, fill=(20, 58, 42))
    cx, cy = u(0.30), v(0.50)
    s = h * 0.40
    for i in range(3):
        t = u(0.15 + i * 0.06)
        d.line([t, v(0.08), t, v(0.22)], fill=GOLD, width=4)
        d.line([t, v(0.78), t, v(0.92)], fill=GOLD, width=4)
    d.rectangle([cx - s, cy - s, cx + s, cy + s], fill=GREEN)
    d.rectangle([cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2],
                outline=GOLD, width=4)
    for i, fh in enumerate((0.28, 0.52, 0.40, 0.68)):
        bx = u(0.58 + i * 0.09)
        d.rectangle([bx, v(0.92 - fh), bx + w * 0.05, v(0.92)],
                    fill=(120, 220, 130))


def paint_virus(p, box):
    d = p.d
    u, v, w, h = frac(box)
    d.rectangle(box, fill=(240, 228, 242))
    cx, cy = u(0.50), v(0.50)
    r = h * 0.40
    for i in range(8):
        a = math.pi * i / 4
        d.line([cx + r * 0.85 * math.cos(a), cy + r * 0.85 * math.sin(a),
                cx + r * 1.15 * math.cos(a), cy + r * 1.15 * math.sin(a)],
               fill=PURPLE, width=5)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=PURPLE)
    d.ellipse([cx - r * 0.35, cy - r * 0.35, cx + r * 0.35, cy + r * 0.35],
              fill=GOLD)
    d.ellipse([cx + r * 0.25, cy - r * 0.70, cx + r * 0.60, cy - r * 0.35],
              fill=GOLD)


def paint_globe(p, box):
    d = p.d
    u, v, w, h = frac(box)
    d.rectangle(box, fill=(216, 234, 228))
    cx, cy = u(0.42), v(0.50)
    r = h * 0.42
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=TEAL, width=5)
    d.ellipse([cx - r * 0.4, cy - r, cx + r * 0.4, cy + r], outline=TEAL,
              width=3)
    d.line([cx - r, cy, cx + r, cy], fill=TEAL, width=3)
    d.rectangle([u(0.80), v(0.10), u(0.88), v(0.90)], outline=RED, width=4)
    d.ellipse([u(0.84) - r * 0.16, v(0.14) - r * 0.16,
               u(0.84) + r * 0.16, v(0.14) + r * 0.16], fill=RED)
    d.line([u(0.84), v(0.14), u(0.84), v(0.86)], fill=RED, width=4)


def paint_tents(p, box):
    d = p.d
    u, v, w, h = frac(box)
    d.rectangle(box, fill=(234, 228, 216))
    for fx in (0.24, 0.54):
        tx = u(fx)
        d.polygon([(tx - w * 0.11, v(0.90)), (tx + w * 0.11, v(0.90)),
                   (tx, v(0.32))], fill=LIGHT, outline=RED, width=4)
        d.line([tx, v(0.32), tx, v(0.90)], fill=RED, width=3)
    d.rectangle([u(0.80), v(0.16), u(0.92), v(0.48)], fill=LIGHT)
    d.rectangle([u(0.83), v(0.26), u(0.89), v(0.38)], fill=RED)
    d.rectangle([u(0.845), v(0.29), u(0.875), v(0.35)], fill=LIGHT)


PAINTERS = {
    "bridge": paint_bridge, "flags": paint_flags, "chip": paint_chip,
    "virus": paint_virus, "globe": paint_globe, "tents": paint_tents,
}

# (number, kicker, colour, headline, summary, painter)
CARDS = [
    (2, "EUROPE · UKRAINE WAR", BLUE,
     "Kerch Bridge span falls into the sea",
     "Second strike in two days; Zelensky hails an \u2018unprecedented "
     "operation\u2019. Russia hits bridges near Kyiv in reply.",
     "bridge"),
    (3, "ASIA · DIPLOMACY", TEAL,
     "Trump in Manila; summit on Thursday",
     "Quad agrees critical-minerals deals; Xi, Trump, Putin meet in "
     "Shenzhen \u2014 the first trilateral of its kind.",
     "flags"),
    (4, "US · MARKETS", GREEN,
     "Nvidia posts record $115.8bn quarter",
     "Sales roughly doubled in a year; first since Huang quit; the "
     "board won\u2019t reinstate him.",
     "chip"),
    (5, "AFRICA · HEALTH", PURPLE,
     "Ebola in DR Congo passes 11,000 cases",
     "More than 5,400 dead, the UN says; cases have more than doubled "
     "in three months.",
     "virus"),
    (6, "GLOBAL · CLIMATE", TEAL,
     "COP31 split over fossil-fuel phase-out",
     "Draft deal calls for $120bn a year in climate finance; talks in "
     "Antalya end Friday.",
     "globe"),
    (7, "MIDDLE EAST · GAZA", RED,
     "Gaza truce at risk of collapse, UN is told",
     "Board of Peace report; UN agencies say 1.4m people face acute "
     "hunger as winter sets in.",
     "tents"),
]

ALSO = ("Rwanda hub \u00b7 Mongolia resigns \u00b7 Japan jets \u00b7 "
        "Serbia students \u00b7 An-12 crash \u00b7 Measles status lost")


def build():
    p = Poster()
    d = p.d
    d.rectangle([0, 0, W - 1, H - 1], outline=INK, width=4)

    # Top bar.
    d.text((16, 6), "THE WORLD IN ONE DAY", font=p.bold(15), fill=RED)
    right = "TUESDAY 17 NOVEMBER 2026"
    d.text((W - 16 - d.textlength(right, font=p.bold(15)), 6), right,
           font=p.bold(15), fill=NAVY)
    d.line([16, 26, W - 16, 26], fill=GOLD, width=2)

    # Hero: painted Gulf scene + dark band with the lead headline.
    paint_hero(p, 4, 28, W - 5, 344)
    d.rectangle([4, 344, W - 5, 470], fill=NAVY)
    p.numdisc(48, 372, 1, r=14)
    d.text((76, 356), "MIDDLE EAST · IRAN WAR", font=p.bold(16), fill=RED)
    p.para(76, 378, "US jets strike Iran after drones hit the Bahrain base",
           p.serif(34), LIGHT, W - 76 - 24, 40, cap=2)
    p.para(76, 448, "A fourth tanker is mined in the Strait of Hormuz \u00b7 "
           "1,441 drones downed over Crimea",
           p.plain(15), (205, 210, 220), W - 76 - 24, 18)

    # Two rows of three big cards.
    cols = [16, 352, 688]
    for row in range(2):
        for c in range(3):
            story = CARDS[row * 3 + c]
            num, kicker, kcolor, head, summ, key = story
            x = cols[c]
            y = 486 + row * 246
            PAINTERS[key](p, (x, y, x + 320, y + 118))
            p.numdisc(x + 20, y + 20, num, r=13)
            d.text((x + 4, y + 126), kicker, font=p.bold(13), fill=kcolor)
            p.para(x + 4, y + 144, head, p.bold(21), INK, 312, 24, cap=2)
            p.para(x + 4, y + 194, summ, p.plain(14), DIM, 312, 17, cap=2)

    # Also strip + footer.
    d.text((16, 978), "ALSO:  " + ALSO, font=p.plain(13), fill=DIM)
    d.line([16, 1000, W - 16, 1000], fill=GREY, width=1)
    d.text((16, 1006),
           "Every story here happened or was first reported on Tuesday "
           "17 November 2026. Sources: Reuters \u00b7 AP \u00b7 AFP \u00b7 "
           "BBC \u00b7 Al Jazeera \u00b7 UN News. Original drawings.",
           font=p.plain(11), fill=GREY)
    return p.img


if __name__ == "__main__":
    poster = build()
    poster.save("entry.png", format="PNG", optimize=True)
    print("wrote entry.png", poster.size)

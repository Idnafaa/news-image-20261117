"""Render the 17 November 2026 world-news poster (1024x1024 PNG).

Draws a newspaper-style front page with PIL and the DejaVu fonts:
a masthead naming the day, one lead story, four more stories in a
grid, and an "also on this day" strip. All text comes from news
reported on Tuesday 17 November 2026. Deterministic: no random
numbers, no clock, no network. Run: python3 render.py
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (246, 241, 231)
INK = (26, 26, 26)
NAVY = (20, 33, 61)
GOLD = (232, 182, 76)
RED = (179, 32, 44)
BLUE = (31, 93, 140)
TEAL = (14, 107, 107)
GREEN = (34, 110, 72)
PURPLE = (91, 58, 140)
GREY = (90, 86, 78)
LIGHT = (255, 255, 255)

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FONT_DIR + name, size)


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


def para(draw, x, y, text, fnt, color, max_w, leading):
    """Draw wrapped text; returns the y just below the last line."""
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=color)
        y += leading
    return y


def letterspaced(draw, x, y, text, fnt, color, spacing=4):
    """Draw text with extra space between letters; returns end x."""
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=color)
        x += draw.textlength(ch, font=fnt) + spacing
    return x


# --- small pictograms, drawn with plain shapes ---------------------------

def icon_burst(d, box, c1, c2):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    pts = []
    for i in range(24):
        ang = math.pi * i / 12
        r = 34 if i % 2 == 0 else 15
        pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
    d.polygon(pts, fill=c1)
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=c2)


def icon_bridge(d, box, c1, c2):
    x0, y0, x1, y1 = box
    d.line([x0 + 4, y1 - 14, x1 - 4, y1 - 14], fill=c1, width=5)
    for tx in (x0 + 14, x1 - 22):
        d.rectangle([tx, y0 + 18, tx + 8, y1 - 14], fill=c1)
    d.arc([x0 + 8, y0 + 6, x1 - 8, y1 - 6], 180, 360, fill=c2, width=4)
    d.line([x0 + 18, y0 + 18, (x0 + x1) / 2, y1 - 14], fill=c2, width=3)
    d.line([x1 - 18, y0 + 18, (x0 + x1) / 2, y1 - 14], fill=c2, width=3)


def icon_globe(d, box, c1, c2):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    d.ellipse([x0 + 6, y0 + 6, x1 - 6, y1 - 6], outline=c1, width=5)
    d.ellipse([cx - 12, y0 + 6, cx + 12, y1 - 6], outline=c1, width=3)
    d.line([x0 + 6, cy, x1 - 6, cy], fill=c1, width=3)
    d.arc([x0 + 6, y0 + 16, x1 - 6, y1 - 16], 270, 90, fill=c2, width=3)
    d.arc([x0 + 6, y0 + 16, x1 - 6, y1 - 16], 90, 270, fill=c2, width=3)


def icon_chip(d, box, c1, c2):
    x0, y0, x1, y1 = box
    for i in range(3):
        t = x0 + 16 + i * 18
        d.line([t, y0 + 2, t, y0 + 12], fill=c1, width=4)
        d.line([t, y1 - 12, t, y1 - 2], fill=c1, width=4)
        t2 = y0 + 16 + i * 18
        d.line([x0 + 2, t2, x0 + 12, t2], fill=c1, width=4)
        d.line([x1 - 12, t2, x1 - 2, t2], fill=c1, width=4)
    d.rectangle([x0 + 12, y0 + 12, x1 - 12, y1 - 12], fill=c1)
    d.rectangle([x0 + 26, y0 + 26, x1 - 26, y1 - 26], outline=c2, width=3)


def icon_virus(d, box, c1, c2):
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for i in range(8):
        ang = math.pi * i / 4
        d.line([cx + 20 * math.cos(ang), cy + 20 * math.sin(ang),
                cx + 32 * math.cos(ang), cy + 32 * math.sin(ang)],
               fill=c1, width=5)
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=c1)
    d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=c2)
    d.ellipse([cx + 4, cy - 14, cx + 12, cy - 6], fill=c2)

# --- page layout ----------------------------------------------------------

def draw_poster():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W - 1, H - 1], outline=INK, width=4)

    # Masthead: the day, named loud and clear.
    d.rectangle([4, 4, W - 5, 154], fill=NAVY)
    letterspaced(d, 36, 26, "THE WORLD IN ONE DAY", BOLD(26), GOLD, 5)
    d.text((34, 58), "TUESDAY, 17 NOVEMBER 2026", font=BOLD(54), fill=LIGHT)
    d.line([36, 122, W - 36, 122], fill=GOLD, width=2)
    d.text((36, 130), "Five stories that defined the day",
           font=REG(19), fill=(205, 210, 220))

    # Lead story: the Gulf.
    y = 168
    d.text((36, y), "WAR IN THE GULF", font=BOLD(22), fill=RED)
    y += 30
    y = para(d, 36, y, "US jets strike Iranian missile site on Qeshm Island",
             BOLD(38), INK, 780, 46)
    y += 6
    y = para(d, 36, y,
             "Iran fired drones at a US radar base in Bahrain, its third "
             "attack there in five days. A fourth oil tanker was hit by a "
             "mine in the Strait of Hormuz.",
             REG(21), (58, 56, 50), 780, 28)
    icon_burst(d, (856, 176, 988, 308), (240, 150, 40), (179, 32, 44))

    d.line([36, 396, W - 36, 396], fill=INK, width=2)

    # Four more stories, two by two.
    stories = [
        ("UKRAINE", BLUE, icon_bridge,
         "Kerch Bridge hit again — a section falls into the sea",
         "Ukrainian drones struck the bridge to Crimea for a second day. "
         "The crossing was closed; Russia hit bridges near Kyiv in reply."),
        ("SUMMIT IN SHENZHEN", TEAL, icon_globe,
         "Trump flies in for first-ever US–China–Russia summit",
         "The three leaders meet on Thursday at APEC to talk nuclear arms "
         "and Ukraine — the first trilateral of its kind."),
        ("MARKETS", GREEN, icon_chip,
         "Nvidia posts record $115bn revenue",
         "Sales roughly doubled in a year. The chipmaker said it will not "
         "bring back ousted chief Jensen Huang."),
        ("HEALTH", PURPLE, icon_virus,
         "Ebola in DR Congo passes 11,000 cases",
         "More than 5,400 people have died, the UN said — cases have more "
         "than doubled in three months."),
    ]
    gx, gy = 36, 416
    cw, ch, gap = 464, 190, 24
    for i, (kick, col, icon, head, body) in enumerate(stories):
        x = gx + (i % 2) * (cw + gap)
        yy = gy + (i // 2) * (ch + gap)
        d.text((x, yy), kick, font=BOLD(18), fill=col)
        icon(d, (x + cw - 62, yy, x + cw, yy + 62), col, GOLD)
        yy += 26
        yy = para(d, x, yy, head, BOLD(26), INK, cw - 72, 32)
        yy += 4
        para(d, x, yy, body, REG(18), (58, 56, 50), cw - 8, 24)

    # Also on this day.
    y = 830
    d.line([36, y, W - 36, y], fill=INK, width=2)
    y += 14
    d.text((36, y), "ALSO ON 17 NOVEMBER", font=BOLD(20), fill=NAVY)
    y += 32
    also = [
        ("COP31 deal — ", "Draft text calls for a faster fossil-fuel "
         "phase-out and $120bn a year in climate finance."),
        ("Europe — ", "Five states plan a joint centre in Rwanda for "
         "rejected asylum seekers."),
        ("Gaza — ", "Britain, Australia, Canada and Italy urge Israel to "
         "open crossings for aid."),
        ("Japan — ", "Fighter jets scrambled after Russian planes entered "
         "its airspace."),
    ]
    for i, (lead, rest) in enumerate(also):
        yy = y + i * 26
        d.text((36, yy), lead, font=BOLD(17), fill=INK)
        lw = d.textlength(lead, font=BOLD(17))
        d.text((36 + lw, yy), rest, font=REG(17), fill=(58, 56, 50))

    # Footer: sources, and the date once more.
    d.line([36, 978, W - 36, 978], fill=GREY, width=1)
    d.text((36, 988), "Sources: CBS News · NPR · Al Jazeera · AFP · UN News · Dawn",
           font=REG(15), fill=GREY)
    d.text((W - 36 - d.textlength("17 NOVEMBER 2026", font=BOLD(15)), 988),
           "17 NOVEMBER 2026", font=BOLD(15), fill=GREY)
    return img


if __name__ == "__main__":
    poster = draw_poster()
    poster.save("entry.png", format="PNG", optimize=True)
    print("wrote entry.png", poster.size)

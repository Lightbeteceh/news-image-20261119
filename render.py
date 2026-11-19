#!/usr/bin/env python3
"""Draw the entry picture for the make.fun news-image-20261119 bounty.

The design is an atlas spread: a dark masthead, a big drawn world map
with numbered pins for the ten places that mattered most, the lead story
and the day's market numbers beside the map, and below it six continent
panels holding 45 headlines from Thursday 19 November 2026.

Everything on the page comes from ``stories.json`` in this same folder.
Run ``python3 render.py`` and it writes ``entry.png`` next to itself:
1024x1024, well under 1 MiB. It needs nothing from the network — the
Merriweather faces it sets the page in are bundled under ``fonts/``
(SIL Open Font License 1.1) — and the only third-party import is Pillow.
Given the same ``stories.json`` it always writes the same bytes; if a
headline ever overflows its panel the script fails loudly instead of
clipping text silently.
"""

import json
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
TYPE_DIR = os.path.join(HERE, "fonts")
PAGE_W, PAGE_H = 1024, 1024

CUTS = {
    "regular": "merriweather-v33-latin-regular.ttf",
    "bold": "merriweather-v33-latin-700.ttf",
    "black": "merriweather-v33-latin-900.ttf",
}

NAVY = (22, 35, 61)
NAVY_SOFT = (48, 66, 96)
PAPER = (244, 241, 235)
CARD = (255, 255, 255)
SEA = (214, 228, 238)
LAND = (232, 219, 188)
LAND_LINE = (96, 118, 130)
RULE_RED = (165, 30, 25)
BODY = (24, 24, 24)
SOFT = (88, 84, 76)
FAINT = (120, 115, 105)
PIN = (178, 34, 34)

# Rough continent outlines in (longitude, latitude), drawn as a
# schematic atlas map — recognisable shapes, not a survey chart.
CONTINENTS = {
    "north_america": [(-168, 66), (-150, 70), (-130, 71), (-110, 73),
                      (-95, 80), (-82, 73), (-68, 62), (-55, 47),
                      (-65, 44), (-75, 36), (-81, 26), (-90, 21),
                      (-97, 16), (-104, 20), (-112, 26), (-122, 37),
                      (-125, 49), (-135, 58), (-152, 58), (-168, 66)],
    "south_america": [(-79, 9), (-62, 8), (-52, 4), (-44, -3),
                      (-35, -8), (-39, -15), (-41, -23), (-49, -29),
                      (-58, -35), (-65, -41), (-70, -50), (-68, -54),
                      (-71, -45), (-73, -32), (-72, -20), (-78, -8),
                      (-81, 1), (-79, 9)],
    "europe": [(-10, 36), (-9, 43), (-2, 48), (0, 51), (4, 53),
               (8, 57), (12, 56), (18, 56), (21, 55), (25, 60),
               (28, 62), (30, 70), (40, 68), (44, 66), (42, 58),
               (40, 50), (35, 45), (30, 46), (28, 41), (23, 36),
               (19, 40), (12, 44), (3, 43), (-2, 37), (-10, 36)],
    "africa": [(-17, 15), (-12, 27), (-6, 35), (10, 37), (20, 32),
               (32, 31), (35, 28), (43, 12), (51, 11), (48, 2),
               (41, -9), (36, -18), (32, -26), (26, -34), (19, -35),
               (15, -27), (12, -18), (9, -2), (9, 4), (-8, 5),
               (-17, 15)],
    "asia": [(40, 68), (52, 69), (60, 70), (70, 72), (80, 73),
             (100, 77), (120, 73), (140, 72), (158, 71), (178, 66),
             (170, 60), (162, 56), (158, 52), (142, 50), (140, 40),
             (130, 35), (127, 34), (122, 31), (120, 23), (110, 20),
             (108, 12), (104, 8), (100, 6), (97, 16), (91, 22),
             (88, 22), (80, 13), (77, 8), (73, 16), (66, 25),
             (61, 25), (57, 26), (52, 26), (50, 30), (48, 30),
             (44, 39), (41, 42), (39, 46), (40, 56), (40, 68)],
    "oceania": [(113, -22), (114, -30), (115, -35), (122, -34),
                (129, -32), (135, -35), (140, -38), (146, -39),
                (150, -37), (153, -32), (153, -27), (150, -22),
                (146, -19), (142, -11), (137, -12), (132, -11),
                (126, -14), (122, -17), (117, -20), (113, -22)],
}

TAB_COLOURS = [(165, 30, 25), (0, 90, 160), (0, 120, 60),
               (150, 60, 0), (110, 40, 130), (0, 120, 120)]


def typeface(cut, size):
    """A Merriweather face at the given size, from the bundled fonts."""
    try:
        return ImageFont.truetype(os.path.join(TYPE_DIR, CUTS[cut]), size)
    except OSError:
        return ImageFont.load_default()


def wrap_lines(draw, text, face, width):
    """Greedy word wrap: split text into lines that fit a pixel width."""
    words, lines, current = text.split(), [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=face) <= width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(draw, x, y, text, face, width, colour, spacing=2):
    """Draw wrapped text and return the y coordinate just below it."""
    for line in wrap_lines(draw, text, face, width):
        draw.text((x, y), line, font=face, fill=colour)
        y += face.size + spacing
    return y


class AtlasMap:
    """Equirectangular world map drawn inside a rectangle."""

    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.lat_top, self.lat_bot = 84.0, -58.0

    def project(self, lon, lat):
        px = self.x + (lon + 180.0) / 360.0 * self.w
        py = self.y + (self.lat_top - lat) / (self.lat_top - self.lat_bot) * self.h
        return px, py

    def draw(self, pen):
        pen.rectangle([self.x, self.y, self.x + self.w, self.y + self.h],
                      fill=SEA)
        # Graticule every 30 degrees.
        for lon in range(-180, 181, 30):
            px, _ = self.project(lon, 0)
            pen.line([(px, self.y), (px, self.y + self.h)],
                     fill=(190, 208, 220), width=1)
        for lat in range(-60, 91, 30):
            _, py = self.project(0, lat)
            pen.line([(self.x, py), (self.x + self.w, py)],
                     fill=(190, 208, 220), width=1)
        for shape in CONTINENTS.values():
            pen.polygon([self.project(lon, lat) for lon, lat in shape],
                        fill=LAND, outline=LAND_LINE, width=1)
        # New Zealand, two small marks south-east of Australia.
        for lon, lat in ((167, -45), (174, -41)):
            px, py = self.project(lon, lat)
            pen.ellipse([px - 3, py - 2, px + 3, py + 2],
                        fill=LAND, outline=LAND_LINE)
        # Compass rose, top right of the sea.
        cx, cy = self.x + self.w - 26, self.y + 24
        pen.ellipse([cx - 13, cy - 13, cx + 13, cy + 13],
                    outline=LAND_LINE, width=1)
        pen.polygon([(cx, cy - 10), (cx + 4, cy + 6), (cx - 4, cy + 6)],
                    fill=NAVY)
        pen.text((cx - 4, cy - 24), "N", font=typeface("bold", 10),
                 fill=NAVY)


def draw_pin(pen, x, y, label):
    """A numbered red pin with a white numeral."""
    pen.ellipse([x - 10, y - 10, x + 10, y + 10], fill=PIN,
                outline=(255, 255, 255), width=2)
    face = typeface("bold", 10)
    tw = pen.textlength(label, font=face)
    pen.text((x - tw / 2, y - 7), label, font=face, fill=(255, 255, 255))


def main():
    with open(os.path.join(HERE, "stories.json"), encoding="utf-8") as fh:
        data = json.load(fh)

    page = Image.new("RGB", (PAGE_W, PAGE_H), PAPER)
    pen = ImageDraw.Draw(page)

    # ---- Masthead: dark navy band, title left, date and count right.
    pen.rectangle([0, 0, PAGE_W, 76], fill=NAVY)
    pen.text((28, 16), "THE WORLD IN ONE DAY",
             font=typeface("black", 34), fill=(255, 255, 255))
    pen.text((28, 56), "THURSDAY 19 NOVEMBER 2026",
             font=typeface("bold", 13), fill=(180, 195, 215))
    total = sum(len(s["headlines"]) for s in data["sections"])
    badge = f"{total} STORIES  ·  6 CONTINENTS"
    face = typeface("bold", 13)
    pen.text((PAGE_W - 28 - pen.textlength(badge, font=face), 22), badge,
             font=face, fill=(255, 214, 90))
    pen.text((PAGE_W - 28 - pen.textlength("ONE IMAGE — THE WHOLE DAY",
             font=typeface("regular", 11)), 48),
             "ONE IMAGE — THE WHOLE DAY",
             font=typeface("regular", 11), fill=(180, 195, 215))

    # ---- Map band: atlas map left, lead story + numbers right.
    map_x, map_y, map_w, map_h = 24, 88, 648, 268
    atlas = AtlasMap(map_x, map_y, map_w, map_h)
    atlas.draw(pen)
    for lon, lat, label, _place in data["map_points"]:
        px, py = atlas.project(lon, lat)
        draw_pin(pen, px, py, label)
    key = "  ·  ".join(f"{n} {place}" for _lon, _lat, n, place
                       in data["map_points"])
    pen.text((map_x, map_y + map_h + 6), key,
             font=typeface("regular", 10), fill=SOFT)

    lead_x, lead_w = 692, 308
    pen.rectangle([lead_x, map_y, lead_x + lead_w, map_y + map_h],
                  fill=CARD, outline=(200, 195, 185), width=1)
    pen.rectangle([lead_x, map_y, lead_x + lead_w, map_y + 5], fill=RULE_RED)
    lx = lead_x + 14
    pen.text((lx, map_y + 14), "TOP STORY",
             font=typeface("bold", 11), fill=RULE_RED)
    y = draw_lines(pen, lx, map_y + 32, data["lead"]["headline"],
                   typeface("black", 19), lead_w - 28, BODY, spacing=3)
    y = draw_lines(pen, lx, y + 6, data["lead"]["standfirst"],
                   typeface("regular", 12), lead_w - 28, SOFT, spacing=3)
    y += 8
    pen.line([(lx, y), (lead_x + lead_w - 14, y)], fill=(215, 210, 200),
             width=1)
    y += 8
    pen.text((lx, y), "THE DAY IN NUMBERS",
             font=typeface("bold", 11), fill=NAVY)
    y += 18
    numbers = data["numbers"]
    for row_i in range(0, len(numbers), 2):
        for col_i, (label, value, move) in enumerate(numbers[row_i:row_i + 2]):
            cell = f"{label} {value} {move}"
            pen.text((lx + col_i * 148, y), cell,
                     font=typeface("regular", 10), fill=BODY)
        y += 16
    if y > map_y + map_h - 6:
        raise SystemExit("lead panel overflow: numbers do not fit")

    # ---- Six continent panels: three columns, two rows.
    grid_x, grid_y = 24, 388
    col_w, row_h, gap = 320, 292, 16
    for i, section in enumerate(data["sections"]):
        col, row = i % 3, i // 3
        x = grid_x + col * (col_w + gap)
        top = grid_y + row * (row_h + gap)
        pen.rectangle([x, top, x + col_w, top + row_h], fill=CARD,
                      outline=(200, 195, 185), width=1)
        pen.rectangle([x, top, x + col_w, top + 6],
                      fill=TAB_COLOURS[i % len(TAB_COLOURS)])
        pen.text((x + 14, top + 16), section["continent"].upper(),
                 font=typeface("bold", 14),
                 fill=TAB_COLOURS[i % len(TAB_COLOURS)])
        count = f"{len(section['headlines'])} stories"
        face = typeface("regular", 11)
        pen.text((x + col_w - 14 - pen.textlength(count, font=face),
                  top + 18), count, font=face, fill=FAINT)
        y = top + 44
        for headline in section["headlines"]:
            y = draw_lines(pen, x + 14, y, "•  " + headline,
                           typeface("regular", 13), col_w - 28, BODY,
                           spacing=1)
            y += 2
            if y > top + row_h - 8:
                raise SystemExit(
                    f"section overflow in {section['continent']}: "
                    "headlines do not fit the panel")
        # Thin rule under the last headline.
        pen.line([(x + 14, top + row_h - 12), (x + col_w - 14,
                  top + row_h - 12)], fill=(228, 224, 216), width=1)

    # ---- Footer.
    pen.text((28, 996),
             f"{total} stories  ·  6 continents  ·  Thursday 19 November 2026"
             "  ·  Sources: Reuters, BBC, Guardian, AP, FT",
             font=typeface("regular", 11), fill=FAINT)

    out = os.path.join(HERE, "entry.png")
    page.save(out, format="PNG", optimize=True)
    print(f"wrote {out} ({os.path.getsize(out)} bytes, {PAGE_W}x{PAGE_H})")


if __name__ == "__main__":
    main()

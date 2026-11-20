#!/usr/bin/env python3
"""news-image-20261120: draws a 1024x1024 world-news infographic for
Friday 20 November 2026, stdlib only, deterministic PNG output.

Hand-written 5x7 bitmap font, manual PNG encoder (struct + zlib).
No network, no randomness, no time, no file reads at runtime.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font 5x7
# Each glyph: 7 rows of 5 characters, '#' = pixel on, '.' = off.
FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '/': ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    '(': ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ')': ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    '$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    '&': (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '|': ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    '\u00b0': (".###.", "#...#", "#...#", ".###.", ".....", ".....", "....."),
}


def text_width(s, scale, spacing):
    """Pixel width of string s at given scale and inter-glyph spacing."""
    if not s:
        return 0
    return len(s) * (5 * scale + spacing) - spacing


def wrap_text(s, scale, spacing, max_w):
    """Greedy word wrap; returns list of lines, each <= max_w pixels."""
    words = s.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if text_width(trial, scale, spacing) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ------------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg=(255, 255, 255)):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x0, x1, y, color):
        for xx in range(x0, x1 + 1):
            self.set(xx, y, color)

    def vline(self, x, y0, y1, color):
        for yy in range(y0, y1 + 1):
            self.set(x, yy, color)

    def line(self, x0, y0, x1, y1, color):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - 1) ** 2 <= d2 <= r * r:
                    self.set(xx, yy, color)

    def tri(self, x1, y1, x2, y2, x3, y3, color):
        """Filled triangle via scanlines."""
        ys = sorted(((x1, y1), (x2, y2), (x3, y3)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = ys

        def edge_x(y, p, q):
            if p[1] == q[1]:
                return p[0]
            return p[0] + (q[0] - p[0]) * (y - p[1]) / (q[1] - p[1])

        for y in range(ay, cy + 1):
            if y < by:
                xa, xb = edge_x(y, (ax, ay), (bx, by)), edge_x(y, (ax, ay), (cx, cy))
            else:
                xa, xb = edge_x(y, (bx, by), (cx, cy)), edge_x(y, (ax, ay), (cx, cy))
            lo, hi = int(min(xa, xb)), int(max(xa, xb))
            for x in range(lo, hi + 1):
                self.set(x, y, color)

    # ------------------------------------------------------------ text
    def draw_char(self, ch, x, y, scale, color):
        glyph = FONT.get(ch.upper(), FONT['?'])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '#':
                    self.rect(x + col * scale, y + row * scale,
                              scale, scale, color)

    def draw_text(self, s, x, y, scale, color, spacing=None):
        if spacing is None:
            spacing = max(1, scale // 2)
        cx = x
        for ch in s:
            if ch != ' ':
                self.draw_char(ch, cx, y, scale, color)
            cx += 5 * scale + spacing
        return cx - spacing - x  # width drawn


# -------------------------------------------------------------- PNG encoder
def _chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
    return out


def write_png(path, canvas):
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: None
        raw += canvas.px[y * stride:(y + 1) * stride]
    png = (b"\x89PNG\r\n\x1a\n"
           + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ------------------------------------------------------------------- icons
# All icons drawn in white inside the panel top bar, in a 44x34 box
# whose top-left is (x, y). Simple shapes only.
def icon_missile(c, x, y, col):
    # rocket body + nose + fins + flame
    c.rect(x + 19, y + 5, 6, 14, col)                    # body
    c.tri(x + 19, y + 5, x + 25, y + 5, x + 22, y - 1, col)  # nose
    c.tri(x + 19, y + 15, x + 14, y + 21, x + 19, y + 19, col)  # fin L
    c.tri(x + 25, y + 15, x + 30, y + 21, x + 25, y + 19, col)  # fin R
    c.tri(x + 20, y + 19, x + 24, y + 19, x + 22, y + 30, col)  # flame


def icon_globe(c, x, y, col):
    cx, cy = x + 22, y + 17
    c.ring(cx, cy, 12, col)
    c.hline(cx - 11, cx + 11, cy, col)
    c.hline(cx - 9, cx + 9, cy - 6, col)
    c.hline(cx - 9, cx + 9, cy + 6, col)
    c.vline(cx, cy - 12, cy + 12, col)


def icon_cyclone(c, x, y, col):
    # spiral of dots, radius growing with angle
    cx, cy = x + 22, y + 17
    for k in range(0, 42):
        ang = k * 0.42
        r = 1.5 + k * 0.27
        import math
        px = int(cx + r * math.cos(ang))
        py = int(cy + r * math.sin(ang))
        c.disc(px, py, 1, col)


def icon_tanker(c, x, y, col):
    # hull + cabin + funnel + waves
    c.tri(x + 6, y + 16, x + 38, y + 16, x + 33, y + 26, col)
    c.rect(x + 6, y + 16, 27, 10, col)
    c.rect(x + 26, y + 8, 7, 8, col)
    c.rect(x + 34, y + 11, 3, 5, col)
    c.hline(x + 4, x + 40, y + 30, col)
    c.hline(x + 8, x + 36, y + 32, col)


def icon_megaphone(c, x, y, col):
    # cone + handle + sound arcs
    c.tri(x + 8, y + 12, x + 8, y + 22, x + 30, y + 6, col)
    c.tri(x + 8, y + 12, x + 8, y + 22, x + 30, y + 28, col)
    c.rect(x + 4, y + 12, 5, 10, col)
    c.rect(x + 10, y + 22, 4, 8, col)
    c.ring(x + 36, y + 17, 4, col)
    c.ring(x + 36, y + 17, 8, col)


def icon_chart(c, x, y, col):
    c.rect(x + 8, y + 20, 6, 10, col)
    c.rect(x + 18, y + 14, 6, 16, col)
    c.rect(x + 28, y + 8, 6, 22, col)
    c.hline(x + 4, x + 40, y + 31, col)


ICONS = (icon_missile, icon_globe, icon_cyclone,
         icon_tanker, icon_megaphone, icon_chart)

# ------------------------------------------------------------------- content
NAVY = (15, 32, 64)
GOLD = (242, 183, 5)
RED = (215, 38, 61)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BODY = (51, 51, 51)
BORDER = (217, 217, 217)

PANELS = [
    ("UKRAINE", (192, 57, 43),
     "MISSILES HIT KYIV",
     "Russian ballistic missiles strike the capital overnight; "
     "fire in a 3-storey block in Obolonskyi district."),
    ("CLIMATE", (30, 132, 73),
     "COP31 CLOSES IN ANTALYA",
     "Final draft drops fossil-fuel language; first summit to "
     "admit the 1.5\u00b0C goal will be missed."),
    ("WEATHER", (36, 113, 163),
     "CYCLONE AKVAN HITS INDIA",
     "Landfall near Gopalpur, Odisha by noon; winds to 110 km/h; "
     "nearly 300,000 evacuated."),
    ("ENERGY", (202, 111, 30),
     "TANKERS HIT IN HORMUZ",
     "Two oil tankers hit naval mines in the Strait of Hormuz, "
     "Iran's Guards say; oil prices jump."),
    ("EUROPE", (108, 52, 131),
     "ITALY STOPS FOR A DAY",
     "CGIL's 24-hour general strike: marches in about 100 cities; "
     "buses, metro and trams disrupted."),
    ("MARKETS", (17, 122, 101),
     "TAIWAN CURBS SHORT SELLING",
     "New curbs take effect after the Taiex plunged 4.4%; stocks "
     "down 3.5% cannot be shorted below close."),
]

COL_X = (24, 520)
ROW_Y = (132, 416, 700)
PANEL_W, PANEL_H = 480, 268
TOPBAR_H = 34

# Fact chip text per panel (same order as PANELS).
FACT_CHIPS = (
    "OBOLONSKYI DISTRICT",
    "1.5\u00b0C GOAL WILL BE MISSED",
    "NEARLY 300,000 EVACUATED",
    "OIL PRICES JUMP",
    "MARCHES IN 100 CITIES",
    "TAIEX FELL 4.4% THURSDAY",
)


def draw_panel(c, idx, kicker, color, headline, body):
    px = COL_X[idx % 2]
    py = ROW_Y[idx // 2]
    # panel fill + border
    c.rect(px, py, PANEL_W, PANEL_H, WHITE)
    c.rect(px, py, PANEL_W, 2, BORDER)
    c.rect(px, py + PANEL_H - 2, PANEL_W, 2, BORDER)
    c.rect(px, py, 2, PANEL_H, BORDER)
    c.rect(px + PANEL_W - 2, py, 2, PANEL_H, BORDER)
    # top bar + kicker + icon
    c.rect(px, py, PANEL_W, TOPBAR_H, color)
    c.draw_text(kicker, px + 16, py + 10, 2, WHITE)
    ICONS[idx](c, px + PANEL_W - 52, py, WHITE)
    # headline, 1-2 lines, scale 3
    head_lines = wrap_text(headline, 3, 3, PANEL_W - 32)
    hy = py + TOPBAR_H + 14
    for ln in head_lines:
        c.draw_text(ln, px + 16, hy, 3, BLACK, spacing=3)
        hy += 21 + 5
    # body, 3 lines, scale 2
    body_lines = wrap_text(body, 2, 2, PANEL_W - 32)
    by = hy + 10
    for ln in body_lines:
        c.draw_text(ln, px + 16, by, 2, BODY, spacing=2)
        by += 14 + 5
    # fact chip at the bottom of the panel, filled with the panel colour
    chip = FACT_CHIPS[idx]
    chip_y = py + PANEL_H - 48
    chip_w = text_width(chip, 2, 2) + 24
    c.rect(px + 16, chip_y, chip_w, 32, color)
    c.draw_text(chip, px + 16 + 12, chip_y + 9, 2, WHITE, spacing=2)


def main():
    c = Canvas(W, H)
    # masthead
    c.rect(0, 0, W, 118, NAVY)
    title = "WORLD NEWS"
    tw = text_width(title, 6, 6)
    c.draw_text(title, (W - tw) // 2, 26, 6, WHITE, spacing=6)
    date = "FRIDAY 20 NOVEMBER 2026"
    dw = text_width(date, 3, 3)
    c.draw_text(date, (W - dw) // 2, 80, 3, GOLD, spacing=3)
    # red rule under masthead
    c.rect(0, 118, W, 6, RED)
    # panels
    for i, (kicker, color, headline, body) in enumerate(PANELS):
        draw_panel(c, i, kicker, color, headline, body)
    # footer strip
    c.rect(0, 984, W, 40, NAVY)
    foot = ("Sources: Reuters - UN News - IMD - LaPresse - FSC  |  "
            "All events Friday 20 November 2026")
    fw = text_width(foot, 2, 1)
    c.draw_text(foot, (W - fw) // 2, 998, 2, WHITE, spacing=1)
    # write output
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path, c)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()

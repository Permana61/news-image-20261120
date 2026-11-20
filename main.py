#!/usr/bin/env python3
"""World News 20 November 2026 — v2 (40 stories, 7 continents).

An entry for the make.fun competition "Sum up 20 November's world news
in one image" (bounty news-image-20261120).

Stdlib-only Python: draws a deterministic newspaper front page
(1024 by 1024 pixels, inside the competition's 1 MiB / 1024x1024 gate)
summarising forty verified world-news stories from Friday 20 November
2026, grouped by continent. No third-party packages, no external fonts,
no images, no network: every pixel is computed in this file.

Run:
    python3 main.py

Writes entry.png to $MAKEFUN_OUTPUT_DIR when set, otherwise to /output.
Running twice produces a byte-identical file.
"""

import os
import struct
import zlib
from binascii import crc32

# --------------------------------------------------------------------------
# 5x7 bitmap font, drawn by hand in this file.
# Each glyph is 7 rows of 5 cells; '#' is ink, '.' is blank.
# --------------------------------------------------------------------------

FONT = {}


def _glyph(ch, rows):
    FONT[ch] = rows


_glyph('A', (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"))
_glyph('B', ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."))
_glyph('C', (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."))
_glyph('D', ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."))
_glyph('E', ("#####", "#....", "#....", "####.", "#....", "#....", "#####"))
_glyph('F', ("#####", "#....", "#....", "####.", "#....", "#....", "#...."))
_glyph('G', (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."))
_glyph('H', ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"))
_glyph('I', ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"))
_glyph('J', ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."))
_glyph('K', ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"))
_glyph('L', ("#....", "#....", "#....", "#....", "#....", "#....", "#####"))
_glyph('M', ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"))
_glyph('N', ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"))
_glyph('O', (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."))
_glyph('P', ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."))
_glyph('Q', (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"))
_glyph('R', ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"))
_glyph('S', (".####", "#....", "#....", ".###.", "....#", "....#", "####."))
_glyph('T', ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."))
_glyph('U', ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."))
_glyph('V', ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."))
_glyph('W', ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"))
_glyph('X', ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"))
_glyph('Y', ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."))
_glyph('Z', ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"))

_glyph('a', (".....", ".....", ".####", "....#", ".####", "#...#", ".###."))
_glyph('b', ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."))
_glyph('c', (".....", ".....", ".###.", "#....", "#....", "#....", ".###."))
_glyph('d', ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".###."))
_glyph('e', (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."))
_glyph('f', ("..##.", ".#..#", ".#...", "###..", ".#...", ".#...", ".#..."))
_glyph('g', (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"))
_glyph('h', ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"))
_glyph('i', (".....", "..#..", ".....", ".##..", "..#..", "..#..", ".###."))
_glyph('j', ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", ".##.."))
_glyph('k', ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."))
_glyph('l', (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."))
_glyph('m', (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"))
_glyph('n', (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"))
_glyph('o', (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."))
_glyph('p', (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."))
_glyph('q', (".....", ".....", ".####", "#...#", "#...#", ".###.", "....#"))
_glyph('r', (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."))
_glyph('s', (".....", ".....", ".####", "#....", ".###.", "....#", "####."))
_glyph('t', (".#...", ".#...", "###..", ".#...", ".#...", ".#...", "..##."))
_glyph('u', (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"))
_glyph('v', (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."))
_glyph('w', (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."))
_glyph('x', (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"))
_glyph('y', (".....", ".....", "#...#", "#...#", ".####", "....#", ".###."))
_glyph('z', (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"))

_glyph('0', (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."))
_glyph('1', ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."))
_glyph('2', (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"))
_glyph('3', ("####.", "....#", "....#", ".###.", "....#", "....#", "####."))
_glyph('4', ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."))
_glyph('5', ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."))
_glyph('6', (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."))
_glyph('7', ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."))
_glyph('8', (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."))
_glyph('9', (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."))

_glyph(' ', (".....", ".....", ".....", ".....", ".....", ".....", "....."))
_glyph('.', (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."))
_glyph(',', (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."))
_glyph(':', (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."))
_glyph(';', (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."))
_glyph("'", ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."))
_glyph('"', (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."))
_glyph('!', ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."))
_glyph('?', (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."))
_glyph('-', (".....", ".....", ".....", ".###.", ".....", ".....", "....."))
_glyph('(', ("...#.", "..#..", "..#..", "..#..", "..#..", "..#..", "...#."))
_glyph(')', (".#...", "..#..", "..#..", "..#..", "..#..", "..#..", ".#..."))
_glyph('/', ("....#", "...#.", "...#.", "..#..", "..#..", ".#...", "#...."))
_glyph('%', ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"))
_glyph('&', (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"))
_glyph('$', ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."))
_glyph('+', (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."))
_glyph('=', (".....", ".....", "#####", ".....", "#####", ".....", "....."))
_glyph('*', (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."))
_glyph('#', (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."))
_glyph('@', (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."))
_glyph('_', (".....", ".....", ".....", ".....", ".....", ".....", "#####"))
_glyph('~', (".....", ".....", ".#.#.", "#.#.#", ".....", ".....", "....."))
_glyph('\u2022', (".....", "..#..", ".###.", ".###.", "..#..", ".....", "....."))


# --------------------------------------------------------------------------
# Text handling. Curly punctuation and dashes are folded to the ASCII
# glyphs above so every story renders with the same font.
# --------------------------------------------------------------------------

_FOLD = {
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u2013": "-", "\u2014": "-", "\u2026": "...", "\u00a0": " ",
}


def clean(text):
    return "".join(_FOLD.get(ch, ch) for ch in text)


def glyph_rows(ch):
    return FONT.get(ch, FONT["?"])


def text_width(text, scale, spacing=1):
    """Pixel width of text at the given scale (spacing between glyphs)."""
    if not text:
        return 0
    return len(text) * (5 * scale + spacing) - spacing


def wrap_text(text, scale, max_w, spacing=1):
    """Greedy word wrap; returns a list of lines that fit max_w pixels."""
    words = clean(text).split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale, spacing) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# --------------------------------------------------------------------------
# Canvas: an RGB pixel buffer with rectangle and bitmap-text drawing.
# --------------------------------------------------------------------------

class Canvas:
    def __init__(self, width, height, bg):
        self.w = width
        self.h = height
        self.px = bytearray(bg * (width * height))

    def put(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = color

    def fill(self, x, y, w, h, color):
        x0, y0 = max(x, 0), max(y, 0)
        x1, y1 = min(x + w, self.w), min(y + h, self.h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            row = color * (x1 - x0)
            self.px[base:base + (x1 - x0) * 3] = row

    def rect(self, x, y, w, h, color, thick=1):
        self.fill(x, y, w, thick, color)
        self.fill(x, y + h - thick, w, thick, color)
        self.fill(x, y, thick, h, color)
        self.fill(x + w - thick, y, thick, h, color)

    def dot(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                if dx * dx + dy * dy <= r * r:
                    self.put(cx + dx, cy + dy, color)

    def text(self, x, y, s, scale, color, spacing=1, bold=False):
        """Draw text left-aligned at (x, y); returns pixel width drawn."""
        s = clean(s)
        cx = x
        for ch in s:
            rows = glyph_rows(ch)
            for ry in range(7):
                row = rows[ry]
                for rx in range(5):
                    if row[rx] == "#":
                        bx, by = cx + rx * scale, y + ry * scale
                        self.fill(bx, by, scale, scale, color)
                        if bold:
                            self.fill(bx + 1, by, scale, scale, color)
            cx += 5 * scale + spacing
        return cx - x - spacing

    def text_center(self, cx, y, s, scale, color, spacing=1, bold=False):
        w = text_width(clean(s), scale, spacing)
        return self.text(cx - w // 2, y, s, scale, color, spacing, bold)

    def text_right(self, x, y, s, scale, color, spacing=1, bold=False):
        w = text_width(clean(s), scale, spacing)
        return self.text(x - w, y, s, scale, color, spacing, bold)


# --------------------------------------------------------------------------
# PNG encoder (RGB, no interlace, filter None). Deterministic: same pixels
# in, same bytes out — no timestamps or variable chunks.
# --------------------------------------------------------------------------

def _chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", crc32(tag + data) & 0xFFFFFFFF)
    return out


def write_png(path, canvas):
    raw = bytearray()
    for y in range(canvas.h):
        raw.append(0)
        start = y * canvas.w * 3
        raw += canvas.px[start:start + canvas.w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", canvas.w, canvas.h,
                                       8, 2, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# --------------------------------------------------------------------------
# Dotted world map (hand-sketched, 76 x 22 cells). '#' is land.
# --------------------------------------------------------------------------

MAP_GRID = [
    "............................................................................",
    "....##########.................................#############.................",
    "...##############....###......................#########################........",
    "....##############.....#.....##..######........###########################......",
    ".....#############.........##########..........#####################..##......",
    "......###########..........#########............###############....###.......",
    ".......#########...........#######.............############..................",
    "........#####............##########.###.......######..######..................",
    ".........####...........##########...........#####....######..................",
    "..........###..........##########............####.....#####...................",
    ".................######.#########....................#######................",
    ".................################....................########..............",
    ".................################.....................######.###............",
    "..................###############.......................#########...........",
    "..................##############.........................########............",
    "...................############..#.......................#######............",
    "...................###########............................######.............",
    "....................#########.............................####....#..........",
    ".....................#######.....................................##.........",
    "......................##....................................................",
    "...............##############..############.................................",
    "...................##########....########...................................",
]

# --------------------------------------------------------------------------
# The forty stories. Headline + one-line summary + outlet, exactly as
# briefed; figures and names are reproduced verbatim.
# --------------------------------------------------------------------------

# (continent, accent colour, headline, summary, outlet)
SECTIONS = [
    ("ASIA", (185, 28, 28), [
        ("COP31 Deadlocks on Final Day",
         "Draft drops fossil-fuel phase-out; Pacific nations demand action as summit ends in stalemate.",
         "Japan Times"),
        ("Cyclone Akvan Hits Eastern India",
         "Landfall near Gopalpur 70-80 km/h; 300,000+ evacuated in Odisha.",
         "Reuters"),
        ("Hormuz Tanker Attacks Intensify",
         "Iran steps up tanker strikes; one tanker hits a mine and catches fire.",
         "Middle East Eye"),
        ("Taiwan Tightens Short-Selling Curbs",
         "New rules as Taiex plunges 6.4% in worst week since 1991.",
         "Reuters"),
        ("Trump, Xi, Putin Sign Peace Declaration",
         "First three-way summit in Shenzhen agrees nuclear-risk and UN-reform text.",
         "BBC"),
        ("Houthi Missile Hits Riyadh Tower",
         "Missile damages Saudi wealth-fund tower; no injuries.",
         "Sky News"),
        ("IAEA: North Korea Expanding Enrichment",
         "Yongbyon uranium site growing; inspectors barred since 2009.",
         "Euronews"),
        ("Pakistan Kills 22 Militants in Raids",
         "Army storms hideouts near Afghan border in Khyber Pakhtunkhwa.",
         "The Hindu"),
        ("Violence Flares Before Hasina Return",
         "Arson and protests as ousted premier plans comeback; passport bid rejected.",
         "Guardian"),
        ("Mongolian President Resigns",
         "Parliament accepts Khurelsukh's resignation; speaker serves as acting president.",
         "AP"),
        ("Japan Inflation Hits Year's High",
         "Core prices jump as energy subsidies end; Bank of Japan rate hike expected.",
         "Japan Times"),
    ]),
    ("EUROPE", (29, 78, 216), [
        ("Russian Missiles Strike Kyiv Bridges",
         "~30 ballistic missiles hit capital; eight killed, three bridges damaged.",
         "BBC"),
        ("Italy Grinds to Halt in Strike",
         "CGIL general strike stops schools, hospitals, transport in 100 cities.",
         "Reuters"),
        ("Ukraine Allies Meet in Berlin",
         "Coalition vows united stance; US envoy floats NATO-style security guarantees.",
         "France 24"),
        ("Third Strike Hits Crimea Bridge",
         "Ukraine hits Kerch Bridge third time in four days; rail traffic halted.",
         "BBC"),
        ("Russian Objects Breach Polish Airspace",
         "Two missiles and a drone cross border; PM Tusk says no air threat.",
         "Devdiscourse"),
        ("World Court: Myanmar Committed Genocide",
         "ICJ rules 9-6 on Rohingya; first genocide verdict against a state.",
         "BBC"),
        ("UK-EU Youth Mobility Deal Nears",
         "London and Brussels set to approve youth scheme at Friday summit.",
         "BBC"),
        ("GTA 6 Tops $2.3 Billion Sales",
         "Rockstar launch becomes biggest entertainment debut ever, estimates say.",
         "BBC"),
    ]),
    ("NORTH AMERICA", (13, 148, 136), [
        ("Anthropic Jumps 17% on Nasdaq Debut",
         "AI firm closes near $97; record $81.3B IPO values it near $1.5T.",
         "BBC"),
        ("Senate Passes Energy Permitting Overhaul",
         "Bill clears 62-33, fast-tracking power plants and data-center grids.",
         "CNBC"),
        ("Haiti Forces Kill 34 in Raid",
         "Police retake Martissant corridor from gangs after years of control.",
         "Al Jazeera"),
        ("Bukele Registers for Third Term",
         "El Salvador president files for third straight six-year term.",
         "Al Jazeera"),
        ("FAA Halts Juniper Router Rollout",
         "Agency stops installs after router fault caused nationwide ground stop.",
         "AP"),
        ("White House Fires Cyber Director",
         "Sean Cairncross sacked after week of tech outages; Pentagon CIO steps in.",
         "France 24"),
    ]),
    ("AFRICA", (217, 119, 6), [
        ("Drone Strike Kills 10 at Sudan Mine",
         "Attack hits Bajoun gold site in South Kordofan; Amnesty seeks probe.",
         "AllAfrica"),
        ("Dozens Missing After Senegal Boat Sinks",
         "Migrant boat carrying 50-100 capsizes off Yenne; four bodies found.",
         "BBC"),
        ("Somalia Expels UAE Ambassador",
         "Mogadishu accuses Abu Dhabi of undermining its sovereignty.",
         "Africanews"),
        ("Zimbabwe Destroys 250,000 Landmines",
         "HALO Trust milestone, but funding gaps threaten 2030 clearance goal.",
         "Africanews"),
        ("Angola Buys 10% of De Beers",
         "Endiama pays $180M for stake; first gold refinery opens in Luanda.",
         "Reuters"),
    ]),
    ("SOUTH AMERICA", (22, 163, 74), [
        ("US, Venezuela Sign Military Deal",
         "Hegseth inks cooperation pact in Caracas after Maduro's removal.",
         "BBC"),
        ("Brazil Sells $1B to Defend Real",
         "Central bank intervenes as dollar nears 5.93 reais; currency down 18%.",
         "MercoPress"),
        ("Brazil Protects Raoni Ancestral Land",
         "Lula recognizes Kayapo and Yudja lands; uncontacted group emerges.",
         "Al Jazeera"),
        ("Thousands Protest Colombia Tax Plans",
         "Unions march in Bogota; first national strike under President Espriella.",
         "Al Jazeera"),
    ]),
    ("OCEANIA", (147, 51, 234), [
        ("Fiji, Tonga Declare Drought Disasters",
         "El Nino drought parches Pacific islands; Cook Islands brace for Cyclone Xavier.",
         "RNZ Pacific"),
        ("Marathon Champ Banned Three Years",
         "Jepchirchir stripped of Sydney title in doping ban.",
         "ABC Australia"),
        ("Xi: China-Australia Ties Fully Turned",
         "Xi hails reset as Albanese visits Beijing; trade access on agenda.",
         "Guardian Australia"),
        ("Man Charged Over Car-Bomb Research",
         "Sydney man, 35, charged; police say no ongoing threat to public.",
         "Register AU"),
    ]),
    ("ANTARCTICA", (219, 39, 119), [
        ("Mawson Doctor Shares Life on Ice",
         "Station doctor's diary from Antarctica published on 20 November.",
         "Australian Antarctic Division"),
        ("Antarctic Ice Cliffs Collapsing Faster",
         "MIT study: cliffs retreat faster than models, then stabilise; no runaway.",
         "MIT/Science"),
    ]),
]

PAPER = (247, 242, 231)
INK = (26, 26, 26)
MUTED = (90, 86, 76)
RULE = (26, 26, 26)
NAVY = (20, 33, 61)
WHITE = (255, 255, 255)


# --------------------------------------------------------------------------
# Layout. Two passes: measure the story rows first (the canvas is fixed
# at 1024x1024, so measure() must come out <= 1024), then draw. Nothing
# is positioned by hand after this point — every y comes from the running
# cursor, and measure() and draw() use the same steps.
# --------------------------------------------------------------------------

W = 1024
H = 1024
MARGIN = 16
CW = W - 2 * MARGIN
COLS = 4
GUT = 12
COLW = (CW - (COLS - 1) * GUT) // COLS

MASTHEAD = "THE WORLD IN ONE DAY"
DATE_LINE = "FRIDAY 20 NOVEMBER 2026"
STAT_LINE = "40 STORIES \u2022 7 CONTINENTS"
MAP_LABEL = "WHERE IT HAPPENED"
MAP_SPACING = 2
MAP_DOT = 1

HEADER_TOP = 16
MASTHEAD_SCALE = 6
DATE_SCALE = 2
STAT_H = 20
SECTION_H = 12
SECTION_GAP = 2


def cell_height(headline, summary):
    """Height of one story cell: headline (scale 2 bold), summary
    (scale 1), numbered SOURCE tag (scale 1). Headlines wrap to 2 lines
    at the column width; summaries to 2-3 lines."""
    hlines = wrap_text(headline, 2, COLW)
    slines = wrap_text(summary, 1, COLW)
    return (len(hlines) * 15 + 3 + len(slines) * 8 + 2 + 7 + 2,
            hlines, slines)


def build_rows():
    """Precompute every section's story rows and heights (COLS per row)."""
    rows_out = []
    n = 0
    for name, accent, stories in SECTIONS:
        numbered = []
        for headline, summary, outlet in stories:
            n += 1
            numbered.append((n, headline, summary, outlet))
        rows = []
        for i in range(0, len(numbered), COLS):
            group = numbered[i:i + COLS]
            heights = [cell_height(h, s)[0] for _, h, s, _ in group]
            rows.append((group, max(heights)))
        rows_out.append((name, accent, rows))
    return rows_out


def measure(rows_out):
    """Total page height if drawn from HEADER_TOP. The canvas is fixed
    at 1024; this must come out <= 1024."""
    y = HEADER_TOP
    y += max(7 * MASTHEAD_SCALE + 4 + 7 * DATE_SCALE,
             len(MAP_GRID) * MAP_SPACING) + 4
    y += 2 + 4                         # rule + gap
    y += STAT_H + 6                    # stat strip + gap
    for _name, _accent, rows in rows_out:
        y += SECTION_H                 # section header
        for _group, rh in rows:
            y += rh
        y += SECTION_GAP               # gap after section
    y += 2 + 6                         # footer rule + gap
    y += 7 + 4                         # footer line 1
    y += 7 + 10                        # footer line 2 + bottom margin
    return y


def draw_story(c, x, y, num, accent, headline, summary, outlet):
    _h, hlines, slines = cell_height(headline, summary)
    ly = y
    for line in hlines:
        c.text(x, ly, line, 2, INK, bold=True)
        ly += 15
    ly += 3
    for line in slines:
        c.text(x, ly, line, 1, INK)
        ly += 8
    ly += 2
    c.text(x, ly, "%02d  SOURCE: %s" % (num, outlet.upper()),
           1, accent, bold=True)


def draw(c, rows_out):
    c.fill(0, 0, W, H, PAPER)
    # single outer border
    c.rect(8, 8, W - 16, H - 16, RULE, 2)

    y = HEADER_TOP
    # masthead + date (left), dotted world map (right, same band)
    c.text(MARGIN + 4, y, MASTHEAD, MASTHEAD_SCALE, INK, bold=True)
    c.text(MARGIN + 4, y + 7 * MASTHEAD_SCALE + 4, DATE_LINE,
           DATE_SCALE, INK, spacing=2)
    cols = max(len(r) for r in MAP_GRID)
    map_w = cols * MAP_SPACING
    x0 = W - MARGIN - map_w
    for ri, row in enumerate(MAP_GRID):
        for ci, ch in enumerate(row):
            if ch == "#":
                c.dot(x0 + ci * MAP_SPACING + MAP_SPACING // 2,
                      y + ri * MAP_SPACING + MAP_SPACING // 2,
                      MAP_DOT, NAVY)
    y += max(7 * MASTHEAD_SCALE + 4 + 7 * DATE_SCALE,
             len(MAP_GRID) * MAP_SPACING) + 4
    c.fill(MARGIN, y, CW, 2, RULE)
    y += 2 + 4

    # stat strip
    c.fill(MARGIN, y, CW, STAT_H, NAVY)
    c.text_center(W // 2, y + 3, STAT_LINE, 2, WHITE, bold=True)
    y += STAT_H + 6

    # continent sections
    for name, accent, rows in rows_out:
        total = sum(len(group) for group, _ in rows)
        first = rows[0][0][0][0]
        last = rows[-1][0][-1][0]
        c.fill(MARGIN, y, CW, SECTION_H, (232, 226, 211))
        c.fill(MARGIN, y, 6, SECTION_H, accent)
        c.text(MARGIN + 10, y + 2, name, 1, accent, bold=True)
        c.text_right(W - MARGIN - 10, y + 2,
                     "%d STORIES  \u2022  %02d-%02d" % (total, first, last),
                     1, MUTED, bold=True)
        y += SECTION_H
        for group, rh in rows:
            for k, (num, headline, summary, outlet) in enumerate(group):
                x = MARGIN + k * (COLW + GUT)
                draw_story(c, x, y, num, accent, headline, summary, outlet)
            y += rh
        y += SECTION_GAP

    # footer
    c.fill(MARGIN, y, CW, 2, RULE)
    y += 2 + 6
    c.text_center(W // 2, y,
                  "All forty stories verified against reporting published "
                  "on Friday 20 November 2026.", 1, MUTED)
    y += 7 + 4
    c.text_center(W // 2, y,
                  "Drawn by a deterministic Python program (stdlib only). "
                  "No photographs, no external data. 40 stories, 7 continents.",
                  1, MUTED)


def main():
    rows_out = build_rows()
    total = measure(rows_out)
    print("measured total height: %d (canvas %d)" % (total, H))
    if total > H:
        print("OVERFLOW by %d px - layout does not fit" % (total - H))
    canvas = Canvas(W, H, PAPER)
    draw(canvas, rows_out)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    size = write_png(path, canvas)
    print("wrote %s  %dx%d  %d bytes" % (path, canvas.w, canvas.h, size))


if __name__ == "__main__":
    main()

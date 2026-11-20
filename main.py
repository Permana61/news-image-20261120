#!/usr/bin/env python3
"""World News 20 November 2026 — v2 (40 stories, 7 continents).

An entry for the make.fun competition "Sum up 20 November's world news
in one image" (bounty news-image-20261120).

Stdlib-only Python: draws a deterministic newspaper front page
(1800 px wide, height fitted to content) summarising forty verified
world-news stories from Friday 20 November 2026, grouped by continent.
No third-party packages, no external fonts, no images, no network:
every pixel is computed in this file.

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
# Layout. Two passes: measure the story rows first (so the page height
# fits the content exactly), then draw. Nothing is positioned by hand
# after this point — every y comes from the running cursor.
# --------------------------------------------------------------------------

W = 1800
MARGIN = 60
CW = W - 2 * MARGIN
COLW = (CW - 40) // 2
GUT = 40

MASTHEAD = "THE WORLD IN ONE DAY"
DATE_LINE = "FRIDAY 20 NOVEMBER 2026"
STAT_LINE = "40 STORIES \u2022 7 CONTINENTS"
MAP_LABEL = "WHERE IT HAPPENED"
MAP_SPACING = 12
MAP_DOT = 4


def cell_height(headline, summary):
    lines = wrap_text(summary, 2, COLW)
    return 21 + 4 + len(lines) * 15 + 3 + 7 + 12, lines


def build_rows():
    """Precompute every section's story rows and heights."""
    rows_out = []
    n = 0
    for name, accent, stories in SECTIONS:
        numbered = []
        for headline, summary, outlet in stories:
            n += 1
            numbered.append((n, headline, summary, outlet))
        rows = []
        for i in range(0, len(numbered), 2):
            pair = numbered[i:i + 2]
            heights = [cell_height(h, s)[0] for _, h, s, _ in pair]
            rows.append((pair, max(heights)))
        rows_out.append((name, accent, rows))
    return rows_out


def measure(rows_out):
    y = 56                       # masthead title
    y += 77 + 10                 # title + gap
    y += 28 + 12                 # date line + gap
    y += 6 + 14                  # rules + gap
    y += 56 + 18                 # stat strip + gap
    y += 14 + 8                  # map label + gap
    y += len(MAP_GRID) * MAP_SPACING + 22   # map + gap
    for _name, _accent, rows in rows_out:
        y += 52                  # section header
        for _pair, rh in rows:
            y += rh
        y += 16                  # gap after section
    y += 2 + 12                  # footer rule + gap
    y += 14 + 6                  # footer line 1
    y += 7 + 40                  # footer line 2 + bottom margin
    return y


def draw_story(c, x, y, num, accent, headline, summary, outlet):
    num_txt = "%02d" % num
    c.text(x, y + 7, num_txt, 2, accent, bold=True)
    hx = x + text_width(num_txt + " ", 2) + 6
    c.text(hx, y, headline, 3, INK, bold=True)
    _h, lines = cell_height(headline, summary)
    ly = y + 21 + 4
    for line in lines:
        c.text(x, ly, line, 2, INK)
        ly += 15
    ly += 3
    c.text(x, ly, "SOURCE: " + outlet.upper(), 1, accent, bold=True)


def draw(c, rows_out):
    c.fill(0, 0, W, c.h, PAPER)
    # double outer border
    c.rect(24, 24, W - 48, c.h - 48, RULE, 3)
    c.rect(32, 32, W - 64, c.h - 64, RULE, 1)

    y = 56
    c.text_center(W // 2, y, MASTHEAD, 11, INK, bold=True)
    y += 77 + 10
    c.text_center(W // 2, y, DATE_LINE, 4, INK, spacing=2)
    y += 28 + 12
    c.fill(MARGIN, y, CW, 4, RULE)
    c.fill(MARGIN, y + 8, CW, 2, RULE)
    y += 6 + 14

    # stat strip
    c.fill(MARGIN, y, CW, 56, NAVY)
    c.text_center(W // 2, y + 14, STAT_LINE, 4, WHITE, bold=True)
    y += 56 + 18

    # dotted world map
    c.text_center(W // 2, y, MAP_LABEL, 2, MUTED, spacing=2)
    y += 14 + 8
    cols = max(len(r) for r in MAP_GRID)
    map_w = cols * MAP_SPACING
    x0 = (W - map_w) // 2
    for ri, row in enumerate(MAP_GRID):
        for ci, ch in enumerate(row):
            if ch == "#":
                c.dot(x0 + ci * MAP_SPACING + MAP_SPACING // 2,
                      y + ri * MAP_SPACING + MAP_SPACING // 2,
                      MAP_DOT, NAVY)
    y += len(MAP_GRID) * MAP_SPACING + 22

    # continent sections
    for name, accent, rows in rows_out:
        total = sum(len(pair) for pair, _ in rows)
        first = rows[0][0][0][0]
        last = rows[-1][0][-1][0]
        c.fill(MARGIN, y, CW, 52, (232, 226, 211))
        c.fill(MARGIN, y, 10, 52, accent)
        c.text(MARGIN + 24, y + 15, name, 4, accent, bold=True)
        c.text_right(W - MARGIN - 24, y + 17,
                     "%d STORIES  \u2022  %02d-%02d" % (total, first, last),
                     2, MUTED, bold=True)
        y += 52
        for pair, rh in rows:
            for k, (num, headline, summary, outlet) in enumerate(pair):
                x = MARGIN + k * (COLW + GUT)
                draw_story(c, x, y, num, accent, headline, summary, outlet)
            y += rh
        y += 16

    # footer
    c.fill(MARGIN, y, CW, 2, RULE)
    y += 12
    c.text_center(W // 2, y,
                  "All forty stories verified against reporting published "
                  "on Friday 20 November 2026.", 2, MUTED)
    y += 14 + 6
    c.text_center(W // 2, y,
                  "Drawn by a deterministic Python program (stdlib only). "
                  "No photographs, no external data. 40 stories, 7 continents.",
                  1, MUTED)


def main():
    rows_out = build_rows()
    total = measure(rows_out)
    canvas = Canvas(W, total, PAPER)
    draw(canvas, rows_out)
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "entry.png")
    size = write_png(path, canvas)
    print("wrote %s  %dx%d  %d bytes" % (path, canvas.w, canvas.h, size))


if __name__ == "__main__":
    main()

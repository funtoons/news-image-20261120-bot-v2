#!/usr/bin/env python3
"""Draw a one-page newspaper summing up the world's news of Friday,
20 November 2026, as a 1024x1024 PNG.

Standard library only. No network, no clock: two runs
write byte-identical output. The program reads MAKEFUN_OUTPUT_DIR
(falling back to /output) and writes entry.png there.

Layout: masthead with the day's date, a dotted world map with a red
dot per story, then 35 verified stories in three columns.
"""

import os
import struct
import sys
import zlib

WIDTH = 1024
HEIGHT = 1024

PAPER = (247, 242, 230)
INK = (20, 20, 20)
ACCENT = (163, 22, 33)
MUTED = (107, 107, 107)
LAND = (46, 46, 46)

# A 5x7 bitmap font, drawn from scratch. Each glyph is 7 rows of
# 5 pixels ('#' on, '.' off). Lowercase letters render as capitals.
FONT = {
    'A': (
        ".###.",
        "#...#",
        "#...#",
        "#####",
        "#...#",
        "#...#",
        "#...#",
    ),
    'B': (
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#...#",
        "#...#",
        "####.",
    ),
    'C': (
        ".####",
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        ".####",
    ),
    'D': (
        "####.",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "####.",
    ),
    'E': (
        "#####",
        "#....",
        "#....",
        "####.",
        "#....",
        "#....",
        "#####",
    ),
    'F': (
        "#####",
        "#....",
        "#....",
        "####.",
        "#....",
        "#....",
        "#....",
    ),
    'G': (
        ".####",
        "#....",
        "#....",
        "#.###",
        "#...#",
        "#...#",
        ".###.",
    ),
    'H': (
        "#...#",
        "#...#",
        "#...#",
        "#####",
        "#...#",
        "#...#",
        "#...#",
    ),
    'I': (
        "#####",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "#####",
    ),
    'J': (
        "..###",
        "...#.",
        "...#.",
        "...#.",
        "...#.",
        "#..#.",
        ".##..",
    ),
    'K': (
        "#...#",
        "#..#.",
        "#.#..",
        "##...",
        "#.#..",
        "#..#.",
        "#...#",
    ),
    'L': (
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        "#....",
        "#####",
    ),
    'M': (
        "#...#",
        "##.##",
        "#.#.#",
        "#.#.#",
        "#...#",
        "#...#",
        "#...#",
    ),
}

FONT.update({
    'N': (
        "#...#",
        "##..#",
        "##..#",
        "#.#.#",
        "#..##",
        "#..##",
        "#...#",
    ),
    'O': (
        ".###.",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".###.",
    ),
    'P': (
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#....",
        "#....",
        "#....",
    ),
    'Q': (
        ".###.",
        "#...#",
        "#...#",
        "#...#",
        "#.#.#",
        "#..#.",
        ".##.#",
    ),
    'R': (
        "####.",
        "#...#",
        "#...#",
        "####.",
        "#.#..",
        "#..#.",
        "#...#",
    ),
    'S': (
        ".####",
        "#....",
        "#....",
        ".###.",
        "....#",
        "....#",
        "####.",
    ),
    'T': (
        "#####",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
    ),
    'U': (
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".###.",
    ),
    'V': (
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
    ),
    'W': (
        "#...#",
        "#...#",
        "#...#",
        "#.#.#",
        "#.#.#",
        "##.##",
        "#...#",
    ),
    'X': (
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
        ".#.#.",
        "#...#",
        "#...#",
    ),
    'Y': (
        "#...#",
        "#...#",
        ".#.#.",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
    ),
    'Z': (
        "#####",
        "....#",
        "...#.",
        "..#..",
        ".#...",
        "#....",
        "#####",
    ),
    '0': (
        ".###.",
        "#..##",
        "#.#.#",
        "##..#",
        "#...#",
        "#...#",
        ".###.",
    ),
    '1': (
        "..#..",
        ".##..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        ".###.",
    ),
    '2': (
        ".###.",
        "#...#",
        "....#",
        "...#.",
        "..#..",
        ".#...",
        "#####",
    ),
    '3': (
        "####.",
        "....#",
        "....#",
        ".###.",
        "....#",
        "....#",
        "####.",
    ),
    '4': (
        "...#.",
        "..##.",
        ".#.#.",
        "#..#.",
        "#####",
        "...#.",
        "...#.",
    ),
    '5': (
        "#####",
        "#....",
        "####.",
        "....#",
        "....#",
        "#...#",
        ".###.",
    ),
    '6': (
        ".###.",
        "#....",
        "#....",
        "####.",
        "#...#",
        "#...#",
        ".###.",
    ),
    '7': (
        "#####",
        "....#",
        "...#.",
        "...#.",
        "..#..",
        "..#..",
        "..#..",
    ),
    '8': (
        ".###.",
        "#...#",
        "#...#",
        ".###.",
        "#...#",
        "#...#",
        ".###.",
    ),
    '9': (
        ".###.",
        "#...#",
        "#...#",
        ".####",
        "....#",
        "....#",
        ".###.",
    ),
    ' ': (
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
    ),
    '.': (
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
        ".##..",
        ".##..",
    ),
    ',': (
        ".....",
        ".....",
        ".....",
        ".....",
        ".##..",
        ".##..",
        ".#...",
    ),
    ':': (
        ".....",
        ".##..",
        ".##..",
        ".....",
        ".##..",
        ".##..",
        ".....",
    ),
    ';': (
        ".....",
        ".##..",
        ".##..",
        ".....",
        ".##..",
        ".##..",
        ".#...",
    ),
    '!': (
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        "..#..",
        ".....",
        "..#..",
    ),
    '?': (
        ".###.",
        "#...#",
        "....#",
        "...#.",
        "..#..",
        ".....",
        "..#..",
    ),
    "'": (
        "..#..",
        "..#..",
        ".#...",
        ".....",
        ".....",
        ".....",
        ".....",
    ),
    '-': (
        ".....",
        ".....",
        ".....",
        "#####",
        ".....",
        ".....",
        ".....",
    ),
    '/': (
        "....#",
        "....#",
        "...#.",
        "...#.",
        "..#..",
        ".#...",
        "#....",
    ),
    '(': (
        "...#.",
        "..#..",
        ".#...",
        ".#...",
        ".#...",
        "..#..",
        "...#.",
    ),
    ')': (
        ".#...",
        "..#..",
        "...#.",
        "...#.",
        "...#.",
        "..#..",
        ".#...",
    ),
    '&': (
        ".##..",
        "#..#.",
        "#..#.",
        ".#...",
        "#.#.#",
        "#..#.",
        ".##.#",
    ),
    '%': (
        "##..#",
        "##.#.",
        "...#.",
        "..#..",
        ".#...",
        "#.##.",
        "#..##",
    ),
    '$': (
        "..#..",
        ".####",
        "#.#..",
        ".###.",
        "..#.#",
        "####.",
        "..#..",
    ),
    '#': (
        ".#.#.",
        ".#.#.",
        "#####",
        ".#.#.",
        "#####",
        ".#.#.",
        ".#.#.",
    ),
    '+': (
        ".....",
        "..#..",
        "..#..",
        "#####",
        "..#..",
        "..#..",
        ".....",
    ),
    '=': (
        ".....",
        ".....",
        "#####",
        ".....",
        "#####",
        ".....",
        ".....",
    ),
    '"': (
        ".#.#.",
        ".#.#.",
        ".....",
        ".....",
        ".....",
        ".....",
        ".....",
    ),
    '*': (
        ".....",
        ".#.#.",
        "..#..",
        "#####",
        "..#..",
        ".#.#.",
        ".....",
    ),
    '@': (
        ".###.",
        "#...#",
        "#.###",
        "#.#.#",
        "#.###",
        "#....",
        ".###.",
    ),
})


CHAR_W = 5
CHAR_H = 7


def char_width(scale):
    return CHAR_W * scale + scale


def text_width(text, scale):
    return len(text) * char_width(scale) - scale


class Canvas:
    """An RGB pixel buffer with tiny drawing helpers."""

    def __init__(self, width, height, color):
        self.width = width
        self.height = height
        self.pixels = bytearray(width * height * 3)
        r, g, b = color
        for i in range(0, len(self.pixels), 3):
            self.pixels[i] = r
            self.pixels[i + 1] = g
            self.pixels[i + 2] = b

    def set_pixel(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i] = color[0]
            self.pixels[i + 1] = color[1]
            self.pixels[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set_pixel(xx, yy, color)

    def draw_char(self, x, y, ch, scale, color):
        glyph = FONT.get(ch.upper())
        if glyph is None:
            return
        for row in range(CHAR_H):
            line = glyph[row]
            for col in range(CHAR_W):
                if line[col] == '#':
                    self.fill_rect(
                        x + col * scale, y + row * scale, scale, scale, color
                    )

    def draw_text(self, x, y, text, scale, color):
        cx = x
        for ch in text:
            self.draw_char(cx, y, ch, scale, color)
            cx += char_width(scale)

    def draw_text_centered(self, y, text, scale, color):
        x = (self.width - text_width(text, scale)) // 2
        self.draw_text(x, y, text, scale, color)


def wrap_text(text, max_chars):
    """Greedy word wrap. Returns a list of lines, each at most
    max_chars characters long."""
    words = text.split(' ')
    lines = []
    current = ''
    for word in words:
        if not current:
            current = word
        elif len(current) + 1 + len(word) <= max_chars:
            current += ' ' + word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def png_chunk(kind, data):
    chunk = struct.pack('>I', len(data)) + kind + data
    chunk += struct.pack('>I', zlib.crc32(kind + data) & 0xFFFFFFFF)
    return chunk


def write_png(canvas, path):
    """Write the canvas as an RGB PNG with no ancillary chunks, so
    the bytes depend only on the pixels."""
    width = canvas.width
    height = canvas.height
    header = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    raw = bytearray()
    row_bytes = width * 3
    for y in range(height):
        raw.append(0)
        start = y * row_bytes
        raw += canvas.pixels[start:start + row_bytes]
    compressed = zlib.compress(bytes(raw), 9)
    png = b'\x89PNG\r\n\x1a\n'
    png += png_chunk(b'IHDR', header)
    png += png_chunk(b'IDAT', compressed)
    png += png_chunk(b'IEND', b'')
    with open(path, 'wb') as handle:
        handle.write(png)
    return len(png)


# Simplified continent outlines as (longitude, latitude) vertices.
# Drawn from general geography; they only need to read as a world map.
CONTINENTS = [
    # North America
    [(-168, 66), (-158, 58), (-152, 60), (-140, 60), (-135, 58),
     (-128, 50), (-125, 42), (-120, 34), (-114, 29), (-110, 24),
     (-105, 20), (-97, 16), (-92, 14), (-86, 12), (-82, 9),
     (-79, 9), (-81, 13), (-84, 16), (-87, 21), (-90, 21),
     (-91, 19), (-97, 26), (-93, 30), (-89, 30), (-84, 30),
     (-81, 25), (-80, 32), (-76, 35), (-74, 40), (-70, 42),
     (-68, 45), (-65, 44), (-60, 47), (-55, 52), (-60, 55),
     (-65, 60), (-68, 58), (-75, 62), (-78, 62), (-85, 66),
     (-92, 66), (-95, 69), (-110, 68), (-125, 70), (-140, 70),
     (-155, 71), (-165, 68), (-168, 66)],
    # Greenland
    [(-58, 64), (-52, 60), (-44, 60), (-40, 64), (-32, 68),
     (-22, 70), (-20, 74), (-30, 76), (-45, 80), (-58, 78),
     (-62, 74), (-60, 70)],
    # South America
    [(-79, 9), (-77, 7), (-72, 12), (-64, 10), (-59, 8),
     (-54, 6), (-51, 4), (-50, 0), (-44, -3), (-38, -5),
     (-35, -8), (-38, -15), (-40, -22), (-48, -27), (-52, -33),
     (-58, -38), (-65, -41), (-68, -50), (-69, -52), (-71, -54),
     (-74, -50), (-73, -44), (-72, -36), (-71, -30), (-70, -22),
     (-75, -15), (-79, -8), (-81, -4), (-80, 0), (-81, 3)],
    # Africa
    [(-17, 15), (-16, 20), (-14, 27), (-10, 31), (-6, 34),
     (-2, 35), (3, 37), (10, 37), (11, 34), (19, 32),
     (25, 32), (30, 31), (32, 31), (35, 28), (37, 22),
     (39, 18), (43, 12), (48, 11), (51, 11), (51, 10),
     (46, 5), (42, 0), (40, -5), (40, -10), (36, -18),
     (35, -22), (33, -26), (29, -32), (26, -34), (20, -35),
     (17, -32), (15, -27), (13, -22), (12, -17), (13, -12),
     (12, -6), (9, 4), (6, 4), (-2, 5), (-8, 5),
     (-13, 8), (-16, 12)],
    # Europe
    [(-10, 36), (-9, 38), (-9, 43), (-4, 44), (-2, 47),
     (-1, 49), (0, 51), (2, 53), (4, 54), (8, 57),
     (7, 58), (10, 59), (6, 60), (5, 62), (10, 64),
     (14, 67), (18, 69), (22, 70), (28, 71), (32, 70),
     (36, 68), (40, 68), (44, 68), (46, 66), (42, 62),
     (40, 58), (36, 56), (32, 52), (30, 48), (28, 45),
     (26, 42), (23, 40), (22, 40), (19, 42), (16, 44),
     (12, 44), (8, 44), (4, 43), (0, 40), (-2, 37),
     (-6, 36)],
    # Asia (Scandinavia is covered by the Europe outline)
    [(27, 37), (30, 36), (33, 36), (36, 36),
     (38, 38), (42, 41), (44, 38), (48, 30), (50, 29),
     (54, 27), (57, 26), (61, 25), (66, 25), (70, 24),
     (72, 20), (76, 10), (77, 8), (80, 13), (80, 16),
     (84, 19), (88, 22), (91, 22), (94, 17), (97, 15),
     (99, 10), (101, 8), (104, 9), (106, 11), (109, 13),
     (109, 18), (108, 21), (110, 21), (114, 22), (117, 24),
     (120, 28), (122, 31), (120, 34), (122, 38), (126, 40),
     (128, 39), (130, 42), (132, 43), (135, 44), (138, 46),
     (140, 50), (142, 52), (142, 55), (146, 59), (150, 60),
     (156, 51), (158, 52), (162, 58), (162, 62), (158, 65),
     (160, 69), (170, 67), (178, 65), (178, 69), (170, 70),
     (160, 70), (150, 70), (140, 72), (130, 72), (120, 73),
     (110, 74), (100, 76), (90, 75), (80, 73), (70, 72),
     (60, 69), (50, 69), (42, 68), (35, 68), (30, 70)],
    # Australia
    [(113, -22), (114, -28), (114, -32), (115, -35), (118, -35),
     (122, -34), (126, -32), (129, -32), (132, -32), (135, -35),
     (137, -35), (140, -38), (144, -38), (147, -39), (150, -37),
     (153, -32), (153, -27), (151, -24), (149, -20), (146, -19),
     (143, -15), (142, -11), (139, -14), (136, -15), (135, -12),
     (132, -12), (130, -13), (127, -14), (124, -16), (121, -19),
     (117, -20), (114, -22)],
    # Japan
    [(130, 31), (132, 33), (134, 34), (135, 35), (137, 36),
     (139, 37), (140, 39), (141, 41), (142, 43), (144, 44),
     (143, 43), (142, 41), (141, 39), (142, 37), (139, 35),
     (137, 34), (134, 33), (132, 32)],
    # United Kingdom
    [(-5, 50), (-4, 52), (-5, 54), (-4, 56), (-3, 58),
     (-1, 57), (0, 54), (1, 52), (0, 51), (-2, 50)],
    # New Zealand
    [(167, -45), (169, -43), (172, -41), (174, -39), (176, -38),
     (178, -38), (176, -40), (174, -41), (171, -43), (168, -46)],
    # Indonesia (schematic island chain)
    [(95, 5), (98, 4), (101, 1), (104, -2), (107, -5),
     (110, -7), (113, -8), (116, -9), (119, -10), (122, -10),
     (125, -9), (128, -6), (131, -4), (134, -3), (137, -3),
     (140, -5), (141, -8), (138, -8), (134, -7), (130, -5),
     (126, -8), (122, -9), (118, -10), (114, -9), (110, -7),
     (106, -6), (102, -2), (99, 1), (96, 4)],
    # Madagascar
    [(44, -16), (47, -15), (50, -16), (49, -20), (47, -24),
     (44, -25), (43, -21), (43, -17)],
    # Sri Lanka
    [(80, 9), (81, 8), (81, 6), (80, 6), (79, 8)],
    # Iceland
    [(-22, 64), (-18, 63), (-14, 64), (-15, 66), (-20, 66),
     (-24, 65)],
]


def point_in_polygon(lon, lat, polygon):
    """Ray casting test for a point inside a polygon."""
    inside = False
    count = len(polygon)
    j = count - 1
    for i in range(count):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if (yi > lat) != (yj > lat):
            cross = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < cross:
                inside = not inside
        j = i
    return inside


def on_land(lon, lat):
    for polygon in CONTINENTS:
        if point_in_polygon(lon, lat, polygon):
            return True
    return False


# Map frame in pixels and the latitude band it shows.
MAP_X = 24
MAP_Y = 138
MAP_W = 976
MAP_H = 200
MAP_LAT_TOP = 75.0
MAP_LAT_BOTTOM = -55.0


def project(lon, lat):
    x = MAP_X + (lon + 180.0) / 360.0 * MAP_W
    y = MAP_Y + (MAP_LAT_TOP - lat) / (MAP_LAT_TOP - MAP_LAT_BOTTOM) * MAP_H
    return int(x), int(y)


# 35 stories, each verified against at least two independent sources
# as first reported on Friday 20 November 2026. Each entry is
# (headline, summary, latitude, longitude).
STORIES = [
    ("Russia hits Kyiv with 110+ missiles overnight",
     "Biggest air raid of November kills 9, wounds 28; Dutch and Austrian embassies damaged.",
     50.45, 30.52),
    ("US stocks plunge as AI trade unwinds",
     "S&P 500 falls 3.7% to 6,910 and Nasdaq 5.3% in the year's sharpest sell-off.",
     40.71, -74.01),
    ("Nvidia shares fall 14% on SEC probe",
     "Reuters: regulator examines potential accounting issues as the chipmaker's stock dives.",
     37.37, -121.96),
    ("EU and UK agree food trade and youth mobility",
     "Brussels summit scraps food checks, links carbon markets, adds 100,000 youth visas a year.",
     50.85, 4.35),
    ("Russian missiles land in Poland, NATO on alert",
     "Two missiles and a drone crash in south-east Poland, no casualties; Warsaw calls it deliberate.",
     50.44, 22.25),
    ("Anthropic IPO closes at record $93.5 billion",
     "Underwriters take the full greenshoe; the AI firm also places $26bn privately.",
     37.77, -122.42),
    ("Claude-assisted proof of Riemann claimed",
     "Anthropic mathematician claims a Claude-assisted proof; experts urge caution as checks go on.",
     37.77, -122.42),
    ("UN chief race deadlocked after ninth straw poll",
     "Grynspan leads 10-4 but two veto powers reject her; no consensus in sight.",
     40.75, -73.97),
    ("COP31 ends its last day with no climate deal",
     "Antalya talks stall as the latest draft drops all mention of fossil fuels.",
     36.90, 30.71),
    ("Cyclone Akvan hits Odisha coast, India",
     "Winds of 70-80 km/h hit near Gopalpur as 370,000 people are evacuated.",
     19.27, 84.92),
    ("Iraqi forces enter militia stronghold",
     "Troops enter Jurf al-Sakhar, the Kataib Hezbollah base, first since 2014.",
     32.93, 44.21),
    ("Saudi-led strikes hit Yemen's Hodeidah port",
     "Strikes hit the port and Sanaa as the Houthis warn airlines to avoid Saudi Arabia.",
     14.80, 42.95),
    ("EU approves EUR 1bn more military aid for Kyiv",
     "The Council mobilises peace facility funds for drones, air defence and shells.",
     50.85, 4.35),
    ("Denmark expels Russian attache over murder plot",
     "PET says Russian intelligence hired Danes to kill rapper Kyivstoner.",
     55.68, 12.57),
    ("Vietnam abolishes death penalty for drug crimes",
     "The National Assembly scraps capital punishment for six offences, including trafficking.",
     21.03, 105.83),
    ("Magnitude 6.7 quake shakes Peru's Andes",
     "The 19:09 tremor near Junin is felt in Lima; no casualties reported yet.",
     -10.85, -75.98),
    ("Jury convicts man who started Palisades fire",
     "Jonathan Rinderknecht, 30, found guilty of arson; the 2025 fire killed 12.",
     34.05, -118.24),
    ("Trump orders contractors to report Congress",
     "Order 14438 makes firms tell the White House about Hill inquiries first.",
     38.90, -77.04),
    ("Judge approves Bayer's $7.25bn Roundup deal",
     "A Missouri court signs off the class settlement over non-Hodgkin lymphoma claims.",
     38.63, -90.20),
    ("Italy clears Tesla assisted driving system",
     "Rome gives temporary approval, the first big EU market to do so.",
     41.90, 12.50),
    ("Migrant caravan of 300 enters southern Mexico",
     "The group crosses into Chiapas, joining 1,500 people heading north.",
     14.90, -92.27),
    ("NASA funds 302 small firms with up to $171m",
     "Funding backs Moon and Mars tech under the SBIR and STTR programmes.",
     38.89, -77.03),
    ("Signal stops AI agents reading chats",
     "iOS 27 and Android builds stop OS agents reading chats, citing privacy.",
     37.77, -122.42),
    ("Prabowo and Xi discuss South China Sea",
     "The leaders meet in Shenzhen and agree $86.8bn of investment commitments.",
     22.54, 114.06),
    ("Three APEC nations urge Russia to accept truce",
     "Australia, Canada and New Zealand press Moscow for a permanent Ukraine ceasefire.",
     22.54, 114.06),
    ("Blast on Iran's Qeshm Island tied to munitions",
     "Tasnim says the explosion came from disposing of unexploded ordnance.",
     26.69, 55.86),
    ("Ram Temple complex construction completed",
     "The Ayodhya complex is finished, the committee chair says; formalities end in December.",
     26.79, 82.20),
    ("South Africa logs 5,590 murders in 3 months",
     "Police release July-September figures: 5,590 murders, 9,908 rapes, 4,362 child victims.",
     -25.75, 28.23),
    ("Mlambo-Ngcuka, ex-deputy president, dies",
     "Phumzile Mlambo-Ngcuka, 71, is mourned after the presidency announces her death.",
     -25.75, 28.23),
    ("Malaysia drops plan to send Rohingya to Turkiye",
     "Kuala Lumpur deletes its announcement on moving 10,000 refugees after training.",
     3.14, 101.69),
    ("Mother of UP chief minister Yogi dies at 91",
     "Savitri Devi dies in Panchur, Uttarakhand; last rites are set for Haridwar.",
     30.15, 78.78),
    ("Harry Kane tears ankle ligament, out for months",
     "Bayern say the striker faces months out after the 1-1 draw with Cologne.",
     48.14, 11.58),
    ("Tom Brady buys into Chelsea FC",
     "The NFL great buys in via Clearlake after leaving Birmingham; price undisclosed.",
     51.48, -0.19),
    ("BTS take Artist of the Year at MAMA Awards",
     "The group wins its eighth top prize on night one in Osaka's Kyocera Dome.",
     34.67, 135.50),
    ("GTA VI album released with 34 original songs",
     "Rockstar's soundtrack features Dua Lipa and Lana Del Rey, among others.",
     40.71, -74.01),
]


def render_page():
    canvas = Canvas(WIDTH, HEIGHT, PAPER)

    # Masthead.
    canvas.draw_text_centered(28, "THE WORLD IN ONE PAGE", 5, INK)
    canvas.draw_text_centered(
        90, "FRIDAY, 20 NOVEMBER 2026 - 35 STORIES - 7 REGIONS", 2, INK
    )
    canvas.fill_rect(24, 112, 976, 3, INK)

    # World map: dotted land, red dot per story.
    canvas.draw_text(24, 122, "WHERE IT HAPPENED", 2, INK)
    legend = "RED DOT = ONE STORY"
    canvas.draw_text(1024 - 24 - text_width(legend, 1), 126, legend, 1, ACCENT)
    canvas.fill_rect(MAP_X, MAP_Y, MAP_W, 1, INK)
    canvas.fill_rect(MAP_X, MAP_Y + MAP_H - 1, MAP_W, 1, INK)
    canvas.fill_rect(MAP_X, MAP_Y, 1, MAP_H, INK)
    canvas.fill_rect(MAP_X + MAP_W - 1, MAP_Y, 1, MAP_H, INK)
    for gx in range(MAP_X + 3, MAP_X + MAP_W - 2, 5):
        lon = (gx - MAP_X) / MAP_W * 360.0 - 180.0
        for gy in range(MAP_Y + 3, MAP_Y + MAP_H - 2, 5):
            lat = MAP_LAT_TOP - (gy - MAP_Y) / MAP_H * (
                MAP_LAT_TOP - MAP_LAT_BOTTOM
            )
            if on_land(lon, lat):
                canvas.fill_rect(gx, gy, 2, 2, LAND)
    for _headline, _summary, lat, lon in STORIES:
        x, y = project(lon, lat)
        canvas.fill_rect(x - 3, y - 3, 7, 7, INK)
        canvas.fill_rect(x - 2, y - 2, 5, 5, ACCENT)
    canvas.fill_rect(24, 348, 976, 2, INK)

    # Stories in three columns, twelve, twelve and eleven.
    col_x = (24, 355, 686)
    col_w = 314
    for index, (headline, summary, _lat, _lon) in enumerate(STORIES):
        col = index // 12
        row = index % 12
        x = col_x[col]
        y = 360 + row * 50
        canvas.draw_text(x, y + 1, "%02d" % (index + 1), 1, ACCENT)
        lines = wrap_text(headline, 24)
        for offset, line in enumerate(lines):
            canvas.draw_text(x + 16, y + offset * 14, line, 2, INK)
        body = wrap_text(summary, 52)
        for offset, line in enumerate(body):
            canvas.draw_text(x + 16, y + 30 + offset * 7, line, 1, INK)
        if row < 11:
            canvas.fill_rect(x, y + 47, col_w, 1, (205, 197, 180))

    # Footer.
    canvas.fill_rect(24, 970, 976, 2, INK)
    canvas.draw_text_centered(
        978, "ALL STORIES FIRST REPORTED ON FRIDAY 20 NOVEMBER 2026", 1, INK
    )
    canvas.draw_text_centered(
        990, "SOURCES: REUTERS, AP, CNN AND OTHERS", 1, MUTED
    )
    return canvas


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(render_page(), path)
    print("wrote %s (%d bytes)" % (path, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())

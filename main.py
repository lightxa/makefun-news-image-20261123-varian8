#!/usr/bin/env python3
"""news-image-20261123 variant 8: one burning ship carries the day.

A broadsheet front page for Monday 23 November 2026. The hero panel is
the day's single most striking moment: Ukrainian sea drones hitting the
Russian corvette Merkury and the cargo ship Angara at Benghazi, Libya,
2,400 km from the front line, as confirmed by President Zelenskyy on
Monday. Six more panels cover the rest of the day across five regions:
COP31 ending with no deal in Antalya, Russian strikes killing 15 around
Kyiv, Nvidia reinstating Jensen Huang as CEO, a factory fire in Java
killing 24, the EU proposing a 22nd Russia sanctions package, and a drone
attack on a police base in Cucuta, Colombia. Pure standard library,
deterministic, no network. Writes one 1024x1024 PNG to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font
# 5x7 bitmap font, written as seven rows of five characters ("#" = ink).
# Only the glyphs the front page needs: capitals, digits and punctuation.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "—": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "*": (".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "$": ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
    "•": (".....", ".....", ".###.", ".###.", ".###.", ".....", "....."),
}

BLANK = (".....",) * 7


def text_w(s, scale):
    return len(s) * (6 * scale) - scale


def wrap(s, max_chars):
    """Greedy word wrap into lines of at most max_chars characters."""
    lines, cur = [], ""
    for word in s.split(" "):
        if cur and len(cur) + 1 + len(word) > max_chars:
            lines.append(cur)
            cur = word
        else:
            cur = (cur + " " + word).strip()
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def get(self, x, y):
        i = (y * self.w + x) * 3
        return self.px[i], self.px[i + 1], self.px[i + 2]

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + (x1 - x0) * 3] = row

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            d = r * r - (yy - cy) ** 2
            if d < 0:
                continue
            dx = int(d ** 0.5)
            self.hline(cx - dx, yy, 2 * dx + 1, c)

    def ring(self, cx, cy, r, c, t=2):
        for k in range(t):
            rr = r - k
            for yy in range(cy - rr, cy + rr + 1):
                d = rr * rr - (yy - cy) ** 2
                if d < 0:
                    continue
                dx = int(d ** 0.5)
                self.set(cx - dx, yy, c)
                self.set(cx + dx, yy, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def tri(self, x0, y0, x1, y1, x2, y2, c):
        """Filled triangle via scanline interpolation."""
        pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        for y in range(ay, cy + 1):
            if y < by:
                t1 = (y - ay) / max(1, by - ay)
                xa = ax + (bx - ax) * t1
            else:
                xa = bx
            t2 = (y - ay) / max(1, cy - ay)
            xb = ax + (cx - ax) * t2
            if xa > xb:
                xa, xb = xb, xa
            self.hline(int(xa), y, int(xb) - int(xa) + 1, c)

    def text(self, x, y, s, c, scale=2):
        s = s.upper()
        cx = x
        for ch in s:
            g = FONT.get(ch, BLANK)
            for r in range(7):
                row = g[r]
                for col in range(5):
                    if row[col] == "#":
                        self.rect(cx + col * scale, y + r * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_c(self, cx, y, s, c, scale=2):
        self.text(cx - text_w(s, scale) // 2, y, s, c, scale)

    def band(self, x, y, w, h, top, bottom):
        """Vertical gradient in h bands, with a 2x2 Bayer dither so the
        blend reads as texture rather than flat colour."""
        bayer = ((0, 2), (3, 1))
        for yy in range(y, y + h):
            f = (yy - y) / max(1, h - 1)
            base = tuple(int(top[i] + (bottom[i] - top[i]) * f)
                         for i in range(3))
            for xx in range(x, x + w):
                d = bayer[yy & 1][xx & 1] - 1
                self.set(xx, yy, tuple(max(0, min(255, v + d))
                                       for v in base))

    def grain(self, x0, y0, x1, y1, amp, seed=12345):
        """Deterministic fine grain over a region. A linear congruential
        generator walks the pixels in order, so two runs agree exactly.
        amp is the largest per-channel shift; keep it small on paper so
        text stays crisp, larger on sky and sea where it reads as spray."""
        x0, y0 = max(0, x0), max(0, y0)
        x1, y1 = min(self.w, x1), min(self.h, y1)
        state = seed & 0x7FFFFFFF
        span = 2 * amp + 1
        for yy in range(y0, y1):
            base = yy * self.w
            for xx in range(x0, x1):
                state = (state * 1103515245 + 12345) & 0x7FFFFFFF
                d = (state >> 16) % span - amp
                if d:
                    i = (base + xx) * 3
                    for k in range(3):
                        v = self.px[i + k] + d
                        self.px[i + k] = 0 if v < 0 else (255 if v > 255 else v)


# ---------------------------------------------------------------- png
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path, cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    data = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(data)
    return len(data)

# ---------------------------------------------------------------- palette
PAPER = (244, 238, 224)     # newsprint cream
CARD = (252, 250, 242)      # panel card
INK = (18, 18, 16)          # near-black print ink
DIM = (96, 88, 76)          # secondary print grey
RED = (178, 34, 28)         # masthead red
DARK = (12, 18, 36)         # hero banner night blue
WHITE = (248, 248, 244)
GOLD = (232, 178, 60)
SKY_TOP = (22, 26, 62)
SKY_LOW = (214, 108, 44)
SEA_TOP = (18, 58, 72)
SEA_LOW = (9, 30, 44)
FLAME_Y = (255, 200, 60)
FLAME_O = (240, 118, 30)
FLAME_R = (198, 48, 20)
SMOKE = (96, 96, 104)
SMOKE_D = (66, 66, 74)


# ---------------------------------------------------------------- hero scene
def scene_hero(cv, x, y, w, h):
    """Dusk at Benghazi: a burning warship under a headline banner."""
    horizon = y + 220
    cv.band(x, y, w, 220, SKY_TOP, SKY_LOW)
    cv.band(x, horizon, w, h - 220, SEA_TOP, SEA_LOW)
    # stars in the upper sky, clear of the banner
    for sx, sy in ((40, 96), (120, 70), (210, 108), (880, 78),
                   (940, 110), (60, 140), (960, 150)):
        cv.set(x + sx, y + sy, WHITE)
        cv.set(x + sx + 1, y + sy, WHITE)
    # distant port cranes on the left horizon
    for cx in (60, 110, 160):
        cv.rect(x + cx, horizon - 52, 6, 52, (20, 26, 44))
        cv.line(x + cx, horizon - 52, x + cx + 42, horizon - 30,
                (20, 26, 44), 3)
        cv.line(x + cx + 42, horizon - 30, x + cx + 42, horizon - 18,
                (20, 26, 44), 2)
    # smoke columns rising from the ship
    for cx, cy, r in ((690, 96, 34), (730, 66, 42), (780, 92, 30),
                      (716, 40, 26), (758, 22, 20)):
        cv.circle(x + cx, y + cy, r, SMOKE)
        cv.circle(x + cx - 8, y + cy + 6, r - 10, SMOKE_D)
    # fireball glow behind the flames
    cv.circle(x + 740, y + 168, 62, (226, 130, 52))
    cv.circle(x + 740, y + 168, 46, FLAME_O)
    cv.circle(x + 740, y + 176, 30, FLAME_Y)
    # hull: long dark silhouette with a raked bow
    cv.rect(x + 470, y + 196, 380, 30, (12, 14, 20))
    cv.tri(x + 850, y + 196, x + 920, y + 214, x + 850, y + 226,
           (12, 14, 20))
    cv.rect(x + 470, y + 226, 450, 8, (12, 14, 20))
    # superstructure, funnel and mast
    cv.rect(x + 560, y + 158, 120, 38, (16, 18, 26))
    cv.rect(x + 700, y + 138, 34, 58, (22, 24, 32))
    cv.rect(x + 700, y + 138, 34, 8, FLAME_R)
    cv.vline(x + 820, y + 118, 80, (16, 18, 26), 4)
    cv.hline(x + 796, y + 118, 52, (16, 18, 26), 3)
    for wx in range(572, 668, 18):
        cv.rect(x + wx, y + 168, 10, 12, (240, 210, 120))
    # flames licking from the deck
    for fx, fh in ((600, 46), (650, 66), (760, 58), (810, 40), (860, 30)):
        cv.tri(x + fx - 16, y + 196, x + fx + 16, y + 196,
               x + fx, y + 196 - fh, FLAME_O)
        cv.tri(x + fx - 8, y + 196, x + fx + 8, y + 196,
               x + fx, y + 196 - fh + 18, FLAME_Y)
    # sea: wave lines, fire reflection, two drone boats
    for wy in range(horizon + 14, y + h - 8, 12):
        span = 40 + ((wy * 7) % 90)
        for wx in range(0, w - span, 150):
            cv.hline(x + wx + ((wy * 13) % 60), wy, span, (52, 104, 122), 2)
    for ry in range(horizon + 10, horizon + 96, 8):
        cv.hline(x + 716, ry, 52 - (ry - horizon) // 4, FLAME_O, 3)
        cv.hline(x + 726, ry + 4, 30, FLAME_Y, 2)
    cv.hline(x + 460, horizon + 2, 470, (220, 230, 235), 2)
    for bx, by in ((250, horizon + 64), (860, horizon + 40)):
        cv.rect(x + bx, by, 26, 8, (10, 12, 16))
        cv.line(x + bx - 30, by + 10, x + bx, by + 6, (200, 210, 215), 2)
        cv.line(x + bx + 26, by + 10, x + bx + 56, by + 6,
                (200, 210, 215), 2)


# ---------------------------------------------------------------- panel scenes
def scene_globe(cv, x, y, w, h):
    """Cracked globe over dry earth, COP31."""
    cv.rect(x, y, w, h, (20, 44, 56))
    cv.circle(x + w // 2, y + 46, 36, (44, 118, 128))
    cv.circle(x + w // 2 - 12, y + 34, 12, (30, 92, 102))
    cv.circle(x + w // 2 + 14, y + 58, 10, (30, 92, 102))
    cv.line(x + w // 2 - 26, y + 14, x + w // 2 - 4, y + 42,
            (235, 235, 225), 3)
    cv.line(x + w // 2 - 4, y + 42, x + w // 2 + 10, y + 66,
            (235, 235, 225), 3)
    cv.line(x + w // 2 + 10, y + 66, x + w // 2 + 2, y + 82,
            (235, 235, 225), 3)
    cv.rect(x, y + h - 18, w, 18, (96, 74, 44))
    cv.line(x + 14, y + h - 18, x + 60, y + h - 6, (60, 44, 26), 2)
    cv.line(x + 60, y + h - 6, x + 120, y + h - 14, (60, 44, 26), 2)
    cv.rect(x + w - 96, y + 8, 88, 22, RED)
    cv.text(x + w - 90, y + 13, "NO DEAL", WHITE, 2)


def scene_kyiv(cv, x, y, w, h):
    """Night skyline with a blast over one tower, Kyiv."""
    cv.rect(x, y, w, h, (14, 18, 38))
    for sx, sy in ((24, 12), (80, 26), (180, 10), (260, 22), (300, 14)):
        cv.set(x + sx, y + sy, (220, 220, 200))
    cv.rect(x, y + h - 34, w, 34, (22, 26, 42))
    for bx, bw, bh in ((10, 30, 44), (48, 24, 60), (80, 34, 38),
                       (200, 28, 52), (236, 30, 66), (274, 26, 42)):
        cv.rect(x + bx, y + h - 34 - bh, bw, bh, (14, 18, 30))
    for wx in range(14, 300, 22):
        for wy in range(y + h - 60, y + h - 38, 12):
            if (wx * 3 + wy) % 5 == 0:
                cv.rect(x + wx, wy, 5, 6, (240, 210, 120))
    bx, by = x + 150, y + 26
    for dx, dy in ((0, -18), (0, 18), (-18, 0), (18, 0),
                   (-13, -13), (13, -13), (-13, 13), (13, 13)):
        cv.line(bx, by, bx + dx, by + dy, FLAME_Y, 3)
    cv.circle(bx, by, 9, FLAME_O)
    cv.circle(bx, by, 4, WHITE)


def scene_chip(cv, x, y, w, h):
    """A green AI chip with a rising arrow, Nvidia."""
    cv.rect(x, y, w, h, (16, 26, 22))
    cv.rect(x + 96, y + 18, 116, 60, (28, 138, 74))
    cv.rect(x + 104, y + 26, 100, 44, (18, 96, 52))
    for px in range(104, 204, 14):
        cv.vline(x + px, y + 10, 8, (180, 190, 185), 2)
        cv.vline(x + px, y + 78, 8, (180, 190, 185), 2)
    for py in range(26, 70, 14):
        cv.hline(x + 88, y + py, 8, (180, 190, 185), 2)
        cv.hline(x + 212, y + py, 8, (180, 190, 185), 2)
    cv.text(x + 128, y + 38, "NVDA", WHITE, 3)
    cv.line(x + 246, y + 74, x + 286, y + 30, (120, 220, 140), 4)
    cv.tri(x + 286, y + 30, x + 268, y + 30, x + 286, y + 48,
           (120, 220, 140))


def scene_factory(cv, x, y, w, h):
    """Factory with flames and smoke, Java."""
    cv.rect(x, y, w, h, (74, 62, 52))
    cv.circle(x + w - 44, y + 22, 15, (232, 196, 120))
    cv.rect(x + 30, y + 44, 150, 48, (52, 48, 46))
    for fx in (30, 80, 130):
        cv.tri(x + fx, y + 44, x + fx + 50, y + 44, x + fx + 25, y + 22,
               (52, 48, 46))
    cv.rect(x + 200, y + 28, 18, 64, (52, 48, 46))
    for wx in range(40, 170, 22):
        cv.rect(x + wx, y + 56, 12, 12, (240, 210, 120))
    for fx, fh in ((70, 26), (110, 38), (150, 24)):
        cv.tri(x + fx - 12, y + 44, x + fx + 12, y + 44,
               x + fx, y + 44 - fh, FLAME_O)
        cv.tri(x + fx - 6, y + 44, x + fx + 6, y + 44,
               x + fx, y + 44 - fh + 12, FLAME_Y)
    for cx, cy, r in ((120, 16, 12), (150, 8, 9), (210, 12, 10)):
        cv.circle(x + cx, y + cy, r, SMOKE)


def scene_eu(cv, x, y, w, h):
    """EU circle of stars with the 22nd package number, Brussels."""
    cv.rect(x, y, w, h, (22, 42, 122))
    cx, cy = x + w // 2, y + 48
    for k in range(12):
        import math
        a = 2 * math.pi * k / 12 - math.pi / 2
        sx = int(cx + 34 * math.cos(a))
        sy = int(cy + 34 * math.sin(a))
        cv.circle(sx, sy, 3, GOLD)
    cv.text(cx - text_w("22", 4) // 2, y + 32, "22", WHITE, 4)
    cv.hline(x + 40, y + 82, w - 80, GOLD, 2)
    cv.text(x + 16, y + 14, "SANCTIONS", GOLD, 2)


def scene_cucuta(cv, x, y, w, h):
    """Police post under a drone, with damaged roofs, Cucuta."""
    cv.rect(x, y, w, h, (52, 56, 78))
    cv.rect(x + 30, y + 40, 110, 52, (232, 228, 218))
    cv.rect(x + 30, y + 40, 110, 12, (28, 74, 150))
    cv.rect(x + 76, y + 64, 18, 28, (28, 74, 150))
    for wx in (40, 106):
        cv.rect(x + wx, y + 58, 12, 10, (40, 60, 90))
    cv.rect(x + 170, y + 58, 90, 34, (150, 120, 92))
    cv.line(x + 170, y + 58, x + 215, y + 44, (120, 80, 50), 3)
    cv.line(x + 215, y + 44, x + 260, y + 58, (120, 80, 50), 3)
    cv.vline(x + 215, y + 44, 14, (120, 80, 50), 2)
    dx, dy = x + 250, y + 22
    cv.rect(dx - 10, dy - 3, 20, 6, (180, 180, 180))
    cv.hline(dx - 22, dy - 6, 16, (200, 200, 200), 2)
    cv.hline(dx + 6, dy - 6, 16, (200, 200, 200), 2)
    cv.circle(dx - 24, dy - 6, 2, (255, 80, 80))
    cv.circle(dx + 28, dy - 6, 2, (255, 80, 80))


PANELS = (
    ("ANTALYA, TURKEY", "CLIMATE TALKS END WITH NO DEAL",
     "RECORD-LONG SUMMIT SPLIT OVER FOSSIL FUELS.",
     scene_globe),
    ("KYIV, UKRAINE", "15 KILLED AS STRIKES HIT KYIV",
     "BOY PULLED ALIVE FROM THE RUBBLE.",
     scene_kyiv),
    ("USA", "HUANG RETURNS AS NVIDIA CEO",
     "FOUNDER REINSTATED AMID TRUMP PRESSURE.",
     scene_chip),
    ("JAVA, INDONESIA", "24 DEAD IN JAVA FACTORY FIRE",
     "SWEETS PLANT BLAZE; ABOUT 30 WORKERS STILL MISSING.",
     scene_factory),
    ("BRUSSELS, EU", "EU PROPOSES 22ND SANCTIONS PACKAGE",
     "BANKS, CRYPTO AND SPORT TARGETED.",
     scene_eu),
    ("CUCUTA, COLOMBIA", "DRONE HITS POLICE BASE IN COLOMBIA",
     "THREE HURT, AN INFANT AMONG THEM; 60 HOMES HIT.",
     scene_cucuta),
)


def draw_panel(cv, x, y, w, h, idx):
    tag, headline, fact, scene = PANELS[idx]
    cv.rect(x, y, w, h, CARD)
    cv.rect(x, y, w, h, INK)  # placeholder overwritten below
    cv.rect(x + 2, y + 2, w - 4, h - 4, CARD)
    scene(cv, x + 8, y + 8, w - 16, 92)
    cv.rect(x + 8, y + 104, w - 16, 2, INK)
    cv.rect(x + 8, y + 116, 10, 10, RED)
    cv.text(x + 24, y + 114, tag, RED, 2)
    hy = y + 138
    for line in wrap(headline, 26):
        cv.text(x + 8, hy, line, INK, 2)
        hy += 16
    fy = hy + 6
    for line in wrap(fact, 26):
        cv.text(x + 8, fy, line, DIM, 2)
        fy += 15


def main():
    cv = Canvas(W, H, PAPER)
    # masthead
    cv.hline(0, 6, W, INK, 3)
    cv.text_c(W // 2, 16, "ONE DAY, SEVEN STORIES", INK, 5)
    cv.text_c(W // 2, 60, "MONDAY 23 NOVEMBER 2026", RED, 3)
    cv.text_c(W // 2, 88, "7 STORIES - 5 REGIONS", DIM, 2)
    cv.hline(0, 110, W, RED, 4)
    # hero: banner headline, then the burning ship, then the sublines
    hx, hy, hw, hh = 16, 118, 992, 384
    scene_hero(cv, hx, hy, hw, hh)
    cv.rect(hx, hy, hw, 84, DARK)
    cv.text_c(W // 2, hy + 10, "ZELENSKY SAYS UKRAINE SANK", WHITE, 4)
    cv.text_c(W // 2, hy + 46, "RUSSIAN WARSHIP OFF LIBYA", WHITE, 4)
    cv.rect(hx, hy + hh - 66, hw, 66, DARK)
    cv.text_c(W // 2, hy + hh - 58,
              "SEVEN SEA DRONES HIT THE CORVETTE MERKURY AND THE CARGO SHIP ANGARA",
              WHITE, 2)
    cv.text_c(W // 2, hy + hh - 38,
              "AT BENGHAZI, 2,400 KM FROM THE FRONT - KA-27 HELICOPTER DESTROYED, 10 WOUNDED",
              (220, 224, 232), 2)
    cv.text_c(W // 2, hy + hh - 18,
              "LIBYAN OFFICIALS SAY THE SHIP WAS BADLY DAMAGED, NOT SUNK",
              GOLD, 2)
    # six story panels, three across and two down
    pw, ph, gap = 320, 216, 16
    for i in range(6):
        draw_panel(cv, 16 + (i % 3) * (pw + gap),
                   514 + (i // 3) * (ph + gap), pw, ph, i)
    # footer ticker: market data, not stories
    cv.rect(0, 968, W, H - 968, DARK)
    cv.hline(0, 968, W, RED, 3)
    cv.text(20, 980,
            "MARKETS: NASDAQ FUTURES +3% - BITCOIN $61,000 - EURO INFLATION 4.0% - SK HYNIX +20%",
            WHITE, 2)
    cv.text(20, 1002,
            "SOURCES: AP, REUTERS, CNN, BBC - ALL STORIES REPORTED MONDAY 23 NOVEMBER 2026",
            (170, 176, 188), 2)
    # fine grain over the picture areas so the file stays dense
    cv.grain(hx, hy, hx + hw, hy + hh, 2, seed=777)
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "entry.png")
    n = write_png(path, cv)
    print("wrote %s (%d bytes)" % (path, n))


if __name__ == "__main__":
    main()

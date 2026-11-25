#!/usr/bin/env python3
"""news-image-20261125: sum up Wednesday 25 November 2026 in one image.

Pure standard library. Renders a 1024x1024 newspaper front page with a
5x7 bitmap font and a hand-rolled PNG encoder, so the output is fully
deterministic: no network, no clock, no randomness. Two runs are
byte-identical.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py   (writes out/entry.png)
Grader: writes /output/entry.png (MAKEFUN_OUTPUT_DIR unset).
"""

import os
import struct
import zlib
from binascii import crc32

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (20, 20, 20)
NAVY = (18, 34, 66)
NAVY_LT = (30, 52, 96)
RED = (176, 30, 36)
GOLD = (197, 146, 44)
CARD = (255, 255, 255)
GREY = (90, 90, 86)
LINE = (180, 175, 160)
TAG_COLORS = [
    (176, 30, 36),    # 1 courts - red
    (45, 45, 45),      # 2 politics - charcoal (distinct from story 1 red)
    (18, 34, 66),     # 3 space - navy
    (176, 90, 10),    # 4 energy - burnt orange
    (20, 90, 70),     # 5 trade - teal green
    (90, 40, 110),    # 6 middle east - purple
]

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, written as strings of '#' / '.'.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '*': ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    '[': ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    ']': ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    '|': ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
}

CHAR_W = 6  # 5 px glyph + 1 px spacing, before scaling


def text_width(text, scale):
    return len(text) * CHAR_W * scale - scale


def wrap_text(text, scale, max_w):
    """Greedy word wrap; returns list of lines that fit max_w pixels."""
    max_chars = max(1, max_w // (CHAR_W * scale))
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            # hard-split an over-long word
            while len(word) > max_chars:
                lines.append(word[:max_chars])
                word = word[max_chars:]
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x, y, w, color, thick=1):
        self.rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.rect(x, y, thick, h, color)

    def circle(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def ring(self, cx, cy, r, color, thick=2):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - thick) ** 2 <= d2 <= r * r:
                    self.set(xx, yy, color)

    def draw_char(self, x, y, ch, scale, color):
        glyph = FONT.get(ch, FONT['?'])
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == '1':
                    self.rect(x + col * scale, y + row * scale,
                              scale, scale, color)

    def draw_text(self, x, y, text, scale, color):
        """Draw one line; text is upper-cased (font is uppercase only)."""
        cx = x
        for ch in text.upper():
            self.draw_char(cx, y, ch, scale, color)
            cx += CHAR_W * scale
        return cx

    def draw_text_centered(self, cx, y, text, scale, color):
        x = cx - text_width(text.upper(), scale) // 2
        self.draw_text(x, y, text, scale, color)
        return x

    def draw_wrapped(self, x, y, text, scale, color, max_w, line_h,
                     max_lines=None):
        lines = wrap_text(text, scale, max_w)
        if max_lines is not None:
            lines = lines[:max_lines]
        for i, line in enumerate(lines):
            self.draw_text(x, y + i * line_h, line, scale, color)
        return y + len(lines) * line_h


# ---------------------------------------------------------------- PNG out
def chunk(ctype, data):
    out = struct.pack(">I", len(data)) + ctype + data
    out += struct.pack(">I", crc32(ctype + data) & 0xFFFFFFFF)
    return out


def write_png(path, canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------- stories
# Headlines + one-line summaries, all verified 25 Nov 2026 against
# Reuters / Xinhua / Al Jazeera / Dawn / Wall Street Journal (see README).
STORIES = [
    {
        "num": "1", "tag": "USA  |  COURTS",
        "head": "HUAWEI GUILTY ON 10 OF 12 COUNTS",
        "body": ("A Brooklyn jury convicts the Chinese telecom giant of bank "
                 "and wire fraud, sanctions breaches and trade-secret theft."),
    },
    {
        "num": "2", "tag": "CHINA  |  POLITICS",
        "head": "SHANGHAI PARTY CHIEF UNDER PROBE",
        "body": ("Chen Jining, a Politburo member, is investigated for "
                 "suspected serious violations of discipline and law, "
                 "Xinhua says."),
    },
    {
        "num": "3", "tag": "SPACE",
        "head": "FIRST PAKISTANI REACHES ORBIT",
        "body": ("Shenzhou-24 lifts off for Tiangong carrying Muhammad "
                 "Zeeshan Ali, the first Pakistani in orbit."),
    },
    {
        "num": "4", "tag": "ENERGY  |  THE GULF",
        "head": "THREE TANKERS HIT MINES IN HORMUZ",
        "body": ("Iran's IRGC says three tankers caught fire after striking "
                 "naval mines in the Strait of Hormuz. The claim is not "
                 "independently verified."),
    },
    {
        "num": "5", "tag": "TRADE",
        "head": "US SET TO HIT 16 ECONOMIES WITH TARIFFS",
        "body": ("Washington is poised to unveil new duties after a probe "
                 "into excess industrial capacity, reports say. Rates are "
                 "not yet set."),
    },
    {
        "num": "6", "tag": "MIDDLE EAST",
        "head": "SECOND HOUTHI STRIKE HITS RIYADH TOWER",
        "body": ("A drone hits the PIF Tower in Riyadh's financial district, "
                 "injuring 11 people, days after the first strike on the "
                 "same tower."),
    },
]


# ---------------------------------------------------------------- icons
def draw_icon(cv, kind, x, y, s, color):
    """Tiny pictogram in a 44x44 box at (x, y); s = unit size."""
    if kind == 0:  # gavel (courts): head, handle, sound block
        cv.rect(x + 4, y + 6, 36, 10, color)
        cv.rect(x + 4, y + 6, 36, 3, (255, 255, 255))
        cv.rect(x + 20, y + 16, 5, 18, color)
        cv.rect(x + 8, y + 36, 28, 5, color)
    elif kind == 1:  # building / party HQ
        cv.rect(x + 12, y + 4, 20, 36, color)
        cv.rect(x + 4, y + 36, 36, 4, color)
        for wy in (12, 20, 28):
            for wx in (17, 25):
                cv.rect(wx, y + wy, 4, 4, PAPER)
    elif kind == 2:  # rocket: body, fins, window, flame
        cv.rect(x + 19, y + 2, 6, 22, color)
        cv.rect(x + 13, y + 18, 6, 12, color)
        cv.rect(x + 25, y + 18, 6, 12, color)
        cv.rect(x + 20, y + 8, 4, 4, PAPER)
        cv.rect(x + 20, y + 24, 4, 6, RED)
        cv.rect(x + 18, y + 30, 8, 4, GOLD)
        cv.rect(x + 14, y + 36, 4, 3, GOLD)
        cv.rect(x + 26, y + 36, 4, 3, GOLD)
    elif kind == 3:  # tanker on waves: hull, bridge, funnel, waves
        cv.rect(x + 4, y + 14, 36, 10, color)
        cv.rect(x + 28, y + 4, 8, 10, color)
        cv.rect(x + 8, y + 8, 5, 6, color)
        cv.rect(x + 4, y + 28, 10, 3, color)
        cv.rect(x + 18, y + 28, 10, 3, color)
        cv.rect(x + 32, y + 28, 8, 3, color)
        cv.rect(x + 11, y + 34, 10, 3, color)
        cv.rect(x + 25, y + 34, 10, 3, color)
    elif kind == 4:  # percent / tariffs
        cv.draw_text(x + 2, y + 2, "%", 5, color)
    elif kind == 5:  # tower struck
        cv.rect(x + 16, y + 2, 12, 38, color)
        cv.rect(x + 10, y + 40, 24, 3, color)
        cv.rect(x + 6, y + 10, 8, 3, RED)
        cv.rect(x + 30, y + 16, 8, 3, RED)
        cv.rect(x + 8, y + 24, 6, 3, GOLD)


# ---------------------------------------------------------------- render
def render():
    cv = Canvas(W, H, PAPER)

    # --- masthead ------------------------------------------------------
    cv.rect(0, 0, W, 148, NAVY)
    cv.rect(0, 148, W, 6, RED)
    cv.draw_text_centered(W // 2, 26, "THE WORLD IN ONE DAY", 5, (255, 255, 255))
    cv.draw_text_centered(W // 2, 76, "WEDNESDAY 25 NOVEMBER 2026", 3,
                          (232, 196, 90))
    cv.draw_text_centered(W // 2, 112, "SIX STORIES THAT DEFINED THE DAY",
                          2, (200, 208, 224))
    # small globe mark left of masthead
    cv.ring(64, 74, 30, (232, 196, 90), 3)
    cv.hline(34, 74, 60, (232, 196, 90), 2)
    cv.vline(64, 44, 60, (232, 196, 90), 2)

    # --- story cards: 2 cols x 3 rows ---------------------------------
    margin, gap = 28, 20
    card_w = (W - 2 * margin - gap) // 2
    card_h = 246
    top = 176
    for idx, st in enumerate(STORIES):
        col, row = idx % 2, idx // 2
        x = margin + col * (card_w + gap)
        y = top + row * (card_h + gap)
        color = TAG_COLORS[idx]
        cv.rect(x, y, card_w, card_h, CARD)
        cv.rect(x, y, card_w, 6, color)
        # border: draw 2px frame
        cv.hline(x, y, card_w, color, 2)
        cv.hline(x, y + card_h - 2, card_w, color, 2)
        cv.vline(x, y, card_h, color, 2)
        cv.vline(x + card_w - 2, y, card_h, color, 2)

        # number disc + tag
        cv.circle(x + 30, y + 34, 16, color)
        cv.draw_text_centered(x + 30, y + 27, st["num"], 2, (255, 255, 255))
        cv.draw_text(x + 56, y + 26, st["tag"], 2, color)

        # icon, top right
        draw_icon(cv, idx, x + card_w - 62, y + 12, 1, color)

        # headline (max 3 lines) + summary (max 4 lines)
        hx, hw = x + 20, card_w - 40
        hy = y + 64
        end_y = cv.draw_wrapped(hx, hy, st["head"], 3, INK, hw, 30,
                                max_lines=3)
        cv.hline(hx, end_y + 8, 60, color, 3)
        cv.draw_wrapped(hx, end_y + 22, st["body"], 2, (40, 40, 40), hw, 20,
                        max_lines=4)

    # --- footer --------------------------------------------------------
    fy = top + 3 * card_h + 2 * gap + 14
    cv.hline(margin, fy, W - 2 * margin, INK, 2)
    cv.draw_text_centered(
        W // 2, fy + 14,
        "SOURCES: REUTERS - XINHUA - AL JAZEERA - DAWN - WALL STREET JOURNAL",
        2, GREY)
    cv.draw_text_centered(W // 2, fy + 40, "ONE DAY, SIX STORIES", 2, INK)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    write_png(os.path.join(out_dir, "entry.png"), render())


if __name__ == "__main__":
    main()

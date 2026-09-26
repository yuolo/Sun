"""Fonts and plain text layout.

* ``FONT``  — Fusion Pixel 12 px (line 14 px): hanzi and Russian text.
* ``SMALL`` — Fusion Pixel 10 px (line 12 px): labels and guesses under glyphs.
* brush glyphs — LXGW WenKai drawn at 40 px with four ink levels, for cards.
"""
from __future__ import annotations

import json
import os
import zlib

import pyxel

ASSETS = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets')
FONT_DIR = os.path.join(ASSETS, 'fonts')

LINE = 14
SMALL_LINE = 12
GLYPH_W = 12  # width of a hanzi in FONT

FONT: pyxel.Font = None  # type: ignore[assignment]
SMALL: pyxel.Font = None  # type: ignore[assignment]


def load() -> None:
    global FONT, SMALL
    FONT = pyxel.Font(os.path.join(FONT_DIR, 'px12.bdf'))
    SMALL = pyxel.Font(os.path.join(FONT_DIR, 'px10.bdf'))


def width(s: str, small: bool = False) -> int:
    return (SMALL if small else FONT).text_width(s)


def draw(x: float, y: float, s: str, col: int, small: bool = False, shadow: int | None = None, outline: int | None = None) -> None:
    font = SMALL if small else FONT
    if outline is not None:
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)):
            pyxel.text(x + dx, y + dy, s, outline, font)
    elif shadow is not None:
        pyxel.text(x + 1, y + 1, s, shadow, font)
    pyxel.text(x, y, s, col, font)


def center(cx: float, y: float, s: str, col: int, small: bool = False, shadow: int | None = None, outline: int | None = None) -> None:
    draw(cx - width(s, small) // 2, y, s, col, small, shadow, outline)


def is_hanzi(ch: str) -> bool:
    o = ord(ch)
    return 0x3400 <= o <= 0x9FFF or 0xF900 <= o <= 0xFAFF


def wrap(s: str, maxw: int, small: bool = False) -> list[str]:
    """Word-wraps Russian text; hanzi may break anywhere."""
    lines: list[str] = []
    for para in s.split('\n'):
        line = ''
        for word in _tokens(para):
            cand = line + word
            if line and width(cand.rstrip(), small) > maxw:
                lines.append(line.rstrip())
                line = word.lstrip()
            else:
                line = cand
        lines.append(line.rstrip())
    return lines


def _tokens(s: str) -> list[str]:
    out: list[str] = []
    cur = ''
    for ch in s:
        if is_hanzi(ch) or ch in '，。！？、：；':
            if cur:
                out.append(cur)
                cur = ''
            out.append(ch)
        elif ch == ' ':
            cur += ch
            out.append(cur)
            cur = ''
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out


# ---------------------------------------------------------------- brush glyphs


class Brush:
    """Large glyphs rendered from LXGW WenKai with four ink levels (0 = empty)."""

    def __init__(self) -> None:
        with open(os.path.join(FONT_DIR, 'brush.json'), encoding='utf-8') as f:
            meta = json.load(f)
        self.size: int = meta['size']
        self.index = {ch: i for i, ch in enumerate(meta['chars'])}
        with open(os.path.join(FONT_DIR, 'brush.bin'), 'rb') as f:
            self.data = zlib.decompress(f.read())
        self.cache: dict[str, pyxel.Image] = {}

    def has(self, ch: str) -> bool:
        return ch in self.index

    def image(self, ch: str) -> pyxel.Image | None:
        img = self.cache.get(ch)
        if img is None:
            i = self.index.get(ch)
            if i is None:
                return None
            n = self.size
            img = pyxel.Image(n, n)
            base = i * n * n
            rows = []
            for y in range(n):
                row = self.data[base + y * n : base + (y + 1) * n]
                rows.append(''.join('0123'[v] for v in row))
            img.set(0, 0, rows)
            self.cache[ch] = img
        return img

    def draw(self, x: float, y: float, ch: str, ink: int, mid: int, light: int, scale: float = 1.0) -> bool:
        img = self.image(ch)
        if img is None:
            return False
        pyxel.pal(3, ink)
        pyxel.pal(2, mid)
        pyxel.pal(1, light)
        n = self.size
        if scale == 1.0:
            pyxel.blt(x, y, img, 0, 0, n, n, 0)
        else:
            # blt scales around the centre of the source region
            off = n * (scale - 1) / 2
            pyxel.blt(x + off, y + off, img, 0, 0, n, n, 0, scale=scale)
        pyxel.pal(3, 3)
        pyxel.pal(2, 2)
        pyxel.pal(1, 1)
        return True


_brush: Brush | None = None


def brush() -> Brush:
    global _brush
    if _brush is None:
        _brush = Brush()
    return _brush

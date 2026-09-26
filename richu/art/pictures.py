"""Illustrations for journal pages (32×32): drawn by code or taken from icons."""
from __future__ import annotations

from collections.abc import Callable

import pyxel

from ..content import lexicon
from . import icons, kit
from . import palette as P

PICTURES: dict[str, Callable[[int, int], None]] = {}
#: words (or glyphs) drawn with an item icon
WORD_ICONS: dict[str, str] = {}


def icon_for(word: str, icon: str) -> None:
    WORD_ICONS[word] = icon


def picture(glyph: str) -> Callable[[Callable[[int, int], None]], Callable[[int, int], None]]:
    """Registers a 32×32 picture for a glyph (the function draws at x, y)."""

    def deco(fn: Callable[[int, int], None]) -> Callable[[int, int], None]:
        PICTURES[glyph] = fn
        return fn

    return deco


def has(glyph: str) -> bool:
    if glyph in PICTURES or glyph in WORD_ICONS:
        return True
    g = lexicon.get(glyph)
    return bool(g and g.icon and icons.has(g.icon))


def draw(glyph: str, x: int, y: int, kind: str = 'picture') -> None:
    pyxel.rect(x, y, 32, 32, P.WHITE)
    fn = PICTURES.get(glyph)
    if fn is not None:
        pyxel.clip(x, y, 32, 32)
        kit.canvas(pyxel)
        fn(x, y)
        pyxel.clip()
        return
    icon = WORD_ICONS.get(glyph, '')
    if not icon and len(glyph) == 1:
        g = lexicon.get(glyph)
        icon = g.icon if g else ''
    if icon and icons.has(icon):
        icons.draw(icon, x + 8, y + 8, 2.0)
        return
    icons.draw('unknown', x + 8, y + 8)

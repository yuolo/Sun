"""Pixel UI parts: panels, buttons, text fields, scroll bars.

Two looks: ``paper`` (the journal, cards, dialogs — rice paper and ink) and
``night`` (the HUD and tooltips — ink with a bronze edge).
"""
from __future__ import annotations

from collections.abc import Callable

import pyxel

from ..art.palette import GOLD, INK, LACQUER, OCHRE, PAPER, PEACH, STONE, VERMILION, WOOD, LAMP
from . import text
from .input import INPUT

STYLES = {
    #        fill   edge  shade  text
    'paper': (PAPER, INK, PEACH, INK),
    'night': (INK, OCHRE, WOOD, PAPER),
    'seal': (VERMILION, LACQUER, LACQUER, PAPER),
    'gold': (GOLD, INK, OCHRE, INK),
}


def panel(x: int, y: int, w: int, h: int, style: str = 'paper', shadow: bool = True) -> None:
    fill, edge, shade, _ = STYLES[style]
    corners = [(cx, cy) for cx in (x, x + w - 1) for cy in (y, y + h - 1)]
    behind = [pyxel.pget(cx, cy) for cx, cy in corners]
    if shadow:
        pyxel.rect(x + 2, y + 2, w, h, INK)
    pyxel.rect(x, y, w, h, fill)
    pyxel.rect(x + 1, y + h - 2, w - 2, 1, shade)
    pyxel.rectb(x, y, w, h, edge)
    # rounded corners: restore what was behind, then step the edge inwards
    for (cx, cy), col in zip(corners, behind):
        pyxel.pset(cx, cy, INK if shadow and cx > x and cy > y else col)
        pyxel.pset(cx + (1 if cx == x else -1), cy + (1 if cy == y else -1), edge)


def rule(x: int, y: int, w: int, col: int = OCHRE) -> None:
    """A dotted separator line."""
    for i in range(0, w, 2):
        pyxel.pset(x + i, y, col)


def seal(x: int, y: int, ch: str, size: int = 16) -> None:
    """A red square seal with a white glyph."""
    pyxel.rect(x, y, size, size, VERMILION)
    pyxel.rectb(x, y, size, size, LACQUER)
    text.draw(x + (size - 12) // 2, y + (size - 14) // 2, ch, PAPER)


class Button:
    def __init__(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        label: str,
        on_click: Callable[[], None] | None = None,
        style: str = 'paper',
        hotkey: int | None = None,
        small: bool = False,
        tooltip: str = '',
    ) -> None:
        self.x, self.y, self.w, self.h = x, y, w, h
        self.label = label
        self.on_click = on_click
        self.style = style
        self.hotkey = hotkey
        self.small = small
        self.enabled = True
        self.visible = True
        self.selected = False
        self.tooltip = tooltip

    @property
    def hovered(self) -> bool:
        return self.visible and INPUT.hover(self.x, self.y, self.w, self.h)

    def update(self) -> bool:
        if not self.visible or not self.enabled:
            return False
        hit = INPUT.click(self.x, self.y, self.w, self.h) or (self.hotkey is not None and INPUT.key(self.hotkey))
        if hit and self.on_click:
            self.on_click()
        return hit

    def draw(self) -> None:
        if not self.visible:
            return
        style = self.style
        if self.selected:
            style = 'seal'
        elif self.enabled and self.hovered:
            style = 'gold'
        panel(self.x, self.y, self.w, self.h, style, shadow=False)
        col = STYLES[style][3] if self.enabled else STONE
        line = text.SMALL_LINE if self.small else text.LINE
        text.center(self.x + self.w // 2, self.y + (self.h - line) // 2 + 1, self.label, col, self.small)


class TextField:
    """One line of typed text (Cyrillic works through the OS text input)."""

    def __init__(self, x: int, y: int, w: int, value: str = '', limit: int = 24, placeholder: str = '') -> None:
        self.x, self.y, self.w = x, y, w
        self.value = value
        self.limit = limit
        self.placeholder = placeholder
        self.focused = True
        self.submitted = False

    def update(self) -> None:
        self.submitted = False
        if INPUT.click(self.x, self.y, self.w, 16):
            self.focused = True
        if not self.focused:
            return
        if INPUT.text:
            clean = ''.join(ch for ch in INPUT.text if ch.isprintable())
            self.value = (self.value + clean)[: self.limit]
        if INPUT.key(pyxel.KEY_BACKSPACE, repeat=True) and self.value:
            self.value = self.value[:-1]
        if INPUT.key(pyxel.KEY_RETURN) or INPUT.key(pyxel.KEY_KP_ENTER):
            self.submitted = True

    def draw(self) -> None:
        pyxel.rect(self.x, self.y, self.w, 16, LAMP if self.focused else PAPER)
        pyxel.rectb(self.x, self.y, self.w, 16, INK)
        if self.value:
            text.draw(self.x + 3, self.y + 1, self.value, INK)
        elif self.placeholder:
            text.draw(self.x + 3, self.y + 1, self.placeholder, STONE)
        if self.focused and (pyxel.frame_count // 15) % 2 == 0:
            cx = self.x + 3 + text.width(self.value) + (1 if self.value else 0)
            pyxel.rect(cx, self.y + 3, 1, 11, VERMILION)


class Scroll:
    """Vertical scrolling for lists: wheel, drag of the bar, keys."""

    def __init__(self, x: int, y: int, w: int, h: int) -> None:
        self.x, self.y, self.w, self.h = x, y, w, h
        self.offset = 0
        self.content = 0

    @property
    def max_offset(self) -> int:
        return max(0, self.content - self.h)

    def update(self, step: int = 14) -> None:
        if INPUT.hover(self.x, self.y, self.w, self.h) and INPUT.wheel:
            self.offset -= INPUT.wheel * step
        if INPUT.key(pyxel.KEY_PAGEDOWN):
            self.offset += self.h - step
        if INPUT.key(pyxel.KEY_PAGEUP):
            self.offset -= self.h - step
        bx = self.x + self.w - 4
        if self.max_offset and INPUT.held and INPUT.inside(bx - 2, self.y, 8, self.h):
            t = (INPUT.my - self.y) / max(1, self.h)
            self.offset = int(t * self.max_offset)
            INPUT.take()
        self.offset = max(0, min(self.max_offset, self.offset))

    def draw_bar(self) -> None:
        if not self.max_offset:
            return
        bx = self.x + self.w - 3
        pyxel.rect(bx, self.y, 2, self.h, PEACH)
        bh = max(8, self.h * self.h // self.content)
        by = self.y + (self.h - bh) * self.offset // self.max_offset
        pyxel.rect(bx, by, 2, bh, OCHRE)

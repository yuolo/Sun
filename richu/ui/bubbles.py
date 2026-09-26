"""Speech bubbles and the narration panel."""
from __future__ import annotations

import pyxel

from ..art.palette import INK, OCHRE, PAPER, PEACH, STONE
from ..core.state import GameState
from ..engine import text
from ..engine.app import H, W
from ..engine.tasks import Future
from . import glyphline

MAX_W = 196
PAD = 4


class Bubble:
    """A line of hanzi above a speaker, with notes under the glyphs."""

    def __init__(self, s: GameState, line: str, anchor: tuple[int, int], auto: int = 0, player: bool = False) -> None:
        self.s = s
        self.line = line
        self.anchor = anchor
        self.fut: Future = Future()
        self.auto = auto
        self.age = 0
        self.player = player
        self.hovered: str | None = None
        self.layout()

    def layout(self) -> None:
        self.rows = glyphline.wrap(self.s, self.line, MAX_W)
        notes = glyphline.has_notes(self.rows)
        self.row_h = glyphline.row_height(notes)
        self.w = max(w for _, w in self.rows) + PAD * 2
        self.h = self.row_h * len(self.rows) + PAD * 2 - (2 if notes else 0)
        ax, ay = self.anchor
        x = ax - self.w // 2
        y = ay - self.h - 6
        self.x = max(2, min(W - self.w - 2, x))
        self.y = max(2, y)
        self.tail_up = False
        if y < 2 and ay + 8 + self.h < H - 20:
            self.y = ay + 8
            self.tail_up = True

    def update(self) -> None:
        self.age += 1
        if self.auto and self.age >= self.auto:
            self.fut.set()

    def draw(self) -> None:
        x, y, w, h = self.x, self.y, self.w, self.h
        fill = PAPER if not self.player else PEACH
        pyxel.rect(x + 2, y + 2, w, h, INK)
        pyxel.rect(x, y, w, h, fill)
        pyxel.rectb(x, y, w, h, INK)
        for cx, cy in ((x, y), (x + w - 1, y), (x, y + h - 1), (x + w - 1, y + h - 1)):
            pyxel.pset(cx, cy, INK)
        ax, ay = self.anchor
        tx = max(x + 4, min(x + w - 5, ax))
        if self.tail_up:
            pyxel.tri(tx - 3, y, tx + 3, y, tx, y - 4, fill)
            pyxel.line(tx - 3, y - 1, tx, y - 4, INK)
            pyxel.line(tx + 3, y - 1, tx, y - 4, INK)
        else:
            pyxel.tri(tx - 3, y + h - 1, tx + 3, y + h - 1, tx, y + h + 3, fill)
            pyxel.line(tx - 3, y + h, tx, y + h + 3, INK)
            pyxel.line(tx + 3, y + h, tx, y + h + 3, INK)
        self.hovered = None
        for i, (cells, _) in enumerate(self.rows):
            hv = glyphline.draw_row(self.s, cells, x + PAD, y + PAD - 1 + i * self.row_h, INK)
            if hv:
                self.hovered = hv


class Narration:
    """A Russian description of something wordless, at the bottom of the screen."""

    def __init__(self, line: str) -> None:
        self.line = line
        self.fut: Future = Future()
        self.lines = text.wrap(line, W - 40)
        self.h = len(self.lines) * text.LINE + 8
        self.age = 0

    def update(self) -> None:
        self.age += 1

    def draw(self) -> None:
        x, w = 14, W - 28
        y = H - self.h - 8
        pyxel.dither(0.85)
        pyxel.rect(x, y, w, self.h, INK)
        pyxel.dither(1.0)
        pyxel.rectb(x, y, w, self.h, OCHRE)
        for i, ln in enumerate(self.lines):
            text.draw(x + 6, y + 4 + i * text.LINE, ln, PAPER)
        if (self.age // 15) % 2:
            pyxel.tri(x + w - 10, y + self.h - 7, x + w - 4, y + self.h - 7, x + w - 7, y + self.h - 4, OCHRE)
        _ = STONE

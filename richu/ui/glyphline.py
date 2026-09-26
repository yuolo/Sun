"""Hanzi text with the player's notes under each glyph (as in Chants of Sennaar).

Under a glyph the player guessed: the guess. Under a confirmed glyph: its
pinyin in the tone colour (or the meaning, if pinyin is switched off). A
cell widens to fit its note, so a phrase with notes takes more room.
"""
from __future__ import annotations

from dataclasses import dataclass

import pyxel

from ..art.palette import INK, JADE, LAMP, OCHRE, PAPER, STONE, TONE_COLORS, VERMILION
from ..content import lexicon
from ..core.phrases import is_han
from ..core.state import GameState
from ..engine import text
from ..engine.input import INPUT

GLYPH = 12
NOTE_MAX = 44


@dataclass
class Cell:
    ch: str
    x: int
    w: int
    note: str = ''
    note_col: int = OCHRE
    han: bool = False


def note_for(s: GameState, ch: str) -> tuple[str, int]:
    if not is_han(ch):
        return '', OCHRE
    g = lexicon.get(ch)
    if g and s.confirmed.get(ch):
        if s.settings.pinyin:
            return g.pinyin, TONE_COLORS.get(g.tone, STONE)
        return g.meaning.split(',')[0], JADE
    guess = s.guesses.get(ch, '')
    return guess, OCHRE


def _fit(note: str) -> str:
    if text.width(note, True) <= NOTE_MAX:
        return note
    while note and text.width(note + '…', True) > NOTE_MAX:
        note = note[:-1]
    return note + '…'


def layout(s: GameState, line: str, notes: bool = True) -> tuple[list[Cell], int]:
    cells: list[Cell] = []
    x = 0
    for ch in line:
        han = is_han(ch)
        if han or ch in '，。！？、：；（）《》':
            w = GLYPH
        else:
            w = max(1, text.width(ch))
        note, col = note_for(s, ch) if notes and han and s.settings.guesses else ('', OCHRE)
        if han and not s.settings.guesses and s.confirmed.get(ch) and s.settings.pinyin:
            note, col = note_for(s, ch)
        note = _fit(note) if note else ''
        if note:
            w = max(w, text.width(note, True) + 2)
        cells.append(Cell(ch, x, w, note, col, han))
        x += w + (1 if han else 0)
    return cells, x


def wrap(s: GameState, line: str, maxw: int, notes: bool = True) -> list[tuple[list[Cell], int]]:
    """Splits a hanzi line into rows no wider than maxw (breaks after punctuation when possible)."""
    rows: list[tuple[list[Cell], int]] = []
    for para in line.split('\n'):
        cells, _ = layout(s, para, notes)
        cur: list[Cell] = []
        start = 0
        for c in cells:
            if cur and c.x + c.w - start > maxw:
                # keep punctuation with the previous glyph
                if c.ch in '，。！？、：；' and len(cur) > 1:
                    pass
                else:
                    rows.append(_shift(cur, start))
                    cur = []
                    start = c.x
            cur.append(c)
        rows.append(_shift(cur, start))
    return rows


def _shift(cells: list[Cell], start: int) -> tuple[list[Cell], int]:
    out = [Cell(c.ch, c.x - start, c.w, c.note, c.note_col, c.han) for c in cells]
    width = (out[-1].x + out[-1].w) if out else 0
    return out, width


def has_notes(rows: list[tuple[list[Cell], int]]) -> bool:
    return any(c.note for cells, _ in rows for c in cells)


def row_height(with_notes: bool) -> int:
    return text.LINE + (text.SMALL_LINE - 2 if with_notes else 0)


def draw_row(s: GameState, cells: list[Cell], x: int, y: int, col: int = INK, hover: bool = True) -> str | None:
    """Draws a row of cells; returns the glyph under the mouse, if any."""
    hovered = None
    for c in cells:
        cx = x + c.x + (c.w - GLYPH) // 2 if c.han else x + c.x
        if c.han and hover and INPUT.inside(x + c.x, y, c.w, row_height(bool(c.note))):
            hovered = c.ch
            pyxel.rect(x + c.x, y + 1, c.w, text.LINE, LAMP)
        gcol = col
        if c.han and s.confirmed.get(c.ch):
            gcol = col
        text.draw(cx, y, c.ch, gcol)
        if c.han and s.confirmed.get(c.ch):
            pyxel.pset(cx + GLYPH, y + 3, VERMILION)
        if c.note:
            nx = x + c.x + (c.w - text.width(c.note, True)) // 2
            text.draw(nx, y + text.LINE - 1, c.note, c.note_col, small=True)
    return hovered


def draw_line(s: GameState, line: str, x: int, y: int, col: int = INK, notes: bool = True, hover: bool = True) -> tuple[int, int, str | None]:
    """Convenience: one unwrapped line. Returns (width, height, hovered glyph)."""
    cells, w = layout(s, line, notes)
    h = row_height(any(c.note for c in cells))
    hovered = draw_row(s, cells, x, y, col, hover)
    return w, h, hovered


def glyph_box(s: GameState, ch: str, x: int, y: int, size: int = 16, selected: bool = False, hover_ok: bool = True) -> bool:
    """A glyph in a square tile (journal grid, palettes). Returns True if hovered."""
    hovered = hover_ok and INPUT.inside(x, y, size, size)
    fill = LAMP if hovered else (PAPER if not selected else VERMILION)
    pyxel.rect(x, y, size, size, fill)
    pyxel.rectb(x, y, size, size, STONE if not selected else INK)
    text.draw(x + (size - GLYPH) // 2, y + (size - text.LINE) // 2 + 1, ch, PAPER if selected else INK)
    if s.confirmed.get(ch):
        pyxel.pset(x + size - 3, y + 2, VERMILION)
        pyxel.pset(x + size - 2, y + 2, VERMILION)
        pyxel.pset(x + size - 3, y + 3, VERMILION)
    return hovered

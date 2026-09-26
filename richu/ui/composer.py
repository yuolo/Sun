"""Writing with glyphs: answering people (AnswerPad) and casting spells (BrushPad).

Both show a palette of every glyph the player has met; a filter field finds
glyphs by the player's guess (type «вода» to find 水) or by pinyin.
"""
from __future__ import annotations

import pyxel

from ..art import palette as P
from ..core import journal
from ..engine import text, ui
from ..engine.app import H, W, Screen
from ..engine.input import INPUT
from . import glyphline
from .session import SESSION

TILE = 17


class GlyphPalette:
    """A paged grid of met glyphs with a filter."""

    def __init__(self, x: int, y: int, cols: int, rows: int, only_confirmed_bright: bool = False) -> None:
        self.x, self.y, self.cols, self.rows = x, y, cols, rows
        self.page = 0
        self.filter = ui.TextField(x, y - 20, 110, '', limit=16, placeholder='поиск…')
        self.filter.focused = False
        self.bright_confirmed = only_confirmed_bright
        self.hovered: str | None = None

    def glyphs(self) -> list[str]:
        s = SESSION.state
        gs = list(reversed(journal.seen_glyphs(s)))
        q = self.filter.value.strip().lower()
        if q:
            def hit(g: str) -> bool:
                from ..content import lexicon

                d = lexicon.get(g)
                if q in s.guesses.get(g, '').lower():
                    return True
                if s.confirmed.get(g) and d and (q in d.pinyin or q in d.meaning.lower()):
                    return True
                return g == q
            gs = [g for g in gs if hit(g)]
        return gs

    @property
    def per_page(self) -> int:
        return self.cols * self.rows

    def update(self) -> str | None:
        """Returns a clicked glyph."""
        self.filter.update()
        gs = self.glyphs()
        pages = max(1, (len(gs) + self.per_page - 1) // self.per_page)
        self.page = min(self.page, pages - 1)
        if INPUT.hover(self.x, self.y, self.cols * TILE, self.rows * TILE) and INPUT.wheel:
            self.page = max(0, min(pages - 1, self.page - INPUT.wheel))
        if pages > 1:
            if INPUT.click(self.x + self.cols * TILE + 2, self.y, 12, 12) or INPUT.key(pyxel.KEY_PAGEUP):
                self.page = max(0, self.page - 1)
            if INPUT.click(self.x + self.cols * TILE + 2, self.y + self.rows * TILE - 12, 12, 12) or INPUT.key(pyxel.KEY_PAGEDOWN):
                self.page = min(pages - 1, self.page + 1)
        chunk = gs[self.page * self.per_page : (self.page + 1) * self.per_page]
        for i, g in enumerate(chunk):
            gx = self.x + (i % self.cols) * TILE
            gy = self.y + (i // self.cols) * TILE
            if INPUT.click(gx, gy, TILE - 1, TILE - 1):
                return g
        return None

    def draw(self) -> None:
        s = SESSION.state
        self.filter.draw()
        gs = self.glyphs()
        chunk = gs[self.page * self.per_page : (self.page + 1) * self.per_page]
        self.hovered = None
        for i, g in enumerate(chunk):
            gx = self.x + (i % self.cols) * TILE
            gy = self.y + (i // self.cols) * TILE
            if self.bright_confirmed and not s.confirmed.get(g):
                pyxel.dither(0.55)
            if glyphline.glyph_box(s, g, gx, gy, TILE - 1):
                self.hovered = g
            pyxel.dither(1.0)
        pages = max(1, (len(gs) + self.per_page - 1) // self.per_page)
        if pages > 1:
            px = self.x + self.cols * TILE + 2
            text.draw(px + 2, self.y - 1, '▲', P.OCHRE)
            text.draw(px + 2, self.y + self.rows * TILE - 13, '▼', P.OCHRE)
            text.draw(px, self.y + self.rows * TILE // 2 - 6, f'{self.page + 1}', P.STONE, small=True)
        if not gs:
            text.draw(self.x + 4, self.y + 4, 'Ничего не найдено', P.STONE, small=True)
        if self.hovered:
            note = s.guesses.get(self.hovered, '')
            if note:
                w = text.width(note, True) + 6
                pyxel.rect(INPUT.mx + 6, INPUT.my - 12, w, 11, P.INK)
                text.draw(INPUT.mx + 9, INPUT.my - 12, note, P.PAPER, small=True)


class Pad(Screen):
    """Shared layout: a panel at the bottom with slots, palette and buttons."""

    title = ''
    ok_label = 'Готово'
    max_len = 8

    def __init__(self) -> None:
        super().__init__()
        self.w, self.h = W - 16, 110
        self.x, self.y = 8, H - self.h - 4
        self.slots: list[str] = []
        self.palette = GlyphPalette(self.x + 8, self.y + 40, 16, 3, only_confirmed_bright=self.bright())
        bx = self.x + self.w - 8
        self.btn_ok = ui.Button(bx - 70, self.y + 6, 70, 16, self.ok_label, style='seal')
        self.btn_del = ui.Button(bx - 70 - 26, self.y + 6, 22, 16, '←')
        self.btn_cancel = ui.Button(self.x + self.w - 70 - 8, self.y + self.h - 20, 70, 15, 'Отмена', small=True)

    def bright(self) -> bool:
        return False

    def update(self) -> None:
        g = self.palette.update()
        if g and len(self.slots) < self.max_len:
            self.slots.append(g)
        if self.btn_del.update() or (INPUT.key(pyxel.KEY_BACKSPACE, repeat=True) and not self.palette.filter.focused):
            if self.slots:
                self.slots.pop()
        # remove a glyph by clicking it in the slots
        sx = self.x + 8
        for i in range(len(self.slots)):
            if INPUT.click(sx + i * 18, self.y + 6, 16, 16):
                self.slots.pop(i)
                break
        if self.btn_ok.update() or (INPUT.key(pyxel.KEY_RETURN) and not self.palette.filter.focused):
            if self.slots:
                self.close(''.join(self.slots))
                return
        if self.btn_cancel.update() or INPUT.key(pyxel.KEY_ESCAPE) or INPUT.right:
            self.close('')

    def draw(self) -> None:
        s = SESSION.state
        ui.panel(self.x, self.y, self.w, self.h, 'paper')
        sx = self.x + 8
        for i in range(self.max_len):
            gx = sx + i * 18
            if i < len(self.slots):
                glyphline.glyph_box(s, self.slots[i], gx, self.y + 6, 16)
            else:
                pyxel.rectb(gx, self.y + 6, 16, 16, P.MIST)
        if self.title:
            text.draw(sx + self.max_len * 18 + 6, self.y + 8, self.title, P.STONE, small=True)
        self.palette.draw()
        self.btn_ok.draw()
        self.btn_del.draw()
        self.btn_cancel.draw()
        self.draw_extra()

    def draw_extra(self) -> None:
        pass


class AnswerPad(Pad):
    title = 'Ответ'
    ok_label = 'Сказать'

    def __init__(self, question: str = '') -> None:
        super().__init__()
        self.question = question


class BrushPad(Pad):
    title = 'Кисть'
    ok_label = 'Написать'
    max_len = 6

    def bright(self) -> bool:
        return True

    def draw_extra(self) -> None:
        s = SESSION.state
        if self.slots and not all(s.confirmed.get(g) for g in self.slots):
            text.draw(self.x + 8, self.y + 25, 'Бледные знаки не подтверждены: выйдет лишь тень смысла.', P.OCHRE, small=True)
        else:
            text.draw(self.x + 8, self.y + 25, 'Напишите знаки, затем выберите, на что направить кисть.', P.STONE, small=True)

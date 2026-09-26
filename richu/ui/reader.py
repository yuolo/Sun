"""Reading a text: grandfather's diary, letters, inscriptions, legends.

The text is shown with the player's notes; when every glyph is confirmed,
the player's own understanding (a Russian retelling) opens below it.
"""
from __future__ import annotations

import pyxel

from ..art import palette as P
from ..art import sketches
from ..content import texts as T
from ..core import journal
from ..engine import text, ui
from ..engine.app import APP, H, W, Screen
from ..engine.input import INPUT
from . import glyphline
from .session import SESSION


class Reader(Screen):
    opaque = True

    def __init__(self, text_id: str) -> None:
        super().__init__()
        self.t = T.text(text_id)
        journal.see(SESSION.state, self.t.zh)
        self.scroll = ui.Scroll(8, 20, W - 16, H - 26)
        self.hovered: str | None = None

    def update(self) -> None:
        self.scroll.update()
        if INPUT.key(pyxel.KEY_ESCAPE) or INPUT.right or INPUT.click(W - 22, 3, 16, 16):
            self.close()
            return
        if self.hovered and INPUT.click_anywhere():
            from .card import GlyphCard

            APP.push(GlyphCard(self.hovered))

    def draw(self) -> None:
        s = SESSION.state
        t = self.t
        paper = P.PAPER if t.kind != 'stone' else P.MIST
        pyxel.cls(paper)
        if t.kind == 'diary':
            for y in range(24, H, 14):
                pyxel.line(10, y + 13, W - 10, y + 13, P.PEACH)
            pyxel.line(24, 18, 24, H, P.ROSE)
        text.draw(10, 4, t.title, P.LACQUER)
        text.draw(W - 19, 4, '×', P.INK)
        done, total = journal.text_progress(s, t)
        info = f'понято знаков: {done}/{total}'
        text.draw(W - 26 - text.width(info, True), 6, info, P.STONE, small=True)
        pyxel.clip(8, 20, W - 16, H - 24)
        y = 22 - self.scroll.offset
        start = y
        if t.date:
            glyphline.draw_line(s, t.date, 30, y, P.STONE, hover=False)
            y += 16
        if t.sketch:
            sketches.draw(t.sketch, W // 2 - 40, y)
            y += 50
        self.hovered = None
        for para in t.zh.split('\n'):
            rows = glyphline.wrap(s, para, W - 50)
            for cells, _ in rows:
                hv = glyphline.draw_row(s, cells, 30, y, P.INK)
                if hv:
                    self.hovered = hv
                y += glyphline.row_height(any(c.note for c in cells))
            y += 4
        if done == total and t.understood:
            y += 4
            ui.rule(30, y, W - 60)
            y += 6
            text.draw(30, y, 'Я понимаю:', P.JADE, small=True)
            y += 12
            for ln in text.wrap(t.understood, W - 60):
                text.draw(30, y, ln, P.INK)
                y += 14
        elif total:
            y += 6
            for ln in text.wrap('Когда все знаки будут подтверждены, смысл откроется целиком.', W - 60, small=True):
                text.draw(30, y, ln, P.STONE, small=True)
                y += 11
        pyxel.clip()
        self.scroll.content = y - start + 8
        self.scroll.draw_bar()

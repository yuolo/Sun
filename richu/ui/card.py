"""The glyph card: a big brush glyph, the player's guess, where it was met, its parts.

After confirmation: pinyin, meaning, voice, origin and living words.
"""
from __future__ import annotations

from typing import Any

import pyxel

from .. import platform
from ..art import palette as P
from ..content import lexicon
from ..content.hanzi_meta import META
from ..content.radicals import RADICALS
from ..core import journal
from ..engine import text, ui
from ..engine.app import H, W, Screen
from ..engine.input import INPUT
from . import glyphline
from .session import SESSION

CW, CH = 280, 164


class GlyphCard(Screen):
    def __init__(self, glyph: str, scene: Any = None) -> None:
        super().__init__()
        self.g = glyph
        self.scene = scene
        s = SESSION.state
        self.x, self.y = (W - CW) // 2, (H - CH) // 2
        self.field = ui.TextField(self.x + 56, self.y + 22, CW - 64, s.guesses.get(glyph, ''), limit=journal.MAX_GUESS, placeholder='что это значит?')
        self.confirmed = bool(s.confirmed.get(glyph))
        self.field.focused = not self.confirmed
        self.buttons: list[ui.Button] = []
        bx = self.x + CW - 8
        for label, action in self._actions():
            w = text.width(label) + 12
            bx -= w + 4
            b = ui.Button(bx, self.y + CH - 20, w, 15, label, style='paper')
            b.action = action  # type: ignore[attr-defined]
            self.buttons.append(b)
        self.scroll = ui.Scroll(self.x + 6, self.y + 42, CW - 12, CH - 66)
        self.hover_line: str | None = None

    def _actions(self) -> list[tuple[str, str]]:
        acts = [('Закрыть', 'close')]
        if self.scene is not None and 'SceneView' in type(self.scene).__name__:
            acts.append(('Спросить…', 'ask'))
        if self.confirmed and platform.can_speak() and SESSION.state.settings.voice:
            acts.append(('Звук', 'speak'))
        return acts

    def save_guess(self) -> None:
        journal.set_guess(SESSION.state, self.g, self.field.value)

    def update(self) -> None:
        self.field.update()
        if self.field.submitted:
            self.save_guess()
            self.close()
            return
        for b in self.buttons:
            if b.update():
                act = b.action  # type: ignore[attr-defined]
                self.save_guess()
                if act == 'close':
                    self.close()
                elif act == 'ask':
                    self.close()
                    self.scene.begin_ask(self.g)
                elif act == 'speak':
                    platform.speak(self.g)
                return
        self.scroll.update()
        if INPUT.key(pyxel.KEY_ESCAPE) or INPUT.right or (INPUT.pressed and not INPUT.inside(self.x, self.y, CW, CH) and INPUT.click_anywhere()):
            self.save_guess()
            self.close()

    def draw(self) -> None:
        s = SESSION.state
        pyxel.dither(0.6)
        pyxel.rect(0, 0, W, H, P.INK)
        pyxel.dither(1.0)
        x, y = self.x, self.y
        ui.panel(x, y, CW, CH, 'paper')
        # big glyph
        pyxel.rect(x + 6, y + 6, 44, 44, P.WHITE)
        pyxel.rectb(x + 6, y + 6, 44, 44, P.STONE)
        pyxel.line(x + 28, y + 7, x + 28, y + 48, P.MIST)
        pyxel.line(x + 7, y + 28, x + 48, y + 28, P.MIST)
        if s.settings.brush_glyphs and text.brush().has(self.g):
            text.brush().draw(x + 8, y + 8, self.g, P.INK, P.STONE, P.GREY)
        else:
            text.draw(x + 22, y + 21, self.g, P.INK)
        g = lexicon.get(self.g)
        if self.confirmed and g:
            ui.seal(x + 38, y + 38, '明', 12)
            text.draw(x + 56, y + 5, g.pinyin, P.TONE_COLORS.get(g.tone, P.STONE))
            text.draw(x + 56 + text.width(g.pinyin) + 8, y + 5, g.meaning, P.INK)
        else:
            text.draw(x + 56, y + 6, 'Ваша догадка:', P.STONE, small=True)
        self.field.draw()
        # body
        body_y = y + 42 + 12
        pyxel.clip(x + 4, body_y, CW - 8, CH - 76)
        yy = body_y - self.scroll.offset
        start = yy
        if self.confirmed and g:
            if g.origin:
                for ln in text.wrap(g.origin, CW - 20, small=True):
                    text.draw(x + 10, yy, ln, P.INK, small=True)
                    yy += 11
                yy += 3
            for zh, py, ru in g.words:
                text.draw(x + 10, yy, zh, P.INK)
                text.draw(x + 14 + text.width(zh), yy + 2, f'{py} — {ru}', P.STONE, small=True)
                yy += 14
        parts = self._parts()
        if parts:
            text.draw(x + 10, yy, 'Части:', P.STONE, small=True)
            px = x + 14 + text.width('Части:', True)
            for ch in parts:
                if lexicon.known(ch):
                    note = s.guesses.get(ch, '') if not s.confirmed.get(ch) else lexicon.get(ch).meaning.split(',')[0]  # type: ignore[union-attr]
                else:
                    note = RADICALS.get(ch, '')
                text.draw(px, yy - 2, ch, P.INK)
                px += 13
                if note:
                    text.draw(px, yy, f'({note})', P.OCHRE, small=True)
                    px += text.width(f'({note})', True) + 4
            yy += 14
        ctx = journal.contexts(s, self.g, 5)
        if ctx:
            text.draw(x + 10, yy, 'Встречалось:', P.STONE, small=True)
            yy += 11
            for line in ctx:
                rows = glyphline.wrap(s, line, CW - 30)
                for cells, _ in rows:
                    glyphline.draw_row(s, cells, x + 14, yy, P.INK, hover=False)
                    yy += glyphline.row_height(any(c.note for c in cells))
                yy += 2
        pyxel.clip()
        self.scroll.content = yy - start
        self.scroll.draw_bar()
        for b in self.buttons:
            b.draw()

    def _parts(self) -> str:
        """Parts the player can read: glyphs of the lexicon and common radicals."""
        meta = META.get(self.g)
        if not meta:
            return ''
        _, layout, parts = meta
        if layout not in ('lr', 'tb', 'wrap', 'repeat'):
            return ''
        return ''.join(p for p in parts if p != self.g and (lexicon.known(p) or p in RADICALS))

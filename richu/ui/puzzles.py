"""Puzzle windows. ``open_puzzle(view, kind, **params)`` returns the player's result."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pyxel

from ..art import icons
from ..art import palette as P
from ..core import talisman as TL
from ..core.talisman import TalismanDef
from ..engine import text, ui
from ..engine.app import APP, H, W, Screen
from ..engine.input import INPUT
from . import audio, glyphline
from .composer import GlyphPalette
from .session import SESSION

PUZZLES: dict[str, Callable[..., Screen]] = {}


def puzzle(kind: str) -> Callable[[type], type]:
    def deco(cls: type) -> type:
        PUZZLES[kind] = cls
        return cls

    return deco


async def open_puzzle(view: Any, kind: str, **params: Any) -> Any:
    cls = PUZZLES.get(kind)
    if cls is None:
        raise KeyError(f'no puzzle window for {kind}')
    return await APP.show(cls(**params))


def dim() -> None:
    pyxel.dither(0.6)
    pyxel.rect(0, 0, W, H, P.INK)
    pyxel.dither(1.0)


# ---------------------------------------------------------------- talisman


@puzzle('talisman')
class TalismanEditor(Screen):
    """Edit an inscription that acts on the world: erase, rewrite or swap glyphs."""

    def __init__(self, talisman: TalismanDef) -> None:
        super().__init__()
        self.t = talisman
        self.text = TL.current(SESSION.state, talisman)
        self.sel: int | None = None
        self.mode = ''  # '' · swap · write
        self.palette = GlyphPalette(24, 118, 15, 2, only_confirmed_bright=True)
        self.b_erase = ui.Button(24, 94, 64, 15, 'Стереть', small=True)
        self.b_write = ui.Button(92, 94, 74, 15, 'Переписать', small=True)
        self.b_swap = ui.Button(170, 94, 74, 15, 'Поменять', small=True)
        self.b_done = ui.Button(W - 80, 94, 56, 15, 'Готово', style='seal', small=True)
        self.message = ''

    def cells(self) -> list[tuple[int, int]]:
        n = len(self.text)
        x0 = W // 2 - n * 12
        return [(x0 + i * 24, 34) for i in range(n)]

    def update(self) -> None:
        s = SESSION.state
        for i, (x, y) in enumerate(self.cells()):
            if INPUT.click(x, y, 22, 26):
                if self.mode == 'swap' and self.sel is not None and self.sel != i:
                    self.text = TL.swap(self.text, self.sel, i)
                    self.sel, self.mode = None, ''
                    audio.sfx('brush')
                else:
                    self.sel = i
                    self.mode = ''
                return
        if self.b_erase.update() and self.sel is not None:
            new = TL.remove(self.text, self.sel)
            if new != self.text:
                self.text = new
                audio.sfx('brush')
            self.sel = None
        if self.b_write.update() and self.sel is not None:
            self.mode = 'write'
        if self.b_swap.update() and self.sel is not None:
            self.mode = 'swap'
        if self.mode == 'write':
            g = self.palette.update()
            if g:
                if not s.confirmed.get(g):
                    self.message = 'Кисть не пишет знак, которого вы не понимаете.'
                else:
                    self.text = TL.replace(self.text, self.sel or 0, g)
                    self.mode, self.sel = '', None
                    self.message = ''
                    audio.sfx('brush')
        if self.b_done.update():
            self.close(self.text)
            return
        if INPUT.cancel():
            self.close(None)

    def draw(self) -> None:
        dim()
        ui.panel(12, 10, W - 24, H - 20, 'paper')
        text.center(W // 2, 14, 'Надпись действует. Измените её — изменится мир.', P.STONE, small=True)
        # yellow talisman paper
        n = len(self.text)
        pw = n * 24 + 16
        pyxel.rect(W // 2 - pw // 2, 28, pw, 40, P.YELLOW)
        pyxel.rectb(W // 2 - pw // 2, 28, pw, 40, P.OCHRE)
        for i, (x, y) in enumerate(self.cells()):
            sel = self.sel == i
            if sel:
                pyxel.rectb(x - 1, y - 1, 24, 28, P.VERMILION)
            if text.brush().has(self.text[i]):
                text.brush().draw(x - 9, y - 7, self.text[i], P.VERMILION, P.RED, P.ORANGE, scale=0.55)
            else:
                text.draw(x + 5, y + 6, self.text[i], P.VERMILION)
        for b in (self.b_erase, self.b_write, self.b_swap):
            b.enabled = self.sel is not None
            b.draw()
        self.b_done.draw()
        hint = {'swap': 'Выберите знак, с которым поменять.', 'write': 'Выберите знак, который написать поверх.'}.get(self.mode, 'Выберите знак на надписи.')
        text.draw(24, 76, self.message or hint, P.VERMILION if self.message else P.STONE, small=True)
        if self.mode == 'write':
            self.palette.draw()


# ---------------------------------------------------------------- choosing


@puzzle('choose')
class Choose(Screen):
    """Pick one of several things (glyph labels and/or icons). Returns the index or None."""

    def __init__(self, prompt: str, options: list[dict[str, str]], cancel: bool = True) -> None:
        super().__init__()
        self.prompt = prompt
        self.options = options
        self.cancel_ok = cancel
        n = len(options)
        self.cw = min(56, (W - 40) // max(1, n))
        self.x0 = W // 2 - n * self.cw // 2

    def rect(self, i: int) -> tuple[int, int, int, int]:
        return self.x0 + i * self.cw + 2, 64, self.cw - 4, 60

    def update(self) -> None:
        for i in range(len(self.options)):
            if INPUT.click(*self.rect(i)):
                audio.sfx('tap')
                self.close(i)
                return
        if self.cancel_ok and INPUT.cancel():
            self.close(None)

    def draw(self) -> None:
        dim()
        s = SESSION.state
        lines = text.wrap(self.prompt, W - 60)
        ui.panel(16, 20, W - 32, 128, 'paper')
        for i, ln in enumerate(lines):
            text.center(W // 2, 26 + i * 14, ln, P.INK)
        for i, opt in enumerate(self.options):
            x, y, w, h = self.rect(i)
            hover = INPUT.inside(x, y, w, h)
            pyxel.rect(x, y, w, h, P.LAMP if hover else P.WHITE)
            pyxel.rectb(x, y, w, h, P.OCHRE)
            if opt.get('icon'):
                icons.draw(opt['icon'], x + w // 2 - 16, y + 4, 2.0)
            label = opt.get('zh', '')
            if label:
                cells, lw = glyphline.layout(s, label)
                glyphline.draw_row(s, cells, x + (w - lw) // 2, y + (38 if opt.get('icon') else 20), P.INK, hover=False)
            if opt.get('ru'):
                text.center(x + w // 2, y + h - 12, opt['ru'], P.STONE, small=True)


# ---------------------------------------------------------------- ancient forms

ANCIENT: dict[str, list[tuple]] = {
    # oracle-bone-like forms drawn with lines and circles on a 28×28 box
    '日': [('circ', 14, 14, 10), ('dot', 14, 14)],
    '月': [('arc', 14, 14, 11), ('line', 10, 12, 16, 12)],
    '山': [('line', 3, 24, 25, 24), ('line', 3, 24, 3, 12), ('line', 14, 24, 14, 4), ('line', 25, 24, 25, 12)],
    '水': [('wave', 14, 3, 14, 25), ('line', 6, 8, 9, 12), ('line', 6, 18, 9, 22), ('line', 22, 8, 19, 12), ('line', 22, 18, 19, 22)],
    '人': [('line', 16, 3, 10, 25), ('line', 14, 11, 20, 21)],
    '火': [('line', 14, 4, 14, 24), ('line', 6, 10, 9, 22), ('line', 22, 10, 19, 22), ('line', 5, 24, 23, 24)],
    '木': [('line', 14, 3, 14, 25), ('line', 6, 6, 14, 12), ('line', 22, 6, 14, 12), ('line', 6, 24, 14, 18), ('line', 22, 24, 14, 18)],
    '门': [('line', 5, 4, 5, 25), ('line', 23, 4, 23, 25), ('line', 5, 4, 11, 4), ('line', 17, 4, 23, 4), ('line', 11, 4, 11, 22), ('line', 17, 4, 17, 22)],
}


def draw_ancient(g: str, x: int, y: int, col: int = P.INK) -> None:
    for op in ANCIENT.get(g, []):
        kind = op[0]
        if kind == 'circ':
            pyxel.circb(x + op[1], y + op[2], op[3], col)
        elif kind == 'dot':
            pyxel.circ(x + op[1], y + op[2], 1, col)
        elif kind == 'line':
            pyxel.line(x + op[1], y + op[2], x + op[3], y + op[4], col)
        elif kind == 'arc':
            # a crescent: the outer circle minus a shifted inner one
            cx, cy, r = x + op[1], y + op[2], op[3]
            ix, iy = cx + 5, cy - 2
            for deg in range(0, 360, 3):
                px, py = cx + r * pyxel.cos(deg), cy + r * pyxel.sin(deg)
                if (px - ix) ** 2 + (py - iy) ** 2 > (r - 1) ** 2:
                    pyxel.pset(round(px), round(py), col)
                qx, qy = ix + (r - 1) * pyxel.cos(deg), iy + (r - 1) * pyxel.sin(deg)
                if (qx - cx) ** 2 + (qy - cy) ** 2 < r * r:
                    pyxel.pset(round(qx), round(qy), col)
        elif kind == 'wave':
            for i in range(op[4] - op[2]):
                pyxel.pset(x + op[1] + round(pyxel.sin(i * 40) * 2), y + op[2] + i, col)


@puzzle('ancient')
class AncientStele(Screen):
    """Match ancient forms carved on a stele with the modern glyphs."""

    def __init__(self, glyphs: str) -> None:
        super().__init__()
        self.glyphs = [g for g in glyphs if g in ANCIENT]
        order = sorted(self.glyphs, key=lambda g: (ord(g) * 7919) % 101)
        self.pool = order
        self.pairs: dict[str, str | None] = {g: None for g in self.glyphs}
        self.sel: str | None = None
        self.done = 0

    def cells(self) -> list[tuple[str, int, int]]:
        n = len(self.glyphs)
        x0 = W // 2 - n * 22
        return [(g, x0 + i * 44 + 6, 44) for i, g in enumerate(self.glyphs)]

    def update(self) -> None:
        if self.done:
            self.done += 1
            if self.done > 40 or INPUT.click_anywhere():
                self.close(True)
            return
        n = len(self.pool)
        px0 = W // 2 - n * 11
        for i, g in enumerate(self.pool):
            if INPUT.click(px0 + i * 22, 118, 20, 20):
                self.sel = g
                audio.sfx('tap')
                return
        for g, x, y in self.cells():
            if INPUT.click(x, y, 32, 60) and self.sel:
                for k, v in self.pairs.items():
                    if v == self.sel:
                        self.pairs[k] = None
                self.pairs[g] = self.sel
                self.sel = None
                from ..core.puzzles import check_ancient

                if check_ancient(self.pairs, ''.join(self.glyphs)):
                    self.done = 1
                    audio.sfx('seal')
                return
        if INPUT.cancel():
            self.close(False)

    def draw(self) -> None:
        dim()
        ui.panel(16, 16, W - 32, H - 30, 'paper')
        text.center(W // 2, 20, 'Древние знаки на стеле. Какой знак стал каким?', P.STONE, small=True)
        s = SESSION.state
        for g, x, y in self.cells():
            pyxel.rect(x, y, 32, 32, P.GREY)
            pyxel.rectb(x, y, 32, 32, P.STONE)
            draw_ancient(g, x + 2, y + 2, P.INK)
            pyxel.rect(x + 6, y + 38, 20, 20, P.WHITE)
            pyxel.rectb(x + 6, y + 38, 20, 20, P.INK)
            if self.pairs[g]:
                text.draw(x + 10, y + 41, self.pairs[g], P.INK)
        n = len(self.pool)
        px0 = W // 2 - n * 11
        for i, g in enumerate(self.pool):
            used = g in self.pairs.values()
            if used:
                pyxel.dither(0.35)
            glyphline.glyph_box(s, g, px0 + i * 22, 118, 20, selected=self.sel == g)
            pyxel.dither(1.0)
        if self.done:
            text.center(W // 2, 146, 'Верно! Знаки выросли из рисунков.', P.JADE)
        else:
            text.center(W // 2, 146, 'Выберите знак внизу, затем древнюю форму.', P.STONE, small=True)

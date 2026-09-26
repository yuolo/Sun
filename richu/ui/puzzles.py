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

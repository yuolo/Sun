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


def show_lines(lines: list[str]) -> None:
    """The player reads what a puzzle window shows: glyphs become met, lines go to the log."""
    from ..core import journal

    st = SESSION.state
    for ln in lines:
        journal.see(st, ln)
        journal.record_line(st, 'puzzle', ln, st.scene)


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
                text.brush().draw(x, y + 2, self.text[i], P.VERMILION, P.RED, P.ORANGE, scale=0.55)
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
        show_lines([o['zh'] for o in options if o.get('zh')])
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


# ---------------------------------------------------------------- the face game


FACE_CX, FACE_CY = 112, 100

# the parts of a face drawn on the blackboard, as click rectangles
FACE_PARTS: dict[str, list[tuple[int, int, int, int]]] = {
    '头发': [(FACE_CX - 32, FACE_CY - 42, 64, 16)],
    '眼睛': [(FACE_CX - 20, FACE_CY - 14, 16, 10), (FACE_CX + 4, FACE_CY - 14, 16, 10)],
    '耳朵': [(FACE_CX - 40, FACE_CY - 10, 10, 22), (FACE_CX + 30, FACE_CY - 10, 10, 22)],
    '鼻子': [(FACE_CX - 5, FACE_CY - 4, 10, 14)],
    '嘴': [(FACE_CX - 12, FACE_CY + 13, 24, 9)],
}


def draw_face(x: int, y: int, chalk: int = P.WHITE) -> None:
    """A chalk face: head, hair, ears, eyes, nose and mouth around (x, y)."""
    pyxel.circb(x - 35, y + 1, 6, chalk)
    pyxel.circb(x + 35, y + 1, 6, chalk)
    pyxel.circ(x, y, 32, P.PINE)
    pyxel.circb(x, y, 32, chalk)
    for i in range(-28, 29, 4):
        pyxel.line(x + i, y - 26 - (28 - abs(i)) // 5, x + i + 2, y - 38 + abs(i) // 3, chalk)
    for ex in (x - 12, x + 12):
        pyxel.circb(ex, y - 9, 4, chalk)
        pyxel.pset(ex, y - 9, chalk)
    pyxel.line(x, y - 2, x - 3, y + 7, chalk)
    pyxel.line(x - 3, y + 7, x + 2, y + 7, chalk)
    for i in range(-9, 10):
        pyxel.pset(x + i, y + 17 + (81 - i * i) // 30, chalk)


@puzzle('face')
class FaceGame(Screen):
    """The teacher names the parts of a face, then asks where each one is."""

    def __init__(self, parts: list[str], lines: list[str] | None = None) -> None:
        super().__init__()
        self.parts = [p for p in parts if p in FACE_PARTS]
        self.lines = lines or [f'这是{p}。' for p in self.parts]
        s = SESSION.state
        show_lines(self.lines)
        order = sorted(self.parts, key=lambda p: (ord(p[0]) * 31) % 17)
        self.questions = [f'{p}在哪儿？' for p in order]
        self.answers = order
        show_lines(self.questions)
        self.phase = 'learn'
        self.step = 0
        self.age = 0
        self.flash = 0
        self.wrong: tuple[int, int] | None = None
        self.done_parts: list[str] = []

    def update(self) -> None:
        self.age += 1
        self.flash = max(0, self.flash - 1)
        if self.phase == 'learn':
            if (self.age > 12 and INPUT.click_anywhere()) or self.age > 90:
                self.step += 1
                self.age = 0
                if self.step >= len(self.parts):
                    self.phase, self.step = 'quiz', 0
            return
        if self.phase == 'done':
            if self.age > 40 or (self.age > 10 and INPUT.click_anywhere()):
                self.close(True)
            return
        if INPUT.cancel():
            self.close(False)
            return
        want = self.answers[self.step]
        for part, rects in FACE_PARTS.items():
            if part not in self.parts:
                continue
            for r in rects:
                if INPUT.click(*r):
                    if part == want:
                        audio.sfx('tap')
                        self.done_parts.append(part)
                        self.step += 1
                        self.age = 0
                        self.wrong = None
                        if self.step >= len(self.answers):
                            self.phase = 'done'
                            audio.sfx('seal')
                    else:
                        self.wrong = (INPUT.mx, INPUT.my)
                        self.flash = 20
                    return

    def draw(self) -> None:
        dim()
        s = SESSION.state
        ui.panel(12, 12, W - 24, H - 24, 'paper')
        # the blackboard with the face
        pyxel.rect(40, 36, 144, 124, P.PINE)
        pyxel.rectb(40, 36, 144, 124, P.WOOD)
        draw_face(FACE_CX, FACE_CY)
        if self.phase == 'learn':
            part = self.parts[self.step]
            for r in FACE_PARTS[part]:
                pyxel.rectb(r[0] - 1, r[1] - 1, r[2] + 2, r[3] + 2, P.YELLOW)
            line = self.lines[self.step] if self.step < len(self.lines) else ''
            cells, lw = glyphline.layout(s, line)
            glyphline.draw_row(s, cells, 196 + (108 - lw) // 2, 80, P.INK, hover=False)
            for i, ln in enumerate(text.wrap('Учительница показывает на доску.', 104, small=True)):
                text.center(250, 128 + i * 11, ln, P.STONE, small=True)
            return
        for part in self.done_parts:
            r = FACE_PARTS[part][0]
            pyxel.circ(r[0] + r[2] + 4, r[1] + 2, 2, P.JADE)
        if self.phase == 'done':
            text.center(250, 80, '你们都很聪明！', P.JADE)
            return
        q = self.questions[self.step]
        cells, lw = glyphline.layout(s, q)
        glyphline.draw_row(s, cells, 196 + (108 - lw) // 2, 80, P.INK, hover=False)
        text.center(250, 140, 'Покажите на доске.', P.STONE, small=True)
        if self.flash and self.wrong:
            text.draw(self.wrong[0] + 4, self.wrong[1] - 14, '不对！', P.VERMILION)


# ---------------------------------------------------------------- the porter's list


def _mini(name: str, x: int, y: int) -> None:
    """A tiny countable thing (about 6×9)."""
    if name == 'bottle':
        pyxel.rect(x + 2, y, 2, 2, P.JADE)
        pyxel.rect(x + 1, y + 2, 4, 7, P.LIGHT_BLUE)
        pyxel.rectb(x + 1, y + 2, 4, 7, P.INK)
    elif name == 'sack':
        pyxel.circ(x + 3, y + 5, 3, P.PAPER)
        pyxel.circb(x + 3, y + 5, 3, P.INK)
        pyxel.line(x + 2, y + 1, x + 4, y + 1, P.WOOD)
    elif name == 'shoes':
        for dx in (0, 5):
            pyxel.rect(x + dx, y + 3, 4, 3, P.JADE)
            pyxel.rect(x + dx, y + 6, 5, 2, P.WHITE)
            pyxel.rectb(x + dx, y + 3, 5, 5, P.INK)
    elif name == 'book':
        pyxel.rect(x, y + 1, 6, 8, P.DARK_BLUE)
        pyxel.rectb(x, y + 1, 6, 8, P.INK)
        pyxel.line(x + 2, y + 3, x + 4, y + 3, P.WHITE)
    else:
        icons.draw(name, x - 4, y - 3, 0.5)


def icon_group(name: str, n: int, x: int, y: int, per_row: int = 5) -> None:
    """``n`` small countable copies of a thing, in rows."""
    step = 12 if name == 'shoes' else 8
    per_row = 3 if name == 'shoes' else per_row
    for i in range(n):
        _mini(name, x + (i % per_row) * step, y + (i // per_row) * 12)


@puzzle('cargo')
class CargoList(Screen):
    """Read a list of goods (number + measure word) and pick the right pile for each line.

    rows: [{'zh': '水　十瓶', 'icon': 'bottle', 'n': 10, 'options': [5, 10, 15]}, …]
    """

    def __init__(self, rows: list[dict[str, Any]], lines: list[str] | None = None, title: str = '单子') -> None:
        super().__init__()
        self.rows = rows
        self.title = title
        self.row = 0
        self.ok: list[bool] = [False] * len(rows)
        self.flash = 0
        self.done = 0
        show_lines(lines or [r['zh'] for r in rows])

    def option_rect(self, i: int) -> tuple[int, int, int, int]:
        return 146 + i * 52, 70, 48, 52

    def update(self) -> None:
        self.flash = max(0, self.flash - 1)
        if self.done:
            self.done += 1
            if self.done > 40 or (self.done > 10 and INPUT.click_anywhere()):
                self.close(True)
            return
        if INPUT.cancel():
            self.close(False)
            return
        for i in range(len(self.rows)):
            if INPUT.click(26, 44 + i * 20, 110, 18):
                self.row = i
                return
        r = self.rows[self.row]
        for i, n in enumerate(r['options']):
            if INPUT.click(*self.option_rect(i)):
                if n == r['n']:
                    self.ok[self.row] = True
                    audio.sfx('tap')
                    nxt = [k for k in range(len(self.rows)) if not self.ok[k]]
                    if nxt:
                        self.row = nxt[0]
                    else:
                        self.done = 1
                        audio.sfx('seal')
                else:
                    self.flash = 25
                return

    def draw(self) -> None:
        dim()
        s = SESSION.state
        ui.panel(12, 12, W - 24, H - 24, 'paper')
        # the list on a slip of paper
        pyxel.rect(22, 22, 118, 20 + len(self.rows) * 20, P.WHITE)
        pyxel.rectb(22, 22, 118, 20 + len(self.rows) * 20, P.STONE)
        cells, lw = glyphline.layout(s, self.title, notes=False)
        glyphline.draw_row(s, cells, 22 + (118 - lw) // 2, 24, P.INK, hover=False)
        for i, r in enumerate(self.rows):
            y = 44 + i * 20
            if i == self.row and not self.done:
                pyxel.rect(24, y - 1, 114, 19, P.LAMP)
            cells, _ = glyphline.layout(s, r['zh'], notes=False)
            glyphline.draw_row(s, cells, 30, y + 2, P.INK, hover=False)
            if self.ok[i]:
                pyxel.circ(132, y + 8, 2, P.JADE)
        if self.done:
            text.center(214, 90, '都对了！', P.JADE)
            return
        r = self.rows[self.row]
        for i, n in enumerate(r['options']):
            x, y, w, h = self.option_rect(i)
            hover = INPUT.inside(x, y, w, h)
            pyxel.rect(x, y, w, h, P.LAMP if hover else P.PAPER)
            pyxel.rectb(x, y, w, h, P.OCHRE)
            icon_group(r['icon'], n, x + 8, y + 8)
        text.center(214, 132, 'Какая груда подходит к строке?', P.STONE, small=True)
        if self.flash:
            text.center(214, 146, '不对！', P.VERMILION)


# ---------------------------------------------------------------- the teahouse tray

TRAY_GOODS: dict[str, tuple[str, str]] = {
    # id: (icon, the word for it)
    'tea': ('tea', '茶'),
    'coffee': ('coffee', '咖啡'),
    'milk': ('milk', '牛奶'),
    'noodles': ('noodles', '面条'),
    'rice': ('rice', '米饭'),
    'beer': ('beer', '啤酒'),
    'water': ('water_glass', '水'),
}


@puzzle('tray')
class TeaTray(Screen):
    """Carry orders: read what a table wants and put it on the tray.

    orders: [{'zh': '两杯茶', 'want': {'tea': 2}}, …]
    """

    def __init__(self, orders: list[dict[str, Any]], lines: list[str] | None = None) -> None:
        super().__init__()
        self.orders = orders
        self.i = 0
        self.tray: list[str] = []
        self.flash = 0
        self.done = 0
        self.shelf = list(TRAY_GOODS)
        self.b_serve = ui.Button(W - 86, 130, 62, 16, '送', style='seal')
        self.b_clear = ui.Button(W - 150, 130, 58, 16, 'Убрать', small=True)
        show_lines(lines or [o['zh'] for o in orders])

    def shelf_rect(self, k: int) -> tuple[int, int, int, int]:
        return 24 + k * 38, 92, 34, 32

    def update(self) -> None:
        from ..core.puzzles import check_list

        self.flash = max(0, self.flash - 1)
        if self.done:
            self.done += 1
            if self.done > 40 or (self.done > 10 and INPUT.click_anywhere()):
                self.close(True)
            return
        if INPUT.cancel():
            self.close(False)
            return
        for k, gid in enumerate(self.shelf):
            if INPUT.click(*self.shelf_rect(k)) and len(self.tray) < 6:
                self.tray.append(gid)
                audio.sfx('tap')
                return
        for k in range(len(self.tray)):
            if INPUT.click(40 + k * 24, 55, 22, 22):
                self.tray.pop(k)
                return
        if self.b_clear.update():
            self.tray = []
        if self.b_serve.update():
            placed: dict[str, int] = {}
            for gid in self.tray:
                placed[gid] = placed.get(gid, 0) + 1
            if not check_list(self.orders[self.i]['want'], placed):
                audio.sfx('seal')
                self.i += 1
                self.tray = []
                if self.i >= len(self.orders):
                    self.done = 1
            else:
                self.flash = 30

    def draw(self) -> None:
        dim()
        s = SESSION.state
        ui.panel(12, 12, W - 24, H - 24, 'paper')
        if self.done:
            text.center(W // 2, 80, '谢谢！你帮了我很大的忙！', P.JADE)
            return
        o = self.orders[self.i]
        text.draw(24, 16, f'Заказ {self.i + 1} из {len(self.orders)}', P.STONE, small=True)
        cells, lw = glyphline.layout(s, o['zh'])
        glyphline.draw_row(s, cells, W // 2 - lw // 2, 26, P.INK, hover=False)
        # the tray
        pyxel.elli(30, 52, 170, 30, P.WOOD)
        pyxel.elli(33, 54, 164, 26, P.OCHRE)
        for k, gid in enumerate(self.tray):
            icons.draw(TRAY_GOODS[gid][0], 43 + k * 24, 58)
        # the shelf: pictures only — read the order and find the things
        for k, gid in enumerate(self.shelf):
            x, y, w, h = self.shelf_rect(k)
            hover = INPUT.inside(x, y, w, h)
            pyxel.rect(x, y, w, h, P.LAMP if hover else P.WHITE)
            pyxel.rectb(x, y, w, h, P.STONE)
            icons.draw(TRAY_GOODS[gid][0], x + 9, y + 7)
        self.b_clear.draw()
        self.b_serve.draw()
        text.draw(24, 152, 'Нажмите на вещь — она ляжет на поднос.', P.STONE, small=True)
        if self.flash:
            text.center(W // 2, 152, '不对！再看看单子。', P.VERMILION)


# ---------------------------------------------------------------- the evening bells


@puzzle('bells')
class Bells(Screen):
    """Ring the bells in the order the inscription names them."""

    def __init__(self, bells: str, chant: str, lines: list[str] | None = None) -> None:
        super().__init__()
        self.bells = list(bells)
        self.chant = chant
        self.progress = 0
        self.swing = [0] * len(self.bells)
        self.flash = 0
        self.done = 0
        self.lines = lines or []
        show_lines(self.lines)

    def bell_x(self, i: int) -> int:
        n = len(self.bells)
        return W // 2 - n * 26 + 13 + i * 52

    def update(self) -> None:
        from ..core.puzzles import ring

        self.swing = [max(0, v - 1) for v in self.swing]
        self.flash = max(0, self.flash - 1)
        if self.done:
            self.done += 1
            if self.done > 50 or (self.done > 12 and INPUT.click_anywhere()):
                self.close(True)
            return
        if INPUT.cancel():
            self.close(False)
            return
        for i, g in enumerate(self.bells):
            if INPUT.click(self.bell_x(i) - 16, 52, 32, 54):
                self.swing[i] = 24
                audio.sfx('bell')
                self.progress, result = ring(self.progress, g, self.chant)
                if result == 'solved':
                    self.done = 1
                elif result == 'wrong':
                    self.flash = 25
                return

    def draw(self) -> None:
        dim()
        s = SESSION.state
        ui.panel(12, 12, W - 24, H - 24, 'paper')
        for i, ln in enumerate(self.lines):
            cells, lw = glyphline.layout(s, ln)
            glyphline.draw_row(s, cells, W // 2 - lw // 2, 16 + i * 26, P.INK, hover=False)
        pyxel.rect(30, 48, W - 60, 4, P.WOOD)
        for i, g in enumerate(self.bells):
            x = self.bell_x(i)
            off = int(pyxel.sin(self.swing[i] * 30) * self.swing[i] / 6)
            pyxel.line(x, 52, x + off, 60, P.INK)
            bx = x + off
            pyxel.tri(bx - 14, 100, bx + 14, 100, bx, 58, P.OCHRE)
            pyxel.rect(bx - 12, 70, 25, 30, P.OCHRE)
            pyxel.elli(bx - 11, 60, 23, 16, P.OCHRE)
            pyxel.rect(bx - 14, 98, 29, 4, P.WOOD)
            pyxel.rectb(bx - 12, 70, 25, 30, P.WOOD)
            glyphline.glyph_box(s, g, bx - 8, 76, 16)
        for k in range(self.progress):
            pyxel.circ(W // 2 - len(self.chant) * 6 + k * 12 + 6, 118, 3, P.JADE)
        for k in range(self.progress, len(self.chant)):
            pyxel.circb(W // 2 - len(self.chant) * 6 + k * 12 + 6, 118, 3, P.STONE)
        if self.done:
            text.center(W // 2, 134, '钟声很好听！', P.JADE)
        elif self.flash:
            text.center(W // 2, 134, 'Звон рассыпался. Начните сначала.', P.VERMILION, small=True)
        else:
            text.center(W // 2, 134, 'Звоните в колокола в том порядке, что в надписи.', P.STONE, small=True)


# ---------------------------------------------------------------- lost and found

COLOR_OF = {'红': P.VERMILION, '黑': P.INK, '蓝': P.DARK_BLUE, '绿': P.JADE, '白': P.WHITE, '黄': P.YELLOW}


def draw_thing(traits: str, x: int, y: int) -> None:
    """A little drawing of a lost thing from its traits (颜色 + 大小/长短 + 伞/帽/裙/本/瓶)."""
    col = next((c for g, c in COLOR_OF.items() if g in traits), P.STONE)
    big = '大' in traits or '长' in traits
    if '伞' in traits:
        w = 22 if big else 14
        pyxel.tri(x + 12 - w // 2, y + 12, x + 12 + w // 2, y + 12, x + 12, y + 2, col)
        pyxel.line(x + 12, y + 12, x + 12, y + 22, P.WOOD)
        pyxel.line(x + 12, y + 22, x + 10, y + 22, P.WOOD)
    elif '帽' in traits:
        pyxel.elli(x + 4, y + 10, 16, 8, col)
        pyxel.rect(x + 1, y + 16, 22, 3, col)
    elif '裙' in traits:
        h = 18 if big else 10
        pyxel.rect(x + 8, y + 4, 8, 3, col)
        pyxel.tri(x + 8, y + 7, x + 16, y + 7, x + 3, y + 7 + h, col)
        pyxel.tri(x + 16, y + 7, x + 21, y + 7 + h, x + 3, y + 7 + h, col)
    elif '本' in traits:
        pyxel.rect(x + 5, y + 4, 14, 18, col)
        pyxel.rectb(x + 5, y + 4, 14, 18, P.INK)
        pyxel.line(x + 8, y + 4, x + 8, y + 21, P.PAPER)
    elif '瓶' in traits:
        pyxel.rect(x + 10, y + 2, 4, 4, col)
        pyxel.rect(x + 8, y + 6, 8, 16, col)
        pyxel.rectb(x + 8, y + 6, 8, 16, P.INK)
    if col == P.INK:
        return
    if col == P.WHITE:
        pyxel.rectb(x + 2, y + 2, 20, 20, P.STONE)


@puzzle('lost')
class LostAndFound(Screen):
    """Give each owner the thing that fits the description.

    owners: [{'id': 'girl', 'zh': '我的伞是红色的，很小。', 'traits': '红小伞'}, …]
    things: [{'id': 'u1', 'traits': '红小伞'}, …]
    """

    def __init__(self, owners: list[dict[str, str]], things: list[dict[str, str]], lines: list[str] | None = None) -> None:
        super().__init__()
        self.owners = owners
        self.things = things
        self.pairs: dict[str, str] = {}
        self.sel: str | None = None
        self.flash = 0
        self.done = 0
        show_lines(lines or [o['zh'] for o in owners])

    def thing_rect(self, k: int) -> tuple[int, int, int, int]:
        return 224 + (k % 3) * 27, 30 + (k // 3) * 30, 26, 28

    def slot_rect(self, i: int) -> tuple[int, int, int, int]:
        return 192, 26 + i * 30, 26, 28

    def update(self) -> None:
        from ..core.puzzles import Thing, match_all

        self.flash = max(0, self.flash - 1)
        if self.done:
            self.done += 1
            if self.done > 40 or (self.done > 10 and INPUT.click_anywhere()):
                self.close(True)
            return
        if INPUT.cancel():
            self.close(False)
            return
        for k, t in enumerate(self.things):
            if INPUT.click(*self.thing_rect(k)):
                self.sel = t['id']
                audio.sfx('tap')
                return
        for i, o in enumerate(self.owners):
            if INPUT.click(*self.slot_rect(i)):
                if self.sel:
                    for key, v in list(self.pairs.items()):
                        if v == self.sel:
                            del self.pairs[key]
                    self.pairs[o['id']] = self.sel
                    self.sel = None
                else:
                    self.pairs.pop(o['id'], None)
                if len(self.pairs) == len(self.owners):
                    things = [Thing(t['id'], frozenset(t['traits'])) for t in self.things]
                    descr = {o['id']: frozenset(o['traits']) for o in self.owners}
                    if match_all(descr, things, self.pairs):
                        self.done = 1
                        audio.sfx('seal')
                    else:
                        self.flash = 30
                return

    def draw(self) -> None:
        dim()
        s = SESSION.state
        ui.panel(12, 12, W - 24, H - 24, 'paper')
        by_id = {t['id']: t for t in self.things}
        for i, o in enumerate(self.owners):
            x, y, w, h = self.slot_rect(i)
            cells, _ = glyphline.layout(s, o['zh'])
            glyphline.draw_row(s, cells, 20, y + 6, P.INK, hover=False)
            pyxel.rect(x, y, w, h, P.WHITE)
            pyxel.rectb(x, y, w, h, P.OCHRE)
            if o['id'] in self.pairs:
                draw_thing(by_id[self.pairs[o['id']]]['traits'], x + 1, y + 2)
        placed = set(self.pairs.values())
        for k, t in enumerate(self.things):
            x, y, w, h = self.thing_rect(k)
            pyxel.rect(x, y, w, h, P.LAMP if self.sel == t['id'] else P.PAPER)
            pyxel.rectb(x, y, w, h, P.STONE)
            if t['id'] in placed:
                pyxel.dither(0.35)
            draw_thing(t['traits'], x + 1, y + 2)
            pyxel.dither(1.0)
        if self.done:
            text.center(W // 2, 150, '都找到了！谢谢你！', P.JADE)
        elif self.flash:
            text.center(W // 2, 150, '不对……再看看！', P.VERMILION)
        else:
            text.center(W // 2, 150, 'Выберите вещь справа, затем — хозяина.', P.STONE, small=True)


# ---------------------------------------------------------------- building glyphs from parts


@puzzle('compose')
class ComposeGlyphs(Screen):
    """Build glyphs from two parts side by side or one above the other.

    recipes: [{'a': '人', 'b': '木', 'layout': 'lr', 'result': '休'}, …]
    targets: [{'hint': '一个人在树旁边休息。', 'result': '休'}, …]
    """

    def __init__(self, parts: str, recipes: list[dict[str, str]], targets: list[dict[str, str]], lines: list[str] | None = None) -> None:
        super().__init__()
        from ..core.puzzles import Recipe

        self.parts = list(parts)
        self.recipes = [Recipe(r['a'], r['b'], r['layout'], r['result']) for r in recipes]
        self.targets = targets
        self.i = 0
        self.a: str | None = None
        self.b: str | None = None
        self.layout = 'lr'
        self.flash = 0
        self.made = 0
        self.done = 0
        self.b_layout = ui.Button(196, 104, 90, 15, 'Расположение', small=True)
        self.b_clear = ui.Button(196, 124, 90, 15, 'Очистить', small=True)
        show_lines(lines or [t['hint'] for t in targets])

    def part_rect(self, k: int) -> tuple[int, int, int, int]:
        return 28 + k * 22, 146, 20, 20

    def update(self) -> None:
        from ..core.puzzles import compose

        self.flash = max(0, self.flash - 1)
        if self.done:
            self.done += 1
            if self.done > 40 or (self.done > 10 and INPUT.click_anywhere()):
                self.close(True)
            return
        if self.made:
            self.made -= 1
            if self.made == 0:
                self.i += 1
                self.a = self.b = None
                if self.i >= len(self.targets):
                    self.done = 1
            return
        if INPUT.cancel():
            self.close(False)
            return
        for k, g in enumerate(self.parts):
            if INPUT.click(*self.part_rect(k)):
                if self.a is None:
                    self.a = g
                elif self.b is None:
                    self.b = g
                else:
                    self.a, self.b = self.b, g
                audio.sfx('tap')
                break
        if self.b_layout.update():
            self.layout = 'tb' if self.layout == 'lr' else 'lr'
        if self.b_clear.update():
            self.a = self.b = None
        if self.a and self.b:
            result = compose(self.recipes, self.a, self.b, self.layout)
            if result and result == self.targets[self.i]['result']:
                SESSION.state.confirmed[result] = True
                from ..core import journal

                journal.see(SESSION.state, result)
                self.made = 45
                audio.sfx('seal')
            elif result is None and INPUT.pressed:
                self.flash = 20

    def draw(self) -> None:
        dim()
        s = SESSION.state
        ui.panel(12, 12, W - 24, H - 24, 'paper')
        if self.done:
            text.center(W // 2, 80, '你会造字了！', P.JADE)
            return
        t = self.targets[self.i]
        cells, lw = glyphline.layout(s, t['hint'])
        glyphline.draw_row(s, cells, W // 2 - lw // 2, 18, P.INK, hover=False)
        text.draw(22, 44, f'Знак {self.i + 1} из {len(self.targets)}', P.STONE, small=True)
        # the two parts, placed as chosen
        pyxel.rect(60, 56, 84, 84, P.WHITE)
        pyxel.rectb(60, 56, 84, 84, P.STONE)
        b = text.brush()
        if self.made:
            if b.has(t['result']):
                b.draw(62, 58, t['result'], P.INK, P.STONE, P.GREY, scale=2.0)
            else:
                text.draw(96, 92, t['result'], P.INK)
            return
        for idx, g in enumerate((self.a, self.b)):
            if not g:
                continue
            if self.layout == 'lr':
                x, y = 64 + idx * 40, 78
            else:
                x, y = 82, 60 + idx * 40
            if b.has(g):
                b.draw(x, y, g, P.INK, P.STONE, P.GREY)
            else:
                text.draw(x + 14, y + 14, g, P.INK)
        self.b_layout.draw()
        self.b_clear.draw()
        text.draw(196, 62, 'Выберите две части внизу.', P.STONE, small=True)
        text.draw(196, 74, 'Расположение: ' + ('рядом' if self.layout == 'lr' else 'одна над другой'), P.INK, small=True)
        for k, g in enumerate(self.parts):
            glyphline.glyph_box(s, g, *self.part_rect(k)[:2], 20)
        if self.flash:
            text.draw(196, 88, 'Такого знака нет.', P.VERMILION, small=True)

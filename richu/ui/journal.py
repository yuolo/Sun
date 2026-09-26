"""The journal: glyphs, words, confirmation pages, texts, phrases, spells, grammar, review."""
from __future__ import annotations

import random
from typing import Any

import pyxel

from ..art import palette as P
from ..art import pictures
from ..content import grammar as G
from ..content import lexicon
from ..content import pages as PG
from ..content import spells as SP
from ..content import texts as T
from ..content import words as WD
from ..content.hsk import WORDS
from ..core import journal, review
from ..core.types import PageDef
from ..engine import text, ui
from ..engine.app import APP, H, W, Screen
from ..engine.input import INPUT
from . import audio, glyphline
from .session import SESSION

TABS = [
    ('字', 'Знаки'), ('词', 'Слова'), ('页', 'Страницы'), ('文', 'Тексты'),
    ('话', 'Фразы'), ('法', 'Заклинания'), ('语', 'Грамматика'), ('习', 'Повторение'),
]
TOP = 22
BODY_H = H - TOP - 6


def _paper() -> None:
    pyxel.cls(P.PAPER)
    for y in range(TOP + 2, H, 14):
        pyxel.line(8, y, W - 8, y, P.PEACH)
    pyxel.rect(0, 0, 4, H, P.VERMILION)
    pyxel.rect(W - 4, 0, 4, H, P.VERMILION)


class Journal(Screen):
    opaque = True

    def __init__(self, scene: Any = None, tab: str = '') -> None:
        super().__init__()
        self.scene = scene
        self.tab = next((i for i, (zh, ru) in enumerate(TABS) if ru == tab or zh == tab), 0)
        self.views = [GlyphsTab(self), WordsTab(self), PagesTab(self), TextsTab(self), PhrasesTab(self), SpellsTab(self), GrammarTab(self), ReviewTab(self)]

    def update(self) -> None:
        for i, _ in enumerate(TABS):
            if INPUT.click(8 + i * 34, 3, 32, 17):
                self.tab = i
                audio.sfx('page')
                return
        if INPUT.click(W - 22, 3, 16, 16) or INPUT.key(pyxel.KEY_J) or INPUT.key(pyxel.KEY_ESCAPE) or (INPUT.right and not self.views[self.tab].captures_right()):
            self.close()
            return
        if INPUT.key(pyxel.KEY_TAB):
            self.tab = (self.tab + 1) % len(TABS)
        self.views[self.tab].update()

    def draw(self) -> None:
        _paper()
        for i, (zh, ru) in enumerate(TABS):
            x = 8 + i * 34
            active = i == self.tab
            pyxel.rect(x, 3, 32, 17 if active else 15, P.VERMILION if active else P.OCHRE)
            pyxel.rectb(x, 3, 32, 17 if active else 15, P.LACQUER)
            text.center(x + 16, 4, zh, P.PAPER if active else P.INK)
        pyxel.line(4, 20, W - 4, 20, P.LACQUER)
        text.draw(W - 19, 4, '×', P.INK)
        self.views[self.tab].draw()
        for i, (zh, ru) in enumerate(TABS):
            if INPUT.inside(8 + i * 34, 3, 32, 17):
                w = text.width(ru, True) + 6
                pyxel.rect(INPUT.mx + 6, INPUT.my + 8, w, 11, P.INK)
                text.draw(INPUT.mx + 9, INPUT.my + 8, ru, P.PAPER, small=True)
        from .scene_view import draw_toasts

        draw_toasts(SESSION.state)

    def open_card(self, g: str) -> None:
        from .card import GlyphCard

        APP.push(GlyphCard(g, self.scene))


class Tab:
    def __init__(self, j: Journal) -> None:
        self.j = j

    @property
    def s(self):
        return SESSION.state

    def captures_right(self) -> bool:
        return False

    def update(self) -> None:
        pass

    def draw(self) -> None:
        pass

    def header(self, title: str, info: str = '') -> None:
        text.draw(10, TOP + 2, title, P.LACQUER)
        if info:
            text.draw(W - 10 - text.width(info, True), TOP + 4, info, P.STONE, small=True)


# ---------------------------------------------------------------- glyphs


class GlyphsTab(Tab):
    COLS, ROWS, SIZE = 16, 6, 18

    def __init__(self, j: Journal) -> None:
        super().__init__(j)
        self.filter = 0  # all · confirmed · waiting
        self.page = 0
        self.search = ui.TextField(W - 118, TOP + 18, 108, '', 16, 'поиск…')
        self.search.focused = False
        self.hover: str | None = None

    def items(self) -> list[str]:
        gs = journal.seen_glyphs(self.s)
        if self.filter == 1:
            gs = [g for g in gs if self.s.confirmed.get(g)]
        elif self.filter == 2:
            gs = [g for g in gs if not self.s.confirmed.get(g)]
        q = self.search.value.strip().lower()
        if q:
            def hit(g: str) -> bool:
                d = lexicon.get(g)
                return q in self.s.guesses.get(g, '').lower() or bool(self.s.confirmed.get(g) and d and (q in d.pinyin or q in d.meaning.lower()))
            gs = [g for g in gs if hit(g)]
        return gs

    def update(self) -> None:
        self.search.update()
        for i in range(3):
            if INPUT.click(10 + i * 64, TOP + 18, 60, 15):
                self.filter, self.page = i, 0
        gs = self.items()
        per = self.COLS * self.ROWS
        pages = max(1, (len(gs) + per - 1) // per)
        if INPUT.wheel:
            self.page = max(0, min(pages - 1, self.page - INPUT.wheel))
        if INPUT.key(pyxel.KEY_RIGHT) or INPUT.click(W - 26, H - 16, 14, 12):
            self.page = min(pages - 1, self.page + 1)
        if INPUT.key(pyxel.KEY_LEFT) or INPUT.click(W - 44, H - 16, 14, 12):
            self.page = max(0, self.page - 1)
        chunk = gs[self.page * per : (self.page + 1) * per]
        for i, g in enumerate(chunk):
            x, y = self._pos(i)
            if INPUT.click(x, y, self.SIZE - 1, self.SIZE - 1):
                self.j.open_card(g)
                return

    def _pos(self, i: int) -> tuple[int, int]:
        return 12 + (i % self.COLS) * (self.SIZE + 1), TOP + 38 + (i // self.COLS) * (self.SIZE + 1)

    def draw(self) -> None:
        seen, conf, _ = journal.progress(self.s)
        self.header('Знаки', f'встречено {seen} · понято {conf}')
        for i, label in enumerate(('Все', 'Понятые', 'Ждут')):
            sel = self.filter == i
            pyxel.rect(10 + i * 64, TOP + 18, 60, 15, P.VERMILION if sel else P.PEACH)
            text.center(40 + i * 64, TOP + 18, label, P.PAPER if sel else P.INK)
        self.search.draw()
        gs = self.items()
        per = self.COLS * self.ROWS
        chunk = gs[self.page * per : (self.page + 1) * per]
        self.hover = None
        for i, g in enumerate(chunk):
            x, y = self._pos(i)
            if glyphline.glyph_box(self.s, g, x, y, self.SIZE - 1):
                self.hover = g
        if not gs:
            text.draw(14, TOP + 44, 'Пока пусто. Знаки попадают сюда, когда вы их видите.', P.STONE, small=True)
        pages = max(1, (len(gs) + per - 1) // per)
        if pages > 1:
            text.draw(W - 44, H - 17, '◀', P.OCHRE)
            text.draw(W - 26, H - 17, '▶', P.OCHRE)
            text.draw(W - 80, H - 15, f'{self.page + 1}/{pages}', P.STONE, small=True)
        if self.hover:
            note = self.s.guesses.get(self.hover, '')
            d = lexicon.get(self.hover)
            label = (f'{d.pinyin} — {d.meaning}' if self.s.confirmed.get(self.hover) and d else note) or '?'
            w = text.width(label, True) + 6
            x = max(2, min(W - w - 2, INPUT.mx + 6))
            pyxel.rect(x, INPUT.my - 13, w, 11, P.INK)
            text.draw(x + 3, INPUT.my - 13, label, P.PAPER, small=True)


# ---------------------------------------------------------------- words


class WordsTab(Tab):
    def __init__(self, j: Journal) -> None:
        super().__init__(j)
        self.scroll = ui.Scroll(10, TOP + 18, W - 20, BODY_H - 18)
        self.cache: list[str] = []
        self.cache_len = -1

    def words(self) -> list[str]:
        n = len(self.s.log) + len(self.s.texts)
        if n != self.cache_len:
            self.cache = journal.met_words(self.s)
            self.cache_len = n
        return self.cache

    def update(self) -> None:
        self.scroll.update()

    def draw(self) -> None:
        ws = self.words()
        understood = sum(1 for w in ws if journal.word_understood(self.s, w))
        self.header('Слова HSK 1–3', f'встречено {len(ws)} · понято {understood} из {len(WORDS)}')
        pyxel.clip(8, TOP + 18, W - 16, BODY_H - 18)
        y = TOP + 18 - self.scroll.offset
        start = y
        col_w = (W - 30) // 2
        for i, w in enumerate(ws):
            cx = 12 + (i % 2) * (col_w + 6)
            if i % 2 == 0 and i:
                y += 26
            ok = journal.word_understood(self.s, w)
            glyphline.draw_line(self.s, w, cx, y, P.INK, hover=False)
            if ok:
                gloss = WD.gloss(w)
                text.draw(cx + len(w) * 13 + 6, y + 2, gloss[:24], P.JADE, small=True)
        y += 26
        pyxel.clip()
        self.scroll.content = y - start
        self.scroll.draw_bar()
        if not ws:
            text.draw(14, TOP + 24, 'Слова из списка HSK появятся здесь, когда встретятся.', P.STONE, small=True)


# ---------------------------------------------------------------- pages


class PagesTab(Tab):
    def __init__(self, j: Journal) -> None:
        super().__init__(j)
        self.scroll = ui.Scroll(10, TOP + 18, W - 20, BODY_H - 18)
        self.rows: list[tuple[int, PageDef | int]] = []

    def update(self) -> None:
        self.scroll.update()
        for y, item in self.rows:
            if isinstance(item, PageDef) and INPUT.click(12, y, W - 28, 13):
                if journal.page_status(self.s, item) != 'locked':
                    APP.push(PageView(item))
                    audio.sfx('page')
                return

    def draw(self) -> None:
        pages = [p for p in PG.PAGES if p.chapter <= max(self.s.chapter, 0) or any(g in self.s.seen for g in p.glyphs)]
        done = sum(1 for p in pages if self.s.pages.get(p.id))
        ready = sum(1 for p in pages if journal.page_status(self.s, p) == 'open')
        self.header('Страницы', f'готовы {ready} · заполнено {done}')
        pyxel.clip(8, TOP + 18, W - 16, BODY_H - 18)
        y = TOP + 18 - self.scroll.offset
        start = y
        self.rows = []
        chapter = None
        for p in pages:
            if p.chapter != chapter:
                chapter = p.chapter
                text.draw(12, y, f'Глава {chapter}' if chapter else 'Пролог', P.LACQUER, small=True)
                y += 12
            st = journal.page_status(self.s, p)
            hover = INPUT.inside(12, y, W - 28, 13)
            if hover and st != 'locked':
                pyxel.rect(12, y, W - 28, 13, P.LAMP)
            col = {'done': P.INK, 'open': P.INK, 'locked': P.GREY}[st]
            text.draw(24, y, p.title, col)
            kind = {'picture': 'картинки', 'icon': 'вещи', 'phrase': 'фразы'}[p.kind]
            text.draw(24 + text.width(p.title) + 6, y + 2, kind, P.STONE, small=True)
            if st == 'done':
                pyxel.rect(14, y + 2, 7, 7, P.VERMILION)
                text.draw(W - 30 - len(p.glyphs) * 13, y, ''.join(p.glyphs), P.INK)
            elif st == 'open':
                pyxel.rectb(14, y + 2, 7, 7, P.GOLD)
                text.draw(W - 70, y + 2, 'готова!', P.VERMILION, small=True)
            else:
                pyxel.rectb(14, y + 2, 7, 7, P.GREY)
                text.draw(W - 110, y + 2, f'не хватает знаков: {journal.missing_count(self.s, p)}', P.GREY, small=True)
            self.rows.append((y, p))
            y += 14
        pyxel.clip()
        self.scroll.content = y - start
        self.scroll.draw_bar()
        if not pages:
            text.draw(14, TOP + 24, 'Страницы появятся, когда встретятся первые знаки.', P.STONE, small=True)


class PageView(Screen):
    """Put each glyph under its picture (or into its phrase). All correct = the glyphs are confirmed."""

    opaque = True

    def __init__(self, page: PageDef) -> None:
        super().__init__()
        self.page = page
        self.selected: str | None = None
        self.shake = 0
        self.sealed = 0
        self.message = ''

    @property
    def s(self):
        return SESSION.state

    def wmax(self) -> int:
        return max(len(w) for w in self.page.glyphs)

    def slot_rects(self) -> list[tuple[int, int, int, int]]:
        n = len(self.page.glyphs)
        tw = 8 + 12 * self.wmax()
        if self.page.kind == 'phrase':
            return [(W - tw - 20, 36 + i * 24, tw, 18) for i in range(n)]
        sw = min(52, (W - 20) // n)
        x0 = (W - sw * n) // 2
        return [(x0 + i * sw + (sw - tw) // 2, 100, tw, 20) for i in range(n)]

    def pool_rects(self) -> list[tuple[str, int, int]]:
        pool = journal.pool_order(self.page)
        widths = [8 + 12 * len(g) for g in pool]
        total = sum(widths) + 3 * (len(pool) - 1)
        x = (W - total) // 2
        out = []
        for g, w in zip(pool, widths):
            out.append((g, x, H - 32))
            x += w + 3
        return out

    def update(self) -> None:
        done = self.s.pages.get(self.page.id)
        if INPUT.key(pyxel.KEY_ESCAPE) or INPUT.right or INPUT.click(W - 22, 3, 16, 16):
            self.close()
            return
        if self.sealed:
            self.sealed -= 1
        if self.shake:
            self.shake -= 1
        if done:
            if INPUT.click_anywhere():
                self.close()
            return
        placed = journal.placements(self.s, self.page)
        for g, x, y in self.pool_rects():
            if INPUT.click(x, y, 8 + 12 * len(g), 20):
                self.selected = None if self.selected == g else g
                audio.sfx('tap')
                return
        for i, (x, y, w, h) in enumerate(self.slot_rects()):
            if INPUT.click(x - 2, y - 2, w + 4, h + 4):
                if self.selected:
                    journal.place(self.s, self.page, i, self.selected)
                    self.selected = None
                    audio.sfx('tap')
                    self._check()
                elif placed[i]:
                    journal.place(self.s, self.page, i, None)
                return
        if INPUT.pressed:
            for g, x, y in self.pool_rects():
                if INPUT.inside(x, y, 8 + 12 * len(g), 20):
                    return
            self.selected = None

    def _check(self) -> None:
        placed = journal.placements(self.s, self.page)
        filled, correct, _ = journal.check_page(self.page, placed)
        if not filled:
            self.message = ''
            return
        if correct:
            ok, fresh = journal.submit_page(self.s, self.page)
            if ok:
                self.sealed = 40
                SESSION.toast('Страница заполнена', ''.join(fresh))
                SESSION.save()
                audio.sfx('seal')
        else:
            self.shake = 12
            self.message = 'Что-то не так. Страница засчитывается, только если всё верно.'
            audio.sfx('wrong')

    def draw(self) -> None:
        _paper()
        p = self.page
        text.center(W // 2, 5, p.title, P.LACQUER)
        text.draw(W - 19, 4, '×', P.INK)
        done = self.s.pages.get(p.id)
        placed = list(p.glyphs) if done else journal.placements(self.s, p)
        dx = (1 if self.shake % 4 < 2 else -1) if self.shake else 0
        rects = self.slot_rects()
        for i, (x, y, w, h) in enumerate(rects):
            x += dx
            if p.kind == 'phrase':
                phrase = p.phrases[i]
                gap = '＿' * len(p.glyphs[i])
                cells, _ = glyphline.layout(self.s, phrase.replace(p.glyphs[i], gap, 1))
                glyphline.draw_row(self.s, cells, 14, y + 1, P.INK, hover=False)
            else:
                cx = x + w // 2
                pictures.draw(p.glyphs[i], cx - 16, 56, kind=p.kind)
                pyxel.rectb(cx - 18, 54, 36, 36, P.OCHRE)
            pyxel.rect(x, y, w, h, P.WHITE)
            pyxel.rectb(x, y, w, h, P.INK if not self.selected else P.VERMILION)
            g = placed[i]
            if g:
                text.center(x + w // 2, y + (h - 14) // 2 + 1, g, P.INK)
                note = ' '.join(self.s.guesses.get(c, '') for c in g if not self.s.confirmed.get(c)).strip()
                if note and p.kind != 'phrase':
                    text.center(x + w // 2, y + h + 1, note[:12], P.OCHRE, small=True)
        if not done:
            for g, x, y in self.pool_rects():
                in_slot = g in placed
                if in_slot:
                    pyxel.dither(0.35)
                word_tile(self.s, g, x, y, self.selected == g)
                pyxel.dither(1.0)
            text.center(W // 2, H - 46, 'Выберите знак внизу, затем клетку.', P.STONE, small=True)
        if self.message and not done:
            text.center(W // 2, H - 58, self.message, P.VERMILION, small=True)
        if done:
            k = 1.0 - self.sealed / 40 if self.sealed else 1.0
            size = int(28 + 20 * (1 - k))
            ui.seal(W - 44 - size // 2 + 14, 20, '好', 28)
            text.center(W // 2, H - 20, 'Страница заполнена. Знаки подтверждены.', P.JADE, small=True)
        from .scene_view import draw_toasts

        draw_toasts(self.s)


def word_tile(s: Any, w: str, x: int, y: int, selected: bool) -> None:
    tw = 8 + 12 * len(w)
    hovered = INPUT.inside(x, y, tw, 20)
    pyxel.rect(x, y, tw, 20, P.VERMILION if selected else P.LAMP if hovered else P.WHITE)
    pyxel.rectb(x, y, tw, 20, P.INK if selected else P.STONE)
    text.draw(x + 4, y + 3, w, P.PAPER if selected else P.INK)


# ---------------------------------------------------------------- texts


KIND_TITLES = {'letter': 'Письма', 'diary': 'Дневник деда', 'stone': 'Надписи', 'book': 'Книги и легенды', 'sign': 'Вывески'}


class TextsTab(Tab):
    def __init__(self, j: Journal) -> None:
        super().__init__(j)
        self.scroll = ui.Scroll(10, TOP + 18, W - 20, BODY_H - 18)
        self.rows: list[tuple[int, str]] = []

    def update(self) -> None:
        self.scroll.update()
        for y, tid in self.rows:
            if INPUT.click(12, y, W - 28, 13):
                from .reader import Reader

                APP.push(Reader(tid))
                return

    def draw(self) -> None:
        texts = [T.TEXTS[t] for t in self.s.texts if t in T.TEXTS]
        self.header('Тексты', f'{len(texts)}')
        pyxel.clip(8, TOP + 18, W - 16, BODY_H - 18)
        y = TOP + 18 - self.scroll.offset
        start = y
        self.rows = []
        for kind, title in KIND_TITLES.items():
            group = [t for t in texts if t.kind == kind]
            if not group:
                continue
            text.draw(12, y, title, P.LACQUER, small=True)
            y += 12
            for t in group:
                done, total = journal.text_progress(self.s, t)
                if INPUT.inside(12, y, W - 28, 13):
                    pyxel.rect(12, y, W - 28, 13, P.LAMP)
                text.draw(20, y, t.title, P.INK)
                pct = f'{done * 100 // max(1, total)}%'
                text.draw(W - 40, y + 2, pct, P.JADE if done == total else P.STONE, small=True)
                self.rows.append((y, t.id))
                y += 14
        pyxel.clip()
        self.scroll.content = y - start
        self.scroll.draw_bar()
        if not texts:
            text.draw(14, TOP + 24, 'Здесь будут дневник деда, письма и надписи.', P.STONE, small=True)


# ---------------------------------------------------------------- phrases


class PhrasesTab(Tab):
    def __init__(self, j: Journal) -> None:
        super().__init__(j)
        self.scroll = ui.Scroll(10, TOP + 18, W - 20, BODY_H - 18)
        self.hovered: str | None = None

    def update(self) -> None:
        self.scroll.update()
        if self.hovered and INPUT.click_anywhere():
            self.j.open_card(self.hovered)

    def draw(self) -> None:
        self.header('Фразы', f'{len(self.s.log)}')
        pyxel.clip(8, TOP + 18, W - 16, BODY_H - 18)
        y = TOP + 18 - self.scroll.offset
        start = y
        self.hovered = None
        for line in reversed(self.s.log):
            rows = glyphline.wrap(self.s, line.text, W - 40)
            for cells, _ in rows:
                if TOP + 10 < y < H:
                    hv = glyphline.draw_row(self.s, cells, 18, y, P.INK)
                    if hv:
                        self.hovered = hv
                y += glyphline.row_height(any(c.note for c in cells))
            y += 3
        pyxel.clip()
        self.scroll.content = y - start
        self.scroll.draw_bar()


# ---------------------------------------------------------------- spells


class SpellsTab(Tab):
    def __init__(self, j: Journal) -> None:
        super().__init__(j)
        self.scroll = ui.Scroll(10, TOP + 18, W - 20, BODY_H - 18)

    def update(self) -> None:
        self.scroll.update()

    def draw(self) -> None:
        self.header('Заклинания', f'{len(self.s.spells)}')
        pyxel.clip(8, TOP + 18, W - 16, BODY_H - 18)
        y = TOP + 18 - self.scroll.offset
        start = y
        if not self.s.flags.get('brush_awake'):
            text.draw(14, y + 6, 'Кисть деда пока молчит.', P.STONE, small=True)
        for sp in self.s.spells:
            w, h, _ = glyphline.draw_line(self.s, sp, 16, y, P.INK, hover=False)
            desc = describe_spell(sp, self.s)
            if desc:
                text.draw(22 + w, y + 2, desc, P.JADE, small=True)
            y += max(h, 14) + 2
        pyxel.clip()
        self.scroll.content = y - start
        self.scroll.draw_bar()


def describe_spell(sp: str, s: Any) -> str:
    if not all(s.confirmed.get(g) for g in sp):
        return ''
    e = SP.SPELLS.get(sp)
    if e:
        return e.title
    parts = []
    for g in sp:
        d = lexicon.get(g)
        if d:
            parts.append(d.meaning.split(',')[0])
    return ' + '.join(parts)


# ---------------------------------------------------------------- grammar


class GrammarTab(Tab):
    def __init__(self, j: Journal) -> None:
        super().__init__(j)
        self.open: int | None = None
        self.scroll = ui.Scroll(10, TOP + 18, W - 20, BODY_H - 18)
        self.list_scroll = ui.Scroll(10, TOP + 18, W - 20, BODY_H - 18)

    def captures_right(self) -> bool:
        return self.open is not None

    def update(self) -> None:
        notes = journal.grammar_unlocked(self.s)
        if self.open is not None:
            self.scroll.update()
            if INPUT.right or INPUT.key(pyxel.KEY_BACKSPACE) or INPUT.click(10, TOP + 2, 60, 14):
                self.open = None
            return
        self.list_scroll.content = len(notes) * 14
        self.list_scroll.update()
        if not INPUT.inside(10, TOP + 18, W - 20, BODY_H - 18):
            return
        for i, _ in enumerate(notes):
            if INPUT.click(12, TOP + 18 + i * 14 - self.list_scroll.offset, W - 28, 13):
                self.open = i
                self.scroll.offset = 0

    def draw(self) -> None:
        notes = journal.grammar_unlocked(self.s)
        if self.open is not None and self.open < len(notes):
            n = notes[self.open]
            text.draw(12, TOP + 2, '◀ ' + n.title, P.LACQUER)
            pyxel.clip(8, TOP + 18, W - 16, BODY_H - 18)
            y = TOP + 20 - self.scroll.offset
            start = y
            for ln in text.wrap(n.text, W - 30):
                text.draw(14, y, ln, P.INK)
                y += 14
            y += 4
            for zh, ru in n.examples:
                w, h, _ = glyphline.draw_line(self.s, zh, 18, y, P.INK, hover=False)
                y += h
                text.draw(24, y, ru, P.STONE, small=True)
                y += 14
            pyxel.clip()
            self.scroll.content = y - start
            self.scroll.draw_bar()
            return
        self.header('Грамматика', f'{len(notes)} из {len(G.GRAMMAR)}')
        pyxel.clip(8, TOP + 18, W - 16, BODY_H - 18)
        for i, n in enumerate(notes):
            y = TOP + 18 + i * 14 - self.list_scroll.offset
            if INPUT.inside(12, y, W - 28, 13) and INPUT.inside(8, TOP + 18, W - 16, BODY_H - 18):
                pyxel.rect(12, y, W - 28, 13, P.LAMP)
            text.draw(18, y, n.title, P.INK)
        pyxel.clip()
        self.list_scroll.content = len(notes) * 14
        self.list_scroll.draw_bar()
        if not notes:
            text.draw(14, TOP + 24, 'Заметки откроются, когда вы поймёте нужные знаки.', P.STONE, small=True)


# ---------------------------------------------------------------- review


class ReviewTab(Tab):
    def __init__(self, j: Journal) -> None:
        super().__init__(j)
        self.q: review.Question | None = None
        self.answered: str | None = None
        self.score = [0, 0]
        self.rng = random.Random()

    def pool(self) -> list[str]:
        return [g for g in journal.seen_glyphs(self.s) if self.s.confirmed.get(g)]

    def next(self) -> None:
        self.q = review.make_question(self.pool(), self.rng, self.q.glyph if self.q else None)
        self.answered = None

    def update(self) -> None:
        if self.q is None:
            self.next()
            return
        if self.answered is not None:
            if INPUT.click_anywhere() or INPUT.key(pyxel.KEY_SPACE):
                self.next()
            return
        for i, opt in enumerate(self.q.options):
            x, y, w, h = self._opt(i)
            if INPUT.click(x, y, w, h):
                self.answered = opt
                self.score[1] += 1
                if opt == self.q.glyph:
                    self.score[0] += 1
                    audio.sfx('seal')
                else:
                    audio.sfx('wrong')

    def _opt(self, i: int) -> tuple[int, int, int, int]:
        if self.q and self.q.mode == 'glyph→meaning':
            return 30, 90 + i * 18, W - 60, 16
        return 60 + i * 52, 100, 40, 40

    def draw(self) -> None:
        self.header('Повторение', f'{self.score[0]} из {self.score[1]}')
        if self.q is None:
            text.draw(14, TOP + 24, f'Нужно хотя бы {review.MIN_REVIEW} понятых знака.', P.STONE, small=True)
            return
        q = self.q
        if q.mode == 'glyph→meaning':
            if text.brush().has(q.glyph):
                text.brush().draw(W // 2 - 20, 40, q.glyph, P.INK, P.STONE, P.GREY)
            else:
                text.center(W // 2, 56, q.glyph, P.INK)
            for i, opt in enumerate(q.options):
                x, y, w, h = self._opt(i)
                d = lexicon.get(opt)
                style = 'paper'
                if self.answered is not None:
                    style = 'seal' if opt == q.glyph else ('night' if opt == self.answered else 'paper')
                ui.panel(x, y, w, h, style, shadow=False)
                text.center(x + w // 2, y + 1, d.meaning if d else opt, P.PAPER if style in ('seal', 'night') else P.INK)
        else:
            d = lexicon.get(q.glyph)
            text.center(W // 2, 50, d.meaning if d else '?', P.INK)
            for i, opt in enumerate(q.options):
                x, y, w, h = self._opt(i)
                style = 'paper'
                if self.answered is not None:
                    style = 'seal' if opt == q.glyph else ('night' if opt == self.answered else 'paper')
                ui.panel(x, y, w, h, style, shadow=False)
                text.center(x + w // 2, y + 13, opt, P.PAPER if style in ('seal', 'night') else P.INK)
        if self.answered is not None:
            text.center(W // 2, H - 18, 'Дальше — клик', P.STONE, small=True)

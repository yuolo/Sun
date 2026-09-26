"""Title, pause menu, settings, chapter cards, ending."""
from __future__ import annotations

from typing import Any

import pyxel

from .. import platform
from ..art import kit
from ..art import palette as P
from ..content.world import CHAPTERS
from ..core import interact, journal
from ..core.state import START
from ..engine import text, ui
from ..engine.app import APP, H, W, Screen
from ..engine.input import INPUT
from . import audio, glyphline
from .session import SESSION


def start_game(new: bool) -> None:
    from .scene_view import SceneView

    if new:
        SESSION.new_game()
    elif not SESSION.load():
        SESSION.new_game()
        new = True
    view = SceneView()
    APP.replace_all(view)
    s = SESSION.state
    if new:
        view.load(*START)
    else:
        view.load(s.scene)

    async def enter() -> None:
        assert view.scene is not None
        await interact.enter_scene(view.rt, view.scene)

    view.run(enter(), 'enter')


class TitleScreen(Screen):
    opaque = True

    def __init__(self) -> None:
        super().__init__()
        bw = 110
        x = (W - bw) // 2
        self.has_save = SESSION.has_save()
        self.buttons = []
        y = 104
        if self.has_save:
            self.buttons.append(ui.Button(x, y, bw, 16, 'Продолжить', style='night'))
            y += 19
        self.buttons.append(ui.Button(x, y, bw, 16, 'Новая игра', style='night'))
        y += 19
        self.buttons.append(ui.Button(x, y, bw, 16, 'Настройки', style='night'))
        self.t = 0
        self.sky = pyxel.Image(W, H)
        self.land = pyxel.Image(W, H)
        kit.canvas(self.sky)
        draw_title_sky()
        kit.canvas(self.land)
        draw_title_land()
        kit.canvas(pyxel)
        audio.music('title')

    def update(self) -> None:
        self.t += 1
        for b in self.buttons:
            if b.update():
                if b.label == 'Продолжить':
                    start_game(False)
                elif b.label == 'Новая игра':
                    if self.has_save:
                        APP.push(Confirm('Начать заново? Сохранение будет стёрто.', lambda: start_game(True)))
                    else:
                        start_game(True)
                elif b.label == 'Настройки':
                    APP.push(SettingsScreen())
                return

    def draw(self) -> None:
        pyxel.blt(0, 0, self.sky, 0, 0, W, H)
        # the sun rises slowly behind the peak
        sy = 104 - min(24, self.t / 12)
        kit.canvas(pyxel)
        kit.sun(W // 2 + 34, int(sy), 14, P.LAMP, P.GOLD)
        pyxel.blt(0, 0, self.land, 0, 0, W, H, 0)
        b = text.brush()
        b.draw(W // 2 - 46, 12, '日', P.VERMILION, P.LACQUER, P.PLUM)
        b.draw(W // 2 + 6, 12, '出', P.VERMILION, P.LACQUER, P.PLUM)
        text.center(W // 2, 58, 'В О С Х О Д', P.PAPER, outline=P.INK)
        for btn in self.buttons:
            btn.draw()
        text.draw(4, H - 12, 'Тайшань · 泰山', P.OCHRE, small=True)


def draw_title_sky() -> None:
    kit.sky([(P.NIGHT, 18), (P.NAVY, 16), (P.DUSK, 18), (P.ROSE, 16), (P.PEACH, 14), (P.LAMP, 98)])
    kit.stars(3, 40, 30)


def draw_title_land() -> None:
    """Mount Tai at dawn; colour 0 stays transparent so the sun can rise behind the peak."""
    kit.C.cls(0)
    kit.ridge(118, 10, 40, 11, P.DUSK, rim=P.ROSE, peaks=[(W // 2 + 10, 44, 80)])
    kit.mist(104, 10, P.ROSE, 0.4)
    kit.ridge(136, 10, 30, 12, P.NAVY, rim=P.DUSK)
    kit.cloud_sea(142, 5, P.MIST, P.DUSK)
    kit.pine(40, 150, 30, P.INK, P.NAVY, P.INK, lean=6, seed=2)
    kit.pine(284, 154, 24, P.INK, P.NAVY, P.INK, lean=-4, seed=5)


class Confirm(Screen):
    def __init__(self, question: str, yes: Any) -> None:
        super().__init__()
        self.q = question
        self.yes = yes
        self.b_yes = ui.Button(W // 2 - 64, H // 2 + 6, 60, 16, 'Да', style='seal')
        self.b_no = ui.Button(W // 2 + 4, H // 2 + 6, 60, 16, 'Нет')

    def update(self) -> None:
        if self.b_yes.update():
            self.close()
            self.yes()
        elif self.b_no.update() or INPUT.cancel():
            self.close()

    def draw(self) -> None:
        pyxel.dither(0.6)
        pyxel.rect(0, 0, W, H, P.INK)
        pyxel.dither(1.0)
        lines = text.wrap(self.q, 200)
        h = len(lines) * 14 + 34
        ui.panel(W // 2 - 110, H // 2 - h + 22, 220, h, 'paper')
        for i, ln in enumerate(lines):
            text.center(W // 2, H // 2 - h + 26 + i * 14, ln, P.INK)
        self.b_yes.draw()
        self.b_no.draw()


class PauseMenu(Screen):
    def __init__(self, scene: Any) -> None:
        super().__init__()
        self.scene = scene
        labels = ['Продолжить', 'Дневник', 'Подсказка', 'Настройки', 'В главное меню']
        self.buttons = [ui.Button(W // 2 - 60, 46 + i * 20, 120, 16, lb) for i, lb in enumerate(labels)]

    def update(self) -> None:
        for b in self.buttons:
            if b.update():
                self.close()
                if b.label == 'Дневник':
                    self.scene.open_journal()
                elif b.label == 'Подсказка':
                    self.scene.show_hint()
                elif b.label == 'Настройки':
                    APP.push(SettingsScreen())
                elif b.label == 'В главное меню':
                    SESSION.save()
                    APP.replace_all(TitleScreen())
                return
        if INPUT.key(pyxel.KEY_ESCAPE) or INPUT.right:
            self.close()

    def draw(self) -> None:
        pyxel.dither(0.6)
        pyxel.rect(0, 0, W, H, P.INK)
        pyxel.dither(1.0)
        ui.panel(W // 2 - 72, 24, 144, 130, 'paper')
        text.center(W // 2, 28, 'Пауза', P.LACQUER)
        for b in self.buttons:
            b.draw()
        s = SESSION.state
        seen, conf, _ = journal.progress(s)
        mins = s.play_frames // 30 // 60
        text.center(W // 2, 142, f'понято знаков: {conf} · в пути {mins} мин', P.STONE, small=True)


SETTINGS = [
    ('pinyin', 'Пиньинь под понятыми знаками'),
    ('guesses', 'Догадки под знаками'),
    ('brush_glyphs', 'Крупный знак кистью'),
    ('voice', 'Озвучка (в браузере)'),
    ('music', 'Музыка'),
    ('sfx', 'Звуки'),
]


class SettingsScreen(Screen):
    def update(self) -> None:
        st = SESSION.state.settings
        for i, (key, _) in enumerate(SETTINGS):
            if INPUT.click(40, 40 + i * 18, W - 80, 16):
                setattr(st, key, not getattr(st, key))
                SESSION.save_settings()
                if key == 'music':
                    audio.refresh()
                audio.sfx('tap')
        if INPUT.click(W // 2 - 40, H - 30, 80, 16) or INPUT.cancel():
            self.close()

    def draw(self) -> None:
        pyxel.dither(0.6)
        pyxel.rect(0, 0, W, H, P.INK)
        pyxel.dither(1.0)
        ui.panel(30, 14, W - 60, H - 24, 'paper')
        text.center(W // 2, 18, 'Настройки', P.LACQUER)
        st = SESSION.state.settings
        for i, (key, label) in enumerate(SETTINGS):
            y = 40 + i * 18
            on = getattr(st, key)
            if INPUT.inside(40, y, W - 80, 16):
                pyxel.rect(40, y, W - 80, 16, P.LAMP)
            pyxel.rect(46, y + 3, 10, 10, P.VERMILION if on else P.WHITE)
            pyxel.rectb(46, y + 3, 10, 10, P.INK)
            text.draw(62, y + 1, label, P.INK if key != 'voice' or platform.IS_WEB else P.STONE)
        ui.Button(W // 2 - 40, H - 30, 80, 16, 'Готово', style='seal').draw()


class ChapterCard(Screen):
    opaque = True

    def __init__(self, n: int) -> None:
        super().__init__()
        self.ch = next(c for c in CHAPTERS if c.n == n)
        self.t = 0

    def update(self) -> None:
        self.t += 1
        if self.t > 20 and (INPUT.advance() or self.t > 30 * 6):
            self.close()

    def draw(self) -> None:
        pyxel.cls(P.INK)
        a = min(1.0, self.t / 20)
        pyxel.dither(a)
        b = text.brush()
        zh = self.ch.zh
        total = len(zh) * 44
        for i, ch in enumerate(zh):
            b.draw(W // 2 - total // 2 + i * 44, 34, ch, P.PAPER, P.GREY, P.STONE)
        label = 'Пролог' if self.ch.n == 0 else f'Глава {self.ch.n}'
        text.center(W // 2, 92, label, P.OCHRE, small=True)
        text.center(W // 2, 106, self.ch.title, P.PAPER)
        text.center(W // 2, 124, self.ch.subtitle, P.STONE, small=True)
        pyxel.dither(1.0)


class Ending(Screen):
    opaque = True

    def __init__(self) -> None:
        super().__init__()
        self.t = 0

    def update(self) -> None:
        self.t += 1
        if self.t > 60 and INPUT.advance():
            self.close()
            APP.replace_all(TitleScreen())

    def draw(self) -> None:
        s = SESSION.state
        pyxel.cls(P.PAPER)
        b = text.brush()
        b.draw(W // 2 - 44, 14, '日', P.VERMILION, P.ROSE, P.PEACH)
        b.draw(W // 2 + 4, 14, '出', P.VERMILION, P.ROSE, P.PEACH)
        seen, conf, total = journal.progress(s)
        words = journal.met_words(s)
        understood = sum(1 for w in words if journal.word_understood(s, w))
        stats = [
            f'Встречено знаков: {seen}, понято: {conf}',
            f'Слов HSK 1–3 понято: {understood} из 601',
            f'Заклинаний: {len(s.spells)}',
            f'В пути: {s.play_frames // 30 // 60} мин',
        ]
        y = 60
        text.center(W // 2, y, 'Восход', P.LACQUER)
        y += 18
        for ln in stats:
            text.center(W // 2, y, ln, P.INK)
            y += 12
        y += 6
        if s.inscription:
            text.center(W // 2, y, 'Ваша строка деду:', P.STONE, small=True)
            y += 12
            cells, lw = glyphline.layout(s, s.inscription)
            glyphline.draw_row(s, cells, W // 2 - lw // 2, y, P.VERMILION, hover=False)
            y += 28
        text.center(W // 2, min(y, H - 14), 'Спасибо, что прошли этот путь.', P.INK)



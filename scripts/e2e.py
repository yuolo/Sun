#!/usr/bin/env python3
"""Plays the game through the real UI in headless mode: clicks, bubbles, pads, items.

    python scripts/e2e.py [--shots DIR]

Unlike the headless-context tests, this drives SceneView and its Runtime with
real frames, so it catches UI bugs (futures that never resolve, screens that
don't close, crashes in drawing).
"""
from __future__ import annotations

import os
import sys
import time
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pyxel  # noqa: E402

from richu import platform  # noqa: E402
from richu.engine import app  # noqa: E402
from richu.engine.app import APP  # noqa: E402
from richu.engine.driver import Driver  # noqa: E402

SHOTS = sys.argv[sys.argv.index('--shots') + 1] if '--shots' in sys.argv else ''


class E2E:
    def __init__(self) -> None:
        platform.use_memory_storage()
        app.init(headless=True)
        from richu.ui.session import SESSION

        SESSION.boot()
        self.d = Driver()
        self.errors: list[str] = []
        self.n = 0
        self.last = ''  # the player's last action, for error messages

    # ---------------------------------------------------------------- helpers

    @property
    def view(self):
        from richu.ui.scene_view import SceneView

        return APP.find(SceneView)

    @property
    def s(self):
        from richu.ui.session import SESSION

        return SESSION.state

    def shot(self, name: str) -> None:
        if SHOTS:
            os.makedirs(SHOTS, exist_ok=True)
            self.n += 1
            self.d.shot(os.path.join(SHOTS, f'{self.n:02d}-{name}'))

    def check(self, cond: bool, msg: str) -> None:
        print(('ok   ' if cond else 'FAIL ') + msg)
        if not cond:
            self.errors.append(msg)

    def settle(self, max_frames: int = 3000, answers: list[str] | None = None, plans: dict[str, list] | None = None) -> str:
        """Advances dialogue and closes cards until the scene waits for the player.

        ``answers`` is consumed in place (a queue shared across calls, like
        HeadlessGame.answer), and so are the planned puzzle results in ``plans``.
        """
        from richu.ui.composer import AnswerPad
        from richu.ui.menus import ChapterCard
        from richu.ui.puzzles import PUZZLES
        from richu.ui.reader import Reader

        kinds = {cls: kind for kind, cls in PUZZLES.items()}
        answers = answers if answers is not None else []
        idle = 0
        for _ in range(max_frames):
            top = APP.top
            v = self.view
            if isinstance(top, ChapterCard):
                self.d.step(25)
                self.d.key(pyxel.KEY_SPACE)
                idle = 0
                continue
            if isinstance(top, Reader):
                self.d.step(3)
                self.d.key(pyxel.KEY_ESCAPE)
                idle = 0
                continue
            if isinstance(top, AnswerPad):
                if not answers:
                    return 'question'
                self.type_answer(top, answers.pop(0))
                idle = 0
                continue
            if type(top) in kinds:
                kind = kinds[type(top)]
                queue = (plans or {}).get(kind)
                self.d.step(4)
                if not queue:
                    self.errors.append(f'no planned result for puzzle {kind}')
                    top.close(None)
                else:
                    top.close(queue.pop(0))
                idle = 0
                continue
            if v is not None and top is v:
                if v.bubbles or v.narration:
                    self.d.step(8)
                    self.d.key(pyxel.KEY_SPACE)
                    idle = 0
                    continue
                if not v.busy and v.fade == v.fade_to and v.player.tx is None:
                    idle += 1
                    if idle > 3:
                        return 'idle'
            elif v is not None and top is not v and not isinstance(top, AnswerPad):
                self.errors.append(f'unexpected screen {type(top).__name__} in {self.s.scene} after {self.last}')
                top.close(None)
                continue
            self.d.step(1)
        self.errors.append(f'timeout in {self.s.scene} after {self.last}')
        return 'timeout'

    def type_answer(self, pad, answer: str) -> None:
        for ch in answer:
            pad.palette.filter.value = ch
            self.d.step(1)
            self.d.click(pad.palette.x + 4, pad.palette.y + 4)
        pad.palette.filter.value = ''
        self.d.step(1)
        typed = ''.join(pad.slots)
        if typed != answer:
            self.errors.append(f'could not type {answer!r} (got {typed!r}) in {self.s.scene}')
        self.d.click(pad.btn_ok.x + 4, pad.btn_ok.y + 4)

    # ---------------------------------------------------------------- the story

    def run(self) -> int:
        from richu.devtools import playthrough as pt

        t0 = time.time()
        g = UIGame(self)
        chapters = [
            ('prologue', lambda: pt.play_prologue(g)),
            ('chapter 1', lambda: pt.play_chapter1(g)),
            ('pages 1', lambda: pt.solve_open_pages(g, 1)),
            ('chapter 2', lambda: pt.play_chapter2(g, sleep=True)),
            ('pages 2', lambda: pt.solve_open_pages(g, 2)),
            ('chapter 3', lambda: pt.play_chapter3(g, climb=True)),
            ('pages 3', lambda: pt.solve_open_pages(g, 3)),
            ('chapter 4', lambda: pt.play_chapter4(g, climb=True)),
            ('pages 4', lambda: pt.solve_open_pages(g, 4)),
            ('chapter 5', lambda: pt.play_chapter5(g)),
            ('pages 5', lambda: pt.solve_open_pages(g, 5)),
        ]
        for name, play in chapters:
            try:
                play()
                self.check(True, f'{name} (now in {self.s.scene})')
            except AssertionError as e:
                self.check(False, f'{name}: {e} (in {self.s.scene})')
                break
            self.shot(name.replace(' ', ''))
        # the journal opens and closes
        self.d.key(pyxel.KEY_J)
        self.d.step(3)
        self.shot('journal')
        self.d.key(pyxel.KEY_ESCAPE)
        self.d.step(3)
        self.check(APP.top is self.view, 'journal closes')
        print(f'{time.time() - t0:.1f}s, {len(self.errors)} errors')
        for e in self.errors:
            print('  ', e)
        return 1 if self.errors else 0


class UIGame:
    """HeadlessGame's API on top of the real UI, so the e2e run replays
    ``richu.devtools.playthrough`` with clicks, bubbles and pads."""

    def __init__(self, e: E2E) -> None:
        self.e = e
        self.answers: list[str] = []
        self.plans: dict[str, list] = defaultdict(list)

    @property
    def state(self):
        return self.e.s

    @property
    def view(self):
        return self.e.view

    def _settle(self) -> str:
        return self.e.settle(answers=self.answers, plans=self.plans)

    def start(self, scene: str = '0a', entry: str = 'start') -> 'UIGame':
        from richu.ui.menus import TitleScreen

        APP.replace_all(TitleScreen())
        self.e.d.step(5)
        new = next(b for b in APP.top.buttons if b.label == 'Новая игра')
        self.e.d.click(new.x + 5, new.y + 5)
        self._settle()
        assert self.state.scene == scene, f'new game starts in {self.state.scene}'
        return self

    def talk(self, actor: str) -> 'UIGame':
        self.e.last = f'talk {actor}'
        m = self.view.actors.get(actor)
        assert m is not None, f'no actor {actor} in {self.state.scene}'
        self.e.d.click(int(m.x), int(m.y) - 12)
        self._settle()
        return self

    def _click_hotspot(self, hid: str) -> None:
        h = next((h for h in self.view.scene.hotspots if h.id == hid), None)
        assert h is not None, f'no hotspot {hid} in {self.state.scene}'
        self.e.d.click(*self._free_point(h.rect))

    def _free_point(self, rect: tuple[int, int, int, int]) -> tuple[int, int]:
        """A point of ``rect`` not covered by a sign, nearest to its centre."""
        from richu.core import interact

        v = self.view
        boxes = [v._sign_box(sg)[:4] for sg in interact.visible_signs(v.scene, self.state) if not sg.talisman]
        x, y, w, h = rect
        pts = [(px, py) for px in range(x + 1, x + w - 1, 2) for py in range(y + 1, y + h - 1, 2)]
        pts.sort(key=lambda p: abs(p[0] - x - w / 2) + abs(p[1] - y - h / 2))
        for px, py in pts:
            if not any(bx <= px < bx + bw and by <= py < by + bh for bx, by, bw, bh in boxes):
                return px, py
        self.e.errors.append(f'{rect} is covered by signs in {self.state.scene}')
        return x + w // 2, y + h // 2

    def click(self, hotspot: str) -> 'UIGame':
        self.e.last = f'click {hotspot}'
        self._click_hotspot(hotspot)
        self._settle()
        return self

    def use(self, item: str, target: str) -> bool:
        self.e.last = f'use {item} on {target}'
        i = self.state.inventory.index(item)
        self.e.d.move(160, 176)
        self.e.d.step(10)
        self.e.d.click(4 + i * 19 + 8, 180 - 10)
        self.e.d.step(2)
        if self.view.mode != 'item' or self.view.item != item:
            self.e.errors.append(f'could not select {item}')
        if target in self.view.actors:
            m = self.view.actors[target]
            self.e.d.click(int(m.x), int(m.y) - 12)
        else:
            self._click_hotspot(target)
        self._settle()
        return True

    def exit(self, exit_id: str) -> bool:
        self.e.last = f'exit {exit_id}'
        before = self.state.scene
        e = next((e for e in self.view.scene.exits if e.id == exit_id), None)
        assert e is not None, f'no exit {exit_id} in {before}'
        x, y, w, h = e.rect
        self.e.d.click(x + w // 2, y + h // 2)
        self._settle()
        return self.state.scene != before

    def answer(self, *answers: str) -> 'UIGame':
        self.answers.extend(answers)
        return self

    def plan(self, kind: str, *results) -> 'UIGame':
        self.plans[kind].extend(results)
        return self

    def cast(self, text_: str, target: str | None = None):
        from richu.ui.composer import BrushPad

        self.e.d.key(pyxel.KEY_B)
        self.e.d.step(3)
        pad = APP.top
        assert isinstance(pad, BrushPad), 'the brush does not open'
        for ch in text_:
            pad.palette.filter.value = ch
            self.e.d.step(1)
            self.e.d.click(pad.palette.x + 4, pad.palette.y + 4)
        pad.palette.filter.value = ''
        self.e.d.step(1)
        assert ''.join(pad.slots) == text_, f'could not write {text_}'
        self.e.d.click(pad.btn_ok.x + 4, pad.btn_ok.y + 4)
        self.e.d.step(3)
        if target in self.view.actors:
            m = self.view.actors[target]
            self.e.d.click(int(m.x), int(m.y) - 12)
        elif target:
            self._click_hotspot(target)
        else:
            self.e.d.click(160, 60)
        self._settle()
        return None

    def read(self, text_id: str) -> 'UIGame':
        from richu.ui.reader import Reader

        self.e.last = f'read {text_id}'
        assert text_id in self.state.texts, f'text {text_id} is not unlocked'
        APP.push(Reader(text_id))
        self.e.d.step(4)
        self.e.d.key(pyxel.KEY_ESCAPE)
        self.e.d.step(3)
        return self

    def solve_page(self, page_id: str) -> list[str]:
        from richu.content.pages import page
        from richu.core import journal

        p = page(page_id)
        for i, gl in enumerate(p.glyphs):
            journal.place(self.state, p, i, gl)
        ok, fresh = journal.submit_page(self.state, p)
        assert ok, f'page {page_id} rejected'
        return fresh


if __name__ == '__main__':
    sys.exit(E2E().run())

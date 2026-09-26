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

    def settle(self, max_frames: int = 3000, answers: list[str] | None = None) -> str:
        """Advances dialogue and closes cards until the scene waits for the player."""
        from richu.ui.composer import AnswerPad
        from richu.ui.menus import ChapterCard
        from richu.ui.reader import Reader

        answers = list(answers or [])
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
            self.d.step(1)
        return 'timeout'

    def type_answer(self, pad, answer: str) -> None:
        for ch in answer:
            pad.palette.filter.value = ch
            self.d.step(1)
            self.d.click(pad.palette.x + 4, pad.palette.y + 4)
        pad.palette.filter.value = ''
        self.d.step(1)
        self.d.click(pad.btn_ok.x + 4, pad.btn_ok.y + 4)

    def click_actor(self, actor_id: str, answers: list[str] | None = None) -> str:
        m = self.view.actors[actor_id]
        self.d.click(int(m.x), int(m.y) - 12)
        return self.settle(answers=answers)

    def click_hotspot(self, hid: str, answers: list[str] | None = None) -> str:
        h = next(h for h in self.view.scene.hotspots if h.id == hid)
        x, y, w, hh = h.rect
        self.d.click(x + w // 2, y + hh // 2)
        return self.settle(answers=answers)

    def click_exit(self, eid: str) -> str:
        e = next(e for e in self.view.scene.exits if e.id == eid)
        x, y, w, h = e.rect
        self.d.click(x + w // 2, y + h // 2)
        return self.settle()

    def use_item(self, item: str, actor: str | None = None, hotspot: str | None = None, answers: list[str] | None = None) -> str:
        i = self.s.inventory.index(item)
        self.d.move(160, 176)
        self.d.step(10)
        self.d.click(4 + i * 19 + 8, 180 - 10)
        self.d.step(2)
        if self.view.mode != 'item' or self.view.item != item:
            self.errors.append(f'could not select {item}')
        if actor:
            m = self.view.actors[actor]
            self.d.click(int(m.x), int(m.y) - 12)
        else:
            h = next(h for h in self.view.scene.hotspots if h.id == hotspot)
            x, y, w, hh = h.rect
            self.d.click(x + w // 2, y + hh // 2)
        return self.settle(answers=answers)

    # ---------------------------------------------------------------- the story

    def run(self) -> int:
        from richu.ui.menus import TitleScreen

        t0 = time.time()
        APP.replace_all(TitleScreen())
        self.d.step(5)
        title = APP.top
        new = next(b for b in title.buttons if b.label == 'Новая игра')
        self.d.click(new.x + 5, new.y + 5)
        self.settle()
        self.check(self.view is not None and self.s.scene == '0a', 'new game starts in grandfather\'s room')
        self.shot('prologue')
        self.click_hotspot('box')
        self.check('brush' in self.s.inventory, 'the box gives the brush, diary, photo and letter')
        self.click_hotspot('photo_wall')
        self.click_exit('door')
        self.check(self.s.scene == '1a', 'the door leads to the airport')
        self.shot('airport')

        self.click_actor('officer')
        self.use_item('passport', actor='officer', answers=['是'])
        self.check(self.s.on('passport_ok'), 'passport control passed')
        self.click_hotspot('black')
        self.click_hotspot('red')
        self.check('suitcase' in self.s.inventory, 'got the red suitcase')
        self.click_exit('out')
        self.check(self.s.scene == '1b', 'arrived at the station')
        self.shot('station')

        self.click_actor('clerk', answers=['泰山'])
        self.use_item('money', actor='clerk')
        self.check('ticket' in self.s.inventory, 'bought a ticket')
        self.click_actor('waitress', answers=['面包'])
        self.use_item('money', actor='waitress')
        self.click_actor('kid', answers=['我是俄罗斯人'])
        self.click_actor('kid')
        self.use_item('bread', actor='kid')
        self.check('apple' in self.s.inventory, 'the granny gave an apple')
        self.use_item('ticket', actor='gatekeeper')
        self.click_exit('platform')
        self.check(self.s.scene == '1c', 'on the train')
        self.click_hotspot('seat8')
        self.check(self.s.on('seated'), 'found seat 8')
        self.click_actor('student', answers=['我是俄罗斯人'])
        self.click_actor('student', answers=['是'])
        self.click_actor('student', answers=['小安'])
        self.click_actor('student')
        self.use_item('diary', actor='student')
        self.check('diary_1' in self.s.texts, 'the student read the diary')
        for _ in range(4):
            self.click_actor('student')
        self.check(self.s.on('arrived'), 'arrived in Tai\'an')
        self.shot('train')
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


if __name__ == '__main__':
    sys.exit(E2E().run())

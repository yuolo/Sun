#!/usr/bin/env python3
"""Screenshots of scenes and screens in headless mode, for reviewing the art and UI.

    python scripts/shots.py [out_dir] [--chapter N]

Plays the story headlessly (as the tests do), then shows each visited scene
and the main windows in the real UI and saves PNGs (×3).
"""
from __future__ import annotations

import copy
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from richu import platform  # noqa: E402
from richu.engine import app  # noqa: E402
from richu.engine.app import APP  # noqa: E402
from richu.engine.driver import Driver  # noqa: E402


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    out = args[0] if args else 'shots'
    only = None
    if '--chapter' in sys.argv:
        only = int(sys.argv[sys.argv.index('--chapter') + 1])
        args = [a for a in args if a != str(only)]
        out = args[0] if args else 'shots'
    out = os.path.abspath(out)  # pyxel resolves relative paths from the script's directory
    os.makedirs(out, exist_ok=True)
    platform.use_memory_storage()
    app.init(headless=True)
    from richu.content.world import load
    from richu.core.headless import HeadlessGame
    from richu.devtools import playthrough as pt
    from richu.ui import bubbles
    from richu.ui.card import GlyphCard
    from richu.ui.composer import AnswerPad, BrushPad
    from richu.ui.journal import Journal, PageView
    from richu.ui.menus import ChapterCard, TitleScreen
    from richu.ui.reader import Reader
    from richu.ui.scene_view import SceneView
    from richu.ui.session import SESSION

    load()
    SESSION.boot()
    d = Driver()
    n = 0

    def shot(name: str, frames: int = 2) -> None:
        nonlocal n
        d.step(frames)
        n += 1
        d.shot(os.path.join(out, f'{n:02d}-{name}'))

    APP.replace_all(TitleScreen())
    d.move(160, 150)
    shot('title', 40)
    APP.replace_all(ChapterCard(1))
    shot('chapter1', 30)

    # play the story, remembering the state at every scene change
    g = HeadlessGame()
    states: list[tuple[str, object]] = []
    orig_goto = g.c.goto

    async def goto(scene_id: str, entry: str) -> None:
        await orig_goto(scene_id, entry)
        states.append((scene_id, copy.deepcopy(g.state)))

    g.c.goto = goto  # type: ignore[method-assign]
    pt.play_prologue(g)
    pt.play_chapter1(g)
    final = copy.deepcopy(g.state)
    pt.solve_open_pages(g, 1)
    pt.play_chapter2(g, sleep=True)
    pt.solve_open_pages(g, 2)
    pt.play_chapter3(g, climb=True)
    pt.solve_open_pages(g, 3)
    pt.play_chapter4(g, climb=True)
    pt.solve_open_pages(g, 4)
    pt.play_chapter5(g)

    for scene_id, st in states:
        if only is not None and st.chapter != only:
            continue
        SESSION.state = copy.deepcopy(st)  # type: ignore[assignment]
        view = SceneView()
        APP.replace_all(view)
        view.load(scene_id)
        d.move(300, 20)
        shot(f'scene-{scene_id}')
        # a speech bubble over the first actor, with notes
        if view.scene and view.scene.actors:
            a = view.scene.actors[0]
            view.bubbles = [bubbles.Bubble(SESSION.state, '你好！你要去哪儿？', view.rt._anchor(a.id))]
            shot(f'bubble-{scene_id}')
            view.bubbles = []

    if only == 5:
        from richu.core import talisman as TL
        from richu.ui.puzzles import Bells, TalismanEditor

        st = copy.deepcopy(g.state)
        st.flags.pop('tal:doumu_gate', None)
        st.flags.pop('doumu_open', None)
        SESSION.state = st  # type: ignore[assignment]
        view = SceneView()
        APP.replace_all(view)
        view.load('5a')
        shot('scene-5a-closed')
        APP.push(TalismanEditor(TL.TALISMANS['doumu_gate']))
        shot('puzzle-talisman')
        SESSION.state = copy.deepcopy(g.state)  # type: ignore[assignment]
        view = SceneView()
        APP.replace_all(view)
        view.load('5d')
        APP.push(Bells('风雨日云月', '雨云月', ['雨后云开月出来']))
        shot('puzzle-bells')
        print(f'{n} screenshots in {out}')
        return

    if only == 4:
        from richu.content.chapters.ch4 import CARGO
        from richu.ui.puzzles import CargoList, TeaTray

        SESSION.state = copy.deepcopy(g.state)  # type: ignore[assignment]
        view = SceneView()
        APP.replace_all(view)
        view.load('4a')
        cl = CargoList(CARGO)
        cl.ok[0] = True
        cl.row = 1
        APP.push(cl)
        shot('puzzle-cargo')
        APP.replace_all(view)
        view.load('4b')
        tt = TeaTray([{'zh': '二号桌：一碗面条，一杯牛奶', 'want': {'noodles': 1, 'milk': 1}}])
        tt.tray = ['noodles']
        APP.push(tt)
        shot('puzzle-tray')
        print(f'{n} screenshots in {out}')
        return

    if only == 3:
        from richu.ui.composer import BrushPad
        from richu.ui.puzzles import FaceGame

        SESSION.state = copy.deepcopy(g.state)  # type: ignore[assignment]
        view = SceneView()
        APP.replace_all(view)
        view.load('3c')
        game = FaceGame(['头发', '眼睛', '耳朵', '鼻子', '嘴'])
        APP.push(game)
        shot('puzzle-face-learn')
        game.phase, game.step = 'quiz', 1
        game.done_parts = [game.answers[0]]
        shot('puzzle-face-quiz')
        APP.replace_all(view)
        view.load('3b')
        APP.push(BrushPad())
        shot('brush-pad-3b')
        print(f'{n} screenshots in {out}')
        return

    if only == 2:
        from richu.ui.puzzles import AncientStele

        SESSION.state = copy.deepcopy(g.state)  # type: ignore[assignment]
        view = SceneView()
        APP.replace_all(view)
        view.load('2e')
        APP.push(AncientStele('日月山水人'))
        shot('puzzle-ancient')
        print(f'{n} screenshots in {out}')
        return

    SESSION.state = final  # type: ignore[assignment]
    SESSION.state.guesses.update({'你': 'ты', '好': 'хорошо', '我': 'я', '是': 'быть', '人': 'человек', '火': 'огонь', '车': 'повозка'})
    view = SceneView()
    APP.replace_all(view)
    view.load('1c')
    view.narration = bubbles.Narration('За окном широкая мутно-жёлтая река. Поезд идёт по длинному мосту.')
    shot('narration')
    view.narration = None
    for tab in ('Знаки', 'Слова', 'Страницы', 'Тексты', 'Фразы', 'Грамматика', 'Повторение'):
        APP.replace_all(view)
        APP.push(Journal(view, tab))
        shot(f'journal-{tab}')
    from richu.content import pages as PG

    for pid in ('greet', 'cafe', 'this'):
        APP.replace_all(view)
        st = SESSION.state
        st.pages.pop(pid, None)
        APP.push(PageView(PG.page(pid)))
        shot(f'page-{pid}')
    APP.replace_all(view)
    APP.push(GlyphCard('火', view))
    shot('card-fire')
    SESSION.state.confirmed.pop('车', None)
    APP.replace_all(view)
    APP.push(GlyphCard('车', view))
    shot('card-cart-unconfirmed')
    APP.replace_all(view)
    APP.push(Reader('diary_1'))
    shot('reader-diary1')
    APP.replace_all(view)
    APP.push(AnswerPad('你好'))
    shot('answer-pad')
    SESSION.state.flags['brush_awake'] = True
    APP.replace_all(view)
    APP.push(BrushPad())
    shot('brush-pad')
    print(f'{n} screenshots in {out}')


if __name__ == '__main__':
    main()

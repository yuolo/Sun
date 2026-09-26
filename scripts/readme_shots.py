#!/usr/bin/env python3
"""Screenshots for the README (docs/screenshots/*.png, ×2).

    python scripts/readme_shots.py
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

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'docs', 'screenshots')


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    platform.use_memory_storage()
    app.init(headless=True)
    from richu.content.world import load
    from richu.core import talisman as TL
    from richu.core.headless import HeadlessGame
    from richu.devtools import playthrough as pt
    from richu.ui import bubbles
    from richu.ui.card import GlyphCard
    from richu.ui.journal import PageView
    from richu.ui.menus import TitleScreen
    from richu.ui.puzzles import TalismanEditor
    from richu.ui.scene_view import SceneView
    from richu.ui.session import SESSION
    from richu.content import pages as PG

    load()
    SESSION.boot()
    d = Driver()

    def shot(name: str, frames: int = 3) -> None:
        d.step(frames)
        d.shot(os.path.join(OUT, name), 2)

    g = HeadlessGame()
    at: dict[str, object] = {}
    orig_goto = g.c.goto

    async def goto(scene_id: str, entry: str) -> None:
        await orig_goto(scene_id, entry)
        at.setdefault(scene_id, copy.deepcopy(g.state))

    g.c.goto = goto  # type: ignore[method-assign]
    pt.play_prologue(g)
    pt.play_chapter1(g)
    pt.solve_open_pages(g, 1)
    pt.play_chapter2(g, sleep=True)
    pt.solve_open_pages(g, 2)
    pt.play_chapter3(g, climb=True)
    pt.solve_open_pages(g, 3)
    pt.play_chapter4(g, climb=True)
    pt.solve_open_pages(g, 4)
    pt.play_chapter5(g, climb=True)
    pt.solve_open_pages(g, 5)
    pt.play_chapter6(g, climb=True)
    pt.solve_open_pages(g, 6)
    pt.play_chapter7(g, climb=True)
    pt.solve_open_pages(g, 7)
    pt.play_chapter8(g)
    final = copy.deepcopy(g.state)

    def scene(scene_id: str, state: object, bubble: tuple[str, str] | None = None) -> SceneView:
        SESSION.state = copy.deepcopy(state)  # type: ignore[assignment]
        view = SceneView()
        APP.replace_all(view)
        view.load(scene_id)
        d.move(300, 10)
        if bubble:
            d.step(2)
            view.bubbles = [bubbles.Bubble(SESSION.state, bubble[1], view.rt._anchor(bubble[0]))]
        return view

    APP.replace_all(TitleScreen())
    d.move(160, 150)
    shot('title', 40)
    scene('3a', at['3a'], ('fisher', '早上好！你是来看大桥的吗？'))
    shot('bridge')
    scene('4b', at['4b'], ('storyteller', '安静！安静！我给大家讲一个故事。'))
    shot('teahouse')
    st = copy.deepcopy(at['5a'])
    view = scene('5a', st)
    APP.push(TalismanEditor(TL.TALISMANS['doumu_gate']))
    shot('talisman')
    scene('5d', at['6a'], ('monk', '钟声很好听吧？月亮出来了。'))
    shot('zhongtianmen')
    scene('7b', at['7c'])
    shot('heavenly-street')
    scene('8b', final, ('liming', '日出了……'))
    shot('sunrise')
    view = scene('3c', at['3d'])
    APP.push(PageView(PG.page('face')))
    shot('journal-page')
    view = scene('3b', at['3c'])
    APP.push(GlyphCard('火', view))
    shot('card')
    print('screenshots in', OUT)


if __name__ == '__main__':
    main()

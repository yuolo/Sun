"""The route map: places visited in the current chapter; click one to go there."""
from __future__ import annotations

from typing import Any

import pyxel

from ..art import palette as P
from ..content.world import CHAPTERS, SCENES, load
from ..engine import text, ui
from ..engine.app import H, W, Screen
from ..engine.input import INPUT
from .session import SESSION


class MapScreen(Screen):
    def __init__(self, view: Any) -> None:
        super().__init__()
        load()
        self.view = view
        s = SESSION.state
        cur = view.scene.chapter if view.scene else s.chapter
        self.places = [sc for sc in SCENES if sc.chapter == cur and sc.id in s.visited]
        self.chapter = next((c for c in CHAPTERS if c.n == cur), CHAPTERS[0])

    def rows(self) -> list[tuple[Any, int]]:
        return [(sc, 44 + i * 18) for i, sc in enumerate(self.places)]

    def update(self) -> None:
        if INPUT.key(pyxel.KEY_ESCAPE) or INPUT.key(pyxel.KEY_M) or INPUT.right:
            self.close()
            return
        for sc, y in self.rows():
            if INPUT.click(40, y, W - 80, 16) and self.view.scene and sc.id != self.view.scene.id:
                self.close()
                entry = next(iter(sc.entries))
                self.view.run(self.view.rt.goto(sc.id, entry), 'map')
                return
        if INPUT.click_anywhere():
            self.close()

    def draw(self) -> None:
        pyxel.dither(0.6)
        pyxel.rect(0, 0, W, H, P.INK)
        pyxel.dither(1.0)
        ui.panel(30, 14, W - 60, H - 28, 'paper')
        text.center(W // 2, 18, f'{self.chapter.zh} · {self.chapter.title}', P.LACQUER)
        text.center(W // 2, 32, 'Куда пойти?', P.STONE, small=True)
        cur = self.view.scene.id if self.view.scene else ''
        for sc, y in self.rows():
            here = sc.id == cur
            if INPUT.inside(40, y, W - 80, 16) and not here:
                pyxel.rect(40, y, W - 80, 16, P.LAMP)
            pyxel.circ(50, y + 8, 3, P.VERMILION if here else P.OCHRE)
            if sc.zh:
                text.draw(60, y + 1, sc.zh, P.INK)
            text.draw(60 + (text.width(sc.zh) + 8 if sc.zh else 0), y + 2, sc.title + (' (вы здесь)' if here else ''), P.STONE if here else P.INK, small=True)

"""Title screen (placeholder art until the scene kit exists)."""
from __future__ import annotations

import pyxel

from ..art.palette import DUSK, GOLD, INK, LAMP, NAVY, NIGHT, OCHRE, PAPER, PEACH, ROSE, STONE, VERMILION
from ..engine import text, ui
from ..engine.app import H, W, Screen


class TitleScreen(Screen):
    opaque = True

    def __init__(self) -> None:
        super().__init__()
        bw = 96
        x = (W - bw) // 2
        self.buttons = [
            ui.Button(x, 112, bw, 16, 'Новая игра', style='night'),
            ui.Button(x, 131, bw, 16, 'Продолжить', style='night'),
            ui.Button(x, 150, bw, 16, 'Настройки', style='night'),
        ]

    def update(self) -> None:
        for b in self.buttons:
            b.update()

    def draw(self) -> None:
        # sky in dithered bands
        bands = [NIGHT, NAVY, DUSK, ROSE, PEACH]
        for i, col in enumerate(bands):
            y0 = i * 22
            pyxel.rect(0, y0, W, 22, col)
            if i + 1 < len(bands):
                pyxel.dither(0.5)
                pyxel.rect(0, y0 + 16, W, 6, bands[i + 1])
                pyxel.dither(1.0)
        pyxel.circ(W // 2, 104, 22, LAMP)
        # mountains
        for layer, (col, base, amp) in enumerate(((STONE, 96, 26), (NAVY, 112, 20), (INK, 128, 14))):
            for x in range(W):
                n = pyxel.noise(x / 40 + layer * 7, layer * 3.1)
                y = int(base - amp * (0.6 + n) - 18 * max(0, 1 - abs(x - W / 2) / 90) * (2 - layer) / 2)
                pyxel.line(x, y, x, H, col)
        text.brush().draw(W // 2 - 44, 14, '日', INK, STONE, OCHRE)
        text.brush().draw(W // 2 + 4, 14, '出', INK, STONE, OCHRE)
        text.center(W // 2, 58, 'В О С Х О Д', PAPER, shadow=INK)
        for b in self.buttons:
            b.draw()
        text.draw(4, H - 12, 'v2 · Pyxel', OCHRE, small=True)
        _ = (GOLD, VERMILION)

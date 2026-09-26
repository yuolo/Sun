"""Drives the game frame by frame in headless mode (tests, screenshots)."""
from __future__ import annotations

import pyxel

from .app import APP


class Driver:
    def step(self, frames: int = 1) -> None:
        for _ in range(frames):
            pyxel.flip()
            APP.update()
            APP.draw()

    def move(self, x: int, y: int) -> None:
        pyxel.flip()
        pyxel.set_mouse_pos(x, y)
        APP.update()
        APP.draw()

    def click(self, x: int, y: int, button: int | None = None) -> None:
        btn = pyxel.MOUSE_BUTTON_LEFT if button is None else button
        pyxel.flip()
        pyxel.set_mouse_pos(x, y)
        pyxel.set_btn(btn, True)
        APP.update()
        APP.draw()
        pyxel.flip()
        pyxel.set_btn(btn, False)
        APP.update()
        APP.draw()

    def key(self, key: int) -> None:
        pyxel.flip()
        pyxel.set_btn(key, True)
        APP.update()
        APP.draw()
        pyxel.flip()
        pyxel.set_btn(key, False)
        APP.update()
        APP.draw()

    def type(self, text: str) -> None:
        pyxel.flip()
        pyxel.set_input_text(text)
        APP.update()
        APP.draw()

    def shot(self, path: str, scale: int = 3) -> None:
        """Saves the current frame as <path>.png."""
        if path.endswith('.png'):
            path = path[:-4]
        pyxel.screen.save(path, scale)

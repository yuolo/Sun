"""Mouse, keyboard and text input for one frame, with click consumption.

Only the top screen receives input. Within a screen, the first widget that
takes a click consumes it, so overlapping widgets don't both fire.
"""
from __future__ import annotations

import pyxel


class Input:
    def __init__(self) -> None:
        self.mx = 0
        self.my = 0
        self.pressed = False
        self.released = False
        self.held = False
        self.right = False
        self.wheel = 0
        self.text = ''
        self._taken = False
        self._keys_taken: set[int] = set()
        self._last_wheel = 0
        self.moved = False

    def begin_frame(self) -> None:
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        self.moved = (mx, my) != (self.mx, self.my)
        self.mx, self.my = mx, my
        self.pressed = pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
        self.released = pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT)
        self.held = pyxel.btn(pyxel.MOUSE_BUTTON_LEFT)
        self.right = pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT)
        self.wheel = pyxel.mouse_wheel
        self.text = pyxel.input_text
        self._taken = False
        self._keys_taken.clear()

    # ---------------------------------------------------------------- mouse

    def inside(self, x: float, y: float, w: float, h: float) -> bool:
        return x <= self.mx < x + w and y <= self.my < y + h

    def hover(self, x: float, y: float, w: float, h: float) -> bool:
        return self.inside(x, y, w, h)

    def click(self, x: float, y: float, w: float, h: float) -> bool:
        """True once if the left button was pressed inside the rectangle."""
        if self.pressed and not self._taken and self.inside(x, y, w, h):
            self._taken = True
            return True
        return False

    def click_anywhere(self) -> bool:
        if self.pressed and not self._taken:
            self._taken = True
            return True
        return False

    def take(self) -> None:
        self._taken = True

    @property
    def taken(self) -> bool:
        return self._taken

    # ---------------------------------------------------------------- keys

    def key(self, key: int, repeat: bool = False) -> bool:
        if key in self._keys_taken:
            return False
        hit = pyxel.btnp(key, hold=12, repeat=3) if repeat else pyxel.btnp(key)
        if hit:
            self._keys_taken.add(key)
        return hit

    def any_key(self, *keys: int) -> bool:
        return any(self.key(k) for k in keys)

    def advance(self) -> bool:
        """Space / Enter / click: move a dialogue forward."""
        return self.any_key(pyxel.KEY_SPACE, pyxel.KEY_RETURN, pyxel.KEY_KP_ENTER) or self.click_anywhere()

    def cancel(self) -> bool:
        return self.key(pyxel.KEY_ESCAPE) or self.right


INPUT = Input()

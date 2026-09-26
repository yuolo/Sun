"""Grandfather's sketches above diary entries (80×44), registered by the content."""
from __future__ import annotations

from collections.abc import Callable

import pyxel

from . import kit
from . import palette as P

SKETCHES: dict[str, Callable[[int, int], None]] = {}


def sketch(name: str) -> Callable[[Callable[[int, int], None]], Callable[[int, int], None]]:
    def deco(fn: Callable[[int, int], None]) -> Callable[[int, int], None]:
        SKETCHES[name] = fn
        return fn

    return deco


def draw(name: str, x: int, y: int) -> None:
    pyxel.rect(x, y, 80, 44, P.PAPER)
    fn = SKETCHES.get(name)
    if fn:
        pyxel.clip(x, y, 80, 44)
        kit.canvas(pyxel)
        fn(x, y)
        pyxel.clip()
    pyxel.rectb(x, y, 80, 44, P.STONE)

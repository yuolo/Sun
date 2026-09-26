"""Building blocks for 32×32 page pictures: people, arrows, hands, clocks, flags, bubbles."""
from __future__ import annotations

import math

import pyxel

from . import icons
from . import palette as P


def person(x: int, y: int, col: int = P.DARK_BLUE, skin: int = P.PEACH, arm: str = '', hair: int = P.INK) -> None:
    """A little figure 14 px tall with its feet at (x, y). arm: '' · up · out · self · bow."""
    if arm == 'bow':
        pyxel.rect(x - 2, y - 6, 4, 6, col)
        pyxel.rect(x - 1, y - 9, 8, 4, col)
        pyxel.circ(x + 7, y - 7, 2, skin)
        pyxel.pset(x + 7, y - 9, hair)
        pyxel.line(x - 1, y, x - 1, y - 1, P.INK)
        pyxel.line(x + 1, y, x + 1, y - 1, P.INK)
        return
    pyxel.rect(x - 1, y - 4, 1, 4, P.INK)
    pyxel.rect(x + 1, y - 4, 1, 4, P.INK)
    pyxel.rect(x - 2, y - 10, 5, 6, col)
    pyxel.circ(x, y - 12, 2, skin)
    pyxel.line(x - 2, y - 14, x + 2, y - 14, hair)
    if arm == 'up':
        pyxel.line(x + 3, y - 9, x + 5, y - 14, col)
        pyxel.pset(x + 5, y - 15, skin)
    elif arm == 'out':
        pyxel.line(x + 3, y - 9, x + 7, y - 9, col)
        pyxel.pset(x + 8, y - 9, skin)
    elif arm == 'self':
        pyxel.line(x + 3, y - 9, x + 1, y - 8, skin)
    elif arm == 'wide':
        pyxel.line(x - 3, y - 9, x - 7, y - 12, col)
        pyxel.line(x + 3, y - 9, x + 7, y - 12, col)


def sitting(x: int, y: int, col: int = P.DARK_BLUE) -> None:
    pyxel.rect(x - 5, y - 6, 10, 2, P.WOOD)
    pyxel.rect(x - 5, y - 4, 1, 4, P.WOOD)
    pyxel.rect(x + 4, y - 4, 1, 4, P.WOOD)
    pyxel.rect(x - 4, y - 14, 3, 8, P.WOOD)
    pyxel.rect(x - 1, y - 13, 4, 6, col)
    pyxel.rect(x - 1, y - 7, 6, 2, col)
    pyxel.rect(x + 4, y - 5, 1, 5, P.INK)
    pyxel.circ(x + 1, y - 15, 2, P.PEACH)


def arrow(x0: int, y0: int, x1: int, y1: int, col: int = P.VERMILION) -> None:
    pyxel.line(x0, y0, x1, y1, col)
    ang = math.atan2(y1 - y0, x1 - x0)
    for d in (2.5, -2.5):
        pyxel.line(x1, y1, round(x1 - 4 * math.cos(ang + d / 3)), round(y1 - 4 * math.sin(ang + d / 3)), col)


def eye(x: int, y: int) -> None:
    pyxel.elli(x - 7, y - 4, 15, 9, P.WHITE)
    pyxel.ellib(x - 7, y - 4, 15, 9, P.INK)
    pyxel.circ(x, y, 2, P.DARK_BLUE)
    pyxel.pset(x, y, P.INK)


def clock(x: int, y: int, r: int, hour: float, minute: float, hi: str = '') -> None:
    pyxel.circ(x, y, r, P.WHITE)
    pyxel.circb(x, y, r, P.INK)
    for i in range(12):
        a = math.radians(i * 30 - 90)
        pyxel.pset(round(x + (r - 2) * math.cos(a)), round(y + (r - 2) * math.sin(a)), P.STONE)
    ha = math.radians((hour % 12 + minute / 60) * 30 - 90)
    ma = math.radians(minute * 6 - 90)
    pyxel.line(x, y, round(x + r * 0.5 * math.cos(ha)), round(y + r * 0.5 * math.sin(ha)), P.VERMILION if hi == 'hour' else P.INK)
    pyxel.line(x, y, round(x + r * 0.8 * math.cos(ma)), round(y + r * 0.8 * math.sin(ma)), P.VERMILION if hi == 'minute' else P.INK)


def flag(x: int, y: int, kind: str) -> None:
    pyxel.line(x, y, x, y + 22, P.WOOD)
    if kind == 'cn':
        pyxel.rect(x + 1, y, 22, 14, P.VERMILION)
        pyxel.pset(x + 5, y + 4, P.YELLOW)
        pyxel.rect(x + 4, y + 3, 3, 3, P.YELLOW)
        for dx, dy in ((9, 2), (10, 5), (10, 8), (9, 10)):
            pyxel.pset(x + dx, y + dy, P.YELLOW)
    elif kind == 'ru':
        pyxel.rect(x + 1, y, 22, 5, P.WHITE)
        pyxel.rect(x + 1, y + 5, 22, 5, P.DARK_BLUE)
        pyxel.rect(x + 1, y + 10, 22, 5, P.VERMILION)
        pyxel.rectb(x + 1, y, 22, 15, P.MIST)


def bubble(x: int, y: int, w: int, h: int, fill: int = P.WHITE) -> None:
    pyxel.rect(x, y, w, h, fill)
    pyxel.rectb(x, y, w, h, P.INK)
    pyxel.tri(x + 3, y + h - 1, x + 7, y + h - 1, x + 2, y + h + 3, fill)
    pyxel.line(x + 2, y + h + 3, x + 3, y + h, P.INK)


def dots(n: int, x: int, y: int) -> None:
    """n dots in rows of five."""
    for i in range(n):
        cx = x + (i % 5) * 5
        cy = y + (i // 5) * 6
        pyxel.circ(cx, cy, 1, P.VERMILION)


def swatch(x: int, y: int, col: int) -> None:
    pyxel.rect(x + 6, y + 6, 20, 20, col)
    pyxel.rectb(x + 6, y + 6, 20, 20, P.INK)


def compass(x: int, y: int, point: str) -> None:
    cx, cy = x + 16, y + 16
    pyxel.circ(cx, cy, 12, P.PAPER)
    pyxel.circb(cx, cy, 12, P.INK)
    dirs = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}
    for d, (dx, dy) in dirs.items():
        col = P.VERMILION if d == point else P.STONE
        pyxel.line(cx, cy, cx + dx * 10, cy + dy * 10, col)
    dx, dy = dirs[point]
    pyxel.circ(cx + dx * 10, cy + dy * 10, 2, P.VERMILION)


def icon(name: str, x: int, y: int, scale: float = 1.0) -> None:
    icons.draw(name, x, y, scale)


def door(x: int, y: int, w: int = 12, h: int = 18) -> None:
    pyxel.rect(x, y, w, h, P.WOOD)
    pyxel.rectb(x, y, w, h, P.INK)
    pyxel.pset(x + w - 3, y + h // 2, P.GOLD)

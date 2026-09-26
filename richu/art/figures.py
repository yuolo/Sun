"""Procedural pixel people.

A figure is painted into a small grid (32×40, feet at the bottom centre),
outlined in ink and cached as a Pyxel image per walk frame. Facing left is
drawn by flipping the image.
"""
from __future__ import annotations

import pyxel

from ..core.types import FigureSpec
from .palette import (
    DARK_BLUE, GOLD, GREY, INK, LACQUER, LAMP, MIST, NAVY, OCHRE, PAPER, PEACH, PINE, PINK, PLUM, STONE, VERMILION, WHITE, WOOD,
)

W, H = 32, 40
CX = 16  # centre column
FRAMES = 4  # 0 stand, 1..3 walk (1 and 3 mirror each other)

_cache: dict[tuple, pyxel.Image] = {}


class Grid:
    def __init__(self) -> None:
        self.px = [[0] * W for _ in range(H)]

    def rect(self, x: int, y: int, w: int, h: int, c: int) -> None:
        for yy in range(max(0, y), min(H, y + h)):
            row = self.px[yy]
            for xx in range(max(0, x), min(W, x + w)):
                row[xx] = c

    def dot(self, x: int, y: int, c: int) -> None:
        if 0 <= x < W and 0 <= y < H:
            self.px[y][x] = c

    def hline(self, x0: int, x1: int, y: int, c: int) -> None:
        self.rect(min(x0, x1), y, abs(x1 - x0) + 1, 1, c)

    def vline(self, x: int, y0: int, y1: int, c: int) -> None:
        self.rect(x, min(y0, y1), 1, abs(y1 - y0) + 1, c)

    def line(self, x0: int, y0: int, x1: int, y1: int, c: int) -> None:
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            self.dot(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c)

    def outline(self, c: int = INK) -> None:
        src = [row[:] for row in self.px]
        for y in range(H):
            for x in range(W):
                if src[y][x]:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < H and src[ny][nx] not in (0, c):
                        self.px[y][x] = c
                        break

    def image(self) -> pyxel.Image:
        img = pyxel.Image(W, H)
        img.cls(0)
        for y, row in enumerate(self.px):
            for x, c in enumerate(row):
                if c:
                    img.pset(x, y, c)
        return img


def _key(spec: FigureSpec, frame: int) -> tuple:
    return (
        spec.coat, spec.trim, spec.style, spec.hat, spec.hat_color, spec.hair, spec.skin, spec.legs, spec.prop, spec.pose,
        spec.beard, spec.glasses, spec.kind, frame,
    )


def sprite(spec: FigureSpec, frame: int = 0) -> pyxel.Image:
    key = _key(spec, frame)
    img = _cache.get(key)
    if img is None:
        g = Grid()
        paint(g, spec, frame)
        g.outline()
        img = g.image()
        _cache[key] = img
    return img


def draw(spec: FigureSpec, x: float, y: float, facing: str = 'right', frame: int = 0, scale: float = 1.0) -> None:
    """Draws a figure with its feet at (x, y)."""
    img = sprite(spec, frame)
    w = W if facing == 'right' else -W
    if scale == 1.0:
        pyxel.blt(round(x) - CX, round(y) - H + 1, img, 0, 0, w, H, 0)
    else:
        # blt scales around the centre of the image; keep the feet on the ground
        pyxel.blt(round(x) - CX, round(y - H * scale / 2 - H / 2 + scale / 2), img, 0, 0, w, H, 0, scale=scale)


def height(spec: FigureSpec) -> int:
    return {'child': 21, 'old': 28}.get(spec.kind, 30)


# ---------------------------------------------------------------- painting


def paint(g: Grid, s: FigureSpec, frame: int) -> None:
    child = s.kind == 'child'
    old = s.kind == 'old'
    skin = s.skin if s.skin is not None else PEACH
    hair = s.hair if s.hair is not None else (GREY if old else INK)
    legs_col = s.legs if s.legs is not None else (WOOD if s.style == 'robe' else NAVY)
    trim = s.trim if s.trim is not None else s.coat
    feet = H - 1

    if child:
        head_w, head_h, torso_h, leg_h = 5, 5, 6, 4
    else:
        head_w, head_h, torso_h, leg_h = 6, 6, 11, 7
    lean = 1 if old else 0

    sitting = s.pose == 'sit'
    if sitting:
        leg_h = 3

    # legs
    leg_top = feet - leg_h
    # (far leg x, near leg x) per frame: stand · stride · passing · other stride
    far_x, near_x = {0: (CX - 2, CX + 1), 1: (CX - 3, CX + 2), 2: (CX - 1, CX), 3: (CX + 2, CX - 3)}[frame % 4]
    bob = 1 if frame in (1, 3) else 0
    if sitting:
        g.rect(CX - 2, feet - 2, 7, 2, legs_col)
        g.rect(CX + 4, feet - 2, 1, 3, legs_col)
        g.dot(CX + 5, feet, INK)
    else:
        shoe = INK if s.style != 'dress' else WOOD
        for lx in (far_x, near_x):
            g.rect(lx, leg_top, 2, leg_h, legs_col)
            g.rect(lx, feet, 3, 1, shoe)

    top = leg_top - torso_h + bob
    # torso
    tw = 7 if child else 8
    tx = CX - tw // 2 + lean
    if s.style == 'robe':
        g.rect(tx, top, tw, torso_h + (leg_h - 2 if not sitting else 0), s.coat)
        g.rect(tx - 1, top + torso_h - 2, tw + 2, (leg_h - 1) if not sitting else 1, s.coat)
        g.vline(tx + tw // 2 + 1, top + 1, top + torso_h + leg_h - 3, trim)
    elif s.style == 'dress':
        g.rect(tx, top, tw, torso_h, s.coat)
        g.rect(tx - 1, top + torso_h - 3, tw + 2, 5, s.coat)
        g.hline(tx - 1, tx + tw, top + torso_h + 1, trim)
    else:
        g.rect(tx, top, tw, torso_h + 1, s.coat)
        g.hline(tx, tx + tw - 1, top + torso_h, trim)
        if s.style == 'uniform':
            g.dot(tx + tw // 2 + 1, top + 3, GOLD)
            g.dot(tx + tw // 2 + 1, top + 6, GOLD)
    # collar
    g.rect(tx + tw // 2 - 1, top, 3, 1, trim)
    # arm (front) and hand
    ax = tx + tw - 2
    arm_len = torso_h - 3
    swing = {0: 0, 1: -1, 2: 0, 3: 1}[frame % 4]
    g.rect(ax, top + 1, 2, arm_len, s.coat)
    g.rect(ax + (1 if swing > 0 else 0), top + 1 + arm_len, 2, 1, skin)
    hand = (ax + 1, top + 1 + arm_len)

    # head
    hx = CX - head_w // 2 + 1 + lean * 2
    hy = top - head_h - 1
    g.rect(hx + 1, top - 1, 3, 1, skin)  # neck
    g.rect(hx, hy, head_w, head_h, skin)
    g.dot(hx + head_w - 2, hy + head_h // 2, INK)  # eye
    if s.glasses:
        g.hline(hx + head_w - 3, hx + head_w - 1, hy + head_h // 2, INK)
        g.dot(hx + head_w - 2, hy + head_h // 2, MIST)
    if s.beard:
        g.rect(hx + head_w - 3, hy + head_h - 2, 3, 3, GREY if old else hair)
    _hat(g, s, hx, hy, head_w, head_h, hair)
    _prop(g, s, hand, top, hx, hy)


def _hat(g: Grid, s: FigureSpec, hx: int, hy: int, w: int, h: int, hair: int) -> None:
    hc = s.hat_color if s.hat_color is not None else hair
    kind = s.hat
    back = hx  # the back of the head (facing right)
    if kind in ('short', 'long', 'ponytail', 'bun', 'twinbuns', 'topknot'):
        g.rect(hx, hy - 1, w, 2, hair)
        g.rect(back, hy, 2, h - 2, hair)
        if kind == 'long':
            g.rect(back - 1, hy + 1, 2, h + 4, hair)
        elif kind == 'ponytail':
            g.rect(back - 2, hy + 1, 2, 4, hair)
        elif kind == 'bun':
            g.rect(back - 1, hy - 2, 3, 3, hair)
        elif kind == 'twinbuns':
            g.rect(hx - 1, hy - 2, 2, 2, hair)
            g.rect(hx + w - 1, hy - 2, 2, 2, hair)
        elif kind == 'topknot':
            g.rect(hx + w // 2 - 1, hy - 3, 2, 2, hair)
    elif kind == 'bald':
        g.rect(back, hy + 1, 1, h - 3, GREY)
    elif kind == 'straw':
        g.rect(hx - 2, hy, w + 4, 1, hc if s.hat_color is not None else OCHRE)
        g.rect(hx + 1, hy - 2, w - 2, 2, hc if s.hat_color is not None else OCHRE)
        g.dot(hx + w // 2, hy - 3, hc if s.hat_color is not None else OCHRE)
    elif kind == 'wide':
        g.rect(hx - 3, hy, w + 6, 1, hc)
        g.rect(hx, hy - 2, w, 2, hc)
    elif kind in ('cap', 'police'):
        col = hc if s.hat_color is not None else (NAVY if kind == 'police' else VERMILION)
        g.rect(hx, hy - 1, w, 2, col)
        g.rect(hx + w - 1, hy + 1, 3, 1, col)
        g.rect(back, hy + 1, 1, 3, hair)
        if kind == 'police':
            g.dot(hx + w // 2, hy - 1, GOLD)
    elif kind == 'scholar':
        g.rect(hx, hy - 2, w, 3, INK)
        g.rect(hx + 1, hy - 3, w - 2, 1, INK)
        g.rect(back, hy + 1, 1, 3, hair)
    elif kind == 'hood':
        col = hc if s.hat_color is not None else GREY
        g.rect(hx - 1, hy - 1, w + 1, 2, col)
        g.rect(hx - 1, hy, 2, h + 1, col)
    elif kind == 'nun':
        col = hc if s.hat_color is not None else INK
        g.rect(hx - 1, hy - 2, w + 1, 3, col)
        g.rect(hx - 1, hy, 2, h + 2, col)


def _prop(g: Grid, s: FigureSpec, hand: tuple[int, int], top: int, hx: int, hy: int) -> None:
    x, y = hand
    p = s.prop
    if not p:
        return
    if p == 'pole':  # porter's carrying pole with loads on both ends
        g.hline(3, W - 4, top + 1, OCHRE)
        for bx in (2, W - 7):
            g.vline(bx + 2, top + 2, top + 5, WOOD)
            g.rect(bx, top + 6, 5, 5, OCHRE)
            g.hline(bx, bx + 4, top + 6, WOOD)
    elif p in ('staff', 'oar', 'broom', 'rod'):
        col = WOOD if p != 'rod' else OCHRE
        g.vline(x + 1, y - 13 if p != 'rod' else y - 6, y + 6, col)
        if p == 'oar':
            g.rect(x, y + 4, 3, 4, WOOD)
        elif p == 'broom':
            g.rect(x, y + 4, 3, 3, OCHRE)
        elif p == 'rod':
            g.line(x + 1, y - 6, x + 9, y - 14, OCHRE)
    elif p in ('lantern', 'lantern_dark'):
        g.vline(x + 1, y, y + 2, WOOD)
        g.rect(x, y + 3, 4, 5, VERMILION if p == 'lantern' else PLUM)
        g.hline(x, x + 3, y + 3, LACQUER)
        g.dot(x + 1, y + 5, LAMP if p == 'lantern' else STONE)
    elif p == 'fan':
        g.rect(x + 1, y - 3, 4, 3, PAPER)
        g.dot(x + 1, y, WOOD)
    elif p == 'book':
        g.rect(x, y - 2, 4, 3, DARK_BLUE)
        g.dot(x + 1, y - 2, PAPER)
    elif p == 'umbrella':
        g.vline(x + 1, y - 12, y + 1, WOOD)
        g.rect(x - 5, y - 13, 13, 2, VERMILION)
        g.rect(x - 3, y - 15, 9, 2, VERMILION)
    elif p == 'suitcase':
        g.rect(x - 1, y + 1, 7, 6, VERMILION)
        g.hline(x + 1, x + 3, y, INK)
    elif p == 'bag':
        g.rect(x - 1, y - 2, 4, 5, OCHRE)
    elif p == 'basket':
        g.rect(x - 1, y, 5, 4, OCHRE)
        g.hline(x - 1, x + 3, y, WOOD)
    elif p == 'cup':
        g.rect(x, y - 2, 3, 2, WHITE)
    elif p == 'brush':
        g.vline(x + 1, y - 7, y, OCHRE)
        g.rect(x + 1, y - 9, 1, 2, INK)
    elif p == 'spear':
        g.vline(x + 1, y - 18, y + 6, WOOD)
        g.rect(x, y - 21, 3, 3, GREY)
        g.dot(x + 1, y - 16, VERMILION)
    elif p == 'flag':
        g.vline(x + 1, y - 16, y + 4, WOOD)
        g.rect(x + 2, y - 16, 6, 4, VERMILION)
    elif p == 'tray':
        g.rect(x - 2, y - 1, 7, 1, WOOD)
        g.rect(x - 1, y - 3, 2, 2, PAPER)
        g.rect(x + 2, y - 3, 2, 2, PAPER)
    _ = (PINE, PINK)

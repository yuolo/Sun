"""Pixel landscape and architecture kit.

Every function draws onto the current canvas ``C`` (the screen or a Pyxel
image, both have the same drawing methods). Scenes are painted once in
daylight colours into a 320×180 image; the time of day is applied later with
a palette remap.
"""
from __future__ import annotations

import math
import random
from typing import Any

import pyxel

from .palette import (
    BLACK, DARK_BLUE, DUSK, GOLD, GREY, INK, JADE, LACQUER, LAMP, LIGHT_BLUE, MINT, MIST, MOSS, NAVY, OCHRE, PAPER, PEACH,
    PERIWINKLE, PINE, PLUM, ROSE, STONE, TEAL, VERMILION, WHITE, WOOD, YELLOW,
)

W, H = 320, 180

C: Any = pyxel


def canvas(target: Any) -> None:
    global C
    C = target


def rng(seed: int) -> random.Random:
    return random.Random(seed)


# ---------------------------------------------------------------- basics


def dither(alpha: float) -> None:
    C.dither(alpha)


def drect(x: float, y: float, w: float, h: float, col: int, alpha: float = 0.5) -> None:
    """A rectangle drawn through a dither pattern."""
    C.dither(alpha)
    C.rect(x, y, w, h, col)
    C.dither(1.0)


def poly(points: list[tuple[float, float]], col: int) -> None:
    """Filled convex-ish polygon as a triangle fan."""
    x0, y0 = points[0]
    for (x1, y1), (x2, y2) in zip(points[1:], points[2:]):
        C.tri(x0, y0, x1, y1, x2, y2, col)


def outline_rect(x: int, y: int, w: int, h: int, fill: int, edge: int = INK) -> None:
    C.rect(x, y, w, h, fill)
    C.rectb(x, y, w, h, edge)


# ---------------------------------------------------------------- sky


def sky(bands: list[tuple[int, int]], y0: int = 0) -> int:
    """Horizontal colour bands from the top, joined with dithered edges. Returns the bottom y."""
    y = y0
    for i, (col, h) in enumerate(bands):
        C.rect(0, y, W, h, col)
        if i + 1 < len(bands):
            nxt = bands[i + 1][0]
            drect(0, y + h - 4, W, 2, nxt, 0.25)
            drect(0, y + h - 2, W, 2, nxt, 0.5)
        y += h
    return y


def sun(x: int, y: int, r: int, col: int = LAMP, halo: int = YELLOW) -> None:
    C.dither(0.25)
    C.circ(x, y, r + 5, halo)
    C.dither(0.5)
    C.circ(x, y, r + 2, halo)
    C.dither(1.0)
    C.circ(x, y, r, col)


def moon(x: int, y: int, r: int, col: int = PAPER, sky_col: int = NAVY, phase: float = 0.0) -> None:
    C.circ(x, y, r, col)
    if phase:
        C.circ(x + round(r * phase), y - 1, r, sky_col)


def stars(seed: int, count: int, y1: int, cols: tuple[int, ...] = (WHITE, PERIWINKLE)) -> None:
    r = rng(seed)
    for _ in range(count):
        C.pset(r.randrange(W), r.randrange(y1), r.choice(cols))


def cloud(x: int, y: int, w: int, col: int = WHITE, shade: int = MIST) -> None:
    """A flat-bottomed pixel cloud about w pixels wide."""
    r = rng(x * 31 + y)
    h = max(4, w // 5)
    C.rect(x, y + h - 2, w, 3, shade)
    n = max(2, w // 10)
    for i in range(n):
        cx = x + (i + 0.5) * w / n + r.randint(-2, 2)
        rad = r.randint(h // 2 + 1, h)
        C.circ(cx, y + h - rad // 2, rad, col)
    C.rect(x, y + h, w, 2, shade)


def cloud_sea(y: int, seed: int, col: int = WHITE, shade: int = MIST) -> None:
    """A sea of clouds below a peak."""
    r = rng(seed)
    C.rect(0, y + 6, W, H - y - 6, shade)
    for i in range(-1, W // 18 + 2):
        cx = i * 18 + r.randint(-4, 4)
        C.circ(cx, y + 6 + r.randint(-2, 3), r.randint(7, 11), col)
    drect(0, y + 14, W, H - y - 14, shade, 0.5)


# ---------------------------------------------------------------- land


def ridge(base: int, amp: float, scale: float, seed: int, col: int, rim: int | None = None, peaks: list[tuple[int, int, int]] | None = None) -> list[int]:
    """A mountain silhouette. peaks: (x, height, half-width) bumps. Returns the top y per column."""
    tops = []
    for x in range(W):
        n = pyxel.noise(x / scale, seed * 1.7, 0.5)
        y = base - amp * (0.5 + n)
        for px, ph, hw in peaks or ():
            d = abs(x - px) / hw
            if d < 1:
                y -= ph * (1 - d) ** 1.4
        y = int(y)
        tops.append(y)
        C.line(x, y, x, H, col)
    if rim is not None:
        for x in range(1, W):
            if tops[x] < tops[x - 1]:
                C.pset(x, tops[x], rim)
                C.pset(x, tops[x] + 1, rim)
    return tops


def slope(points: list[tuple[int, int]], col: int, bottom: int = H) -> None:
    """Ground under a polyline, down to the bottom of the screen."""
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        for x in range(x0, x1 + 1):
            t = (x - x0) / max(1, x1 - x0)
            C.line(x, round(y0 + (y1 - y0) * t), x, bottom, col)


def ground(y: int, col: int, speck: int | None = None, seed: int = 1, density: float = 0.04, x0: int = 0, x1: int = W) -> None:
    C.rect(x0, y, x1 - x0, H - y, col)
    if speck is not None:
        r = rng(seed)
        for _ in range(int((x1 - x0) * (H - y) * density)):
            C.pset(r.randrange(x0, x1), r.randrange(y, H), speck)


def mist(y: int, h: int, col: int = MIST, alpha: float = 0.5) -> None:
    drect(0, y, W, h, col, alpha)


def water(y: int, h: int, col: int = TEAL, light: int = MINT, seed: int = 3, x0: int = 0, x1: int = W) -> None:
    C.rect(x0, y, x1 - x0, h, col)
    r = rng(seed)
    for _ in range((x1 - x0) * h // 30):
        wx, wy = r.randrange(x0, x1 - 4), r.randrange(y + 1, y + h)
        C.line(wx, wy, wx + r.randint(2, 5), wy, light)


def water_anim(y: int, h: int, frame: int, light: int = MINT, col: int = TEAL, x0: int = 0, x1: int = W) -> None:
    """Moving glints drawn every frame over a water band."""
    r = rng(y * 7 + x0)
    for i in range(max(6, (x1 - x0) * h // 60)):
        wy = r.randrange(y + 1, y + h)
        speed = 0.3 + (wy - y) / max(1, h) * 0.7
        wx = x0 + (r.randrange(x1 - x0) + int(frame * speed)) % (x1 - x0)
        ln = r.randint(2, 5)
        if (frame // 8 + i) % 3:
            C.line(wx, wy, min(x1 - 1, wx + ln), wy, light)
        else:
            C.line(wx, wy, min(x1 - 1, wx + ln), wy, col)


def path_band(points: list[tuple[int, int]], width: int, col: int, edge: int | None = None) -> None:
    """A walkable path drawn along a polyline (the band sits on and below the line)."""
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        for x in range(x0, x1 + 1):
            t = (x - x0) / max(1, x1 - x0)
            y = round(y0 + (y1 - y0) * t)
            C.line(x, y - width // 2, x, y + width // 2, col)
            if edge is not None:
                C.pset(x, y - width // 2, edge)


# ---------------------------------------------------------------- plants and rocks


def pine(x: int, y: int, h: int, col: int = PINE, light: int = JADE, trunk: int = WOOD, lean: int = 0, seed: int = 0) -> None:
    """A Mount Tai pine: a crooked trunk, side branches and flat umbrella pads of needles."""
    r = rng(seed or x * 13 + y)
    pts = []
    for i in range(h):
        t = i / max(1, h)
        tx = round(x + lean * t + math.sin(t * 3.2 + seed) * 1.5)
        pts.append(tx)
        C.rect(tx, y - i, 2 if i < h * 0.6 else 1, 1, trunk)
    pads = max(2, h // 8)
    for i in range(pads):
        k = h - 1 - round(i * h * 0.55 / pads)
        k = max(2, min(h - 1, k))
        bx = pts[k]
        by = y - k
        side = -1 if i % 2 else 1
        pw = round(h * (0.28 + 0.16 * i)) + r.randint(0, 3)
        px = bx + side * r.randint(1, pw // 3)
        C.line(bx, by, px, by - 2, trunk)
        C.elli(px - pw // 2, by - 5, pw, 5, col)
        C.line(px - pw // 2 + 2, by - 5, px + pw // 2 - 3, by - 5, light)
        C.line(px - pw // 2 + 1, by - 1, px + pw // 2 - 2, by - 1, INK if col == PINE else col)


def cypress(x: int, y: int, h: int, col: int = PINE, light: int = JADE) -> None:
    C.rect(x, y - 3, 2, 4, WOOD)
    for i in range(h):
        w = max(2, round((1 - i / h) * h * 0.28 + 2))
        C.line(x + 1 - w // 2, y - 3 - i, x + 1 + w // 2, y - 3 - i, col)
        if i % 4 == 0:
            C.pset(x + w // 4 + 1, y - 3 - i, light)


def bush(x: int, y: int, w: int, col: int = MOSS, light: int = JADE) -> None:
    C.elli(x, y - w // 3, w, w // 2 + 2, col)
    C.line(x + 2, y - w // 3, x + w - 3, y - w // 3, light)


def grass(x0: int, x1: int, y: int, col: int = JADE, seed: int = 5, n: int = 30) -> None:
    r = rng(seed)
    for _ in range(n):
        gx = r.randrange(x0, x1)
        C.line(gx, y, gx + r.choice((-1, 0, 1)), y - r.randint(1, 3), col)


def rock(x: int, y: int, w: int, h: int, col: int = STONE, light: int = GREY, dark: int = PLUM) -> None:
    """A boulder with light from the upper left; (x, y) is its bottom-left."""
    C.elli(x, y - h, w, h + 2, col)
    C.elli(x + 2, y - h + 1, w // 2, h // 2, light)
    C.line(x + w // 3, y, x + w - 2, y, dark)


def cliff(x: int, y: int, w: int, h: int, col: int = STONE, light: int = GREY, dark: int = PLUM, seed: int = 9) -> None:
    """A craggy rock face."""
    r = rng(seed)
    C.rect(x, y, w, h, col)
    for _ in range(w * h // 40):
        cx, cy = r.randrange(x, x + w), r.randrange(y, y + h)
        C.line(cx, cy, cx + r.randint(-3, 3), cy + r.randint(2, 6), dark)
    for _ in range(w * h // 80):
        cx, cy = r.randrange(x, x + w), r.randrange(y, y + h)
        C.line(cx, cy, cx + r.randint(2, 5), cy, light)


# ---------------------------------------------------------------- architecture


def roof(x: int, y: int, w: int, h: int, col: int = INK, tile: int = STONE, curl: int = 2, ridge_col: int | None = None) -> None:
    """A hip roof with upturned eaves; (x, y) is the eave's left end, the roof rises h above it."""
    inset = h + 1
    for i in range(h):
        yy = y - i
        x0 = x + round(inset * i / h)
        x1 = x + w - 1 - round(inset * i / h)
        C.line(x0, yy, x1, yy, col)
    for tx in range(x + 3, x + w - 3, 3):
        C.line(tx, y - 1, tx, y - h + 2, tile)
    C.line(x - curl, y - curl, x + 2, y, col)
    C.line(x + w - 3, y, x + w - 1 + curl, y - curl, col)
    C.line(x, y + 1, x + w - 1, y + 1, tile)
    rc = ridge_col if ridge_col is not None else col
    C.line(x + inset - 1, y - h, x + w - inset, y - h, rc)
    C.rect(x + inset - 2, y - h - 2, 2, 3, rc)
    C.rect(x + w - inset, y - h - 2, 2, 3, rc)


def wall(x: int, y: int, w: int, h: int, col: int = VERMILION, dark: int = LACQUER, cap: int | None = INK) -> None:
    C.rect(x, y, w, h, col)
    C.line(x, y + h - 1, x + w - 1, y + h - 1, dark)
    if cap is not None:
        C.rect(x - 1, y - 2, w + 2, 2, cap)
        for tx in range(x, x + w, 3):
            C.pset(tx, y - 3, cap)


def door(x: int, y: int, w: int, h: int, col: int = LACQUER, studs: int | None = GOLD, open_: bool = False) -> None:
    if open_:
        C.rect(x, y, w, h, INK)
        C.rect(x - 2, y, 2, h, col)
        C.rect(x + w, y, 2, h, col)
        return
    C.rect(x, y, w, h, col)
    C.line(x + w // 2, y, x + w // 2, y + h - 1, INK)
    if studs is not None:
        for sy in range(y + 3, y + h - 2, 4):
            for sx in (x + 2, x + w - 3):
                C.pset(sx, sy, studs)


def window(x: int, y: int, w: int, h: int, lit: bool = False, frame: int = WOOD) -> None:
    C.rect(x, y, w, h, LAMP if lit else INK)
    C.rectb(x, y, w, h, frame)
    C.line(x + w // 2, y, x + w // 2, y + h - 1, frame)
    C.line(x, y + h // 2, x + w - 1, y + h // 2, frame)


def house(x: int, y: int, w: int, h: int, wall_col: int = PAPER, roof_col: int = INK, door_col: int = WOOD, windows: int = 1, lit: bool = False) -> None:
    """A village house; (x, y) is the bottom-left corner."""
    top = y - h
    C.rect(x, top, w, h, wall_col)
    C.line(x, y - 1, x + w - 1, y - 1, STONE)
    dw = max(6, w // 6)
    door(x + w // 2 - dw // 2, y - 14, dw, 14, door_col, None)
    for i in range(windows):
        wx = x + 5 + i * (w - 16) // max(1, windows - 1) if windows > 1 else x + 5
        if abs(wx + 4 - (x + w // 2)) > dw:
            window(wx, top + 5, 8, 7, lit)
    roof(x - 3, top, w + 6, max(6, w // 5), roof_col)


def pillar(x: int, y: int, h: int, col: int = VERMILION, dark: int = LACQUER) -> None:
    C.rect(x, y - h, 3, h, col)
    C.line(x + 2, y - h, x + 2, y - 1, dark)
    C.rect(x - 1, y - 2, 5, 2, STONE)


def paifang(x: int, y: int, w: int, h: int, col: int = STONE, dark: int = PLUM, roof_col: int = INK, plaque: int = LACQUER) -> tuple[int, int, int, int]:
    """A memorial archway. Returns the plaque rectangle (for a sign overlay)."""
    for px in (x, x + w - 4):
        C.rect(px, y - h, 4, h, col)
        C.line(px + 3, y - h, px + 3, y - 1, dark)
        C.rect(px - 2, y - 4, 8, 4, col)
    C.rect(x - 2, y - h, w + 4, 4, col)
    C.rect(x - 2, y - h + 10, w + 4, 3, col)
    pw, ph = min(w - 12, 36), 9
    px0 = x + w // 2 - pw // 2
    C.rect(px0, y - h + 2, pw, ph, plaque)
    C.rectb(px0, y - h + 2, pw, ph, GOLD)
    roof(x - 6, y - h - 1, w + 12, 6, roof_col)
    return (px0, y - h + 2, pw, ph)


def gate_tower(x: int, y: int, w: int, h: int, wall_col: int = VERMILION, open_: bool = False, light: bool = False) -> tuple[int, int, int, int]:
    """A gate with an arched passage and a pavilion on top. Returns the plaque rectangle."""
    C.rect(x, y - h, w, h, wall_col)
    C.line(x, y - 1, x + w - 1, y - 1, LACQUER)
    aw, ah = w // 3, h * 2 // 3
    ax = x + w // 2 - aw // 2
    C.rect(ax, y - ah + aw // 2, aw, ah - aw // 2, INK if not light else LAMP)
    C.circ(ax + aw // 2, y - ah + aw // 2, aw // 2, INK if not light else LAMP)
    if not open_:
        C.rect(ax, y - ah + aw // 2, aw, ah - aw // 2, LACQUER)
        C.line(ax + aw // 2, y - ah + 2, ax + aw // 2, y - 1, INK)
        C.circ(ax + aw // 2, y - ah + aw // 2, aw // 2 - 1, LACQUER)
    pw = w // 2
    px0 = x + w // 2 - pw // 2
    ty = y - h - 16
    C.rect(px0 - 2, ty, pw + 4, 16, wall_col)
    for cx in range(px0, px0 + pw, 6):
        C.rect(cx, ty + 3, 3, 9, LACQUER)
    roof(px0 - 8, ty, pw + 16, 8, INK)
    C.rect(x - 2, y - h - 1, w + 4, 2, INK)
    return (x + w // 2 - 14, y - h + 3, 28, 9)


def stairs(x_bottom: int, y_bottom: int, w_bottom: int, x_top: int, y_top: int, w_top: int, col: int = STONE, edge: int = GREY, steps: int = 18) -> None:
    """A flight of stone steps rising into the distance (a trapezoid of step lines)."""
    for i in range(steps + 1):
        t = i / steps
        y = round(y_bottom + (y_top - y_bottom) * t)
        cx = x_bottom + (x_top - x_bottom) * t
        w = w_bottom + (w_top - w_bottom) * t
        nxt_y = round(y_bottom + (y_top - y_bottom) * min(1, (i + 1) / steps))
        C.rect(round(cx - w / 2), nxt_y, round(w), max(1, y - nxt_y), col)
        C.line(round(cx - w / 2), y, round(cx + w / 2), y, edge)


def railing(x0: int, x1: int, y: int, col: int = STONE, post: int = 8) -> None:
    C.line(x0, y - 5, x1, y - 5, col)
    C.line(x0, y - 2, x1, y - 2, col)
    for x in range(x0, x1 + 1, post):
        C.rect(x, y - 7, 2, 7, col)


def lantern(x: int, y: int, lit: bool = True, col: int = VERMILION) -> None:
    """A hanging red lantern; (x, y) is where it hangs."""
    C.line(x, y, x, y + 2, INK)
    C.rect(x - 2, y + 3, 5, 6, col)
    C.rect(x - 3, y + 4, 7, 4, col)
    C.line(x - 2, y + 3, x + 2, y + 3, INK)
    C.line(x - 2, y + 9, x + 2, y + 9, INK)
    if lit:
        C.pset(x, y + 5, LAMP)
        C.pset(x, y + 6, LAMP)


def glow(x: int, y: int, r: int, col: int = GOLD, core: int = LAMP) -> None:
    """Warm light around a lamp, in sparse dithered rings (draw after the night remap)."""
    C.dither(0.08)
    C.circ(x, y, r, col)
    C.dither(0.18)
    C.circ(x, y, r * 3 // 5, col)
    C.dither(0.4)
    C.circ(x, y, max(2, r // 4), core)
    C.dither(1.0)


def stele(x: int, y: int, w: int, h: int, col: int = STONE, face: int = GREY, base: int = PLUM) -> tuple[int, int, int, int]:
    """A stone tablet on a base. Returns the inscribed face rectangle."""
    C.rect(x - 3, y - 5, w + 6, 5, base)
    C.rect(x, y - 5 - h, w, h, col)
    C.rect(x + 2, y - 3 - h, w - 4, h - 4, face)
    C.elli(x, y - 9 - h, w, 8, col)
    return (x + 2, y - 3 - h, w - 4, h - 4)


def bridge_arch(x: int, y: int, w: int, h: int, col: int = STONE, dark: int = PLUM, rail: bool = True) -> None:
    """A stone arch bridge; (x, y) is the deck's left end."""
    C.rect(x, y, w, 4, col)
    C.line(x, y + 4, x + w, y + 4, dark)
    arch_w = w * 2 // 3
    ax = x + (w - arch_w) // 2
    C.rect(ax, y + 4, arch_w, h, col)
    C.elli(ax + 3, y + 7, arch_w - 6, h * 2, INK)
    if rail:
        railing(x, x + w, y, col)


def concrete_bridge(x: int, y: int, w: int, pier_h: int, col: int = GREY, dark: int = STONE, spans: int = 4) -> None:
    """A long 1950s bridge with piers; (x, y) is the deck's left end."""
    C.rect(x, y, w, 5, col)
    C.line(x, y + 5, x + w, y + 5, dark)
    for i in range(spans + 1):
        px = x + i * w // spans
        C.rect(px - 3, y + 5, 6, pier_h, col)
        C.line(px + 2, y + 5, px + 2, y + 5 + pier_h, dark)
    railing(x, x + w, y, col, 6)


def fence(x0: int, x1: int, y: int, col: int = WOOD) -> None:
    C.line(x0, y - 4, x1, y - 4, col)
    for x in range(x0, x1 + 1, 5):
        C.line(x, y - 6, x, y, col)


def banner(x: int, y: int, w: int, h: int, col: int = VERMILION) -> tuple[int, int, int, int]:
    C.line(x - 1, y - 2, x + w, y - 2, WOOD)
    C.rect(x, y, w, h, col)
    C.tri(x, y + h, x + w // 2, y + h - 3, x + w - 1, y + h, col)
    return (x, y + 1, w, h - 3)


# ---------------------------------------------------------------- modern interiors


def tiles(y: int, col: int = GREY, line: int = STONE, size: int = 12, x0: int = 0, x1: int = W) -> None:
    """A tiled floor in simple perspective."""
    C.rect(x0, y, x1 - x0, H - y, col)
    row = 0
    yy = y
    while yy < H:
        C.line(x0, yy, x1, yy, line)
        yy += 2 + row * 2
        row += 1
    cx = (x0 + x1) // 2
    for i in range(-12, 13):
        C.line(cx + i * size // 2, y, cx + i * size * 2, H, line)


def panel_wall(y0: int, y1: int, col: int = PAPER, trim: int = STONE, x0: int = 0, x1: int = W) -> None:
    C.rect(x0, y0, x1 - x0, y1 - y0, col)
    C.line(x0, y1 - 1, x1, y1 - 1, trim)
    C.line(x0, y1 - 3, x1, y1 - 3, trim)


def counter(x: int, y: int, w: int, h: int, col: int = OCHRE, top: int = PAPER, dark: int = WOOD) -> None:
    C.rect(x, y - h, w, h, col)
    C.rect(x - 1, y - h - 2, w + 2, 2, top)
    C.line(x, y - 1, x + w - 1, y - 1, dark)


def board(x: int, y: int, w: int, h: int, col: int = INK, edge: int = STONE) -> tuple[int, int, int, int]:
    """A display board (departures, menu, notices). Returns the inner rectangle."""
    C.rect(x, y, w, h, col)
    C.rectb(x, y, w, h, edge)
    return (x + 2, y + 2, w - 4, h - 4)


def building(x: int, y: int, w: int, h: int, col: int = GREY, win: int = DARK_BLUE, seed: int = 0, lit: float = 0.0) -> None:
    """A modern block with a grid of windows; (x, y) is the bottom-left."""
    C.rect(x, y - h, w, h, col)
    r = rng(seed or x)
    for wy in range(y - h + 3, y - 4, 6):
        for wx in range(x + 2, x + w - 3, 5):
            C.rect(wx, wy, 3, 3, LAMP if r.random() < lit else win)


def plant_pot(x: int, y: int, col: int = JADE) -> None:
    C.rect(x, y - 5, 6, 5, OCHRE)
    C.elli(x - 3, y - 13, 12, 9, col)


# re-exported colours used by scene modules
__all__ = [
    'BLACK', 'DUSK', 'GOLD', 'LIGHT_BLUE', 'MINT', 'NAVY', 'PEACH', 'ROSE', 'WOOD',
]

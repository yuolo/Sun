"""Visual effects: brush ink, conjured images, particles, weather."""
from __future__ import annotations

import random
from typing import Any

import pyxel

from ..art import icons
from ..art import palette as P
from ..content import lexicon
from ..core.magic import Spell
from ..engine import text
from ..engine.app import H, W
from ..engine.tasks import Future


class Effect:
    done = False

    def update(self) -> None:
        pass

    def draw(self) -> None:
        pass


class InkWrite(Effect):
    """The spell's glyphs appear one by one in glowing ink."""

    def __init__(self, spell: str, x: int, y: int) -> None:
        self.spell = spell
        self.x = max(8, min(W - 8 - len(spell) * 14, x - len(spell) * 7))
        self.y = max(4, y - 24)
        self.t = 0
        self.fut: Future = Future()
        self.total = len(spell) * 9 + 14
        self.sparks: list[list[float]] = []

    def update(self) -> None:
        self.t += 1
        n = min(len(self.spell), self.t // 9 + 1)
        if self.t % 3 == 0 and self.t < self.total - 6:
            gx = self.x + (n - 1) * 14 + 6
            self.sparks.append([gx + random.uniform(-6, 6), self.y + random.uniform(0, 12), random.uniform(-0.5, 0.5), -random.uniform(0.3, 1.0), 14])
        for s in self.sparks:
            s[0] += s[2]
            s[1] += s[3]
            s[4] -= 1
        self.sparks = [s for s in self.sparks if s[4] > 0]
        if self.t >= self.total:
            self.fut.set()
        if self.t >= self.total + 10:
            self.done = True

    def draw(self) -> None:
        n = min(len(self.spell), self.t // 9 + 1)
        fade = self.t > self.total
        for i, ch in enumerate(self.spell[:n]):
            gx, gy = self.x + i * 14, self.y
            if fade:
                pyxel.dither(max(0.1, 1 - (self.t - self.total) / 10))
            text.draw(gx, gy, ch, P.LAMP, outline=P.OCHRE)
            pyxel.dither(1.0)
        for x, y, _, _, life in self.sparks:
            pyxel.pset(x, y, P.GOLD if life > 6 else P.OCHRE)


class Fizzle(Effect):
    def __init__(self, x: int, y: int) -> None:
        self.parts = [[x + random.uniform(-8, 8), y + random.uniform(-6, 6), random.uniform(-0.3, 0.3), -random.uniform(0.2, 0.6)] for _ in range(14)]
        self.t = 0

    def update(self) -> None:
        self.t += 1
        for p in self.parts:
            p[0] += p[2]
            p[1] += p[3]
        self.done = self.t > 30

    def draw(self) -> None:
        pyxel.dither(max(0.1, 1 - self.t / 30))
        for x, y, _, _ in self.parts:
            pyxel.circ(x, y, 1 + self.t // 12, P.GREY)
        pyxel.dither(1.0)


class Apparition(Effect):
    """An image (icon or glyph) conjured by the brush: rises and fades."""

    def __init__(self, x: int, y: int, icon: str = '', glyph: str = '', count: int = 1, ghost: bool = False, scale: float = 1.0, wobble: bool = False) -> None:
        self.x, self.y = x, y
        self.icon, self.glyph = icon, glyph
        self.count = max(1, min(count, 10))
        self.ghost = ghost
        self.scale = scale
        self.wobble = wobble
        self.t = 0
        self.life = 70 if not ghost else 40

    def update(self) -> None:
        self.t += 1
        self.done = self.t >= self.life

    def draw(self) -> None:
        a = 1.0
        if self.t < 8:
            a = self.t / 8
        elif self.t > self.life - 15:
            a = (self.life - self.t) / 15
        if self.ghost:
            a *= 0.45
        pyxel.dither(max(0.05, a))
        n = self.count
        for i in range(n):
            ox = (i - (n - 1) / 2) * 18 * self.scale
            oy = -self.t * 0.25 - (i % 2) * 4
            if self.wobble:
                ox += pyxel.sin(self.t * 20 + i * 90) * 2
            x, y = self.x + ox - 8, self.y + oy - 8
            if self.icon and icons.has(self.icon):
                icons.draw(self.icon, x, y, self.scale)
            else:
                text.draw(x + 2, y + 1, self.glyph, P.LAMP, outline=P.INK)
        pyxel.dither(1.0)


class Particles(Effect):
    """Elemental bursts: fire, water, wind, rain, snow, light, flowers, cloud, stone."""

    STYLE = {
        'fire': ((P.RED, P.ORANGE, P.YELLOW), (-0.4, 0.4), (-1.4, -0.5), 0.0),
        'water': ((P.TEAL, P.MINT, P.LIGHT_BLUE), (-1.2, 1.2), (-2.0, -0.6), 0.12),
        'wind': ((P.MIST, P.WHITE), (1.5, 3.5), (-0.3, 0.3), 0.0),
        'rain': ((P.LIGHT_BLUE, P.PERIWINKLE), (-0.2, 0.2), (1.5, 2.5), 0.0),
        'snow': ((P.WHITE, P.MIST), (-0.4, 0.4), (0.3, 0.8), 0.0),
        'light': ((P.LAMP, P.YELLOW, P.WHITE), (-1.2, 1.2), (-1.2, 1.2), 0.0),
        'flower': ((P.PINK, P.ROSE, P.WHITE), (-0.8, 0.8), (-1.0, -0.2), 0.03),
        'cloud': ((P.WHITE, P.MIST), (-0.6, 0.6), (-0.3, 0.1), 0.0),
        'stone': ((P.STONE, P.GREY), (-1.0, 1.0), (-2.0, -1.0), 0.15),
        'joy': ((P.PINK, P.VERMILION), (-0.5, 0.5), (-1.0, -0.4), 0.0),
        'dark': ((P.NAVY, P.NIGHT, P.DUSK), (-1.0, 1.0), (-1.0, 1.0), 0.0),
    }

    def __init__(self, kind: str, x: int, y: int, n: int = 40, ghost: bool = False) -> None:
        cols, vx, vy, grav = self.STYLE.get(kind, self.STYLE['light'])
        self.grav = grav
        self.ghost = ghost
        self.kind = kind
        sx = -30 if kind == 'wind' else 0
        spread = 40 if kind in ('rain', 'snow') else 8
        self.parts = [
            [x + sx + random.uniform(-spread, spread), y + random.uniform(-6, 6) - (30 if kind in ('rain', 'snow') else 0),
             random.uniform(*vx), random.uniform(*vy), random.choice(cols), random.randint(25, 55)]
            for _ in range(n)
        ]
        self.t = 0

    def update(self) -> None:
        self.t += 1
        for p in self.parts:
            p[0] += p[2]
            p[1] += p[3]
            p[3] += self.grav
            p[5] -= 1
        self.parts = [p for p in self.parts if p[5] > 0]
        self.done = not self.parts

    def draw(self) -> None:
        if self.ghost:
            pyxel.dither(0.4)
        for x, y, vx, vy, col, _ in self.parts:
            if self.kind in ('wind', 'rain'):
                pyxel.line(x, y, x - vx * 2, y - vy * 2, col)
            elif self.kind in ('cloud', 'stone'):
                pyxel.circ(x, y, 2, col)
            else:
                pyxel.pset(x, y, col)
        pyxel.dither(1.0)


class Flash(Effect):
    def __init__(self, col: int = P.LAMP, frames: int = 10) -> None:
        self.col, self.frames, self.t = col, frames, 0

    def update(self) -> None:
        self.t += 1
        self.done = self.t >= self.frames

    def draw(self) -> None:
        pyxel.dither(0.5 * (1 - self.t / self.frames))
        pyxel.rect(0, 0, W, H, self.col)
        pyxel.dither(1.0)


ELEMENT_OF = {'fire': 'fire', 'water': 'water', 'wind': 'wind', 'rain': 'rain', 'snow': 'snow', 'light': 'light', 'flower': 'flower', 'cloud': 'cloud', 'stone': 'stone', 'wood': 'flower'}
VERB_ANIM = {'jump': 'jump', 'laugh': 'laugh', 'sleep': 'sleep', 'fly': 'float', 'float': 'float', 'dance': 'jump', 'cry': 'shake', 'shake': 'shake', 'walk': 'jump', 'run': 'jump', 'sing': 'laugh'}


def _glyph_tag(word: str | None, prefix: str) -> str | None:
    if not word or len(word) != 1:
        return None
    g = lexicon.get(word)
    return g.tag(prefix) if g else None


def _icon_of(word: str | None) -> str:
    if not word:
        return ''
    from ..content import spells

    e = spells.SPELLS.get(word)
    if e and e.icon:
        return e.icon
    g = lexicon.get(word) if len(word) == 1 else None
    return g.icon if g and g.icon else ''


def generic(spell: Spell, x: int, y: int, mover: Any = None) -> list[Effect]:
    """What a spell looks like when the world has no special reaction to it."""
    m = spell.meaning
    ghost = spell.power != 'full'
    if m is None:
        return [Fizzle(x, y)]
    out: list[Effect] = []
    noun = m.noun
    if m.kind == 'special':
        out.append(Particles('light', x, y, 60, ghost))
        out.append(Apparition(x, y, glyph=m.special or spell.text, ghost=ghost))
        return out
    if m.kind == 'thing' or (m.kind == 'statement' and noun and not mover):
        elem = _glyph_tag(noun, 'elem')
        if elem in ELEMENT_OF:
            n = 60 if m.adj == '大' or m.degree else 30 if m.adj == '小' else 45
            out.append(Particles(ELEMENT_OF[elem], x, y, n, ghost))
        icon = _icon_of(noun)
        if icon or not elem:
            scale = 1.5 if m.adj == '大' else 0.75 if m.adj == '小' else 1.0
            out.append(Apparition(x, y, icon=icon, glyph=noun or '', count=m.count, ghost=ghost, scale=scale, wobble=not m.mw_ok))
        if m.kind == 'statement' and m.verb:
            anim = VERB_ANIM.get(_glyph_tag(m.verb, 'verb') or '')
            if anim == 'float' and out:
                out.append(Particles('wind', x, y, 12, ghost))
        return out
    verb_tag = _glyph_tag(m.verb, 'verb')
    adj_tag = _glyph_tag(m.adj, 'adj')
    if mover is not None and not ghost:
        anim = VERB_ANIM.get(verb_tag or '')
        if anim and not m.neg:
            mover.anim, mover.anim_t = anim, 0
        if adj_tag and adj_tag.startswith('color'):
            out.append(Particles('light', x, y, 20))
    if adj_tag in ('hot',):
        out.append(Particles('fire', x, y + 10, 25, ghost))
    elif adj_tag in ('cold',):
        out.append(Particles('snow', x, y, 25, ghost))
    elif adj_tag in ('bright+', 'happy'):
        out.append(Particles('light' if adj_tag == 'bright+' else 'joy', x, y, 30, ghost))
    elif adj_tag in ('bright-',):
        out.append(Particles('dark', x, y, 30, ghost))
    if not out:
        out.append(Apparition(x, y, glyph=m.adj or m.verb or spell.text[-1], ghost=ghost))
    return out


class Weather:
    """Rain, mist and snow over the whole scene."""

    def __init__(self) -> None:
        self.rain = self.mist = self.snow = False
        self.drops: list[list[float]] = []
        self.t = 0

    def set(self, look: Any) -> None:
        self.rain, self.mist, self.snow = look.rain, look.mist, look.snow
        n = 90 if self.rain else 50 if self.snow else 0
        self.drops = [[random.uniform(0, W), random.uniform(0, H), random.uniform(0.7, 1.3)] for _ in range(n)]

    def update(self) -> None:
        self.t += 1
        for d in self.drops:
            if self.rain:
                d[0] -= 1.2 * d[2]
                d[1] += 4.5 * d[2]
            else:
                d[0] += pyxel.sin(self.t * 3 + d[1]) * 0.3
                d[1] += 0.6 * d[2]
            if d[1] > H:
                d[1] -= H
                d[0] = random.uniform(0, W + 20)
            if d[0] < -4:
                d[0] += W + 8

    def draw(self) -> None:
        if self.mist:
            for i in range(3):
                y = 60 + i * 34 + int(pyxel.sin(self.t * 0.7 + i * 50) * 4)
                x = (self.t // (3 + i)) % 64
                pyxel.dither(0.18)
                for k in range(-1, W // 64 + 2):
                    pyxel.elli(k * 64 - x, y, 70, 18, P.MIST)
                pyxel.dither(1.0)
        for x, y, s in self.drops:
            if self.rain:
                pyxel.line(x, y, x + 1, y - 3, P.PERIWINKLE if s > 1 else P.LIGHT_BLUE)
            else:
                pyxel.pset(x, y, P.WHITE)


# ---------------------------------------------------------------- story events


class Fade(Effect):
    """Darkens the screen and lets it go again (sleep, nightfall)."""

    def __init__(self, col: int = P.NIGHT, frames: int = 60, peak: float = 0.85) -> None:
        self.col, self.frames, self.peak, self.t = col, frames, peak, 0

    def update(self) -> None:
        self.t += 1
        self.done = self.t >= self.frames

    def draw(self) -> None:
        half = self.frames / 2
        a = self.peak * (self.t / half if self.t < half else (self.frames - self.t) / half)
        pyxel.dither(max(0.0, min(1.0, a)))
        pyxel.rect(0, 0, W, H, self.col)
        pyxel.dither(1.0)


class DragonFlight(Effect):
    """The painted dragon leaves the wall and flies west, dragging the clouds along."""

    def __init__(self, x: int, y: int, frames: int = 100, cover: tuple[int, int, int, int] | None = None, wall: int = P.LACQUER) -> None:
        self.x0, self.y0, self.frames, self.t = x, y, frames, 0
        self.cover, self.wall = cover, wall

    def update(self) -> None:
        self.t += 1
        self.done = self.t >= self.frames

    def draw(self) -> None:
        if self.cover:
            # the wall where the painting was
            pyxel.rect(*self.cover, self.wall)
        k = self.t / self.frames
        hx = self.x0 - k * (self.x0 + 60)
        hy = self.y0 - k * 70 - pyxel.sin(self.t * 6) * 6
        for i in range(16):
            x = hx + i * 5
            y = hy + pyxel.sin(self.t * 12 + i * 40) * 4 + i * 1.5 * k
            pyxel.circ(x, y, 3, P.JADE)
        pyxel.circ(hx - 3, hy, 5, P.JADE)
        pyxel.pset(hx - 5, hy - 1, P.INK)
        pyxel.pset(hx - 2, hy - 1, P.INK)
        pyxel.dither(0.5)
        for i in range(5):
            pyxel.elli(hx + 60 + i * 18, hy - 4 + (i % 2) * 6, 26, 10, P.MIST)
        pyxel.dither(1.0)


class CloudsPart(Effect):
    """Clouds slide apart from the middle of the eastern sky."""

    def __init__(self, cx: int, y: int, frames: int = 80) -> None:
        self.cx, self.y, self.frames, self.t = cx, y, frames, 0

    def update(self) -> None:
        self.t += 1
        self.done = self.t >= self.frames

    def draw(self) -> None:
        k = self.t / self.frames
        for i in range(4):
            off = 10 + k * (60 + i * 25)
            y = self.y + i * 8
            pyxel.elli(self.cx - off - 50, y, 50, 14, P.STONE)
            pyxel.elli(self.cx + off, y, 50, 14, P.STONE)
        pyxel.dither(k)
        pyxel.rect(self.cx - 40, self.y + 26, 80, 3, P.ORANGE)
        pyxel.dither(1.0)


class SunRise(Effect):
    """The sun comes up over the sea of clouds."""

    def __init__(self, x: int, y_from: int, y_to: int, frames: int = 150) -> None:
        self.x, self.y0, self.y1, self.frames, self.t = x, y_from, y_to, frames, 0

    def update(self) -> None:
        self.t += 1
        self.done = self.t >= self.frames

    def draw(self) -> None:
        k = min(1.0, self.t / (self.frames * 0.8))
        y = self.y0 + (self.y1 - self.y0) * k
        pyxel.dither(0.25 * k)
        pyxel.circ(self.x, y, 40, P.YELLOW)
        pyxel.dither(0.5 * k)
        pyxel.circ(self.x, y, 24, P.LAMP)
        pyxel.dither(1.0)
        pyxel.clip(0, 0, W, self.y0 + 2)
        pyxel.circ(self.x, y, 14, P.ORANGE if k < 0.6 else P.YELLOW)
        pyxel.circ(self.x, y, 11, P.LAMP)
        pyxel.clip()
        if self.t > self.frames * 0.8:
            f = (self.t - self.frames * 0.8) / (self.frames * 0.2)
            pyxel.dither(0.6 * (1 - f))
            pyxel.rect(0, 0, W, H, P.LAMP)
            pyxel.dither(1.0)

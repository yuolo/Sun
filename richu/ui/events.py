"""Scene events: sunsets, opening gates, clouds parting… registered by the content."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from ..engine.app import APP

EVENTS: dict[str, Callable[[Any], Awaitable[None]]] = {}


def event(name: str) -> Callable[[Callable[[Any], Awaitable[None]]], Callable[[Any], Awaitable[None]]]:
    def deco(fn: Callable[[Any], Awaitable[None]]) -> Callable[[Any], Awaitable[None]]:
        EVENTS[name] = fn
        return fn

    return deco


async def run_event(view: Any, name: str) -> None:
    fn = EVENTS.get(name)
    if fn is None:
        view.bg_dirty = True
        await APP.sched.sleep(15)
        return
    await fn(view)


# ---------------------------------------------------------------- the story's events


def _hotspot_center(view: Any, hid: str, default: tuple[int, int] = (160, 90)) -> tuple[int, int]:
    for h in view.scene.hotspots if view.scene else ():
        if h.id == hid:
            x, y, w, hh = h.rect
            return x + w // 2, y + hh // 2
    return default


async def _play(view: Any, *effects: Any, frames: int = 30) -> None:
    view.effects.extend(effects)
    await APP.sched.sleep(frames)


@event('brush_awake')
async def _(view: Any) -> None:
    from . import audio, fx

    audio.sfx('magic')
    x, y = int(view.player.x), int(view.player.y) - 16
    await _play(view, fx.Flash(fx.P.LAMP, 14), fx.Particles('light', x, y, 60), frames=40)


@event('fire_lit')
async def _(view: Any) -> None:
    from . import audio, fx

    audio.sfx('fire')
    x, y = _hotspot_center(view, 'stove')
    view.bg_dirty = True
    await _play(view, fx.Flash(fx.P.ORANGE, 8), fx.Particles('fire', x, y, 70), frames=36)


@event('gate_open')
async def _(view: Any) -> None:
    from . import audio, fx

    audio.sfx('gate')
    view.bg_dirty = True
    await _play(view, fx.Flash(fx.P.YELLOW, 12), frames=24)


@event('stream_low')
async def _(view: Any) -> None:
    from . import fx

    x, y = _hotspot_center(view, 'stream')
    view.bg_dirty = True
    await _play(view, fx.Particles('water', x, y, 50), frames=36)


@event('wind')
async def _(view: Any) -> None:
    from . import audio, fx

    audio.sfx('wind')
    view.bg_dirty = True
    await _play(view, fx.Particles('wind', 40, 70, 60), fx.Particles('wind', 60, 120, 60), frames=45)


@event('rain_stop')
async def _(view: Any) -> None:
    from . import fx

    view.bg_dirty = True
    await _play(view, fx.Flash(fx.P.WHITE, 12), frames=20)


@event('night')
async def _(view: Any) -> None:
    from . import audio, fx

    audio.sfx('bell')
    fade = fx.Fade(fx.P.NIGHT, 70, 0.9)
    view.effects.append(fade)
    await APP.sched.sleep(35)
    view.bg_dirty = True
    await APP.sched.sleep(35)


@event('sleep')
async def _(view: Any) -> None:
    from . import fx

    fade = fx.Fade(fx.P.NIGHT, 90, 1.0)
    view.effects.append(fade)
    await APP.sched.sleep(90)


@event('dragon')
async def _(view: Any) -> None:
    from . import audio, fx

    audio.sfx('magic')
    x, y = _hotspot_center(view, 'dragon', (124, 92))
    rect = next((h.rect for h in view.scene.hotspots if h.id == 'dragon'), None) if view.scene else None
    await _play(view, fx.DragonFlight(x - 40, y, cover=rect), frames=100)


@event('clouds_open')
async def _(view: Any) -> None:
    from . import audio, fx

    audio.sfx('wind')
    await _play(view, fx.Particles('wind', 180, 80, 70), fx.CloudsPart(250, 70), frames=80)


@event('sunrise')
async def _(view: Any) -> None:
    from . import audio, fx

    audio.music('sunrise')
    await _play(view, fx.SunRise(250, 112, 92), frames=150)

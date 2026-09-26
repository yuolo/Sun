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

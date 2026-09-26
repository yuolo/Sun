"""Helpers shared by chapter scripts."""
from __future__ import annotations

from typing import Any

from ...art import palette as P
from ...core.phrases import normalize
from ...core.types import FigureSpec, ScriptContext


async def cycle(c: ScriptContext, key: str, actor: str, lines: list[str]) -> None:
    """Says the next line of a list on each click."""
    n = int(c.flag(key) or 0)
    await c.say(actor, lines[n % len(lines)])
    c.set(key, n + 1)


def yes(answer: str) -> bool:
    """«Yes» in Chinese is said by repeating the verb (是, 要, 有, 会, 对, 好)."""
    a = normalize(answer)
    return bool(a) and not a.startswith(('不', '没')) and (a[0] in '是要有会对好去' or a in ('是的', '对'))


def no(answer: str) -> bool:
    a = normalize(answer)
    return a.startswith(('不', '没'))


def said(answer: str, *options: str) -> bool:
    a = normalize(answer)
    return any(normalize(o) == a for o in options)


def has_all(answer: str, glyphs: str) -> bool:
    a = normalize(answer)
    return all(g in a for g in glyphs)


async def pay(c: ScriptContext, actor: str, price: int, item: str) -> bool:
    """The player hands over money (the 钱 item). Returns True if there was enough."""
    if item != 'money':
        return False
    if c.state.coins < price:
        await c.say(actor, '钱不够。')
        return False
    c.add_coins(-price)
    return True


def fig(coat: int, trim: int | None = None, style: str = 'jacket', hat: str = 'short', **kw: Any) -> FigureSpec:
    return FigureSpec(coat, trim, style, hat, **kw)


# frequently used people
OFFICER = fig(P.NAVY, P.GOLD, 'uniform', 'police')
STAFF = fig(P.DARK_BLUE, P.WHITE, 'uniform', 'bun', hair=P.INK)

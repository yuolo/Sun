"""Rules of the puzzles, without any drawing."""
from __future__ import annotations

from dataclasses import dataclass

# ---------------------------------------------------------------- tea tray


@dataclass(frozen=True)
class Cup:
    drink: str  # 茶 · 水 · 汤 …
    size: str  # 大 · 小
    vessel: str = '杯'  # 杯 · 碗


@dataclass(frozen=True)
class Order:
    drink: str
    count: int
    size: str | None = None
    vessel: str | None = None


MAX_TRAY = 4


def check_order(cups: list[Cup], order: Order) -> str | None:
    """None if the tray matches the order, otherwise what is wrong: empty · drink · vessel · count · size."""
    if not cups:
        return 'empty'
    if any(c.drink != order.drink for c in cups):
        return 'drink'
    if order.vessel and any(c.vessel != order.vessel for c in cups):
        return 'vessel'
    if len(cups) != order.count:
        return 'count'
    if order.size and any(c.size != order.size for c in cups):
        return 'size'
    return None


# ---------------------------------------------------------------- bells


def ring(progress: int, glyph: str, chant: str) -> tuple[int, str]:
    """Returns (new progress, result: progress · restart · wrong · solved)."""
    if glyph == chant[progress]:
        nxt = progress + 1
        return nxt, 'solved' if nxt >= len(chant) else 'progress'
    if glyph == chant[0]:
        return 1, 'restart'
    return 0, 'wrong'


# ---------------------------------------------------------------- building characters


@dataclass(frozen=True)
class Recipe:
    a: str
    b: str
    layout: str  # lr · tb · repeat3
    result: str


def compose(recipes: list[Recipe], a: str, b: str, layout: str) -> str | None:
    for r in recipes:
        if r.a == a and r.b == b and r.layout == layout:
            return r.result
    return None


# ---------------------------------------------------------------- bargaining


@dataclass
class Haggle:
    """A seller who starts high and gives in slowly."""

    asking: int
    floor: int
    step: int = 1
    rounds: int = 0

    def offer(self, price: int) -> str:
        """high (more than asked) · deal · low (below the floor: 太少了) · counter (the seller comes down a step)."""
        self.rounds += 1
        if price > self.asking:
            return 'high'
        if price == self.asking:
            return 'deal'
        if price < self.floor:
            return 'low'
        self.asking = max(price, self.floor, self.asking - self.step)
        return 'deal' if self.asking == price else 'counter'


# ---------------------------------------------------------------- shopping lists and budgets


def check_list(wanted: dict[str, int], packed: dict[str, int]) -> list[str]:
    """Items whose count differs (empty list = exactly right)."""
    keys = set(wanted) | {k for k, v in packed.items() if v}
    return sorted(k for k in keys if wanted.get(k, 0) != packed.get(k, 0))


def total(prices: dict[str, int], order: dict[str, int]) -> int:
    return sum(prices[k] * n for k, n in order.items())


def within_budget(prices: dict[str, int], order: dict[str, int], budget: int, must: set[str] | None = None) -> bool:
    if must and not all(order.get(k) for k in must):
        return False
    return 0 < total(prices, order) <= budget


# ---------------------------------------------------------------- matching by description


@dataclass(frozen=True)
class Thing:
    id: str
    traits: frozenset[str]  # e.g. {'红', '小', '伞'}


def matches(description: frozenset[str], thing: Thing) -> bool:
    return description <= thing.traits


def match_all(descriptions: dict[str, frozenset[str]], things: list[Thing], pairs: dict[str, str]) -> bool:
    """pairs: owner → thing id. True if every owner got the thing matching the description."""
    by_id = {t.id: t for t in things}
    return all(o in pairs and pairs[o] in by_id and matches(d, by_id[pairs[o]]) for o, d in descriptions.items())


# ---------------------------------------------------------------- directions in the fog


def walk(route: list[str], choices: list[str]) -> tuple[int, bool]:
    """How far the player got following a route (左/右/上…), and whether they arrived."""
    for i, c in enumerate(choices):
        if i >= len(route) or c != route[i]:
            return i, False
    return len(choices), len(choices) >= len(route)


# ---------------------------------------------------------------- couplets


def couplet_ok(upper: str, lower: str, pairs: dict[str, str]) -> bool:
    """Every glyph of the lower line mirrors the upper one (天↔地, 日↔月…)."""
    if len(upper) != len(lower):
        return False
    mirror = {**pairs, **{b: a for a, b in pairs.items()}}
    return all(mirror.get(u) == l for u, l in zip(upper, lower))


# ---------------------------------------------------------------- ancient forms


def check_ancient(pairs: dict[str, str | None], glyphs: str) -> bool:
    return all(pairs.get(g) == g for g in glyphs)

"""Items: named in hanzi, drawn as 16×16 icons."""
from __future__ import annotations

from ..core.types import ItemDef

ITEMS: dict[str, ItemDef] = {}


def add(*items: ItemDef) -> None:
    for it in items:
        if it.id in ITEMS:
            raise ValueError(f'duplicate item {it.id}')
        ITEMS[it.id] = it


def item(id: str) -> ItemDef:
    return ITEMS[id]

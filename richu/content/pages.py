"""Journal confirmation pages (filled chapter by chapter)."""
from __future__ import annotations

from ..core.types import PageDef

PAGES: list[PageDef] = []
BY_ID: dict[str, PageDef] = {}


def add(*pages: PageDef) -> None:
    for p in pages:
        if p.id in BY_ID:
            raise ValueError(f'duplicate page {p.id}')
        PAGES.append(p)
        BY_ID[p.id] = p


def page(id: str) -> PageDef:
    return BY_ID[id]

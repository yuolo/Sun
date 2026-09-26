"""Compounds and idioms with their own magic (filled chapter by chapter)."""
from __future__ import annotations

from ..core.magic import SpellEntry

SPELLS: dict[str, SpellEntry] = {}


def add(*entries: SpellEntry) -> None:
    for e in entries:
        if e.zh in SPELLS:
            raise ValueError(f'duplicate spell {e.zh}')
        SPELLS[e.zh] = e

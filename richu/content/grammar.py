"""Grammar notes, unlocked when their glyphs are confirmed."""
from __future__ import annotations

from ..core.types import GrammarDef

GRAMMAR: list[GrammarDef] = []


def add(*notes: GrammarDef) -> None:
    GRAMMAR.extend(notes)

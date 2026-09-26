"""Texts to read: grandfather's diary, letters, steles, legends."""
from __future__ import annotations

from ...core.types import TextDef

TEXTS: dict[str, TextDef] = {}


def add(*texts: TextDef) -> None:
    for t in texts:
        if t.id in TEXTS:
            raise ValueError(f'duplicate text {t.id}')
        TEXTS[t.id] = t


def text(id: str) -> TextDef:
    return TEXTS[id]

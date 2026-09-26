"""Compact constructor for lexicon entries."""
from __future__ import annotations

from ...core.types import GlyphDef


def G(
    ch: str,
    pinyin: str,
    meaning: str,
    chapter: int,
    pos: str,
    field: str,
    origin: str = '',
    words: list[tuple[str, str, str]] | None = None,
    icon: str = '',
    magic: str = '',
) -> GlyphDef:
    return GlyphDef(ch, pinyin, meaning, chapter, pos, field, origin, tuple(words or ()), icon, magic)

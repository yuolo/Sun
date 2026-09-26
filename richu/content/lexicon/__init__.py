"""The lexicon: every hanzi the player can meet (~350).

Entries live in one module per chapter (ch0 = prologue … ch6) and are
written by hand: pinyin, Russian meaning, part of speech, semantic field,
origin, living words, icon and magic tags.
"""
from __future__ import annotations

from ...core.types import GlyphDef
from . import ch0, ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8

LEXICON: dict[str, GlyphDef] = {}
for _mod in (ch0, ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8):
    for _g in _mod.GLYPHS:
        if _g.ch in LEXICON:
            raise ValueError(f'duplicate lexicon entry {_g.ch}')
        LEXICON[_g.ch] = _g


def get(ch: str) -> GlyphDef | None:
    return LEXICON.get(ch)


def known(ch: str) -> bool:
    return ch in LEXICON

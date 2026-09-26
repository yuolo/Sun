"""Russian glosses for HSK words (shown once all their glyphs are confirmed)."""
from __future__ import annotations

GLOSSES: dict[str, str] = {}


def add(table: str) -> None:
    """Lines of «word — gloss»."""
    for line in table.strip().splitlines():
        if '—' in line:
            w, g = line.split('—', 1)
            GLOSSES[w.strip()] = g.strip()


def gloss(word: str) -> str:
    if word in GLOSSES:
        return GLOSSES[word]
    from . import lexicon

    if len(word) == 1 and lexicon.get(word):
        return lexicon.get(word).meaning  # type: ignore[union-attr]
    return ''

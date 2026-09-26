"""Hanzi in strings: splitting, normalising answers."""
from __future__ import annotations


def is_han(ch: str) -> bool:
    o = ord(ch)
    return 0x3400 <= o <= 0x9FFF or 0xF900 <= o <= 0xFAFF


def glyphs_of(text: str) -> list[str]:
    """Unique hanzi of a text, in order of appearance."""
    out: list[str] = []
    for ch in text:
        if is_han(ch) and ch not in out:
            out.append(ch)
    return out


def normalize(text: str) -> str:
    """Only hanzi matter in answers: punctuation and spaces are dropped."""
    return ''.join(ch for ch in text if is_han(ch))


def matches(answer: str, *accepted: str) -> bool:
    a = normalize(answer)
    return any(normalize(x) == a for x in accepted)


def contains(answer: str, glyph: str) -> bool:
    return glyph in normalize(answer)

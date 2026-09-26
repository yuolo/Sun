"""Talismans: inscriptions that already act on the world.

The player edits one with the brush — removes a glyph, writes another over
it, or swaps two — and the world follows the new text. Writing a glyph
needs understanding (a confirmed glyph); removing and swapping do not.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .state import GameState


@dataclass(frozen=True)
class TalismanDef:
    id: str
    text: str
    #: final text → outcome id (the scene script reacts to the outcome)
    outcomes: dict[str, str] = field(default_factory=dict)
    #: the longest text allowed
    max_len: int = 6


def current(s: GameState, t: TalismanDef) -> str:
    v = s.flags.get(f'tal:{t.id}')
    return v if isinstance(v, str) else t.text


def outcome(s: GameState, t: TalismanDef) -> str | None:
    return t.outcomes.get(current(s, t))


def remove(text: str, i: int) -> str:
    if 0 <= i < len(text) and len(text) > 1:
        return text[:i] + text[i + 1 :]
    return text


def replace(text: str, i: int, glyph: str) -> str:
    if 0 <= i < len(text):
        return text[:i] + glyph + text[i + 1 :]
    return text


def insert(text: str, i: int, glyph: str, max_len: int = 6) -> str:
    if 0 <= i <= len(text) and len(text) < max_len:
        return text[:i] + glyph + text[i:]
    return text


def swap(text: str, i: int, j: int) -> str:
    if 0 <= i < len(text) and 0 <= j < len(text) and i != j:
        chars = list(text)
        chars[i], chars[j] = chars[j], chars[i]
        return ''.join(chars)
    return text


def apply(s: GameState, t: TalismanDef, new_text: str) -> str | None:
    """Stores the edited text; returns the outcome it produces (or None)."""
    s.flags[f'tal:{t.id}'] = new_text
    return t.outcomes.get(new_text)


def reset(s: GameState, t: TalismanDef) -> None:
    s.flags.pop(f'tal:{t.id}', None)

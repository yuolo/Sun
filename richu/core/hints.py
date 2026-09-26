"""Hints: story hints first, then a nudge about open journal pages."""
from __future__ import annotations

from ..content import hints as H
from . import journal
from .state import GameState


def current(s: GameState) -> str:
    for when, text in H.HINTS:
        try:
            if when(s):
                return text
        except (KeyError, AttributeError):
            continue
    if journal.open_pages(s):
        return H.PAGE_HINT
    return H.DEFAULT_HINT

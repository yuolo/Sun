"""Hints: the first matching rule wins (filled chapter by chapter)."""
from __future__ import annotations

from collections.abc import Callable

from ..core.state import GameState

HINTS: list[tuple[Callable[[GameState], bool], str]] = []
PAGE_HINT = 'В дневнике ждёт страница: все её знаки уже встречались. Откройте «Страницы» и разложите знаки по картинкам.'
DEFAULT_HINT = 'Поговорите со всеми, осмотритесь, откройте дневник. Знаки становятся понятнее от повторения.'


def add(when: Callable[[GameState], bool], text: str) -> None:
    HINTS.append((when, text))

"""Review mode: multiple-choice questions over confirmed glyphs."""
from __future__ import annotations

import random
from dataclasses import dataclass

MIN_REVIEW = 4


@dataclass
class Question:
    mode: str  # glyph→meaning · meaning→glyph
    glyph: str
    options: list[str]


def make_question(pool: list[str], rng: random.Random | None = None, previous: str | None = None) -> Question | None:
    if len(pool) < MIN_REVIEW:
        return None
    rng = rng or random.Random()
    candidates = [g for g in pool if g != previous] or list(pool)
    glyph = rng.choice(candidates)
    others = [g for g in pool if g != glyph]
    options = [glyph] + rng.sample(others, 3)
    rng.shuffle(options)
    return Question(rng.choice(['glyph→meaning', 'meaning→glyph']), glyph, options)

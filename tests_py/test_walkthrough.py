"""The whole game played through the scene API, as a careful player would."""
from __future__ import annotations

import pytest

from richu import platform
from richu.content import pages as PG
from richu.content.world import load
from richu.core import journal
from richu.core.headless import HeadlessGame
from richu.devtools.playthrough import play_chapter1, play_chapter2, play_prologue, solve_open_pages

platform.use_memory_storage()
load()


def test_prologue_and_chapter1():
    g = HeadlessGame()
    play_prologue(g)
    play_chapter1(g)
    solved = solve_open_pages(g, 1)
    missing = [p.id for p in PG.PAGES if p.chapter == 1 and p.id not in solved]
    assert not missing, f'pages still closed after chapter 1: {missing}'
    assert sum(1 for v in g.state.confirmed.values() if v) >= 90


def test_chapter2_the_city():
    g = HeadlessGame()
    play_prologue(g)
    play_chapter1(g)
    solve_open_pages(g, 1)
    play_chapter2(g)
    solved = solve_open_pages(g, 2)
    missing = [(p.id, [c for c in journal.page_chars(p) if c not in g.state.seen]) for p in PG.PAGES if p.chapter == 2 and p.id not in solved]
    assert not missing, f'pages still closed after chapter 2: {missing}'


def test_every_line_uses_known_glyphs():
    """Every hanzi the player can meet is in the lexicon (checked on a full run's log)."""
    from richu.content import lexicon
    from richu.core.phrases import is_han

    from richu.devtools.playthrough import play_chapter3

    g = HeadlessGame()
    play_prologue(g)
    play_chapter1(g)
    solve_open_pages(g, 1)
    play_chapter2(g, sleep=True)
    solve_open_pages(g, 2)
    play_chapter3(g)
    unknown = sorted({ch for line in g.state.log for ch in line.text if is_han(ch) and not lexicon.known(ch)})
    assert not unknown, f'glyphs missing from the lexicon: {"".join(unknown)}'


@pytest.mark.parametrize('answers', [('你好', '是'), ('护照', '我是俄罗斯人'), ('俄罗斯人',)])
def test_officer_waits_for_a_real_answer(answers):
    g = HeadlessGame()
    play_prologue(g)
    g.talk('officer')
    g.answer(*answers)
    g.use('passport', 'officer')
    assert g.state.on('passport_ok') and not g.c.answers


def test_chapter3_the_village():
    from richu.devtools.playthrough import play_chapter3

    g = HeadlessGame()
    play_prologue(g)
    play_chapter1(g)
    solve_open_pages(g, 1)
    play_chapter2(g, sleep=True)
    solve_open_pages(g, 2)
    play_chapter3(g)
    solved = solve_open_pages(g, 3)
    missing = [(p.id, [c for c in journal.page_chars(p) if c not in g.state.seen]) for p in PG.PAGES
               if p.chapter == 3 and p.id not in solved and p.id != 'elements']
    assert not missing, f'pages still closed after chapter 3: {missing}'

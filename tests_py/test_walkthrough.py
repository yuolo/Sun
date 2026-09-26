"""The whole game played through the scene API, as a careful player would."""
from __future__ import annotations

import pytest

from richu import platform
from richu.content import pages as PG
from richu.content.world import load
from richu.core import journal
from richu.content import lexicon
from richu.core.headless import HeadlessGame
from richu.core.phrases import is_han
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


def test_chapter4_the_red_gate():
    from richu.devtools.playthrough import play_chapter3, play_chapter4

    g = HeadlessGame()
    play_prologue(g)
    play_chapter1(g)
    solve_open_pages(g, 1)
    play_chapter2(g, sleep=True)
    solve_open_pages(g, 2)
    play_chapter3(g, climb=True)
    solve_open_pages(g, 3)
    play_chapter4(g)
    solved = solve_open_pages(g, 4)
    missing = [(p.id, [c for c in journal.page_chars(p) if c not in g.state.seen]) for p in PG.PAGES
               if p.chapter == 4 and p.id not in solved]
    assert not missing, f'pages still closed after chapter 4: {missing}'
    unknown = sorted({ch for line in g.state.log for ch in line.text if is_han(ch) and not lexicon.known(ch)})
    assert not unknown, f'glyphs missing from the lexicon: {"".join(unknown)}'


def test_chapter5_zhongtianmen():
    from richu.devtools.playthrough import play_chapter3, play_chapter4, play_chapter5

    g = HeadlessGame()
    play_prologue(g)
    play_chapter1(g)
    solve_open_pages(g, 1)
    play_chapter2(g, sleep=True)
    solve_open_pages(g, 2)
    play_chapter3(g, climb=True)
    solve_open_pages(g, 3)
    play_chapter4(g, climb=True)
    solve_open_pages(g, 4)
    play_chapter5(g)
    solved = solve_open_pages(g, 5)
    missing = [(p.id, [c for c in journal.page_chars(p) if c not in g.state.seen]) for p in PG.PAGES
               if p.chapter == 5 and p.id not in solved]
    assert not missing, f'pages still closed after chapter 5: {missing}'
    unknown = sorted({ch for line in g.state.log for ch in line.text if is_han(ch) and not lexicon.known(ch)})
    assert not unknown, f'glyphs missing from the lexicon: {"".join(unknown)}'


def play_to(chapter: int) -> HeadlessGame:
    """A full run up to the start of ``chapter``, with every open page solved."""
    from richu.devtools import playthrough as pt

    g = HeadlessGame()
    pt.play_prologue(g)
    steps = [pt.play_chapter1, pt.play_chapter2, pt.play_chapter3, pt.play_chapter4, pt.play_chapter5, pt.play_chapter6,
             pt.play_chapter7, pt.play_chapter8]
    for n, play in enumerate(steps[: chapter - 1], start=1):
        if n == 1:
            play(g)
        elif n == 2:
            play(g, sleep=True)
        else:
            play(g, climb=True)
        pt.solve_open_pages(g, n)
    return g


def test_chapter6_the_night_climb():
    from richu.devtools.playthrough import play_chapter6

    g = play_to(6)
    play_chapter6(g)
    solved = solve_open_pages(g, 6)
    missing = [(p.id, [c for c in journal.page_chars(p) if c not in g.state.seen]) for p in PG.PAGES
               if p.chapter == 6 and p.id not in solved]
    assert not missing, f'pages still closed after chapter 6: {missing}'
    unknown = sorted({ch for line in g.state.log for ch in line.text if is_han(ch) and not lexicon.known(ch)})
    assert not unknown, f'glyphs missing from the lexicon: {"".join(unknown)}'


def test_chapter7_the_summit_at_night():
    from richu.devtools.playthrough import play_chapter7

    g = play_to(7)
    play_chapter7(g)
    solved = solve_open_pages(g, 7)
    missing = [(p.id, [c for c in journal.page_chars(p) if c not in g.state.seen]) for p in PG.PAGES
               if p.chapter == 7 and p.id not in solved and p.id != 'dragon']
    assert not missing, f'pages still closed after chapter 7: {missing}'
    unknown = sorted({ch for line in g.state.log for ch in line.text if is_han(ch) and not lexicon.known(ch)})
    assert not unknown, f'glyphs missing from the lexicon: {"".join(unknown)}'


def test_chapter8_the_sunrise_and_the_whole_game():
    from richu.content import hsk
    from richu.devtools.playthrough import play_chapter8

    g = play_to(8)
    play_chapter8(g)
    solved = solve_open_pages(g, 8)
    missing = [(p.id, [c for c in journal.page_chars(p) if c not in g.state.seen]) for p in PG.PAGES
               if p.chapter == 8 and p.id not in solved and journal.page_status(g.state, p) != 'done']
    assert not missing, f'pages still closed after chapter 8: {missing}'
    unknown = sorted({ch for line in g.state.log for ch in line.text if is_han(ch) and not lexicon.known(ch)})
    assert not unknown, f'glyphs missing from the lexicon: {"".join(unknown)}'
    # every page of the game can be opened on the way
    closed = [p.id for p in PG.PAGES if journal.page_status(g.state, p) != 'done']
    assert not closed, f'pages never solved in a full run: {closed}'
    # the story teaches the whole of HSK 1-3: every word is met in a full run
    for t in g.state.texts:
        g.read(t)
    seen_text = ''.join(line.text for line in g.state.log)
    from richu.content.texts import text as text_of

    seen_text += ''.join(text_of(t).zh for t in g.state.texts)
    unmet = [w for w in hsk.WORDS if w not in seen_text]
    assert not unmet, f'HSK words never met in a full run ({len(unmet)}): {" ".join(unmet)}'

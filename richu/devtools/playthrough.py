"""Scripted playthroughs used by tests and by the screenshot tool."""
from __future__ import annotations

from ..content import pages as PG
from ..core import journal
from ..core.headless import HeadlessGame


def solve_open_pages(g: HeadlessGame, chapter: int) -> list[str]:
    done = []
    for p in PG.PAGES:
        if p.chapter == chapter and journal.page_status(g.state, p) == 'open':
            g.solve_page(p.id)
            done.append(p.id)
    return done


def play_prologue(g: HeadlessGame) -> None:
    g.start('0a', 'start')
    assert g.state.chapter == 0
    g.click('box')
    assert all(it in g.state.inventory for it in ('letter', 'diary', 'photo', 'brush'))
    assert 'envelope' in g.state.texts
    assert g.exit('door')
    assert g.state.scene == '1a'


def play_chapter1(g: HeadlessGame) -> None:
    s = g.state
    assert s.chapter == 1 and s.coins == 200
    g.talk('officer')
    g.answer('是')
    assert g.use('passport', 'officer')
    assert s.on('passport_ok')
    g.click('black')
    assert s.on('black_taken')
    g.click('red')
    assert 'suitcase' in s.inventory
    g.talk('staff')
    assert g.exit('out') and s.scene == '1b'

    g.answer('泰山').talk('clerk')
    assert s.on('price_asked')
    assert g.use('money', 'clerk')
    assert 'ticket' in s.inventory and s.coins == 150
    g.answer('面包').talk('waitress')
    g.use('money', 'waitress')
    assert 'bread' in s.inventory
    g.answer('我是俄罗斯人').talk('kid')
    g.talk('kid')
    g.use('bread', 'kid')
    assert 'apple' in s.inventory
    assert not g.exit('platform')
    g.use('ticket', 'gatekeeper')
    assert g.exit('platform') and s.scene == '1c'

    g.click('seat8')
    assert s.on('seated')
    g.answer('我是俄罗斯人').talk('student')
    g.answer('是').talk('student')
    g.answer('小安').talk('student')
    g.talk('student')
    g.use('diary', 'student')
    assert 'diary_1' in s.texts
    for _ in range(4):
        g.talk('student')
    assert s.on('arrived')

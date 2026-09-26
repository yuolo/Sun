"""Content integrity: pages, pictures, glosses, items."""
from __future__ import annotations

from richu import platform
from richu.art import icons, pictures
from richu.content import items, lexicon, words
from richu.content import pages as PG
from richu.content.world import load

platform.use_memory_storage()
load()


def test_every_page_can_be_shown_and_explained():
    problems = []
    for p in PG.PAGES:
        if p.kind == 'phrase':
            if len(p.phrases) != len(p.glyphs):
                problems.append(f'{p.id}: {len(p.glyphs)} slots, {len(p.phrases)} phrases')
            for w, ph in zip(p.glyphs, p.phrases):
                if w not in ph:
                    problems.append(f'{p.id}: «{ph}» does not contain {w}')
        else:
            for w in p.glyphs:
                if not pictures.has(w):
                    problems.append(f'{p.id}: no picture for {w}')
        for w in p.glyphs:
            if len(w) > 1 and not words.gloss(w):
                problems.append(f'{p.id}: no gloss for {w}')
            for ch in w:
                if not lexicon.known(ch):
                    problems.append(f'{p.id}: {ch} not in the lexicon')
    assert not problems, '\n'.join(problems)


def test_page_ids_are_unique():
    ids = [p.id for p in PG.PAGES]
    assert len(ids) == len(set(ids))


def test_items_have_icons_and_known_glyphs():
    problems = []
    for it in items.ITEMS.values():
        if not icons.has(it.icon):
            problems.append(f'{it.id}: no icon {it.icon}')
        problems += [f'{it.id}: {ch} not in the lexicon' for ch in it.zh if not lexicon.known(ch)]
    assert not problems, '\n'.join(problems)


def test_grammar_notes_use_known_glyphs():
    from richu.content import grammar
    from richu.core.phrases import is_han

    problems = []
    for g in grammar.GRAMMAR:
        problems += [f'{g.id}: requires unknown {c}' for c in g.requires if not lexicon.known(c)]
        for zh, _ in g.examples:
            problems += [f'{g.id}: {c} in «{zh}» not in the lexicon' for c in zh if is_han(c) and not lexicon.known(c)]
    ids = [g.id for g in grammar.GRAMMAR]
    assert len(ids) == len(set(ids)), 'duplicate grammar ids'
    assert not problems, '\n'.join(problems)

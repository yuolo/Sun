"""Word magic: a spell is a short phrase written with the brush.

The phrase is parsed like a (very small) Chinese grammar:

* ``火`` — a thing appears (its image);
* ``三条鱼``, ``大火``, ``红花`` — things with a number or a quality;
* ``红``, ``很大``, ``不冷`` — a quality applied to the target;
* ``笑``, ``开``, ``不动`` — an action of the target;
* ``门开``, ``雨停``, ``水大``, ``门不开`` — a statement that becomes true;
* ``开门``, ``吃鱼`` — an action with an object;
* compounds and idioms from the spell table (``火山``, ``风吹云开``).

Power comes from understanding: a spell whose glyphs are all confirmed works
in full; one with glyphs that are only guessed shows a faint shadow of its
meaning and changes nothing.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from .types import GlyphDef

NOUNS = {'n', 'place', 'name', 'pron'}
NEG = {'不', '没', '别'}
DEGREE = {'很': 'very', '太': 'too', '非常': 'very', '最': 'most', '更': 'more', '真': 'very', '极': 'most'}


@dataclass(frozen=True)
class SpellEntry:
    """A compound or idiom with its own meaning (content/spells.py)."""

    zh: str
    pos: str  # n · a · v · idiom
    title: str  # Russian, shown in the spell book once understood
    effect: str = ''  # effect id for the UI
    icon: str = ''


@dataclass
class Meaning:
    kind: str  # thing · quality · action · statement · special
    noun: str | None = None  # the thing, or the subject of a statement
    adj: str | None = None
    verb: str | None = None
    obj: str | None = None
    count: int = 1
    mw: str | None = None
    mw_ok: bool = True
    neg: bool = False
    degree: str | None = None
    special: str | None = None


@dataclass
class Spell:
    text: str
    power: str  # full · shadow · fizzle
    meaning: Meaning | None = None
    reason: str = ''
    words: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.meaning is not None

    # Helpers for scene scripts ------------------------------------------------

    def is_thing(self, noun: str) -> bool:
        m = self.meaning
        return bool(m and m.kind == 'thing' and m.noun == noun)

    def acts(self, verb: str, on: str | None = None, neg: bool = False) -> bool:
        """An action (开, 开门) or a statement (门开) with this verb."""
        m = self.meaning
        if not m or m.verb != verb or m.neg != neg:
            return False
        if m.kind == 'action':
            return on is None or m.obj in (None, on)
        if m.kind == 'statement':
            return on is None or m.noun == on
        return False

    def says(self, noun: str | None = None, adj: str | None = None, verb: str | None = None, neg: bool = False) -> bool:
        """A quality or statement: 水小, 小 (on the water), 雨停, 不冷."""
        m = self.meaning
        if not m or m.neg != neg or m.kind not in ('quality', 'statement', 'action'):
            return False
        if adj is not None and m.adj != adj:
            return False
        if verb is not None and m.verb != verb:
            return False
        if noun is not None and m.kind == 'statement' and m.noun != noun:
            return False
        return adj is not None or verb is not None

    def is_special(self, key: str) -> bool:
        return bool(self.meaning and self.meaning.special == key)


Lookup = Callable[[str], GlyphDef | None]
Specials = dict[str, SpellEntry]


@dataclass
class _Word:
    text: str
    pos: str
    tags: str = ''
    special: SpellEntry | None = None


def _segment(text: str, lookup: Lookup, specials: Specials) -> list[_Word] | str:
    words: list[_Word] = []
    i = 0
    while i < len(text):
        for size in (4, 3, 2):
            chunk = text[i : i + size]
            if len(chunk) == size and chunk in specials:
                e = specials[chunk]
                words.append(_Word(chunk, e.pos, special=e))
                i += size
                break
            if len(chunk) == size and chunk in DEGREE:
                words.append(_Word(chunk, 'degree'))
                i += size
                break
        else:
            ch = text[i]
            g = lookup(ch)
            if g is None:
                return f'Знак {ch} кисть не знает.'
            pos = g.pos
            if ch in NEG:
                pos = 'neg'
            elif ch in DEGREE:
                pos = 'degree'
            words.append(_Word(ch, pos, g.magic))
            i += 1
    return words


def _mw_allowed(noun: _Word) -> set[str]:
    for t in noun.tags.split():
        if t.startswith('mw:'):
            return set(t[3:])
    return {'个'}


def parse(text: str, lookup: Lookup, specials: Specials | None = None) -> Meaning | str:
    """Returns a Meaning, or a Russian explanation of why the words don't form a spell."""
    specials = specials or {}
    if not text:
        return 'Кисть ждёт знаков.'
    if text in specials and specials[text].pos == 'idiom':
        return Meaning('special', special=text)
    seg = _segment(text, lookup, specials)
    if isinstance(seg, str):
        return seg
    words = seg

    special = next((w.special.zh for w in words if w.special), None)

    def noun_like(w: _Word) -> bool:
        return w.pos in NOUNS

    # peel modifiers
    neg = False
    degree = None
    core: list[_Word] = []
    for w in words:
        if w.pos == 'neg':
            neg = not neg
        elif w.pos == 'degree':
            degree = DEGREE.get(w.text, 'very')
        else:
            core.append(w)
    kinds = [('N' if noun_like(w) else 'V' if w.pos == 'v' else 'A' if w.pos == 'a' else 'Q' if w.pos == 'num' else 'M' if w.pos == 'm' else '?') for w in core]
    pattern = ''.join(kinds)

    if not core:
        return 'Эти знаки ничего не рисуют сами по себе — они меняют смысл других.'
    if '?' in pattern:
        odd = core[kinds.index('?')].text
        return f'Знак {odd} связывает слова, но сам ничего не делает.'

    def thing(noun: _Word, count: int = 1, mw: str | None = None, adj: str | None = None) -> Meaning:
        ok = True
        if count != 1 or mw:
            ok = mw is not None and mw in _mw_allowed(noun)
        return Meaning('thing', noun=noun.text, adj=adj, count=count, mw=mw, mw_ok=ok, neg=neg, degree=degree, special=special)

    if pattern == 'N':
        if neg:
            return 'Отрицать можно действие или свойство, а не вещь.'
        return thing(core[0])
    if pattern in ('QN', 'QMN', 'QAN', 'QMAN'):
        count = _number(core[0], lookup)
        mw = core[1].text if 'M' in pattern else None
        adj = core[-2].text if 'A' in pattern else None
        return thing(core[-1], count, mw, adj)
    if pattern in ('Q', 'QM'):
        return 'Сколько — понятно. Но чего?'
    if pattern == 'AN':
        return thing(core[1], adj=core[0].text)
    if pattern == 'A':
        return Meaning('quality', adj=core[0].text, neg=neg, degree=degree, special=special)
    if pattern == 'V':
        return Meaning('action', verb=core[0].text, neg=neg, degree=degree, special=special)
    if pattern == 'NA':
        return Meaning('statement', noun=core[0].text, adj=core[1].text, neg=neg, degree=degree, special=special)
    if pattern == 'NV':
        return Meaning('statement', noun=core[0].text, verb=core[1].text, neg=neg, special=special)
    if pattern == 'VN':
        return Meaning('action', verb=core[0].text, obj=core[1].text, neg=neg, special=special)
    if pattern == 'NVN':
        return Meaning('statement', noun=core[0].text, verb=core[1].text, obj=core[2].text, neg=neg, special=special)
    if pattern == 'NN':
        return 'Две вещи рядом — но что между ними происходит?'
    if pattern == 'AA':
        return 'Два свойства — но у чего?'
    if pattern == 'VV':
        return 'Два действия подряд — кто их делает?'
    if pattern == 'NAN':
        return 'Свойство повисло между двумя вещами.'
    return 'Знаки не сложились: кисть не понимает, как они связаны.'


def _number(w: _Word, lookup: Lookup) -> int:
    for t in w.tags.split():
        if t.startswith('num:'):
            try:
                return int(t[4:])
            except ValueError:
                pass
    return 2 if w.text == '两' else 1


def cast(text: str, confirmed: dict[str, bool], lookup: Lookup, specials: Specials | None = None) -> Spell:
    """Parses a written spell and decides its power."""
    result = parse(text, lookup, specials)
    if isinstance(result, str):
        return Spell(text, 'fizzle', None, result)
    if result.kind == 'thing' and not result.mw_ok:
        power_reason = 'Счётное слово не подходит к этой вещи — образ дрожит.'
    else:
        power_reason = ''
    full = all(confirmed.get(ch) for ch in text)
    return Spell(text, 'full' if full else 'shadow', result, power_reason)


def default_lookup(ch: str) -> GlyphDef | None:
    from ..content import lexicon

    return lexicon.get(ch)


def default_specials() -> Specials:
    from ..content import spells

    return spells.SPELLS

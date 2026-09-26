"""Types shared by the logic, the content and the UI.

Coordinates are screen pixels (320×180). Scene scripts are ``async``
functions written against :class:`ScriptContext`; the game UI and the
headless test context both implement it.
"""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from .magic import Spell
    from .state import GameState

Glyph = str
Pred = Callable[['GameState'], bool]
Num = int | Callable[['GameState'], int]
Script = Callable[['ScriptContext'], Awaitable[None]]
ItemScript = Callable[['ScriptContext', str], Awaitable[bool]]
SpellScript = Callable[['ScriptContext', 'Spell'], Awaitable[bool]]
AskScript = Callable[['ScriptContext', str], Awaitable[bool]]


# ---------------------------------------------------------------- lexicon


@dataclass(frozen=True)
class GlyphDef:
    ch: Glyph
    pinyin: str
    meaning: str
    chapter: int
    #: n noun · v verb · a adjective · num · m measure word · pron · adv · part particle · prep · conj · name
    pos: str
    #: semantic field: nature, people, body, animal, plant, food, thing, place, time, number, motion, action,
    #: speech, feeling, quality, color, direction, grammar, magic
    field: str
    origin: str = ''
    words: tuple[tuple[str, str, str], ...] = ()
    #: icon id (art/icons.py) for things that can be drawn
    icon: str = ''
    #: magic tags, space separated: elem:fire adj:size+ verb:laugh mw:long neg degree:very num:3
    magic: str = ''

    @property
    def tone(self) -> int:
        return tone_of(self.pinyin)

    def tag(self, prefix: str) -> str | None:
        for t in self.magic.split():
            if t.startswith(prefix + ':'):
                return t[len(prefix) + 1 :]
            if t == prefix:
                return ''
        return None


_TONES = {**{c: 1 for c in 'āēīōūǖ'}, **{c: 2 for c in 'áéíóúǘ'}, **{c: 3 for c in 'ǎěǐǒǔǚ'}, **{c: 4 for c in 'àèìòùǜ'}}


def tone_of(pinyin: str) -> int:
    for ch in pinyin:
        if ch in _TONES:
            return _TONES[ch]
    return 0


# ---------------------------------------------------------------- journal


@dataclass(frozen=True)
class PageDef:
    id: str
    title: str
    chapter: int
    glyphs: tuple[Glyph, ...]
    #: 'picture' — illustration per slot; 'icon' — item icons; 'phrase' — sentences with a gap
    kind: str = 'picture'
    #: phrase pages: one sentence per glyph, the gap is where the glyph goes
    phrases: tuple[str, ...] = ()


@dataclass(frozen=True)
class GrammarDef:
    id: str
    title: str
    requires: tuple[Glyph, ...]
    text: str
    examples: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class ItemDef:
    id: str
    #: the item's name in hanzi — shown instead of a Russian name
    zh: str
    icon: str
    #: what the player sees when looking at it (Russian, without naming it)
    look: str


@dataclass(frozen=True)
class TextDef:
    """Something to read: a diary entry, a letter, a stele, a legend."""

    id: str
    kind: str  # diary · letter · stone · book · sign
    title: str  # Russian title in the reader
    zh: str  # the text; lines separated by \n
    #: Russian retelling, unlocked when every glyph is confirmed
    understood: str
    chapter: int = 0
    #: diary: date line shown above the entry
    date: str = ''
    #: sketch id drawn above a diary entry
    sketch: str = ''


# ---------------------------------------------------------------- scenes


@dataclass
class FigureSpec:
    coat: int
    trim: int | None = None
    hat: str = 'none'
    hat_color: int | None = None
    hair: int | None = None
    skin: int | None = None
    prop: str = ''
    pose: str = 'stand'
    beard: bool = False
    kind: str = 'adult'  # adult · child · old
    legs: int | None = None


@dataclass
class ActorDef:
    id: str
    name: str
    figure: FigureSpec | Callable[['GameState'], FigureSpec]
    x: Num
    y: Num
    facing: str | Callable[['GameState'], str] = 'left'
    visible: Pred | None = None
    stand_at: Num | None = None
    on_talk: Script | None = None
    on_item: ItemScript | None = None
    on_spell: SpellScript | None = None
    #: the player shows a glyph from the journal (asks what it is)
    on_ask: AskScript | None = None
    #: glyphs the magic can use to point at this actor (人, 孩子…)
    tags: tuple[str, ...] = ('人',)


@dataclass
class HotspotDef:
    id: str
    name: str
    rect: tuple[int, int, int, int]
    stand_at: Num | None = None
    visible: Pred | None = None
    on_click: Script | None = None
    on_item: ItemScript | None = None
    on_spell: SpellScript | None = None
    tags: tuple[str, ...] = ()
    cursor: str = 'look'


@dataclass
class SignDef:
    id: str
    text: str  # lines separated by \n
    x: int
    y: int
    style: str = 'plaque'  # plaque · board · stone · banner · paper · tag · carved
    vertical: bool = False
    visible: Pred | None = None
    #: an editable talisman (core/talisman.py)
    talisman: str = ''
    #: clicking opens this text in the reader
    read: str = ''


@dataclass
class ExitDef:
    id: str
    to: str
    entry: str
    rect: tuple[int, int, int, int]
    dir: str  # left · right · up · down
    stand_at: int
    label: str
    visible: Pred | None = None
    guard: Callable[['ScriptContext'], Awaitable[bool]] | None = None


@dataclass
class SceneLook:
    time: str = 'day'
    rain: bool = False
    mist: bool = False
    lantern: bool = False
    snow: bool = False


@dataclass
class SceneDef:
    id: str
    chapter: int
    title: str
    #: draws the background (320×180) in daylight colours
    art: Callable[['GameState', SceneLook], None]
    look: Callable[['GameState'], SceneLook]
    path: list[tuple[int, int]]
    entries: dict[str, int]
    actors: list[ActorDef] = field(default_factory=list)
    hotspots: list[HotspotDef] = field(default_factory=list)
    signs: list[SignDef] = field(default_factory=list)
    exits: list[ExitDef] = field(default_factory=list)
    #: drawn over the actors
    front: Callable[['GameState', SceneLook], None] | None = None
    #: animated layers drawn every frame (water, fire…)
    anim: Callable[['GameState', SceneLook, int], None] | None = None
    marks: dict[str, tuple[int, int]] = field(default_factory=dict)
    on_enter: Script | None = None
    #: a spell cast into the air (no target)
    on_spell: SpellScript | None = None
    #: diary entries unlocked when the player first comes here
    diary: tuple[str, ...] = ()
    music: str = ''
    zh: str = ''


@dataclass(frozen=True)
class ChapterDef:
    n: int
    zh: str
    title: str
    subtitle: str
    start: tuple[str, str]


# ---------------------------------------------------------------- scripts


class ScriptContext(Protocol):
    state: 'GameState'

    def flag(self, name: str) -> Any: ...
    def set(self, name: str, value: Any = True) -> None: ...
    def has(self, item: str) -> bool: ...
    def give(self, item: str) -> None: ...
    def take(self, item: str) -> None: ...
    def add_coins(self, n: int) -> None: ...
    def confirm(self, glyphs: str) -> None: ...
    def unlock(self, text_id: str) -> None: ...
    def sfx(self, name: str) -> None: ...

    async def say(self, actor: str, text: str, auto: int = 0) -> None: ...
    async def talk(self, lines: list[tuple[str, str]]) -> None: ...
    async def narrate(self, text: str) -> None: ...
    async def ask(self, actor: str, question: str) -> str: ...
    async def puzzle(self, kind: str, **params: Any) -> Any: ...
    async def move(self, actor: str, x: int, y: int | None = None) -> None: ...
    async def goto(self, scene: str, entry: str) -> None: ...
    async def wait(self, ms: int) -> None: ...
    async def event(self, name: str) -> None: ...
    async def read(self, text_id: str) -> None: ...
    async def chapter(self, n: int) -> None: ...
    async def finish(self) -> None: ...

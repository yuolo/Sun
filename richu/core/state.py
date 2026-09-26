"""Game state and saving."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, fields
from typing import Any

STATE_VERSION = 2
SAVE_KEY = 'richu-save-v2'
START = ('0a', 'start')


@dataclass
class Settings:
    pinyin: bool = True
    guesses: bool = True
    voice: bool = True
    music: bool = True
    sfx: bool = True
    brush_glyphs: bool = True
    text_speed: int = 1  # 0 slow · 1 normal · 2 fast


@dataclass
class LogLine:
    who: str
    text: str
    scene: str


@dataclass
class GameState:
    v: int = STATE_VERSION
    scene: str = START[0]
    #: player position on the walk path (x), -1 = scene entry
    px: int = -1
    facing: str = 'right'
    chapter: int = 0
    #: glyph → order in which it was first met
    seen: dict[str, int] = field(default_factory=dict)
    guesses: dict[str, str] = field(default_factory=dict)
    confirmed: dict[str, bool] = field(default_factory=dict)
    pages: dict[str, bool] = field(default_factory=dict)
    placements: dict[str, list[str | None]] = field(default_factory=dict)
    inventory: list[str] = field(default_factory=list)
    coins: int = 0
    flags: dict[str, Any] = field(default_factory=dict)
    log: list[LogLine] = field(default_factory=list)
    #: texts the player can open in the reader (diary entries, letters, steles)
    texts: list[str] = field(default_factory=list)
    #: spell formulas that worked, in discovery order
    spells: list[str] = field(default_factory=list)
    #: scenes visited (for the map)
    visited: list[str] = field(default_factory=list)
    inscription: str = ''
    settings: Settings = field(default_factory=Settings)
    play_frames: int = 0
    finished: bool = False

    def flag(self, name: str) -> Any:
        return self.flags.get(name)

    def on(self, name: str) -> bool:
        return bool(self.flags.get(name))


def to_json(s: GameState) -> dict[str, Any]:
    return asdict(s)


def from_json(raw: Any) -> GameState | None:
    """Restores a saved state, filling in anything missing. Returns None for garbage."""
    if not isinstance(raw, dict) or not isinstance(raw.get('scene'), str) or raw.get('v') != STATE_VERSION:
        return None
    s = GameState()
    names = {f.name for f in fields(GameState)}
    for key, value in raw.items():
        if key not in names or key in ('settings', 'log'):
            continue
        default = getattr(s, key)
        if isinstance(default, bool):
            if isinstance(value, bool):
                setattr(s, key, value)
        elif isinstance(default, int):
            if isinstance(value, int) and not isinstance(value, bool):
                setattr(s, key, value)
        elif isinstance(default, str):
            if isinstance(value, str):
                setattr(s, key, value)
        elif isinstance(default, dict):
            if isinstance(value, dict):
                setattr(s, key, value)
        elif isinstance(default, list):
            if isinstance(value, list):
                setattr(s, key, value)
    if isinstance(raw.get('settings'), dict):
        known = {f.name for f in fields(Settings)}
        s.settings = Settings(**{k: v for k, v in raw['settings'].items() if k in known})
    if isinstance(raw.get('log'), list):
        s.log = [LogLine(**x) for x in raw['log'] if isinstance(x, dict) and set(x) == {'who', 'text', 'scene'}]
    return s


def dumps(s: GameState) -> str:
    return json.dumps(to_json(s), ensure_ascii=False, separators=(',', ':'))


def loads(raw: str | None) -> GameState | None:
    if not raw:
        return None
    try:
        return from_json(json.loads(raw))
    except (ValueError, TypeError):
        return None


def save(s: GameState) -> None:
    from .. import platform

    platform.storage_set(SAVE_KEY, dumps(s))


def load() -> GameState | None:
    from .. import platform

    return loads(platform.storage_get(SAVE_KEY))


def clear() -> None:
    from .. import platform

    platform.storage_del(SAVE_KEY)


SETTINGS_KEY = 'richu-settings-v2'


def load_settings() -> Settings:
    from .. import platform

    raw = platform.load_json(SETTINGS_KEY)
    if isinstance(raw, dict):
        known = {f.name for f in fields(Settings)}
        try:
            return Settings(**{k: v for k, v in raw.items() if k in known})
        except TypeError:
            pass
    return Settings()


def save_settings(st: Settings) -> None:
    from .. import platform

    platform.save_json(SETTINGS_KEY, asdict(st))

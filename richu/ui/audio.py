"""Music and sound effects on Pyxel's four channels.

Everything is synthesised with Pyxel's built-in tones: short pentatonic loops
for the places (channels 0–2) and small effects (channel 3). Sounds are built
on first use, after ``pyxel.init``; without an audio device every call is a
quiet no-op.
"""
from __future__ import annotations

import pyxel

_current = ''
_ready = False
enabled_music = True
enabled_sfx = True

SFX_CH = 3

# name: (notes, tones, volumes, effects, speed)
SFX: dict[str, tuple[str, str, str, str, int]] = {
    'tap': ('c3', 'p', '4', 'f', 5),
    'talk': ('g3', 't', '3', 'f', 4),
    'page': ('g3c4', 'p', '43', 'nf', 5),
    'seal': ('c2g2c3', 'p', '654', 'nnf', 7),
    'brush': ('c4a3f3d3', 'n', '3321', 'nnnf', 3),
    'wrong': ('d2c2', 's', '43', 'nf', 8),
    'item': ('c3e3g3c4', 't', '5555', 'nnnf', 5),
    'coins': ('c4e4c4g4', 'p', '4343', 'nnnf', 3),
    'bell': ('c2c2c2c2c2c2', 's', '765432', 'nnnnnf', 12),
    'magic': ('c3e3g3b3d4g4', 't', '345676', 'vvvvvf', 5),
    'fire': ('c1c1c1c1c1c1', 'n', '765432', 'nnnnnf', 6),
    'wind': ('g1a1g1f1e1d1', 'n', '234321', 'ssssss', 10),
    'gate': ('c1d1c1', 's', '654', 'ssf', 12),
    'open': ('c2e2', 's', '54', 'nf', 8),
    'stamp': ('c1', 'n', '7', 'f', 8),
    'tv': ('a3a3a3', 'p', '222', 'nnn', 4),
}

# theme: (melody, bass, drone) as (notes, tone, volume, effect, speed)
Theme = tuple[tuple[str, str, str, str], tuple[str, str, str, str], tuple[str, str, str, str], int]

THEMES: dict[str, Theme] = {
    'title': (
        ('e3 g3 a3 g3 e3 d3 c3 d3 e3 g3 a3 c4 a3 g3 e3 r', 't', '4', 'f'),
        ('c2 r g1 r a1 r e1 r c2 r g1 r f1 r g1 r', 't', '3', 'n'),
        ('c2 c2 c2 c2 a1 a1 a1 a1 f1 f1 f1 f1 g1 g1 g1 g1', 's', '1', 'n'),
        30,
    ),
    'village': (
        ('g3 a3 c4 a3 g3 e3 g3 r d3 e3 g3 e3 d3 c3 d3 r g3 a3 c4 d4 c4 a3 g3 e3 d3 e3 g3 a3 g3 r r r', 'p', '4', 'f'),
        ('c2 r g1 r c2 r g1 r a1 r e1 r a1 r e1 r f1 r c2 r f1 r c2 r g1 r d2 r g1 r g1 r', 't', '3', 'n'),
        ('c2 r r r r r r r a1 r r r r r r r f1 r r r r r r r g1 r r r r r r r', 's', '1', 'f'),
        22,
    ),
    'city': (
        ('c3 e3 g3 e3 d3 c3 d3 e3 g3 e3 d3 c3 a2 c3 d3 r e3 g3 a3 g3 e3 d3 c3 d3 e3 d3 c3 a2 c3 r r r', 'p', '3', 'n'),
        ('c2 g1 c2 g1 a1 e1 a1 e1 f1 c2 f1 c2 g1 d2 g1 d2 c2 g1 c2 g1 a1 e1 a1 e1 f1 c2 g1 d2 c2 r r r', 't', '3', 'n'),
        ('r r r r r r r r r r r r r r r r r r r r r r r r r r r r r r r r', 's', '0', 'n'),
        18,
    ),
    'temple': (
        ('a2 r c3 r d3 r r r e3 r d3 r c3 r r r a2 r g2 r a2 r c3 r d3 r r r r r r r', 't', '4', 'f'),
        ('a1 r r r r r r r e1 r r r r r r r d1 r r r r r r r e1 r r r r r r r', 's', '2', 'f'),
        ('a0 a0 a0 a0 a0 a0 a0 a0 a0 a0 a0 a0 a0 a0 a0 a0 a0 a0 a0 a0 a0 a0 a0 a0 a0 a0 a0 a0 a0 a0 a0 a0', 't', '1', 'n'),
        30,
    ),
    'mountain': (
        ('d3 r a3 r g3 e3 d3 r e3 r g3 a3 d4 r r r c4 r a3 g3 e3 r d3 r e3 g3 e3 d3 c3 r d3 r', 't', '4', 'f'),
        ('d2 r a1 r d2 r a1 r c2 r g1 r c2 r g1 r a1 r e1 r a1 r e1 r g1 r d2 r d2 r r r', 't', '3', 'n'),
        ('d1 d1 d1 d1 d1 d1 d1 d1 c1 c1 c1 c1 c1 c1 c1 c1 a0 a0 a0 a0 a0 a0 a0 a0 d1 d1 d1 d1 d1 d1 d1 d1', 's', '1', 'n'),
        24,
    ),
    'night': (
        ('a2 r c3 r e3 r d3 c3 a2 r r r g2 r a2 r c3 r d3 r e3 r g3 e3 d3 r c3 r a2 r r r', 't', '3', 'f'),
        ('a1 r r r e1 r r r f1 r r r e1 r r r a1 r r r c2 r r r d2 r r r e1 r r r', 't', '2', 'f'),
        ('r r r r r r r r r r r r r r r r r r r r r r r r r r r r r r r r', 's', '0', 'n'),
        34,
    ),
    'teahouse': (
        ('e3 g3 a3 r c4 a3 g3 r e3 d3 c3 d3 e3 r r r g3 a3 c4 d4 e4 d4 c4 a3 g3 e3 d3 e3 c3 r r r', 'p', '4', 'f'),
        ('c2 r c2 r g1 r g1 r a1 r a1 r e1 r e1 r f1 r f1 r c2 r c2 r g1 r g1 r c2 r r r', 'p', '2', 'f'),
        ('r r r r r r r r r r r r r r r r r r r r r r r r r r r r r r r r', 's', '0', 'n'),
        16,
    ),
    'dawn': (
        ('c3 r e3 r g3 r c4 r d4 r e4 r g4 r r r e4 r d4 r c4 r a3 r c4 r r r r r r r', 't', '5', 'v'),
        ('c2 r r r g1 r r r a1 r r r e1 r r r f1 r r r c2 r r r g1 r r r c2 r r r', 't', '3', 'n'),
        ('c1 c1 c1 c1 c1 c1 c1 c1 a0 a0 a0 a0 a0 a0 a0 a0 f0 f0 f0 f0 f0 f0 f0 f0 g0 g0 g0 g0 c1 c1 c1 c1', 's', '2', 'n'),
        26,
    ),
}

ALIASES = {
    'travel': 'city', 'train': 'city', 'room': 'city', 'river': 'village', 'sunrise': 'dawn',
}

_sfx_slot: dict[str, int] = {}
_music_slot: dict[str, int] = {}


def _setup() -> bool:
    """Builds every sound once. Returns False if Pyxel isn't ready."""
    global _ready
    if _ready:
        return True
    try:
        for i, (name, (notes, tones, vols, fx, speed)) in enumerate(SFX.items()):
            pyxel.sounds[i].set(notes, tones, vols, fx, speed)
            _sfx_slot[name] = i
        base = 24
        for m, (name, (mel, bass, drone, speed)) in enumerate(THEMES.items()):
            seqs = []
            for k, (notes, tone, vol, fx) in enumerate((mel, bass, drone)):
                slot = base + m * 3 + k
                pyxel.sounds[slot].set(notes, tone, vol, fx, speed)
                seqs.append([slot])
            pyxel.musics[m].set(*seqs)
            _music_slot[name] = m
    except Exception:
        return False
    _ready = True
    return True


def _settings_allow(kind: str) -> bool:
    try:
        from .session import SESSION

        st = SESSION.state.settings
        return bool(st.music if kind == 'music' else st.sfx)
    except Exception:
        return True


def music(name: str) -> None:
    """Starts a place's theme (keeps playing if it's already on)."""
    global _current
    name = ALIASES.get(name, name)
    if name == _current:
        return
    _current = name
    if not enabled_music or not _settings_allow('music') or not _setup():
        return
    try:
        if name in _music_slot:
            pyxel.playm(_music_slot[name], loop=True)
        else:
            stop_music()
    except Exception:
        pass


def stop_music() -> None:
    try:
        for ch in range(3):
            pyxel.stop(ch)
    except Exception:
        pass


def refresh() -> None:
    """Settings changed: restart or silence the current theme."""
    global _current
    name, _current = _current, ''
    if _settings_allow('music'):
        music(name)
    else:
        stop_music()


def sfx(name: str) -> None:
    if not enabled_sfx or not _settings_allow('sfx') or not _setup():
        return
    slot = _sfx_slot.get(name)
    if slot is None:
        return
    try:
        pyxel.play(SFX_CH, slot)
    except Exception:
        pass

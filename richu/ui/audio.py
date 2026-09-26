"""Music and sound effects (Pyxel's four channels). Filled in at the sound stage."""
from __future__ import annotations

_current = ''
enabled_music = True
enabled_sfx = True


def music(name: str) -> None:
    global _current
    _current = name


def sfx(name: str) -> None:
    pass

"""The running game: state, saving, settings, toasts."""
from __future__ import annotations

from dataclasses import dataclass

from ..core import state as st
from ..core.state import GameState


@dataclass
class Toast:
    text: str
    glyphs: str = ''
    icon: str = ''
    frames: int = 90


class Session:
    def __init__(self) -> None:
        self.state = GameState()
        self.toasts: list[Toast] = []

    def boot(self) -> None:
        """Reads saved settings (needs Pyxel initialised for the data directory)."""
        self.state.settings = st.load_settings()

    def new_game(self) -> GameState:
        settings = self.state.settings
        self.state = GameState()
        self.state.settings = settings
        st.clear()
        return self.state

    def has_save(self) -> bool:
        return st.load() is not None

    def load(self) -> bool:
        loaded = st.load()
        if loaded is None:
            return False
        loaded.settings = self.state.settings
        self.state = loaded
        return True

    def save(self) -> None:
        st.save(self.state)

    def save_settings(self) -> None:
        st.save_settings(self.state.settings)

    def toast(self, text: str, glyphs: str = '', icon: str = '', frames: int = 90) -> None:
        self.toasts.append(Toast(text, glyphs, icon, frames))


SESSION = Session()

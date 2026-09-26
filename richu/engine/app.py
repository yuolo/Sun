"""The application: Pyxel window, main loop and a stack of screens.

A screen is anything drawn full-screen or as an overlay: the title, the
scene, the journal, a card, a puzzle window. Only the top screen receives
input; the ones below keep drawing (and may keep animating via ``tick``).
"""
from __future__ import annotations

import pyxel

from ..art import palette
from . import text
from .input import INPUT
from .tasks import Future, Scheduler

W, H = 320, 180
FPS = 30
TITLE = '日出 · Восход'


class Screen:
    #: Screens below an opaque screen are not drawn.
    opaque = False

    def __init__(self) -> None:
        self.closed = Future()

    def update(self) -> None:
        """Input and logic; called only while this screen is on top."""

    def tick(self) -> None:
        """Animation that keeps running while another screen is on top."""

    def draw(self) -> None:
        pass

    def cursor(self) -> str:
        """Cursor shape while this screen is on top."""
        return 'arrow'

    def close(self, value: object = None) -> None:
        APP.pop(self)
        self.closed.set(value)


class App:
    def __init__(self) -> None:
        self.stack: list[Screen] = []
        self.sched = Scheduler()
        self.frame = 0
        self.headless = False
        self.quit_requested = False

    # ---------------------------------------------------------------- stack

    @property
    def top(self) -> Screen | None:
        return self.stack[-1] if self.stack else None

    def push(self, screen: Screen) -> Screen:
        self.stack.append(screen)
        return screen

    def pop(self, screen: Screen | None = None) -> None:
        if screen is None:
            if self.stack:
                self.stack.pop()
        elif screen in self.stack:
            self.stack.remove(screen)

    def replace_all(self, screen: Screen) -> None:
        self.sched.cancel_all()
        self.stack = [screen]

    def find(self, kind: type) -> Screen | None:
        for s in reversed(self.stack):
            if isinstance(s, kind):
                return s
        return None

    async def show(self, screen: Screen) -> object:
        """Pushes a screen and waits until it closes; returns its result."""
        self.push(screen)
        return await screen.closed

    # ---------------------------------------------------------------- loop

    def update(self) -> None:
        INPUT.begin_frame()
        self.frame += 1
        top = self.top
        for s in self.stack[:-1]:
            s.tick()
        if top is not None:
            top.update()
        self.sched.step()

    def draw(self) -> None:
        palette.reset()
        start = 0
        for i, s in enumerate(self.stack):
            if s.opaque:
                start = i
        if not self.stack:
            pyxel.cls(palette.INK)
        for s in self.stack[start:]:
            palette.reset()
            s.draw()
        palette.reset()
        if not self.headless:
            draw_cursor(self.top.cursor() if self.top else 'arrow')


APP = App()

# 7×9 cursors: '#' outline, '+' fill.
_CURSORS = {
    'arrow': ['#', '##', '#+#', '#++#', '#+++#', '#++++#', '#+++##', '##+#', '#  #'],
    'hand': ['  ##', ' #++#', ' #++#', ' #++###', '##+++++#', '#++++++#', '#++++++#', ' #++++#', '  ####'],
    'talk': ['######', '#++++#', '#++++#', '#++++#', '###+##', '  #+#', '  ##'],
    'look': ['  ###', ' #+++#', '#++#++#', '#+###+#', '#++#++#', ' #+++#', '  ###'],
    'brush': ['     ##', '    #+#', '   #+#', '  #+#', ' ###', '#+#', '##'],
    'wait': ['#####', '#+++#', ' #+#', '  #', ' #+#', '#+++#', '#####'],
}


def draw_cursor(kind: str) -> None:
    shape = _CURSORS.get(kind, _CURSORS['arrow'])
    x, y = INPUT.mx, INPUT.my
    if kind in ('talk', 'look', 'wait'):
        x -= 3
        y -= 3
    for dy, row in enumerate(shape):
        for dx, c in enumerate(row):
            if c == '#':
                pyxel.pset(x + dx, y + dy, palette.INK)
            elif c == '+':
                pyxel.pset(x + dx, y + dy, palette.PAPER if kind != 'brush' else palette.GOLD)


def init(headless: bool = False) -> None:
    pyxel.init(W, H, title=TITLE, fps=FPS, quit_key=pyxel.KEY_NONE, headless=headless, capture_scale=4)
    palette.apply()
    text.load()
    APP.headless = headless
    if not headless:
        pyxel.mouse(False)


def run() -> None:
    pyxel.run(APP.update, APP.draw)

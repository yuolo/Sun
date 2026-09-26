"""A ScriptContext without UI: lines are recorded, animations skipped, answers
and puzzle results come from queues. Tests use it to play the whole game."""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from . import interact, journal, talisman
from .path import WalkPath
from .phrases import glyphs_of
from .state import START, GameState


class HeadlessContext:
    def __init__(self, state: GameState | None = None) -> None:
        self.state = state or GameState()
        self.transcript: list[str] = []
        self.events: list[str] = []
        self.answers: list[str] = []
        self.solutions: dict[str, list[Any]] = defaultdict(list)

    # ---------------------------------------------------------------- state

    def flag(self, name: str) -> Any:
        return self.state.flags.get(name)

    def set(self, name: str, value: Any = True) -> None:
        self.state.flags[name] = value

    def has(self, item: str) -> bool:
        return item in self.state.inventory

    def give(self, item: str) -> None:
        from ..content.items import ITEMS

        if item not in ITEMS:
            raise KeyError(f'unknown item {item}')
        if item not in self.state.inventory:
            self.state.inventory.append(item)
        journal.see(self.state, ITEMS[item].zh)
        self.events.append(f'give:{item}')

    def take(self, item: str) -> None:
        if item in self.state.inventory:
            self.state.inventory.remove(item)

    def add_coins(self, n: int) -> None:
        self.state.coins = max(0, self.state.coins + n)

    def confirm(self, glyphs: str) -> None:
        journal.confirm(self.state, list(glyphs))

    def unlock(self, text_id: str) -> None:
        if journal.unlock_text(self.state, text_id):
            self.events.append(f'text:{text_id}')

    def sfx(self, name: str) -> None:
        pass

    # ---------------------------------------------------------------- dialogue

    async def say(self, actor: str, text: str, auto: int = 0) -> None:
        journal.see(self.state, text)
        journal.record_line(self.state, actor, text, self.state.scene)
        self.transcript.append(f'{actor}: {text}')

    async def talk(self, lines: list[tuple[str, str]]) -> None:
        for actor, text in lines:
            await self.say(actor, text)

    async def narrate(self, text: str) -> None:
        self.transcript.append(f'* {text}')

    async def ask(self, actor: str, question: str) -> str:
        await self.say(actor, question)
        if not self.answers:
            raise AssertionError(f'unexpected question from {actor}: {question}')
        answer = self.answers.pop(0)
        for g in glyphs_of(answer):
            if g not in self.state.seen:
                raise AssertionError(f'answer uses a glyph the player has not met: {g}')
        self.transcript.append(f'> {answer}')
        return answer

    async def puzzle(self, kind: str, **params: Any) -> Any:
        self.events.append(f'puzzle:{kind}')
        # lines the puzzle window shows (a lesson, a riddle) are read by the player
        for line in params.get('lines') or ():
            journal.see(self.state, line)
        queue = self.solutions.get(kind)
        if not queue:
            raise AssertionError(f'no planned solution for puzzle {kind} {params}')
        sol = queue.pop(0)
        result = sol(**params) if callable(sol) else sol
        if kind == 'talisman' and isinstance(result, str):
            tal = params['talisman']
            talisman.apply(self.state, tal, result)
        return result

    # ---------------------------------------------------------------- stage

    async def move(self, actor: str, x: int, y: int | None = None) -> None:
        pass

    async def wait(self, ms: int) -> None:
        pass

    async def event(self, name: str) -> None:
        self.events.append(name)

    async def read(self, text_id: str) -> None:
        from ..content.texts import text

        self.unlock(text_id)
        journal.see(self.state, text(text_id).zh)
        self.events.append(f'read:{text_id}')

    async def chapter(self, n: int) -> None:
        self.state.chapter = n
        self.events.append(f'chapter:{n}')

    async def finish(self) -> None:
        self.state.finished = True
        self.events.append('finish')

    async def goto(self, scene_id: str, entry: str) -> None:
        from ..content.world import scene_by_id

        scene = scene_by_id(scene_id)
        if entry not in scene.entries:
            raise KeyError(f'scene {scene_id} has no entry {entry}')
        self.state.scene = scene_id
        self.state.px = int(WalkPath(scene.path).clamp(scene.entries[entry]))
        await interact.enter_scene(self, scene)


class HeadlessGame:
    """Plays through the scene API the way a player would, without animation."""

    def __init__(self, state: GameState | None = None) -> None:
        from .tasks_sync import run

        self.c = HeadlessContext(state)
        self._run = run

    @property
    def state(self) -> GameState:
        return self.c.state

    def scene(self):
        from ..content.world import scene_by_id

        return scene_by_id(self.state.scene)

    def start(self, scene: str = START[0], entry: str = START[1]) -> 'HeadlessGame':
        self._run(self.c.goto(scene, entry))
        return self

    def talk(self, actor: str) -> 'HeadlessGame':
        self._run(interact.talk_to(self.c, self.scene(), actor))
        return self

    def click(self, hotspot: str) -> 'HeadlessGame':
        self._run(interact.click_hotspot(self.c, self.scene(), hotspot))
        return self

    def use(self, item: str, target: str) -> bool:
        return self._run(interact.use_item_on(self.c, self.scene(), target, item))

    def ask(self, actor: str, glyph: str) -> bool:
        return self._run(interact.ask_about(self.c, self.scene(), actor, glyph))

    def cast(self, text: str, target: str | None = None):
        for g in text:
            if g not in self.state.seen:
                raise AssertionError(f'cannot write {g}: not met yet')
        return self._run(interact.perform_cast(self.c, self.scene(), text, target))

    def exit(self, exit_id: str) -> bool:
        return self._run(interact.take_exit(self.c, self.scene(), exit_id))

    def answer(self, *answers: str) -> 'HeadlessGame':
        self.c.answers.extend(answers)
        return self

    def plan(self, kind: str, *results: Any) -> 'HeadlessGame':
        self.c.solutions[kind].extend(results)
        return self

    def read(self, text_id: str) -> 'HeadlessGame':
        """Opens an unlocked text in the journal and reads it."""
        from ..content.texts import text

        if text_id not in self.state.texts:
            raise AssertionError(f'text {text_id} is not unlocked')
        journal.see(self.state, text(text_id).zh)
        return self

    def solve_page(self, page_id: str) -> list[str]:
        """Places every glyph correctly, as a player who understood them."""
        from ..content.pages import page

        p = page(page_id)
        if journal.page_status(self.state, p) != 'open':
            raise AssertionError(f'page {page_id} is not open: missing {[g for g in journal.page_chars(p) if g not in self.state.seen]}')
        for i, g in enumerate(p.glyphs):
            journal.place(self.state, p, i, g)
        ok, fresh = journal.submit_page(self.state, p)
        assert ok
        return fresh

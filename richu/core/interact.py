"""Scene API shared by the UI runtime and the headless context."""
from __future__ import annotations

from typing import TYPE_CHECKING

from . import journal
from .state import GameState
from .types import ActorDef, ExitDef, HotspotDef, Num, SceneDef, SignDef

if TYPE_CHECKING:
    from .magic import Spell
    from .types import ScriptContext


def num(v: Num | None, s: GameState, default: int = 0) -> int:
    if v is None:
        return default
    return v(s) if callable(v) else v


def visible_actors(scene: SceneDef, s: GameState) -> list[ActorDef]:
    return [a for a in scene.actors if a.visible is None or a.visible(s)]


def visible_hotspots(scene: SceneDef, s: GameState) -> list[HotspotDef]:
    return [h for h in scene.hotspots if h.visible is None or h.visible(s)]


def visible_exits(scene: SceneDef, s: GameState) -> list[ExitDef]:
    return [e for e in scene.exits if e.visible is None or e.visible(s)]


def visible_signs(scene: SceneDef, s: GameState) -> list[SignDef]:
    return [g for g in scene.signs if g.visible is None or g.visible(s)]


def actor_stand(a: ActorDef, s: GameState) -> int:
    """Where the player stands to talk to an actor."""
    if a.stand_at is not None:
        return num(a.stand_at, s)
    x = num(a.x, s)
    return x - 22 if x > 40 else x + 22


def hotspot_stand(h: HotspotDef, s: GameState) -> int:
    if h.stand_at is not None:
        return num(h.stand_at, s)
    return h.rect[0] + h.rect[2] // 2


def find_actor(scene: SceneDef, s: GameState, actor_id: str) -> ActorDef:
    for a in visible_actors(scene, s):
        if a.id == actor_id:
            return a
    raise KeyError(f'no visible actor {actor_id} in {scene.id}')


def find_hotspot(scene: SceneDef, s: GameState, hid: str) -> HotspotDef:
    for h in visible_hotspots(scene, s):
        if h.id == hid:
            return h
    raise KeyError(f'no visible hotspot {hid} in {scene.id}')


def sign_text(sign: SignDef, s: GameState) -> str:
    """A sign's text; an edited talisman shows its new inscription."""
    if sign.talisman:
        from .talisman import text_of

        return text_of(s, sign.talisman, sign.text)
    return sign.text


def see_signs(scene: SceneDef, s: GameState) -> None:
    for sign in visible_signs(scene, s):
        t = sign_text(sign, s)
        journal.see(s, t)
        journal.record_line(s, 'sign', t.replace('\n', ''), scene.id)


async def enter_scene(c: 'ScriptContext', scene: SceneDef) -> None:
    s = c.state
    first = scene.id not in s.visited
    if first:
        s.visited.append(scene.id)
    see_signs(scene, s)
    for text_id in scene.diary:
        c.unlock(text_id)
    if scene.on_enter:
        await scene.on_enter(c)
    see_signs(scene, s)


async def talk_to(c: 'ScriptContext', scene: SceneDef, actor_id: str) -> None:
    a = find_actor(scene, c.state, actor_id)
    if a.on_talk:
        await a.on_talk(c)


async def click_hotspot(c: 'ScriptContext', scene: SceneDef, hid: str) -> None:
    h = find_hotspot(scene, c.state, hid)
    if h.on_click:
        await h.on_click(c)


async def use_item_on(c: 'ScriptContext', scene: SceneDef, target: str, item: str) -> bool:
    """Uses (shows) an inventory item on an actor or hotspot. Returns whether it was handled."""
    if not c.has(item):
        raise KeyError(f'player has no {item}')
    for a in visible_actors(scene, c.state):
        if a.id == target:
            return bool(a.on_item and await a.on_item(c, item))
    for h in visible_hotspots(scene, c.state):
        if h.id == target:
            return bool(h.on_item and await h.on_item(c, item))
    raise KeyError(f'no target {target} in {scene.id}')


async def ask_about(c: 'ScriptContext', scene: SceneDef, actor_id: str, glyph: str) -> bool:
    """The player points at a glyph in the journal and shows it to someone."""
    a = find_actor(scene, c.state, actor_id)
    return bool(a.on_ask and await a.on_ask(c, glyph))


async def cast_on(c: 'ScriptContext', scene: SceneDef, target: str | None, spell: 'Spell') -> bool:
    """Lets the target react to a spell. Returns True if it did something special."""
    if spell.power != 'full':
        return False
    if target:
        for a in visible_actors(scene, c.state):
            if a.id == target:
                return bool(a.on_spell and await a.on_spell(c, spell))
        for h in visible_hotspots(scene, c.state):
            if h.id == target:
                return bool(h.on_spell and await h.on_spell(c, spell))
    return bool(scene.on_spell and await scene.on_spell(c, spell))


async def take_exit(c: 'ScriptContext', scene: SceneDef, exit_id: str) -> bool:
    for e in visible_exits(scene, c.state):
        if e.id == exit_id:
            if e.guard and not await e.guard(c):
                return False
            await c.goto(e.to, e.entry)
            return True
    raise KeyError(f'no exit {exit_id} in {scene.id}')


async def perform_cast(c: 'ScriptContext', scene: SceneDef, text: str, target: str | None) -> tuple['Spell', bool]:
    """Casts a written spell at a target: returns the spell and whether the world reacted specially.

    Full-power spells that form a meaning are written into the spell book.
    """
    from . import magic

    spell = magic.cast(text, c.state.confirmed, magic.default_lookup, magic.default_specials())
    handled = False
    if spell.power == 'full' and spell.ok:
        handled = await cast_on(c, scene, target, spell)
        if text not in c.state.spells:
            c.state.spells.append(text)
    return spell, handled

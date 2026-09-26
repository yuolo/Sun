"""The scene: walking, people, things, exits, signs, bubbles — and the script runtime.

``SceneView`` is the screen; ``Runtime`` implements ``ScriptContext`` for the
scene scripts with animation (bubbles wait for a click, walks take time).
"""
from __future__ import annotations

from typing import Any

import pyxel

from .. import platform
from ..art import figures, icons, kit
from ..art import palette as P
from ..content import items as I
from ..content.world import scene_by_id
from ..core import interact, journal
from ..core.path import WalkPath
from ..core.state import GameState
from ..core.types import ActorDef, FigureSpec, SceneDef, SceneLook, SignDef
from ..engine import text, ui
from ..engine.app import APP, H, W, Screen
from ..engine.input import INPUT
from ..engine.tasks import Future
from . import audio, fx, glyphline
from .bubbles import Bubble, Narration
from .session import SESSION

WALK_SPEED = 2.0
NPC_SPEED = 1.4
HUD_Y = H - 20


def player_spec(s: GameState, look: SceneLook) -> FigureSpec:
    prop = ''
    if look.rain and 'umbrella' in s.inventory:
        prop = 'umbrella'
    elif look.lantern and 'lantern' in s.inventory:
        prop = 'lantern'
    elif s.chapter <= 2 and 'suitcase' in s.inventory:
        prop = 'suitcase'
    return FigureSpec(P.DARK_BLUE, P.OCHRE, 'jacket', 'short', legs=P.INK, prop=prop)


class Mover:
    """A figure on stage: position, facing, walking and a little acting."""

    def __init__(self, id: str, x: float, y: float, facing: str = 'right') -> None:
        self.id = id
        self.x, self.y = x, y
        self.facing = facing
        self.tx: float | None = None
        self.ty: float | None = None
        self.fut: Future | None = None
        self.step = 0
        self.anim = ''
        self.anim_t = 0
        self.speed = NPC_SPEED

    def walk_to(self, x: float, y: float | None = None, speed: float | None = None) -> Future:
        if self.fut is not None:
            self.fut.set()
        self.tx, self.ty = x, y
        self.speed = speed or self.speed
        fut: Future = Future()
        self.fut = fut
        if abs(x - self.x) < 1 and (y is None or abs(y - self.y) < 1):
            self._arrive()
        return fut

    def _arrive(self) -> None:
        self.tx = self.ty = None
        self.step = 0
        fut, self.fut = self.fut, None
        if fut:
            fut.set()

    def update(self, path: WalkPath | None = None) -> None:
        if self.anim:
            self.anim_t += 1
            if self.anim_t > 60 and self.anim not in ('sleep',):
                self.anim, self.anim_t = '', 0
            elif self.anim == 'sleep' and self.anim_t > 120:
                self.anim, self.anim_t = '', 0
        if self.tx is None:
            return
        dx = self.tx - self.x
        if abs(dx) >= 0.5:
            self.facing = 'right' if dx > 0 else 'left'
        dist = abs(dx)
        if self.ty is not None:
            dist = max(dist, abs(self.ty - self.y))
        if dist <= self.speed:
            self.x = self.tx
            if self.ty is not None:
                self.y = self.ty
            elif path is not None:
                self.y = path.y_at(self.x)
            self._arrive()
            return
        k = self.speed / dist
        self.x += dx * k
        if self.ty is not None:
            self.y += (self.ty - self.y) * k
        elif path is not None:
            self.y = path.y_at(self.x)
        self.step += 1

    @property
    def frame(self) -> int:
        if self.tx is None:
            return 0
        return 1 + (self.step // 5) % 3 if (self.step // 5) % 4 != 3 else 0

    def offset(self) -> tuple[float, float]:
        t = self.anim_t
        if self.anim == 'jump':
            return 0, -abs(pyxel.sin(t * 12) * 6) if t < 30 else 0
        if self.anim == 'laugh':
            return 0, -(t // 4 % 2)
        if self.anim == 'float':
            return 0, -min(10, t / 3) if t < 45 else -max(0, 10 - (t - 45))
        if self.anim == 'shake':
            return (1 if t // 2 % 2 else -1) if t < 20 else 0, 0
        return 0, 0


class SceneView(Screen):
    opaque = True

    def __init__(self) -> None:
        super().__init__()
        self.rt = Runtime(self)
        self.scene: SceneDef | None = None
        self.look = SceneLook()
        self.bg = pyxel.Image(W, H)
        self.front = pyxel.Image(W, H)
        self.has_front = False
        self.bg_dirty = True
        self.path: WalkPath | None = None
        self.player = Mover('player', 0, 0)
        self.player.speed = WALK_SPEED
        self.actors: dict[str, Mover] = {}
        self.bubbles: list[Bubble] = []
        self.narration: Narration | None = None
        self.task = None
        self.mode = 'free'  # free · item · brush · ask
        self.item: str | None = None
        self.spell_text = ''
        self.ask_glyph = ''
        self.fade = 0.0
        self.fade_to = 0.0
        self.fade_fut: Future | None = None
        self.effects: list[fx.Effect] = []
        self.weather = fx.Weather()
        self.tooltip = ''
        self.hover_glyph: str | None = None
        self.hud_open = 0.0
        self.frame = 0
        self.hud_buttons: list[tuple[str, int, int, int, int]] = []

    @property
    def s(self) -> GameState:
        return SESSION.state

    # ---------------------------------------------------------------- scene loading

    def load(self, scene_id: str, entry: str | None = None) -> None:
        scene = scene_by_id(scene_id)
        self.scene = scene
        self.s.scene = scene_id
        self.path = WalkPath(scene.path)
        if entry is not None:
            self.s.px = int(self.path.clamp(scene.entries[entry]))
            mid = (self.path.x0 + self.path.x1) / 2
            self.s.facing = 'right' if self.s.px < mid else 'left'
        x = self.s.px if self.s.px >= 0 else scene.entries[next(iter(scene.entries))]
        self.player = Mover('player', x, self.path.y_at(x), self.s.facing)
        self.player.speed = WALK_SPEED
        self.actors = {}
        for a in scene.actors:
            self.actors[a.id] = Mover(a.id, interact.num(a.x, self.s), interact.num(a.y, self.s), self._facing(a))
        self.bubbles.clear()
        self.narration = None
        self.effects.clear()
        self.mode = 'free'
        self.item = None
        self.bg_dirty = True
        audio.music(scene.music)

    def _facing(self, a: ActorDef) -> str:
        return a.facing(self.s) if callable(a.facing) else a.facing

    def refresh(self) -> None:
        """Flags may have changed: redraw the background, re-read actor positions of idle actors."""
        self.bg_dirty = True
        if not self.scene:
            return
        for a in self.scene.actors:
            m = self.actors.get(a.id)
            if m is None:
                self.actors[a.id] = Mover(a.id, interact.num(a.x, self.s), interact.num(a.y, self.s), self._facing(a))

    def render_background(self) -> None:
        assert self.scene is not None
        self.look = self.scene.look(self.s)
        kit.canvas(self.bg)
        self.bg.cls(P.INK)
        self.scene.art(self.s, self.look)
        self.has_front = self.scene.front is not None
        if self.has_front:
            kit.canvas(self.front)
            self.front.cls(0)
            self.scene.front(self.s, self.look)  # type: ignore[misc]
        kit.canvas(pyxel)
        self.weather.set(self.look)
        self.bg_dirty = False

    # ---------------------------------------------------------------- scripts

    @property
    def busy(self) -> bool:
        return self.task is not None and not self.task.finished

    def run(self, coro: Any, name: str = '') -> None:
        if self.busy:
            coro.close()
            return

        async def wrapped() -> None:
            try:
                await coro
            finally:
                self.bubbles.clear()
                self.narration = None
                self.refresh()
                SESSION.save()

        self.task = APP.sched.spawn(wrapped(), name)

    # ---------------------------------------------------------------- update

    def update(self) -> None:
        self.frame += 1
        self.s.play_frames += 1
        if self.bg_dirty and self.scene:
            self.render_background()
        self._animate()
        if self.fade != self.fade_to:
            return
        for b in self.bubbles:
            b.update()
        if self.narration:
            self.narration.update()
        if self._hud_update():
            return
        if self.bubbles or self.narration:
            self._dialogue_input()
            return
        if self.busy:
            return
        self._keys()
        self._pointer()

    def tick(self) -> None:
        self._animate()

    def _animate(self) -> None:
        self.player.update(self.path)
        for m in self.actors.values():
            m.update()
        self.s.px = int(self.player.x)
        self.s.facing = self.player.facing
        for e in self.effects:
            e.update()
        self.effects = [e for e in self.effects if not e.done]
        self.weather.update()
        if self.fade != self.fade_to:
            step = 0.12
            self.fade = min(self.fade_to, self.fade + step) if self.fade < self.fade_to else max(self.fade_to, self.fade - step)
            if self.fade == self.fade_to and self.fade_fut:
                self.fade_fut.set()
                self.fade_fut = None
        for t in SESSION.toasts[:1]:
            t.frames -= 1
        SESSION.toasts[:] = [t for t in SESSION.toasts if t.frames > 0]

    def _dialogue_input(self) -> None:
        hovered = next((b.hovered for b in self.bubbles if b.hovered), None)
        if hovered and INPUT.click(0, 0, W, H):
            self._open_card(hovered)
            return
        if INPUT.advance():
            if self.narration:
                if self.narration.age > 6:
                    self.narration.fut.set()
            elif self.bubbles:
                top = self.bubbles[-1]
                if top.age > 6 and not top.auto:
                    top.fut.set()

    def _keys(self) -> None:
        if INPUT.key(pyxel.KEY_J):
            self.open_journal()
        elif INPUT.key(pyxel.KEY_B):
            self.open_brush()
        elif INPUT.key(pyxel.KEY_H):
            self.show_hint()
        elif INPUT.key(pyxel.KEY_M):
            self.open_map()
        elif INPUT.key(pyxel.KEY_ESCAPE) or INPUT.right:
            if self.mode != 'free':
                self.mode, self.item = 'free', None
            else:
                self.open_menu()

    # ---------------------------------------------------------------- pointer

    def _targets(self) -> list[tuple[str, str, tuple[int, int, int, int], str]]:
        """(kind, id, rect, label) under the pointer, topmost first."""
        out = []
        if not self.scene:
            return out
        for a in reversed(sorted(interact.visible_actors(self.scene, self.s), key=lambda a: self.actors[a.id].y if a.id in self.actors else 0)):
            m = self.actors.get(a.id)
            if not m:
                continue
            spec = self._spec(a)
            h = figures.height(spec)
            out.append(('actor', a.id, (int(m.x) - 7, int(m.y) - h - 1, 14, h + 2), a.name))
        for h in reversed(interact.visible_hotspots(self.scene, self.s)):
            out.append(('hotspot', h.id, h.rect, h.name))
        for e in interact.visible_exits(self.scene, self.s):
            out.append(('exit', e.id, e.rect, e.label))
        return out

    def _hit(self) -> tuple[str, str, str] | None:
        for kind, tid, (x, y, w, h), label in self._targets():
            if INPUT.inside(x, y, w, h):
                return kind, tid, label
        return None

    def _pointer(self) -> None:
        self.tooltip = ''
        hit = self._hit()
        # people and ways out come before signs: a sign under them isn't clickable
        sign_glyph = None if hit and hit[0] in ('actor', 'exit') else self._sign_hover()
        if sign_glyph is None:
            self.hover_glyph = None
        if hit:
            self.tooltip = hit[2]
        if sign_glyph and INPUT.click(0, 0, W, H):
            self._open_card(sign_glyph)
            return
        if not INPUT.pressed or INPUT.taken:
            return
        INPUT.take()
        if self.mode == 'brush':
            target = hit[1] if hit and hit[0] != 'exit' else None
            text_ = self.spell_text
            self.mode = 'free'
            self.run(self._cast(text_, target), 'cast')
            return
        if self.mode == 'ask':
            glyph = self.ask_glyph
            self.mode = 'free'
            if hit and hit[0] == 'actor':
                self.run(self._ask(hit[1], glyph), 'ask')
            return
        if hit:
            kind, tid, _ = hit
            if self.mode == 'item' and self.item and kind in ('actor', 'hotspot'):
                item = self.item
                self.mode, self.item = 'free', None
                self.run(self._use(kind, tid, item), 'use')
            elif kind == 'actor':
                self.run(self._talk(tid), 'talk')
            elif kind == 'hotspot':
                self.run(self._click(tid), 'click')
            elif kind == 'exit':
                self.run(self._exit(tid), 'exit')
            return
        if self.mode == 'item':
            self.mode, self.item = 'free', None
            return
        if self.path and INPUT.my < HUD_Y + (0 if self.hud_open > 0.5 else 20):
            self.player.walk_to(self.path.nearest_x(INPUT.mx, INPUT.my))

    def cursor(self) -> str:
        if self.busy and not (self.bubbles or self.narration):
            return 'wait'
        if self.mode == 'brush':
            return 'brush'
        if self.mode == 'ask':
            return 'talk'
        hit = self._hit() if not (self.bubbles or self.narration) else None
        if hit:
            if hit[0] == 'actor':
                return 'talk'
            if hit[0] == 'exit':
                return 'hand'
            h = next((h for h in self.scene.hotspots if h.id == hit[1]), None) if self.scene else None
            return h.cursor if h else 'look'
        return 'arrow'

    # ---------------------------------------------------------------- interactions (scripts)

    async def _walk(self, x: int) -> None:
        await self.player.walk_to(x)

    async def _face(self, x: float) -> None:
        self.player.facing = 'right' if x >= self.player.x else 'left'

    async def _talk(self, actor_id: str) -> None:
        assert self.scene
        a = interact.find_actor(self.scene, self.s, actor_id)
        await self._walk(interact.actor_stand(a, self.s))
        await self._face(self.actors[actor_id].x)
        m = self.actors[actor_id]
        m.facing = 'left' if self.player.x < m.x else 'right'
        await interact.talk_to(self.rt, self.scene, actor_id)

    async def _click(self, hid: str) -> None:
        assert self.scene
        h = interact.find_hotspot(self.scene, self.s, hid)
        await self._walk(interact.hotspot_stand(h, self.s))
        await self._face(h.rect[0] + h.rect[2] / 2)
        await interact.click_hotspot(self.rt, self.scene, hid)

    async def _use(self, kind: str, tid: str, item: str) -> None:
        assert self.scene
        if kind == 'actor':
            a = interact.find_actor(self.scene, self.s, tid)
            await self._walk(interact.actor_stand(a, self.s))
            await self._face(self.actors[tid].x)
        else:
            h = interact.find_hotspot(self.scene, self.s, tid)
            await self._walk(interact.hotspot_stand(h, self.s))
            await self._face(h.rect[0] + h.rect[2] / 2)
        handled = await interact.use_item_on(self.rt, self.scene, tid, item)
        if not handled:
            if kind == 'actor':
                # people name the thing they are shown
                await self.rt.say(tid, I.item(item).zh + '？')
            else:
                await self.rt.narrate('Ничего не происходит.')

    async def _ask(self, actor_id: str, glyph: str) -> None:
        assert self.scene
        a = interact.find_actor(self.scene, self.s, actor_id)
        await self._walk(interact.actor_stand(a, self.s))
        await self._face(self.actors[actor_id].x)
        await self.rt.say('player', glyph + '？', auto=45)
        if not await interact.ask_about(self.rt, self.scene, actor_id, glyph):
            await self.rt.say(actor_id, glyph + '。')

    async def _exit(self, exit_id: str) -> None:
        assert self.scene
        e = next(x for x in interact.visible_exits(self.scene, self.s) if x.id == exit_id)
        await self._walk(e.stand_at)
        await interact.take_exit(self.rt, self.scene, exit_id)

    async def _cast(self, spell_text: str, target: str | None) -> None:
        assert self.scene
        if target and target in self.actors:
            m = self.actors[target]
            tx, ty = int(m.x), int(m.y) - 20
        elif target:
            h = next((h for h in self.scene.hotspots if h.id == target), None)
            tx, ty = (h.rect[0] + h.rect[2] // 2, h.rect[1] + h.rect[3] // 2) if h else (W // 2, 60)
        else:
            tx, ty = INPUT.mx, INPUT.my
        await self._face(tx)
        ink = fx.InkWrite(spell_text, tx, ty)
        self.effects.append(ink)
        audio.sfx('brush')
        await ink.fut
        spell, handled = await interact.perform_cast(self.rt, self.scene, spell_text, target)
        if spell.power == 'fizzle':
            self.effects.append(fx.Fizzle(tx, ty))
            await self.rt.narrate(spell.reason)
            return
        if not handled:
            self.effects.extend(fx.generic(spell, tx, ty, self.actors.get(target or '')))
        if spell.power == 'shadow':
            SESSION.toast('Тень смысла: не все знаки подтверждены', spell_text, frames=70)
        elif spell.text in self.s.spells and self.s.spells[-1] == spell.text:
            SESSION.toast('Новое заклинание', spell_text)
        if spell.reason:
            await self.rt.narrate(spell.reason)

    # ---------------------------------------------------------------- screens

    def _open_card(self, glyph: str) -> None:
        from .card import GlyphCard

        APP.push(GlyphCard(glyph, self))

    def open_journal(self, tab: str = '') -> None:
        from .journal import Journal

        APP.push(Journal(self, tab))

    def open_brush(self) -> None:
        if 'brush' not in self.s.inventory or not self.s.flags.get('brush_awake'):
            SESSION.toast('Кисть пока молчит')
            return
        from .composer import BrushPad

        async def flow() -> None:
            result = await APP.show(BrushPad())
            if isinstance(result, str) and result:
                self.spell_text = result
                self.mode = 'brush'

        APP.sched.spawn(flow(), 'brush')

    def begin_ask(self, glyph: str) -> None:
        self.ask_glyph = glyph
        self.mode = 'ask'

    def open_map(self) -> None:
        from .map import MapScreen

        APP.push(MapScreen(self))

    def open_menu(self) -> None:
        from .menus import PauseMenu

        APP.push(PauseMenu(self))

    def show_hint(self) -> None:
        from ..core import hints

        self.run(self.rt.narrate(hints.current(self.s)), 'hint')

    # ---------------------------------------------------------------- HUD

    def _hud_visible(self) -> bool:
        return INPUT.my >= H - 26 or self.mode in ('item',) or self.hud_open > 0.99 and INPUT.my >= H - 40

    def _hud_update(self) -> bool:
        target = 1.0 if self._hud_visible() and not (self.bubbles or self.narration) else 0.0
        self.hud_open += (target - self.hud_open) * 0.35
        if self.hud_open < 0.5:
            return False
        y = H - 20
        for name, x, bw, _, _ in self.hud_buttons:
            if INPUT.click(x, y + 2, bw, 16):
                self._hud_action(name)
                return True
        if INPUT.inside(0, y, W, 20) and INPUT.pressed:
            INPUT.take()
            return True
        return False

    def _hud_action(self, name: str) -> None:
        if name.startswith('item:'):
            item = name[5:]
            if self.mode == 'item' and self.item == item:
                self.mode, self.item = 'free', None
            else:
                self.mode, self.item = 'item', item
        elif name == 'brush':
            self.open_brush()
        elif name == 'journal':
            self.open_journal()
        elif name == 'map':
            self.open_map()
        elif name == 'menu':
            self.open_menu()

    def _draw_hud(self) -> None:
        self.hud_buttons = []
        if self.hud_open < 0.05:
            # a small handle
            pyxel.rect(W // 2 - 10, H - 3, 20, 3, P.OCHRE)
            return
        y = H - int(20 * min(1.0, self.hud_open))
        pyxel.dither(0.9)
        pyxel.rect(0, y, W, 20, P.INK)
        pyxel.dither(1.0)
        pyxel.line(0, y, W, y, P.OCHRE)
        x = 4
        hovered_item = None
        for it in self.s.inventory:
            d = I.ITEMS.get(it)
            if not d:
                continue
            sel = self.mode == 'item' and self.item == it
            if sel:
                pyxel.rect(x - 1, y + 1, 18, 18, P.VERMILION)
            elif INPUT.inside(x - 1, y + 1, 18, 18):
                pyxel.rect(x - 1, y + 1, 18, 18, P.WOOD)
                hovered_item = d
            icons.draw(d.icon, x, y + 2)
            self.hud_buttons.append((f'item:{it}', x - 1, 18, y, 18))
            x += 19
        bx = W - 4
        for name, label in (('menu', '…'), ('map', '图'), ('journal', '记'), ('brush', '笔')):
            bw = 16 if len(label) == 1 else 30
            bx -= bw + 2
            self.hud_buttons.append((name, bx, bw, y, 16))
            hover = INPUT.inside(bx, y + 2, bw, 16)
            pyxel.rect(bx, y + 2, bw, 16, P.GOLD if hover else P.WOOD)
            pyxel.rectb(bx, y + 2, bw, 16, P.OCHRE)
            text.center(bx + bw // 2, y + 3, label, P.INK if hover else P.PAPER)
        coins = f'{self.s.coins}'
        cx = bx - 8 - text.width(coins) - 12
        icons.draw('coins', cx, y + 2)
        text.draw(cx + 16, y + 3, coins, P.GOLD)
        if hovered_item:
            self._item_tip(hovered_item, y)

    def _item_tip(self, d: Any, y: int) -> None:
        w, h, _ = glyphline.draw_line(self.s, d.zh, -1000, -1000, hover=False)
        tw = max(w + 8, 30)
        tx = max(2, min(W - tw - 2, INPUT.mx - tw // 2))
        ty = y - h - 10
        ui.panel(tx, ty, tw, h + 6, 'paper')
        glyphline.draw_line(self.s, d.zh, tx + 4, ty + 2, hover=False)

    # ---------------------------------------------------------------- drawing

    def _spec(self, a: ActorDef) -> FigureSpec:
        return a.figure(self.s) if callable(a.figure) else a.figure

    def draw(self) -> None:
        if not self.scene:
            pyxel.cls(P.INK)
            return
        if self.bg_dirty:
            self.render_background()
        look = self.look
        P.set_time(look.time)
        pyxel.blt(0, 0, self.bg, 0, 0, W, H)
        if self.scene.anim:
            self.scene.anim(self.s, look, self.frame)
        P.reset()
        self._draw_signs()
        # people, sorted by depth
        movers: list[tuple[float, Any, Any]] = []
        for a in interact.visible_actors(self.scene, self.s):
            m = self.actors.get(a.id)
            if m:
                movers.append((m.y, m, self._spec(a)))
        movers.append((self.player.y + 0.1, self.player, player_spec(self.s, look)))
        movers.sort(key=lambda t: t[0])
        lit = look.lantern and 'lantern' in self.s.inventory
        for _, m, spec in movers:
            P.set_figure_time(look.time, lit and abs(m.x - self.player.x) < 60)
            ox, oy = m.offset()
            if m.anim == 'sleep':
                figures.draw(spec, m.x + ox, m.y + oy, m.facing, 0)
            else:
                figures.draw(spec, m.x + ox, m.y + oy, m.facing, m.frame)
            P.reset()
            if m.anim == 'sleep' and (self.frame // 20) % 2:
                text.draw(m.x + 4, m.y - 38, 'z', P.MIST, small=True)
        if self.has_front:
            P.set_time(look.time)
            pyxel.blt(0, 0, self.front, 0, 0, W, H, 0)
            P.reset()
        if lit:
            kit.canvas(pyxel)
            kit.glow(int(self.player.x) + 4, int(self.player.y) - 18, 40)
        self.weather.draw()
        for e in self.effects:
            e.draw()
        for b in self.bubbles:
            b.draw()
        if self.narration:
            self.narration.draw()
        if not (self.bubbles or self.narration):
            self._draw_hud()
            self._draw_tooltip()
        self._draw_mode_banner()
        draw_toasts(self.s)
        if self.fade > 0:
            pyxel.dither(min(1.0, self.fade))
            pyxel.rect(0, 0, W, H, P.INK)
            pyxel.dither(1.0)

    def _draw_tooltip(self) -> None:
        if self.hover_glyph:
            note = self.s.guesses.get(self.hover_glyph, '')
            label = self.hover_glyph + (f' — {note}' if note else '')
        else:
            label = self.tooltip
        if not label or self.busy:
            return
        w = text.width(label, True) + 6
        x = max(2, min(W - w - 2, INPUT.mx + 8))
        y = max(2, INPUT.my - 14)
        pyxel.rect(x, y, w, 12, P.INK)
        text.draw(x + 3, y + 1, label, P.PAPER, small=True)

    def _draw_mode_banner(self) -> None:
        msg = ''
        if self.mode == 'item' and self.item:
            msg = 'Показать или использовать: выберите цель'
        elif self.mode == 'brush':
            msg = f'{self.spell_text} — куда направить кисть?'
        elif self.mode == 'ask':
            msg = f'{self.ask_glyph} — кого спросить?'
        if msg:
            w = text.width(msg) + 10
            ui.panel(W // 2 - w // 2, 2, w, 16, 'night', shadow=False)
            text.center(W // 2, 3, msg, P.GOLD)

    # ---------------------------------------------------------------- signs

    def _sign_box(self, sign: SignDef) -> tuple[int, int, int, int, list[str]]:
        lines = interact.sign_text(sign, self.s).split('\n')
        if sign.vertical:
            cols = lines
            w = len(cols) * 14 + 4
            h = max(len(c) for c in cols) * 13 + 5
        else:
            w = max(len(l) for l in lines) * 13 + 5
            h = len(lines) * 14 + 3
        return sign.x, sign.y, w, h, lines

    def _sign_hover(self) -> str | None:
        self.hover_glyph = None
        if not self.scene:
            return None
        for sign in interact.visible_signs(self.scene, self.s):
            if sign.talisman:
                # an acting inscription is edited with the brush, not looked up
                continue
            x, y, w, h, lines = self._sign_box(sign)
            if not INPUT.inside(x, y, w, h):
                continue
            for i, line in enumerate(lines):
                for j, ch in enumerate(line):
                    gx, gy = (x + 3 + i * 14, y + 3 + j * 13) if sign.vertical else (x + 3 + j * 13, y + 2 + i * 14)
                    if INPUT.inside(gx, gy, 13, 14):
                        self.hover_glyph = ch
                        return ch
        return None

    def _draw_signs(self) -> None:
        assert self.scene
        night = self.look.time in ('night', 'dusk', 'predawn')
        for sign in interact.visible_signs(self.scene, self.s):
            x, y, w, h, lines = self._sign_box(sign)
            fill, edge, ink = SIGN_STYLES.get(sign.style, SIGN_STYLES['plaque'])
            if night and sign.style not in ('screen', 'lit'):
                fill, ink = {P.PAPER: P.GREY, P.OCHRE: P.PLUM, P.STONE: P.NAVY}.get(fill, fill), ink
            if fill is not None:
                pyxel.rect(x, y, w, h, fill)
            if edge is not None:
                pyxel.rectb(x, y, w, h, edge)
            for i, line in enumerate(lines):
                for j, ch in enumerate(line):
                    gx, gy = (x + 3 + i * 14, y + 3 + j * 13) if sign.vertical else (x + 3 + j * 13, y + 2 + i * 14)
                    hov = self.hover_glyph == ch and INPUT.inside(gx, gy, 13, 14)
                    text.draw(gx, gy, ch, P.LAMP if hov else ink)
            if INPUT.inside(x, y, w, h) and not self.busy:
                self._sign_notes(sign, x, y, w, h, lines)

    def _sign_notes(self, sign: SignDef, x: int, y: int, w: int, h: int, lines: list[str]) -> None:
        """Notes (guesses, pinyin) appear under a sign while it is hovered."""
        line = ''.join(lines)
        cells, lw = glyphline.layout(self.s, line)
        if not any(c.note for c in cells):
            return
        ty = y + h + 2 if y + h + 30 < H else y - 30
        tx = max(2, min(W - lw - 8, x))
        ui.panel(tx, ty, lw + 8, 28, 'paper', shadow=False)
        glyphline.draw_row(self.s, cells, tx + 4, ty + 1, hover=False)


# fill, edge, ink
SIGN_STYLES: dict[str, tuple[int | None, int | None, int]] = {
    'plaque': (P.LACQUER, P.GOLD, P.GOLD),
    'board': (P.OCHRE, P.WOOD, P.INK),
    'stone': (P.STONE, P.PLUM, P.INK),
    'banner': (P.VERMILION, P.LACQUER, P.GOLD),
    'paper': (P.PAPER, P.STONE, P.INK),
    'tag': (P.PAPER, P.INK, P.INK),
    'carved': (None, None, P.INK),
    'screen': (P.INK, P.STONE, P.GOLD),
    'lit': (P.JADE, P.PINE, P.WHITE),
    'blue': (P.DARK_BLUE, P.WHITE, P.WHITE),
    'chalk': (P.PINE, P.WOOD, P.WHITE),
}


def draw_toasts(s: GameState) -> None:
    if not SESSION.toasts:
        return
    t = SESSION.toasts[0]
    label = t.text
    gw = 0
    if t.glyphs:
        cells, gw = glyphline.layout(s, t.glyphs, notes=False)
    w = text.width(label) + 12 + (gw + 6 if t.glyphs else 0) + (18 if t.icon else 0)
    x = W // 2 - w // 2
    y = 4 if t.frames > 8 else 4 - (8 - t.frames) * 3
    ui.panel(x, y, w, 18, 'night')
    cx = x + 6
    if t.icon:
        icons.draw(t.icon, cx - 2, y + 1)
        cx += 18
    if t.glyphs:
        text.draw(cx, y + 2, t.glyphs, P.LAMP)
        cx += gw + 6
    text.draw(cx, y + 2, label, P.PAPER)


# ---------------------------------------------------------------- the script runtime


class Runtime:
    """ScriptContext for the real game: every await is a real wait."""

    def __init__(self, view: SceneView) -> None:
        self.v = view

    @property
    def state(self) -> GameState:
        return SESSION.state

    def flag(self, name: str) -> Any:
        return self.state.flags.get(name)

    def set(self, name: str, value: Any = True) -> None:
        self.state.flags[name] = value
        self.v.bg_dirty = True

    def has(self, item: str) -> bool:
        return item in self.state.inventory

    def give(self, item: str) -> None:
        d = I.item(item)
        if item not in self.state.inventory:
            self.state.inventory.append(item)
        journal.see(self.state, d.zh)
        SESSION.toast('', d.zh, d.icon, 100)
        audio.sfx('item')

    def take(self, item: str) -> None:
        if item in self.state.inventory:
            self.state.inventory.remove(item)
        if self.v.item == item:
            self.v.mode, self.v.item = 'free', None

    def add_coins(self, n: int) -> None:
        self.state.coins = max(0, self.state.coins + n)
        audio.sfx('coins')

    def confirm(self, glyphs: str) -> None:
        fresh = journal.confirm(self.state, list(glyphs))
        if fresh:
            SESSION.toast('понято', ''.join(fresh))
            audio.sfx('seal')

    def unlock(self, text_id: str) -> None:
        if journal.unlock_text(self.state, text_id):
            SESSION.toast('Новая запись в дневнике', icon='diary')

    def sfx(self, name: str) -> None:
        audio.sfx(name)

    # ---------------------------------------------------------------- dialogue

    def _anchor(self, actor: str) -> tuple[int, int]:
        v = self.v
        if actor == 'player':
            return int(v.player.x), int(v.player.y) - 32
        m = v.actors.get(actor)
        if m and v.scene:
            a = next((a for a in v.scene.actors if a.id == actor), None)
            h = figures.height(v._spec(a)) if a else 30
            ox, oy = m.offset()
            return int(m.x + ox), int(m.y + oy) - h - 2
        if v.scene and actor in v.scene.marks:
            return v.scene.marks[actor]
        return W // 2, 30

    async def say(self, actor: str, line: str, auto: int = 0) -> None:
        s = self.state
        journal.see(s, line)
        journal.record_line(s, actor, line, s.scene)
        if s.settings.voice and actor != 'player':
            platform.speak(line)
        audio.sfx('talk')
        b = Bubble(s, line, self._anchor(actor), auto=auto, player=actor == 'player')
        self.v.bubbles = [b]
        await b.fut
        if b in self.v.bubbles:
            self.v.bubbles.remove(b)

    async def talk(self, lines: list[tuple[str, str]]) -> None:
        for actor, line in lines:
            await self.say(actor, line)

    async def narrate(self, line: str) -> None:
        n = Narration(line)
        self.v.narration = n
        await n.fut
        if self.v.narration is n:
            self.v.narration = None

    async def ask(self, actor: str, question: str) -> str:
        from .composer import AnswerPad

        s = self.state
        journal.see(s, question)
        journal.record_line(s, actor, question, s.scene)
        if s.settings.voice:
            platform.speak(question)
        b = Bubble(s, question, self._anchor(actor))
        self.v.bubbles = [b]
        answer = await APP.show(AnswerPad(question))
        self.v.bubbles = []
        answer = answer if isinstance(answer, str) else ''
        if answer:
            await self.say('player', answer, auto=50)
        return answer

    async def puzzle(self, kind: str, **params: Any) -> Any:
        from .puzzles import open_puzzle

        return await open_puzzle(self.v, kind, **params)

    # ---------------------------------------------------------------- stage

    async def move(self, actor: str, x: int, y: int | None = None) -> None:
        if actor == 'player':
            await self.v.player.walk_to(x)
            return
        m = self.v.actors[actor]
        await m.walk_to(x, y)

    async def goto(self, scene_id: str, entry: str) -> None:
        v = self.v
        fut: Future = Future()
        v.fade_to, v.fade_fut = 1.0, fut
        await fut
        v.load(scene_id, entry)
        v.render_background()
        fut2: Future = Future()
        v.fade_to, v.fade_fut = 0.0, fut2
        SESSION.save()
        assert v.scene
        await interact.enter_scene(self, v.scene)
        await fut2

    async def wait(self, ms: int) -> None:
        await APP.sched.sleep(max(1, ms * 30 // 1000))

    async def event(self, name: str) -> None:
        from .events import run_event

        await run_event(self.v, name)

    async def read(self, text_id: str) -> None:
        from .reader import Reader

        self.unlock(text_id)
        await APP.show(Reader(text_id))

    async def chapter(self, n: int) -> None:
        from .menus import ChapterCard

        self.state.chapter = n
        SESSION.save()
        await APP.show(ChapterCard(n))

    async def finish(self) -> None:
        from .menus import Ending

        self.state.finished = True
        SESSION.save()
        await APP.show(Ending())

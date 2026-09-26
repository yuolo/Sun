import { see } from './journal';
import type { ActorDef, ExitDef, GameState, HotspotDef, Num, SceneDef, ScriptContext } from './types';

export function num(v: Num, s: GameState): number {
  return typeof v === 'function' ? v(s) : v;
}

export function actorVisible(a: ActorDef, s: GameState): boolean {
  return a.visible ? a.visible(s) : true;
}

export function visibleActors(scene: SceneDef, s: GameState): ActorDef[] {
  return scene.actors.filter((a) => actorVisible(a, s));
}

export function visibleHotspots(scene: SceneDef, s: GameState): HotspotDef[] {
  return scene.hotspots.filter((h) => (h.visible ? h.visible(s) : true));
}

export function visibleExits(scene: SceneDef, s: GameState): ExitDef[] {
  return scene.exits.filter((e) => (e.visible ? e.visible(s) : true));
}

export function visibleSigns(scene: SceneDef, s: GameState) {
  return scene.signs.filter((g) => (g.visible ? g.visible(s) : true));
}

/** Where the player should stand to interact with an actor. */
export function actorStand(a: ActorDef, s: GameState): number {
  if (a.standAt !== undefined) return num(a.standAt, s);
  return num(a.x, s) - 110;
}

/** Record a line in the player's log (no duplicates). */
export function recordLine(s: GameState, who: string, text: string, scene: string): void {
  if (!s.log.some((l) => l.who === who && l.text === text)) s.log.push({ who, text, scene });
}

/** Mark signs as seen and run the scene's enter script. */
export async function enterScene(c: ScriptContext, scene: SceneDef): Promise<void> {
  for (const sign of visibleSigns(scene, c.state)) see(c.state, sign.lines.join(''));
  if (scene.onEnter) await scene.onEnter(c);
  for (const sign of visibleSigns(scene, c.state)) see(c.state, sign.lines.join(''));
}

export async function talkTo(c: ScriptContext, scene: SceneDef, actorId: string): Promise<void> {
  const a = scene.actors.find((x) => x.id === actorId);
  if (!a || !actorVisible(a, c.state)) throw new Error(`no actor ${actorId} in ${scene.id}`);
  await a.onTalk?.(c);
}

export async function clickHotspot(c: ScriptContext, scene: SceneDef, id: string): Promise<void> {
  const h = visibleHotspots(scene, c.state).find((x) => x.id === id);
  if (!h) throw new Error(`no hotspot ${id} in ${scene.id}`);
  await h.onClick?.(c);
}

/** Use an inventory item on an actor or hotspot. Returns whether it was handled. */
export async function useItemOn(c: ScriptContext, scene: SceneDef, targetId: string, item: string): Promise<boolean> {
  if (!c.has(item)) throw new Error(`player has no ${item}`);
  const a = visibleActors(scene, c.state).find((x) => x.id === targetId);
  if (a) return a.onItem ? a.onItem(c, item) : false;
  const h = visibleHotspots(scene, c.state).find((x) => x.id === targetId);
  if (h) return h.onItem ? h.onItem(c, item) : false;
  throw new Error(`no target ${targetId} in ${scene.id}`);
}

/** Try to leave through an exit. Returns true if the player moved on. */
export async function takeExit(c: ScriptContext, scene: SceneDef, exitId: string): Promise<boolean> {
  const e = visibleExits(scene, c.state).find((x) => x.id === exitId);
  if (!e) throw new Error(`no exit ${exitId} in ${scene.id}`);
  if (e.guard && !(await e.guard(c))) return false;
  await c.goto(e.to, e.entry);
  return true;
}

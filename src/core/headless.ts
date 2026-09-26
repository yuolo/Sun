import { sceneById } from '../content/world';
import { enterScene, recordLine, takeExit, talkTo, clickHotspot, useItemOn } from './interact';
import { confirmGlyphs, see } from './journal';
import { WalkPath } from './path';
import { glyphsOf } from './phrases';
import { START, createState } from './state';
import type { Chapter, ComposeRequest, Cup, FlagValue, GameState, Glyph, PuzzleId, SceneDef, ScriptContext } from './types';

export interface PuzzleSolver {
  tray(): Cup[] | null;
  bells(): boolean;
  compose(req: ComposeRequest): Glyph[];
  stele(): string;
  ancient(): boolean;
}

/**
 * A ScriptContext without UI: lines are recorded, animations are skipped,
 * answers and puzzle results come from queues. Used by tests to play the
 * whole game and by the debug console.
 */
export class HeadlessContext implements ScriptContext {
  readonly state: GameState;
  readonly transcript: string[] = [];
  readonly events: string[] = [];
  answers: string[] = [];
  trays: (Cup[] | null)[] = [];
  solver: PuzzleSolver = {
    tray: () => (this.trays.length ? this.trays.shift()! : null),
    bells: () => true,
    compose: (req) => [...req.targets],
    stele: () => '',
    ancient: () => true,
  };

  constructor(state: GameState = createState(0)) {
    this.state = state;
  }

  flag(name: string) {
    return this.state.flags[name];
  }

  set(name: string, value: FlagValue = true) {
    this.state.flags[name] = value;
  }

  has(item: string) {
    return this.state.inventory.includes(item);
  }

  give(item: string) {
    if (!this.has(item)) this.state.inventory.push(item);
    this.events.push(`give:${item}`);
  }

  take(item: string) {
    this.state.inventory = this.state.inventory.filter((i) => i !== item);
  }

  addCoins(n: number) {
    this.state.coins = Math.max(0, this.state.coins + n);
  }

  async say(actor: string, text: string) {
    see(this.state, text);
    recordLine(this.state, actor, text, this.state.scene);
    this.transcript.push(`${actor}: ${text}`);
  }

  async talk(lines: [string, string][]) {
    for (const [a, t] of lines) await this.say(a, t);
  }

  async narrate(text: string) {
    this.transcript.push(`* ${text}`);
  }

  async ask(actor: string, question: string) {
    await this.say(actor, question);
    const answer = this.answers.shift();
    if (answer === undefined) throw new Error(`unexpected question from ${actor}: ${question}`);
    for (const g of glyphsOf(answer)) {
      if (!this.state.seen[g]) throw new Error(`answer uses unseen glyph ${g}`);
    }
    this.transcript.push(`> ${answer}`);
    return answer;
  }

  puzzle(id: 'tray'): Promise<Cup[] | null>;
  puzzle(id: 'bells'): Promise<boolean>;
  puzzle(id: 'compose', req: ComposeRequest): Promise<Glyph[]>;
  puzzle(id: 'stele'): Promise<string>;
  puzzle(id: 'ancient'): Promise<boolean>;
  async puzzle(id: PuzzleId, req?: ComposeRequest): Promise<unknown> {
    this.events.push(`puzzle:${id}`);
    switch (id) {
      case 'tray':
        return this.solver.tray();
      case 'bells':
        return this.solver.bells();
      case 'compose':
        return this.solver.compose(req!);
      case 'stele':
        return this.solver.stele();
      case 'ancient':
        return this.solver.ancient();
    }
  }

  async move() {}
  async wait() {}

  async event(name: string) {
    this.events.push(name);
  }

  sfx() {}

  confirm(glyphs: Glyph[]) {
    confirmGlyphs(this.state, glyphs);
  }

  async chapter(n: Chapter) {
    this.events.push(`chapter:${n}`);
  }

  async finish() {
    this.state.finished = true;
    this.events.push('finish');
  }

  async goto(sceneId: string, entry: string) {
    const scene = sceneById(sceneId);
    const x = scene.entries[entry];
    if (x === undefined) throw new Error(`scene ${sceneId} has no entry ${entry}`);
    this.state.scene = sceneId;
    this.state.px = new WalkPath(scene.path).atX(x);
    await enterScene(this, scene);
  }
}

/** Drives a HeadlessContext through the scene API. */
export class HeadlessGame {
  readonly c: HeadlessContext;

  constructor(state?: GameState) {
    this.c = new HeadlessContext(state);
  }

  get state() {
    return this.c.state;
  }

  scene(): SceneDef {
    return sceneById(this.c.state.scene);
  }

  start() {
    return this.c.goto(START.scene, START.entry);
  }

  talk(actor: string) {
    return talkTo(this.c, this.scene(), actor);
  }

  click(hotspot: string) {
    return clickHotspot(this.c, this.scene(), hotspot);
  }

  use(item: string, target: string) {
    return useItemOn(this.c, this.scene(), target, item);
  }

  exit(exitId: string) {
    return takeExit(this.c, this.scene(), exitId);
  }

  answer(...answers: string[]) {
    this.c.answers.push(...answers);
    return this;
  }
}

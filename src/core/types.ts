/** A single hanzi used as a journal entry. */
export type Glyph = string;

export type Tone = 0 | 1 | 2 | 3 | 4;
export type Chapter = 1 | 2 | 3 | 4;

export interface GlyphDef {
  ch: Glyph;
  pinyin: string;
  tone: Tone;
  /** Short Russian meaning shown after confirmation. */
  meaning: string;
  chapter: Chapter;
  /** Origin / structure of the character (Russian). */
  origin: string;
  /** Real-life words with this character: [hanzi, pinyin, meaning]. */
  words: [string, string, string][];
}

export interface PageDef {
  id: string;
  title: string;
  chapter: Chapter;
  glyphs: Glyph[];
}

export interface GrammarDef {
  id: string;
  title: string;
  /** Unlocked when all of these glyphs are confirmed. */
  requires: Glyph[];
  text: string;
  examples: [string, string][];
}

export interface ItemDef {
  id: string;
  name: string;
  description: string;
}

export type Drink = 'tea' | 'water';
export type CupSize = 'big' | 'small';
export interface Cup {
  drink: Drink;
  size: CupSize;
}

export interface Settings {
  pinyin: boolean;
  guesses: boolean;
  voice: boolean;
  music: boolean;
  sfx: boolean;
}

export interface LogLine {
  who: string;
  text: string;
  scene: string;
}

export type FlagValue = boolean | number | string;

export interface GameState {
  v: number;
  scene: string;
  px: number;
  seen: Record<Glyph, number>;
  guesses: Record<Glyph, string>;
  confirmed: Record<Glyph, true>;
  pages: Record<string, true>;
  placements: Record<string, (Glyph | null)[]>;
  inventory: string[];
  coins: number;
  tray: Cup[];
  flags: Record<string, FlagValue>;
  log: LogLine[];
  inscription: string;
  settings: Settings;
  startedAt: number;
  playMs: number;
  finished: boolean;
}

/* ------------------------------------------------------------------ */
/* Scenes                                                              */
/* ------------------------------------------------------------------ */

export type Pred = (s: GameState) => boolean;
export type Num = number | ((s: GameState) => number);

export type Script = (c: ScriptContext) => Promise<void>;
/** Returns true if the item was handled. */
export type ItemScript = (c: ScriptContext, item: string) => Promise<boolean>;

export type HatKind =
  | 'none'
  | 'straw'
  | 'cap'
  | 'topknot'
  | 'bun'
  | 'bald'
  | 'scholar'
  | 'guard'
  | 'hood'
  | 'twinbuns'
  | 'wide';

export interface FigureSpec {
  robe: string;
  trim?: string;
  skin?: string;
  hat: HatKind;
  hatColor?: string;
  scale?: number;
  /** Extra prop drawn with the figure. */
  prop?: 'pole' | 'oar' | 'staff' | 'lantern' | 'lanternDark' | 'bucket' | 'gourd' | 'fan' | 'hoe' | 'spear' | 'broom' | 'scroll' | 'none';
  /** Pose tweak. */
  pose?: 'stand' | 'sit' | 'kneel' | 'bow' | 'point';
  beard?: boolean;
}

export interface ActorDef {
  id: string;
  /** Russian label, used in the log and tooltips. */
  name: string;
  figure: FigureSpec | ((s: GameState) => FigureSpec);
  x: Num;
  y: Num;
  facing?: 'left' | 'right' | ((s: GameState) => 'left' | 'right');
  visible?: Pred;
  /** Where the player stands to interact (x on the walk path). */
  standAt?: Num;
  onTalk?: Script;
  onItem?: ItemScript;
}

export interface HotspotDef {
  id: string;
  name: string;
  rect: [number, number, number, number];
  standAt?: Num;
  visible?: Pred;
  onClick?: Script;
  onItem?: ItemScript;
}

export type SignStyle = 'plaque' | 'board' | 'stone' | 'banner' | 'carved' | 'jar' | 'post';

export interface SignDef {
  id: string;
  /** Lines of text; each line is a string of hanzi. */
  lines: string[];
  x: number;
  y: number;
  style: SignStyle;
  vertical?: boolean;
  /** Pointed board for direction posts. */
  arrow?: 'left' | 'right' | 'up';
  size?: number;
  visible?: Pred;
}

export interface ExitDef {
  id: string;
  to: string;
  entry: string;
  /** Clickable zone. */
  rect: [number, number, number, number];
  /** Arrow direction shown on hover. */
  dir: 'left' | 'right' | 'up' | 'down';
  standAt: number;
  label: string;
  visible?: Pred;
  /** Return false to block the exit (the script shows why). */
  guard?: (c: ScriptContext) => Promise<boolean>;
}

export type TimeOfDay = 'day' | 'golden' | 'sunset' | 'dusk' | 'night' | 'predawn' | 'dawn';

export interface SceneLook {
  time: TimeOfDay;
  rain?: boolean;
  mist?: boolean;
  lantern?: boolean;
  stars?: boolean;
}

export interface SceneDef {
  id: string;
  chapter: Chapter;
  title: string;
  /** Background SVG markup (1600×900). */
  art: (s: GameState, look: SceneLook) => string;
  /** Foreground SVG markup drawn over actors. */
  front?: (s: GameState, look: SceneLook) => string;
  look: (s: GameState) => SceneLook;
  /** Walkable polyline. */
  path: [number, number][];
  entries: Record<string, number>;
  actors: ActorDef[];
  hotspots: HotspotDef[];
  signs: SignDef[];
  exits: ExitDef[];
  /** Named points for pointing gestures: event 'point-<name>'. */
  marks?: Record<string, [number, number]>;
  onEnter?: Script;
}

export interface ChapterDef {
  n: Chapter;
  zh: string;
  title: string;
  subtitle: string;
  start: { scene: string; entry: string };
}

/* ------------------------------------------------------------------ */
/* Script context                                                      */
/* ------------------------------------------------------------------ */

export type PuzzleId = 'tray' | 'bells' | 'compose' | 'stele' | 'ancient';

export interface ComposeRequest {
  targets: Glyph[];
}

export interface ScriptContext {
  readonly state: GameState;
  flag(name: string): FlagValue | undefined;
  set(name: string, value?: FlagValue): void;
  has(item: string): boolean;
  give(item: string): void;
  take(item: string): void;
  addCoins(n: number): void;
  /** Show a speech bubble in hanzi. `auto` closes it after that many ms. */
  say(actor: string, text: string, opts?: { auto?: number }): Promise<void>;
  talk(lines: [string, string][]): Promise<void>;
  /** A short Russian description of a wordless action. */
  narrate(text: string): Promise<void>;
  /** Ask the player to answer by composing glyphs. Returns '' if cancelled. */
  ask(actor: string, question: string): Promise<string>;
  puzzle(id: 'tray'): Promise<Cup[] | null>;
  puzzle(id: 'bells'): Promise<boolean>;
  puzzle(id: 'compose', req: ComposeRequest): Promise<Glyph[]>;
  puzzle(id: 'stele'): Promise<string>;
  puzzle(id: 'ancient'): Promise<boolean>;
  move(actor: string, x: number, y?: number): Promise<void>;
  goto(scene: string, entry: string): Promise<void>;
  wait(ms: number): Promise<void>;
  /** Scene-specific visual event (sunset, rain, gate opening…). */
  event(name: string): Promise<void>;
  sfx(name: string): void;
  confirm(glyphs: Glyph[]): void;
  chapter(n: Chapter): Promise<void>;
  finish(): Promise<void>;
}

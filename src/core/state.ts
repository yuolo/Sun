import type { FlagValue, GameState, Settings } from './types';

export const STATE_VERSION = 1;
export const SAVE_KEY = 'richu-save-v1';
export const START = { scene: '1a', entry: 'boat' } as const;

export const DEFAULT_SETTINGS: Settings = {
  pinyin: true,
  guesses: true,
  voice: true,
  music: true,
  sfx: true,
};

export function createState(now = Date.now()): GameState {
  return {
    v: STATE_VERSION,
    scene: START.scene,
    px: -1,
    seen: {},
    guesses: {},
    confirmed: {},
    pages: {},
    placements: {},
    inventory: [],
    coins: 0,
    tray: [],
    flags: {},
    log: [],
    inscription: '',
    settings: { ...DEFAULT_SETTINGS },
    startedAt: now,
    playMs: 0,
    finished: false,
  };
}

function isRecord(v: unknown): v is Record<string, unknown> {
  return typeof v === 'object' && v !== null && !Array.isArray(v);
}

/** Restore a saved state, filling in anything missing. Returns null for garbage. */
export function restoreState(raw: unknown): GameState | null {
  if (!isRecord(raw) || typeof raw.scene !== 'string') return null;
  const base = createState();
  const s = { ...base, ...raw } as GameState;
  s.settings = { ...DEFAULT_SETTINGS, ...(isRecord(raw.settings) ? raw.settings : {}) } as Settings;
  for (const key of ['seen', 'guesses', 'confirmed', 'pages', 'placements', 'flags'] as const) {
    if (!isRecord(s[key])) (s as unknown as Record<string, unknown>)[key] = {};
  }
  for (const key of ['inventory', 'tray', 'log'] as const) {
    if (!Array.isArray(s[key])) (s as unknown as Record<string, unknown>)[key] = [];
  }
  if (typeof s.coins !== 'number' || !Number.isFinite(s.coins)) s.coins = 0;
  if (typeof s.px !== 'number') s.px = -1;
  if (typeof s.inscription !== 'string') s.inscription = '';
  s.v = STATE_VERSION;
  return s;
}

export function serialize(s: GameState): string {
  return JSON.stringify(s);
}

export function deserialize(json: string | null): GameState | null {
  if (!json) return null;
  try {
    return restoreState(JSON.parse(json));
  } catch {
    return null;
  }
}

/** localStorage may be missing or throw (private mode, blocked cookies). */
export interface KeyValueStore {
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
  removeItem(key: string): void;
}

export function loadFrom(store: KeyValueStore | undefined): GameState | null {
  try {
    return deserialize(store?.getItem(SAVE_KEY) ?? null);
  } catch {
    return null;
  }
}

export function saveTo(store: KeyValueStore | undefined, s: GameState): boolean {
  try {
    store?.setItem(SAVE_KEY, serialize(s));
    return !!store;
  } catch {
    return false;
  }
}

export function clearSave(store: KeyValueStore | undefined): void {
  try {
    store?.removeItem(SAVE_KEY);
  } catch {
    /* storage unavailable */
  }
}

export function getFlag(s: GameState, name: string): FlagValue | undefined {
  return s.flags[name];
}

export function isOn(s: GameState, name: string): boolean {
  return !!s.flags[name];
}

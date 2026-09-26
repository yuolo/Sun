import type { ScriptContext } from '../../core/types';

/** What an item "is" in the characters the player already met. */
const ITEM_GLYPH: Record<string, string> = {
  water: '水',
  wood: '木',
  torch: '火',
  lantern: '火',
};

/** «不要X。我要Y。» — refuse a wrong item, repeat the wish. */
export async function refuse(c: ScriptContext, actor: string, item: string, want: string): Promise<boolean> {
  const g = ITEM_GLYPH[item];
  await c.say(actor, g && g !== want ? `不要${g}。我要${want}。` : `不。我要${want}。`);
  return true;
}

/** Cycle through lines on repeated clicks. */
export async function cycle(c: ScriptContext, key: string, actor: string, lines: string[]): Promise<void> {
  const n = Number(c.flag(key) ?? 0);
  await c.say(actor, lines[n % lines.length]);
  c.set(key, n + 1);
}

export const PLAYER_FIGURE = {
  robe: '#2f5d62',
  trim: '#c9a86a',
  hat: 'wide',
  hatColor: '#6b5436',
  prop: 'staff',
} as const;

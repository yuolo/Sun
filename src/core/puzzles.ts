import { RECIPES, type Layout } from '../content/recipes';
import type { Cup, CupSize, Drink, Glyph } from './types';

/* ------------------------------------------------------------------ */
/* Tea tray                                                            */
/* ------------------------------------------------------------------ */

export const MAX_TRAY = 4;

export interface Order {
  drink: Drink;
  count: number;
  /** Undefined: any size will do. */
  size?: CupSize;
}

export type OrderProblem = 'empty' | 'drink' | 'count' | 'size';
export type OrderResult = { ok: true } | { ok: false; problem: OrderProblem };

export function checkOrder(cups: readonly Cup[], order: Order): OrderResult {
  if (cups.length === 0) return { ok: false, problem: 'empty' };
  if (cups.some((c) => c.drink !== order.drink)) return { ok: false, problem: 'drink' };
  if (cups.length !== order.count) return { ok: false, problem: 'count' };
  if (order.size && cups.some((c) => c.size !== order.size)) return { ok: false, problem: 'size' };
  return { ok: true };
}

export function addCup(cups: readonly Cup[], cup: Cup): Cup[] {
  return cups.length >= MAX_TRAY ? [...cups] : [...cups, cup];
}

/* ------------------------------------------------------------------ */
/* Temple bells                                                        */
/* ------------------------------------------------------------------ */

export type BellId = 'mountain' | 'sun' | 'rain' | 'water' | 'moon' | 'cloud';

/** Left-to-right order on the rack. */
export const BELLS: BellId[] = ['mountain', 'sun', 'rain', 'water', 'moon', 'cloud'];

export const BELL_GLYPH: Record<BellId, Glyph> = {
  mountain: '山',
  sun: '日',
  rain: '雨',
  water: '水',
  moon: '月',
  cloud: '云',
};

/** Written on the temple board. */
export const BELL_CHANT: Glyph[] = ['雨', '云', '月'];

export type BellResult = 'progress' | 'restart' | 'wrong' | 'solved';

export function ringBell(progress: number, bell: BellId, chant: readonly Glyph[] = BELL_CHANT): { progress: number; result: BellResult } {
  const g = BELL_GLYPH[bell];
  if (g === chant[progress]) {
    const next = progress + 1;
    return { progress: next, result: next >= chant.length ? 'solved' : 'progress' };
  }
  if (g === chant[0]) return { progress: 1, result: 'restart' };
  return { progress: 0, result: 'wrong' };
}

/* ------------------------------------------------------------------ */
/* Building characters                                                 */
/* ------------------------------------------------------------------ */

export function compose(a: Glyph, b: Glyph, layout: Layout): Glyph | null {
  return RECIPES.find((r) => r.a === a && r.b === b && r.layout === layout)?.result ?? null;
}

/* ------------------------------------------------------------------ */
/* Ancient stele: match ancient forms with modern characters           */
/* ------------------------------------------------------------------ */

export const ANCIENT_SET: Glyph[] = ['日', '月', '山', '水', '人', '木'];

/** `pairs` maps ancient form (by its glyph id) to the modern glyph chosen by the player. */
export function checkAncient(pairs: Record<Glyph, Glyph | undefined>, set: readonly Glyph[] = ANCIENT_SET): boolean {
  return set.every((g) => pairs[g] === g);
}

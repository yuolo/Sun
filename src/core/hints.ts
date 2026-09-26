import { DEFAULT_HINT, HINTS, PAGE_HINT } from '../content/hints';
import { openPages } from './journal';
import type { GameState } from './types';

export function currentHint(s: GameState): string {
  const h = HINTS.find((x) => x.when(s));
  if (h) return h.text;
  if (openPages(s).length) return PAGE_HINT;
  return DEFAULT_HINT;
}

/** A page is waiting: a gentler nudge shown before the story hint. */
export function pageNudge(s: GameState): string | null {
  return openPages(s).length ? PAGE_HINT : null;
}

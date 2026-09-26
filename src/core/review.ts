import type { Glyph } from './types';

export type ReviewMode = 'glyph-to-meaning' | 'meaning-to-glyph';

export interface ReviewQuestion {
  mode: ReviewMode;
  glyph: Glyph;
  /** Four glyphs, one of them is `glyph`. */
  options: Glyph[];
}

export const MIN_REVIEW = 4;

function pick<T>(arr: readonly T[], rand: () => number): T {
  return arr[Math.floor(rand() * arr.length) % arr.length];
}

/** Build a multiple-choice question from the confirmed glyphs, avoiding the previous one. */
export function makeQuestion(pool: readonly Glyph[], rand: () => number = Math.random, previous?: Glyph): ReviewQuestion | null {
  if (pool.length < MIN_REVIEW) return null;
  const candidates = pool.length > 1 && previous ? pool.filter((g) => g !== previous) : [...pool];
  const glyph = pick(candidates, rand);
  const others = pool.filter((g) => g !== glyph);
  const options: Glyph[] = [glyph];
  while (options.length < 4) {
    const o = pick(others, rand);
    if (!options.includes(o)) options.push(o);
  }
  for (let i = options.length - 1; i > 0; i--) {
    const j = Math.floor(rand() * (i + 1)) % (i + 1);
    [options[i], options[j]] = [options[j], options[i]];
  }
  return { mode: rand() < 0.5 ? 'glyph-to-meaning' : 'meaning-to-glyph', glyph, options };
}

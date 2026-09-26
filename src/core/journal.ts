import { GRAMMAR } from '../content/grammar';
import { LEXICON, inLexicon } from '../content/lexicon';
import { PAGES } from '../content/pages';
import { isHan } from './phrases';
import type { GameState, Glyph, GrammarDef, PageDef } from './types';

export const MAX_GUESS = 32;

/** Register every lexicon glyph of a text as seen. Returns the newly seen ones. */
export function see(s: GameState, text: string): Glyph[] {
  const fresh: Glyph[] = [];
  for (const ch of text) {
    if (!isHan(ch) || !inLexicon(ch) || s.seen[ch]) continue;
    s.seen[ch] = Object.keys(s.seen).length + 1;
    fresh.push(ch);
  }
  return fresh;
}

export function isSeen(s: GameState, g: Glyph): boolean {
  return !!s.seen[g];
}

/** Glyphs in the order the player met them. */
export function seenGlyphs(s: GameState): Glyph[] {
  return Object.keys(s.seen).sort((a, b) => s.seen[a] - s.seen[b]);
}

export function setGuess(s: GameState, g: Glyph, text: string): void {
  const t = text.trim().slice(0, MAX_GUESS);
  if (t) s.guesses[g] = t;
  else delete s.guesses[g];
}

export function confirmGlyphs(s: GameState, glyphs: Glyph[]): Glyph[] {
  const fresh: Glyph[] = [];
  for (const g of glyphs) {
    if (!inLexicon(g)) continue;
    see(s, g);
    if (!s.confirmed[g]) {
      s.confirmed[g] = true;
      fresh.push(g);
    }
  }
  return fresh;
}

export type PageStatus = 'locked' | 'open' | 'done';

export function missingCount(s: GameState, page: PageDef): number {
  return page.glyphs.filter((g) => !s.seen[g]).length;
}

export function pageStatus(s: GameState, page: PageDef): PageStatus {
  if (s.pages[page.id]) return 'done';
  return missingCount(s, page) === 0 ? 'open' : 'locked';
}

export function openPages(s: GameState): PageDef[] {
  return PAGES.filter((p) => pageStatus(s, p) === 'open');
}

export function placementsFor(s: GameState, page: PageDef): (Glyph | null)[] {
  const saved = s.placements[page.id];
  const out: (Glyph | null)[] = page.glyphs.map((_, i) => saved?.[i] ?? null);
  return out.map((g) => (g && page.glyphs.includes(g) ? g : null));
}

/** Put a glyph into a slot (or clear it with null). A glyph lives in one slot at most. */
export function place(s: GameState, page: PageDef, slot: number, glyph: Glyph | null): (Glyph | null)[] {
  const p = placementsFor(s, page);
  if (slot < 0 || slot >= p.length) return p;
  if (glyph !== null) {
    if (!page.glyphs.includes(glyph)) return p;
    const other = p.indexOf(glyph);
    if (other !== -1) p[other] = null;
  }
  p[slot] = glyph;
  s.placements[page.id] = p;
  return p;
}

export interface PageCheck {
  filled: boolean;
  correct: boolean;
  wrong: number;
}

export function checkPage(page: PageDef, placements: (Glyph | null)[]): PageCheck {
  const filled = page.glyphs.every((_, i) => placements[i] != null);
  const wrong = page.glyphs.filter((g, i) => placements[i] !== g).length;
  return { filled, correct: filled && wrong === 0, wrong };
}

/** Validate a page. On success its glyphs become confirmed. */
export function submitPage(s: GameState, page: PageDef): PageCheck & { confirmed: Glyph[] } {
  const res = checkPage(page, placementsFor(s, page));
  if (!res.correct) return { ...res, confirmed: [] };
  s.pages[page.id] = true;
  delete s.placements[page.id];
  return { ...res, confirmed: confirmGlyphs(s, page.glyphs) };
}

function hash(str: string): number {
  let h = 2166136261;
  for (const ch of str) h = Math.imul(h ^ ch.codePointAt(0)!, 16777619);
  return h >>> 0;
}

/** Deterministic shuffle of a page's glyph pool, never equal to the answer order. */
export function poolOrder(page: PageDef): Glyph[] {
  const out = [...page.glyphs];
  let seed = hash(page.id) || 1;
  for (let i = out.length - 1; i > 0; i--) {
    seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0;
    const j = seed % (i + 1);
    [out[i], out[j]] = [out[j], out[i]];
  }
  if (out.every((g, i) => g === page.glyphs[i])) out.push(out.shift()!);
  return out;
}

export function grammarUnlocked(s: GameState): GrammarDef[] {
  return GRAMMAR.filter((g) => g.requires.every((c) => s.confirmed[c]));
}

export function progress(s: GameState): { seen: number; confirmed: number; total: number } {
  return {
    seen: Object.keys(s.seen).length,
    confirmed: Object.keys(s.confirmed).length,
    total: LEXICON.length,
  };
}

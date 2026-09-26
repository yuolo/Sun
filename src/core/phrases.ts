import type { Glyph } from './types';

const HAN = /[㐀-䶿一-鿿]/;

export function isHan(ch: string): boolean {
  return HAN.test(ch);
}

/** Unique hanzi of a text, in order of appearance. */
export function glyphsOf(text: string): Glyph[] {
  const out: Glyph[] = [];
  for (const ch of text) {
    if (isHan(ch) && !out.includes(ch)) out.push(ch);
  }
  return out;
}

/** Keep only hanzi: punctuation and spaces do not matter in answers. */
export function normalizeAnswer(text: string): string {
  let out = '';
  for (const ch of text) if (isHan(ch)) out += ch;
  return out;
}

export function matchesAny(answer: string, accepted: readonly string[]): boolean {
  const a = normalizeAnswer(answer);
  return accepted.some((x) => normalizeAnswer(x) === a);
}

export function contains(answer: string, glyph: Glyph): boolean {
  return normalizeAnswer(answer).includes(glyph);
}

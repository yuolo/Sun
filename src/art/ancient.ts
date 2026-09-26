import type { Glyph } from '../core/types';

/**
 * Simplified archaic forms (oracle bone / bronze style), drawn as strokes
 * in a 100×100 box. They are schematic, meant to show the picture behind
 * the modern character, not to reproduce a specific inscription.
 */
const FORMS: Record<Glyph, string> = {
  日: '<circle cx="50" cy="50" r="30"/><circle cx="50" cy="50" r="3" fill="currentColor"/>',
  月: '<path d="M62 12 Q24 24 26 54 Q28 80 58 90 Q42 70 44 50 Q46 30 62 12 Z"/><path d="M36 50 L46 46"/>',
  山: '<path d="M12 78 H88 M12 78 L22 48 L32 78 M34 78 L50 18 L66 78 M68 78 L78 48 L88 78"/>',
  水: '<path d="M50 10 Q38 30 52 50 Q64 70 50 90"/><path d="M28 26 L34 34 M24 48 L32 52 M72 26 L66 34 M76 48 L68 52 M28 70 L34 76 M72 70 L66 76"/>',
  火: '<path d="M16 82 Q50 62 84 82 M50 76 L50 20 M32 72 L22 38 M68 72 L78 38"/>',
  木: '<path d="M50 8 V92 M50 40 L22 18 M50 40 L78 18 M50 64 L22 90 M50 64 L78 90"/>',
  人: '<path d="M58 10 Q56 50 28 90 M54 40 L74 58"/>',
  门: '<path d="M22 90 V20 H44 V90 M56 90 V20 H78 V90 M26 34 H40 M60 34 H74"/>',
  雨: '<path d="M12 16 H88 M50 16 V30 M24 30 V42 M24 56 V66 M76 30 V42 M76 56 V66 M50 44 V56 M50 70 V82"/>',
  云: '<path d="M28 18 H72 M26 34 H74 M52 34 Q28 52 38 70 Q52 88 66 72 Q72 60 58 58"/>',
  大: '<circle cx="50" cy="16" r="7"/><path d="M50 23 V56 M18 40 Q50 30 82 40 M50 56 L26 90 M50 56 L74 90"/>',
  天: '<circle cx="50" cy="16" r="11"/><path d="M50 27 V58 M20 42 Q50 34 80 42 M50 58 L28 90 M50 58 L72 90"/>',
  小: '<path d="M50 24 V52 M30 56 L24 72 M70 56 L76 72"/>',
  上: '<path d="M40 36 H60 M18 62 Q50 72 82 62"/>',
  下: '<path d="M18 38 Q50 28 82 38 M40 64 H60"/>',
  中: '<path d="M50 8 V92 M50 8 L68 12 M50 18 L68 22 M50 82 L68 86"/><ellipse cx="50" cy="50" rx="22" ry="13"/>',
  出: '<path d="M22 58 V88 H78 V58"/><path d="M40 70 V30 Q52 22 62 26 M40 48 H56 M40 30 L32 20"/>',
  东: '<path d="M50 6 V94 M32 30 Q50 22 68 30 V66 Q50 74 32 66 Z M32 48 H68 M38 88 L50 74 L62 88 M38 12 L50 24 L62 12"/>',
  明: '<circle cx="30" cy="50" r="18"/><circle cx="30" cy="50" r="2.5" fill="currentColor"/><path d="M78 20 Q56 30 58 52 Q60 72 78 82 Q68 66 70 50 Q72 34 78 20 Z"/>',
  旦: '<circle cx="50" cy="38" r="22"/><circle cx="50" cy="38" r="2.5" fill="currentColor"/><path d="M14 80 H86"/>',
  休: '<path d="M30 12 Q30 46 12 88 M28 40 L40 52"/><path d="M68 10 V92 M68 36 L50 20 M68 36 L86 20 M68 62 L50 86 M68 62 L86 86"/>',
  林: '<path d="M30 10 V92 M30 36 L14 20 M30 36 L46 20 M30 62 L14 86 M30 62 L46 86 M70 10 V92 M70 36 L54 20 M70 36 L86 20 M70 62 L54 86 M70 62 L86 86"/>',
};

export function ancientForm(g: Glyph, size?: number): string | null {
  const inner = FORMS[g];
  if (!inner) return null;
  const dims = size ? ` width="${size}" height="${size}"` : '';
  return `<svg viewBox="0 0 100 100"${dims} class="ancient" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">${inner}</svg>`;
}

/** Just the strokes, for embedding into another SVG (100×100 box). */
export function ancientStrokes(g: Glyph): string | null {
  const inner = FORMS[g];
  if (!inner) return null;
  return `<g fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round" stroke-linejoin="round">${inner}</g>`;
}

export function hasAncient(g: Glyph): boolean {
  return g in FORMS;
}

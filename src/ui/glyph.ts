import { glyphDef } from '../content/lexicon';
import { isHan } from '../core/phrases';
import type { Glyph } from '../core/types';
import type { App } from './app';
import { h } from './dom';

export interface GlyphOpts {
  /** Show the guess / meaning under the character. */
  subtitle?: boolean;
  /** Clicking opens the glyph card. */
  interactive?: boolean;
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'sign' | 'bubble';
  brush?: boolean;
}

/** One character with its pinyin (when confirmed) and the player's note. */
export function glyphEl(app: App, g: Glyph, opts: GlyphOpts = {}): HTMLElement {
  const el = h('span', {
    class: `glyph size-${opts.size ?? 'md'}${opts.brush ? ' brush' : ''}${opts.subtitle === false ? ' nosub' : ''}`,
    'data-g': g,
  });
  if (opts.interactive !== false) {
    el.setAttribute('role', 'button');
    el.tabIndex = 0;
    el.addEventListener('click', (e) => {
      e.stopPropagation();
      app.openGlyph(g, el);
    });
    el.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        e.stopPropagation();
        app.openGlyph(g, el);
      }
    });
  }
  fillGlyph(app, el);
  return el;
}

export function fillGlyph(app: App, el: HTMLElement): void {
  const g = el.dataset.g!;
  const s = app.state;
  const def = glyphDef(g);
  const confirmed = !!s.confirmed[g];
  el.classList.toggle('confirmed', confirmed);
  el.classList.toggle('noted', !confirmed && !!s.guesses[g]);
  el.replaceChildren();
  if (def && confirmed && s.settings.pinyin) el.append(h('span', { class: `py t${def.tone}` }, def.pinyin));
  else el.append(h('span', { class: 'py empty' }, ' '));
  el.append(h('span', { class: 'ch' }, g));
  if (!el.classList.contains('nosub')) {
    const text = confirmed && def ? s.guesses[g] || def.meaning : (s.guesses[g] ?? '');
    el.append(h('span', { class: `gs${text ? '' : ' empty'}` }, s.settings.guesses ? text || ' ' : ' '));
  }
  el.title = confirmed && def ? `${g} ${def.pinyin} — ${def.meaning}` : s.guesses[g] ? `${g}: ${s.guesses[g]}` : g;
}

/** A whole phrase: glyphs plus punctuation. */
export function phraseEl(app: App, text: string, opts: GlyphOpts = {}): HTMLElement {
  const el = h('span', { class: `phrase size-${opts.size ?? 'md'}` });
  for (const ch of text) {
    if (isHan(ch)) el.append(glyphEl(app, ch, opts));
    else if (ch.trim()) el.append(h('span', { class: 'punct' }, ch));
    else el.append(h('span', { class: 'gap' }));
  }
  return el;
}

/** Re-render every glyph on the page (after a guess or confirmation). */
export function refreshAllGlyphs(app: App): void {
  document.querySelectorAll<HTMLElement>('.glyph[data-g]').forEach((el) => fillGlyph(app, el));
}

export const TONE_NAMES = ['лёгкий', 'первый (ровный)', 'второй (восходящий)', 'третий (нисходяще-восходящий)', 'четвёртый (резкий нисходящий)'];

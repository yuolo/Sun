import { seenGlyphs } from '../core/journal';
import type { Glyph } from '../core/types';
import type { App } from './app';
import { h } from './dom';
import { glyphEl, phraseEl } from './glyph';
import { openModal } from './modal';

export interface ComposerOpts {
  title: string;
  question?: string;
  description?: string;
  max?: number;
  submit: string;
  cancel: string;
  initial?: string;
}

/** Let the player compose a phrase from the glyphs they have met. Resolves '' on cancel. */
export function openComposer(app: App, opts: ComposerOpts): Promise<string> {
  const max = opts.max ?? 6;
  let chosen: Glyph[] = [...(opts.initial ?? '')].filter((c) => app.state.seen[c]);
  let result = '';

  const answer = h('div', { class: 'answer-row', 'aria-live': 'polite' });
  const palette = h('div', { class: 'palette' });
  const sayBtn = h('button', { class: 'primary', onclick: () => finish(chosen.join('')) }, opts.submit);

  const render = () => {
    answer.replaceChildren();
    for (let i = 0; i < max; i++) {
      const g = chosen[i];
      if (g) {
        const b = h('button', { class: 'answer-slot filled', 'aria-label': `Убрать ${g}` }, glyphEl(app, g, { interactive: false, size: 'lg' }));
        b.addEventListener('click', () => {
          chosen.splice(i, 1);
          render();
        });
        answer.append(b);
      } else answer.append(h('span', { class: 'answer-slot' }));
    }
    sayBtn.disabled = chosen.length === 0;
  };

  for (const g of seenGlyphs(app.state)) {
    const b = h('button', { class: 'palette-glyph', 'aria-label': `Добавить ${g}` }, glyphEl(app, g, { interactive: false, size: 'md' }));
    b.addEventListener('click', () => {
      if (chosen.length >= max) return;
      chosen.push(g);
      app.audio.sfx('click');
      render();
    });
    b.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      app.openGlyph(g);
    });
    palette.append(b);
  }

  const body = h(
    'div',
    { class: 'composer' },
    opts.question ? h('div', { class: 'composer-question' }, phraseEl(app, opts.question, { size: 'lg' })) : null,
    opts.description ? h('p', { class: 'muted' }, opts.description) : null,
    answer,
    h(
      'div',
      { class: 'composer-actions' },
      h('button', { class: 'ghost', onclick: () => ((chosen = chosen.slice(0, -1)), render()), 'aria-label': 'Стереть последний знак' }, '⌫'),
      h('button', { class: 'ghost', onclick: () => ((chosen = []), render()) }, 'Очистить'),
      h('button', { class: 'ghost', onclick: () => finish('') }, opts.cancel),
      sayBtn,
    ),
    h('p', { class: 'muted small' }, 'Нажимайте на знаки, чтобы составить фразу. Нажмите на знак в ответе, чтобы убрать его.'),
    palette,
  );

  const handle = openModal(app.overlay, body, { title: opts.title, className: 'composer-modal', onClose: () => resolve(result) });
  let resolve!: (v: string) => void;
  const done = new Promise<string>((r) => (resolve = r));
  const finish = (v: string) => {
    result = v;
    handle.close();
  };
  render();
  return done;
}

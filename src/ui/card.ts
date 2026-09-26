import { ancientForm } from '../art/ancient';
import { glyphDef } from '../content/lexicon';
import { PAGES } from '../content/pages';
import { recipeFor } from '../content/recipes';
import { MAX_GUESS, setGuess } from '../core/journal';
import type { Glyph } from '../core/types';
import type { App } from './app';
import { h } from './dom';
import { TONE_NAMES, phraseEl } from './glyph';
import { openModal } from './modal';

/** The card of a single character: the player's note, and after confirmation — meaning, sound, origin. */
export function openGlyphCard(app: App, g: Glyph, _anchor?: HTMLElement): void {
  const s = app.state;
  const def = glyphDef(g);
  const confirmed = !!s.confirmed[g];

  const input = h('input', {
    class: 'guess-input',
    type: 'text',
    maxLength: MAX_GUESS,
    placeholder: confirmed ? 'Ваша заметка…' : 'Что это может значить?',
    value: s.guesses[g] ?? '',
    'aria-label': 'Догадка',
    autocomplete: 'off',
    spellcheck: false,
  });
  input.addEventListener('input', () => {
    setGuess(s, g, input.value);
    app.changed();
  });
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handle.close();
  });

  const speak = h('button', { class: 'speak', 'aria-label': 'Произнести', title: 'Произнести', onclick: () => app.audio.speak(g, 0.7) }, '🔊');

  const head = h(
    'div',
    { class: 'card-head' },
    h('div', { class: `card-glyph${confirmed ? ' confirmed' : ''}` }, g),
    h(
      'div',
      { class: 'card-meta' },
      confirmed && def ? h('div', { class: `card-pinyin t${def.tone}` }, def.pinyin, ' ', speak) : h('div', { class: 'card-pinyin muted' }, 'звучание ', speak),
      confirmed && def ? h('div', { class: 'card-meaning' }, def.meaning) : h('div', { class: 'card-meaning muted' }, 'значение не подтверждено'),
      confirmed && def ? h('div', { class: 'card-tone muted' }, `тон: ${TONE_NAMES[def.tone]}`) : null,
    ),
  );

  const body = h('div', { class: 'glyph-card' }, head, h('label', { class: 'guess-label' }, confirmed ? 'Ваша заметка' : 'Ваша догадка', input));

  if (confirmed && def) {
    const ancient = ancientForm(g);
    body.append(
      h('div', { class: 'card-origin' }, ancient ? h('span', { class: 'ancient-box', title: 'Древняя форма', html: ancient }) : null, h('p', {}, def.origin)),
      h(
        'ul',
        { class: 'card-words' },
        ...def.words.map(([zh, py, ru]) => h('li', {}, h('button', { class: 'word-say', title: 'Произнести', onclick: () => app.audio.speak(zh, 0.75) }, zh), ' ', h('span', { class: 'word-py' }, py), ' — ', ru)),
      ),
    );
  } else {
    const page = PAGES.find((p) => p.glyphs.includes(g));
    const note = page
      ? `Знак подтверждается на странице дневника «${page.title}». Соберите все её знаки и разложите их по рисункам.`
      : recipeFor(g)
        ? 'Этот знак можно собрать из других — как рисунок из частей.'
        : '';
    if (note) body.append(h('p', { class: 'card-note muted' }, note));
  }

  const lines = s.log.filter((l) => l.text.includes(g)).slice(-4);
  if (lines.length) {
    body.append(h('div', { class: 'card-lines' }, h('div', { class: 'muted small' }, 'Где встречался:'), ...lines.map((l) => h('div', { class: 'card-line' }, phraseEl(app, l.text, { interactive: false, size: 'sm' })))));
  }

  const handle = openModal(app.overlay, body, { className: 'card' });
  if (!('ontouchstart' in window)) setTimeout(() => input.focus(), 50);
}

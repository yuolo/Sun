import { glyphDef } from '../content/lexicon';
import { MIN_REVIEW, makeQuestion, type ReviewQuestion } from '../core/review';
import type { Glyph } from '../core/types';
import type { App } from './app';
import { h } from './dom';

/** Multiple-choice review of the confirmed characters. */
export function flashcards(app: App): HTMLElement {
  const pool = Object.keys(app.state.confirmed);
  const wrap = h('div', { class: 'review' });
  if (pool.length < MIN_REVIEW) {
    wrap.append(h('p', { class: 'empty-note' }, `Повторение откроется, когда будет подтверждено хотя бы ${MIN_REVIEW} знака. Сейчас: ${pool.length}.`));
    return wrap;
  }
  let right = 0;
  let total = 0;
  let prev: Glyph | undefined;

  const ask = () => {
    const q = makeQuestion(pool, Math.random, prev) as ReviewQuestion;
    prev = q.glyph;
    const def = glyphDef(q.glyph)!;
    const score = h('div', { class: 'review-score' }, total ? `Верно ${right} из ${total}` : 'Выберите правильный ответ');
    const prompt =
      q.mode === 'glyph-to-meaning'
        ? h('div', { class: 'review-prompt' }, h('div', { class: 'review-glyph' }, q.glyph), h('button', { class: 'speak', 'aria-label': 'Произнести', onclick: () => app.audio.speak(q.glyph, 0.7) }, '🔊'))
        : h('div', { class: 'review-prompt' }, h('div', { class: 'review-meaning' }, def.meaning));
    const feedback = h('div', { class: 'review-feedback', 'aria-live': 'polite' });
    const options = h('div', { class: `review-options ${q.mode}` });
    for (const o of q.options) {
      const label = q.mode === 'glyph-to-meaning' ? glyphDef(o)!.meaning : o;
      const b = h('button', { class: 'review-option' }, label);
      b.addEventListener('click', () => {
        if (options.classList.contains('answered')) return;
        options.classList.add('answered');
        total++;
        const ok = o === q.glyph;
        if (ok) right++;
        b.classList.add(ok ? 'right' : 'wrong');
        options.querySelectorAll('button').forEach((x, i) => {
          if (q.options[i] === q.glyph) x.classList.add('right');
        });
        app.audio.sfx(ok ? 'confirm' : 'wrong');
        app.audio.speak(q.glyph, 0.7);
        feedback.replaceChildren(h('span', { class: 'zh' }, q.glyph), ' ', h('span', { class: `t${def.tone}` }, def.pinyin), ' — ', def.meaning, ' ', h('button', { class: 'primary', onclick: ask }, 'Дальше →'));
        score.textContent = `Верно ${right} из ${total}`;
      });
      options.append(b);
    }
    wrap.replaceChildren(score, prompt, options, feedback);
  };
  ask();
  return wrap;
}

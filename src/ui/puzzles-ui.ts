import { ancientForm } from '../art/ancient';
import { BELL_PICTURES, tabletPicture } from '../art/illustrations';
import { cup as cupArt } from '../art/kit';
import { RECIPES, recipeFor, type Layout } from '../content/recipes';
import { confirmGlyphs, seenGlyphs } from '../core/journal';
import { ANCIENT_SET, BELLS, BELL_CHANT, MAX_TRAY, addCup, checkAncient, compose, ringBell } from '../core/puzzles';
import type { ComposeRequest, Cup, CupSize, Drink, Glyph } from '../core/types';
import type { App } from './app';
import { h, sleep, svgEl } from './dom';
import { glyphEl } from './glyph';
import { openModal } from './modal';
import { openComposer } from './composer-ui';

function modalPromise<T>(app: App, title: string, cls: string, build: (finish: (v: T) => void) => HTMLElement, onCancel: T): Promise<T> {
  let result = onCancel;
  let resolve!: (v: T) => void;
  const done = new Promise<T>((r) => (resolve = r));
  const finish = (v: T) => {
    result = v;
    handle.close();
  };
  const body = build(finish);
  const handle = openModal(app.overlay, body, { title, className: `puzzle ${cls}`, onClose: () => resolve(result) });
  return done;
}

/* ------------------------------------------------------------------ */
/* Tea tray                                                            */
/* ------------------------------------------------------------------ */

const cupSvg = (size: CupSize, drink?: Drink) =>
  svgEl(`<svg viewBox="-30 -34 60 40" class="cup-svg ${size}">${cupArt(0, 0, size === 'big', '#efe7d4', drink === 'tea' ? '#9a7a3a' : drink === 'water' ? '#8ec3dd' : undefined)}</svg>`);

export function openTray(app: App): Promise<Cup[] | null> {
  return modalPromise<Cup[] | null>(app, 'Поднос', 'tray-puzzle', (finish) => {
    let cups: Cup[] = [...app.state.tray];
    let drink: Drink | null = null;
    const trayEl = h('div', { class: 'tray' });
    const jars = h('div', { class: 'jars' });
    const sizes = h('div', { class: 'sizes' });
    const hint = h('p', { class: 'muted small' });

    const render = () => {
      jars.replaceChildren(
        ...(['tea', 'water'] as Drink[]).map((d) => {
          const label = d === 'tea' ? '茶' : '水';
          const b = h(
            'button',
            { class: `jar${drink === d ? ' selected' : ''}`, 'aria-label': `Кувшин с надписью ${label}` },
            svgEl('<svg viewBox="0 0 80 100" class="jar-svg"><path d="M22 18 Q-4 48 16 96 L64 96 Q84 48 58 18 Z" fill="#e9e2cf" stroke="#9a8f78" stroke-width="2"/><path d="M8 52 Q40 58 72 52" stroke="#4c6c8c" stroke-width="3" fill="none"/><rect x="26" y="6" width="28" height="14" rx="3" fill="#4c6c8c"/></svg>'),
            glyphEl(app, label, { size: 'md', subtitle: true }),
          );
          b.addEventListener('click', () => {
            drink = d;
            app.audio.sfx('click');
            render();
          });
          return b;
        }),
      );
      sizes.replaceChildren(
        ...(['big', 'small'] as CupSize[]).map((sz) => {
          const b = h('button', { class: 'cup-btn', disabled: !drink || cups.length >= MAX_TRAY, 'aria-label': sz === 'big' ? 'Большая чашка' : 'Маленькая чашка' }, cupSvg(sz));
          b.addEventListener('click', () => {
            if (!drink) return;
            cups = addCup(cups, { drink, size: sz });
            app.audio.sfx('pour');
            render();
          });
          return b;
        }),
      );
      trayEl.replaceChildren(
        ...cups.map((c, i) => {
          const b = h('button', { class: 'tray-cup', 'aria-label': 'Убрать чашку' }, cupSvg(c.size, c.drink));
          b.addEventListener('click', () => {
            cups = cups.filter((_, k) => k !== i);
            render();
          });
          return b;
        }),
      );
      if (!cups.length) trayEl.append(h('span', { class: 'muted' }, 'пусто'));
      hint.textContent = drink ? 'Теперь выберите чашку — она наполнится из выбранного кувшина. Нажмите на чашку на подносе, чтобы убрать её.' : 'Выберите кувшин.';
    };
    render();
    return h(
      'div',
      { class: 'tray-body' },
      h('div', { class: 'tray-top' }, jars, sizes),
      hint,
      h('div', { class: 'tray-wrap' }, trayEl),
      h('div', { class: 'actions' }, h('button', { class: 'ghost', onclick: () => ((cups = []), render()) }, 'Очистить'), h('button', { class: 'primary', onclick: () => finish(cups) }, 'Взять поднос')),
    );
  }, null);
}

/* ------------------------------------------------------------------ */
/* Bells                                                               */
/* ------------------------------------------------------------------ */

export function openBells(app: App): Promise<boolean> {
  return modalPromise<boolean>(app, 'Колокола', 'bells-puzzle', (finish) => {
    let progress = 0;
    const dots = h('div', { class: 'bell-dots', 'aria-hidden': 'true' });
    const msg = h('p', { class: 'bell-msg', 'aria-live': 'polite' }, 'Ударьте в колокола.');
    const renderDots = () => dots.replaceChildren(...BELL_CHANT.map((_, i) => h('i', { class: i < progress ? 'on' : '' })));
    const rack = h('div', { class: 'bell-rack' });
    BELLS.forEach((bell, i) => {
      const b = h('button', { class: 'bell-btn', 'aria-label': `Колокол ${i + 1}` }, h('span', { class: 'bell-shape' }, h('span', { class: 'bell-pic', html: `<svg viewBox="0 0 100 100">${BELL_PICTURES[bell]()}</svg>` })));
      b.addEventListener('click', async () => {
        if (rack.classList.contains('solved')) return;
        app.audio.bell(i);
        b.classList.remove('ring');
        void b.offsetWidth;
        b.classList.add('ring');
        const r = ringBell(progress, bell);
        progress = r.progress;
        renderDots();
        if (r.result === 'wrong') {
          msg.textContent = 'Звон рассыпается. Начните сначала.';
          rack.classList.remove('shake');
          void rack.offsetWidth;
          rack.classList.add('shake');
          app.audio.sfx('wrong');
        } else if (r.result === 'restart') {
          msg.textContent = 'Начало заново…';
        } else if (r.result === 'progress') {
          msg.textContent = '…';
        } else {
          rack.classList.add('solved');
          msg.textContent = 'Звон сливается в одну ноту.';
          await sleep(1400);
          finish(true);
        }
      });
      rack.append(b);
    });
    renderDots();
    const board = h('div', { class: 'chant-board' }, ...BELL_CHANT.map((g) => glyphEl(app, g, { size: 'lg' })));
    return h('div', { class: 'bells-body' }, h('div', { class: 'bells-layout' }, rack, board), dots, msg);
  }, false);
}

/* ------------------------------------------------------------------ */
/* Building characters                                                 */
/* ------------------------------------------------------------------ */

export function openCompose(app: App, req: ComposeRequest): Promise<Glyph[]> {
  const made: Glyph[] = [];
  return modalPromise<Glyph[]>(app, 'Сложите знак', 'compose-puzzle', (finish) => {
    let parts: (Glyph | null)[] = [null, null];
    let layout: Layout = 'lr';
    const tablets = h('div', { class: 'tablets' });
    const slots = h('div', { class: 'part-slots' });
    const preview = h('div', { class: 'compose-preview' });
    const msg = h('p', { class: 'compose-msg', 'aria-live': 'polite' });
    const palette = h('div', { class: 'palette' });

    const renderTablets = () =>
      tablets.replaceChildren(
        ...req.targets.map((t) => {
          const r = recipeFor(t);
          const ok = made.includes(t);
          return h(
            'div',
            { class: `tablet${ok ? ' done' : ''}` },
            h('div', { class: 'tablet-pic', html: `<svg viewBox="0 0 100 100">${tabletPicture(t)}</svg>` }),
            h('div', { class: 'tablet-caption' }, r?.caption ?? ''),
            h('div', { class: 'tablet-slot' }, ok ? glyphEl(app, t, { size: 'lg' }) : h('span', { class: 'slot-empty' }, '？')),
          );
        }),
      );

    const renderParts = () => {
      slots.replaceChildren(
        ...parts.map((p, i) => {
          const b = h('button', { class: `part-slot${p ? ' filled' : ''}`, 'aria-label': p ? `Убрать ${p}` : 'Пустая часть' }, p ? glyphEl(app, p, { interactive: false, size: 'lg' }) : h('span', { class: 'slot-empty' }, i === 0 ? (layout === 'lr' ? 'левая' : 'верхняя') : layout === 'lr' ? 'правая' : 'нижняя'));
          b.addEventListener('click', () => {
            parts[i] = null;
            renderParts();
          });
          return b;
        }),
      );
      slots.classList.toggle('tb', layout === 'tb');
      preview.className = `compose-preview ${layout}`;
      preview.replaceChildren(...parts.map((p) => h('span', {}, p ?? '')));
      layoutBtns.forEach(([l, b]) => b.classList.toggle('active', l === layout));
    };

    const layoutBtns: [Layout, HTMLButtonElement][] = [
      ['lr', h('button', { class: 'ghost', title: 'Рядом', onclick: () => ((layout = 'lr'), renderParts()) }, '⇆ рядом')],
      ['tb', h('button', { class: 'ghost', title: 'Друг над другом', onclick: () => ((layout = 'tb'), renderParts()) }, '⇅ одна над другой')],
    ];

    const tryCompose = async () => {
      const [a, b] = parts;
      if (!a || !b) {
        msg.textContent = 'Нужны две части.';
        return;
      }
      const result = compose(a, b, layout);
      if (result && req.targets.includes(result) && !made.includes(result)) {
        made.push(result);
        app.audio.sfx('confirm');
        preview.replaceChildren(h('span', { class: 'result' }, result));
        preview.classList.add('merged');
        msg.textContent = `${a} + ${b} = ${result}`;
        confirmGlyphs(app.state, [result]);
        app.changed();
        app.audio.speak(result, 0.7);
        renderTablets();
        parts = [null, null];
        if (made.length === req.targets.length) {
          await sleep(1800);
          finish(made);
        } else {
          await sleep(1200);
          preview.classList.remove('merged');
          renderParts();
        }
        return;
      }
      app.audio.sfx('wrong');
      preview.classList.remove('shake');
      void preview.offsetWidth;
      preview.classList.add('shake');
      msg.textContent = result && made.includes(result) ? 'Этот знак уже сложен.' : 'Не похоже на рисунок на табличке.';
    };

    const pool = new Set<Glyph>(seenGlyphs(app.state));
    for (const r of RECIPES) if (req.targets.includes(r.result)) for (const p of [r.a, r.b]) if (app.state.seen[p]) pool.add(p);
    for (const g of pool) {
      if (req.targets.includes(g) && !app.state.confirmed[g]) continue;
      const b = h('button', { class: 'palette-glyph', 'aria-label': `Часть ${g}` }, glyphEl(app, g, { interactive: false, size: 'md' }));
      b.addEventListener('click', () => {
        const i = parts[0] === null ? 0 : parts[1] === null ? 1 : 1;
        parts[i] = g;
        app.audio.sfx('click');
        renderParts();
      });
      palette.append(b);
    }

    renderTablets();
    renderParts();
    return h(
      'div',
      { class: 'compose-body' },
      tablets,
      h('p', { class: 'muted small' }, 'Выберите две части, их расположение, и сложите знак, который подходит к рисунку.'),
      h('div', { class: 'compose-work' }, slots, h('div', { class: 'layout-btns' }, ...layoutBtns.map(([, b]) => b)), preview, h('button', { class: 'primary', onclick: tryCompose }, 'Сложить')),
      msg,
      palette,
    );
  }, made);
}

/* ------------------------------------------------------------------ */
/* Wordless stele                                                      */
/* ------------------------------------------------------------------ */

export function openStele(app: App): Promise<string> {
  return openComposer(app, {
    title: 'Стела без надписей',
    description: 'Гладкий камень высотой в шесть метров. Говорят, его поставил император — и не оставил на нём ни слова. Можете высечь свои.',
    max: 8,
    submit: 'Высечь',
    cancel: 'Уйти',
    initial: app.state.inscription,
  });
}

/* ------------------------------------------------------------------ */
/* Ancient stele                                                       */
/* ------------------------------------------------------------------ */

export function openAncient(app: App): Promise<boolean> {
  return modalPromise<boolean>(app, 'Стела Цинь', 'ancient-puzzle', (finish) => {
    const order = [...ANCIENT_SET].sort((a, b) => (a.charCodeAt(0) * 7) % 13 - (b.charCodeAt(0) * 7) % 13);
    const poolOrder = [...ANCIENT_SET].reverse();
    const pairs: Record<Glyph, Glyph | undefined> = {};
    let picked: Glyph | null = null;
    const cards = h('div', { class: 'ancient-cards' });
    const pool = h('div', { class: 'pool' });
    const msg = h('p', { class: 'compose-msg', 'aria-live': 'polite' });

    const render = () => {
      cards.replaceChildren(
        ...order.map((a) => {
          const m = pairs[a];
          const b = h('button', { class: `ancient-card${m ? ' filled' : ''}`, 'aria-label': 'Древний знак' }, h('span', { class: 'ancient-box big', html: ancientForm(a) ?? '' }), h('span', { class: 'ancient-slot' }, m ? glyphEl(app, m, { interactive: false, size: 'md' }) : '？'));
          b.addEventListener('click', () => {
            if (picked) {
              for (const k of Object.keys(pairs)) if (pairs[k] === picked) pairs[k] = undefined;
              pairs[a] = picked;
              picked = null;
              app.audio.sfx('click');
            } else pairs[a] = undefined;
            render();
            check();
          });
          return b;
        }),
      );
      const used = new Set(Object.values(pairs));
      pool.replaceChildren(
        ...poolOrder.map((g) => {
          const b = h('button', { class: `pool-glyph${used.has(g) ? ' used' : ''}${picked === g ? ' selected' : ''}`, disabled: used.has(g) }, glyphEl(app, g, { interactive: false, size: 'lg' }));
          b.addEventListener('click', () => {
            picked = picked === g ? null : g;
            render();
          });
          return b;
        }),
      );
    };

    const check = async () => {
      if (!order.every((a) => pairs[a])) {
        msg.textContent = '';
        return;
      }
      if (checkAncient(pairs)) {
        msg.textContent = 'Две тысячи лет — а знаки всё те же.';
        app.audio.sfx('confirm');
        cards.classList.add('solved');
        await sleep(1600);
        finish(true);
      } else {
        msg.textContent = 'Не всё сходится.';
        app.audio.sfx('wrong');
        cards.classList.remove('shake');
        void cards.offsetWidth;
        cards.classList.add('shake');
      }
    };

    render();
    return h('div', { class: 'ancient-body' }, h('p', { class: 'muted' }, 'Обломок стелы с надписью времён первого императора Цинь. Черты стёрлись и выглядят иначе — но это знаки, которые вы уже знаете. Сопоставьте древние формы с нынешними.'), cards, msg, pool);
  }, false);
}

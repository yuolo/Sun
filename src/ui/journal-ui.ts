import { illustration } from '../art/illustrations';
import { GRAMMAR } from '../content/grammar';
import { LEXICON, glyphDef } from '../content/lexicon';
import { PAGES } from '../content/pages';
import { SCENES } from '../content/world';
import { grammarUnlocked, missingCount, pageStatus, place, placementsFor, poolOrder, progress, seenGlyphs, submitPage } from '../core/journal';
import type { Glyph } from '../core/types';
import type { App } from './app';
import { h, icon } from './dom';
import { glyphEl, phraseEl } from './glyph';
import { openModal, type ModalHandle } from './modal';
import { flashcards } from './review';

export type JournalTab = 'glyphs' | 'pages' | 'lines' | 'grammar' | 'review';

const TABS: [JournalTab, string][] = [
  ['glyphs', 'Знаки'],
  ['pages', 'Страницы'],
  ['lines', 'Фразы'],
  ['grammar', 'Грамматика'],
  ['review', 'Повторение'],
];

export function openJournal(app: App, tab: JournalTab = 'glyphs', pageId?: string): ModalHandle {
  const content = h('div', { class: 'journal-content' });
  const tabs = h('nav', { class: 'journal-tabs', role: 'tablist' });
  const stats = h('div', { class: 'journal-stats' });
  const root = h('div', { class: 'journal' }, h('header', { class: 'journal-head' }, h('h2', {}, '笔记', h('span', {}, ' · Дневник')), stats), tabs, content);
  let current = tab;

  const render = () => {
    const p = progress(app.state);
    stats.textContent = `Встречено ${p.seen} · подтверждено ${p.confirmed} из ${p.total}`;
    tabs.replaceChildren(
      ...TABS.map(([id, label]) => {
        const badge = id === 'pages' && PAGES.some((pg) => pageStatus(app.state, pg) === 'open') ? h('i', { class: 'badge' }) : null;
        return h('button', { class: `tab${id === current ? ' active' : ''}`, role: 'tab', 'aria-selected': String(id === current), onclick: () => show(id) }, label, badge);
      }),
    );
  };

  const show = (id: JournalTab, pid?: string) => {
    current = id;
    render();
    content.replaceChildren();
    content.scrollTop = 0;
    if (id === 'glyphs') content.append(glyphsTab(app));
    else if (id === 'pages') content.append(pid ? pageView(app, pid, () => show('pages'), render) : pagesTab(app, (x) => show('pages', x)));
    else if (id === 'lines') content.append(linesTab(app));
    else if (id === 'grammar') content.append(grammarTab(app));
    else content.append(flashcards(app));
  };

  const handle = openModal(app.overlay, root, { className: 'journal-modal' });
  app.audio.sfx('page');
  show(tab, pageId);
  const off = app.onChange(render);
  void handle.closed.then(off);
  return handle;
}

function glyphsTab(app: App): HTMLElement {
  const seen = seenGlyphs(app.state);
  if (!seen.length) return h('p', { class: 'empty-note' }, 'Пока здесь пусто. Кликайте по людям и надписям — каждый встреченный знак попадёт в дневник.');
  const grid = h('div', { class: 'glyph-grid' });
  for (const g of seen) grid.append(h('div', { class: `glyph-tile${app.state.confirmed[g] ? ' done' : ''}` }, glyphEl(app, g, { size: 'lg' })));
  const unseen = LEXICON.length - seen.length;
  return h('div', {}, h('p', { class: 'muted small' }, 'Нажмите на знак, чтобы записать догадку. Подтверждённые знаки получают значение, звучание и историю.'), grid, unseen ? h('p', { class: 'muted small center' }, `Ещё не встречено знаков: ${unseen}`) : null);
}

function pagesTab(app: App, openPage: (id: string) => void): HTMLElement {
  const list = h('div', { class: 'page-list' });
  for (const p of PAGES) {
    const st = pageStatus(app.state, p);
    const miss = missingCount(app.state, p);
    const preview = h('div', { class: 'page-preview' }, ...p.glyphs.map((g) => h('span', { class: app.state.seen[g] ? 'pg seen' : 'pg' }, app.state.seen[g] ? g : '？')));
    const label = st === 'done' ? '✓ подтверждено' : st === 'open' ? 'можно заполнить' : `не хватает знаков: ${miss}`;
    list.append(
      h(
        'button',
        { class: `page-item ${st}`, disabled: st === 'locked', onclick: () => openPage(p.id) },
        h('span', { class: 'page-title' }, p.title),
        preview,
        h('span', { class: 'page-state' }, label),
      ),
    );
  }
  return h('div', {}, h('p', { class: 'muted small' }, 'Страница открывается, когда вы встретили все её знаки. Разложите знаки по рисункам — страница засчитывается, только если всё верно.'), list);
}

function pageView(app: App, pageId: string, back: () => void, rerenderTabs: () => void): HTMLElement {
  const page = PAGES.find((p) => p.id === pageId)!;
  const wrap = h('div', { class: 'page-view' });
  let selected: Glyph | null = null;
  let selectedSlot: number | null = null;

  const render = () => {
    const s = app.state;
    const done = pageStatus(s, page) === 'done';
    const placed = done ? [...page.glyphs] : placementsFor(s, page);
    wrap.replaceChildren();
    wrap.append(
      h('div', { class: 'page-bar' }, h('button', { class: 'link', onclick: back }, '← Все страницы'), h('h3', {}, `«${page.title}»`)),
      h('p', { class: 'muted small' }, done ? 'Страница подтверждена. Нажмите на знак, чтобы услышать его и прочитать историю.' : 'Выберите знак внизу и нажмите на рисунок, к которому он относится.'),
    );
    const grid = h('div', { class: `page-grid n${page.glyphs.length}${done ? ' done' : ''}` });
    page.glyphs.forEach((answer, i) => {
      const g = placed[i];
      const slot = h(
        'div',
        {
          class: `slot${g ? ' filled' : ''}${selectedSlot === i ? ' selected' : ''}`,
          role: 'button',
          tabIndex: 0,
          'aria-label': g ? `Ячейка ${i + 1}: ${g}` : `Ячейка ${i + 1}: пусто`,
        },
        g ? glyphEl(app, g, { interactive: done, size: 'lg' }) : h('span', { class: 'slot-empty' }, '？'),
      );
      if (!done) {
        slot.addEventListener('click', () => {
          if (g && selected === null) {
            place(s, page, i, null);
            selectedSlot = null;
          } else if (selected !== null) {
            place(s, page, i, selected);
            selected = null;
            selectedSlot = null;
            app.audio.sfx('click');
          } else {
            selectedSlot = selectedSlot === i ? null : i;
          }
          app.save();
          afterChange();
        });
      }
      grid.append(h('div', { class: 'slot-card' }, h('div', { class: 'slot-pic', html: `<svg viewBox="0 0 100 100">${illustration(answer)}</svg>` }), slot, done ? h('div', { class: 'slot-meaning' }, glyphDef(answer)?.meaning ?? '') : null));
    });
    wrap.append(grid);
    if (!done) {
      const pool = h('div', { class: 'pool' });
      for (const g of poolOrder(page)) {
        const used = placed.includes(g);
        const b = h('button', { class: `pool-glyph${used ? ' used' : ''}${selected === g ? ' selected' : ''}`, disabled: used, 'aria-label': `Знак ${g}` }, glyphEl(app, g, { interactive: false, size: 'lg' }));
        b.addEventListener('click', () => {
          if (selectedSlot !== null) {
            place(s, page, selectedSlot, g);
            selectedSlot = null;
            selected = null;
            app.audio.sfx('click');
            app.save();
            afterChange();
            return;
          }
          selected = selected === g ? null : g;
          render();
        });
        pool.append(b);
      }
      wrap.append(pool, h('div', { class: 'page-msg', 'aria-live': 'polite' }));
    }
  };

  const afterChange = () => {
    const placed = placementsFor(app.state, page);
    render();
    if (!placed.every((g) => g !== null)) return;
    const before = new Set(grammarUnlocked(app.state).map((g) => g.id));
    const res = submitPage(app.state, page);
    const msg = wrap.querySelector('.page-msg');
    if (res.correct) {
      app.audio.sfx('confirm');
      app.changed();
      rerenderTabs();
      render();
      wrap.classList.add('stamped');
      wrap.append(h('div', { class: 'seal', 'aria-hidden': 'true' }, '好'));
      app.toast(h('span', {}, 'Подтверждено: ', h('b', { class: 'zh' }, res.confirmed.join(' '))), 'ok');
      for (const note of grammarUnlocked(app.state)) if (!before.has(note.id)) app.toast(h('span', {}, 'Новая заметка о грамматике: ', h('b', {}, note.title)), 'page');
      page.glyphs.forEach((g, i) => setTimeout(() => app.audio.speak(g, 0.75), 700 + i * 900));
    } else {
      app.audio.sfx('wrong');
      wrap.querySelector('.page-grid')?.classList.add('shake');
      if (msg) msg.textContent = res.wrong <= 2 ? 'Почти… но что-то не сходится.' : 'Не сходится. Пересмотрите свои догадки.';
    }
  };

  render();
  return wrap;
}

function linesTab(app: App): HTMLElement {
  const log = app.state.log;
  if (!log.length) return h('p', { class: 'empty-note' }, 'Здесь будут все услышанные фразы. Сравнивайте их — одинаковые знаки в разных фразах подскажут значение.');
  const names = new Map<string, string>();
  for (const sc of SCENES) for (const a of sc.actors) names.set(`${sc.id}:${a.id}`, a.name);
  const groups = new Map<string, typeof log>();
  for (const l of log) {
    if (!groups.has(l.scene)) groups.set(l.scene, []);
    groups.get(l.scene)!.push(l);
  }
  const wrap = h('div', { class: 'lines' });
  for (const [sceneId, lines] of groups) {
    const title = SCENES.find((s) => s.id === sceneId)?.title ?? sceneId;
    wrap.append(h('h4', {}, title));
    for (const l of lines) {
      wrap.append(
        h(
          'div',
          { class: 'line' },
          h('span', { class: 'who' }, names.get(`${sceneId}:${l.who}`) ?? l.who),
          phraseEl(app, l.text, { size: 'md' }),
          h('button', { class: 'speak small', title: 'Произнести', 'aria-label': 'Произнести', onclick: () => app.audio.speak(l.text, 0.8) }, '🔊'),
        ),
      );
    }
  }
  return wrap;
}

function grammarTab(app: App): HTMLElement {
  const open = grammarUnlocked(app.state);
  const wrap = h('div', { class: 'grammar' });
  if (!open.length) wrap.append(h('p', { class: 'empty-note' }, 'Заметки о грамматике откроются, когда вы подтвердите первые знаки.'));
  for (const note of open) {
    wrap.append(
      h(
        'article',
        { class: 'note' },
        h('h4', {}, note.title),
        h('p', {}, note.text),
        h('ul', {}, ...note.examples.map(([zh, ru]) => h('li', {}, phraseEl(app, zh, { size: 'sm' }), h('span', { class: 'ru' }, ru)))),
      ),
    );
  }
  const locked = GRAMMAR.length - open.length;
  if (locked) wrap.append(h('p', { class: 'muted small center' }, `Ещё заметок: ${locked}`));
  return wrap;
}

export const journalIcon = () =>
  icon('<path d="M18 14 H74 Q84 14 84 24 V88 H26 Q18 88 18 80 Z" fill="#8a4a2a"/><path d="M26 22 H76 V80 H26 Z" fill="#f4ead2"/><path d="M34 36 H66 M34 48 H66 M34 60 H56" stroke="#8a4a2a" stroke-width="5" stroke-linecap="round"/>');

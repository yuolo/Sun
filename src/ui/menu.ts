import { ART } from '../art/scenes';
import { LEXICON } from '../content/lexicon';
import { PAGES } from '../content/pages';
import { progress } from '../core/journal';
import { MIN_REVIEW } from '../core/review';
import { createState } from '../core/state';
import type { ChapterDef, Settings } from '../core/types';
import type { App } from './app';
import { h, sleep } from './dom';
import { phraseEl } from './glyph';
import { openModal } from './modal';

/* ------------------------------------------------------------------ */
/* Title screen                                                        */
/* ------------------------------------------------------------------ */

export interface TitleActions {
  onContinue: () => void;
  onNew: () => void;
}

export function titleScreen(app: App, actions: TitleActions): HTMLElement {
  const s = createState();
  s.flags.sunrise = true;
  const art = ART.sunpeak(s, { time: 'dawn' });
  const hasSave = app.hasSave() && app.state.px >= 0;
  const p = progress(app.state);
  const el = h(
    'div',
    { class: 'title-screen' },
    h('div', { class: 'title-art', html: art }),
    h('div', { class: 'title-shade' }),
    h(
      'div',
      { class: 'title-box' },
      h('h1', { class: 'title-zh' }, '日出', h('span', { class: 'seal-small' }, '山')),
      h('p', { class: 'title-ru' }, 'Восход'),
      h('p', { class: 'title-sub' }, 'Путь на гору Тайшань — и ещё полсотни иероглифов'),
      h(
        'div',
        { class: 'title-buttons' },
        hasSave ? h('button', { class: 'primary big', onclick: actions.onContinue }, 'Продолжить', h('small', {}, `подтверждено ${p.confirmed} из ${p.total}`)) : null,
        h(
          'button',
          {
            class: hasSave ? 'big' : 'primary big',
            onclick: () => {
              if (!hasSave) return actions.onNew();
              confirmNew(app, actions.onNew);
            },
          },
          'Новая игра',
        ),
        h('button', { onclick: () => howToPlay(app) }, 'Как играть'),
        h('button', { onclick: () => settingsDialog(app) }, 'Настройки'),
        Object.keys(app.state.confirmed).length >= MIN_REVIEW ? h('button', { onclick: () => app.openJournal('review') }, 'Повторение') : null,
      ),
      h('p', { class: 'title-foot' }, 'Игра-расшифровка по мотивам Chants of Sennaar. Ни одного перевода — только контекст, догадки и дневник.'),
    ),
  );
  return el;
}

function confirmNew(app: App, onNew: () => void): void {
  const body = h(
    'div',
    {},
    h('p', {}, 'Начать заново? Текущий прогресс и дневник будут стёрты.'),
    h('div', { class: 'actions' }, h('button', { class: 'ghost', onclick: () => m.close() }, 'Отмена'), h('button', { class: 'primary', onclick: () => (m.close(), onNew()) }, 'Начать заново')),
  );
  const m = openModal(app.overlay, body, { title: 'Новая игра', className: 'small' });
}

/* ------------------------------------------------------------------ */
/* Help and settings                                                   */
/* ------------------------------------------------------------------ */

export function howToPlay(app: App): void {
  const items = [
    ['Ходите', 'Кликните по земле, чтобы идти. По человеку — чтобы заговорить. По предмету — чтобы взять или осмотреть. Стрелки у краёв экрана ведут дальше.'],
    ['Записывайте догадки', 'Все реплики и надписи — на китайском. Нажмите на любой знак и запишите, что он, по-вашему, значит. Догадка появится под знаком везде, где он встречается.'],
    ['Подтверждайте', 'Когда вы встретите все знаки одной страницы дневника, разложите их по рисункам. Если всё верно — знаки подтвердятся: вы узнаете значение, пиньинь и услышите звучание.'],
    ['Отвечайте', 'Иногда вас спросят. Составьте ответ из знаков, которые уже встречали.'],
    ['Используйте вещи', 'Выберите предмет в сумке (внизу слева), затем кликните по человеку или объекту.'],
    ['Не спешите', 'Сравнивайте фразы в дневнике: один и тот же знак в разных фразах — лучшая подсказка. Если застряли — кнопка «?».'],
  ];
  const body = h(
    'div',
    { class: 'howto' },
    ...items.map(([t, d]) => h('div', { class: 'howto-item' }, h('h4', {}, t), h('p', {}, d))),
    h('p', { class: 'muted small' }, 'Клавиши: J — дневник, H — подсказка, Пробел — дальше, Esc — меню. Тоны пиньиня раскрашены: 1 — красный, 2 — зелёный, 3 — синий, 4 — фиолетовый.'),
  );
  openModal(app.overlay, body, { title: 'Как играть' });
}

export function settingsDialog(app: App): void {
  const rows: [keyof Settings, string, string][] = [
    ['pinyin', 'Пиньинь', 'над подтверждёнными знаками'],
    ['guesses', 'Подписи', 'ваши догадки под знаками'],
    ['voice', 'Голос', 'озвучка реплик и знаков (если браузер умеет говорить по-китайски)'],
    ['music', 'Музыка', 'тихая пентатоника'],
    ['sfx', 'Звуки', 'колокола, шаги, вода'],
  ];
  const body = h(
    'div',
    { class: 'settings' },
    ...rows.map(([key, label, note]) => {
      const input = h('input', { type: 'checkbox', checked: app.state.settings[key] });
      input.addEventListener('change', () => {
        app.state.settings[key] = input.checked;
        app.audio.applySettings();
        app.changed();
      });
      return h('label', { class: 'setting' }, input, h('span', {}, h('b', {}, label), h('small', {}, note)));
    }),
    app.audio.canSpeak() ? null : h('p', { class: 'muted small' }, 'Похоже, в этом браузере нет китайского голоса — пиньинь всё равно покажет звучание.'),
  );
  openModal(app.overlay, body, { title: 'Настройки', className: 'small' });
}

export function pauseMenu(app: App, onMain: () => void): void {
  const body = h(
    'div',
    { class: 'pause' },
    h('button', { class: 'primary', onclick: () => m.close() }, 'Продолжить'),
    h('button', { onclick: () => (m.close(), app.openJournal()) }, 'Дневник'),
    h('button', { onclick: () => (m.close(), app.showHint()) }, 'Подсказка'),
    h('button', { onclick: () => howToPlay(app) }, 'Как играть'),
    h('button', { onclick: () => settingsDialog(app) }, 'Настройки'),
    h('button', { class: 'ghost', onclick: () => (m.close(), app.saveNow(), onMain()) }, 'Главное меню'),
    h('p', { class: 'muted small center' }, 'Прогресс сохраняется автоматически.'),
  );
  const m = openModal(app.overlay, body, { title: 'Пауза', className: 'small' });
}

/* ------------------------------------------------------------------ */
/* Prologue and chapter cards                                          */
/* ------------------------------------------------------------------ */

export async function prologue(host: HTMLElement): Promise<void> {
  const lines = [
    'Говорят, тот, кто встретит рассвет на вершине Тайшань, проживёт долгую жизнь.',
    'Вы пришли издалека — вверх по реке, на лодке.',
    'Вы не знаете здешнего языка. Но у вас есть дневник.',
  ];
  const el = h('div', { class: 'prologue' }, ...lines.map((l) => h('p', {}, l)), h('p', { class: 'next' }, 'нажмите, чтобы продолжить'));
  host.append(el);
  await sleep(30);
  el.classList.add('on');
  await new Promise<void>((r) => {
    const done = () => r();
    el.addEventListener('click', done, { once: true });
    const onKey = (e: KeyboardEvent) => {
      if (e.key === ' ' || e.key === 'Enter' || e.key === 'Escape') {
        document.removeEventListener('keydown', onKey);
        r();
      }
    };
    document.addEventListener('keydown', onKey);
    setTimeout(r, 14000);
  });
  el.classList.remove('on');
  await sleep(600);
  el.remove();
}

export async function chapterCard(_app: App, host: HTMLElement, def: ChapterDef): Promise<void> {
  const el = h(
    'div',
    { class: 'chapter-card' },
    h('div', { class: 'chapter-n' }, `Глава ${def.n}`),
    h('div', { class: 'chapter-zh' }, def.zh),
    h('div', { class: 'chapter-title' }, def.title),
    h('div', { class: 'chapter-sub' }, def.subtitle),
  );
  host.append(el);
  await sleep(30);
  el.classList.add('on');
  await Promise.race([sleep(4200), new Promise<void>((r) => el.addEventListener('click', () => r(), { once: true }))]);
  el.classList.remove('on');
  await sleep(700);
  el.remove();
}

/* ------------------------------------------------------------------ */
/* Ending                                                              */
/* ------------------------------------------------------------------ */

function formatTime(ms: number): string {
  const min = Math.round(ms / 60000);
  if (min < 60) return `${min} мин`;
  return `${Math.floor(min / 60)} ч ${min % 60} мин`;
}

export function showEnding(app: App, onMain: () => void): Promise<void> {
  app.tickPlaytime();
  const s = app.state;
  const p = progress(s);
  const pages = PAGES.filter((pg) => s.pages[pg.id]).length;
  const extras: HTMLElement[] = [];
  if (s.inscription) extras.push(h('p', {}, 'На Стеле без надписей теперь высечено: ', phraseEl(app, s.inscription, { size: 'md' })));
  if (s.flags.porter_tea) extras.push(h('p', {}, 'Вы угостили носильщика чаем. Он запомнит. ', phraseEl(app, '谢谢！', { size: 'sm' })));
  if (s.flags.ancient_done) extras.push(h('p', {}, 'Вы прочли стелу времён Цинь — знаки, которым больше двух тысяч лет.'));

  const body = h(
    'div',
    { class: 'ending' },
    h('div', { class: 'ending-zh' }, '日出'),
    h('div', { class: 'ending-py' }, h('span', { class: 't4' }, 'rì'), ' ', h('span', { class: 't1' }, 'chū'), ' — восход'),
    h('p', {}, `Вы поднялись на Тайшань и встретили рассвет над морем облаков. Внизу остались деревня, чайная, колокола и Восемнадцать поворотов.`),
    h('p', {}, `По дороге вы научились читать ${p.confirmed} из ${LEXICON.length} знаков и заполнили ${pages} из ${PAGES.length} страниц дневника.`),
    ...extras,
    h('p', { class: 'muted small' }, `Время в пути: ${formatTime(s.playMs)}.`),
    h(
      'div',
      { class: 'actions wrap' },
      h('button', { class: 'primary', onclick: () => (m.close(), app.openJournal('review')) }, 'Повторить знаки'),
      h('button', { onclick: () => (m.close(), app.openJournal('glyphs')) }, 'Дневник'),
      h('button', { onclick: () => m.close() }, 'Остаться на вершине'),
      h('button', { class: 'ghost', onclick: () => (m.close(), onMain()) }, 'Главное меню'),
    ),
    h('p', { class: 'credits muted small' }, 'По мотивам Chants of Sennaar (Rundisc). Шрифты LXGW WenKai и Ma Shan Zheng (SIL OFL). Графика и музыка сгенерированы кодом.'),
  );
  const m = openModal(app.overlay, body, { className: 'ending-modal' });
  return m.closed;
}

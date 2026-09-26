import { ART } from '../../art/scenes';
import { contains, matchesAny } from '../../core/phrases';
import { isOn } from '../../core/state';
import type { SceneDef, ScriptContext } from '../../core/types';
import { cycle } from './common';

/* ------------------------------------------------------------------ */
/* 4a · Южные небесные ворота                                          */
/* ------------------------------------------------------------------ */

export const SUNRISE_ACCEPT = ['看', '看日出', '我看日出', '我要看日出', '要看日出', '我要看', '要看', '我看'];

async function gatekeeper(c: ScriptContext): Promise<void> {
  if (c.flag('gate_open')) {
    await c.say('gatekeeper', '好！看日出！');
    return;
  }
  const ans = await c.ask('gatekeeper', '你好。你看日出吗？');
  if (!ans) return;
  if (contains(ans, '不')) {
    await c.say('gatekeeper', '不看？好。');
    return;
  }
  if (matchesAny(ans, SUNRISE_ACCEPT)) {
    await c.say('gatekeeper', '好！开门！');
    c.set('gate_open');
    c.sfx('gate');
    await c.event('gate-open');
    return;
  }
  await c.say('gatekeeper', '……？你看日出吗？');
}

const southgate: SceneDef = {
  id: '4a',
  chapter: 4,
  title: 'Южные небесные ворота',
  art: ART.southgate,
  look: () => ({ time: 'night', lantern: true, stars: true }),
  path: [
    [40, 842],
    [600, 846],
    [900, 840],
  ],
  entries: { bottom: 100, gate: 880 },
  actors: [
    {
      id: 'gatekeeper',
      name: 'Привратник',
      figure: { robe: '#7a2e2a', trim: '#d9b36c', hat: 'guard', hatColor: '#2b1f1d' },
      x: 600,
      y: 842,
      facing: 'right',
      standAt: 720,
      onTalk: gatekeeper,
    },
  ],
  hotspots: [
    {
      id: 'doors',
      name: 'Ворота',
      rect: [860, 480, 280, 360],
      standAt: 880,
      visible: (s) => !isOn(s, 'gate_open'),
      onClick: async (c) => c.say('gatekeeper', '门不开。'),
    },
  ],
  signs: [{ id: 'plaque', lines: ['南天门'], x: 1000, y: 446, style: 'plaque', size: 40 }],
  exits: [
    { id: 'down', to: '3b', entry: 'top', rect: [0, 600, 80, 300], dir: 'down', standAt: 40, label: 'Вниз по ступеням' },
    {
      id: 'through',
      to: '4b',
      entry: 'south',
      rect: [860, 480, 280, 360],
      dir: 'up',
      standAt: 900,
      label: 'Сквозь ворота',
      visible: (s) => isOn(s, 'gate_open'),
    },
  ],
  onEnter: async (c) => {
    if (c.flag('ch4')) return;
    c.set('ch4');
    await c.chapter(4);
  },
};

/* ------------------------------------------------------------------ */
/* 4b · Небесная улица                                                 */
/* ------------------------------------------------------------------ */

const skystreet: SceneDef = {
  id: '4b',
  chapter: 4,
  title: 'Небесная улица',
  art: ART.skystreet,
  look: () => ({ time: 'night', lantern: true, stars: true }),
  path: [
    [40, 842],
    [800, 850],
    [1580, 842],
  ],
  entries: { south: 800, west: 90, east: 1510, north: 1000 },
  marks: { south: [800, 860], west: [190, 330], east: [1540, 420] },
  actors: [
    {
      id: 'geomancer',
      name: 'Геомант',
      figure: { robe: '#4a3f6b', trim: '#d8c7a0', hat: 'scholar', hatColor: '#15121c', beard: true },
      x: 560,
      y: 842,
      facing: 'right',
      standAt: 670,
      onTalk: async (c) => {
        const n = Number(c.flag('geo_n') ?? 0);
        c.set('geo_n', n + 1);
        if (n % 3 === 0) {
          await c.say('geomancer', '南。');
          await c.event('point-south');
        } else if (n % 3 === 1) {
          await c.event('point-west');
          await c.say('geomancer', '月下山……西。');
        } else {
          await c.event('point-east');
          await c.say('geomancer', '日出……东。');
        }
      },
    },
    {
      id: 'innkeeper',
      name: 'Хозяин постоялого двора',
      figure: { robe: '#6a5236', trim: '#e2c48f', hat: 'cap', hatColor: '#221a12' },
      x: 1300,
      y: 842,
      facing: 'left',
      standAt: 1190,
      onTalk: (c) => cycle(c, 'inn_n', 'innkeeper', ['你好！', '你要茶吗？', '你看日出吗？好！']),
    },
  ],
  hotspots: [
    {
      id: 'compass',
      name: 'Компас геоманта',
      rect: [380, 700, 150, 90],
      standAt: 520,
      onClick: async (c) => c.narrate('Бронзовый компас-луопань. Стрелка смотрит на юг — туда, откуда вы пришли.'),
    },
  ],
  signs: [
    { id: 'compass-n', lines: ['北'], x: 455, y: 706, style: 'carved', size: 20 },
    { id: 'compass-s', lines: ['南'], x: 455, y: 772, style: 'carved', size: 20 },
    { id: 'compass-w', lines: ['西'], x: 398, y: 739, style: 'carved', size: 20 },
    { id: 'compass-e', lines: ['东'], x: 512, y: 739, style: 'carved', size: 20 },
    { id: 'post-w', lines: ['西'], x: 915, y: 560, style: 'post', arrow: 'left', size: 40 },
    { id: 'post-n', lines: ['北'], x: 990, y: 486, style: 'post', arrow: 'up', size: 40 },
    { id: 'post-e', lines: ['东'], x: 1065, y: 560, style: 'post', arrow: 'right', size: 40 },
  ],
  exits: [
    { id: 'south', to: '4a', entry: 'gate', rect: [700, 860, 200, 40], dir: 'down', standAt: 800, label: 'Назад, к Южным воротам' },
    { id: 'west', to: '4c', entry: 'east', rect: [0, 560, 80, 340], dir: 'left', standAt: 40, label: '西' },
    { id: 'north', to: '4d', entry: 'south', rect: [930, 330, 150, 220], dir: 'up', standAt: 1000, label: '北' },
    { id: 'east', to: '4e', entry: 'west', rect: [1520, 560, 80, 340], dir: 'right', standAt: 1570, label: '东' },
  ],
};

/* ------------------------------------------------------------------ */
/* 4c · Пик созерцания луны (запад)                                    */
/* ------------------------------------------------------------------ */

const moonpeak: SceneDef = {
  id: '4c',
  chapter: 4,
  title: 'Пик созерцания луны',
  art: ART.moonpeak,
  look: () => ({ time: 'night', lantern: true, stars: true }),
  path: [
    [420, 800],
    [1000, 822],
    [1580, 830],
  ],
  entries: { east: 1510 },
  actors: [
    {
      id: 'poet',
      name: 'Поэт',
      figure: { robe: '#e8e0d0', trim: '#6b6258', hat: 'topknot', hatColor: '#1a1a1a', pose: 'sit', prop: 'gourd', beard: true },
      x: 600,
      y: 796,
      facing: 'left',
      standAt: 730,
      onTalk: async (c) => {
        if (!c.flag('poet_1')) {
          c.set('poet_1');
          await c.say('poet', '看，明月！');
          return;
        }
        if (!c.flag('poet_wrote')) {
          await c.say('poet', '日，月……');
          await c.event('poet-writes');
          await c.say('poet', '明！');
          c.set('poet_wrote');
          return;
        }
        await cycle(c, 'poet_n', 'poet', ['明月！', '日，月……明！', '看，明月。']);
      },
    },
  ],
  hotspots: [],
  signs: [],
  exits: [{ id: 'back', to: '4b', entry: 'west', rect: [1520, 560, 80, 340], dir: 'right', standAt: 1570, label: 'Небесная улица' }],
};

/* ------------------------------------------------------------------ */
/* 4d · Пик Нефритового императора (север)                             */
/* ------------------------------------------------------------------ */

async function scholarTalk(c: ScriptContext): Promise<void> {
  if (c.flag('compose_done')) return cycle(c, 'scholar_n', 'scholar', ['东，日出。', '好！']);
  await c.say('scholar', '你看。');
  const made = await c.puzzle('compose', { targets: ['休', '林'] });
  c.confirm(made);
  if (['休', '林'].every((g) => c.state.confirmed[g])) {
    c.set('compose_done');
    await c.say('scholar', '好！');
    await c.event('point-east');
    await c.say('scholar', '东，日出。');
  }
}

const summit: SceneDef = {
  id: '4d',
  chapter: 4,
  title: 'Пик Нефритового императора',
  art: ART.summit,
  look: () => ({ time: 'predawn', lantern: true, stars: true }),
  path: [
    [40, 842],
    [800, 846],
    [1560, 842],
  ],
  entries: { south: 110 },
  marks: { east: [1540, 380] },
  actors: [
    {
      id: 'scholar',
      name: 'Старый учёный',
      figure: { robe: '#3a4a5a', trim: '#d8c7a0', hat: 'scholar', hatColor: '#141414', beard: true, prop: 'scroll' },
      x: 1180,
      y: 842,
      facing: 'left',
      standAt: 1060,
      onTalk: scholarTalk,
    },
  ],
  hotspots: [
    {
      id: 'stele',
      name: 'Стела без надписей',
      rect: [600, 330, 170, 480],
      standAt: 560,
      onClick: async (c) => {
        const text = await c.puzzle('stele');
        if (text) c.state.inscription = text;
      },
    },
    {
      id: 'qin',
      name: 'Обломок древней стелы',
      rect: [250, 600, 170, 220],
      standAt: 300,
      onClick: async (c) => {
        if (c.flag('ancient_done')) return c.narrate('Древние знаки — те же, что вы уже знаете. Только старше на две тысячи лет.');
        const ok = await c.puzzle('ancient');
        if (ok) {
          c.set('ancient_done');
          await c.say('scholar', '好！好！');
        }
      },
    },
  ],
  signs: [],
  exits: [{ id: 'back', to: '4b', entry: 'north', rect: [0, 560, 80, 340], dir: 'left', standAt: 40, label: 'Небесная улица' }],
};

/* ------------------------------------------------------------------ */
/* 4e · Пик созерцания солнца (восток)                                 */
/* ------------------------------------------------------------------ */

async function altar(c: ScriptContext): Promise<void> {
  if (c.flag('sunrise')) return c.finish();
  const made = await c.puzzle('compose', { targets: ['旦'] });
  c.confirm(made);
  if (!made.includes('旦')) return;
  c.set('sunrise');
  await c.event('sunrise');
  await c.talk([
    ['pilgrim', '看！日出！'],
    ['porter', '日出！'],
    ['monk', '好！'],
  ]);
  await c.finish();
}

const sunpeak: SceneDef = {
  id: '4e',
  chapter: 4,
  title: 'Пик созерцания солнца',
  art: ART.sunpeak,
  look: (s) => (isOn(s, 'sunrise') ? { time: 'dawn' } : { time: 'predawn', lantern: true, stars: true }),
  path: [
    [40, 842],
    [700, 836],
    [1180, 812],
  ],
  entries: { west: 100 },
  actors: [
    {
      id: 'pilgrim',
      name: 'Паломница',
      figure: { robe: '#9a5b4a', trim: '#e3c9a0', hat: 'bun', hatColor: '#2a2320' },
      x: 420,
      y: 840,
      facing: 'right',
      standAt: 320,
      onTalk: async (c) => c.say('pilgrim', c.flag('sunrise') ? '日出！' : '日出？'),
    },
    {
      id: 'porter',
      name: 'Носильщик',
      figure: { robe: '#556070', trim: '#2f3640', hat: 'straw', pose: 'sit' },
      x: 560,
      y: 842,
      facing: 'right',
      standAt: 670,
      onTalk: async (c) => c.say('porter', c.flag('sunrise') ? '日出！好！' : isOn(c.state, 'porter_tea') ? '你好！看东！' : '看东！'),
    },
    {
      id: 'monk',
      name: 'Монах',
      figure: { robe: '#b8864b', trim: '#6a4a22', hat: 'bald' },
      x: 1300,
      y: 800,
      facing: 'right',
      standAt: 1180,
      onTalk: async (c) => c.say('monk', c.flag('sunrise') ? '好！' : '你好。'),
    },
  ],
  hotspots: [
    {
      id: 'altar',
      name: 'Алтарный камень',
      rect: [860, 640, 180, 170],
      standAt: 920,
      onClick: altar,
    },
  ],
  signs: [],
  exits: [{ id: 'back', to: '4b', entry: 'east', rect: [0, 560, 80, 340], dir: 'left', standAt: 40, label: 'Небесная улица' }],
};

export const CHAPTER4: SceneDef[] = [southgate, skystreet, moonpeak, summit, sunpeak];

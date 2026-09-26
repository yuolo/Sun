import { ART } from '../../art/scenes';
import { isOn } from '../../core/state';
import type { SceneDef, ScriptContext } from '../../core/types';
import { cycle } from './common';

/* ------------------------------------------------------------------ */
/* 3a · Средние небесные ворота                                        */
/* ------------------------------------------------------------------ */

const solved = (s: Parameters<typeof isOn>[0]) => isOn(s, 'bells_solved');

async function ringBells(c: ScriptContext): Promise<void> {
  if (c.flag('bells_solved')) {
    c.sfx('bell');
    return;
  }
  if (!c.flag('ch3_intro')) return;
  const ok = await c.puzzle('bells');
  if (!ok) return;
  c.set('bells_solved');
  await c.event('rain-stop');
  await c.event('moonrise');
  await c.say('priest', '好！看，月上山。');
  await c.say('nun', '好，上山。');
  await c.move('nun', 1330, 780);
}

const midgate: SceneDef = {
  id: '3a',
  chapter: 3,
  title: 'Средние небесные ворота',
  art: ART.midgate,
  look: (s) =>
    isOn(s, 'bells_solved')
      ? { time: 'night', lantern: true, stars: true }
      : isOn(s, 'ch3_intro')
        ? { time: 'dusk', rain: true, mist: true, lantern: true }
        : { time: 'sunset' },
  path: [
    [40, 842],
    [700, 846],
    [1190, 842],
  ],
  entries: { bottom: 100, top: 1150 },
  marks: { board: [1010, 470] },
  actors: [
    {
      id: 'priest',
      name: 'Даос',
      figure: { robe: '#2f4f6f', trim: '#d8c7a0', hat: 'topknot', hatColor: '#141414', beard: true, prop: 'fan' },
      x: 560,
      y: 842,
      facing: 'right',
      standAt: 450,
      onTalk: async (c) => {
        if (!c.flag('ch3_intro')) return;
        if (c.flag('bells_solved')) return cycle(c, 'priest_n', 'priest', ['看，月上山。', '好。']);
        await c.say('priest', '你看。');
        await c.event('point-board');
      },
    },
    {
      id: 'nun',
      name: 'Монахиня',
      figure: { robe: '#6d6d7d', trim: '#2d2d38', hat: 'hood' },
      x: (s) => (solved(s) ? 1330 : 1225),
      y: (s) => (solved(s) ? 780 : 842),
      facing: 'left',
      standAt: 1110,
      onTalk: async (c) => c.say('nun', c.flag('bells_solved') ? '好，上山。' : '下雨，不上山。'),
    },
    {
      id: 'pilgrim',
      name: 'Паломница',
      figure: { robe: '#9a5b4a', trim: '#e3c9a0', hat: 'bun', hatColor: '#2a2320' },
      x: 170,
      y: 842,
      facing: 'right',
      standAt: 280,
      onTalk: async (c) => c.say('pilgrim', c.flag('bells_solved') ? '看，月！' : '看！云！'),
    },
    {
      id: 'kid',
      name: 'Ребёнок',
      figure: { robe: '#d08a3a', trim: '#7a4a1c', hat: 'twinbuns', scale: 0.6 },
      x: 250,
      y: 848,
      facing: 'right',
      standAt: 340,
      onTalk: async (c) => c.say('kid', c.flag('bells_solved') ? '月！大月！' : '雨！大雨！'),
    },
  ],
  hotspots: [
    {
      id: 'bells',
      name: 'Колокола',
      rect: [640, 420, 300, 260],
      standAt: 700,
      onClick: ringBells,
    },
    {
      id: 'map',
      name: 'Каменная карта горы',
      rect: [290, 440, 170, 300],
      standAt: 330,
      onClick: async (c) => c.narrate('Каменная карта тропы. Красная точка отмечает, где вы стоите.'),
    },
  ],
  signs: [
    { id: 'plaque', lines: ['中天门'], x: 1240, y: 354, style: 'plaque', size: 44 },
    { id: 'map-top', lines: ['南天门'], x: 428, y: 480, style: 'carved', size: 22 },
    { id: 'map-mid', lines: ['中天门'], x: 428, y: 580, style: 'carved', size: 22 },
    { id: 'map-bottom', lines: ['一天门'], x: 428, y: 680, style: 'carved', size: 22 },
    { id: 'chant', lines: ['雨', '云', '月'], x: 1010, y: 540, style: 'board', size: 40 },
  ],
  exits: [
    {
      id: 'stairs',
      to: '3b',
      entry: 'bottom',
      rect: [1150, 360, 320, 480],
      dir: 'up',
      standAt: 1180,
      label: 'Вверх, к Восемнадцати поворотам',
      guard: async (c) => {
        if (c.flag('bells_solved')) return true;
        await c.say('nun', c.flag('ch3_intro') ? '下雨，不上山。' : '你好。');
        return false;
      },
    },
  ],
  onEnter: async (c) => {
    if (c.flag('ch3_intro')) return;
    await c.chapter(3);
    await c.event('sunset');
    await c.say('priest', '看，日下山。');
    await c.event('clouds');
    await c.say('pilgrim', '看！云！');
    c.set('ch3_intro');
    await c.event('rain');
    await c.say('kid', '雨！大雨！');
    await c.say('nun', '下雨，不上山。');
    await c.say('priest', '你看。');
    await c.event('point-board');
  },
};

/* ------------------------------------------------------------------ */
/* 3b · Восемнадцать поворотов                                         */
/* ------------------------------------------------------------------ */

const stairs: SceneDef = {
  id: '3b',
  chapter: 3,
  title: 'Восемнадцать поворотов',
  art: ART.stairs,
  front: ART.stairsFront,
  look: () => ({ time: 'night', lantern: true, stars: true, mist: true }),
  path: [
    [90, 858],
    [820, 780],
    [360, 660],
    [930, 560],
    [560, 450],
    [1040, 360],
    [1260, 300],
  ],
  entries: { bottom: 130, top: 1230 },
  marks: { carving: [1230, 600] },
  actors: [
    {
      id: 'porter',
      name: 'Носильщик',
      figure: { robe: '#556070', trim: '#2f3640', hat: 'straw', prop: 'pole' },
      x: 760,
      y: 786,
      facing: 'left',
      standAt: 660,
      onTalk: async (c) => {
        if (!c.flag('porter_3b')) {
          c.set('porter_3b');
          await c.talk([
            ['porter', isOn(c.state, 'porter_tea') ? '你好！谢谢！' : '你好！'],
            ['porter', '十八！'],
          ]);
          await c.event('point-carving');
          await c.say('porter', '上山！');
          return;
        }
        await cycle(c, 'porter3_n', 'porter', ['十八！', '上山！', '你好！']);
      },
    },
    {
      id: 'tired',
      name: 'Уставший паломник',
      figure: { robe: '#77705f', trim: '#3b372c', hat: 'hood', pose: 'sit', prop: 'staff' },
      x: 470,
      y: 640,
      facing: 'right',
      standAt: 560,
      onTalk: (c) => cycle(c, 'tired_n', 'tired', ['我不上山。', '下山！我要下山。']),
    },
  ],
  hotspots: [],
  signs: [
    { id: 'carving', lines: ['十八'], x: 1230, y: 640, style: 'carved', vertical: true, size: 58 },
    { id: 'gate', lines: ['南天门'], x: 1330, y: 262, style: 'plaque', size: 20 },
  ],
  exits: [
    { id: 'down', to: '3a', entry: 'top', rect: [0, 780, 200, 120], dir: 'down', standAt: 90, label: 'Вниз, к Средним воротам' },
    { id: 'up', to: '4a', entry: 'bottom', rect: [1180, 160, 300, 170], dir: 'up', standAt: 1260, label: 'К Южным небесным воротам' },
  ],
};

export const CHAPTER3: SceneDef[] = [midgate, stairs];

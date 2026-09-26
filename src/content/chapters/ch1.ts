import { ART } from '../../art/scenes';
import { contains, matchesAny } from '../../core/phrases';
import { isOn } from '../../core/state';
import type { SceneDef, ScriptContext } from '../../core/types';
import { cycle, refuse } from './common';

/* ------------------------------------------------------------------ */
/* 1a · Пристань                                                       */
/* ------------------------------------------------------------------ */

const pier: SceneDef = {
  id: '1a',
  chapter: 1,
  title: 'Пристань',
  art: ART.pier,
  look: () => ({ time: 'golden' }),
  path: [
    [440, 812],
    [900, 818],
    [1580, 812],
  ],
  entries: { boat: 470, right: 1520 },
  marks: { mountain: [1000, 260] },
  actors: [
    {
      id: 'boatman',
      name: 'Лодочник',
      figure: { robe: '#4f6d7a', trim: '#2c3e48', hat: 'straw', prop: 'oar' },
      x: 285,
      y: 792,
      facing: 'right',
      standAt: 470,
      onTalk: (c) => cycle(c, 'boatman_n', 'boatman', ['你好！你上山吗？', '山！', '你好！']),
      onItem: async (c, item) => {
        if (item === 'water') await c.say('boatman', '不要水。');
        else await c.say('boatman', '不要。');
        return true;
      },
    },
  ],
  hotspots: [
    {
      id: 'river',
      name: 'Река',
      rect: [0, 660, 400, 240],
      standAt: 460,
      onClick: async (c) => {
        if (c.has('bucket')) return fillBucket(c);
        await c.narrate(c.has('water') ? 'Ведро уже полное.' : 'Холодная река бежит с гор. Зачерпнуть воду не во что.');
      },
      onItem: async (c, item) => {
        if (item !== 'bucket') return false;
        await fillBucket(c);
        return true;
      },
    },
  ],
  signs: [],
  exits: [
    { id: 'village', to: '1b', entry: 'left', rect: [1500, 560, 100, 340], dir: 'right', standAt: 1560, label: 'Деревня' },
  ],
  onEnter: async (c) => {
    if (c.flag('ch1')) return;
    c.set('ch1');
    await c.chapter(1);
    await c.say('boatman', '你好！');
  },
};

async function fillBucket(c: ScriptContext): Promise<void> {
  c.take('bucket');
  c.give('water');
  c.sfx('splash');
}

/* ------------------------------------------------------------------ */
/* 1b · Деревня                                                        */
/* ------------------------------------------------------------------ */

const village: SceneDef = {
  id: '1b',
  chapter: 1,
  title: 'Деревня',
  art: ART.village,
  look: () => ({ time: 'golden' }),
  path: [
    [40, 815],
    [800, 822],
    [1580, 815],
  ],
  entries: { left: 90, right: 1510 },
  actors: [
    {
      id: 'woman',
      name: 'Женщина у чана',
      figure: { robe: '#9c4a3c', trim: '#e3c9a0', hat: 'bun', hatColor: '#2a2320' },
      x: 540,
      y: 812,
      facing: 'right',
      standAt: 420,
      onTalk: async (c) => {
        if (c.flag('woman_done')) return cycle(c, 'woman_n', 'woman', ['谢谢！', '你好！']);
        if (!c.flag('woman_met')) {
          c.set('woman_met');
          await c.say('woman', '你好！');
        }
        await c.say('woman', '我要水。');
      },
      onItem: async (c, item) => {
        if (c.flag('woman_done')) {
          await c.say('woman', '谢谢！');
          return true;
        }
        if (item !== 'water') return refuse(c, 'woman', item, '水');
        c.take('water');
        c.set('woman_done');
        c.sfx('pour');
        await c.say('woman', '好！谢谢！谢谢！');
        c.addCoins(3);
        await c.narrate('Она благодарно кланяется и вкладывает вам в ладонь три монеты с квадратными отверстиями.');
        return true;
      },
    },
    {
      id: 'oldman',
      name: 'Старик у костра',
      figure: { robe: '#6b5a45', trim: '#3b3025', hat: 'bald', beard: true, pose: 'sit' },
      x: 905,
      y: 812,
      facing: 'right',
      standAt: 790,
      onTalk: async (c) => {
        if (c.flag('fire_lit')) return cycle(c, 'oldman_n', 'oldman', ['火！好！', '谢谢。']);
        await c.say('oldman', '我要木。');
      },
      onItem: async (c, item) => {
        if (c.flag('fire_lit')) {
          await c.say('oldman', '不要。');
          return true;
        }
        if (item === 'water') {
          await c.say('oldman', '不！不要水！我要木。');
          return true;
        }
        if (item !== 'wood') return refuse(c, 'oldman', item, '木');
        c.take('wood');
        c.set('fire_lit');
        c.sfx('fire');
        await c.event('campfire');
        await c.say('oldman', '好！火！谢谢。');
        return true;
      },
    },
    {
      id: 'lanternman',
      name: 'Человек с фонарём',
      figure: (s) => ({
        robe: '#3f5a45',
        trim: '#c9a86a',
        hat: 'cap',
        hatColor: '#1f2a22',
        prop: isOn(s, 'lantern_given') ? 'lantern' : 'lanternDark',
      }),
      x: 1335,
      y: 812,
      facing: 'left',
      standAt: 1220,
      onTalk: async (c) => {
        if (c.flag('lantern_given')) return cycle(c, 'lanternman_n', 'lanternman', ['谢谢！', '你上山吗？好！']);
        await c.say('lanternman', '我要火。');
      },
      onItem: async (c, item) => {
        if (c.flag('lantern_given')) {
          await c.say('lanternman', '谢谢！');
          return true;
        }
        if (item !== 'torch') return refuse(c, 'lanternman', item, '火');
        c.take('torch');
        c.set('lantern_given');
        c.sfx('fire');
        await c.say('lanternman', '好！火！谢谢！谢谢！');
        c.give('lantern');
        await c.narrate('Он зажигает свой фонарь, а от него — второй, и протягивает его вам.');
        return true;
      },
    },
    {
      id: 'kid',
      name: 'Ребёнок',
      figure: { robe: '#c9853a', trim: '#7a4a1c', hat: 'twinbuns', scale: 0.62 },
      x: 790,
      y: 822,
      facing: 'right',
      standAt: 700,
      onTalk: (c) => cycle(c, 'kid1_n', 'kid', ['你好！', '山！山！', '你好！你好！']),
    },
  ],
  hotspots: [
    {
      id: 'bucket',
      name: 'Ведро',
      rect: [250, 700, 80, 110],
      standAt: 300,
      visible: (s) => !isOn(s, 'bucket_taken'),
      onClick: async (c) => {
        c.set('bucket_taken');
        c.give('bucket');
      },
    },
    {
      id: 'jar',
      name: 'Чан',
      rect: [600, 690, 140, 130],
      standAt: 640,
      onClick: async (c) => {
        await c.narrate(c.flag('woman_done') ? 'Чан полон воды.' : 'Большой глиняный чан. Пустой.');
      },
      onItem: async (c, item) => {
        if (item !== 'water') return false;
        await c.say('woman', '好！我要水！');
        return true;
      },
    },
    {
      id: 'campfire',
      name: 'Костёр',
      rect: [960, 720, 130, 100],
      standAt: 1000,
      onClick: async (c) => {
        if (!c.flag('fire_lit')) return c.narrate('Костёр погас. Одни холодные угли.');
        if (c.has('torch') || c.has('lantern')) return c.narrate('Костёр весело трещит.');
        c.give('torch');
        c.sfx('fire');
        await c.narrate('Вы поджигаете от костра длинную щепу.');
      },
      onItem: async (c, item) => {
        if (item === 'wood') {
          await c.say('oldman', c.flag('fire_lit') ? '好。' : '我要木。');
          return true;
        }
        if (item === 'water') {
          await c.say('oldman', '不！不要水！');
          return true;
        }
        return false;
      },
    },
    {
      id: 'woodpile',
      name: 'Поленница',
      rect: [1130, 640, 150, 170],
      standAt: 1170,
      onClick: async (c) => {
        if (c.has('wood') || c.flag('fire_lit')) return c.narrate('Аккуратная поленница.');
        c.give('wood');
      },
    },
  ],
  signs: [{ id: 'jar-label', lines: ['水'], x: 670, y: 752, style: 'jar', size: 34 }],
  exits: [
    { id: 'pier', to: '1a', entry: 'right', rect: [0, 560, 90, 340], dir: 'left', standAt: 40, label: 'Пристань', guard: dropTorch },
    { id: 'arch', to: '1c', entry: 'left', rect: [1510, 560, 90, 340], dir: 'right', standAt: 1570, label: 'Начало тропы', guard: dropTorch },
  ],
};

async function dropTorch(c: ScriptContext): Promise<boolean> {
  if (c.has('torch')) {
    c.take('torch');
    await c.narrate('Лучина догорела и погасла.');
  }
  return true;
}

/* ------------------------------------------------------------------ */
/* 1c · Арка начала пути                                               */
/* ------------------------------------------------------------------ */

const GUARD_X = 1085;

const arch: SceneDef = {
  id: '1c',
  chapter: 1,
  title: 'Арка начала пути',
  art: ART.arch,
  look: () => ({ time: 'golden' }),
  path: [
    [40, 818],
    [700, 822],
    [1010, 818],
  ],
  depth: [470, 0.3],
  entries: { left: 90 },
  actors: [
    {
      id: 'guard',
      name: 'Стражник',
      figure: { robe: '#7a2e2a', trim: '#d9b36c', hat: 'guard', hatColor: '#2b1f1d', prop: 'spear' },
      x: (s) => (isOn(s, 'guard_passed') ? 1250 : GUARD_X),
      y: (s) => (isOn(s, 'guard_passed') ? 760 : 812),
      facing: 'left',
      standAt: 960,
      onTalk: guardDialog,
    },
    {
      id: 'porter',
      name: 'Носильщик',
      figure: { robe: '#556070', trim: '#2f3640', hat: 'straw', prop: 'pole' },
      x: 150,
      y: 818,
      facing: 'right',
      visible: (s) => !isOn(s, 'arch_scene'),
    },
    {
      id: 'pilgrim',
      name: 'Паломник',
      figure: { robe: '#8a7d6a', trim: '#4a4032', hat: 'hood', prop: 'staff' },
      x: 1330,
      y: 600,
      facing: 'left',
      visible: (s) => !isOn(s, 'arch_scene'),
    },
  ],
  hotspots: [],
  signs: [
    { id: 'up', lines: ['上山'], x: 650, y: 560, style: 'post', arrow: 'right', size: 40 },
    { id: 'down', lines: ['下山'], x: 630, y: 640, style: 'post', arrow: 'left', size: 40 },
  ],
  exits: [
    { id: 'back', to: '1b', entry: 'right', rect: [0, 560, 80, 340], dir: 'left', standAt: 40, label: 'Деревня' },
    {
      id: 'stairs',
      to: '2a',
      entry: 'bottom',
      rect: [1130, 380, 470, 420],
      dir: 'up',
      standAt: 1000,
      label: 'Вверх по тропе',
      guard: async (c) => {
        if (!c.flag('guard_passed')) await guardDialog(c);
        return !!c.flag('guard_passed');
      },
    },
  ],
  onEnter: async (c) => {
    if (c.flag('arch_scene')) return;
    await c.move('porter', 980);
    await c.talk([
      ['guard', '你上山吗？'],
      ['porter', '上山。'],
      ['guard', '好。'],
    ]);
    await c.move('porter', 1340, 590);
    await c.move('pilgrim', 1010, 818);
    await c.talk([
      ['pilgrim', '你好！'],
      ['guard', '你好！下山吗？'],
      ['pilgrim', '下山。'],
    ]);
    await c.move('pilgrim', -120, 818);
    c.set('arch_scene');
  },
};

export const GUARD_ACCEPT = ['上', '上山', '我上山', '我要上山', '要上山'];

async function guardDialog(c: ScriptContext): Promise<void> {
  if (c.flag('guard_passed')) {
    await c.say('guard', '好！上山！');
    return;
  }
  const ans = await c.ask('guard', '你上山吗？');
  if (!ans) return;
  if (contains(ans, '不')) {
    await c.say('guard', '不上山？好。');
    return;
  }
  if (matchesAny(ans, GUARD_ACCEPT)) {
    if (!c.has('lantern')) {
      c.set('guard_needs_fire');
      await c.say('guard', '上山……要火。');
      return;
    }
    await c.say('guard', '好！');
    c.set('guard_passed');
    await c.move('guard', 1250, 760);
    return;
  }
  if (contains(ans, '下')) {
    await c.say('guard', '下山？不……上山吗？');
    return;
  }
  await c.say('guard', '……？');
}

export const CHAPTER1: SceneDef[] = [pier, village, arch];

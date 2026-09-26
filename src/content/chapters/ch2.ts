import { ART } from '../../art/scenes';
import { toHanzi } from '../../core/numerals';
import { contains, matchesAny } from '../../core/phrases';
import { checkOrder, type Order } from '../../core/puzzles';
import { isOn } from '../../core/state';
import type { ActorDef, SceneDef, ScriptContext } from '../../core/types';
import { cycle } from './common';

const NUMS = ['一', '二', '三', '四', '五', '六', '七', '八', '九', '十'];
const HOP_X0 = 380;
const HOP_STEP = 62;

/* ------------------------------------------------------------------ */
/* 2a · Рынок у Красных ворот                                          */
/* ------------------------------------------------------------------ */

async function countHops(c: ScriptContext): Promise<void> {
  await c.move('hopper', HOP_X0 - 70, 830);
  for (let i = 0; i < NUMS.length; i++) {
    await c.move('hopper', HOP_X0 + i * HOP_STEP, 830);
    c.sfx('hop');
    await c.say('hopper', NUMS[i], { auto: 650 });
  }
  await c.say('friend', '好！');
  await c.move('hopper', HOP_X0 - 70, 830);
}

const market: SceneDef = {
  id: '2a',
  chapter: 2,
  title: 'Рынок у Красных ворот',
  art: ART.market,
  look: () => ({ time: 'sunset' }),
  path: [
    [40, 842],
    [800, 848],
    [1580, 842],
  ],
  entries: { bottom: 100, right: 1510 },
  actors: [
    {
      id: 'hopper',
      name: 'Девочка играет в классики',
      figure: { robe: '#d08a3a', trim: '#7a4a1c', hat: 'twinbuns', scale: 0.6 },
      x: HOP_X0 - 70,
      y: 830,
      facing: 'right',
      standAt: 250,
      onTalk: countHops,
    },
    {
      id: 'friend',
      name: 'Мальчик',
      figure: { robe: '#5d7fa3', trim: '#2d4056', hat: 'topknot', scale: 0.58 },
      x: 1060,
      y: 838,
      facing: 'left',
      standAt: 1140,
      onTalk: (c) => cycle(c, 'friend_n', 'friend', ['一，二，三！', '你好！', '十！']),
    },
    {
      id: 'porter',
      name: 'Носильщик',
      figure: { robe: '#556070', trim: '#2f3640', hat: 'straw', pose: 'sit' },
      x: 1300,
      y: 842,
      facing: 'left',
      standAt: 1190,
      onTalk: async (c) => {
        if (c.flag('porter_tea')) return cycle(c, 'porter2_n', 'porter', ['谢谢！谢谢！', '你好！上山！']);
        await c.talk([
          ['porter', '我要茶。'],
          ['porter', '我没有钱。'],
        ]);
      },
      onItem: async (c, item) => {
        if (c.flag('porter_tea')) {
          await c.say('porter', '谢谢！');
          return true;
        }
        if (item !== 'tray') {
          await c.say('porter', '不要。我要茶。');
          return true;
        }
        const res = checkOrder(c.state.tray, { drink: 'tea', count: 1 });
        if (!res.ok) {
          if (res.problem === 'drink') await c.say('porter', '不要水。我要茶。');
          else if (res.problem === 'count') await c.say('porter', '一杯！一杯茶。');
          else await c.say('porter', '我要茶。');
          return true;
        }
        c.state.tray = [];
        c.set('porter_tea');
        c.sfx('pour');
        await c.say('porter', '谢谢！谢谢！');
        return true;
      },
    },
  ],
  hotspots: [],
  signs: [{ id: 'banner', lines: ['茶'], x: 1440, y: 470, style: 'banner', vertical: true, size: 54 }],
  exits: [
    { id: 'teahouse', to: '2b', entry: 'left', rect: [1500, 560, 100, 340], dir: 'right', standAt: 1570, label: 'Чайная' },
  ],
  onEnter: async (c) => {
    if (c.flag('ch2')) return;
    c.set('ch2');
    await c.chapter(2);
    await countHops(c);
  },
};

/* ------------------------------------------------------------------ */
/* 2b · Чайная                                                         */
/* ------------------------------------------------------------------ */

interface Customer {
  id: string;
  name: string;
  order: Order;
  line: string;
}

export const CUSTOMERS: Customer[] = [
  { id: 'bigman', name: 'Здоровяк', order: { drink: 'tea', count: 1, size: 'big' }, line: '一大杯茶！' },
  { id: 'lady', name: 'Женщина за столом', order: { drink: 'tea', count: 2, size: 'small' }, line: '两小杯茶。' },
  { id: 'monk', name: 'Монах', order: { drink: 'water', count: 3 }, line: '不要茶。三杯水。' },
];

const DRINK = { tea: '茶', water: '水' } as const;
const SIZE = { big: '大', small: '小' } as const;

async function serve(c: ScriptContext, cu: Customer, item: string): Promise<boolean> {
  if (c.flag(`served_${cu.id}`)) {
    await c.say(cu.id, '谢谢！');
    return true;
  }
  if (item !== 'tray') {
    await c.say(cu.id, `不要。${cu.line}`);
    return true;
  }
  const res = checkOrder(c.state.tray, cu.order);
  if (res.ok) {
    c.state.tray = [];
    c.set(`served_${cu.id}`);
    c.sfx('pour');
    await c.say(cu.id, '谢谢！');
    if (CUSTOMERS.every((x) => c.flag(`served_${x.id}`))) await payday(c);
    return true;
  }
  switch (res.problem) {
    case 'empty':
      await c.say(cu.id, cu.line);
      break;
    case 'drink': {
      const wrong = c.state.tray.find((x) => x.drink !== cu.order.drink)!.drink;
      await c.say(cu.id, `不要${DRINK[wrong]}！我要${DRINK[cu.order.drink]}。`);
      break;
    }
    case 'count':
      await c.say(cu.id, `不！${cu.line.replace('不要茶。', '')}`);
      break;
    case 'size':
      await c.say(cu.id, `不！${SIZE[cu.order.size!]}杯！`);
      break;
  }
  return true;
}

async function payday(c: ScriptContext): Promise<void> {
  c.set('tea_job');
  await c.say('owner', '好！谢谢！谢谢！');
  c.addCoins(10);
  c.sfx('coins');
  await c.say('owner', '十钱。');
  await c.narrate('Хозяйка отсчитывает вам монеты за помощь.');
}

function customerActor(cu: Customer, x: number, figure: ActorDef['figure'], facing: 'left' | 'right' = 'left'): ActorDef {
  return {
    id: cu.id,
    name: cu.name,
    figure,
    x,
    y: 840,
    facing,
    standAt: x - 120,
    onTalk: async (c) => {
      await c.say(cu.id, c.flag(`served_${cu.id}`) ? '谢谢！' : cu.line);
    },
    onItem: (c, item) => serve(c, cu, item),
  };
}

async function ownerTalk(c: ScriptContext): Promise<void> {
  if (c.flag('tea_job')) return cycle(c, 'owner_n', 'owner', ['谢谢！', '你好！']);
  if (!c.has('tray')) {
    await c.say('owner', '你好！');
    c.give('tray');
    await c.narrate('Хозяйка сует вам в руки поднос и кивает на столы: помогите!');
    return;
  }
  await c.say('owner', '一大杯茶，两小杯茶，三杯水！');
}

const teahouse: SceneDef = {
  id: '2b',
  chapter: 2,
  title: 'Чайная',
  art: ART.teahouse,
  look: () => ({ time: 'sunset' }),
  path: [
    [40, 852],
    [800, 856],
    [1580, 852],
  ],
  entries: { left: 90, right: 1510 },
  actors: [
    {
      id: 'owner',
      name: 'Хозяйка чайной',
      figure: { robe: '#7d3b53', trim: '#e6c07a', hat: 'bun', hatColor: '#221a1a' },
      x: 330,
      y: 790,
      facing: 'right',
      standAt: 470,
      onTalk: ownerTalk,
      onItem: async (c, item) => {
        if (item === 'tray' && !c.flag('tea_job')) {
          await c.say('owner', '一大杯茶，两小杯茶，三杯水！');
          return true;
        }
        return false;
      },
    },
    customerActor(CUSTOMERS[0], 760, { robe: '#4b5d3a', trim: '#2a3420', hat: 'cap', hatColor: '#1d2418', scale: 1.12, pose: 'sit' }),
    customerActor(CUSTOMERS[1], 1085, { robe: '#b06a7a', trim: '#f0d9c0', hat: 'bun', hatColor: '#2a2020', pose: 'sit' }),
    {
      id: 'husband',
      name: 'Мужчина за столом',
      figure: { robe: '#3d5a73', trim: '#1f3040', hat: 'cap', hatColor: '#162230', pose: 'sit' },
      x: 1185,
      y: 840,
      facing: 'left',
      standAt: 1060,
      onTalk: async (c) => c.say('husband', c.flag('served_lady') ? '谢谢！' : '两小杯茶。'),
      onItem: (c, item) => serve(c, CUSTOMERS[1], item),
    },
    customerActor(CUSTOMERS[2], 1400, { robe: '#b8864b', trim: '#6a4a22', hat: 'bald', pose: 'sit' }),
    {
      id: 'monk2',
      name: 'Монах',
      figure: { robe: '#b8864b', trim: '#6a4a22', hat: 'bald', pose: 'sit', scale: 0.95 },
      x: 1485,
      y: 840,
      facing: 'left',
      standAt: 1370,
      onTalk: async (c) => c.say('monk2', c.flag('served_monk') ? '谢谢！' : '三杯水。'),
      onItem: (c, item) => serve(c, CUSTOMERS[2], item),
    },
    {
      id: 'monk3',
      name: 'Монах',
      figure: { robe: '#a9793f', trim: '#6a4a22', hat: 'bald', pose: 'sit', scale: 0.92 },
      x: 1330,
      y: 846,
      facing: 'right',
      standAt: 1230,
      onTalk: async (c) => c.say('monk3', c.flag('served_monk') ? '谢谢！' : '不要茶。'),
      onItem: (c, item) => serve(c, CUSTOMERS[2], item),
    },
  ],
  hotspots: [
    {
      id: 'counter',
      name: 'Стойка с кувшинами',
      rect: [90, 640, 200, 200],
      standAt: 250,
      onClick: async (c) => {
        if (!c.has('tray')) return ownerTalk(c);
        const cups = await c.puzzle('tray');
        if (cups) c.state.tray = cups;
      },
    },
  ],
  signs: [
    { id: 'prices', lines: ['大杯 五钱', '小杯 三钱'], x: 600, y: 470, style: 'board', size: 34 },
    { id: 'jar-tea', lines: ['茶'], x: 150, y: 668, style: 'jar', size: 28 },
    { id: 'jar-water', lines: ['水'], x: 240, y: 668, style: 'jar', size: 28 },
    { id: 'banner', lines: ['茶'], x: 45, y: 420, style: 'banner', vertical: true, size: 46 },
  ],
  exits: [
    { id: 'market', to: '2a', entry: 'right', rect: [0, 560, 70, 340], dir: 'left', standAt: 40, label: 'Рынок' },
    { id: 'gate', to: '2c', entry: 'left', rect: [1530, 560, 70, 340], dir: 'right', standAt: 1570, label: 'К воротам' },
  ],
  onEnter: async (c) => {
    if (c.flag('orders_heard')) return;
    await c.talk([
      ['owner', '你好！你要几杯茶？'],
      ['bigman', '一大杯茶！'],
      ['lady', '两小杯茶。'],
      ['monk', '不要茶。三杯水。'],
    ]);
    c.set('orders_heard');
  },
};

/* ------------------------------------------------------------------ */
/* 2c · Первые небесные ворота                                         */
/* ------------------------------------------------------------------ */

export const TOLL = 10;
export const TOLL_ACCEPT = ['有', '有钱', '我有钱', '我有', '有十钱', '我有十钱'];

async function keeperDialog(c: ScriptContext): Promise<void> {
  if (c.flag('gate1_passed')) {
    await c.say('keeper', '好。上山！');
    return;
  }
  const ans = await c.ask('keeper', '你好。一人十钱。你有钱吗？');
  if (!ans) return;
  if (contains(ans, '没') || contains(ans, '不')) {
    await c.say('keeper', '没有钱，不上山。');
    return;
  }
  if (!matchesAny(ans, TOLL_ACCEPT)) {
    await c.say('keeper', '……？你有钱吗？');
    return;
  }
  const coins = c.state.coins;
  if (coins >= TOLL) {
    c.addCoins(-TOLL);
    c.sfx('coins');
    c.set('gate1_passed');
    await c.say('keeper', '好。上山！');
    return;
  }
  if (coins > 0) await c.say('keeper', `${toHanzi(coins)}钱？不！十钱。`);
  else await c.say('keeper', '你没有钱。');
}

const gate1: SceneDef = {
  id: '2c',
  chapter: 2,
  title: 'Первые небесные ворота',
  art: ART.gate1,
  look: () => ({ time: 'sunset' }),
  path: [
    [40, 842],
    [700, 846],
    [1010, 842],
  ],
  entries: { left: 90 },
  actors: [
    {
      id: 'keeper',
      name: 'Сборщик у ворот',
      figure: { robe: '#5a4a3a', trim: '#c9a86a', hat: 'scholar', hatColor: '#1c1a18', pose: 'sit', beard: true },
      x: 860,
      y: 842,
      facing: 'left',
      standAt: 740,
      onTalk: keeperDialog,
    },
    {
      id: 'payer',
      name: 'Паломница',
      figure: { robe: '#8a6d7a', trim: '#3f2f38', hat: 'hood', prop: 'staff' },
      x: 200,
      y: 842,
      facing: 'right',
      visible: (s) => !isOn(s, 'toll_scene'),
    },
  ],
  hotspots: [],
  signs: [
    { id: 'plaque', lines: ['一天门'], x: 1240, y: 354, style: 'plaque', size: 44 },
    { id: 'toll', lines: ['一人十钱'], x: 600, y: 650, style: 'stone', vertical: true, size: 38 },
  ],
  exits: [
    { id: 'back', to: '2b', entry: 'right', rect: [0, 560, 70, 340], dir: 'left', standAt: 40, label: 'Чайная' },
    {
      id: 'gate',
      to: '3a',
      entry: 'bottom',
      rect: [1080, 360, 320, 480],
      dir: 'up',
      standAt: 1000,
      label: 'Сквозь ворота',
      guard: async (c) => {
        if (!c.flag('gate1_passed')) await keeperDialog(c);
        if (!c.flag('gate1_passed')) return false;
        if (c.has('tray')) {
          c.take('tray');
          c.state.tray = [];
          await c.narrate('Поднос вы оставляете у ворот — хозяйка чайной его заберёт.');
        }
        return true;
      },
    },
  ],
  onEnter: async (c) => {
    if (c.flag('toll_scene')) return;
    await c.move('payer', 740);
    await c.talk([
      ['payer', '你好。'],
      ['keeper', '你好。一人十钱。'],
    ]);
    c.sfx('coins');
    await c.say('keeper', '好。上山！');
    await c.move('payer', 1240, 700);
    c.set('toll_scene');
  },
};

export const CHAPTER2: SceneDef[] = [market, teahouse, gate1];

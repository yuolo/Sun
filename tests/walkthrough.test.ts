import { describe, expect, it } from 'vitest';
import { LEXICON } from '../src/content/lexicon';
import { PAGES } from '../src/content/pages';
import { HeadlessGame } from '../src/core/headless';
import { currentHint } from '../src/core/hints';
import { pageStatus, place, see, submitPage } from '../src/core/journal';
import type { Cup } from '../src/core/types';

const tea = (size: 'big' | 'small'): Cup => ({ drink: 'tea', size });
const water = (size: 'big' | 'small' = 'small'): Cup => ({ drink: 'water', size });

async function tray(game: HeadlessGame, cups: Cup[]) {
  game.c.trays.push(cups);
  await game.click('counter');
  expect(game.state.tray).toEqual(cups);
}

function lastLine(game: HeadlessGame): string {
  return game.c.transcript.filter((l) => !l.startsWith('*') && !l.startsWith('>')).at(-1) ?? '';
}

/** Chapter 1 up to the lantern, shared by several tests. */
async function playVillage(game: HeadlessGame) {
  await game.start();
  await game.exit('village');
  await game.talk('woman');
  await game.talk('oldman');
  await game.talk('lanternman');
  await game.click('bucket');
  await game.click('woodpile');
  await game.use('wood', 'oldman');
  expect(game.state.flags.fire_lit).toBe(true);
  await game.click('campfire');
  await game.use('torch', 'lanternman');
  expect(game.c.has('lantern')).toBe(true);
}

describe('full playthrough', () => {
  it('reaches the sunrise and makes every glyph confirmable', async () => {
    const game = new HeadlessGame();
    const s = game.state;

    /* ---------------- Chapter 1 ---------------- */
    await game.start();
    expect(s.scene).toBe('1a');
    expect(game.c.events).toContain('chapter:1');
    await game.talk('boatman');
    await game.exit('village');
    await game.talk('woman');
    await game.talk('kid');
    await game.click('bucket');
    await game.use('bucket', 'woman');
    expect(lastLine(game)).toBe('woman: 不。我要水。');
    await game.click('woodpile');
    await game.use('wood', 'lanternman');
    expect(lastLine(game)).toBe('lanternman: 不要木。我要火。');
    await game.use('wood', 'oldman');
    await game.click('campfire');
    expect(game.c.has('torch')).toBe(true);
    await game.use('torch', 'lanternman');
    expect(game.c.has('lantern')).toBe(true);
    await game.exit('pier');
    await game.click('river');
    expect(game.c.has('water')).toBe(true);
    await game.exit('village');
    await game.use('water', 'woman');
    expect(s.coins).toBe(3);
    await game.exit('arch');
    expect(s.flags.arch_scene).toBe(true);
    game.answer('我要水');
    await game.talk('guard');
    expect(lastLine(game)).toBe('guard: ……？');
    game.answer('上山');
    expect(await game.exit('stairs')).toBe(true);

    /* ---------------- Chapter 2 ---------------- */
    expect(s.scene).toBe('2a');
    expect(game.c.events).toContain('chapter:2');
    for (const n of '一二三四五六七八九十') expect(s.seen[n], n).toBeTruthy();
    await game.talk('porter');
    await game.exit('teahouse');
    expect(s.flags.orders_heard).toBe(true);
    await game.talk('owner');
    expect(game.c.has('tray')).toBe(true);

    await tray(game, [tea('small')]);
    await game.use('tray', 'bigman');
    expect(lastLine(game)).toBe('bigman: 不！大杯！');
    await tray(game, [water()]);
    await game.use('tray', 'bigman');
    expect(lastLine(game)).toBe('bigman: 不要水！我要茶。');
    await tray(game, [tea('big')]);
    await game.use('tray', 'bigman');
    expect(s.flags.served_bigman).toBe(true);
    await tray(game, [tea('small')]);
    await game.use('tray', 'husband');
    expect(lastLine(game)).toBe('lady: 不！两小杯茶。');
    await tray(game, [tea('small'), tea('small')]);
    await game.use('tray', 'lady');
    await tray(game, [water(), water('big'), water()]);
    await game.use('tray', 'monk2');
    expect(s.flags.tea_job).toBe(true);
    expect(s.coins).toBe(13);

    await tray(game, [tea('big')]);
    await game.exit('market');
    await game.use('tray', 'porter');
    expect(s.flags.porter_tea).toBe(true);
    await game.exit('teahouse');
    await game.exit('gate');
    expect(s.scene).toBe('2c');
    expect(s.flags.toll_scene).toBe(true);
    game.answer('没有');
    await game.talk('keeper');
    expect(lastLine(game)).toBe('keeper: 没有钱，不上山。');
    game.answer('我有钱');
    expect(await game.exit('gate')).toBe(true);
    expect(s.coins).toBe(3);
    expect(game.c.has('tray')).toBe(false);

    /* ---------------- Chapter 3 ---------------- */
    expect(s.scene).toBe('3a');
    expect(s.flags.ch3_intro).toBe(true);
    expect(await game.exit('stairs')).toBe(false);
    await game.click('bells');
    expect(s.flags.bells_solved).toBe(true);
    expect(s.seen['月']).toBeTruthy();
    expect(await game.exit('stairs')).toBe(true);
    await game.talk('porter');
    await game.talk('tired');
    await game.exit('up');

    /* ---------------- Chapter 4 ---------------- */
    expect(s.scene).toBe('4a');
    await game.click('doors');
    expect(lastLine(game)).toBe('gatekeeper: 门不开。');
    game.answer('我要看日出');
    await game.talk('gatekeeper');
    expect(s.flags.gate_open).toBe(true);
    await game.exit('through');
    for (let i = 0; i < 3; i++) await game.talk('geomancer');
    await game.exit('west');
    await game.talk('poet');
    await game.talk('poet');
    expect(s.flags.poet_wrote).toBe(true);
    await game.exit('back');
    await game.exit('north');
    game.c.solver.stele = () => '我看日出';
    await game.click('stele');
    expect(s.inscription).toBe('我看日出');
    await game.click('qin');
    expect(s.flags.ancient_done).toBe(true);
    await game.talk('scholar');
    expect(s.flags.compose_done).toBe(true);
    await game.exit('back');
    await game.exit('east');
    expect(s.scene).toBe('4e');
    await game.click('altar');
    expect(s.flags.sunrise).toBe(true);
    expect(s.finished).toBe(true);

    /* ---------------- Journal ---------------- */
    for (const page of PAGES) {
      expect(pageStatus(s, page), page.id).toBe('open');
      page.glyphs.forEach((g, i) => place(s, page, i, g));
      expect(submitPage(s, page).correct).toBe(true);
    }
    for (const g of LEXICON) expect(s.confirmed[g.ch], g.ch).toBe(true);
  });
});

describe('dead ends are impossible', () => {
  it('the guard asks for fire until the player has the lantern', async () => {
    const game = new HeadlessGame();
    await game.start();
    await game.exit('village');
    await game.exit('arch');
    game.answer('上山');
    expect(await game.exit('stairs')).toBe(false);
    expect(lastLine(game)).toBe('guard: 上山……要火。');
    expect(currentHint(game.state)).toMatch(/Женщина|Старику|лучину/);
  });

  it('the torch goes out when leaving the village', async () => {
    const game = new HeadlessGame();
    await game.start();
    await game.exit('village');
    await game.click('woodpile');
    await game.use('wood', 'oldman');
    await game.click('campfire');
    expect(game.c.has('torch')).toBe(true);
    await game.exit('arch');
    expect(game.c.has('torch')).toBe(false);
    await game.exit('back');
    await game.click('campfire');
    expect(game.c.has('torch')).toBe(true);
  });

  it('the toll needs ten coins, the tea house pays them', async () => {
    const game = new HeadlessGame();
    await playVillage(game);
    await game.exit('arch');
    game.answer('上');
    await game.exit('stairs');
    await game.exit('teahouse');
    await game.exit('gate');
    game.answer('有');
    expect(await game.exit('gate')).toBe(false);
    expect(lastLine(game)).toBe('keeper: 你没有钱。');
    expect(game.state.scene).toBe('2c');
  });

  it('the south gate stays shut after a refusal and opens after a yes', async () => {
    const game = new HeadlessGame();
    game.state.flags = { ch4: true };
    game.state.inventory = ['lantern'];
    see(game.state, '不');
    await game.c.goto('4a', 'bottom');
    game.answer('不看');
    await game.talk('gatekeeper');
    expect(game.state.flags.gate_open).toBeUndefined();
    game.answer('看');
    await game.talk('gatekeeper');
    expect(game.state.flags.gate_open).toBe(true);
  });

  it('the altar needs the dawn character', async () => {
    const game = new HeadlessGame();
    game.state.flags = { ch4: true, gate_open: true };
    await game.c.goto('4e', 'west');
    game.c.solver.compose = () => ['明'];
    await game.click('altar');
    expect(game.state.flags.sunrise).toBeUndefined();
    game.c.solver.compose = (req) => req.targets;
    await game.click('altar');
    expect(game.state.finished).toBe(true);
  });
});

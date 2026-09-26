#!/usr/bin/env node
/**
 * Plays the whole game in a real browser through the UI: clicks on people,
 * uses items, answers questions, solves every journal page and puzzle, and
 * checks that the sunrise and the ending are reached without page errors.
 *
 *   npm run build && npm run preview      # in one terminal
 *   npm run e2e                           # in another
 *
 * Environment:
 *   E2E_URL     game URL with ?debug (default http://localhost:4173/?debug)
 *   CHROMIUM    path to a Chromium binary (default: Playwright's own)
 *   E2E_SHOTS   directory for screenshots (default: none)
 */
import { mkdirSync } from 'node:fs';
import { chromium } from 'playwright-core';

const URL = process.env.E2E_URL ?? 'http://localhost:4173/?debug';
const SHOTS = process.env.E2E_SHOTS;
if (SHOTS) mkdirSync(SHOTS, { recursive: true });

const browser = await chromium.launch(process.env.CHROMIUM ? { executablePath: process.env.CHROMIUM } : {});
const page = await browser.newPage({ viewport: { width: 1600, height: 900 } });
const errors = [];
page.on('console', (m) => {
  if (m.type() === 'error' && !m.text().includes('favicon')) errors.push(`console: ${m.text()}`);
});
page.on('pageerror', (e) => errors.push(`pageerror: ${e.message}`));

const wait = (ms) => page.waitForTimeout(ms);
let shotN = 0;
async function shot(name) {
  if (!SHOTS) return;
  shotN++;
  await page.screenshot({ path: `${SHOTS}/${String(shotN).padStart(2, '0')}-${name}.png` });
}
function check(cond, msg) {
  console.log(`${cond ? 'ok  ' : 'FAIL'} ${msg}`);
  if (!cond) errors.push(`check failed: ${msg}`);
}
const state = () => page.evaluate(() => JSON.parse(JSON.stringify(window.__richu.app.state)));
const scene = async () => (await state()).scene;

/** Advance bubbles and cards until the game waits for the player again. */
async function settle(maxMs = 25000, allowModal = false) {
  const t0 = Date.now();
  let idle = 0;
  while (Date.now() - t0 < maxMs) {
    const st = await page.evaluate(() => ({
      catcher: document.querySelector('.catcher')?.classList.contains('on'),
      busy: document.body.classList.contains('busy'),
      modal: !!document.querySelector('.backdrop:not(.closing)'),
      chapter: !!document.querySelector('.chapter-card'),
      curtain: document.querySelector('.curtain')?.classList.contains('on'),
    }));
    if (st.modal && !allowModal) return 'modal';
    if (st.chapter) {
      await page.locator('.chapter-card').click({ force: true });
      await wait(800);
      idle = 0;
    } else if (st.catcher) {
      await page.keyboard.press('Space');
      await wait(250);
      idle = 0;
    } else {
      if (!st.busy && !st.curtain && ++idle > 3) return 'idle';
      await wait(150);
    }
  }
  return 'timeout';
}

async function click(selector) {
  await page.locator(selector).first().click({ force: true });
  await wait(100);
  return settle();
}
const actor = (id) => click(`.actor[data-id="${id}"] .hit`);
const hot = (id) => click(`.hotspot[data-id="${id}"]`);
const exit = (id) => click(`.exit[data-id="${id}"]`);
const item = (name) => page.locator(`.inventory .item[aria-label="${name}"]`).click();

async function answer(text) {
  await page.waitForSelector('.composer-modal');
  for (const ch of text) await page.locator(`.composer-modal .palette-glyph[aria-label="Добавить ${ch}"]`).click();
  await page.locator('.composer-modal button.primary').click();
  return settle();
}

async function solvePage(title, glyphs) {
  await page.locator('.hud .journal-btn').click();
  await page.locator('.journal-tabs .tab', { hasText: 'Страницы' }).click();
  await page.locator('.page-item').filter({ has: page.locator('.page-title', { hasText: new RegExp(`^${title}$`) }) }).click();
  for (let i = 0; i < glyphs.length; i++) {
    await page.locator(`.pool-glyph[aria-label="Знак ${glyphs[i]}"]`).click();
    await page.locator('.slot').nth(i).click();
  }
  await wait(500);
  await shot(`page-${title}`);
  check((await page.locator('.seal').count()) === 1, `page «${title}» confirmed`);
  await page.keyboard.press('Escape');
  await wait(300);
}

async function tray(cups) {
  await hot('counter');
  await page.waitForSelector('.tray-puzzle');
  for (const [drink, size] of cups) {
    await page.locator(`.jar[aria-label="Кувшин с надписью ${drink}"]`).click();
    await page.locator(`.cup-btn[aria-label="${size === 'big' ? 'Большая чашка' : 'Маленькая чашка'}"]`).click();
  }
  await page.getByRole('button', { name: 'Взять поднос' }).click();
  await settle();
  await item('Поднос');
}

async function build(a, b, layout) {
  await page.locator(`.compose-puzzle .palette-glyph[aria-label="Часть ${a}"]`).click();
  await page.locator(`.compose-puzzle .palette-glyph[aria-label="Часть ${b}"]`).click();
  await page.locator('.layout-btns button').nth(layout === 'lr' ? 0 : 1).click();
  await page.getByRole('button', { name: 'Сложить' }).click();
  await wait(1500);
}

/* ------------------------------------------------------------------ */

await page.goto(URL, { waitUntil: 'networkidle' });
await page.evaluate(() => localStorage.clear());
await page.reload({ waitUntil: 'networkidle' });
await page.getByRole('button', { name: 'Новая игра' }).click();
await wait(600);
await page.locator('.prologue').click();
await wait(900);
await settle();
check((await scene()) === '1a', 'chapter 1: the pier');
await actor('boatman');

await exit('village');
await actor('woman');
await actor('oldman');
await actor('lanternman');
await hot('bucket');
await hot('woodpile');
await item('Дрова');
await actor('oldman');
await hot('campfire');
await item('Лучина');
await actor('lanternman');
check((await state()).inventory.includes('lantern'), 'got the lantern');
await exit('pier');
await item('Ведро');
await hot('river');
await exit('village');
await item('Ведро с водой');
await actor('woman');
check((await state()).coins === 3, 'the woman paid 3 coins');
await exit('arch');
await shot('arch');
await solvePage('Стихии', ['山', '水', '火', '木']);
await solvePage('Люди', ['你', '我', '好', '谢']);
await solvePage('Путь', ['上', '下', '要', '不', '吗']);
await actor('guard');
await answer('上山');
await exit('stairs');

check((await scene()) === '2a', 'chapter 2: the market');
await actor('porter');
await exit('teahouse');
await actor('owner');
await tray([['茶', 'big']]);
await actor('bigman');
await tray([['茶', 'small'], ['茶', 'small']]);
await actor('lady');
await tray([['水', 'small'], ['水', 'small'], ['水', 'big']]);
await actor('monk');
check((await state()).coins === 13, 'the tea house paid 10 coins');
await hot('counter');
await page.locator('.jar[aria-label="Кувшин с надписью 茶"]').click();
await page.locator('.cup-btn[aria-label="Маленькая чашка"]').click();
await page.getByRole('button', { name: 'Взять поднос' }).click();
await settle();
await exit('market');
await item('Поднос');
await actor('porter');
check((await state()).flags.porter_tea === true, 'the porter got his tea');
await exit('teahouse');
await exit('gate');
await shot('gate');
await solvePage('Счёт I', ['一', '二', '三', '四', '五']);
await solvePage('Счёт II', ['六', '七', '八', '九', '十']);
await solvePage('Чайная', ['茶', '杯', '大', '小', '钱']);
await solvePage('Торг', ['有', '没', '几', '两', '人']);
await actor('keeper');
await answer('我有钱');
await exit('gate');

check((await scene()) === '3a', 'chapter 3: the Midway Gate');
await hot('bells');
await page.waitForSelector('.bells-puzzle');
for (const i of [2, 5, 4]) {
  await page.locator('.bell-btn').nth(i).click();
  await wait(300);
}
await page.waitForSelector('.bells-puzzle', { state: 'detached' });
await settle();
check((await state()).flags.bells_solved === true, 'the bells are solved');
await shot('night');
await solvePage('Небо', ['日', '月', '云', '雨', '天']);
await exit('stairs');
await actor('porter');
await exit('up');

check((await scene()) === '4a', 'chapter 4: the South Gate');
await hot('doors');
await actor('gatekeeper');
await answer('我要看日出');
await exit('through');
for (let i = 0; i < 3; i++) await actor('geomancer');
await solvePage('Путь в небо', ['中', '门', '看']);
await exit('west');
await actor('poet');
await actor('poet');
await exit('back');
await solvePage('Стороны света', ['东', '西', '南', '北']);
await solvePage('Рассвет', ['开', '出', '明']);
await exit('north');
await actor('scholar');
await page.waitForSelector('.compose-puzzle');
await build('人', '木', 'lr');
await build('木', '木', 'lr');
await page.waitForSelector('.compose-puzzle', { state: 'detached' });
await settle();
check((await state()).flags.compose_done === true, 'characters built from parts');
await exit('back');
await exit('east');
await hot('altar');
await page.waitForSelector('.compose-puzzle');
await build('日', '一', 'tb');
await page.waitForSelector('.compose-puzzle', { state: 'detached' });
await settle(40000);
await shot('ending');
check((await page.locator('.ending-modal').count()) === 1, 'the ending is shown');
const final = await state();
check(final.finished === true, 'the game is finished');
check(Object.keys(final.confirmed).length === 51, 'all 51 glyphs confirmed');

await browser.close();
if (errors.length) {
  console.error(errors.join('\n'));
  process.exit(1);
}
console.log('playthrough complete, no errors');

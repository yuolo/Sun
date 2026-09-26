import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { describe, expect, it } from 'vitest';
import { hasIllustration, tabletPicture } from '../src/art/illustrations';
import { GRAMMAR } from '../src/content/grammar';
import { HINTS } from '../src/content/hints';
import { ITEMS } from '../src/content/items';
import { LEXICON, inLexicon } from '../src/content/lexicon';
import { PAGES } from '../src/content/pages';
import { RECIPES } from '../src/content/recipes';
import { CHAPTERS, SCENES, hasScene } from '../src/content/world';
import { isHan } from '../src/core/phrases';
import { createState } from '../src/core/state';

const CHAPTER_DIR = join(__dirname, '../src/content/chapters');

describe('lexicon', () => {
  it('has 51 unique single characters with pinyin and meaning', () => {
    expect(LEXICON).toHaveLength(51);
    expect(new Set(LEXICON.map((g) => g.ch)).size).toBe(LEXICON.length);
    for (const g of LEXICON) {
      expect([...g.ch]).toHaveLength(1);
      expect(g.pinyin).toMatch(/^[a-zāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜü']+$/);
      expect(g.meaning.length).toBeGreaterThan(0);
      expect(g.origin.length).toBeGreaterThan(0);
    }
  });

  it('marks tones consistently with the pinyin', () => {
    const marks: Record<number, RegExp> = { 1: /[āēīōūǖ]/, 2: /[áéíóúǘ]/, 3: /[ǎěǐǒǔǚ]/, 4: /[àèìòùǜ]/ };
    for (const g of LEXICON) {
      if (g.tone === 0) expect(g.pinyin).not.toMatch(/[āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ]/);
      else expect(g.pinyin).toMatch(marks[g.tone]);
    }
  });

  it('every glyph can be confirmed by exactly one page or one recipe', () => {
    for (const g of LEXICON) {
      const pages = PAGES.filter((p) => p.glyphs.includes(g.ch)).length;
      const recipes = RECIPES.filter((r) => r.result === g.ch && !PAGES.some((p) => p.glyphs.includes(g.ch))).length;
      expect(pages + recipes, g.ch).toBe(1);
    }
  });
});

describe('pages, grammar, recipes', () => {
  it('pages hold 3–5 lexicon glyphs with illustrations', () => {
    expect(new Set(PAGES.map((p) => p.id)).size).toBe(PAGES.length);
    for (const p of PAGES) {
      expect(p.glyphs.length).toBeGreaterThanOrEqual(3);
      expect(p.glyphs.length).toBeLessThanOrEqual(5);
      for (const g of p.glyphs) {
        expect(inLexicon(g), g).toBe(true);
        expect(hasIllustration(g), g).toBe(true);
      }
    }
  });

  it('grammar notes require lexicon glyphs and quote only lexicon glyphs', () => {
    for (const note of GRAMMAR) {
      for (const g of note.requires) expect(inLexicon(g), g).toBe(true);
      for (const [zh] of note.examples) for (const ch of zh) if (isHan(ch)) expect(inLexicon(ch), `${note.id}: ${ch}`).toBe(true);
    }
  });

  it('recipes use lexicon parts and have tablet pictures', () => {
    for (const r of RECIPES) {
      for (const g of [r.a, r.b, r.result]) expect(inLexicon(g), g).toBe(true);
      expect(tabletPicture(r.result).length).toBeGreaterThan(0);
    }
  });
});

describe('scenes', () => {
  it('all hanzi in the chapter scripts are in the lexicon', () => {
    for (const file of readdirSync(CHAPTER_DIR)) {
      const src = readFileSync(join(CHAPTER_DIR, file), 'utf8').replace(/\/\*[\s\S]*?\*\/|\/\/.*$/gm, '');
      for (const ch of src) if (isHan(ch)) expect(inLexicon(ch), `${file}: ${ch}`).toBe(true);
    }
  });

  it('have unique ids and valid exits, entries and chapter starts', () => {
    expect(new Set(SCENES.map((s) => s.id)).size).toBe(SCENES.length);
    for (const scene of SCENES) {
      expect(scene.path.length).toBeGreaterThanOrEqual(2);
      for (const e of scene.exits) {
        expect(hasScene(e.to), `${scene.id} → ${e.to}`).toBe(true);
        const target = SCENES.find((s) => s.id === e.to)!;
        expect(target.entries[e.entry], `${scene.id} → ${e.to}:${e.entry}`).toBeTypeOf('number');
      }
      const ids = [...scene.actors.map((a) => a.id), ...scene.hotspots.map((h) => h.id)];
      expect(new Set(ids).size, scene.id).toBe(ids.length);
    }
    for (const c of CHAPTERS) expect(SCENES.find((s) => s.id === c.start.scene)?.entries[c.start.entry]).toBeTypeOf('number');
  });

  it('render art for their initial state without throwing', () => {
    const s = createState(0);
    for (const scene of SCENES) {
      const look = scene.look(s);
      expect(scene.art(s, look)).toMatch(/^<svg/);
      if (scene.front) expect(scene.front(s, look)).toMatch(/^<svg/);
    }
  });

  it('every item has a definition', () => {
    const ids = new Set(ITEMS.map((i) => i.id));
    for (const file of readdirSync(CHAPTER_DIR)) {
      const src = readFileSync(join(CHAPTER_DIR, file), 'utf8');
      for (const m of src.matchAll(/c\.give\('([a-z]+)'\)/g)) expect(ids.has(m[1]), m[1]).toBe(true);
    }
  });

  it('hints are Russian text', () => {
    for (const h of HINTS) expect(h.text).toMatch(/[а-я]/);
  });
});

import { describe, expect, it } from 'vitest';
import { PAGES, pageDef } from '../src/content/pages';
import { checkPage, confirmGlyphs, grammarUnlocked, missingCount, pageStatus, place, placementsFor, poolOrder, see, setGuess, submitPage } from '../src/core/journal';
import { fromHanzi, toHanzi } from '../src/core/numerals';
import { contains, glyphsOf, matchesAny, normalizeAnswer } from '../src/core/phrases';
import { BELL_CHANT, addCup, checkAncient, checkOrder, compose, ringBell, MAX_TRAY } from '../src/core/puzzles';
import { SAVE_KEY, createState, deserialize, loadFrom, restoreState, saveTo, serialize } from '../src/core/state';

describe('phrases', () => {
  it('extracts unique glyphs in order', () => {
    expect(glyphsOf('你好！你上山吗？')).toEqual(['你', '好', '上', '山', '吗']);
  });

  it('normalizes answers ignoring punctuation', () => {
    expect(normalizeAnswer(' 我，上山！')).toBe('我上山');
    expect(matchesAny('上山。', ['上', '上山'])).toBe(true);
    expect(matchesAny('山上', ['上山'])).toBe(false);
    expect(contains('我不上山', '不')).toBe(true);
  });
});

describe('numerals', () => {
  it('writes numbers in Chinese', () => {
    expect([1, 2, 7, 10, 11, 13, 20, 42, 99].map(toHanzi)).toEqual(['一', '二', '七', '十', '十一', '十三', '二十', '四十二', '九十九']);
  });

  it('round-trips 1–99', () => {
    for (let n = 1; n < 100; n++) expect(fromHanzi(toHanzi(n))).toBe(n);
    expect(fromHanzi('山')).toBeNull();
    expect(fromHanzi('')).toBeNull();
  });

  it('rejects out of range', () => {
    expect(() => toHanzi(100)).toThrow();
  });
});

describe('journal', () => {
  it('registers only lexicon glyphs as seen, in order', () => {
    const s = createState(0);
    expect(see(s, '你好！')).toEqual(['你', '好']);
    expect(see(s, '好吗？')).toEqual(['吗']);
    expect(s.seen['你']).toBe(1);
    expect(s.seen['吗']).toBe(3);
    see(s, '零');
    expect(s.seen['零']).toBeUndefined();
  });

  it('stores trimmed guesses and deletes empty ones', () => {
    const s = createState(0);
    setGuess(s, '水', '  вода ');
    expect(s.guesses['水']).toBe('вода');
    setGuess(s, '水', '   ');
    expect(s.guesses['水']).toBeUndefined();
  });

  it('unlocks a page once every glyph is seen', () => {
    const s = createState(0);
    const page = pageDef('elements')!;
    expect(pageStatus(s, page)).toBe('locked');
    see(s, '山水火');
    expect(missingCount(s, page)).toBe(1);
    see(s, '木');
    expect(pageStatus(s, page)).toBe('open');
  });

  it('keeps a glyph in one slot and validates only full correct pages', () => {
    const s = createState(0);
    const page = pageDef('elements')!;
    see(s, '山水火木');
    place(s, page, 0, '水');
    place(s, page, 1, '水');
    expect(placementsFor(s, page)).toEqual([null, '水', null, null]);
    place(s, page, 0, '山');
    place(s, page, 2, '木');
    place(s, page, 3, '火');
    expect(checkPage(page, placementsFor(s, page))).toEqual({ filled: true, correct: false, wrong: 2 });
    expect(submitPage(s, page).confirmed).toEqual([]);
    place(s, page, 2, '火');
    place(s, page, 3, '木');
    const res = submitPage(s, page);
    expect(res.correct).toBe(true);
    expect(res.confirmed).toEqual(['山', '水', '火', '木']);
    expect(pageStatus(s, page)).toBe('done');
    expect(s.placements[page.id]).toBeUndefined();
  });

  it('ignores glyphs that do not belong to the page', () => {
    const s = createState(0);
    const page = pageDef('elements')!;
    place(s, page, 0, '你');
    expect(placementsFor(s, page)).toEqual([null, null, null, null]);
  });

  it('shuffles pools deterministically and never in answer order', () => {
    for (const page of PAGES) {
      const pool = poolOrder(page);
      expect([...pool].sort()).toEqual([...page.glyphs].sort());
      expect(pool).not.toEqual(page.glyphs);
      expect(poolOrder(page)).toEqual(pool);
    }
  });

  it('unlocks grammar notes by confirmed glyphs', () => {
    const s = createState(0);
    expect(grammarUnlocked(s)).toEqual([]);
    confirmGlyphs(s, ['吗']);
    expect(grammarUnlocked(s).map((g) => g.id)).toEqual(['ma']);
  });
});

describe('tea tray', () => {
  const big = { drink: 'tea', size: 'big' } as const;
  const small = { drink: 'tea', size: 'small' } as const;
  const water = { drink: 'water', size: 'small' } as const;

  it('checks drink, then count, then size', () => {
    expect(checkOrder([], { drink: 'tea', count: 1 })).toEqual({ ok: false, problem: 'empty' });
    expect(checkOrder([water], { drink: 'tea', count: 1 })).toEqual({ ok: false, problem: 'drink' });
    expect(checkOrder([small, small], { drink: 'tea', count: 1, size: 'big' })).toEqual({ ok: false, problem: 'count' });
    expect(checkOrder([small], { drink: 'tea', count: 1, size: 'big' })).toEqual({ ok: false, problem: 'size' });
    expect(checkOrder([big], { drink: 'tea', count: 1, size: 'big' })).toEqual({ ok: true });
    expect(checkOrder([water, water, { drink: 'water', size: 'big' }], { drink: 'water', count: 3 })).toEqual({ ok: true });
  });

  it('caps the tray', () => {
    let cups: ReturnType<typeof addCup> = [];
    for (let i = 0; i < 6; i++) cups = addCup(cups, small);
    expect(cups).toHaveLength(MAX_TRAY);
  });
});

describe('bells', () => {
  it('solves the chant in order and restarts on mistakes', () => {
    expect(BELL_CHANT).toEqual(['雨', '云', '月']);
    let r = ringBell(0, 'rain');
    expect(r).toEqual({ progress: 1, result: 'progress' });
    r = ringBell(r.progress, 'sun');
    expect(r).toEqual({ progress: 0, result: 'wrong' });
    r = ringBell(1, 'rain');
    expect(r).toEqual({ progress: 1, result: 'restart' });
    r = ringBell(r.progress, 'cloud');
    r = ringBell(r.progress, 'moon');
    expect(r).toEqual({ progress: 3, result: 'solved' });
  });
});

describe('composition', () => {
  it('builds characters from parts with the right layout and order', () => {
    expect(compose('日', '月', 'lr')).toBe('明');
    expect(compose('人', '木', 'lr')).toBe('休');
    expect(compose('木', '人', 'lr')).toBeNull();
    expect(compose('木', '木', 'lr')).toBe('林');
    expect(compose('日', '一', 'tb')).toBe('旦');
    expect(compose('日', '一', 'lr')).toBeNull();
  });

  it('checks the ancient stele pairs', () => {
    expect(checkAncient({ 日: '日', 月: '月', 山: '山', 水: '水', 人: '人', 木: '木' })).toBe(true);
    expect(checkAncient({ 日: '月', 月: '日', 山: '山', 水: '水', 人: '人', 木: '木' })).toBe(false);
  });
});

describe('state', () => {
  it('round-trips through JSON', () => {
    const s = createState(5);
    s.flags.x = true;
    s.coins = 7;
    expect(deserialize(serialize(s))).toEqual(s);
  });

  it('fills in missing fields and rejects garbage', () => {
    expect(restoreState(null)).toBeNull();
    expect(restoreState({ nope: 1 })).toBeNull();
    expect(deserialize('{broken')).toBeNull();
    const s = restoreState({ scene: '2a', coins: 'x', settings: { music: false } })!;
    expect(s.coins).toBe(0);
    expect(s.settings.music).toBe(false);
    expect(s.settings.pinyin).toBe(true);
    expect(s.inventory).toEqual([]);
  });

  it('survives a storage that throws', () => {
    const broken = {
      getItem: () => {
        throw new Error('denied');
      },
      setItem: () => {
        throw new Error('denied');
      },
      removeItem: () => {},
    };
    expect(loadFrom(broken)).toBeNull();
    expect(saveTo(broken, createState())).toBe(false);
    expect(loadFrom(undefined)).toBeNull();
  });

  it('saves and loads with a working storage', () => {
    const mem = new Map<string, string>();
    const store = { getItem: (k: string) => mem.get(k) ?? null, setItem: (k: string, v: string) => void mem.set(k, v), removeItem: (k: string) => void mem.delete(k) };
    const s = createState(1);
    s.scene = '3a';
    expect(saveTo(store, s)).toBe(true);
    expect(mem.has(SAVE_KEY)).toBe(true);
    expect(loadFrom(store)?.scene).toBe('3a');
  });
});

import type { Glyph } from '../core/types';
import { circle, ellipse, g, line, path, poly, rect } from './svg';

/** All illustrations live in a 100×100 box. */
const INK = '#3a2f28';
const SOFT = '#8c7b6b';
const RED = '#c0392b';
const GOLD = '#d9a441';
const BLUE = '#4f86a8';
const GREEN = '#6f8f5a';
const ORANGE = '#e8862f';

const S = (w = 3.5) => ({ stroke: INK, 'stroke-width': w, fill: 'none', 'stroke-linecap': 'round' as const, 'stroke-linejoin': 'round' as const });

function person(x: number, y: number, s: number, color = SOFT, extra = ''): string {
  return g(
    { transform: `translate(${x} ${y}) scale(${s})` },
    circle(0, -34, 7, { fill: color }),
    path('M-9 -24 Q0 -28 9 -24 L13 0 L-13 0 Z', { fill: color }),
    extra,
  );
}

function dots(n: number): string {
  const layouts: Record<number, [number, number][]> = {
    1: [[50, 50]],
    2: [[35, 50], [65, 50]],
    3: [[30, 62], [50, 38], [70, 62]],
    4: [[35, 35], [65, 35], [35, 65], [65, 65]],
    5: [[30, 30], [70, 30], [50, 50], [30, 70], [70, 70]],
  };
  const pts: [number, number][] = [];
  if (n <= 5) pts.push(...layouts[n]);
  else {
    for (let i = 0; i < 5; i++) pts.push([18 + i * 16, 36]);
    for (let i = 0; i < n - 5; i++) pts.push([18 + i * 16, 64]);
  }
  return g({}, ...pts.map(([x, y]) => circle(x, y, n <= 5 ? 9 : 6.5, { fill: '#b8733a', stroke: '#7a4a1c', 'stroke-width': 1.5 })));
}

function compass(dir: 'n' | 's' | 'e' | 'w', extra = ''): string {
  const arrows = {
    n: 'M50 50 L44 50 L50 16 L56 50 Z',
    s: 'M50 50 L44 50 L50 84 L56 50 Z',
    e: 'M50 50 L50 44 L84 50 L50 56 Z',
    w: 'M50 50 L50 44 L16 50 L50 56 Z',
  };
  return g(
    {},
    circle(50, 50, 38, { fill: '#f1e4c4', stroke: SOFT, 'stroke-width': 2 }),
    ...(['n', 's', 'e', 'w'] as const).map((k) => path(arrows[k], { fill: k === dir ? RED : '#cdbfa6' })),
    circle(50, 50, 4, { fill: INK }),
    extra,
  );
}

function cupShape(x: number, y: number, s: number, hi: boolean): string {
  return g(
    { transform: `translate(${x} ${y}) scale(${s})` },
    path('M-16 -20 L-11 0 L11 0 L16 -20 Z', { fill: '#efe7d4', stroke: hi ? GOLD : SOFT, 'stroke-width': hi ? 3.5 : 2 }),
    path('M-13 -11 H13', { stroke: BLUE, 'stroke-width': 2 }),
  );
}

function sun(x: number, y: number, r: number, rays = true): string {
  const out = [circle(x, y, r, { fill: '#f2b33d' })];
  if (rays) for (let i = 0; i < 8; i++) {
    const a = (i / 8) * Math.PI * 2;
    out.push(line(x + Math.cos(a) * (r + 5), y + Math.sin(a) * (r + 5), x + Math.cos(a) * (r + 13), y + Math.sin(a) * (r + 13), { stroke: '#f2b33d', 'stroke-width': 3.5, 'stroke-linecap': 'round' }));
  }
  return g({}, ...out);
}

function moon(x: number, y: number, r: number): string {
  return path(`M${x + r * 0.2} ${y - r} A${r} ${r} 0 1 0 ${x + r * 0.2} ${y + r} A${r * 1.3} ${r * 1.3} 0 0 1 ${x + r * 0.2} ${y - r} Z`, { fill: '#e9c95a' });
}

function cloud(x: number, y: number, s: number, color = '#c9d3dc'): string {
  return g({ transform: `translate(${x} ${y}) scale(${s})` }, ellipse(0, 0, 30, 10, { fill: color }), circle(-12, -6, 12, { fill: color }), circle(6, -12, 15, { fill: color }), circle(20, -3, 10, { fill: color }));
}

function tree(x: number, y: number, s: number): string {
  return g({ transform: `translate(${x} ${y}) scale(${s})` }, path('M-4 0 L-3 -30 L3 -30 L4 0 Z', { fill: '#7a5634' }), path('M-3 -2 l-8 4 M3 -2 l8 4', { stroke: '#7a5634', 'stroke-width': 2.5 }), circle(0, -42, 17, { fill: GREEN }), circle(-10, -34, 10, { fill: '#5d7c4a' }), circle(10, -34, 10, { fill: '#5d7c4a' }));
}

function gateIcon(open: boolean): string {
  return g(
    {},
    rect(18, 30, 64, 58, { fill: '#8a5a3a' }),
    path('M12 30 Q50 14 88 30 Z', { fill: '#5a6068' }),
    open
      ? g({}, rect(26, 38, 48, 50, { fill: '#ffd98a' }), path('M26 38 L14 44 L14 92 L26 88 Z', { fill: RED }), path('M74 38 L86 44 L86 92 L74 88 Z', { fill: RED }))
      : g({}, rect(26, 38, 24, 50, { fill: RED }), rect(50, 38, 24, 50, { fill: '#a8322a' }), circle(46, 64, 2.5, { fill: GOLD }), circle(54, 64, 2.5, { fill: GOLD })),
  );
}

const PICS: Record<Glyph, () => string> = {
  /* Стихии */
  山: () => g({}, poly([[8, 84], [34, 38], [52, 64], [66, 26], [92, 84]], { fill: '#7f9690' }), poly([[34, 38], [28, 49], [40, 49]], { fill: '#f1ece0' }), poly([[66, 26], [60, 38], [72, 38]], { fill: '#f1ece0' }), line(4, 86, 96, 86, S(3))),
  水: () => g({}, path('M14 40 q9 -10 18 0 t18 0 t18 0 t18 0', { ...S(5), stroke: BLUE }), path('M14 58 q9 -10 18 0 t18 0 t18 0 t18 0', { ...S(5), stroke: BLUE }), path('M14 76 q9 -10 18 0 t18 0 t18 0 t18 0', { ...S(5), stroke: '#7fb3cf' }), path('M50 8 Q60 22 50 28 Q40 22 50 8 Z', { fill: BLUE })),
  火: () => g({}, path('M50 10 Q76 36 72 62 Q70 88 50 90 Q30 88 28 64 Q26 46 40 34 Q40 52 48 54 Q42 34 50 10 Z', { fill: ORANGE }), path('M50 50 Q62 64 58 76 Q54 86 50 86 Q42 84 42 74 Q42 64 50 50 Z', { fill: '#ffd36b' })),
  木: () => g({}, tree(40, 86, 1.25), g({ transform: 'translate(78 80)' }, ellipse(0, 0, 14, 7, { fill: '#9a6c42' }), ellipse(-10, 0, 5, 7, { fill: '#d9b27a' }), ellipse(0, -12, 12, 6, { fill: '#8a5c32' }), ellipse(-9, -12, 4, 6, { fill: '#d9b27a' }))),
  /* Люди */
  你: () => g({}, person(28, 86, 1.2, SOFT), person(74, 86, 1.2, RED), path('M36 50 L60 50', { ...S(3.5), stroke: INK }), path('M54 44 L62 50 L54 56', S(3.5))),
  我: () => g({}, person(50, 88, 1.5, RED), path('M72 46 Q60 40 56 50', S(3.5)), path('M58 42 L55 51 L64 50', S(3))),
  好: () => g({}, path('M34 50 L34 84 L70 84 Q78 84 78 76 L82 56 Q84 48 74 48 L58 48 L62 30 Q63 20 55 20 L42 48 Z', { fill: '#e2bf98', stroke: INK, 'stroke-width': 2.5 }), rect(20, 48, 14, 38, { fill: RED, rx: 2 }), path('M80 16 l3 8 l8 3 l-8 3 l-3 8 l-3 -8 l-8 -3 l8 -3 z', { fill: GOLD })),
  谢: () => g({}, g({ transform: 'translate(50 88) rotate(-18) scale(1.45)' }, circle(0, -34, 7, { fill: SOFT }), path('M-9 -24 Q0 -28 9 -24 L13 0 L-13 0 Z', { fill: SOFT })), circle(66, 52, 7, { fill: '#e2bf98', stroke: INK, 'stroke-width': 2 }), path('M24 22 q6 -8 12 0 q6 -8 12 0 q0 8 -12 16 q-12 -8 -12 -16z', { fill: RED })),
  /* Путь */
  上: () => g({}, path('M12 86 H32 V70 H52 V54 H72 V38 H90', S(4)), path('M40 34 L40 10 M30 20 L40 8 L50 20', { ...S(5), stroke: RED })),
  下: () => g({}, path('M10 38 H28 V54 H48 V70 H68 V86 H88', S(4)), path('M62 10 L62 36 M52 26 L62 38 L72 26', { ...S(5), stroke: RED })),
  要: () => g({}, g({ transform: 'translate(70 62)' }, path('M-20 0 Q0 22 20 0 Z', { fill: '#b8733a' }), ellipse(0, 0, 20, 5, { fill: '#8a5a2a' })), path('M8 70 Q20 60 34 58 L48 56', { ...S(7), stroke: '#e2bf98' }), path('M44 50 L52 56 L44 62', S(3)), path('M60 34 q4 -8 0 -14 M72 32 q4 -8 0 -14 M84 34 q4 -8 0 -14', { ...S(2.5), stroke: SOFT })),
  不: () => g({}, path('M50 34 Q66 44 50 70 Q34 44 50 34 Z', { fill: '#b8733a', opacity: 0.8 }), circle(50, 52, 34, { fill: 'none', stroke: RED, 'stroke-width': 7 }), line(26, 28, 74, 76, { stroke: RED, 'stroke-width': 7 })),
  吗: () => g({}, path('M16 22 H84 Q90 22 90 28 V62 Q90 68 84 68 H44 L28 84 L32 68 H16 Q10 68 10 62 V28 Q10 22 16 22 Z', { fill: '#f7efdc', stroke: INK, 'stroke-width': 3 }), path('M40 36 Q40 28 50 28 Q60 28 60 36 Q60 43 50 46 V52', S(4.5)), circle(50, 59, 2.8, { fill: INK })),
  /* Счёт */
  一: () => dots(1),
  二: () => dots(2),
  三: () => dots(3),
  四: () => dots(4),
  五: () => dots(5),
  六: () => dots(6),
  七: () => dots(7),
  八: () => dots(8),
  九: () => dots(9),
  十: () => dots(10),
  /* Чайная */
  茶: () => g({}, path('M26 48 Q24 84 50 86 Q76 84 74 48 Z', { fill: '#6b8f7a' }), path('M74 56 Q90 54 86 70 Q82 78 72 74', S(4)), path('M26 56 L12 44', { ...S(6), stroke: '#6b8f7a' }), rect(40, 40, 20, 8, { fill: '#56786a' }), path('M40 32 q-4 -8 2 -14 M52 30 q-4 -8 2 -14 M64 32 q-4 -8 2 -14', { ...S(2.5), stroke: SOFT }), path('M82 20 q8 4 6 14 q-10 -2 -6 -14z', { fill: GREEN })),
  杯: () => cupShape(50, 76, 2.4, false),
  大: () => g({}, cupShape(38, 82, 2.6, true), cupShape(80, 82, 1.1, false)),
  小: () => g({}, cupShape(38, 82, 2.6, false), cupShape(80, 82, 1.1, true)),
  钱: () => g({}, ...[[34, 66], [62, 58], [48, 38]].map(([x, y]) => g({}, circle(x, y, 17, { fill: '#c8923a', stroke: '#7a5420', 'stroke-width': 2.5 }), rect(x - 5, y - 5, 10, 10, { fill: '#f6ecd6', stroke: '#7a5420', 'stroke-width': 2 })))),
  /* Торг */
  有: () => g({}, path('M18 60 Q30 88 54 86 Q78 84 84 60 Z', { fill: '#e2bf98', stroke: INK, 'stroke-width': 2.5 }), ...[[40, 52], [58, 50], [50, 38]].map(([x, y]) => g({}, circle(x, y, 11, { fill: '#c8923a', stroke: '#7a5420', 'stroke-width': 2 }), rect(x - 3.5, y - 3.5, 7, 7, { fill: '#f6ecd6' })))),
  没: () => g({}, path('M18 60 Q30 88 54 86 Q78 84 84 60 Z', { fill: '#e2bf98', stroke: INK, 'stroke-width': 2.5 }), circle(50, 44, 11, { fill: 'none', stroke: SOFT, 'stroke-width': 2, 'stroke-dasharray': '4 4' }), path('M22 20 L34 32 M34 20 L22 32', { ...S(3), stroke: RED })),
  几: () => g({}, ...[[24, 70], [42, 76], [60, 70], [78, 76]].map(([x, y]) => circle(x, y, 7, { fill: '#b8733a' })), path('M40 30 Q40 18 50 18 Q60 18 60 28 Q60 36 50 40 V48', S(5)), circle(50, 56, 3, { fill: INK })),
  两: () => g({}, cupShape(34, 76, 1.8, true), cupShape(66, 76, 1.8, true)),
  人: () => g({}, circle(52, 22, 9, { fill: INK }), path('M52 32 L44 58 L30 86 M46 52 L62 86 M48 40 L30 52 M50 40 L68 50', S(6))),
  /* Небо */
  日: () => sun(50, 50, 20),
  月: () => g({}, moon(48, 50, 30), path('M80 20 l2 5 l5 2 l-5 2 l-2 5 l-2 -5 l-5 -2 l5 -2 z', { fill: GOLD }), path('M20 78 l1.5 4 l4 1.5 l-4 1.5 l-1.5 4 l-1.5 -4 l-4 -1.5 l4 -1.5 z', { fill: GOLD })),
  云: () => g({}, cloud(48, 58, 1.5, '#b9c6d2'), cloud(66, 40, 0.8, '#d7dee6')),
  雨: () => g({}, cloud(50, 36, 1.4, '#8fa0b2'), ...[[28, 58], [44, 64], [60, 58], [76, 64], [36, 80], [52, 84], [68, 80]].map(([x, y]) => line(x, y, x - 4, y + 10, { stroke: BLUE, 'stroke-width': 3.5, 'stroke-linecap': 'round' }))),
  天: () => g({}, path('M6 80 Q50 -10 94 80', { fill: '#cfe0ec', stroke: BLUE, 'stroke-width': 3 }), line(4, 80, 96, 80, S(3)), person(50, 80, 0.75, INK), path('M24 34 l1.5 4 l4 1.5 l-4 1.5 l-1.5 4 l-1.5 -4 l-4 -1.5 l4 -1.5 z', { fill: GOLD })),
  /* Путь в небо */
  中: () => g({}, rect(10, 38, 22, 24, { fill: '#d9ccb2' }), rect(39, 34, 22, 32, { fill: RED }), rect(68, 38, 22, 24, { fill: '#d9ccb2' }), line(50, 18, 50, 82, S(3))),
  门: () => gateIcon(false),
  看: () => g({}, path('M14 60 Q50 30 86 60 Q50 90 14 60 Z', { fill: '#f7efdc', stroke: INK, 'stroke-width': 3 }), circle(50, 60, 12, { fill: '#5a4636' }), circle(54, 56, 3.5, { fill: '#fff' }), path('M18 34 Q50 14 84 34 L78 40 Q50 24 22 40 Z', { fill: '#e2bf98', stroke: INK, 'stroke-width': 2 })),
  /* Стороны света */
  东: () => compass('e', sun(86, 18, 7, false)),
  西: () => compass('w', moon(14, 18, 8)),
  南: () => compass('s'),
  北: () => compass('n'),
  /* Рассвет */
  开: () => gateIcon(true),
  出: () => g({}, rect(12, 26, 44, 60, { fill: '#8a5a3a' }), rect(20, 34, 28, 52, { fill: '#2a2320' }), path('M34 60 H86 M74 48 L88 60 L74 72', { ...S(6), stroke: RED })),
  明: () => g({}, circle(50, 52, 30, { fill: '#fff3c4' }), circle(50, 52, 18, { fill: '#ffe08a' }), ...Array.from({ length: 12 }, (_, i) => {
    const a = (i / 12) * Math.PI * 2;
    return line(50 + Math.cos(a) * 34, 52 + Math.sin(a) * 34, 50 + Math.cos(a) * 46, 52 + Math.sin(a) * 46, { stroke: GOLD, 'stroke-width': 3, 'stroke-linecap': 'round' });
  })),
  /* Составные */
  休: () => g({}, tree(66, 88, 1.35), g({ transform: 'translate(40 88) rotate(12)' }, circle(0, -38, 8, { fill: SOFT }), path('M-9 -28 Q0 -31 9 -28 L13 0 L-13 0 Z', { fill: SOFT }))),
  林: () => g({}, tree(32, 88, 1.2), tree(68, 88, 1.2)),
  旦: () => g({}, sun(50, 40, 16, true), line(8, 74, 92, 74, { stroke: INK, 'stroke-width': 5, 'stroke-linecap': 'round' }), path('M8 74 Q30 64 50 74 T92 74', { fill: 'none', stroke: SOFT, 'stroke-width': 2 })),
};

/** Composition tablet pictures (can differ from the page picture). */
const TABLETS: Record<Glyph, () => string> = {
  明: () => g({}, sun(34, 50, 15), moon(70, 50, 18)),
  休: PICS['休'],
  林: PICS['林'],
  旦: PICS['旦'],
};

export function illustration(g0: Glyph): string {
  return (PICS[g0] ?? (() => ''))();
}

export function tabletPicture(g0: Glyph): string {
  return (TABLETS[g0] ?? PICS[g0] ?? (() => ''))();
}

export function hasIllustration(g0: Glyph): boolean {
  return g0 in PICS;
}

/* ------------------------------------------------------------------ */
/* Bells: white pictures on bronze                                     */
/* ------------------------------------------------------------------ */

const W_ = '#fbf3dc';
const WS = (w = 6) => ({ stroke: W_, 'stroke-width': w, fill: 'none', 'stroke-linecap': 'round' as const, 'stroke-linejoin': 'round' as const });

export const BELL_ICONS: Record<string, string> = {
  mountain: g({}, path('M8 86 L34 36 L52 62 L68 26 L94 86 Z', { fill: W_ })),
  sun: g({}, circle(50, 52, 18, { fill: W_ }), ...Array.from({ length: 8 }, (_, i) => {
    const a = (i / 8) * Math.PI * 2;
    return line(50 + Math.cos(a) * 26, 52 + Math.sin(a) * 26, 50 + Math.cos(a) * 38, 52 + Math.sin(a) * 38, WS(6));
  })),
  rain: g({}, ellipse(50, 34, 34, 14, { fill: W_ }), circle(38, 26, 14, { fill: W_ }), circle(60, 22, 16, { fill: W_ }), ...[[26, 60], [44, 66], [62, 60], [78, 66], [36, 84], [56, 86]].map(([x, y]) => line(x, y, x - 5, y + 12, WS(6)))),
  water: g({}, path('M8 38 q10 -12 21 0 t21 0 t21 0 t21 0', WS(7)), path('M8 60 q10 -12 21 0 t21 0 t21 0 t21 0', WS(7)), path('M8 82 q10 -12 21 0 t21 0 t21 0 t21 0', WS(7))),
  moon: path('M60 12 A38 38 0 1 0 60 88 A48 48 0 0 1 60 12 Z', { fill: W_ }),
  cloud: g({}, ellipse(50, 62, 40, 14, { fill: W_ }), circle(34, 52, 16, { fill: W_ }), circle(56, 42, 22, { fill: W_ }), circle(76, 56, 13, { fill: W_ })),
};

/** Same pictures in colour, for the close-up bell panel. */
export const BELL_PICTURES: Record<string, () => string> = {
  mountain: PICS['山'],
  sun: PICS['日'],
  rain: PICS['雨'],
  water: PICS['水'],
  moon: PICS['月'],
  cloud: PICS['云'],
};

/* ------------------------------------------------------------------ */
/* Inventory icons                                                     */
/* ------------------------------------------------------------------ */

export const ITEM_ICONS: Record<string, string> = {
  bucket: g({}, path('M22 30 L30 88 L70 88 L78 30 Z', { fill: '#9a6c42', stroke: '#5a3e24', 'stroke-width': 3 }), path('M24 46 H76 M27 70 H73', { stroke: '#5a3e24', 'stroke-width': 4 }), path('M22 30 Q50 -6 78 30', { stroke: '#5a3e24', 'stroke-width': 3, fill: 'none' })),
  water: g({}, path('M22 30 L30 88 L70 88 L78 30 Z', { fill: '#9a6c42', stroke: '#5a3e24', 'stroke-width': 3 }), ellipse(50, 32, 27, 6, { fill: '#6fb0d0' }), path('M24 46 H76 M27 70 H73', { stroke: '#5a3e24', 'stroke-width': 4 }), path('M22 30 Q50 -6 78 30', { stroke: '#5a3e24', 'stroke-width': 3, fill: 'none' }), path('M50 4 Q58 16 50 20 Q42 16 50 4 Z', { fill: '#6fb0d0' })),
  wood: g({}, ...[[30, 70], [58, 70], [44, 46], [72, 46]].map(([x, y]) => g({}, rect(x - 20, y - 11, 40, 22, { fill: '#8a5c32', rx: 10 }), ellipse(x + 18, y, 7, 11, { fill: '#d9b27a', stroke: '#8a5c32', 'stroke-width': 2 })))),
  torch: g({}, line(30, 90, 62, 34, { stroke: '#7a5634', 'stroke-width': 8, 'stroke-linecap': 'round' }), path('M62 34 Q52 20 64 4 Q66 18 74 20 Q84 34 70 42 Q60 42 62 34 Z', { fill: ORANGE }), path('M66 34 Q62 24 68 16 Q72 26 74 30 Q72 38 66 34 Z', { fill: '#ffd36b' })),
  lantern: g({}, circle(50, 56, 34, { fill: '#ffb060', opacity: 0.3 }), line(50, 6, 50, 22, { stroke: '#222', 'stroke-width': 3 }), rect(36, 22, 28, 7, { fill: '#222' }), ellipse(50, 56, 26, 28, { fill: '#f06a3a' }), path('M38 32 Q30 56 38 80 M62 32 Q70 56 62 80 M50 29 V83', { stroke: '#a83a22', 'stroke-width': 2, fill: 'none' }), rect(38, 82, 24, 7, { fill: '#222' }), line(50, 89, 50, 98, { stroke: GOLD, 'stroke-width': 3 })),
  tray: g({}, ellipse(50, 70, 44, 14, { fill: '#8a5c32' }), ellipse(50, 66, 40, 11, { fill: '#a8733f' }), cupShape(34, 66, 1, false), cupShape(56, 66, 1.2, false), cupShape(72, 64, 0.8, false)),
};

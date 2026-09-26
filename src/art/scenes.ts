import { isOn } from '../core/state';
import { BELLS } from '../core/puzzles';
import type { GameState, SceneLook } from '../core/types';
import { ancientStrokes } from './ancient';
import { darken, lighten, mix } from './color';
import { BELL_ICONS } from './illustrations';
import {
  Defs,
  bellRack,
  bigJar,
  boat,
  bucketProp,
  campfire,
  cliffMass,
  cloudBank,
  compassTable,
  cup,
  fence,
  gateTower,
  grassTufts,
  ground,
  hangingLantern,
  hopscotch,
  house,
  lanternString,
  lowTable,
  mapStone,
  mistBand,
  paifang,
  pier as pierPlanks,
  pine,
  puff,
  railing,
  range,
  reeds,
  rock,
  roof,
  roundTree,
  signPole,
  sky,
  stairsInto,
  stairsPath,
  stall,
  stele,
  tablet,
  teaJar,
  wallSegment,
  waterBody,
  willow,
  woodpile,
} from './kit';
import { PALETTES, type Palette } from './palette';
import { H, W, circle, ellipse, g, line, path, rect, svgDoc } from './svg';

type Art = (s: GameState, look: SceneLook) => string;

function compose(prefix: string, look: SceneLook, draw: (d: Defs, p: Palette) => string): string {
  const d = new Defs(prefix);
  const p = PALETTES[look.time];
  const body = draw(d, p);
  return svgDoc(body, d.toString());
}

/** Mount Tai: a broad massif with one dominant peak. */
function taishan(d: Defs, p: Palette, cx: number, base: number, height: number, name = 'tai'): string {
  return range(d, {
    name,
    seed: 11,
    base,
    amp: 40,
    color: p.far,
    fade: mix(p.far, p.sky[2], 0.55),
    peaks: [
      [cx, height, 150],
      [cx - 230, height * 0.55, 170],
      [cx + 260, height * 0.6, 180],
      [cx - 520, height * 0.3, 200],
    ],
  });
}

/* ------------------------------------------------------------------ */
/* Chapter 1                                                           */
/* ------------------------------------------------------------------ */

const pier: Art = (_s, look) =>
  compose('pier', look, (d, p) =>
    [
      sky(d, p, { sun: [1330, 170, 40], glow: [1330, 170, 620] }),
      taishan(d, p, 1000, 560, 330),
      mistBand(d, 'a', 440, 170, p.mist),
      range(d, { name: 'mid', seed: 4, base: 640, amp: 50, color: p.mid, fade: mix(p.mid, p.sky[2], 0.3), peaks: [[260, 70, 220], [1420, 90, 240]] }),
      mistBand(d, 'b', 590, 90, p.mist),
      range(d, { name: 'hill', seed: 9, base: 720, amp: 26, color: p.hill, fade: darken(p.hill, 0.1), x0: 480 }),
      puff(420, 150, 1.2, lighten(p.sky[1], 0.4), 0.8),
      puff(760, 230, 0.8, lighten(p.sky[1], 0.4), 0.7),
      waterBody(d, p, [[-20, 690], [240, 686], [470, 700], [610, 760], [640, 900], [-20, 900]], 5),
      path('M520 900 L560 772 Q700 748 900 764 L1620 752 L1620 900 Z', { fill: d.linear('bank', [[0, p.ground], [1, p.groundDark]]) }),
      path('M600 820 Q900 800 1620 808 L1620 836 Q900 830 610 848 Z', { fill: lighten(p.ground, 0.15), opacity: 0.7 }),
      reeds(p, 470, 600, 792, 3),
      willow(p, 780, 780, 1.05, 2),
      rock(p, 1460, 812, 90, 50, 4),
      rock(p, 1080, 790, 50, 30, 8),
      house(p, 1440, 760, 150, 96, { window: false, roofH: 50 }),
      grassTufts(p, 900, 1560, 780, 12, 22),
      boat(p, 270, 832, 270),
      pierPlanks(p, 330, 650, 816),
    ].join(''),
  );

const village: Art = (s, look) =>
  compose('village', look, (d, p) =>
    [
      sky(d, p, { sun: [1420, 150, 38], glow: [1420, 150, 600] }),
      taishan(d, p, 1100, 520, 300),
      mistBand(d, 'a', 400, 170, p.mist),
      range(d, { name: 'mid', seed: 6, base: 640, amp: 60, color: p.mid, fade: mix(p.mid, p.sky[2], 0.3) }),
      mistBand(d, 'b', 580, 100, p.mist),
      ground(d, p, 790, { seed: 5 }),
      path('M-40 818 Q800 800 1640 816 L1640 846 Q800 836 -40 850 Z', { fill: lighten(p.ground, 0.14), opacity: 0.7 }),
      roundTree(p, 470, 790, 1.2, 3),
      house(p, 110, 800, 290, 190),
      isOn(s, 'bucket_taken') ? '' : bucketProp(p, 292, 812),
      bigJar(p, 670, 818, 1.15),
      roundTree(p, 830, 790, 0.95, 8, darken(p.foliage, 0.05)),
      campfire(p, 1025, 822, isOn(s, 'fire_lit')),
      woodpile(p, 1205, 806),
      house(p, 1300, 806, 270, 200),
      hangingLantern(p, 1432, 596, 1.1, isOn(s, 'lantern_given')),
      fence(p, 1580, 1640, 812),
      fence(p, -30, 90, 812),
      grassTufts(p, 0, 1600, 830, 21, 24),
    ].join(''),
  );

const arch: Art = (_s, look) =>
  compose('arch', look, (d, p) =>
    [
      sky(d, p, { sun: [240, 250, 42], glow: [240, 250, 560] }),
      taishan(d, p, 1250, 560, 420),
      mistBand(d, 'a', 420, 170, p.mist),
      range(d, { name: 'mid', seed: 14, base: 660, amp: 60, color: p.mid, fade: mix(p.mid, p.sky[2], 0.25), peaks: [[1320, 140, 260]] }),
      mistBand(d, 'b', 600, 110, p.mist),
      range(d, { name: 'near', seed: 19, base: 760, amp: 40, color: p.near, fade: darken(p.near, 0.1), peaks: [[1500, 200, 200], [1060, 90, 160]] }),
      ground(d, p, 820, { seed: 8 }),
      stairsInto(p, 1260, 870, 250, 1330, 470, 56, 26),
      pine(p, 1500, 780, 0.9, 5, -0.2),
      pine(p, 930, 800, 0.8, 7, 0.2),
      paifang(p, 1040, 846, 440, 480),
      pine(p, 170, 830, 1.25, 3, 0.15),
      rock(p, 330, 836, 110, 60, 6),
      signPole(p, 640, 846, 330),
      grassTufts(p, 0, 1000, 836, 31, 18),
    ].join(''),
  );

/* ------------------------------------------------------------------ */
/* Chapter 2                                                           */
/* ------------------------------------------------------------------ */

const market: Art = (_s, look) =>
  compose('market', look, (d, p) =>
    [
      sky(d, p, { sun: [210, 380, 60], glow: [210, 380, 700] }),
      taishan(d, p, 1040, 520, 320),
      mistBand(d, 'a', 420, 150, p.mist),
      range(d, { name: 'mid', seed: 21, base: 610, amp: 50, color: p.mid, fade: mix(p.mid, p.sky[2], 0.3) }),
      wallSegment(p, 520, 1120, 700, 150),
      path('M760 700 V600 A60 60 0 0 1 880 600 V700 Z', { fill: darken(p.red, 0.45) }),
      ground(d, p, 830, { seed: 12 }),
      lanternString(p, -20, 800, 250, 30, 5, true),
      lanternString(p, 800, 1620, 250, 30, 5, true),
      stall(p, 60, 846, 230, '#b8563a'),
      g({}, ...[80, 130, 180, 230].map((x, i) => circle(x + 20, 770, 14, { fill: ['#e89a3a', '#c9483a', '#e8c23a', '#8aa84a'][i] }))),
      hopscotch(380, 848, 10, 62),
      house(p, 1180, 846, 440, 290, { window: true }),
      g({}, path('M1370 846 L1400 780 L1440 846 Z', { fill: '#b89458' }), path('M1400 846 L1430 790 L1466 846 Z', { fill: '#a8844a' })),
      grassTufts(p, 0, 1600, 860, 41, 10),
    ].join(''),
  );

const teahouse: Art = (_s, look) =>
  compose('tea', look, (d, p) => {
    const beam = darken(p.woodDark, 0.15);
    return [
      sky(d, p, { sun: [1450, 520, 50], glow: [1450, 520, 520] }),
      taishan(d, p, 1250, 600, 260),
      mistBand(d, 'a', 520, 140, p.mist),
      rect(0, 160, 700, 660, { fill: p.wall }),
      rect(0, 160, 700, 660, { fill: d.linear('wallshade', [[0, 'rgba(0,0,0,0.15)'], [1, 'rgba(0,0,0,0)']]) }),
      g({}, ...[380, 560].map((x) => g({}, rect(x - 64, 260, 128, 128, { fill: p.woodDark }), rect(x - 56, 268, 112, 112, { fill: mix(p.paper, p.gold, 0.25) }), path(`M${x - 56} 305 h112 M${x - 56} 343 h112 M${x - 19} 268 v112 M${x + 19} 268 v112`, { stroke: p.woodDark, 'stroke-width': 4 })))),
      g({}, rect(80, 470, 230, 12, { fill: p.wood }), rect(80, 560, 230, 12, { fill: p.wood }), ...[110, 170, 230, 290].map((x) => cup(x, 470, true)), ...[100, 140, 180, 220, 260, 300].map((x) => cup(x, 560, false))),
      rect(0, 820, W, 80, { fill: d.linear('floor', [[0, p.wood], [1, p.woodDark]]) }),
      path(Array.from({ length: 16 }, (_, i) => `M${i * 110} 820 L${i * 110 - 60} 900`).join(' '), { stroke: p.woodDark, 'stroke-width': 2, opacity: 0.5 }),
      rect(76, 704, 238, 140, { fill: p.wood }),
      rect(70, 696, 250, 14, { fill: lighten(p.wood, 0.1) }),
      rect(90, 724, 210, 110, { fill: darken(p.wood, 0.15) }),
      teaJar(p, 150, 700, 1),
      teaJar(p, 240, 700, 1),
      g({}, line(520, 160, 540, 420, { stroke: p.ink, 'stroke-width': 1.5 }), line(680, 160, 660, 420, { stroke: p.ink, 'stroke-width': 1.5 })),
      lowTable(p, 855, 856, 110),
      g({}, cup(835, 806, false, '#efe7d4'), cup(870, 808, false, '#efe7d4')),
      lowTable(p, 1135, 856, 100),
      lowTable(p, 1335, 856, 100),
      g({}, cup(1320, 806, false, '#efe7d4'), cup(1352, 808, false, '#efe7d4')),
      rect(0, 0, W, 150, { fill: beam }),
      rect(0, 140, W, 24, { fill: p.woodDark }),
      path(Array.from({ length: 30 }, (_, i) => `M${i * 56} 150 v-150`).join(' '), { stroke: darken(beam, 0.2), 'stroke-width': 3 }),
      g({}, ...[18, 560, 975, 1582].map((x) => rect(x - 14, 160, 28, 690, { fill: p.red }))),
      g({}, ...[300, 830, 1350].map((x) => hangingLantern(p, x, 165, 1, true))),
    ].join('');
  });

const gate1: Art = (_s, look) =>
  compose('gate1', look, (d, p) =>
    [
      sky(d, p, { sun: [180, 400, 58], glow: [180, 400, 700] }),
      taishan(d, p, 1150, 540, 360),
      mistBand(d, 'a', 430, 150, p.mist),
      range(d, { name: 'mid', seed: 25, base: 660, amp: 60, color: p.mid, fade: mix(p.mid, p.sky[2], 0.25), peaks: [[1250, 120, 200]] }),
      mistBand(d, 'b', 600, 100, p.mist),
      range(d, { name: 'near', seed: 27, base: 770, amp: 30, color: p.near, fade: darken(p.near, 0.1), peaks: [[1500, 160, 180]] }),
      ground(d, p, 832, { seed: 14 }),
      stairsInto(p, 1240, 876, 200, 1290, 520, 50, 22),
      pine(p, 1520, 800, 1.0, 9, -0.1),
      paifang(p, 1080, 846, 320, 600),
      stele(p, 555, 800, 90, 250, { color: p.stoneLight }),
      lowTable(p, 950, 856, 110),
      g({}, rect(915, 792, 44, 22, { fill: p.woodDark }), ...[0, 1, 2].map((i) => circle(975 + i * 10, 804 - i * 3, 7, { fill: '#c8923a', stroke: '#7a5420', 'stroke-width': 1.5 }))),
      pine(p, 250, 846, 1.3, 13, 0.1),
      rock(p, 420, 850, 120, 64, 18),
      grassTufts(p, 0, 1000, 850, 51, 18),
    ].join(''),
  );

/* ------------------------------------------------------------------ */
/* Chapter 3                                                           */
/* ------------------------------------------------------------------ */

const midgate: Art = (s, look) =>
  compose('mid', look, (d, p) => {
    const night = look.time === 'night';
    const sunset = look.time === 'sunset';
    return [
      sky(d, p, {
        sun: sunset ? [240, 430, 50] : undefined,
        glow: sunset ? [240, 430, 700] : night ? [1420, 180, 400] : undefined,
        moon: night ? [1420, 180, 34] : undefined,
        stars: night,
        seed: 31,
      }),
      range(d, { name: 'far', seed: 33, base: 520, amp: 60, color: p.far, fade: mix(p.far, p.sky[2], 0.5), peaks: [[1280, 300, 160], [900, 120, 200]] }),
      mistBand(d, 'a', 440, 160, p.mist),
      range(d, { name: 'mid', seed: 35, base: 660, amp: 50, color: p.mid, fade: mix(p.mid, p.sky[2], 0.25), peaks: [[300, 90, 200]] }),
      g({ opacity: 0.9 }, house(p, 60, 700, 380, 150, { window: false, roofH: 90, wall: mix(p.wall, p.mid, 0.3) })),
      mistBand(d, 'b', 600, 100, p.mist),
      ground(d, p, 830, { seed: 17 }),
      stairsInto(p, 1240, 876, 200, 1290, 520, 50, 22),
      pine(p, 1520, 800, 1.1, 21, -0.2),
      paifang(p, 1080, 846, 320, 600),
      mapStone(p, 300, 760, 200, 330),
      bellRack(p, 640, 430, 300, BELLS.map((b) => BELL_ICONS[b])),
      signPole(p, 1010, 846, 300),
      rock(p, 960, 850, 90, 40, 5),
      grassTufts(p, 0, 1000, 850, 61, 16),
      isOn(s, 'bells_solved') ? '' : '',
    ].join('');
  });

const STAIRS_PATH: [number, number][] = [
  [90, 858],
  [820, 780],
  [360, 660],
  [930, 560],
  [560, 450],
  [1040, 360],
  [1260, 300],
];

const stairs: Art = (_s, look) =>
  compose('stairs', look, (d, p) =>
    [
      sky(d, p, { moon: [200, 130, 30], stars: true, seed: 41 }),
      range(d, { name: 'far', seed: 43, base: 760, amp: 60, color: p.far, fade: mix(p.far, p.sky[2], 0.5), peaks: [[300, 120, 160], [700, 60, 120]] }),
      mistBand(d, 'a', 640, 160, p.mist),
      cliffMass(p, [[-20, 900], [-20, 420], [80, 380], [200, 520], [260, 700], [300, 900]], 45, p.stoneDark),
      cliffMass(p, [[1080, 900], [1120, 640], [1180, 420], [1300, 330], [1450, 300], [1620, 260], [1620, 900]], 47, p.stoneDark),
      g({}, rect(1250, 240, 160, 70, { fill: p.stone }), path('M1300 310 V272 A30 30 0 0 1 1360 272 V310 Z', { fill: '#2a2230' }), rect(1245, 205, 170, 38, { fill: p.redDark }), roof(1232, 160, 196, 44, p.roof, { oh: 22 })),
      stairsPath(p, STAIRS_PATH),
      pine(p, 1540, 330, 0.75, 49, -0.4),
      pine(p, 120, 430, 0.9, 51, 0.5),
      rock(p, 700, 520, 80, 40, 52),
    ].join(''),
  );

const stairsFront: Art = (_s, look) =>
  compose('stairsf', look, (_d, p) =>
    [
      cliffMass(p, [[1300, 900], [1360, 820], [1500, 780], [1620, 760], [1620, 900]], 53, darken(p.stoneDark, 0.2)),
      path('M-20 60 Q120 90 240 40 Q300 20 360 30', { stroke: p.trunk, 'stroke-width': 12, fill: 'none', 'stroke-linecap': 'round' }),
      ellipse(250, 40, 90, 22, { fill: p.foliageDark }),
      ellipse(360, 30, 60, 16, { fill: p.foliage }),
      ellipse(110, 70, 80, 20, { fill: p.foliage }),
    ].join(''),
  );

/* ------------------------------------------------------------------ */
/* Chapter 4                                                           */
/* ------------------------------------------------------------------ */

function cloudSea(p: Palette, y: number, seed: number, tint?: string): string {
  const c = tint ?? mix(p.sky[2], '#ffffff', 0.35);
  return g(
    { class: 'cloud-sea' },
    cloudBank(-40, y, 1700, H - y + 20, mix(c, p.sky[1], 0.35), seed, 60),
    cloudBank(-40, y + 50, 1700, H - y, mix(c, p.sky[1], 0.15), seed + 1, 50),
    cloudBank(-40, y + 110, 1700, H - y, c, seed + 2, 44),
  );
}

const southgate: Art = (s, look) =>
  compose('south', look, (d, p) =>
    [
      sky(d, p, { moon: [1420, 150, 32], stars: true, seed: 61 }),
      range(d, { name: 'far', seed: 63, base: 700, amp: 50, color: p.far, fade: mix(p.far, p.sky[2], 0.5), peaks: [[200, 120, 160], [1500, 100, 140]] }),
      cloudSea(p, 640, 65),
      ground(d, p, 830, { seed: 23 }),
      stairsInto(p, 160, 910, 300, 250, 836, 220, 6),
      gateTower(p, 1000, 846, { open: isOn(s, 'gate_open') }),
      hangingLantern(p, 790, 450, 1.1, true),
      hangingLantern(p, 1210, 450, 1.1, true),
      railing(p, 0, 640, 850, 46),
      pine(p, 1500, 846, 1.1, 67, -0.2),
    ].join(''),
  );

const skystreet: Art = (_s, look) =>
  compose('street', look, (d, p) =>
    [
      sky(d, p, { moon: [190, 330, 46], glow: [190, 330, 300], stars: true, seed: 71 }),
      cloudSea(p, 600, 73),
      range(d, { name: 'hill', seed: 75, base: 700, amp: 30, color: p.mid, fade: p.near, peaks: [[1010, 330, 160]] }),
      g({}, rect(965, 330, 90, 40, { fill: p.redDark }), roof(950, 300, 120, 36, p.roof, { oh: 14 })),
      stairsInto(p, 1000, 800, 110, 1010, 380, 30, 18),
      ground(d, p, 832, { seed: 29 }),
      house(p, 60, 836, 300, 230),
      hangingLantern(p, 210, 590, 1, true),
      house(p, 1200, 836, 330, 240),
      hangingLantern(p, 1365, 580, 1, true),
      lanternString(p, 360, 880, 470, 16, 4, true),
      compassTable(p, 455, 739),
      signPole(p, 990, 846, 390),
      path('M700 900 L716 876 H884 L900 900 Z', { fill: p.stoneLight }),
      path('M680 900 L700 884 H900 L920 900', { fill: 'none', stroke: p.stoneDark, 'stroke-width': 3 }),
    ].join(''),
  );

const moonpeak: Art = (_s, look) =>
  compose('moon', look, (d, p) =>
    [
      sky(d, p, { moon: [300, 400, 70], glow: [300, 400, 420], stars: true, seed: 81 }),
      cloudSea(p, 520, 83, '#cdd6ec'),
      path('M300 470 Q320 600 280 900', { stroke: '#fffbe0', 'stroke-width': 60, opacity: 0.12, fill: 'none' }),
      path(`M380 900 L400 812 Q430 770 520 776 Q900 790 1620 800 L1620 900 Z`, { fill: d.linear('peak', [[0, p.stone], [1, p.stoneDark]]) }),
      cliffMass(p, [[380, 900], [400, 812], [440, 830], [420, 900]], 85, darken(p.stoneDark, 0.1)),
      rock(p, 600, 800, 120, 40, 86),
      pine(p, 470, 800, 1.0, 87, -1.1),
      pine(p, 1480, 810, 1.2, 88, 0.1),
      rock(p, 1200, 812, 100, 60, 89),
    ].join(''),
  );

const summit: Art = (_s, look) =>
  compose('summit', look, (d, p) =>
    [
      sky(d, p, { glow: [1600, 720, 760], stars: true, seed: 91 }),
      cloudSea(p, 660, 93),
      wallSegment(p, -20, 1620, 720, 200),
      g({}, rect(1000, 470, 400, 60, { fill: p.redDark }), roof(960, 400, 480, 80, p.roof, { oh: 40 })),
      ground(d, p, 830, { seed: 31, color: p.stone, dark: p.stoneDark }),
      stele(p, 600, 820, 170, 490, { color: mix(p.stoneLight, '#ffffff', 0.08) }),
      g({}, path('M250 830 L262 660 L300 640 L330 668 L372 630 L410 650 L420 830 Z', { fill: p.stone }), path('M262 660 L300 640 L330 668 L372 630 L410 650', { stroke: p.stoneLight, 'stroke-width': 4, fill: 'none' })),
      g({ opacity: 0.5, color: darken(p.stone, 0.45) }, ...['日', '月', '山', '水', '人', '木'].map((c, i) => `<g transform="translate(${272 + (i % 3) * 44} ${690 + Math.floor(i / 3) * 56}) scale(0.36)">${ancientStrokes(c) ?? ''}</g>`)),
      lowTable(p, 1330, 856, 150),
      g({}, tablet(p, 1270, 800, 44, 56), tablet(p, 1325, 800, 44, 56), tablet(p, 1380, 800, 44, 56)),
      pine(p, 1540, 830, 1.1, 95, -0.3),
    ].join(''),
  );

const sunpeak: Art = (s, look) =>
  compose('sun', look, (d, p) => {
    const dawn = look.time === 'dawn';
    return [
      sky(d, p, dawn ? { sun: [1330, 470, 58], glow: [1330, 470, 900] } : { glow: [1600, 620, 800], stars: true, seed: 101 }),
      dawn ? '' : rect(0, 480, W, 120, { fill: d.linear('horizon', [[0, 'rgba(255,170,140,0)'], [1, 'rgba(255,170,140,0.35)']]) }),
      cloudSea(p, 540, 103, dawn ? '#fff0e0' : undefined),
      path('M-20 900 L-20 820 Q300 800 700 810 Q1000 800 1180 820 L1230 900 Z', { fill: d.linear('rock', [[0, p.stone], [1, p.stoneDark]]) }),
      cliffMass(p, [[1150, 900], [1180, 820], [1250, 840], [1270, 900]], 105, darken(p.stoneDark, 0.1)),
      g({}, path('M1220 900 L1250 800 L1330 790 L1400 810 L1420 900 Z', { fill: p.stoneDark }), path('M1250 800 L1330 790 L1400 810', { stroke: p.stone, 'stroke-width': 5, fill: 'none' })),
      railing(p, 60, 780, 830, 44),
      g({}, rect(870, 740, 170, 80, { fill: p.stoneLight }), rect(860, 730, 190, 16, { fill: lighten(p.stoneLight, 0.1) }), line(890, 800, 1020, 800, { stroke: darken(p.stoneLight, 0.45), 'stroke-width': 6, 'stroke-linecap': 'round' }), isOn(s, 'sunrise') ? circle(955, 772, 14, { fill: '#f2b33d' }) : ''),
      pine(p, 150, 820, 1.0, 107, 0.4),
    ].join('');
  });

export const ART = {
  pier,
  village,
  arch,
  market,
  teahouse,
  gate1,
  midgate,
  stairs,
  stairsFront,
  southgate,
  skystreet,
  moonpeak,
  summit,
  sunpeak,
};

export { STAIRS_PATH };

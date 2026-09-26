import type { TimeOfDay } from '../core/types';

export interface Palette {
  sky: [string, string, string];
  sun: string;
  glow: string;
  far: string;
  mid: string;
  near: string;
  hill: string;
  mist: string;
  ground: string;
  groundDark: string;
  grass: string;
  water: string;
  waterLight: string;
  foliage: string;
  foliageDark: string;
  trunk: string;
  stone: string;
  stoneDark: string;
  stoneLight: string;
  wood: string;
  woodDark: string;
  roof: string;
  roofDark: string;
  wall: string;
  wallShade: string;
  red: string;
  redDark: string;
  gold: string;
  paper: string;
  ink: string;
  shade: string;
}

const GOLDEN: Palette = {
  sky: ['#8fbcd4', '#d9e4d8', '#f6e1ae'],
  sun: '#fff4cf',
  glow: 'rgba(255,236,180,0.55)',
  far: '#a8b8c0',
  mid: '#86a0a0',
  near: '#6a8a74',
  hill: '#7f9a62',
  mist: 'rgba(250,244,228,0.55)',
  ground: '#c9ab78',
  groundDark: '#a88a5c',
  grass: '#8f9f58',
  water: '#6d9fb0',
  waterLight: '#b9dbe0',
  foliage: '#5f8452',
  foliageDark: '#3f6040',
  trunk: '#5b4632',
  stone: '#b3ab9c',
  stoneDark: '#8a8274',
  stoneLight: '#d6cfbf',
  wood: '#9a6c42',
  woodDark: '#6b4a2c',
  roof: '#56606a',
  roofDark: '#3a424b',
  wall: '#efe4cc',
  wallShade: '#d4c5a4',
  red: '#b2402f',
  redDark: '#7f2a20',
  gold: '#d9b25c',
  paper: '#f4ead2',
  ink: '#2b2622',
  shade: 'rgba(40,30,20,0.22)',
};

const SUNSET: Palette = {
  sky: ['#5e6aa3', '#d98b7c', '#f7c886'],
  sun: '#ffd79a',
  glow: 'rgba(255,190,120,0.55)',
  far: '#9a86a0',
  mid: '#7a6888',
  near: '#584d6c',
  hill: '#6d6a58',
  mist: 'rgba(255,214,190,0.45)',
  ground: '#b58a66',
  groundDark: '#8e6a4e',
  grass: '#7e7f4c',
  water: '#8c7fa0',
  waterLight: '#f0c1a0',
  foliage: '#4f6a4a',
  foliageDark: '#34483a',
  trunk: '#4a3528',
  stone: '#a58f86',
  stoneDark: '#7b6864',
  stoneLight: '#cdb5a6',
  wood: '#8e5c3c',
  woodDark: '#5e3d28',
  roof: '#4c4a5c',
  roofDark: '#353345',
  wall: '#f0d6bc',
  wallShade: '#cfae92',
  red: '#b43c32',
  redDark: '#7a2724',
  gold: '#e4b35e',
  paper: '#f6e2c6',
  ink: '#2b2224',
  shade: 'rgba(50,25,30,0.25)',
};

const DUSK: Palette = {
  sky: ['#3c465e', '#5d6780', '#8b90a2'],
  sun: '#e8c9a0',
  glow: 'rgba(200,190,210,0.3)',
  far: '#6e768a',
  mid: '#565f74',
  near: '#40495c',
  hill: '#4a5448',
  mist: 'rgba(205,212,228,0.45)',
  ground: '#6f665e',
  groundDark: '#565049',
  grass: '#4e5a44',
  water: '#5a6a80',
  waterLight: '#9aa8ba',
  foliage: '#3d5040',
  foliageDark: '#2a3a30',
  trunk: '#3a2f28',
  stone: '#8a8a8e',
  stoneDark: '#65666c',
  stoneLight: '#aaaaae',
  wood: '#6f4e38',
  woodDark: '#4a3526',
  roof: '#3b4250',
  roofDark: '#2a303b',
  wall: '#c9c3b8',
  wallShade: '#a7a196',
  red: '#8e3a34',
  redDark: '#622824',
  gold: '#bfa060',
  paper: '#d9cfbb',
  ink: '#1f1d22',
  shade: 'rgba(15,18,30,0.3)',
};

const NIGHT: Palette = {
  sky: ['#0b1430', '#18284d', '#2c3f68'],
  sun: '#f6f0d4',
  glow: 'rgba(220,230,255,0.25)',
  far: '#2a3a5e',
  mid: '#1f2d4c',
  near: '#16223b',
  hill: '#1c2a3a',
  mist: 'rgba(150,170,210,0.22)',
  ground: '#3a3d4e',
  groundDark: '#2a2c3a',
  grass: '#26323a',
  water: '#23355a',
  waterLight: '#7f95c0',
  foliage: '#1e3034',
  foliageDark: '#142226',
  trunk: '#221c1e',
  stone: '#5c6275',
  stoneDark: '#41475a',
  stoneLight: '#7c8398',
  wood: '#4a3a36',
  woodDark: '#322628',
  roof: '#262d40',
  roofDark: '#1a1f2e',
  wall: '#6f7286',
  wallShade: '#565a6e',
  red: '#7d3434',
  redDark: '#552426',
  gold: '#b7995a',
  paper: '#a9a6a8',
  ink: '#101018',
  shade: 'rgba(0,0,10,0.35)',
};

const PREDAWN: Palette = {
  ...NIGHT,
  sky: ['#101a3c', '#33386a', '#8a6b8c'],
  glow: 'rgba(255,190,170,0.28)',
  far: '#3b3f6a',
  mid: '#2c2f55',
  near: '#1f2342',
  mist: 'rgba(200,180,210,0.28)',
  ground: '#43405a',
  groundDark: '#312f45',
  stone: '#6a6780',
  stoneDark: '#4c4a60',
  stoneLight: '#8a87a0',
};

const DAWN: Palette = {
  ...GOLDEN,
  sky: ['#78a6d6', '#f2b98a', '#ffe3a8'],
  sun: '#fff2c4',
  glow: 'rgba(255,214,150,0.6)',
  far: '#b89aa6',
  mid: '#8e7c96',
  near: '#665d78',
  mist: 'rgba(255,236,226,0.7)',
  ground: '#a88a78',
  groundDark: '#83685a',
  stone: '#a8948e',
  stoneDark: '#7c6a66',
  stoneLight: '#d2bcb0',
};

export const PALETTES: Record<TimeOfDay, Palette> = {
  day: GOLDEN,
  golden: GOLDEN,
  sunset: SUNSET,
  dusk: DUSK,
  night: NIGHT,
  predawn: PREDAWN,
  dawn: DAWN,
};

export function isDark(t: TimeOfDay): boolean {
  return t === 'night' || t === 'predawn' || t === 'dusk';
}

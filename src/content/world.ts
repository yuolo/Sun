import type { ChapterDef, SceneDef } from '../core/types';
import { CHAPTER1 } from './chapters/ch1';
import { CHAPTER2 } from './chapters/ch2';
import { CHAPTER3 } from './chapters/ch3';
import { CHAPTER4 } from './chapters/ch4';

export const SCENES: SceneDef[] = [...CHAPTER1, ...CHAPTER2, ...CHAPTER3, ...CHAPTER4];

const BY_ID = new Map(SCENES.map((s) => [s.id, s]));

export function sceneById(id: string): SceneDef {
  const s = BY_ID.get(id);
  if (!s) throw new Error(`unknown scene ${id}`);
  return s;
}

export function hasScene(id: string): boolean {
  return BY_ID.has(id);
}

export const CHAPTERS: ChapterDef[] = [
  { n: 1, zh: '山下', title: 'У подножия', subtitle: 'Деревня у подножия горы Тайшань', start: { scene: '1a', entry: 'boat' } },
  { n: 2, zh: '一天门', title: 'Первые небесные ворота', subtitle: 'Рынок и чайная у начала тропы', start: { scene: '2a', entry: 'bottom' } },
  { n: 3, zh: '中天门', title: 'Средние небесные ворота', subtitle: 'Середина пути. Вечереет', start: { scene: '3a', entry: 'bottom' } },
  { n: 4, zh: '山上', title: 'На вершине', subtitle: 'Ночь перед рассветом', start: { scene: '4a', entry: 'bottom' } },
];

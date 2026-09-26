import type { Glyph } from '../core/types';

export type Layout = 'lr' | 'tb';

export interface Recipe {
  a: Glyph;
  b: Glyph;
  layout: Layout;
  result: Glyph;
  /** Russian caption of the tablet picture. */
  caption: string;
}

/** Characters the player can build from parts. */
export const RECIPES: Recipe[] = [
  { a: '日', b: '月', layout: 'lr', result: '明', caption: 'Солнце и луна сияют вместе' },
  { a: '人', b: '木', layout: 'lr', result: '休', caption: 'Человек прислонился к дереву' },
  { a: '木', b: '木', layout: 'lr', result: '林', caption: 'Деревья растут рядом' },
  { a: '日', b: '一', layout: 'tb', result: '旦', caption: 'Солнце над линией горизонта' },
];

export function recipeFor(result: Glyph): Recipe | undefined {
  return RECIPES.find((r) => r.result === result);
}

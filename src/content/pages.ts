import type { PageDef } from '../core/types';

/** Journal confirmation pages. Illustrations are keyed by glyph (see art/illustrations.ts). */
export const PAGES: PageDef[] = [
  { id: 'elements', title: 'Стихии', chapter: 1, glyphs: ['山', '水', '火', '木'] },
  { id: 'people', title: 'Люди', chapter: 1, glyphs: ['你', '我', '好', '谢'] },
  { id: 'way', title: 'Путь', chapter: 1, glyphs: ['上', '下', '要', '不', '吗'] },
  { id: 'count1', title: 'Счёт I', chapter: 2, glyphs: ['一', '二', '三', '四', '五'] },
  { id: 'count2', title: 'Счёт II', chapter: 2, glyphs: ['六', '七', '八', '九', '十'] },
  { id: 'teahouse', title: 'Чайная', chapter: 2, glyphs: ['茶', '杯', '大', '小', '钱'] },
  { id: 'trade', title: 'Торг', chapter: 2, glyphs: ['有', '没', '几', '两', '人'] },
  { id: 'sky', title: 'Небо', chapter: 3, glyphs: ['日', '月', '云', '雨', '天'] },
  { id: 'gates', title: 'Путь в небо', chapter: 3, glyphs: ['中', '门', '看'] },
  { id: 'compass', title: 'Стороны света', chapter: 4, glyphs: ['东', '西', '南', '北'] },
  { id: 'dawn', title: 'Рассвет', chapter: 4, glyphs: ['开', '出', '明'] },
];

export function pageDef(id: string): PageDef | undefined {
  return PAGES.find((p) => p.id === id);
}

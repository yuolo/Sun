import type { ItemDef } from '../core/types';

export const ITEMS: ItemDef[] = [
  { id: 'bucket', name: 'Ведро', description: 'Пустое деревянное ведро.' },
  { id: 'water', name: 'Ведро с водой', description: 'Холодная речная вода.' },
  { id: 'wood', name: 'Дрова', description: 'Охапка сухих поленьев.' },
  { id: 'torch', name: 'Лучина', description: 'Горящая щепа. Долго не продержится.' },
  { id: 'lantern', name: 'Фонарь', description: 'Бумажный фонарь. Светит тепло и ровно.' },
  { id: 'tray', name: 'Поднос', description: 'Поднос хозяйки чайной.' },
];

export function itemDef(id: string): ItemDef | undefined {
  return ITEMS.find((i) => i.id === id);
}

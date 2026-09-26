"""All scenes and chapters."""
from __future__ import annotations

from ..core.types import ChapterDef, SceneDef

CHAPTERS: list[ChapterDef] = [
    ChapterDef(0, '信', 'Письмо', 'Квартира деда', ('0a', 'start')),
    ChapterDef(1, '路上', 'В пути', 'Аэропорт, вокзал, поезд', ('1a', 'gate')),
    ChapterDef(2, '泰安', 'Тайань', 'Город у подножия горы', ('2a', 'station')),
    ChapterDef(3, '山下', 'У подножия', 'Деревня у моста деда', ('3a', 'road')),
    ChapterDef(4, '红门', 'Красные ворота', 'Начало тропы', ('4a', 'bottom')),
    ChapterDef(5, '中天门', 'Средние ворота', 'Закат на середине пути', ('5a', 'bottom')),
    ChapterDef(6, '十八盘', 'Восемнадцать поворотов', 'Ночной подъём', ('6a', 'bottom')),
    ChapterDef(7, '天街', 'Небесная улица', 'Вершина ночью', ('7a', 'bottom')),
    ChapterDef(8, '日出', 'Восход', 'Рассвет равноденствия', ('8a', 'bottom')),
]

SCENES: list[SceneDef] = []
_BY_ID: dict[str, SceneDef] = {}


def register(*scenes: SceneDef) -> None:
    for s in scenes:
        if s.id in _BY_ID:
            raise ValueError(f'duplicate scene {s.id}')
        SCENES.append(s)
        _BY_ID[s.id] = s


def scene_by_id(scene_id: str) -> SceneDef:
    load()
    return _BY_ID[scene_id]


def has_scene(scene_id: str) -> bool:
    load()
    return scene_id in _BY_ID


_loaded = False


def load() -> None:
    """Imports every chapter module (they register their scenes, pages, items…)."""
    global _loaded
    if _loaded:
        return
    _loaded = True
    import importlib
    import pkgutil

    from . import chapters

    for mod in sorted(m.name for m in pkgutil.iter_modules(chapters.__path__)):
        if not mod.startswith('_'):
            importlib.import_module(f'{chapters.__name__}.{mod}')

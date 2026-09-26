"""Prologue · 信 «Письмо» — grandfather's room in Russia, September."""
from __future__ import annotations

from ...art import kit
from ...art import palette as P
from ...core.types import ExitDef, HotspotDef, ItemDef, SceneDef, SceneLook, ScriptContext, TextDef
from .. import items, texts
from ..world import register

items.add(
    ItemDef('letter', '信', 'letter', 'Плотный конверт. Адрес написан знаками, аккуратно, как в прописях.'),
    ItemDef('diary', '日记', 'diary', 'Толстая тетрадь в красной обложке. Дед писал в ней по-китайски.'),
    ItemDef('photo', '照片', 'photo', 'Двое молодых людей на каменной лестнице, в дождевиках.'),
    ItemDef('brush', '笔', 'brush', 'Старая кисть из тёмного бамбука. Ворс чуть тёплый на ощупь.'),
)

texts.add(
    TextDef(
        'envelope', 'letter', 'Конверт', '泰山　中天门\n李家茶馆\n李明　收',
        'Гора Тайшань, Средние небесные ворота. Чайная семьи Ли. Получатель — Ли Мин.',
        chapter=0,
    ),
    TextDef(
        'photo_back', 'sign', 'Фото, оборот', '一九六零年　泰山\n李明　小安',
        '1960 год, гора Тайшань. Ли Мин и Сяо Ань — так друг звал деда.',
        chapter=0,
    ),
)

NOTE = [
    'Если читаешь это — меня уже нет. В конверте письмо моему другу Ли Мину. Я так и не отправил его: шестьдесят лет не знал как.',
    'Отнеси его на гору Тайшань, в чайную у Средних небесных ворот. И кисть отнеси — она его.',
    'Переводчиком не пользуйся: он не поймёт главного. Учись, как учился я, — у людей. Дневник поможет.',
    'Будь на вершине к рассвету в день осеннего равноденствия. Встреть его за меня. — Дед',
]


def art(s, look: SceneLook) -> None:
    c = kit.C
    # wallpaper
    c.rect(0, 0, 320, 132, P.PEACH)
    for y in range(6, 128, 12):
        for x in range((y // 12 % 2) * 6, 320, 12):
            c.pset(x, y, P.OCHRE)
            c.pset(x + 1, y + 1, P.ROSE)
    c.rect(0, 124, 320, 4, P.WOOD)
    # floor
    kit.ground(128, P.OCHRE)
    for y in range(128, 180, 6):
        c.line(0, y, 320, y, P.WOOD)
    for i, y in enumerate(range(128, 180, 6)):
        for x in range((i % 3) * 22, 320, 66):
            c.line(x, y, x, y + 5, P.WOOD)
    # window with birches
    wx, wy, ww, wh = 96, 26, 74, 70
    c.rect(wx, wy, ww, wh, P.LIGHT_BLUE)
    c.rect(wx, wy + 40, ww, 30, P.MIST)
    for bx, h in ((106, 60), (128, 66), (152, 58)):
        c.rect(bx, wy + wh - h, 3, h, P.WHITE)
        for yy in range(wy + wh - h + 4, wy + wh, 7):
            c.line(bx, yy, bx + 1, yy, P.INK)
        c.circ(bx + 1, wy + wh - h + 2, 8, P.YELLOW)
        c.circ(bx + 5, wy + wh - h + 8, 6, P.ORANGE)
    c.rectb(wx, wy, ww, wh, P.WOOD)
    c.line(wx + ww // 2, wy, wx + ww // 2, wy + wh, P.WOOD)
    c.line(wx, wy + 30, wx + ww, wy + 30, P.WOOD)
    c.rect(wx - 8, wy - 4, 10, wh + 10, P.LACQUER)
    c.rect(wx + ww - 2, wy - 4, 10, wh + 10, P.LACQUER)
    c.rect(wx - 4, wy + wh, ww + 8, 4, P.PAPER)
    # bookshelf
    c.rect(10, 34, 62, 94, P.WOOD)
    for sy in (48, 72, 96, 120):
        c.rect(12, sy, 58, 3, P.OCHRE)
    cols = [P.VERMILION, P.DARK_BLUE, P.JADE, P.PLUM, P.OCHRE, P.PAPER, P.TEAL, P.LACQUER]
    for i, sy in enumerate((48, 72, 96, 120)):
        x = 13
        while x < 66:
            w = 3 + (x * 7 + i) % 3
            h = 12 + (x * 3 + i * 5) % 8
            c.rect(x, sy - h, w, h, cols[(x + i) % len(cols)])
            x += w + 1
    # framed photo on the wall
    c.rect(196, 30, 26, 20, P.OCHRE)
    c.rect(198, 32, 22, 16, P.GREY)
    c.rect(200, 38, 5, 9, P.STONE)
    c.rect(210, 37, 5, 10, P.STONE)
    c.circ(202, 36, 2, P.PEACH)
    c.circ(212, 35, 2, P.PEACH)
    # desk with lamp and the box
    c.rect(208, 100, 100, 6, P.WOOD)
    c.rect(212, 106, 6, 32, P.WOOD)
    c.rect(298, 106, 6, 32, P.WOOD)
    c.rect(240, 106, 58, 18, P.WOOD)
    c.rect(242, 108, 54, 7, P.OCHRE)
    c.rect(262, 110, 12, 2, P.GOLD)
    c.line(292, 100, 292, 76, P.INK)
    c.tri(282, 76, 302, 76, 292, 66, P.JADE)
    if not s.on('box_open'):
        c.rect(222, 88, 30, 12, P.LACQUER)
        c.rect(222, 88, 30, 3, P.VERMILION)
        c.rect(235, 91, 4, 3, P.GOLD)
    else:
        c.rect(222, 92, 30, 8, P.LACQUER)
        c.rect(220, 84, 34, 5, P.VERMILION)
    # red suitcase by the door
    if not s.on('packed'):
        c.rect(18, 146, 22, 18, P.VERMILION)
        c.rect(18, 146, 22, 2, P.LACQUER)
        c.rect(25, 142, 8, 4, P.INK)
    # door on the right edge
    c.rect(306, 44, 14, 84, P.WOOD)
    c.rect(308, 84, 3, 3, P.GOLD)


def anim(s, look: SceneLook, frame: int) -> None:
    import pyxel

    # lamp light pool on the desk
    pyxel.dither(0.25)
    pyxel.tri(282, 77, 302, 77, 316, 100, P.LAMP)
    pyxel.tri(282, 77, 268, 100, 316, 100, P.LAMP)
    pyxel.dither(1.0)


async def enter(c: ScriptContext) -> None:
    if c.flag('ch0'):
        return
    c.set('ch0')
    await c.chapter(0)
    await c.narrate('Квартира деда. Сентябрь. Сорок дней прошло, а здесь всё как при нём: книги, старая лампа, берёзы за окном.')
    await c.narrate('На столе — коробка. На крышке моё имя, его почерком.')


async def open_box(c: ScriptContext) -> None:
    if c.flag('box_open'):
        await c.narrate('Коробка пуста. Всё, что в ней было, теперь со мной.')
        return
    c.set('box_open')
    c.sfx('open')
    await c.narrate('Внутри — толстый конверт, тетрадь в красной обложке, старая фотография и кисть.')
    for it in ('letter', 'diary', 'photo', 'brush'):
        c.give(it)
    await c.read('envelope')
    await c.narrate('На конверте нет ни одной русской буквы. Под конвертом — записка деда.')
    for part in NOTE:
        await c.narrate(part)
    await c.event('brush_flicker')
    await c.narrate('Кисть вздрагивает в руке — и в воздухе на миг остаётся золотая черта. Показалось?')


async def look_photo(c: ScriptContext) -> None:
    await c.narrate('Та же фотография, что в коробке, только в рамке. Двое на каменной лестнице, под дождём. Дед смеётся.')
    await c.read('photo_back')


async def window(c: ScriptContext) -> None:
    await c.narrate('Берёзы уже желтеют. Дед любил говорить, что на горе Тайшань солнце встаёт иначе.')


async def shelf(c: ScriptContext) -> None:
    await c.narrate('Книги о мостах, о бетоне и сопромате. И один потрёпанный китайский словарь 1957 года — весь в закладках.')


async def suitcase(c: ScriptContext) -> None:
    if not c.flag('box_open'):
        await c.narrate('Красный чемодан собран. Не хватает только главного — того, что лежит на столе.')
        return
    if not c.flag('packed'):
        c.set('packed')
        await c.narrate('Кладу в чемодан конверт, дневник, фотографию и кисть. Паспорт с визой — в карман.')


async def leave(c: ScriptContext) -> bool:
    if not c.flag('box_open'):
        await c.narrate('Сначала коробка на столе.')
        return False
    if not c.flag('packed'):
        await suitcase(c)
    await c.narrate('Самолёт до Цзинаня. Девять часов над облаками. Телефон садится ещё в воздухе.')
    return True


register(
    SceneDef(
        id='0a',
        chapter=0,
        title='Комната деда',
        zh='',
        art=art,
        anim=anim,
        look=lambda s: SceneLook('day'),
        path=[(40, 164), (180, 166), (300, 162)],
        entries={'start': 150},
        hotspots=[
            HotspotDef('box', 'Коробка', (218, 82, 38, 20), stand_at=230, on_click=open_box, cursor='hand'),
            HotspotDef('photo_wall', 'Фотография', (194, 28, 30, 24), stand_at=208, on_click=look_photo),
            HotspotDef('window', 'Окно', (92, 22, 82, 80), stand_at=130, on_click=window),
            HotspotDef('shelf', 'Книжная полка', (8, 32, 66, 96), stand_at=60, on_click=shelf),
            HotspotDef('suitcase', 'Чемодан', (16, 140, 26, 26), stand_at=48, on_click=suitcase, visible=lambda s: not s.on('packed'), cursor='hand'),
        ],
        exits=[ExitDef('door', '1a', 'gate', (302, 40, 18, 90), 'right', 296, 'В дорогу', guard=leave)],
        on_enter=enter,
    )
)

"""Chapter 6 · 十八盘 «Восемнадцать поворотов» — the night climb: fog, rain, the porters' chant."""
from __future__ import annotations

import pyxel

from ...art import kit, picto
from ...art import palette as P
from ...art.pictures import icon_for, picture
from ...art.sketches import sketch
from ...core.types import ActorDef, ExitDef, HotspotDef, PageDef, SceneDef, SceneLook, ScriptContext, SignDef, TextDef
from .. import hints, pages, texts, words
from ..world import register
from ._common import cycle, fig, no

texts.add(
    TextDef(
        'diary_12', 'diary', 'Дневник деда · 12',
        '今天我们第一次夜里爬山。\n下大雨了，我们在一棵老松树下面等雨停。\n'
        '李明说：两千多年以前，秦始皇也在这棵树下面等过雨。\n我说："那这棵树比我们更累！"李明笑了。',
        '«Сегодня мы впервые шли в гору ночью. Хлынул дождь, и мы пережидали его под старой сосной. '
        'Ли Мин сказал: больше двух тысяч лет назад здесь же пережидал дождь Цинь Шихуан. Я сказал: „Значит, это дерево устало больше нас!“ Ли Мин засмеялся».',
        chapter=6, date='一九六零年八月十五号', sketch='pine_rain',
    ),
    TextDef(
        'diary_13', 'diary', 'Дневник деда · 13',
        '李先生把笔借给我。我写了一个"火"字，可是什么变化都没有。\n'
        '李先生说："你还不了解这个字。别着急，慢慢来。"\n我觉得汉字越来越有意思了。',
        '«Учитель Ли одолжил мне кисть. Я написал знак „огонь“ — и ничего не изменилось. '
        'Учитель сказал: „Ты ещё не понимаешь этот знак. Не торопись, всё придёт“. Мне кажется, иероглифы всё интереснее».',
        chapter=6, date='一九六零年九月一号', sketch='magic_brush',
    ),
    TextDef(
        'pine_legend', 'stone', 'Стела у сосны',
        '五大夫松\n秦始皇上泰山的时候，下了大雨。\n他在这棵松树下面等雨停。\n后来，这棵松树被叫作"五大夫"。',
        'Сосна пятого ранга. Когда Цинь Шихуан поднимался на Тайшань, пошёл сильный дождь. Он переждал его под этой сосной. '
        'С тех пор сосну зовут «сановником пятого ранга».',
        chapter=6,
    ),
)

# ---------------------------------------------------------------- 6a · the Cloud-step bridge


def fog_look(s) -> SceneLook:
    return SceneLook('night', mist=not s.on('fog_blown') and not s.on('fog_done'), lantern=True)


def fog_art(s, look: SceneLook) -> None:
    c = kit.C
    kit.sky([(P.LIGHT_BLUE, 40), (P.MIST, 30), (P.WHITE, 40)])
    kit.stars(161, 50, 60)
    kit.ridge(60, 12, 30, 161, P.PERIWINKLE)
    kit.cliff(0, 70, 60, 110, P.STONE, P.GREY, P.PLUM, seed=162)
    kit.cliff(260, 60, 60, 120, P.STONE, P.GREY, P.PLUM, seed=163)
    # the waterfall and the little stone bridge
    c.rect(150, 40, 16, 100, P.LIGHT_BLUE)
    for i in range(6):
        c.line(152 + i * 2, 40, 152 + i * 2, 139, P.WHITE if i % 2 else P.MIST)
    kit.bridge_arch(120, 118, 76, 16, P.STONE, P.PLUM)
    kit.ground(140, P.MOSS, P.JADE, seed=164, density=0.03)
    # the forks of the path, visible only when the fog is gone
    if s.on('fog_blown') or s.on('fog_done'):
        kit.path_band([(200, 140), (230, 120), (250, 100)], 6, P.PAPER)
        kit.path_band([(200, 140), (240, 150), (300, 150)], 6, P.PAPER)
        kit.path_band([(250, 100), (240, 80), (260, 60)], 6, P.PAPER)
    kit.path_band([(0, 164), (160, 166), (320, 162)], 12, P.PAPER, P.STONE)


def fog_front(s, look: SceneLook) -> None:
    if s.on('fog_blown') or s.on('fog_done'):
        return
    kit.C.dither(0.55)
    kit.C.rect(0, 40, 320, 110, P.MIST)
    kit.C.dither(1.0)


async def fog_enter(c: ScriptContext) -> None:
    if c.flag('ch6'):
        return
    c.set('ch6')
    await c.chapter(6)
    await c.narrate('Ночь. Лампа бабушки Ван светит на три шага вперёд. У водопада — туман такой густой, что не видно тропы.')
    await c.say('zhao6', '喂——！你在哪儿？')
    await c.narrate('Голос Лао Чжао — откуда-то сверху. Он уже прошёл этот участок.')


FORKS = [
    ('往左走！', 0),
    ('然后往上走！', 1),
    ('最后往右走！别往下走！', 2),
]
FORK_OPTIONS = [{'zh': '往左'}, {'zh': '往上'}, {'zh': '往右'}, {'zh': '往下'}]


async def fog_path(c: ScriptContext) -> None:
    if c.flag('fog_done'):
        await c.narrate('Тропа ведёт вверх, к сосне.')
        return
    await c.say('zhao6', '这段路很难走！我说，你走！')
    for call, right in FORKS:
        await c.say('zhao6', call)
        idx = await c.puzzle('choose', prompt='Развилка. Куда идти?', options=FORK_OPTIONS)
        if idx is None:
            return
        if idx != right:
            await c.narrate('Под ногой — пустота. Отступаю назад. Туман.')
            await c.say('zhao6', '不对！你听清楚：')
            return
    c.set('fog_done')
    await c.say('zhao6', '好！你上来了！')
    await c.narrate('Туман остаётся внизу. Под ногами — ступени.')


async def fog_spell(c: ScriptContext, spell) -> bool:
    if spell.power != 'full' or c.flag('fog_done'):
        return False
    if spell.is_thing('风') or spell.says(noun='风', adj='大') or spell.acts('刮风'):
        c.set('fog_blown')
        await c.event('wind')
        await c.narrate('Порыв ветра срывает туман с тропы. На миг видны все развилки: налево, потом вверх, потом направо.')
        return True
    return False


async def zhao6_talk(c: ScriptContext) -> None:
    await cycle(c, 'zhao6_n', 'zhao6', ['又黑，而且冷！', '我几乎看不见你！', '我们挑山工晚上也上山。习惯了！'])


async def fog_up(c: ScriptContext) -> bool:
    if c.flag('fog_done'):
        return True
    if c.flag('fog_blown'):
        c.set('fog_done')
        await c.narrate('Пока ветер держит туман, поднимаюсь по видимой тропе: налево, вверх, направо.')
        return True
    await c.narrate('В тумане тропа раздваивается и пропадает. Наугад идти опасно. Лао Чжао кричит сверху — надо слушать.')
    return False


register(
    SceneDef(
        id='6a', chapter=6, title='Мост облачных шагов', zh='云步桥',
        art=fog_art, front=fog_front, look=fog_look,
        path=[(8, 164), (160, 166), (312, 162)],
        entries={'bottom': 20, 'top': 300},
        actors=[
            ActorDef('zhao6', 'Голос Лао Чжао', fig(P.STONE, P.OCHRE, 'jacket', 'straw', kind='old', prop='pole'), 262, 66, 'left',
                     stand_at=280, on_talk=zhao6_talk),
        ],
        hotspots=[
            HotspotDef('fork', 'Развилка в тумане', (200, 60, 90, 90), stand_at=260, on_click=fog_path, cursor='hand'),
        ],
        signs=[SignDef('bridge', '云步桥', 134, 98, 'carved')],
        exits=[
            ExitDef('bottom', '5d', 'top', (0, 100, 10, 70), 'left', 12, 'Средние ворота'),
            ExitDef('up', '6b', 'bottom', (300, 90, 20, 80), 'right', 310, 'Вверх', guard=fog_up),
        ],
        on_enter=fog_enter,
        on_spell=fog_spell,
        music='night',
    )
)

# ---------------------------------------------------------------- 6b · the Fifth-rank pine


def pine_look(s) -> SceneLook:
    return SceneLook('night', rain=s.on('rain6') and not s.on('rain_stopped'), lantern=True)


def pine_art(s, look: SceneLook) -> None:
    c = kit.C
    kit.sky([(P.LIGHT_BLUE, 40), (P.MIST, 30), (P.WHITE, 40)])
    kit.ridge(70, 10, 30, 171, P.PERIWINKLE)
    kit.cliff(0, 60, 80, 120, P.STONE, P.GREY, P.PLUM, seed=172)
    kit.ground(132, P.MOSS, P.JADE, seed=173, density=0.03)
    # the great pine
    kit.pine(186, 132, 80, P.PINE, P.JADE, P.WOOD, lean=6, seed=174)
    c.rect(184, 100, 8, 32, P.WOOD)
    # the stele of the legend
    kit.stele(240, 146, 22, 30)
    kit.path_band([(0, 164), (160, 166), (320, 160)], 12, P.PAPER, P.STONE)


async def pine_enter(c: ScriptContext) -> None:
    if c.flag('pine_in'):
        return
    c.set('pine_in')
    c.set('rain6')
    await c.narrate('Как и обещал прогноз: сначала редкие капли, потом ливень. Под огромной сосной сухо — там уже кто-то прячется.')
    c.unlock('diary_12')


async def hiker_talk(c: ScriptContext) -> None:
    if c.flag('rain_stopped') or c.flag('umbrella_given'):
        await cycle(c, 'hk_n', 'hiker6', ['你真关心别人！谢谢！', '爬山对健康很好，可是今天太累了！', '我们一起走吧！'])
        return
    await c.say('hiker6', '我忘记带伞了！雨太大了，我不能走。')
    await c.say('hiker6', '除了我们，山上几乎没有别人。')


async def hiker_item(c: ScriptContext, item: str) -> bool:
    if item == 'umbrella' and not c.flag('umbrella_given'):
        c.take('umbrella')
        c.set('umbrella_given')
        await c.say('hiker6', '你的伞给我？那你呢？')
        await c.narrate('Показываю на куртку Ли Мина: она не промокает.')
        await c.say('hiker6', '你真关心别人！谢谢！')
        await c.say('hiker6', '爬山对健康很好，可是今天太累了！')
        return True
    return False


async def stop_rain(c: ScriptContext) -> None:
    c.set('rain_stopped')
    await c.event('rain_stop')
    await c.narrate('Капли повисают в воздухе — и тают. Дождь кончился, как будто его выключили.')
    await c.say('hiker6', '雨停了！你……你是怎么做的？')
    await c.say('hiker6', '爬山对健康很好，可是今天太累了！')


async def pine_spell(c: ScriptContext, spell) -> bool:
    if spell.power != 'full' or c.flag('rain_stopped'):
        return False
    if spell.says(noun='雨', verb='停') or spell.acts('停') or spell.says(noun='雨', neg=True, verb='下'):
        await stop_rain(c)
        return True
    return False


async def pine_tree(c: ScriptContext) -> None:
    await c.narrate('Сосна Пятого ранга. Ствол в три обхвата, ветви как крыша.')


async def pine_item(c: ScriptContext, item: str) -> bool:
    if item == 'fu' and not c.flag('rain_stopped'):
        await c.narrate('Жёлтая бумага для талисманов. Если написать на ней — сбудется. Но что писать? Кисть (笔) пишет прямо в воздухе.')
        return True
    return False


async def pine_up(c: ScriptContext) -> bool:
    if c.flag('rain_stopped') or c.flag('umbrella_given') or c.has('umbrella'):
        return True
    await c.narrate('Ливень стеной. Без зонта дальше не пройти.')
    return False


register(
    SceneDef(
        id='6b', chapter=6, title='Сосна пятого ранга', zh='五大夫松',
        art=pine_art, look=pine_look,
        path=[(8, 164), (160, 166), (312, 160)],
        entries={'bottom': 20, 'top': 300},
        actors=[
            ActorDef('hiker6', 'Промокшая туристка', fig(P.PINK, P.WHITE, 'jacket', 'ponytail', prop='bag'), 176, 154, 'right',
                     on_talk=hiker_talk, on_item=hiker_item),
        ],
        hotspots=[
            HotspotDef('pine', 'Сосна', (150, 40, 80, 92), stand_at=190, on_click=pine_tree, on_item=pine_item, on_spell=pine_spell, tags=('松', '树')),
            HotspotDef('stele', 'Стела', (236, 108, 30, 38), stand_at=248, on_click=lambda c: c.read('pine_legend')),
        ],
        signs=[SignDef('pine', '五大夫松', 214, 24, 'plaque')],
        exits=[
            ExitDef('bottom', '6a', 'top', (0, 100, 10, 70), 'left', 12, 'Мост облачных шагов'),
            ExitDef('up', '6c', 'bottom', (300, 90, 20, 80), 'right', 310, 'Вверх', guard=pine_up),
        ],
        on_enter=pine_enter,
        on_spell=pine_spell,
        music='night',
    )
)

# ---------------------------------------------------------------- 6c · the Eighteen Bends


def bends_look(s) -> SceneLook:
    return SceneLook('night', lantern=True)


def bends_art(s, look: SceneLook) -> None:
    c = kit.C
    kit.sky([(P.LIGHT_BLUE, 40), (P.MIST, 30), (P.WHITE, 40)])
    kit.stars(181, 80, 50)
    kit.cliff(0, 30, 110, 150, P.STONE, P.GREY, P.PLUM, seed=182)
    kit.cliff(210, 30, 110, 150, P.STONE, P.GREY, P.PLUM, seed=183)
    kit.stairs(160, 176, 120, 160, 20, 20, P.GREY, P.STONE, steps=30)
    # the South Gate of Heaven far above, lit
    kit.gate_tower(146, 24, 28, 14, P.VERMILION, light=True)
    # lamps of other climbers on the stairs
    for x, y in ((150, 120), (168, 90), (156, 64), (164, 44)):
        c.pset(x, y, P.LAMP)


async def bends_enter(c: ScriptContext) -> None:
    if c.flag('bends_in'):
        return
    c.set('bends_in')
    c.unlock('diary_13')
    await c.narrate('Восемнадцать поворотов. Лестница уходит в небо почти отвесно. Далеко вверху светятся Южные небесные ворота.')


CHANT = [
    ('山再高——', [{'zh': '也要上！'}, {'zh': '不上了！'}, {'zh': '坐索道！'}], 0),
    ('路再长——', [{'zh': '快点儿跑！'}, {'zh': '慢慢走！'}, {'zh': '回家吧！'}], 1),
    ('累不累？——', [{'zh': '累极了！'}, {'zh': '我要睡觉！'}, {'zh': '唱歌就不累！'}], 2),
]


async def zhao_chant(c: ScriptContext) -> None:
    if c.flag('chant_done'):
        await cycle(c, 'chant_n', 'zhao7', ['走"之"字，不累！', '最后一段路最难，也最近！', '南天门就在上面！'])
        return
    await c.say('zhao7', '十八盘最难走。我们挑山工一边走，一边唱。你跟我唱！')
    for call, options, right in CHANT:
        await c.say('zhao7', call)
        idx = await c.puzzle('choose', prompt='Как ответить на запев?', options=options)
        if idx is None:
            return
        if idx != right:
            await c.say('zhao7', '哈哈，不对！我们从头再来！')
            return
        await c.say('player', options[right]['zh'], auto=40)
    c.set('chant_done')
    await c.say('zhao7', '唱得好！你看，我们已经走了一半了！')
    await c.say('zhao7', '走路要走"之"字：往左，往右，往左……这样不累。')
    await c.narrate('Лао Чжао показывает, как идти зигзагом, будто пишешь знак 之 ногами. И правда, легче.')


async def tired_talk(c: ScriptContext) -> None:
    if c.flag('tired_ok'):
        await cycle(c, 'tired_n', 'tired', ['谢谢你！舒服多了！', '这段路比较难，可是风景特别好！'])
        return
    await c.say('tired', '我累极了……我几乎走不动了。')
    await c.say('tired', '越往上越冷，也更难走。')


async def tired_item(c: ScriptContext, item: str) -> bool:
    if item in ('drink', 'water', 'pancake', 'banana', 'apple') and not c.flag('tired_ok'):
        c.take(item)
        c.set('tired_ok')
        await c.say('tired', '谢谢你！舒服多了！')
        await c.say('tired', '你能上去吗？')
        await c.say('player', '当然能！', auto=40)
        await c.say('tired', '这段路比较难，可是风景特别好！')
        return True
    return False


async def tired_spell(c: ScriptContext, spell) -> bool:
    if spell.power != 'full' or c.flag('tired_ok'):
        return False
    if spell.acts('休') or spell.acts('休息') or spell.is_special('休息'):
        c.set('tired_ok')
        await c.narrate('Путник садится на ступень, закрывает глаза — и через минуту встаёт свежим.')
        await c.say('tired', '奇怪，我不累了！谢谢你！')
        await c.say('tired', '这段路比较难，可是风景特别好！')
        return True
    return False


async def bends_up(c: ScriptContext) -> bool:
    if c.flag('chant_done'):
        await c.narrate('Шаг, ещё шаг. Зигзагом, с песней. Южные небесные ворота всё ближе.')
        return True
    await c.narrate('Ноги дрожат. Одному не подняться. Лао Чжао машет: «Иди сюда, споём!»')
    return False


register(
    SceneDef(
        id='6c', chapter=6, title='Восемнадцать поворотов', zh='十八盘',
        art=bends_art, look=bends_look,
        path=[(8, 168), (160, 170), (312, 168)],
        entries={'bottom': 20, 'top': 160},
        actors=[
            ActorDef('zhao7', 'Лао Чжао', fig(P.STONE, P.OCHRE, 'jacket', 'straw', kind='old', prop='pole'), 196, 164, 'left',
                     on_talk=zhao_chant),
            ActorDef('tired', 'Уставший путник', fig(P.DARK_BLUE, P.WHITE, 'jacket', 'cap', pose='sit'), 110, 164, 'right',
                     on_talk=tired_talk, on_item=tired_item, on_spell=tired_spell),
        ],
        signs=[SignDef('bends', '十八盘', 20, 40, 'carved', vertical=True)],
        exits=[
            ExitDef('bottom', '6b', 'top', (0, 100, 10, 70), 'left', 12, 'Сосна'),
            ExitDef('up', '7a', 'bottom', (140, 20, 40, 120), 'up', 160, 'Вверх, к Южным воротам', guard=bends_up),
        ],
        on_enter=bends_enter,
        music='night',
    )
)

# ---------------------------------------------------------------- pages, pictures, glossary, hints

pages.add(
    PageDef('fog6', 'Туман', 6, ('往下', '然后', '最后', '几乎', '而且'), kind='phrase',
            phrases=('别往下走！', '然后往上走！', '最后往右走！', '我几乎看不见你！', '又黑，而且冷！')),
    PageDef('pine6', 'Под сосной', 6, ('忘记', '关心', '别人', '除了', '健康'), kind='phrase',
            phrases=('我忘记带伞了！', '你真关心别人！', '你真关心别人！', '除了我们，山上几乎没有别人。', '爬山对健康很好')),
    PageDef('legend6', 'Сосна пятого ранга', 6, ('秦始皇', '松树', '棵', '停', '被'), kind='phrase',
            phrases=('秦始皇上泰山的时候', '他在这棵松树下面等雨停。', '他在这棵松树下面等雨停。', '他在这棵松树下面等雨停。', '这棵松树被叫作"五大夫"。')),
    PageDef('chant6', 'Песня носильщиков', 6, ('再', '也要', '慢慢', '一半'), kind='phrase',
            phrases=('山再高——', '也要上！', '慢慢走！', '我们已经走了一半了！')),
    PageDef('tired6', 'Уставший путник', 6, ('极', '更', '比较', '特别', '当然'), kind='phrase',
            phrases=('我累极了……', '越往上越冷，也更难走。', '这段路比较难', '可是风景特别好！', '当然能！')),
    PageDef('diary12', 'Ночь под сосной', 6, ('夜里', '大雨', '等雨停', '更累'), kind='phrase',
            phrases=('今天我们第一次夜里爬山。', '下大雨了', '我们在一棵老松树下面等雨停。', '那这棵树比我们更累！')),
    PageDef('diary13', 'Кисть не пишет', 6, ('借', '变化', '了解', '有意思'), kind='phrase',
            phrases=('李先生把笔借给我。', '可是什么变化都没有。', '你还不了解这个字。', '我觉得汉字越来越有意思了。')),
    PageDef('night6', 'Ночь в горах', 6, ('松', '雨', '云', '星星'), kind='picture'),
)

icon_for('松', 'tree')


@picture('雨')
def _(x: int, y: int) -> None:
    pyxel.elli(x + 4, y + 2, 24, 10, P.STONE)
    for i in range(6):
        pyxel.line(x + 5 + i * 4, y + 14 + (i % 2) * 3, x + 3 + i * 4, y + 20 + (i % 2) * 3, P.LIGHT_BLUE)


@picture('云')
def _(x: int, y: int) -> None:
    pyxel.rect(x, y, 32, 32, P.LIGHT_BLUE)
    pyxel.elli(x + 4, y + 12, 16, 10, P.WHITE)
    pyxel.elli(x + 12, y + 8, 16, 12, P.WHITE)
    pyxel.elli(x + 16, y + 14, 14, 8, P.WHITE)


@picture('星星')
def _(x: int, y: int) -> None:
    pyxel.rect(x, y, 32, 32, P.NAVY)
    for dx, dy in ((6, 6), (20, 4), (26, 16), (12, 20), (4, 26), (22, 26)):
        pyxel.pset(x + dx, y + dy, P.LAMP)
    pyxel.line(x + 14, y + 10, x + 18, y + 10, P.WHITE)
    pyxel.line(x + 16, y + 8, x + 16, y + 12, P.WHITE)


@sketch('pine_rain')
def _(x: int, y: int) -> None:
    pyxel.line(x + 40, y + 42, x + 42, y + 20, P.INK)
    for i in range(4):
        pyxel.line(x + 22 + i * 3, y + 12 + i * 4, x + 62 - i * 3, y + 12 + i * 4, P.INK)
    for i in range(10):
        pyxel.line(x + 4 + i * 8, y + 2, x + 2 + i * 8, y + 8, P.STONE)
    picto.person(x + 34, y + 42, P.INK)
    picto.person(x + 48, y + 42, P.INK)


words.add('''
云步桥 — Мост облачных шагов
往下 — вниз
然后 — затем
最后 — в конце, наконец
几乎 — почти
而且 — к тому же
这段路 — этот участок пути
五大夫松 — Сосна пятого ранга
忘记 — забыть
关心 — заботиться
别人 — другие люди
除了 — кроме
健康 — здоровье
秦始皇 — Цинь Шихуан, первый император
松树 — сосна
停 — остановиться
被 — (показатель пассива)
十八盘 — Восемнадцать поворотов
再 — ещё, снова; как бы ни
也要 — всё равно надо
慢慢 — медленно
一半 — половина
极 — крайне
更 — ещё более
比较 — сравнительно
特别 — особенно
当然 — конечно
风景 — пейзаж
夜里 — ночью
大雨 — ливень
等雨停 — ждать, пока дождь кончится
更累 — ещё более уставший
借 — одолжить
变化 — перемена
了解 — понимать, знать
有意思 — интересный
星星 — звёзды
''')

hints.add(lambda s: s.scene == '6a' and not s.on('fog_done'),
          'В тумане не видно тропы. Нажмите на развилку и слушайте Лао Чжао: 往左 — налево, 往上 — вверх, 往右 — направо. Или развейте туман ветром (风).')
hints.add(lambda s: s.scene == '6b' and not s.on('rain_stopped') and not s.on('umbrella_given'),
          'Ливень. Туристка забыла зонт — отдайте ей свой (雨伞). Или остановите дождь фразой кистью: «дождь» + «остановиться».')
hints.add(lambda s: s.scene == '6c' and not s.on('chant_done'),
          'Лао Чжао поёт запев — отвечайте по смыслу: гора высока — всё равно поднимемся; путь долог — идём медленно; устал? — с песней не устаёшь.')

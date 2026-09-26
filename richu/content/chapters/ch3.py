"""Chapter 3 · 山下 «У подножия» — grandfather's bridge, the village, the school, the arch."""
from __future__ import annotations

import pyxel

from ...art import kit, picto
from ...art import palette as P
from ...art.pictures import icon_for, picture
from ...art.sketches import sketch
from ...core.numerals import from_hanzi
from ...core.phrases import normalize
from ...core.types import ActorDef, ExitDef, HotspotDef, ItemDef, PageDef, SceneDef, SceneLook, ScriptContext, SignDef, TextDef
from .. import hints, items, pages, texts, words
from ..world import register
from ._common import cycle, fig, no, yes

# ---------------------------------------------------------------- items and texts

items.add(
    ItemDef('bucket', '桶', 'bucket', 'Старое деревянное ведро рыбака.'),
    ItemDef('water', '水', 'bucket_water', 'Ведро речной воды. Тяжёлое.'),
    ItemDef('firewood', '柴', 'wood', 'Вязанка сухих дров.'),
    ItemDef('pencil', '铅笔', 'pencil', 'Жёлтый карандаш с ластиком. Изгрызенный.'),
    ItemDef('lamp', '灯', 'oil_lamp', 'Старая керосиновая лампа бабушки Ван. Светит ровно и тепло.'),
    ItemDef('old_photo', '老照片', 'photo', 'Фото 1959 года: мост, трое на перилах.'),
    ItemDef('drawing', '画', 'drawing', 'Рисунок Сяолуна: мост, собака и солнце.'),
)

texts.add(
    TextDef(
        'bridge_plaque', 'stone', 'Камень у моста', '大汶河大桥\n一九六零年\n中苏友好',
        'Мост через реку Давэньхэ. 1960 год. Китайско-советская дружба.',
        chapter=3,
    ),
    TextDef(
        'wang_photo', 'sign', 'Фото бабушки Ван, оборот', '一九五九年　大桥上\n小安　李明　小王',
        '1959 год, на мосту. Сяо Ань, Ли Мин и маленькая Ван — сама бабушка.',
        chapter=3,
    ),
    TextDef(
        'drawing', 'sign', 'Рисунок Сяолуна', '大桥　太阳\n白白　我\n送给我的朋友',
        'Мост, солнце. Байбай и я. Моему другу.',
        chapter=3,
    ),
    TextDef(
        'diary_3', 'diary', 'Дневник деда · 3',
        '今天我们开始修桥。大汶河很大，水很多。\n中国工人工作非常努力，他们每天早上五点起床。\n'
        '一个年轻人帮我拿东西。他叫李明，他很爱笑。',
        '«Сегодня мы начали строить мост. Давэньхэ большая, воды много. Китайские рабочие работают очень старательно, '
        'каждый день встают в пять утра. Один молодой человек помог мне нести вещи. Его зовут Ли Мин, он всё время смеётся».',
        chapter=3, date='一九五八年九月二十五号', sketch='bridge_1958',
    ),
    TextDef(
        'diary_4', 'diary', 'Дневник деда · 4',
        '李明问我："你为什么来中国？"\n我说："因为我会修桥。"\n他说："我希望以后也能修桥。"\n'
        '晚上我们在河边写字。他教我写"山"、"水"、"火"、"木"。\n他的字非常漂亮，我的字很难看。',
        '«Ли Мин спросил: „Почему ты приехал в Китай?“ Я ответил: „Потому что умею строить мосты“. Он сказал: „Надеюсь, потом и я смогу“. '
        'Вечерами мы пишем знаки у реки. Он учит меня писать „гора“, „вода“, „огонь“, „дерево“. Его знаки очень красивые, мои — корявые».',
        chapter=3, date='一九五九年五月一号', sketch='river_writing',
    ),
    TextDef(
        'diary_5', 'diary', 'Дневник деда · 5',
        '今天是春节，春节是中国最大的节日。\n村子里的人非常热情，请我们吃饭。\n王家的小女儿给我们唱歌，她唱得非常好听。\n'
        '我第一次觉得，我不是外国人。\n李明说："这也是你的家。"',
        '«Сегодня Праздник Весны — самый большой праздник Китая. Деревенские очень радушны, позвали нас к столу. Младшая дочка Ванов пела нам — очень красиво. '
        'Впервые я почувствовал, что я здесь не иностранец. Ли Мин сказал: „Это и твой дом“».',
        chapter=3, date='一九六零年一月二十八号', sketch='spring_festival',
    ),
)

# ---------------------------------------------------------------- 3a · the bridge


def bridge_look(s) -> SceneLook:
    return SceneLook('day', mist=not s.on('fisher_story'))


DECK = 44
SPAN = 64


def _arch_top(x: float, left: int) -> float:
    """The underside of the arch between two piers (a half-ellipse)."""
    rx = SPAN / 2 - 4
    cx = left + SPAN / 2
    d = (x - cx) / rx
    return 86 - 30 * max(0.0, 1 - d * d) ** 0.5


def bridge_art(s, look: SceneLook) -> None:
    c = kit.C
    kit.sky([(P.LIGHT_BLUE, 26), (P.MIST, 24), (P.WHITE, 40)])
    kit.ridge(62, 8, 40, 61, P.PERIWINKLE, peaks=[(250, 28, 110)])
    kit.ridge(74, 5, 24, 62, P.MIST)
    # the far bank with willows
    c.rect(0, 74, 320, 8, P.MOSS)
    for x in (22, 86, 150, 214, 278):
        c.rect(x, 62, 2, 14, P.WOOD)
        for i in range(6):
            c.line(x - 6 + i * 3, 60 + i, x - 8 + i * 4, 74, P.JADE)
    kit.water(80, 56, P.TEAL, P.MINT, seed=63)
    # the bridge: a deck on stone piers with shallow arches
    c.rect(0, DECK, 320, 6, P.GREY)
    c.line(0, DECK + 6, 319, DECK + 6, P.STONE)
    kit.railing(0, 319, DECK, P.GREY, 6)
    for i in range(-1, 6):
        left = i * SPAN + 16
        for x in range(max(0, left), min(320, left + SPAN)):
            top = _arch_top(x + 0.5, left)
            c.line(x, DECK + 7, x, int(top), P.GREY)
            c.pset(x, int(top), P.STONE)
        px = left
        if 0 <= px < 320 or 0 <= px + 4 < 320:
            c.rect(px - 4, DECK + 6, 8, 44, P.GREY)
            c.line(px + 3, DECK + 6, px + 3, DECK + 49, P.STONE)
            c.rect(px - 5, 88, 10, 3, P.STONE)
    # reflections of the piers
    kit.dither(0.3)
    for i in range(6):
        c.rect(i * SPAN + 12, 92, 8, 16, P.STONE)
    kit.dither(1.0)
    # the near bank
    kit.ground(134, P.MOSS, P.JADE, seed=64, density=0.05)
    c.line(0, 134, 319, 134, P.PINE)
    kit.path_band([(0, 164), (160, 166), (320, 164)], 12, P.PAPER, P.OCHRE)
    kit.grass(0, 320, 150, P.JADE, seed=65, n=40)
    # steps up to the bridge on the right
    for i in range(12):
        y = 134 - i * 7
        x = 294 + i * 2
        c.rect(x, y - 7, 320 - x, 7, P.GREY)
        c.line(x, y - 7, 319, y - 7, P.STONE)
    # the memorial stone
    c.rect(4, 104, 82, 46, P.STONE)
    c.rect(7, 107, 76, 40, P.GREY)
    c.rect(0, 148, 90, 5, P.PLUM)
    # the boat
    c.tri(190, 122, 198, 131, 198, 122, P.WOOD)
    c.rect(198, 122, 52, 9, P.WOOD)
    c.tri(250, 122, 250, 131, 258, 122, P.WOOD)
    c.line(190, 122, 258, 122, P.OCHRE)
    c.line(198, 131, 250, 131, P.INK)
    c.line(242, 122, 250, 104, P.WOOD)
    # the catch on a board: seven fish
    c.rect(140, 146, 72, 5, P.WOOD)
    c.line(140, 151, 211, 151, P.INK)
    for i in range(7):
        fx, fy = 142 + i * 10, 134 + (i % 2) * 3
        c.elli(fx, fy, 8, 5, P.LIGHT_BLUE)
        c.ellib(fx, fy, 8, 5, P.INK)
        c.tri(fx + 7, fy + 2, fx + 10, fy - 1, fx + 10, fy + 5, P.LIGHT_BLUE)
        c.pset(fx + 2, fy + 1, P.INK)


def bridge_anim(s, look: SceneLook, frame: int) -> None:
    kit.canvas(pyxel)
    kit.water_anim(80, 54, frame)
    # the boat rocks a little
    if (frame // 20) % 2:
        pyxel.line(198, 132, 250, 132, P.MINT)
    if not s.on('xl_school'):
        # Baibai the dog wags its tail beside the boy
        x, y = 124, 152
        pyxel.elli(x, y, 12, 6, P.WHITE)
        pyxel.circ(x + 12, y + 1, 3, P.WHITE)
        pyxel.pset(x + 13, y, P.INK)
        pyxel.line(x + 2, y + 6, x + 2, y + 9, P.WHITE)
        pyxel.line(x + 9, y + 6, x + 9, y + 9, P.WHITE)
        wag = 2 if (frame // 6) % 2 else -2
        pyxel.line(x, y + 2, x - 3, y + wag, P.WHITE)
    elif not s.has('pencil') and not s.on('pencil_given'):
        pyxel.line(104, 161, 112, 158, P.YELLOW)
        pyxel.pset(113, 158, P.PINK)
    kit.canvas(None)


async def bridge_enter(c: ScriptContext) -> None:
    if c.flag('ch3'):
        return
    c.set('ch3')
    await c.chapter(3)
    await c.narrate('Мост. Серый камень, шесть пролётов, перила. Шестьдесят с лишним лет назад его строил дед.')
    await c.narrate('Внизу широкая река, над водой туман. У берега в лодке сидит рыбак.')


def _count(answer: str) -> int | None:
    digits = ''.join(ch for ch in normalize(answer) if ch in '零一二两三四五六七八九十百')
    return from_hanzi(digits) if digits else None


async def fisher_talk(c: ScriptContext) -> None:
    if not c.flag('fisher_story'):
        answer = await c.ask('fisher', '早上好！你是来看大桥的吗？')
        if no(answer):
            await c.say('fisher', '不是？那你看看吧，这个桥很有名。')
        else:
            await c.say('fisher', '这个桥很有名。它比我还老！')
        await c.say('fisher', '这个桥很有历史。以前这儿没有桥，大家都坐船过河。')
        await c.say('fisher', '一九五八年，中国人和苏联人一起修这个桥。')
        await c.say('fisher', '我奶奶告诉我，那时候有一个苏联年轻人，很爱笑。大家都叫他"小安"。')
        await c.narrate('Сяо Ань! Так звали деда.')
        answer = await c.ask('fisher', '你认识小安吗？')
        a = normalize(answer)
        if '爷爷' in a or yes(answer) or '小安' in a:
            await c.say('fisher', '他是你爷爷？！太好了！')
            await c.say('fisher', '你去村子里找王奶奶吧。她认识小安！她知道很多以前的事情。')
        else:
            await c.say('fisher', '你去村子里问问王奶奶吧。她知道很多以前的事情。')
        c.set('fisher_story')
        return
    if not c.flag('fish_counted'):
        answer = await c.ask('fisher', '你帮我数一下：我今天有几条鱼？')
        n = _count(answer)
        if n == 7:
            if '条' in normalize(answer):
                await c.say('fisher', '对！七条鱼！你的汉语很好！昨天我只有三条。')
            else:
                await c.say('fisher', '对，七条！我们说："七条鱼"。')
            c.set('fish_counted')
            await c.say('fisher', '村子里的井坏了，大家都没有水。这个桶你拿去吧！')
            c.give('bucket')
            await c.narrate('Благодарю.')
            await c.say('fisher', '不客气！')
        elif n is None:
            await c.say('fisher', '几条？')
            await c.narrate('Рыбак кивает на доску с уловом у берега.')
        else:
            await c.say('fisher', '不对，不对。你再数一下！')
        return
    if c.has('bucket'):
        await c.say('fisher', '桶里没有水？河里有很多水！')
        return
    await cycle(c, 'fisher_n', 'fisher', ['河里的水很干净。', '王奶奶家在村子里，大树旁边。', '一路平安！'])


async def fisher_item(c: ScriptContext, item: str) -> bool:
    if item == 'photo':
        await c.say('fisher', '这是这个桥！旁边的人是小安吗？')
        return True
    return False


async def boy_talk(c: ScriptContext) -> None:
    if not c.flag('xl_met'):
        await c.say('boy', '你好！我叫小龙。这是我的狗，它叫白白。白白喜欢在草上跑。')
        await c.say('boy', '船上的人是我叔叔，他每天在这儿打鱼。')
        await c.say('boy', '我八岁，上二年级。')
        await c.say('boy', '我不想去学校……')
        await c.narrate('Мальчик вздыхает и бросает камешек в воду.')
        c.set('xl_met')
        return
    await c.say('boy', '今天上午有考试。我没有复习，我很担心，也很害怕。')
    answer = await c.ask('boy', '你觉得我能考好吗？')
    a = normalize(answer)
    if yes(answer) or a.startswith('能') or '能' in a and not no(answer):
        await c.say('boy', '真的吗？好！我去学校！')
        await c.say('boy', '白白，回家！')
        await c.move('boy', 330)
        c.set('xl_school')
        await c.narrate('Мальчик убегает вверх по ступеням. В траве осталось что-то жёлтое.')
    else:
        await c.say('boy', '你也觉得不能……')
        await c.narrate('Мальчик совсем сник. Может, его надо подбодрить: «能！»')


async def pencil(c: ScriptContext) -> None:
    c.give('pencil')
    await c.narrate('Жёлтый карандаш с ластиком, весь изгрызенный. Наверное, мальчика.')


async def plaque(c: ScriptContext) -> None:
    await c.read('bridge_plaque')
    if c.flag('fisher_story') and not c.flag('su_explained'):
        c.set('su_explained')
        await c.say('fisher', '"苏"就是苏联。那时候俄罗斯是苏联。')


async def river(c: ScriptContext) -> None:
    await c.narrate('Широкая река цвета глины. Течение медленное, у берега — камыш.')


async def river_item(c: ScriptContext, item: str) -> bool:
    if item == 'bucket':
        c.take('bucket')
        c.give('water')
        await c.narrate('Зачерпываю полное ведро. Тяжело, но донесу.')
        return True
    if item == 'water':
        await c.narrate('Ведро и так полное.')
        return True
    return False


async def catch(c: ScriptContext) -> None:
    await c.narrate('Улов рыбака лежит на доске: рыбы ровным рядом, хвостами в одну сторону.')


register(
    SceneDef(
        id='3a', chapter=3, title='Мост деда', zh='大桥',
        art=bridge_art, anim=bridge_anim, look=bridge_look,
        path=[(8, 164), (160, 166), (300, 164)],
        entries={'road': 20, 'village': 296},
        actors=[
            ActorDef('fisher', 'Рыбак', fig(P.NAVY, P.WOOD, 'jacket', 'straw', kind='old', pose='sit', prop='rod'), 222, 124, 'left',
                     stand_at=214, on_talk=fisher_talk, on_item=fisher_item),
            ActorDef('boy', 'Мальчик с собакой', fig(P.WHITE, P.VERMILION, 'jacket', 'short', kind='child', pose='sit'), 110, 158, 'right',
                     visible=lambda s: not s.on('xl_school'), stand_at=96, on_talk=boy_talk, tags=('人', '孩子')),
        ],
        hotspots=[
            HotspotDef('plaque', 'Памятный камень', (4, 104, 82, 46), stand_at=60, on_click=plaque),
            HotspotDef('river', 'Река', (0, 82, 290, 38), stand_at=180, on_click=river, on_item=river_item, tags=('河', '水')),
            HotspotDef('catch', 'Улов', (146, 138, 58, 16), stand_at=176, on_click=catch, tags=('鱼',)),
            HotspotDef('pencil', 'Что-то жёлтое', (100, 152, 16, 12), stand_at=108, on_click=pencil,
                       visible=lambda s: s.on('xl_school') and not s.has('pencil') and not s.on('pencil_given'), cursor='hand'),
        ],
        signs=[SignDef('plaque', '大汶河大桥\n一九六零年\n中苏友好', 10, 106, 'carved')],
        exits=[ExitDef('village', '3b', 'bridge', (300, 60, 20, 100), 'right', 300, 'Деревня')],
        on_enter=bridge_enter,
        diary=('diary_3',),
        music='river',
    )
)

# ---------------------------------------------------------------- 3b · the village


def village_look(s) -> SceneLook:
    return SceneLook('day')


def village_art(s, look: SceneLook) -> None:
    c = kit.C
    kit.sky([(P.LIGHT_BLUE, 34), (P.MIST, 24), (P.WHITE, 40)])
    kit.ridge(84, 10, 30, 71, P.PERIWINKLE, peaks=[(190, 52, 130)])
    kit.ridge(100, 6, 20, 72, P.MOSS)
    kit.ground(124, P.PEACH, P.OCHRE, seed=73, density=0.03)
    # auntie's house and her firewood
    kit.house(4, 124, 60, 44, P.PAPER, P.INK, P.WOOD, windows=2)
    for i in range(3):
        c.rect(48 + i * 2, 116 - i * 4, 22 - i * 4, 4, P.OCHRE)
        c.line(48 + i * 2, 116 - i * 4, 69 - i * 2, 116 - i * 4, P.WOOD)
    # the Li family's old gate, shut
    kit.wall(72, 92, 48, 32, P.STONE, P.PLUM, P.INK)
    kit.door(88, 100, 18, 24, P.WOOD, None)
    c.rect(95, 110, 4, 3, P.GOLD)
    # the old tree with red ribbons
    c.rect(160, 70, 10, 56, P.WOOD)
    c.line(162, 80, 150, 64, P.WOOD)
    c.line(168, 78, 182, 60, P.WOOD)
    for dx, dy, r in ((-18, -8, 16), (16, -12, 18), (0, -22, 18), (-6, 2, 14), (22, 4, 12)):
        c.circ(165 + dx, 58 + dy, r, P.PINE)
    for dx, dy, r in ((-14, -12, 10), (14, -16, 11), (2, -26, 10)):
        c.circ(165 + dx, 58 + dy, r, P.JADE)
    for rx, ry in ((150, 72), (158, 76), (176, 74), (184, 70), (168, 80)):
        c.line(rx, ry, rx, ry + 7, P.VERMILION)
    # grandmother Wang's house: red couplets by the door
    kit.house(198, 124, 64, 46, P.PAPER, P.INK, P.LACQUER, windows=2)
    c.rect(219, 106, 3, 16, P.VERMILION)
    c.rect(238, 106, 3, 16, P.VERMILION)
    # the clay stove and the kettle
    c.rect(244, 128, 20, 16, P.OCHRE)
    c.rect(244, 128, 20, 2, P.WOOD)
    c.rect(250, 136, 8, 6, P.INK)
    c.rect(248, 122, 12, 6, P.STONE)
    c.line(250, 121, 258, 121, P.INK)
    c.line(260, 124, 263, 121, P.STONE)
    # the school at the edge of the village
    c.rect(266, 72, 54, 52, P.WHITE)
    kit.roof(263, 72, 60, 8, P.VERMILION, P.LACQUER)
    kit.window(272, 84, 10, 9)
    kit.window(306, 84, 10, 9)
    c.rect(288, 100, 16, 24, P.WOOD)
    c.line(296, 100, 296, 123, P.INK)
    c.line(314, 60, 314, 72, P.GREY)
    c.rect(315, 60, 5, 4, P.VERMILION)
    # the well
    c.elli(122, 132, 26, 10, P.STONE)
    c.elli(126, 134, 18, 5, P.INK)
    c.rect(122, 137, 26, 10, P.GREY)
    c.line(122, 137, 147, 137, P.STONE)
    c.line(124, 118, 124, 136, P.WOOD)
    c.line(146, 118, 146, 136, P.WOOD)
    if not s.on('well_fixed'):
        c.line(124, 118, 136, 122, P.WOOD)
        c.line(146, 118, 140, 116, P.WOOD)
    else:
        c.line(124, 118, 146, 118, P.WOOD)
        c.line(135, 118, 135, 132, P.OCHRE)
    # cobbles along the lane
    kit.path_band([(0, 164), (160, 166), (320, 164)], 14, P.PAPER, P.OCHRE)
    r = kit.rng(74)
    for _ in range(40):
        x, y = r.randrange(0, 320), r.randrange(158, 172)
        c.line(x, y, x + 3, y, P.PEACH)


def village_anim(s, look: SceneLook, frame: int) -> None:
    kit.canvas(pyxel)
    # a bird on the tree
    bx = 180 + (4 if (frame // 90) % 2 else 0)
    pyxel.rect(bx, 66, 4, 3, P.TEAL)
    pyxel.pset(bx + 4, 66, P.ORANGE)
    if s.on('stove_fire'):
        for i in range(4):
            fx = 251 + i * 2
            h = 3 + int(pyxel.sin(frame * 20 + i * 70) * 2 + 2)
            pyxel.line(fx, 141, fx, 141 - h, P.ORANGE if i % 2 else P.YELLOW)
        for i in range(3):
            y = 118 - (frame // 2 + i * 9) % 26
            pyxel.pset(262 + int(pyxel.sin(frame * 5 + i * 90) * 2), y, P.MIST)
    kit.canvas(None)


async def village_enter(c: ScriptContext) -> None:
    if c.flag('village_in'):
        return
    c.set('village_in')
    await c.narrate('Деревня за мостом. Каменные дома, старое дерево в красных ленточках, колодец. Пахнет дымом и землёй.')


async def aunt_talk(c: ScriptContext) -> None:
    if c.flag('tea_done'):
        await cycle(c, 'aunt_n', 'aunt', ['王奶奶今天很高兴！', '你要上山吗？路上小心！'])
        return
    if c.flag('gw_water') and not c.flag('got_firewood'):
        await c.say('aunt', '你帮王奶奶打水了？谢谢你的帮助！你真是个好人！')
        await c.say('aunt', '这些柴你拿给她吧。')
        c.give('firewood')
        c.set('got_firewood')
        return
    if c.flag('aunt_asked'):
        await c.say('aunt', '王奶奶正在门口坐着呢。她家在大树旁边。')
        return
    await c.say('aunt', '你好！我姓刘，大家都叫我刘阿姨。')
    await c.say('aunt', '井坏了，所以我们都没有水。我丈夫去城里了，明天才回来。')
    await c.say('aunt', '现在大家都要去河边打水，太累了！')
    await c.say('aunt', '王奶奶是我的邻居。她一个人住，我经常照顾她。她的腿不好，不能去河边。')
    answer = await c.ask('aunt', '你能帮她打水吗？')
    if no(answer):
        await c.say('aunt', '没关系。')
    else:
        await c.say('aunt', '谢谢你！王奶奶正在门口坐着呢。')
        c.set('aunt_asked')


async def aunt_item(c: ScriptContext, item: str) -> bool:
    if item == 'water':
        await c.say('aunt', '给王奶奶吧！她家在那儿。')
        return True
    return False


async def grandma_talk(c: ScriptContext) -> None:
    if c.flag('tea_done'):
        await cycle(c, 'gw_n', 'grandma', ['你一定要找到李明！', '晚上山上很冷，多穿衣服！', '一路平安，孩子！'])
        return
    if not c.flag('grandma_met'):
        await c.say('grandma', '你好，孩子。')
        answer = await c.ask('grandma', '你从哪儿来？')
        if '俄' in normalize(answer):
            await c.say('grandma', '俄罗斯？！让我看看你……')
            await c.narrate('Старушка долго смотрит мне в лицо.')
            await c.say('grandma', '你的脸……你长得很像一个人……')
        else:
            await c.say('grandma', '我的耳朵不太好。')
        await c.say('grandma', '来，坐吧！我给你做茶。')
        await c.say('grandma', '啊……井坏了，所以没有水。')
        c.set('grandma_met')
        return
    if not c.flag('gw_water'):
        await c.say('grandma', '没有水，不能做茶。')
    elif not c.flag('gw_wood'):
        await c.say('grandma', '有水了，可是没有柴。')
    elif not c.flag('stove_fire'):
        await c.say('grandma', '有水，有柴……可是火柴没有了！附近也没有商店。')
    else:
        await grandma_story(c)


async def grandma_item(c: ScriptContext, item: str) -> bool:
    if item == 'water' and not c.flag('gw_water'):
        c.take('water')
        c.set('gw_water')
        await c.say('grandma', '水！谢谢你，孩子！')
        await c.say('grandma', '有水了，可是没有柴。')
        return True
    if item == 'firewood':
        return await give_firewood(c)
    if item == 'brush':
        return await wake_brush(c)
    if item == 'photo':
        await c.say('grandma', '这……这是小安和李明！')
        await c.say('grandma', '孩子，先做茶。你坐。')
        return True
    return False


async def give_firewood(c: ScriptContext) -> bool:
    if c.flag('gw_wood'):
        return False
    c.take('firewood')
    c.set('gw_wood')
    await c.narrate('Бабушка Ван укладывает дрова в печку и шарит по карманам.')
    await c.say('grandma', '有水，有柴……可是火柴没有了！附近也没有商店。')
    await c.narrate('Спичек нет. До лавки далеко, а бабушка еле ходит.')
    c.set('need_fire')
    return True


async def wake_brush(c: ScriptContext) -> bool:
    if not c.flag('need_fire'):
        return False
    if c.flag('brush_awake'):
        await c.narrate('Кисть готова. Нажмите «笔», напишите знак и укажите на печку.')
        return True
    if not c.state.confirmed.get('火'):
        await c.narrate('Кисть в руке тёплая, будто чего-то ждёт. Но какой знак писать? Знак огня я ещё не понимаю.')
        return True
    c.set('brush_awake')
    await c.event('brush_awake')
    await c.narrate('Кисть вздрагивает. Кончик сам тянется к печке, и я понимаю: она хочет писать.')
    await c.narrate('Дед писал в записке: «Учись, как учился я». Кисть пишет только то, что понимаешь.')
    await c.narrate('Нажмите «笔» (клавиша B), напишите знаки и укажите, куда направить кисть.')
    return True


async def stove(c: ScriptContext) -> None:
    if c.flag('stove_fire'):
        await c.narrate('В печке весело трещит огонь. Чайник начинает посвистывать.')
    elif c.flag('gw_wood'):
        await c.narrate('Дрова сложены, но огня нет.')
    else:
        await c.narrate('Глиняная печка у дома. Холодная.')


async def stove_item(c: ScriptContext, item: str) -> bool:
    if item == 'firewood':
        return await give_firewood(c)
    if item == 'brush':
        return await wake_brush(c)
    if item == 'water':
        return await grandma_item(c, 'water')
    return False


async def stove_spell(c: ScriptContext, spell) -> bool:
    if not spell.is_thing('火') or spell.power != 'full':
        return False
    if not c.flag('gw_wood'):
        await c.narrate('Огонёк вспыхивает над пустой печкой и гаснет: гореть нечему.')
        return True
    if c.flag('stove_fire'):
        return False
    c.set('stove_fire')
    await c.event('fire_lit')
    await c.narrate('Знак вспыхивает на кончике кисти, падает в печку — и дрова занимаются.')
    await grandma_story(c)
    return True


async def grandma_story(c: ScriptContext) -> None:
    if c.flag('tea_done'):
        return
    await c.say('grandma', '火！你……你会写字？')
    await c.say('grandma', '这是李家的笔！')
    answer = await c.ask('grandma', '孩子，你爷爷是不是小安？')
    if no(answer):
        await c.say('grandma', '不是？……可是这是李家的笔啊。')
    else:
        await c.say('grandma', '我知道！你笑的时候跟他一样！')
    await c.narrate('Чайник закипает. Бабушка разливает чай по чашкам и садится рядом.')
    await c.say('grandma', '一九五八年，我十五岁。苏联人来我们村子修桥。')
    await c.say('grandma', '小安和李明是好朋友。李明帮他们拿东西，小安教他说俄语。')
    await c.say('grandma', '李明的爸爸是写字的先生。这笔是他的。')
    await c.say('grandma', '晚上，他们两个人在河边写字。小安写得很认真。')
    await c.say('grandma', '一九六零年，小安要回国了。李明把这笔送给了他。')
    await c.say('grandma', '李明说："你一定要回来！"')
    await c.say('grandma', '可是小安一直没有回来……')
    await c.say('grandma', '后来，李家搬到山上去了。李明在中天门开了一个茶馆。')
    await c.say('grandma', '去年李明还回村子看我们。他八十七岁了，还每天爬山！')
    await c.say('grandma', '现在笔回来了，你也来了。')
    await c.say('grandma', '这张照片给你。你拿给李明看吧！')
    c.give('old_photo')
    await c.read('wang_photo')
    await c.narrate('Выцветшее фото: мост, трое на перилах — дед, Ли Мин и девочка с косичками.')
    await c.say('grandma', '晚上山上很黑。这个灯你也拿去。')
    c.give('lamp')
    c.unlock('diary_4')
    c.set('tea_done')
    await c.say('grandma', '放心吧，你一定能找到他！慢一点儿走，别着急！')
    await c.narrate('Ли Мин поднимается на вершину сегодня ночью. Путь на гору начинается за школой, у арки 岱宗坊.')


async def mother_talk(c: ScriptContext) -> None:
    await cycle(c, 'mother_n', 'mother', ['儿子，别玩水！', '我儿子五岁了，明年上学。', '我女儿在学校，她上二年级。'])


async def son_talk(c: ScriptContext) -> None:
    step = int(c.flag('son_step') or 0)
    if step == 0:
        answer = await c.ask('son', '你有哥哥吗？')
        if no(answer):
            await c.say('son', '我也没有。')
        else:
            await c.say('son', '我也想要一个哥哥！')
    elif step == 1:
        await c.say('son', '我有一个姐姐。她叫小红，在学校上课。我家后面有一条小河。')
    elif step == 2:
        await c.say('son', '妈妈说，明年我会有一个弟弟或者妹妹！')
    else:
        await c.say('son', '你看！树上有一只鸟！')
    c.set('son_step', step + 1)


async def well(c: ScriptContext) -> None:
    if c.flag('well_fixed'):
        await c.narrate('Ворот снова на месте. Ведро плещется в глубине.')
    else:
        await c.narrate('Колодец. Ворот сломан, верёвка оборвана.')


async def well_spell(c: ScriptContext, spell) -> bool:
    if spell.power != 'full' or c.flag('well_fixed'):
        return False
    if spell.acts('修') or spell.says(noun='井', adj='好'):
        c.set('well_fixed')
        await c.narrate('Ворот со скрипом встаёт на место, верёвка сама завязывается узлом.')
        await c.say('aunt', '井好了！太好了！')
        return True
    return False


async def tree(c: ScriptContext) -> None:
    await c.narrate('Старое дерево. На ветвях — красные ленточки с пожеланиями. На табличке — его возраст.')


async def li_gate(c: ScriptContext) -> None:
    if c.flag('tea_done'):
        await c.narrate('Дом семьи Ли. Отсюда Ли Мин ушёл на гору.')
    else:
        await c.narrate('Старые ворота с замком. Здесь давно никто не живёт.')


async def road_guard(c: ScriptContext) -> bool:
    if c.flag('tea_done'):
        return True
    await c.narrate('Рыбак сказал: бабушка Ван помнит деда. Сначала — к ней.')
    return False


register(
    SceneDef(
        id='3b', chapter=3, title='Деревня', zh='村子',
        art=village_art, anim=village_anim, look=village_look,
        path=[(8, 164), (160, 166), (312, 164)],
        entries={'bridge': 20, 'school': 290, 'road': 300},
        actors=[
            ActorDef('aunt', 'Соседка у колодца', fig(P.PINK, P.WHITE, 'jacket', 'bun'), 152, 156, 'left', on_talk=aunt_talk, on_item=aunt_item),
            ActorDef('grandma', 'Бабушка Ван', fig(P.DARK_BLUE, P.WHITE, 'jacket', 'bun', kind='old', hair=P.GREY, pose='sit'), 226, 142, 'left',
                     stand_at=222, on_talk=grandma_talk, on_item=grandma_item),
            ActorDef('mother', 'Мама', fig(P.JADE, P.WHITE, 'jacket', 'ponytail'), 34, 156, 'right', on_talk=mother_talk),
            ActorDef('son', 'Малыш', fig(P.YELLOW, P.VERMILION, 'jacket', 'short', kind='child'), 52, 162, 'left', on_talk=son_talk,
                     tags=('人', '孩子')),
        ],
        hotspots=[
            HotspotDef('well', 'Колодец', (120, 116, 30, 32), stand_at=134, on_click=well, on_spell=well_spell, tags=('井',)),
            HotspotDef('stove', 'Печка', (242, 118, 24, 28), stand_at=248, on_click=stove, on_item=stove_item, on_spell=stove_spell, tags=('火',)),
            HotspotDef('tree', 'Старое дерево', (146, 36, 40, 88), stand_at=168, on_click=tree, tags=('树', '木')),
            HotspotDef('li_gate', 'Старые ворота', (72, 92, 48, 32), stand_at=96, on_click=li_gate),
        ],
        signs=[
            SignDef('age', '五百岁', 146, 92, 'tag'),
            SignDef('li', '李家', 84, 82, 'plaque'),
            SignDef('wang', '王家', 213, 84, 'plaque'),
            SignDef('school', '学校', 276, 58, 'plaque'),
        ],
        exits=[
            ExitDef('bridge', '3a', 'village', (0, 100, 10, 70), 'left', 12, 'Мост'),
            ExitDef('school', '3c', 'door', (288, 100, 16, 24), 'up', 296, 'Школа'),
            ExitDef('road', '3d', 'village', (310, 130, 10, 44), 'right', 312, 'Дорога в гору', guard=road_guard),
        ],
        on_enter=village_enter,
        music='village',
    )
)

# ---------------------------------------------------------------- 3c · the school


def school_look(s) -> SceneLook:
    return SceneLook('day')


LESSON_X = 118


def school_art(s, look: SceneLook) -> None:
    c = kit.C
    c.rect(0, 0, 320, 180, P.WHITE)
    c.rect(0, 96, 320, 30, P.MINT)
    c.line(0, 96, 319, 96, P.JADE)
    kit.tiles(126, P.GREY, P.STONE, 16)
    # windows with the morning sun
    for wx in (8, 276):
        c.rect(wx, 30, 36, 50, P.LIGHT_BLUE)
        c.rectb(wx, 30, 36, 50, P.WOOD)
        c.line(wx + 18, 30, wx + 18, 79, P.WOOD)
        c.line(wx, 55, wx + 35, 55, P.WOOD)
    kit.dither(0.3)
    c.tri(8, 80, 44, 80, 70, 126, P.LAMP)
    kit.dither(1.0)
    # the blackboard
    c.rect(86, 26, 148, 64, P.WOOD)
    c.rect(89, 29, 142, 58, P.PINE)
    c.rect(96, 88, 128, 3, P.WOOD)
    c.rect(200, 86, 6, 2, P.WHITE)
    if s.on('lesson1'):
        # little chalk pictures over the four glyphs
        x = LESSON_X
        c.line(x, 58, x + 4, 50, P.WHITE)
        c.line(x + 4, 50, x + 8, 58, P.WHITE)
        c.line(x + 5, 58, x + 9, 52, P.WHITE)
        c.line(x + 9, 52, x + 12, 58, P.WHITE)
        x += 26
        for i in range(3):
            c.line(x, 52 + i * 3, x + 3, 50 + i * 3, P.WHITE)
            c.line(x + 3, 50 + i * 3, x + 6, 52 + i * 3, P.WHITE)
            c.line(x + 6, 52 + i * 3, x + 9, 50 + i * 3, P.WHITE)
        x += 26
        c.tri(x + 5, 49, x + 1, 58, x + 9, 58, P.WHITE)
        c.tri(x + 5, 53, x + 3, 58, x + 7, 58, P.PINE)
        x += 26
        c.circb(x + 5, 52, 4, P.WHITE)
        c.line(x + 5, 56, x + 5, 60, P.WHITE)
    if s.on('face_done'):
        # the chalk face from the game stays on the board
        c.circb(214, 64, 10, P.WHITE)
        c.pset(210, 61, P.WHITE)
        c.pset(218, 61, P.WHITE)
        c.line(214, 63, 213, 66, P.WHITE)
        c.line(211, 69, 217, 69, P.WHITE)
        for i in range(-8, 9, 3):
            c.line(214 + i, 55, 215 + i, 51, P.WHITE)
    # the slogan above the board
    c.rect(98, 10, 124, 12, P.VERMILION)
    # the teacher's desk
    c.rect(150, 104, 58, 18, P.OCHRE)
    c.rect(148, 102, 62, 3, P.WOOD)
    c.rect(186, 96, 6, 6, P.WHITE)
    c.rect(192, 98, 2, 3, P.WHITE)
    # the clock
    picto.clock(254, 18, 8, 8, 40, 'minute')
    # pupils' desks (the pupils sit in front of them, facing the board)
    for dx in (36, 124, 224):
        c.rect(dx, 128, 52, 4, P.OCHRE)
        c.rect(dx, 132, 52, 6, P.WOOD)
        c.rect(dx + 2, 138, 3, 10, P.WOOD)
        c.rect(dx + 47, 138, 3, 10, P.WOOD)
        c.rect(dx + 30, 125, 12, 3, P.WHITE)
    # the door on the left
    c.rect(52, 70, 26, 56, P.WOOD)
    c.pset(74, 98, P.GOLD)


async def school_enter(c: ScriptContext) -> None:
    if c.flag('school_in'):
        return
    c.set('school_in')
    await c.narrate('Класс. Парты, доска, запах мела. Трое учеников оборачиваются на дверь. Учительница поправляет очки.')


async def teacher_talk(c: ScriptContext) -> None:
    if not c.flag('teacher_met'):
        await c.say('teacher', '你好！我姓张，是这儿的老师，也是校长。欢迎你来我们的教室！')
        answer = await c.ask('teacher', '你是新同学吗？')
        if no(answer):
            answer = await c.ask('teacher', '不是？那你是谁？')
            if '俄' in normalize(answer):
                await c.say('teacher', '俄罗斯人！你会说汉语，真好！')
            else:
                await c.say('teacher', '欢迎欢迎！')
        else:
            await c.say('teacher', '哈哈，你是一个很大的同学！')
        await c.say('teacher', '我给大家介绍一下：这是我们的新朋友！')
        await c.say('teacher', '我们现在上课。你也可以听！')
        c.set('teacher_met')
        return
    if not c.flag('lesson1'):
        await c.say('teacher', '同学们好！')
        await c.say('xiaohong', '老师好！')
        await c.say('teacher', '请安静！请大家打开书。')
        await c.say('teacher', '今天星期二。我们学习四个字。')
        c.set('lesson1')
        await c.narrate('Учительница пишет на доске четыре знака и над каждым рисует маленькую картинку.')
        await c.say('teacher', '请大家看黑板。')
        await c.say('teacher', '请大家跟我读：山，水，火，木。')
        await c.say('xiaohong', '山，水，火，木！')
        await c.say('teacher', '很好！你们的声音很好听。现在我们练习写字。')
        if c.flag('xl_school'):
            await c.say('teacher', '小龙呢？他怎么还没来？')
            await c.say('xiaolong', '对不起，老师，我迟到了！')
            await c.say('teacher', '快坐下吧。')
        else:
            await c.say('teacher', '小龙呢？他怎么还没来？')
            await c.say('pangpang', '他在河边玩！')
        return
    if not c.flag('math_done'):
        await c.say('teacher', '现在是数学课。我有一个问题。谁能回答？')
        answer = await c.ask('teacher', '一个小时有多少分钟？')
        if _count(answer) == 60:
            await c.say('teacher', '对！六十分钟！你真聪明！')
        else:
            await c.say('teacher', '不对。小红，你说！')
            await c.say('xiaohong', '六十分钟！')
            await c.say('teacher', '对！')
        answer = await c.ask('teacher', '这个题很简单：一个星期有几天？')
        if _count(answer) == 7:
            await c.say('teacher', '很好！七天！')
        else:
            await c.say('pangpang', '七天！')
            await c.say('teacher', '对，一个星期有七天。')
        c.set('math_done')
        return
    if not c.flag('face_done'):
        await c.say('teacher', '我们来玩一个游戏！我说，你们指。')
        parts = ['头发', '眼睛', '耳朵', '鼻子', '嘴']
        lines = [f'这是{p}。' for p in parts] + [f'{p}在哪儿？' for p in parts]
        ok = await c.puzzle('face', parts=parts, lines=lines)
        if ok:
            c.set('face_done')
            await c.say('teacher', '你们都很聪明！')
        else:
            await c.say('teacher', '没关系，我们再玩一次！')
        return
    if not c.flag('exam_started'):
        c.set('exam_started')
        await c.say('teacher', '现在考试！准备好了吗？请大家拿出铅笔。')
        if c.flag('xl_school'):
            await c.say('xiaolong', '我的铅笔呢？我的铅笔没有了！')
            await c.narrate('Сяолун в панике шарит по карманам.')
        return
    if c.flag('pencil_given') and not c.flag('exam_done'):
        c.set('exam_done')
        await c.narrate('Ученики пишут. Тихо, только скрипят карандаши. Через десять минут учительница собирает листки.')
        await c.say('teacher', '小龙，你的成绩很好！一百分！')
        await c.say('xiaolong', '真的吗？！太好了！')
        await c.say('teacher', '今天的作业：写十次"山水火木"。')
        return
    if not c.flag('teacher_asked'):
        c.set('teacher_asked')
        answer = await c.ask('teacher', '你觉得我们学校怎么样？')
        await c.say('teacher', '谢谢你！欢迎你再来！' if not no(answer) else '哈哈，你说得对，我们的学校很小。')
        return
    await cycle(c, 'teacher_n', 'teacher', ['好好学习，天天向上！', '你的汉语越来越好了！', '你要去爬山吗？再见，一路平安！'])


async def xiaolong_talk(c: ScriptContext) -> None:
    if c.flag('exam_done') and not c.flag('drawing_given'):
        c.set('drawing_given')
        await c.say('xiaolong', '这是我画的大桥。这是给你的礼物！')
        c.give('drawing')
        await c.read('drawing')
        return
    if c.flag('exam_started') and not c.flag('pencil_given'):
        await c.say('xiaolong', '我的铅笔没有了……你看见了吗？')
        return
    await cycle(c, 'xl_n', 'xiaolong', ['你好！我来了！', '我不害怕了！', '我的爱好是画画。我也喜欢动物！'])


async def xiaolong_item(c: ScriptContext, item: str) -> bool:
    if item == 'pencil':
        c.take('pencil')
        c.set('pencil_given')
        await c.say('xiaolong', '我的铅笔！谢谢你！你是我的好朋友！')
        return True
    return False


async def xiaohong_talk(c: ScriptContext) -> None:
    if not c.flag('xh_color'):
        await c.say('xiaohong', '我叫小红。我弟弟在村子里，他五岁。我每天七点半去学校。')
        answer = await c.ask('xiaohong', '你喜欢什么颜色？')
        a = normalize(answer)
        if '红' in a:
            await c.say('xiaohong', '你也喜欢红色？我最喜欢红色！')
        else:
            await c.say('xiaohong', '我最喜欢红色，因为我叫小红！')
        c.set('xh_color')
        return
    await cycle(c, 'xh_n', 'xiaohong', ['考试不难，很容易！', '我每天早上六点起床。', '张老师很认真，我们都喜欢她。'])


async def pangpang_talk(c: ScriptContext) -> None:
    if not c.flag('pp_met'):
        await c.say('pangpang', '大家都叫我胖胖，因为我很胖。哈哈！')
        await c.say('pangpang', '我哥哥很瘦，他不喜欢吃饭。')
        await c.say('pangpang', '我们班有十二个同学，六个男同学。')
        answer = await c.ask('pangpang', '你喜欢运动吗？')
        if no(answer):
            await c.say('pangpang', '我也不喜欢！我最喜欢吃饭！')
        else:
            await c.say('pangpang', '我也喜欢！虽然我每天跑步，可是我还是很胖！')
        c.set('pp_met')
        return
    await cycle(c, 'pp_n', 'pangpang', ['中午我们在学校吃饭。', '考试？我不害怕！'])


async def blackboard(c: ScriptContext) -> None:
    if c.flag('lesson1'):
        await c.narrate('На доске — четыре знака и четыре рисунка мелом: горы, волны, язык пламени, деревце.')
    else:
        await c.narrate('Доска чистая. Сверху — дата.')


register(
    SceneDef(
        id='3c', chapter=3, title='Сельская школа', zh='学校',
        art=school_art, look=school_look,
        path=[(14, 172), (306, 172)],
        entries={'door': 64},
        actors=[
            ActorDef('teacher', 'Учительница Чжан', fig(P.PINK, P.WHITE, 'dress', 'bun', glasses=True), 176, 150, 'left', stand_at=168,
                     on_talk=teacher_talk),
            ActorDef('xiaohong', 'Сяохун', fig(P.VERMILION, P.WHITE, 'jacket', 'twinbuns', kind='child', pose='sit'), 60, 152, 'right',
                     stand_at=66, on_talk=xiaohong_talk, tags=('人', '孩子')),
            ActorDef('pangpang', 'Пухлый мальчик', fig(P.ORANGE, P.WHITE, 'jacket', 'short', kind='child', pose='sit'), 148, 152, 'left',
                     stand_at=140, on_talk=pangpang_talk, tags=('人', '孩子')),
            ActorDef('xiaolong', 'Сяолун', fig(P.WHITE, P.VERMILION, 'jacket', 'short', kind='child', pose='sit'), 248, 152, 'left',
                     visible=lambda s: s.on('xl_school'), stand_at=240, on_talk=xiaolong_talk, on_item=xiaolong_item, tags=('人', '孩子')),
        ],
        hotspots=[
            HotspotDef('blackboard', 'Доска', (86, 26, 148, 64), stand_at=160, on_click=blackboard),
        ],
        signs=[
            SignDef('slogan', '好好学习　天天向上', 98, 8, 'banner'),
            SignDef('date', '星期二', 184, 30, 'chalk'),
            SignDef('lesson', '山　水　火　木', LESSON_X - 3, 60, 'chalk', visible=lambda s: s.on('lesson1')),
        ],
        exits=[ExitDef('door', '3b', 'school', (52, 70, 26, 56), 'left', 64, 'Деревня')],
        on_enter=school_enter,
        music='village',
    )
)

# ---------------------------------------------------------------- 3d · the arch of Daizong


def arch_look(s) -> SceneLook:
    return SceneLook('golden')


def arch_art(s, look: SceneLook) -> None:
    c = kit.C
    kit.sky([(P.LIGHT_BLUE, 40), (P.MIST, 30), (P.WHITE, 40)])
    kit.ridge(98, 8, 30, 81, P.PERIWINKLE, rim=P.MIST, peaks=[(170, 74, 150)])
    kit.ridge(116, 8, 20, 82, P.MOSS)
    for x, h in ((20, 30), (40, 38), (276, 34), (300, 28)):
        kit.pine(x, 128, h, seed=x)
    kit.ground(126, P.PEACH, P.OCHRE, seed=83, density=0.03)
    # the stone path up through the arch
    kit.stairs(160, 168, 90, 160, 104, 26, P.GREY, P.STONE, steps=12)
    kit.paifang(114, 140, 92, 64, P.STONE, P.PLUM, P.INK, P.LACQUER)
    # the signpost
    c.rect(44, 116, 3, 38, P.WOOD)
    c.rect(96, 116, 3, 38, P.WOOD)
    # the ranger's hut
    c.rect(236, 106, 44, 34, P.PAPER)
    kit.roof(232, 106, 52, 8, P.INK)
    kit.window(244, 114, 12, 10)
    c.rect(262, 116, 12, 24, P.WOOD)
    kit.path_band([(0, 164), (160, 168), (320, 164)], 12, P.PAPER, P.OCHRE)


async def arch_enter(c: ScriptContext) -> None:
    if c.flag('arch_in'):
        return
    c.set('arch_in')
    await c.narrate('Каменная арка 岱宗坊. Отсюда начинается путь на гору: ступени уходят вверх, в сосны.')


async def wife_talk(c: ScriptContext) -> None:
    if c.flag('tourists_ok'):
        await cycle(c, 'wife_n', 'wife', ['我丈夫总是走错路！', '谢谢你！再见！'])
        return
    await c.say('wife', '我说往左边！')
    await c.say('husband', '不对，往右边！牌子上的字是什么意思？')
    answer = await c.ask('wife', '请问，去红门往哪儿走？')
    a = normalize(answer)
    if '前' in a:
        await c.say('wife', '往前走？谢谢你！你的汉语真好！')
        await c.say('wife', '你看，我丈夫总是走错路。')
        await c.say('husband', '好吧……我妻子说得对。')
        c.set('tourists_ok')
    elif '左' in a or '右' in a:
        await c.say('husband', '是吗？牌子上不是这样写的……')
    else:
        await c.say('wife', '你看看那个牌子，好吗？')


async def husband_talk(c: ScriptContext) -> None:
    if c.flag('tourists_ok'):
        await c.say('husband', '一起走吧！')
        return
    await c.say('husband', '我们第一次来泰山，不知道往哪儿走。')


async def ranger_talk(c: ScriptContext) -> None:
    if c.flag('ranger_ok'):
        await cycle(c, 'ranger_n', 'ranger', ['上山的路很长，你要多休息。', '一路平安！'])
        return
    answer = await c.ask('ranger', '你要上山吗？')
    if no(answer):
        await c.say('ranger', '不上山？那你看看就回去吧。')
        return
    await c.say('ranger', '上山的路很长，要很长时间。现在已经下午了。')
    await c.say('ranger', '红门就在前面，离这儿不远。')
    await c.say('ranger', '晚上可能下雨，山上很黑，也很冷。')
    if c.has('lamp'):
        await c.say('ranger', '你有灯？好！一路平安！')
        c.set('ranger_ok')
    else:
        await c.say('ranger', '你没有灯？晚上不能上山！')


async def arch_up(c: ScriptContext) -> bool:
    if c.flag('ranger_ok'):
        await c.narrate('Прохожу под аркой. Ступени, сосны, ветер с горы. Впереди — Красные ворота.')
        return True
    await c.say('ranger', '等一下！')
    return False


register(
    SceneDef(
        id='3d', chapter=3, title='Арка Дайцзун', zh='岱宗坊',
        art=arch_art, look=arch_look,
        path=[(8, 164), (160, 168), (312, 164)],
        entries={'village': 20},
        actors=[
            ActorDef('wife', 'Туристка', fig(P.VERMILION, P.WHITE, 'jacket', 'ponytail', prop='bag'), 62, 160, 'right', on_talk=wife_talk),
            ActorDef('husband', 'Её муж', fig(P.NAVY, P.GREY, 'jacket', 'cap', prop='staff'), 84, 160, 'left', on_talk=husband_talk),
            ActorDef('ranger', 'Смотритель тропы', fig(P.PINE, P.GOLD, 'uniform', 'cap'), 250, 156, 'left', on_talk=ranger_talk),
        ],
        signs=[
            SignDef('plaque', '岱宗坊', 141, 78, 'plaque'),
            SignDef('post', '红门　往前走\n天外村　往右走\n泰安站　往左走', 30, 72, 'board'),
        ],
        exits=[
            ExitDef('village', '3b', 'road', (0, 100, 10, 70), 'left', 12, 'Деревня'),
            ExitDef('up', '4a', 'bottom', (140, 96, 40, 44), 'up', 160, 'Под арку', guard=arch_up),
        ],
        on_enter=arch_enter,
        diary=('diary_5',),
        music='mountain',
    )
)

# ---------------------------------------------------------------- pages, pictures, glossary, hints

pages.add(
    # the main path
    PageDef('elements', 'Стихии', 3, ('山', '水', '火', '木')),
    PageDef('bridge3', 'Мост', 3, ('桥', '船', '河', '鱼', '桶')),
    PageDef('family3', 'Семья', 3, ('妈妈', '儿子', '奶奶', '孩子', '丈夫', '邻居')),
    PageDef('siblings', 'Братья и сёстры', 3, ('哥哥', '姐姐', '弟弟', '妹妹')),
    PageDef('school3', 'Школа', 3, ('学校', '老师', '同学', '黑板', '铅笔')),
    PageDef('face', 'Лицо', 3, ('头发', '眼睛', '耳朵', '鼻子', '嘴')),
    PageDef('time3', 'Время', 3, ('小时', '分钟', '星期', '一百')),
    PageDef('dirs', 'Куда идти', 3, ('往前走', '往左走', '往右走', '上山')),
    PageDef('fire3', 'Огонь', 3, ('柴', '灯', '火柴', '打水'), kind='icon'),
    PageDef('fisher', 'Рыбак', 3, ('条', '数', '以前', '比', '有名'), kind='phrase',
            phrases=('七条鱼！', '你帮我数一下', '以前这儿没有桥', '它比我还老！', '这个桥很有名。')),
    PageDef('fisher2', 'Мост деда', 3, ('坐船', '过河', '那时候', '年轻人', '事情'), kind='phrase',
            phrases=('大家都坐船过河。', '大家都坐船过河。', '那时候有一个苏联年轻人', '那时候有一个苏联年轻人', '她知道很多以前的事情。')),
    PageDef('xiaolong', 'Сяолун', 3, ('考试', '复习', '害怕', '觉得', '年级'), kind='phrase',
            phrases=('今天有考试。', '我没有复习，我很害怕。', '我没有复习，我很害怕。', '你觉得我能考好吗？', '我八岁，上二年级。')),
    PageDef('aunt', 'Соседка', 3, ('坏', '才', '累', '腿', '帮'), kind='phrase',
            phrases=('井坏了！', '明天才回来。', '太累了！', '她的腿不好', '你能帮她打水吗？')),
    PageDef('grandma1', 'Бабушка Ван', 3, ('从', '像', '跟', '一样', '的时候'), kind='phrase',
            phrases=('你从哪儿来？', '你长得很像一个人……', '你笑的时候跟他一样！', '你笑的时候跟他一样！', '你笑的时候跟他一样！')),
    PageDef('grandma2', 'Рассказ бабушки', 3, ('把', '送', '一定', '一直', '后来', '搬'), kind='phrase',
            phrases=('李明把这笔送给了他。', '李明把这笔送给了他。', '你一定要回来！', '可是小安一直没有回来……', '后来，李家搬到山上去了。',
                     '后来，李家搬到山上去了。')),
    PageDef('grandma3', 'Как они учились', 3, ('教', '俄语', '写字', '认真', '先生'), kind='phrase',
            phrases=('小安教他说俄语。', '小安教他说俄语。', '他们两个人在河边写字。', '小安写得很认真。', '李明的爸爸是写字的先生。')),
    PageDef('class3', 'Урок', 3, ('学习', '读', '上课', '聪明', '游戏'), kind='phrase',
            phrases=('我们学习四个字。', '请大家跟我读', '我们现在上课。', '你真聪明！', '我们来玩一个游戏！')),
    PageDef('kids3', 'Одноклассники', 3, ('颜色', '最', '胖', '瘦', '运动', '跑步'), kind='phrase',
            phrases=('你喜欢什么颜色？', '我最喜欢红色', '因为我很胖', '我哥哥很瘦', '你喜欢运动吗？', '我每天跑步')),
    PageDef('why', 'Почему', 3, ('因为', '可是', '还是', '怎么'), kind='phrase',
            phrases=('因为我叫小红！', '可是我还是很胖！', '可是我还是很胖！', '他怎么还没来？')),
    PageDef('exam', 'Экзамен', 3, ('迟到', '坐下', '拿出', '一百分', '画'), kind='phrase',
            phrases=('我迟到了！', '快坐下吧。', '请大家拿出铅笔。', '一百分！', '这是我画的大桥。')),
    PageDef('tourists', 'Туристы', 3, ('妻子', '总是', '走错', '第一次'), kind='phrase',
            phrases=('我妻子说得对。', '我丈夫总是走错路！', '我丈夫总是走错路！', '我们第一次来泰山')),
    PageDef('ranger', 'Смотритель', 3, ('路', '黑', '一路平安', '玩'), kind='phrase',
            phrases=('上山的路很长。', '晚上山上很黑', '一路平安！', '儿子，别玩水！')),
    PageDef('son', 'Малыш', 3, ('别', '或者', '只', '鸟', '明年'), kind='phrase',
            phrases=('别玩水！', '一个弟弟或者妹妹！', '树上有一只鸟！', '树上有一只鸟！', '明年上学。')),
    PageDef('teacher2', 'Учительница Чжан', 3, ('姓', '校长', '教室', '介绍', '安静'), kind='phrase',
            phrases=('我姓张', '是这儿的老师，也是校长。', '欢迎你来我们的教室！', '我给大家介绍一下', '请安静！')),
    PageDef('lesson2', 'На уроке', 3, ('书', '声音', '练习', '问题', '回答', '简单'), kind='phrase',
            phrases=('请大家打开书。', '你们的声音很好听。', '现在我们练习写字。', '我有一个问题。', '谁能回答？', '这个题很简单')),
    PageDef('exam2', 'После экзамена', 3, ('准备', '成绩', '作业', '礼物', '爱好', '动物'), kind='phrase',
            phrases=('准备好了吗？', '你的成绩很好！', '今天的作业', '这是给你的礼物！', '我的爱好是画画。', '我也喜欢动物！')),
    PageDef('aunt2', 'Тётя Лю', 3, ('阿姨', '所以', '经常', '照顾', '附近', '帮助'), kind='phrase',
            phrases=('大家都叫我刘阿姨。', '井坏了，所以我们都没有水。', '我经常照顾她。', '我经常照顾她。', '附近也没有商店。', '谢谢你的帮助！')),
    PageDef('grandma4', 'Бабушка Ван провожает', 3, ('让', '脸', '去年', '放心', '慢', '着急'), kind='phrase',
            phrases=('让我看看你……', '你的脸……', '去年李明还回村子看我们。', '放心吧', '慢一点儿走', '别着急！')),
    PageDef('ranger2', 'Перед подъёмом', 3, ('时间', '已经', '前面', '离', '可能', '下雨'), kind='phrase',
            phrases=('要很长时间。', '现在已经下午了。', '红门就在前面', '离这儿不远。', '晚上可能下雨', '晚上可能下雨')),
    PageDef('bridge4', 'Сяолун и его дядя', 3, ('草', '叔叔', '昨天', '担心', '历史', '告诉'), kind='phrase',
            phrases=('白白喜欢在草上跑。', '船上的人是我叔叔', '昨天我只有三条。', '我很担心，也很害怕。', '这个桥很有历史。', '我奶奶告诉我')),
    PageDef('tourists2', 'Лево и право', 3, ('左边', '右边', '意思', '不客气'), kind='phrase',
            phrases=('我说往左边！', '不对，往右边！', '牌子上的字是什么意思？', '不客气！')),
    PageDef('class4', 'Наш класс', 3, ('班', '男', '虽然', '半', '正在', '着'), kind='phrase',
            phrases=('我们班有十二个同学', '六个男同学。', '虽然我每天跑步', '我每天七点半去学校。', '王奶奶正在门口坐着呢。', '王奶奶正在门口坐着呢。')),
    PageDef('diary3', 'Запись деда', 3, ('开始', '努力', '起床', '爱笑', '工人'), kind='phrase',
            phrases=('今天我们开始修桥。', '工作非常努力', '每天早上五点起床。', '他很爱笑。', '中国工人工作非常努力')),
    PageDef('diary4', 'Почему ты приехал', 3, ('为什么', '希望', '以后', '非常', '漂亮'), kind='phrase',
            phrases=('你为什么来中国？', '我希望以后也能修桥。', '我希望以后也能修桥。', '他的字非常漂亮', '他的字非常漂亮')),
    PageDef('diary5', 'Праздник Весны', 3, ('春节', '唱歌', '好听', '第一', '请'), kind='phrase',
            phrases=('今天是春节。', '王家的小女儿给我们唱歌', '她唱得非常好听。', '我第一次觉得', '村子里的人请我们吃饭。')),
)

for w, ic in (('桥', 'bridge'), ('船', 'boat'), ('鱼', 'fish'), ('桶', 'bucket'), ('柴', 'wood'), ('灯', 'oil_lamp'),
              ('火柴', 'fire'), ('打水', 'bucket_water'), ('铅笔', 'pencil'), ('黑板', 'blackboard'), ('学校', 'house'),
              ('木', 'tree'), ('火', 'fire')):
    icon_for(w, ic)


@picture('河')
def _(x: int, y: int) -> None:
    pyxel.rect(x, y + 12, 32, 10, P.TEAL)
    for i in range(4):
        pyxel.line(x + 2 + i * 8, y + 16, x + 6 + i * 8, y + 16, P.MINT)
    pyxel.rect(x, y + 22, 32, 10, P.MOSS)
    pyxel.rect(x, y + 4, 32, 8, P.MOSS)


@picture('山')
def _(x: int, y: int) -> None:
    pyxel.tri(x + 2, y + 28, x + 12, y + 8, x + 22, y + 28, P.PERIWINKLE)
    pyxel.tri(x + 12, y + 28, x + 22, y + 4, x + 31, y + 28, P.PLUM)
    pyxel.tri(x + 19, y + 10, x + 22, y + 4, x + 25, y + 10, P.WHITE)


@picture('水')
def _(x: int, y: int) -> None:
    for i in range(3):
        for k in range(8):
            yy = y + 8 + i * 8 + (1 if k % 2 else 0)
            pyxel.line(x + 2 + k * 4, yy, x + 5 + k * 4, yy + (-1 if k % 2 else 1), P.TEAL)


def _person(x: int, y: int, col: int, h: int, hair: int = P.INK, skirt: bool = False) -> None:
    pyxel.circ(x, y - h + 3, 3, P.PEACH)
    pyxel.rect(x - 3, y - h, 7, 2, hair)
    pyxel.rect(x - 3, y - h + 7, 7, h - 11, col)
    if skirt:
        pyxel.tri(x - 5, y - 4, x + 5, y - 4, x, y - h + 9, col)
    pyxel.line(x - 2, y - 4, x - 2, y, P.INK)
    pyxel.line(x + 2, y - 4, x + 2, y, P.INK)


def _mark(x: int, y: int) -> None:
    picto.arrow(x, y - 8, x, y - 2, P.VERMILION)


@picture('妈妈')
def _(x: int, y: int) -> None:
    _person(x + 12, y + 30, P.PINK, 24, skirt=True)
    _person(x + 24, y + 30, P.YELLOW, 13)
    _mark(x + 12, y + 6)


@picture('儿子')
def _(x: int, y: int) -> None:
    _person(x + 10, y + 30, P.PINK, 24, skirt=True)
    _person(x + 22, y + 30, P.DARK_BLUE, 14)
    _mark(x + 22, y + 16)


@picture('奶奶')
def _(x: int, y: int) -> None:
    _person(x + 16, y + 30, P.DARK_BLUE, 22, hair=P.WHITE, skirt=True)
    pyxel.line(x + 22, y + 16, x + 24, y + 30, P.WOOD)


@picture('孩子')
def _(x: int, y: int) -> None:
    _person(x + 8, y + 30, P.YELLOW, 14)
    _person(x + 18, y + 30, P.VERMILION, 12, skirt=True)
    _person(x + 27, y + 30, P.JADE, 15)


@picture('丈夫')
def _(x: int, y: int) -> None:
    _person(x + 10, y + 30, P.PINK, 23, skirt=True)
    _person(x + 22, y + 30, P.NAVY, 26)
    pyxel.circ(x + 16, y + 10, 2, P.VERMILION)
    _mark(x + 22, y + 6)


@picture('邻居')
def _(x: int, y: int) -> None:
    picto.icon('house', x, y + 12)
    picto.icon('house', x + 16, y + 12)
    picto.arrow(x + 10, y + 8, x + 22, y + 8, P.VERMILION)


def _siblings(mark: int) -> None:
    def draw(x: int, y: int) -> None:
        specs = [(P.NAVY, 26, False), (P.PINK, 24, True), (P.DARK_BLUE, 16, False), (P.VERMILION, 14, True)]
        for i, (col, h, skirt) in enumerate(specs):
            _person(x + 4 + i * 8, y + 31, col, h, skirt=skirt)
        _mark(x + 4 + mark * 8, y + 31 - specs[mark][1] - 1)
    return draw


picture('哥哥')(_siblings(0))
picture('姐姐')(_siblings(1))
picture('弟弟')(_siblings(2))
picture('妹妹')(_siblings(3))


@picture('老师')
def _(x: int, y: int) -> None:
    pyxel.rect(x + 2, y + 4, 22, 14, P.PINE)
    pyxel.rectb(x + 2, y + 4, 22, 14, P.WOOD)
    pyxel.line(x + 6, y + 9, x + 16, y + 9, P.WHITE)
    _person(x + 26, y + 31, P.PINK, 22, skirt=True)


@picture('同学')
def _(x: int, y: int) -> None:
    for i in range(3):
        _person(x + 6 + i * 10, y + 30, (P.VERMILION, P.ORANGE, P.WHITE)[i], 14)
    pyxel.rect(x + 1, y + 26, 30, 3, P.WOOD)


def _face_part(part: str) -> None:
    def draw(x: int, y: int) -> None:
        cx, cy = x + 16, y + 17
        pyxel.circ(cx, cy, 11, P.PEACH)
        pyxel.circ(cx - 11, cy, 3, P.PEACH)
        pyxel.circ(cx + 11, cy, 3, P.PEACH)
        pyxel.rect(cx - 10, cy - 12, 21, 5, P.INK)
        pyxel.pset(cx - 4, cy - 2, P.INK)
        pyxel.pset(cx + 4, cy - 2, P.INK)
        pyxel.line(cx, cy, cx - 1, cy + 3, P.OCHRE)
        pyxel.line(cx - 3, cy + 6, cx + 3, cy + 6, P.RED)
        spots = {'头发': (cx, cy - 10, 13, 5), '眼睛': (cx, cy - 2, 12, 5), '耳朵': (cx + 11, cy, 5, 7),
                 '鼻子': (cx, cy + 2, 5, 6), '嘴': (cx, cy + 6, 9, 4)}
        sx, sy, sw, sh = spots[part]
        pyxel.rectb(sx - sw // 2 - 1, sy - sh // 2 - 1, sw + 2, sh + 2, P.VERMILION)
    return draw


for _p in ('头发', '眼睛', '耳朵', '鼻子', '嘴'):
    picture(_p)(_face_part(_p))


@picture('小时')
def _(x: int, y: int) -> None:
    picto.clock(x + 16, y + 16, 13, 3, 0, 'hour')


@picture('分钟')
def _(x: int, y: int) -> None:
    picto.clock(x + 16, y + 16, 13, 3, 10, 'minute')


@picture('星期')
def _(x: int, y: int) -> None:
    for i in range(7):
        pyxel.rect(x + 1 + i * 4, y + 10, 3, 12, P.VERMILION if i >= 5 else P.WHITE)
        pyxel.rectb(x + 1 + i * 4, y + 10, 3, 12, P.INK)
    pyxel.rect(x + 1, y + 6, 28, 3, P.VERMILION)


@picture('一百')
def _(x: int, y: int) -> None:
    pyxel.rect(x + 4, y + 4, 24, 26, P.WHITE)
    pyxel.rectb(x + 4, y + 4, 24, 26, P.STONE)
    pyxel.text(x + 9, y + 12, '100', P.VERMILION)
    pyxel.circb(x + 16, y + 14, 9, P.VERMILION)


def _dir(dx: int, dy: int) -> None:
    def draw(x: int, y: int) -> None:
        picto.person(x + 16, y + 30, P.DARK_BLUE)
        picto.arrow(x + 16, y + 12, x + 16 + dx, y + 12 + dy, P.VERMILION)
    return draw


picture('往前走')(_dir(0, -10))
picture('往左走')(_dir(-12, 0))
picture('往右走')(_dir(12, 0))


@picture('上山')
def _(x: int, y: int) -> None:
    pyxel.tri(x + 2, y + 30, x + 18, y + 4, x + 31, y + 30, P.PERIWINKLE)
    picto.person(x + 10, y + 30, P.DARK_BLUE)
    picto.arrow(x + 12, y + 18, x + 20, y + 8, P.VERMILION)


@sketch('bridge_1958')
def _(x: int, y: int) -> None:
    pyxel.line(x + 2, y + 30, x + 78, y + 30, P.STONE)
    for i in range(4):
        pyxel.line(x + 8 + i * 20, y + 16, x + 8 + i * 20, y + 34, P.INK)
    pyxel.line(x + 2, y + 16, x + 78, y + 16, P.INK)
    for i in range(3):
        pyxel.line(x + 38 + i * 6, y + 16, x + 36 + i * 6, y + 6, P.INK)
    pyxel.line(x + 34, y + 6, x + 56, y + 6, P.INK)
    for k in range(6):
        pyxel.line(x + 4 + k * 13, y + 38, x + 9 + k * 13, y + 38, P.STONE)
    picto.person(x + 64, y + 30, P.INK)


@sketch('river_writing')
def _(x: int, y: int) -> None:
    pyxel.line(x + 2, y + 34, x + 78, y + 34, P.STONE)
    for k in range(6):
        pyxel.line(x + 4 + k * 13, y + 38, x + 9 + k * 13, y + 38, P.STONE)
    picto.person(x + 22, y + 32, P.INK)
    picto.person(x + 36, y + 32, P.INK)
    pyxel.line(x + 50, y + 28, x + 50, y + 22, P.INK)
    pyxel.line(x + 46, y + 25, x + 54, y + 25, P.INK)
    pyxel.line(x + 58, y + 28, x + 62, y + 22, P.INK)
    pyxel.line(x + 62, y + 22, x + 66, y + 28, P.INK)
    pyxel.circb(x + 66, y + 8, 5, P.INK)


@sketch('spring_festival')
def _(x: int, y: int) -> None:
    for i, lx in enumerate((14, 40, 66)):
        pyxel.line(x + lx, y + 2, x + lx, y + 6, P.INK)
        pyxel.elli(x + lx - 5, y + 6, 11, 9, P.VERMILION)
    pyxel.rect(x + 8, y + 24, 64, 4, P.INK)
    for i in range(5):
        picto.person(x + 12 + i * 14, y + 42, P.INK)


words.add('''
大汶河 — река Давэньхэ
大桥 — большой мост
苏联 — Советский Союз
友好 — дружба, дружественный
坐船 — плыть на лодке
过河 — переправиться через реку
那时候 — в то время
年轻人 — молодой человек
事情 — дело, событие
以前 — раньше
有名 — знаменитый
村子 — деревня
一路平安 — счастливого пути
考试 — экзамен
复习 — повторять (уроки)
害怕 — бояться
觉得 — считать, чувствовать
年级 — класс (в школе)
学校 — школа
老师 — учитель
同学 — одноклассник
黑板 — доска
铅笔 — карандаш
妈妈 — мама
儿子 — сын
奶奶 — бабушка
孩子 — ребёнок
丈夫 — муж
妻子 — жена
邻居 — сосед
哥哥 — старший брат
姐姐 — старшая сестра
弟弟 — младший брат
妹妹 — младшая сестра
头发 — волосы
眼睛 — глаза
耳朵 — уши
鼻子 — нос
小时 — час
分钟 — минута
星期 — неделя
星期二 — вторник
一百 — сто
往前走 — идти вперёд
往左走 — идти налево
往右走 — идти направо
上山 — подниматься в гору
火柴 — спички
打水 — набирать воду
一样 — одинаковый
的时候 — когда
一定 — обязательно
一直 — всё время, всё ещё
后来 — потом, позже
俄语 — русский язык
写字 — писать иероглифы
认真 — старательный, всерьёз
先生 — господин; учитель (старое)
学习 — учиться
上课 — идти на урок, заниматься
聪明 — умный
游戏 — игра
颜色 — цвет
运动 — спорт, двигаться
跑步 — бегать
因为 — потому что
可是 — но
还是 — всё-таки; или
怎么 — как, почему
迟到 — опоздать
坐下 — сесть
拿出 — достать
一百分 — сто баллов
总是 — всегда
走错 — пойти не туда
第一次 — в первый раз
或者 — или
明年 — в следующем году
开始 — начинать
努力 — старательно
起床 — вставать с постели
爱笑 — смешливый
工人 — рабочий
为什么 — почему
希望 — надеяться
以后 — потом, в будущем
非常 — очень
漂亮 — красивый
春节 — Праздник Весны
唱歌 — петь
好听 — приятный на слух
第一 — первый
老照片 — старая фотография
好好学习，天天向上 — хорошо учись, каждый день расти
校长 — директор школы
教室 — класс (комната)
介绍 — представлять, знакомить
安静 — тихий
声音 — голос, звук
练习 — упражняться
问题 — вопрос
回答 — отвечать
简单 — простой
准备 — готовиться
成绩 — оценки, успехи
作业 — домашнее задание
礼物 — подарок
爱好 — увлечение
动物 — животное
阿姨 — тётя
所以 — поэтому
经常 — часто
照顾 — заботиться
附近 — поблизости
帮助 — помощь
去年 — в прошлом году
放心 — не беспокоиться
着急 — волноваться, спешить
时间 — время
已经 — уже
前面 — впереди
可能 — возможно
下雨 — идёт дождь
叔叔 — дядя
昨天 — вчера
担心 — беспокоиться
历史 — история
告诉 — сказать, сообщить
左边 — слева
右边 — справа
意思 — смысл
不客气 — не за что
虽然 — хотя
正在 — как раз (сейчас)
太阳 — солнце
节日 — праздник
热情 — радушный
一点儿 — немного
后面 — сзади
怎么样 — как?
''')

hints.add(lambda s: s.scene == '3a' and not s.on('fisher_story'),
          'Рыбак в лодке у берега. Поговорите с ним — он знает историю моста.')
hints.add(lambda s: s.scene == '3a' and s.on('fisher_story') and not s.on('fish_counted') and not s.has('water'),
          'Рыбак просит посчитать его улов. Рыбы лежат на доске у берега. Ответ — число и счётное слово 条.')
hints.add(lambda s: s.has('bucket'),
          'Пустое ведро. Выберите его в сумке и нажмите на реку.')
hints.add(lambda s: s.scene == '3a' and s.on('xl_met') and not s.on('xl_school'),
          'Мальчик боится экзамена и спрашивает: «你觉得我能考好吗？» — «Думаешь, я смогу?» Подбодрите его: ответьте тем же глаголом.')
hints.add(lambda s: s.has('water') and not s.on('gw_water'),
          'Вода нужна бабушке Ван — она сидит у своего дома за большим деревом. Отдайте ей ведро.')
hints.add(lambda s: s.on('gw_water') and not s.on('got_firewood'),
          'У бабушки нет дров. У соседки у колодца дрова сложены у стены — поговорите с ней.')
hints.add(lambda s: s.has('firewood'),
          'Отдайте дрова (柴) бабушке Ван.')
hints.add(lambda s: s.on('need_fire') and not s.confirmed.get('火'),
          'Огня нет. Кисть деда тёплая — но писать можно только знаки, которые понимаешь. Сельская школа рядом: может, там учат знакам? Потом разложите страницу «Стихии».')
hints.add(lambda s: s.on('need_fire') and not s.on('brush_awake'),
          'Вы понимаете знак огня. Выберите кисть (笔) в сумке и нажмите на печку.')
hints.add(lambda s: s.on('brush_awake') and not s.on('stove_fire'),
          'Нажмите «笔» (B), напишите 火 и укажите на печку.')
hints.add(lambda s: s.scene == '3c' and not s.on('face_done'),
          'Поговорите с учительницей ещё раз: урок продолжается.')
hints.add(lambda s: s.has('pencil') and s.on('exam_started'),
          'Сяолун потерял карандаш — а у вас в сумке жёлтый карандаш с берега.')
hints.add(lambda s: s.scene == '3d' and not s.on('tourists_ok'),
          'Туристы спрашивают дорогу к 红门. Найдите на указателе строку с 红门 и повторите, что там написано.')
hints.add(lambda s: s.scene == '3d' and not s.on('ranger_ok'),
          'Смотритель спросит, идёте ли вы в гору. «Да» — повторите глагол: 上山 или 要.')
hints.add(lambda s: s.chapter == 3 and s.on('tea_done') and s.scene != '3d',
          'Дорога в гору — за школой, направо. Там арка 岱宗坊.')

"""Chapter 2 · 泰安 «Тайань» — the station square, the hotel, a street, the Dai Temple."""
from __future__ import annotations

import pyxel

from ...art import kit, picto
from ...art import palette as P
from ...art.pictures import icon_for, picture
from ...art.sketches import sketch
from ...core.numerals import to_hanzi
from ...core.phrases import normalize
from ...core.types import ActorDef, ExitDef, HotspotDef, ItemDef, PageDef, SceneDef, SceneLook, ScriptContext, SignDef, TextDef
from .. import hints, items, pages, texts, words
from ..world import register
from ._common import STAFF, cycle, fig, no, pay, yes

# ---------------------------------------------------------------- items and texts

items.add(
    ItemDef('card', '信用卡', 'card', 'Банковская карта. Дома ею можно платить где угодно.'),
    ItemDef('keycard', '房卡', 'keycard', 'Пластиковая карточка с номером 308.'),
    ItemDef('umbrella', '雨伞', 'umbrella', 'Складной зонт. По прогнозу он скоро понадобится.'),
    ItemDef('map', '地图', 'map', 'Карта города. Вокзал, гостиница, храм — и гора.'),
    ItemDef('watermelon', '西瓜', 'watermelon', 'Целый полосатый шар. Тяжёлый.'),
    ItemDef('banana', '香蕉', 'banana', 'Связка спелых бананов.'),
    ItemDef('cake', '蛋糕', 'cake', 'Кусок праздничного торта.'),
    ItemDef('drink', '饮料', 'bottle', 'Бутылка сладкого чая из холодильника.'),
)

texts.add(
    TextDef(
        'diary_2', 'diary', 'Дневник деда · 2',
        '今天我们到泰安了。泰安是一个小城市。\n我住在一个宾馆里。房间很小，但是很干净。\n我看见了泰山。泰山很高！',
        '«Сегодня мы приехали в Тайань. Тайань — маленький город. Я живу в гостинице. Комната маленькая, но очень чистая. Я увидел гору Тайшань. Она очень высокая!»',
        chapter=2, date='一九五八年九月二十一号', sketch='taian_1958',
    ),
    TextDef(
        'forecast', 'sign', 'Прогноз погоды',
        '天气\n今天：晴\n明天：晴\n明天晚上：山上有雨',
        'Погода. Сегодня ясно, завтра ясно, завтра вечером в горах — дождь.',
        chapter=2,
    ),
)

# ---------------------------------------------------------------- 2a · station square

FRUIT = {'西瓜': ('watermelon', 15), '香蕉': ('banana', 5), '苹果': ('apple', 3)}


def square_art(s, look: SceneLook) -> None:
    c = kit.C
    kit.sky([(P.LIGHT_BLUE, 30), (P.MIST, 26), (P.WHITE, 20)])
    kit.ridge(78, 10, 40, 21, P.PERIWINKLE, peaks=[(210, 46, 90)])
    kit.mist(66, 12, P.MIST, 0.5)
    for i, (bx, bw, bh) in enumerate(((0, 40, 36), (44, 30, 48), (238, 36, 52), (278, 42, 40))):
        kit.building(bx, 104, bw, bh, P.GREY if i % 2 else P.MIST, P.DARK_BLUE, seed=bx + 3)
    # the station: a long hall with a roof
    c.rect(78, 70, 156, 42, P.PAPER)
    kit.roof(72, 70, 168, 10, P.INK, P.STONE)
    for wx in range(86, 228, 16):
        kit.window(wx, 84, 10, 14)
    c.rect(146, 94, 20, 18, P.DARK_BLUE)
    kit.ground(112, P.GREY, P.STONE, seed=31, density=0.02)
    for y in range(116, 180, 8):
        c.line(0, y, 320, y, P.MIST)
    # taxi
    c.rect(34, 138, 46, 14, P.YELLOW)
    c.rect(42, 130, 28, 9, P.YELLOW)
    c.rect(45, 132, 10, 6, P.LIGHT_BLUE)
    c.rect(58, 132, 10, 6, P.LIGHT_BLUE)
    c.rect(52, 126, 8, 4, P.VERMILION)
    for wx in (42, 70):
        c.circ(wx, 152, 4, P.INK)
        c.circ(wx, 152, 1, P.GREY)
    # fruit stall
    c.rect(214, 132, 52, 16, P.OCHRE)
    c.rect(210, 112, 60, 5, P.VERMILION)
    c.line(214, 117, 214, 132, P.WOOD)
    c.line(266, 117, 266, 132, P.WOOD)
    for i in range(4):
        c.circ(222 + i * 7, 129, 3, P.JADE)
        c.line(220 + i * 7, 129, 224 + i * 7, 129, P.PINE)
    c.rect(248, 124, 12, 6, P.YELLOW)
    for i in range(3):
        c.circ(252 + i * 4, 122, 2, P.VERMILION)
    # map seller's board
    c.rect(116, 124, 20, 22, P.PAPER)
    c.rectb(116, 124, 20, 22, P.WOOD)
    c.line(119, 130, 132, 138, P.JADE)
    c.line(120, 140, 130, 128, P.VERMILION)
    c.line(126, 146, 126, 152, P.WOOD)
    kit.cypress(10, 156, 28)
    kit.cypress(306, 158, 26)


async def square_enter(c: ScriptContext) -> None:
    if c.flag('ch2'):
        return
    c.set('ch2')
    await c.chapter(2)
    c.give('card')
    await c.narrate('Тайань. Вокзальная площадь, такси, торговцы. А над крышами — гора. Та самая, с фотографии.')


async def driver_talk(c: ScriptContext) -> None:
    if c.flag('taxi_paid'):
        await c.say('driver', '上车吧！')
        return
    if c.flag('taxi_ready'):
        await c.say('driver', '宾馆很近，十五块。')
        return
    answer = await c.ask('driver', '你好！坐出租车吗？')
    if no(answer):
        await c.say('driver', '不坐？好吧。')
        return
    answer = await c.ask('driver', '你去哪儿？')
    a = normalize(answer)
    if not ('泰' in a or '中天门' in a or '山' in a):
        await c.say('driver', '你去哪儿？火车站？宾馆？泰山？')
        return
    await taxi_explains(c)


async def taxi_explains(c: ScriptContext) -> None:
    await c.say('driver', '我是出租车司机，泰安我都知道。')
    await c.say('driver', '中天门？中天门在山上。太远了！')
    await c.say('driver', '现在是下午四点。今天太晚了，明天去吧！')
    await c.ask('driver', '你今天住哪儿？')
    await c.say('driver', '我知道一个宾馆，很近，也不贵。')
    await c.say('driver', '上车吧！十五块。')
    c.set('taxi_ready')


async def driver_item(c: ScriptContext, item: str) -> bool:
    if item == 'letter' and not c.flag('taxi_ready'):
        await c.narrate('Водитель щурится на конверт и медленно читает адрес.')
        await c.say('driver', '泰山，中天门，李家茶馆……')
        await taxi_explains(c)
        return True
    if item == 'money' and c.flag('taxi_ready') and not c.flag('taxi_paid'):
        if await pay(c, 'driver', 15, item):
            await c.say('driver', '好！走吧！')
            c.set('taxi_paid')
        return True
    if item == 'card':
        await c.say('driver', '卡？不行。给我钱吧。')
        return True
    return False


async def fruit_talk(c: ScriptContext) -> None:
    pending = c.flag('fruit_order')
    if pending:
        await c.say('fruit', f'{pending}，{to_hanzi(FRUIT[pending][1])}块。')
        return
    answer = await c.ask('fruit', '你好！买水果吗？西瓜、香蕉、苹果，都很新鲜！')
    a = normalize(answer)
    for name in FRUIT:
        if name in a:
            c.set('fruit_order', name)
            await c.say('fruit', f'{name}？{to_hanzi(FRUIT[name][1])}块。')
            return
    if no(answer):
        await c.say('fruit', '不买？没关系！')


async def fruit_item(c: ScriptContext, item: str) -> bool:
    pending = c.flag('fruit_order')
    if item == 'money' and pending:
        it, price = FRUIT[pending]
        if await pay(c, 'fruit', price, item):
            await c.say('fruit', '谢谢！')
            c.give(it)
            c.set('fruit_order', '')
        return True
    return False


async def mapman_talk(c: ScriptContext) -> None:
    if c.has('map'):
        await c.say('mapman', '有地图，你就不会走错了！')
        return
    await c.say('mapman', '地图！地图！十块一张！')


async def mapman_item(c: ScriptContext, item: str) -> bool:
    if item == 'money' and not c.has('map'):
        if await pay(c, 'mapman', 10, item):
            await c.say('mapman', '谢谢！这是泰安的地图。')
            c.give('map')
            await c.narrate('На карте подписаны вокзал, гостиница, улица с лавками, храм Дай — и гора на севере.')
        return True
    return False


async def square_exit(c: ScriptContext) -> bool:
    if not c.flag('taxi_paid'):
        await c.say('driver', '坐出租车吗？')
        return False
    await c.narrate('Такси петляет по улицам. Водитель что-то рассказывает, я киваю.')
    await c.say('driver', '到了！这是宾馆。再见！')
    return True


register(
    SceneDef(
        id='2a', chapter=2, title='Площадь у вокзала', zh='火车站',
        art=square_art, look=lambda s: SceneLook('golden'),
        path=[(10, 164), (160, 166), (310, 164)],
        entries={'station': 160},
        actors=[
            ActorDef('driver', 'Таксист', fig(P.WHITE, P.DARK_BLUE, 'jacket', 'cap', hat_color=P.DARK_BLUE), 90, 160, 'right',
                     on_talk=driver_talk, on_item=driver_item),
            ActorDef('mapman', 'Продавец карт', fig(P.MOSS, P.OCHRE, 'jacket', 'straw', kind='old'), 142, 160, 'left',
                     on_talk=mapman_talk, on_item=mapman_item),
            ActorDef('fruit', 'Торговка фруктами', fig(P.ROSE, P.WHITE, 'jacket', 'bun'), 240, 152, 'left', stand_at=222,
                     on_talk=fruit_talk, on_item=fruit_item),
        ],
        signs=[
            SignDef('station', '泰安站', 136, 58, 'blue'),
            SignDef('taxi', '出租车', 32, 106, 'lit'),
            SignDef('bus', '公共汽车', 258, 70, 'blue'),
            SignDef('fruit', '水果', 226, 98, 'banner'),
            SignDef('maps', '地图', 112, 110, 'tag'),
        ],
        exits=[ExitDef('taxi', '2b', 'door', (30, 124, 54, 32), 'left', 70, 'Такси', guard=square_exit)],
        on_enter=square_enter,
        music='city',
    )
)

# ---------------------------------------------------------------- 2b · hotel lobby


def lobby_art(s, look: SceneLook) -> None:
    c = kit.C
    kit.panel_wall(0, 128, P.PEACH, P.OCHRE)
    c.rect(0, 0, 320, 6, P.OCHRE)
    for x in range(20, 320, 60):
        c.circ(x, 10, 4, P.LAMP)
    kit.tiles(128, P.PAPER, P.PEACH, 18)
    # reception desk and the wall behind it
    c.rect(96, 50, 108, 50, P.WOOD)
    c.rect(98, 52, 104, 20, P.OCHRE)
    # clock: half past four
    c.circ(186, 86, 7, P.WHITE)
    c.circb(186, 86, 7, P.INK)
    c.line(186, 86, 190, 88, P.INK)
    c.line(186, 86, 186, 92, P.INK)
    # elevator
    c.rect(248, 62, 34, 66, P.GREY)
    c.rect(252, 70, 26, 58, P.STONE)
    c.line(265, 70, 265, 127, P.INK)
    c.rect(284, 90, 4, 8, P.INK)
    c.pset(286, 92, P.VERMILION)
    # sofa and a plant
    c.rect(18, 140, 44, 12, P.VERMILION)
    c.rect(18, 132, 44, 8, P.LACQUER)
    c.rect(14, 134, 6, 18, P.LACQUER)
    c.rect(60, 134, 6, 18, P.LACQUER)
    kit.plant_pot(232, 152)
    # street door
    c.rect(0, 70, 12, 60, P.LIGHT_BLUE)
    c.rect(0, 70, 12, 3, P.WOOD)


def lobby_front(s, look: SceneLook) -> None:
    c = kit.C
    c.rect(92, 118, 116, 30, P.WOOD)
    c.rect(90, 114, 120, 5, P.OCHRE)
    c.rect(100, 126, 100, 2, P.OCHRE)


async def lobby_enter(c: ScriptContext) -> None:
    if c.flag('lobby_in'):
        return
    c.set('lobby_in')
    await c.say('clerk2', '您好！欢迎！')


async def reception_talk(c: ScriptContext) -> None:
    if c.has('keycard'):
        await cycle(c, 'recep_n', 'clerk2', ['您的房间在三楼。电梯在那儿。', '饭馆在宾馆旁边，很好吃！', '晚上好！'])
        return
    if c.flag('room_price'):
        if c.state.coins < 300:
            await c.say('clerk2', '三百块。您的钱不够。银行在宾馆旁边，您可以去换钱。')
        else:
            await c.say('clerk2', '一个晚上，三百块。')
        return
    if not c.flag('checkin_passport'):
        answer = await c.ask('clerk2', '您好！您要住宾馆吗？')
        if no(answer):
            await c.say('clerk2', '好的。')
            return
        await c.say('clerk2', '请给我您的护照。')
        c.set('checkin_asked')
        return
    await ask_days(c)


async def ask_days(c: ScriptContext) -> None:
    answer = await c.ask('clerk2', '您住几天？')
    a = normalize(answer)
    if any(n in a for n in '一二三两') or '晚' in a:
        await c.say('clerk2', '好。一个晚上，三百块。您有信用卡吗？')
        c.set('room_price')
    else:
        await c.say('clerk2', '一天？两天？')


async def reception_item(c: ScriptContext, item: str) -> bool:
    if c.has('keycard'):
        return False
    if item == 'passport' and c.flag('checkin_asked') and not c.flag('checkin_passport'):
        c.set('checkin_passport')
        await c.say('clerk2', '谢谢。')
        await ask_days(c)
        return True
    if item == 'card' and c.flag('room_price'):
        await c.narrate('Администратор вставляет карту в терминал. Короткий писк, красная надпись.')
        await c.say('clerk2', '对不起，这个卡不能用。没关系，您有钱吗？')
        c.set('card_failed')
        return True
    if item == 'money' and c.flag('room_price'):
        if c.state.coins < 300:
            await c.say('clerk2', '对不起，钱不够。银行在宾馆旁边，您可以去换钱。')
            c.set('need_bank')
            return True
        c.add_coins(-300)
        await c.say('clerk2', '好！您的房间在三楼，三零八。这是您的房卡。电梯在那儿。')
        await c.say('clerk2', '您饿了吗？饭馆在宾馆旁边，很好吃！')
        c.give('keycard')
        return True
    return False


async def newspaper_talk(c: ScriptContext) -> None:
    await cycle(c, 'paper_n', 'guest', ['你好。……今天的报纸说，明天是晴天。', '我每天早上看报纸。', '泰山？我去过三次！'])


async def elevator_guard(c: ScriptContext) -> bool:
    if not c.has('keycard'):
        await c.narrate('Лифт не едет без карточки от номера.')
        return False
    return True


register(
    SceneDef(
        id='2b', chapter=2, title='Гостиница', zh='宾馆',
        art=lobby_art, front=lobby_front, look=lambda s: SceneLook('day'),
        path=[(8, 164), (300, 164)],
        entries={'door': 30, 'street': 20, 'elevator': 262},
        actors=[
            ActorDef('clerk2', 'Администратор', fig(P.LACQUER, P.GOLD, 'uniform', 'bun'), 150, 132, 'right', stand_at=150,
                     on_talk=reception_talk, on_item=reception_item),
            ActorDef('guest', 'Постоялец с газетой', fig(P.STONE, P.PAPER, 'jacket', 'short', pose='sit', glasses=True, prop='book'), 40, 146, 'right',
                     stand_at=74, on_talk=newspaper_talk),
        ],
        signs=[
            SignDef('hotel', '泰山宾馆', 124, 56, 'plaque'),
            SignDef('lift', '电梯', 252, 50, 'blue'),
            SignDef('breakfast', '早饭\n七点', 212, 70, 'paper'),
        ],
        exits=[
            ExitDef('street', '2d', 'hotel', (0, 70, 14, 90), 'left', 12, 'Улица'),
            ExitDef('elevator', '2c', 'door', (250, 68, 30, 62), 'up', 264, 'Лифт', guard=elevator_guard),
        ],
        on_enter=lobby_enter,
        music='city',
    )
)

# ---------------------------------------------------------------- 2c · hotel room


def room_night(s) -> bool:
    return bool(s.on('know_deadline'))


def room_art(s, look: SceneLook) -> None:
    c = kit.C
    kit.panel_wall(0, 130, P.PAPER, P.GREY)
    kit.tiles(130, P.OCHRE, P.WOOD, 24)
    # window with the mountain; at night a thread of pilgrims' lamps goes up
    wx, wy, ww, wh = 118, 20, 96, 64
    c.rect(wx, wy, ww, wh, P.LIGHT_BLUE if not room_night(s) else P.NAVY)
    if room_night(s):
        kit.stars(7, 20, wy + 30)
    kit.canvas(c)
    for i in range(ww):
        x = wx + i
        top = wy + 18 + int(abs(i - 58) * 0.6) + int(pyxel.noise(i / 9, 3) * 4)
        c.line(x, top, x, wy + wh - 1, P.STONE if not room_night(s) else P.INK)
    if room_night(s):
        for i in range(12):
            c.pset(wx + 20 + i * 3 + (i % 3), wy + wh - 8 - i * 3, P.LAMP)
    c.rectb(wx, wy, ww, wh, P.WOOD)
    c.line(wx + ww // 2, wy, wx + ww // 2, wy + wh, P.WOOD)
    c.rect(wx - 6, wy - 4, 8, wh + 10, P.JADE)
    c.rect(wx + ww - 2, wy - 4, 8, wh + 10, P.JADE)
    # air conditioner
    c.rect(24, 24, 50, 14, P.WHITE)
    c.line(28, 34, 70, 34, P.GREY)
    c.pset(68, 28, P.JADE)
    # bed
    c.rect(214, 118, 96, 24, P.WHITE)
    c.rect(214, 110, 20, 10, P.PAPER)
    c.rect(210, 96, 6, 50, P.WOOD)
    c.rect(214, 130, 96, 12, P.PERIWINKLE)
    c.rect(306, 110, 6, 36, P.WOOD)
    # TV on a stand
    c.rect(20, 92, 52, 34, P.INK)
    c.rect(24, 96, 44, 26, P.DARK_BLUE if not s.on('tv_on') else P.LIGHT_BLUE)
    c.rect(16, 126, 60, 16, P.WOOD)
    # fridge
    c.rect(84, 112, 22, 30, P.WHITE)
    c.line(84, 124, 105, 124, P.GREY)
    c.rect(102, 116, 2, 6, P.GREY)
    # bathroom door
    c.rect(286, 52, 30, 44, P.OCHRE)
    c.rect(282, 48, 38, 4, P.WOOD)


def room_anim(s, look: SceneLook, frame: int) -> None:
    if s.on('tv_on'):
        for i in range(3):
            pyxel.line(26, 100 + i * 7, 26 + (frame * 3 + i * 17) % 40, 100 + i * 7, P.WHITE)
        pyxel.circ(58, 104, 4, P.YELLOW)


async def room_enter(c: ScriptContext) -> None:
    if c.flag('room_in'):
        return
    c.set('room_in')
    await c.narrate('Номер 308. Кровать, телевизор, окно — и в окне гора.')
    await c.narrate('Дед писал, что жил в гостинице. Открываю дневник на второй записи.')
    await c.read('diary_2')


async def tv(c: ScriptContext) -> None:
    c.set('tv_on')
    c.sfx('tv')
    await c.say('tv', '现在是天气。今天是晴天，明天也是晴天，不热也不冷。')
    await c.say('tv', '但是明天晚上，山上有雨！')
    c.unlock('forecast')
    c.set('saw_forecast')
    await c.narrate('На экране над горой нарисована туча с каплями. Завтра ночью там будет дождь.')


async def ac(c: ScriptContext) -> None:
    await c.say('player', '太热了！', auto=40)
    await c.narrate('Нажимаю кнопку. Кондиционер (空调) гудит и дует прохладой.')


async def fridge(c: ScriptContext) -> None:
    if c.flag('took_drink'):
        await c.narrate('В холодильнике только пиво. Не сегодня.')
        return
    c.set('took_drink')
    await c.narrate('В маленьком холодильнике напитки (饮料) и пиво (啤酒). Беру бутылку холодного чая.')
    c.give('drink')


async def bathroom(c: ScriptContext) -> None:
    await c.narrate('Душ, зубная щётка в пакетике, табличка на стене. Смываю с себя дорогу.')
    await c.read('bath_sign')


async def window(c: ScriptContext) -> None:
    if room_night(c.state):
        await c.narrate('Ночь. По чёрному склону горы тянется цепочка огоньков — люди поднимаются встречать рассвет. Завтра ночью и я.')
    else:
        await c.narrate('Гора совсем рядом, за крышами. Где-то там, на середине, чайная у Средних ворот.')


async def bed(c: ScriptContext) -> None:
    if not c.flag('know_deadline'):
        await c.narrate('Спать ещё рано. Надо понять, где искать Ли Мина. На карте рядом с гостиницей — старый храм Дай.')
        return
    await c.narrate('Ложусь. Завтра — мост деда, а ночью подъём. Послезавтра на рассвете — равноденствие.')
    await c.event('sleep')
    await c.narrate('Утро. Двадцать второе сентября. Автобус до деревни у реки — там мост, который строил дед.')
    await c.goto('3a', 'road')


texts.add(TextDef('bath_sign', 'sign', 'Табличка в ванной', '洗澡\n刷牙\n请用热水', 'Мыться. Чистить зубы. Пожалуйста, пользуйтесь горячей водой.', chapter=2))

register(
    SceneDef(
        id='2c', chapter=2, title='Номер 308', zh='房间',
        art=room_art, anim=room_anim, look=lambda s: SceneLook('night' if room_night(s) else 'golden'),
        path=[(10, 164), (300, 164)],
        entries={'door': 260},
        hotspots=[
            HotspotDef('tv', 'Телевизор', (18, 90, 58, 38), stand_at=60, on_click=tv, cursor='hand'),
            HotspotDef('ac', 'Кондиционер', (22, 22, 54, 18), stand_at=50, on_click=ac, cursor='hand'),
            HotspotDef('fridge', 'Холодильник', (82, 110, 26, 34), stand_at=96, on_click=fridge, cursor='hand'),
            HotspotDef('window', 'Окно', (116, 18, 100, 68), stand_at=166, on_click=window),
            HotspotDef('bath', 'Ванная', (284, 50, 34, 48), stand_at=292, on_click=bathroom),
            HotspotDef('bed', 'Кровать', (212, 94, 100, 50), stand_at=236, on_click=bed, cursor='hand'),
        ],
        signs=[
            SignDef('number', '三零八', 226, 78, 'tag'),
            SignDef('guide', '房间里有：\n电视　空调\n冰箱　电话', 224, 30, 'paper'),
            SignDef('minibar', '饮料十块\n啤酒十五', 76, 88, 'tag'),
        ],
        exits=[ExitDef('lift', '2b', 'elevator', (240, 60, 20, 20), 'down', 250, 'Лифт вниз')],
        marks={'tv': (46, 88)},
        on_enter=room_enter,
        diary=('diary_2',),
        music='room',
    )
)

# ---------------------------------------------------------------- 2d · street

DISHES = {'米饭': 2, '面条': 10, '鸡蛋': 5, '羊肉': 30, '鱼': 25, '菜': 8, '啤酒': 6, '茶': 3}


def street_look(s) -> SceneLook:
    return SceneLook('sunset' if s.on('know_deadline') else 'golden')


def street_art(s, look: SceneLook) -> None:
    c = kit.C
    kit.sky([(P.LIGHT_BLUE, 24), (P.MIST, 16)])
    kit.ridge(46, 8, 30, 41, P.PERIWINKLE, peaks=[(170, 30, 80)])
    # three shop fronts
    fronts = [(0, 98, P.PAPER, '银行'), (104, 110, P.PEACH, '饭馆'), (220, 100, P.MIST, '商店')]
    for x, w, col, _ in fronts:
        c.rect(x, 40, w, 92, col)
        kit.roof(x - 2, 40, w + 4, 6, P.INK, P.STONE)
    # bank: glass door and a teller window
    c.rect(10, 70, 30, 60, P.LIGHT_BLUE)
    c.line(25, 70, 25, 130, P.GREY)
    c.rect(52, 76, 36, 30, P.LIGHT_BLUE)
    c.rect(50, 104, 40, 4, P.GREY)
    # eatery: open front, tables
    c.rect(112, 66, 94, 66, P.WOOD)
    c.rect(116, 70, 86, 40, P.OCHRE)
    for lx in (120, 160, 196):
        kit.lantern(lx, 46, True)
    for tx in (122, 170):
        c.rect(tx, 136, 30, 4, P.WOOD)
        c.rect(tx + 2, 140, 3, 10, P.WOOD)
        c.rect(tx + 25, 140, 3, 10, P.WOOD)
    if not s.on('cake_taken'):
        c.rect(178, 130, 12, 6, P.WHITE)
        c.rect(178, 128, 12, 2, P.PINK)
        c.pset(184, 126, P.YELLOW)
    # shop: goods outside
    c.rect(228, 70, 84, 60, P.PAPER)
    for i, col in enumerate((P.VERMILION, P.INK, P.DARK_BLUE)):
        x = 236 + i * 12
        c.tri(x - 5, 82, x + 5, 82, x, 76, col)
        c.line(x, 82, x, 96, P.WOOD)
    for i, col in enumerate((P.JADE, P.YELLOW, P.PINK, P.DARK_BLUE)):
        c.rect(276 + i * 8, 76, 6, 14, col)
        c.line(276 + i * 8, 76, 282 + i * 8, 76, P.INK)
    c.rect(234, 117, 24, 13, P.WHITE)
    c.rect(236, 119, 20, 10, P.LIGHT_BLUE)
    for i in range(3):
        c.rect(238 + i * 6, 121, 4, 7, (P.VERMILION, P.JADE, P.YELLOW)[i])
    c.circ(292, 102, 7, P.WHITE)
    c.circ(288, 97, 3, P.INK)
    c.circ(296, 97, 3, P.INK)
    c.circ(290, 102, 2, P.INK)
    c.circ(294, 102, 2, P.INK)
    c.pset(290, 102, P.WHITE)
    c.pset(294, 102, P.WHITE)
    c.rect(291, 105, 3, 1, P.INK)
    # pavement
    kit.ground(132, P.GREY, P.STONE, seed=44, density=0.02)
    c.line(0, 132, 320, 132, P.STONE)
    # a bicycle
    c.circb(96, 154, 6, P.INK)
    c.circb(112, 154, 6, P.INK)
    c.line(96, 154, 104, 146, P.VERMILION)
    c.line(104, 146, 112, 154, P.VERMILION)
    c.line(104, 146, 110, 146, P.VERMILION)
    # a dog asleep under the table
    c.elli(150, 150, 14, 6, P.OCHRE)
    c.circ(151, 150, 3, P.OCHRE)
    c.pset(150, 149, P.INK)


async def street_enter(c: ScriptContext) -> None:
    if c.flag('street_in'):
        return
    c.set('street_in')
    await c.narrate('Улица за гостиницей: банк, ресторанчик со столиками прямо на тротуаре, лавка с зонтиками. Дальше, за перекрёстком, — стены храма.')


async def bank_talk(c: ScriptContext) -> None:
    if c.flag('bank_done'):
        await c.say('banker', '再见！')
        return
    answer = await c.ask('banker', '您好！您要做什么？')
    if '钱' in normalize(answer):
        await c.say('banker', '换钱？好。请给我您的卡。')
        c.set('bank_asked')
    else:
        await c.say('banker', '您要换钱吗？')
        c.set('bank_asked')


async def bank_item(c: ScriptContext, item: str) -> bool:
    if c.flag('bank_done'):
        return False
    if item == 'card':
        await c.say('banker', '请等一下。')
        await c.wait(600)
        await c.say('banker', '好了！给您一千块。')
        c.add_coins(1000)
        c.set('bank_done')
        return True
    if item == 'passport':
        await c.say('banker', '谢谢。您的卡呢？')
        return True
    return False


async def waiter_talk(c: ScriptContext) -> None:
    if c.flag('dinner_done'):
        await cycle(c, 'waiter_n', 'waiter', ['好吃吗？', '欢迎再来！'])
        return
    if not c.flag('eatery_seat'):
        answer = await c.ask('waiter', '您好！几位？')
        if '一' in normalize(answer) or yes(answer):
            await c.say('waiter', '一位？请坐！这是菜单。')
            c.set('eatery_seat')
            await c.read('menu2')
        else:
            await c.say('waiter', '几位？一位？')
        return
    if c.flag('bill'):
        await c.say('waiter', f'一共{to_hanzi(int(c.flag("bill")))}块。')
        return
    answer = await c.ask('waiter', '你想吃什么？')
    order = [d for d in DISHES if d in normalize(answer)]
    if not order:
        await c.say('waiter', '米饭？面条？鱼？羊肉？')
        return
    answer2 = await c.ask('waiter', '好！还要什么？喝什么？')
    order += [d for d in DISHES if d in normalize(answer2) and d not in order]
    total = sum(DISHES[d] for d in order)
    c.set('bill', total)
    await c.say('waiter', f'一共{to_hanzi(total)}块。')


async def waiter_item(c: ScriptContext, item: str) -> bool:
    if item == 'money' and c.flag('bill') and not c.flag('dinner_done'):
        if await pay(c, 'waiter', int(c.flag('bill')), item):
            await c.say('waiter', '谢谢！请等一下。')
            await c.say('waiter', '这是筷子，这是碗，这是盘子。')
            await c.narrate('Приносят еду, пар столбом. Очень вкусно — и очень остро.')
            await c.say('player', '好吃！', auto=40)
            c.set('dinner_done')
            c.set('bill', 0)
        return True
    return False


async def family_talk(c: ScriptContext) -> None:
    if c.flag('cake_taken'):
        await cycle(c, 'family_n', 'mother', ['生日快乐！', '谢谢你！'])
        return
    if not c.flag('family_met'):
        c.set('family_met')
        await c.talk([
            ('father', '今天是我女儿的生日！'),
            ('mother', '她七岁了。'),
            ('daughter', '我很高兴！'),
        ])
        return
    answer = await c.ask('mother', '你吃蛋糕吗？')
    if yes(answer) or '吃' in normalize(answer) or '蛋糕' in normalize(answer):
        await c.say('daughter', '给你！')
        c.give('cake')
        c.set('cake_taken')
        await c.narrate('Все хлопают. Девочка очень серьёзно отрезает мне кусок торта.')
    elif no(answer):
        await c.say('mother', '没关系！')


async def daughter_talk(c: ScriptContext) -> None:
    if c.flag('sang_birthday'):
        await c.say('daughter', '谢谢！')
        return
    answer = await c.ask('daughter', '今天是我的生日！')
    a = normalize(answer)
    if '生日' in a and '快乐' in a:
        c.set('sang_birthday')
        await c.say('daughter', '谢谢！谢谢！')
        await c.say('father', '你会说中文！')
    elif a:
        await c.say('father', '她说：今天是她的生日。你知道「生日快乐」吗？')


async def oldmen_talk(c: ScriptContext) -> None:
    step = int(c.flag('oldmen_step') or 0)
    if step == 0:
        answer = await c.ask('oldman1', '你好！你是哪国人？')
        if '俄罗斯' in normalize(answer):
            await c.say('oldman1', '俄罗斯！我爸爸认识俄罗斯人！')
            await c.say('oldman2', '一九五八年，很多俄罗斯人在泰安工作。')
            await c.say('oldman1', '他们在大汶河修大桥。')
            c.set('oldmen_step', 1)
        else:
            await c.say('oldman2', '他说：你是哪国人？')
        return
    if step == 1:
        answer = await c.ask('oldman2', '你喜欢喝啤酒吗？')
        if yes(answer) or '喜欢' in normalize(answer):
            await c.say('oldman2', '好！我们一起喝！')
        else:
            await c.say('oldman1', '不喜欢？那喝茶吧！')
        c.set('oldmen_step', 2)
        return
    await cycle(c, 'oldmen_n', 'oldman1', ['你爷爷也在泰安工作过吗？', '泰山很高，你要多休息！'])


async def shop_talk(c: ScriptContext) -> None:
    pending = c.flag('shop_order')
    if pending:
        await c.say('shopkeeper', {'red': '红的三十块。', 'black': '黑的二十块。'}.get(str(pending), '你要哪个？'))
        return
    answer = await c.ask('shopkeeper', '欢迎！你要买什么？')
    a = normalize(answer)
    if '伞' in a:
        answer2 = await c.ask('shopkeeper', '雨伞在这儿。红的三十块，黑的二十块。你要哪个？')
        b = normalize(answer2)
        if '红' in b:
            c.set('shop_order', 'red')
            await c.say('shopkeeper', '红的，三十块。')
        elif '黑' in b:
            c.set('shop_order', 'black')
            await c.say('shopkeeper', '黑的，二十块。')
        else:
            await c.say('shopkeeper', '红的？黑的？')
    elif '地图' in a:
        await c.say('shopkeeper', '地图？火车站那儿有。')
    elif '熊猫' in a:
        await c.say('shopkeeper', '熊猫五十块。很可爱吧？')
    elif a:
        await c.say('shopkeeper', '我们卖衣服、裤子、帽子、雨伞、饮料……')


async def shop_item(c: ScriptContext, item: str) -> bool:
    pending = c.flag('shop_order')
    if item == 'money' and pending in ('red', 'black'):
        price = 30 if pending == 'red' else 20
        if await pay(c, 'shopkeeper', price, item):
            await c.say('shopkeeper', '谢谢！明天山上有雨，带上雨伞！')
            c.give('umbrella')
            c.set('shop_order', '')
        return True
    return False


async def street_guard_temple(c: ScriptContext) -> bool:
    return True


register(
    SceneDef(
        id='2d', chapter=2, title='Улица', zh='街道',
        art=street_art, look=street_look,
        path=[(8, 164), (160, 166), (312, 164)],
        entries={'hotel': 20, 'temple': 300},
        actors=[
            ActorDef('banker', 'Кассир банка', fig(P.DARK_BLUE, P.WHITE, 'uniform', 'short', glasses=True), 70, 124, 'right', stand_at=70,
                     on_talk=bank_talk, on_item=bank_item),
            ActorDef('waiter', 'Официант', fig(P.WHITE, P.VERMILION, 'jacket', 'short'), 132, 160, 'right', on_talk=waiter_talk, on_item=waiter_item),
            ActorDef('father', 'Отец семейства', fig(P.NAVY, P.WHITE, 'jacket', 'short', pose='sit'), 166, 148, 'right', on_talk=family_talk),
            ActorDef('mother', 'Мать', fig(P.PINK, P.WHITE, 'dress', 'ponytail', pose='sit'), 196, 148, 'left', on_talk=family_talk),
            ActorDef('daughter', 'Именинница', fig(P.YELLOW, P.PINK, 'dress', 'twinbuns', kind='child'), 184, 158, 'left', stand_at=172,
                     on_talk=daughter_talk),
            ActorDef('oldman1', 'Старик с пивом', fig(P.WOOD, P.OCHRE, 'jacket', 'bald', kind='old', pose='sit'), 120, 148, 'right',
                     stand_at=110, on_talk=oldmen_talk),
            ActorDef('oldman2', 'Его приятель', fig(P.STONE, P.GREY, 'jacket', 'cap', kind='old', pose='sit'), 150, 148, 'left',
                     stand_at=110, on_talk=oldmen_talk),
            ActorDef('shopkeeper', 'Продавщица', fig(P.JADE, P.WHITE, 'jacket', 'bun'), 262, 158, 'left', on_talk=shop_talk, on_item=shop_item),
        ],
        signs=[
            SignDef('bank', '银行', 30, 48, 'blue'),
            SignDef('eatery', '饭馆', 140, 48, 'banner'),
            SignDef('shop', '商店', 250, 48, 'lit'),
            SignDef('umbrellas', '雨伞', 230, 98, 'tag'),
            SignDef('panda', '熊猫五十', 262, 115, 'tag'),
            SignDef('to_temple', '岱庙', 290, 132, 'board'),
            SignDef('street', '岱宗大街', 104, 118, 'blue'),
        ],
        exits=[
            ExitDef('hotel', '2b', 'street', (0, 80, 10, 90), 'left', 10, 'Гостиница'),
            ExitDef('temple', '2e', 'gate', (310, 100, 10, 70), 'right', 312, 'Храм Дай'),
        ],
        on_enter=street_enter,
        music='city',
    )
)

texts.add(TextDef('menu2', 'sign', 'Меню', '米饭　两块\n面条　十块\n鸡蛋　五块\n羊肉　三十块\n鱼　　二十五块\n菜　　八块\n啤酒　六块\n茶　　三块',
                  'Рис 2, лапша 10, яйца 5, баранина 30, рыба 25, овощи 8, пиво 6, чай 3 юаня.', chapter=2))

# ---------------------------------------------------------------- 2e · Dai Temple


def temple_look(s) -> SceneLook:
    return SceneLook('sunset' if s.on('know_deadline') else 'golden')


def temple_art(s, look: SceneLook) -> None:
    c = kit.C
    kit.sky([(P.LIGHT_BLUE, 30), (P.MIST, 20), (P.WHITE, 12)])
    kit.ridge(60, 10, 40, 51, P.PERIWINKLE, peaks=[(240, 34, 90)])
    # the great hall
    c.rect(96, 52, 150, 50, P.VERMILION)
    for px in range(104, 244, 16):
        kit.pillar(px, 102, 42, P.VERMILION, P.LACQUER)
    kit.roof(86, 52, 170, 14, P.GOLD, P.OCHRE, ridge_col=P.OCHRE)
    kit.roof(96, 38, 150, 9, P.GOLD, P.OCHRE, ridge_col=P.OCHRE)
    c.rect(96, 100, 150, 6, P.STONE)
    kit.stairs(171, 116, 60, 171, 104, 50, P.GREY, P.PAPER, steps=4)
    # walls on the sides
    kit.wall(0, 86, 80, 40, P.VERMILION, P.LACQUER, P.GOLD)
    kit.wall(262, 86, 58, 40, P.VERMILION, P.LACQUER, P.GOLD)
    kit.ground(116, P.PAPER, P.MIST, seed=51, density=0.03)
    # ancient cypresses
    for x, h in ((34, 64), (286, 58)):
        c.rect(x - 2, 132 - h // 2, 6, h // 2, P.WOOD)
        for i in range(5):
            c.elli(x - 14 + i * 2, 132 - h + i * 8, 28 - i * 3, 12, P.PINE)
            c.line(x - 10 + i * 2, 132 - h + i * 8, x + 8, 132 - h + i * 8, P.JADE)
    # the Qin stele in its pavilion
    c.rect(60, 118, 30, 4, P.STONE)
    kit.stele(66, 150, 18, 26)
    kit.roof(56, 118, 38, 6, P.INK, P.STONE)
    c.line(58, 118, 58, 150, P.LACQUER)
    c.line(92, 118, 92, 150, P.LACQUER)
    # incense burner
    c.rect(202, 138, 16, 12, P.OCHRE)
    c.rect(200, 136, 20, 3, P.WOOD)
    for i in range(3):
        c.line(206 + i * 4, 136, 206 + i * 4, 128, P.GREY)


def temple_anim(s, look: SceneLook, frame: int) -> None:
    for i in range(3):
        x = 206 + i * 4 + int(pyxel.sin(frame * 6 + i * 60) * 2)
        y = 126 - (frame // 3 + i * 7) % 20
        pyxel.pset(x, y, P.MIST)


async def temple_enter(c: ScriptContext) -> None:
    if c.flag('temple_in'):
        return
    c.set('temple_in')
    await c.narrate('Храм Дай. Красные стены, огромные кипарисы, дым благовоний. Отсюда когда-то начинали путь на гору императоры.')


async def keeper_talk(c: ScriptContext) -> None:
    if c.flag('know_deadline'):
        await cycle(c, 'keeper_n', 'keeper', ['明天早上去吧。', '你爷爷修的大桥还在！村子里的人还记得他们。', '一路平安！'])
        return
    answer = await c.ask('keeper', '你好！你找谁？')
    if '李明' in normalize(answer) or '李' in normalize(answer):
        await keeper_story(c)
    elif answer:
        await c.say('keeper', '你找谁？')
        await c.narrate('Старик опирается на метлу и ждёт. Кого я ищу? Имя написано на конверте.')


async def keeper_item(c: ScriptContext, item: str) -> bool:
    if item == 'letter' and not c.flag('know_deadline'):
        await c.narrate('Смотритель подносит конверт к глазам.')
        await keeper_story(c)
        return True
    if item == 'photo':
        await c.say('keeper', '这是李明！很年轻！旁边的人是谁？')
        await c.narrate('Показываю на молодого человека рядом с Ли Мином, потом на себя.')
        await c.say('keeper', '你的爷爷？')
        return True
    return False


async def keeper_story(c: ScriptContext) -> None:
    await c.say('keeper', '李明？中天门的李明？')
    await c.say('keeper', '我认识他！他是我的老朋友。')
    await c.say('keeper', '他是挑山工。现在他很老了，八十八岁了。')
    await c.say('keeper', '他每年秋分都上山看日出。')
    await c.say('keeper', '今天是九月二十一号。秋分是二十三号。')
    await c.say('keeper', '他明天晚上上山！你明天早上去中天门吧，他的家人在茶馆。')
    await c.narrate('Равноденствие — двадцать третьего, на рассвете. Ли Мин поднимется на вершину завтра ночью. Нужно успеть.')
    c.set('know_deadline')
    await c.say('keeper', '你爷爷在大汶河修桥？那个桥还在！村子里的人还记得他们。')
    await c.narrate('Мост деда стоит до сих пор. Утром — к мосту, потом на гору.')


async def stele(c: ScriptContext) -> None:
    await c.say('keeper', '这是很老很老的字，两千多年了！')
    await c.narrate('На камне едва видны древние знаки — не такие, как сейчас, больше похожие на рисунки.')
    if not c.flag('ancient_done'):
        ok = await c.puzzle('ancient', glyphs='日月山水人火')
        if ok:
            c.set('ancient_done')
            await c.say('keeper', '你看懂了！很好！')


async def exerciser_talk(c: ScriptContext) -> None:
    await cycle(c, 'ex_n', 'exerciser', ['我每天早上在这儿锻炼身体。', '你也锻炼吗？锻炼身体很重要！', '你要多休息！'])


async def kids_talk(c: ScriptContext) -> None:
    answer = await c.ask('footballer', '你会踢足球吗？')
    if yes(answer):
        await c.say('footballer', '来！一起踢！')
        await c.event('kick')
        await c.say('footballer', '你踢得真好！')
    else:
        await c.say('footballer', '没关系！我教你！')


register(
    SceneDef(
        id='2e', chapter=2, title='Храм Дай', zh='岱庙',
        art=temple_art, anim=temple_anim, look=temple_look,
        path=[(10, 164), (160, 160), (310, 164)],
        entries={'gate': 20},
        actors=[
            ActorDef('keeper', 'Смотритель храма', fig(P.STONE, P.PAPER, 'robe', 'bald', kind='old', beard=True, prop='broom'), 150, 152, 'left',
                     on_talk=keeper_talk, on_item=keeper_item),
            ActorDef('exerciser', 'Бабушка на зарядке', fig(P.VERMILION, P.WHITE, 'jacket', 'short', kind='old', hair=P.GREY), 232, 160, 'left',
                     on_talk=exerciser_talk),
            ActorDef('footballer', 'Мальчик с мячом', fig(P.DARK_BLUE, P.WHITE, 'jacket', 'short', kind='child'), 276, 164, 'left',
                     on_talk=kids_talk),
        ],
        hotspots=[
            HotspotDef('stele', 'Стела Цинь', (58, 116, 36, 36), stand_at=96, on_click=stele),
            HotspotDef('burner', 'Курильница', (198, 124, 24, 28), stand_at=196, on_click=lambda c: c.narrate('Палочки благовоний дымят. Люди кланяются трижды.')),
        ],
        signs=[SignDef('plaque', '岱庙', 160, 62, 'plaque')],
        exits=[ExitDef('street', '2d', 'temple', (0, 100, 10, 70), 'left', 12, 'Улица')],
        on_enter=temple_enter,
        music='temple',
    )
)

# ---------------------------------------------------------------- pages, pictures, glossary, hints

pages.add(
    # the main path
    PageDef('taxi', 'Такси', 2, ('出租车', '司机', '远', '近', '上车', '公共汽车')),
    PageDef('time2', 'Время', 2, ('现在', '下午', '今天', '明天', '晚上', '早上')),
    PageDef('city', 'Город', 2, ('宾馆', '银行', '饭馆', '商店', '地图', '大街')),
    PageDef('hotel', 'В гостинице', 2, ('房间', '电梯', '楼', '电视', '空调', '冰箱'), kind='icon'),
    PageDef('weather', 'Погода', 2, ('天气', '晴', '雨', '热', '冷')),
    PageDef('temple', 'Храм', 2, ('老', '朋友', '认识', '找', '家人', '爷爷')),
    PageDef('numbers3', 'Большие числа', 2, ('百', '千', '岁', '每年')),
    PageDef('please', 'Вежливость', 2, ('您', '对不起', '没关系', '可以', '用'), kind='phrase',
            phrases=('您好！欢迎！', '对不起，这个卡不能用。', '没关系，您有钱吗？', '您可以去换钱。', '这个卡不能用。')),
    PageDef('grammar2', 'Связки', 2, ('很', '也', '吧', '但是', '还', '都'), kind='phrase',
            phrases=('泰山很高！', '很近，也不贵。', '明天去吧！', '但是明天晚上，山上有雨！', '那个桥还在！', '他每年秋分都上山看日出。')),
    PageDef('verbs2', 'Глаголы', 2, ('住', '知道', '做', '等', '换', '走'), kind='phrase',
            phrases=('你今天住哪儿？', '我知道一个宾馆。', '您要做什么？', '请等一下。', '您可以去换钱。', '好！走吧！')),
    PageDef('hotel2', 'Деньги и еда', 2, ('卡', '够', '饿', '旁边', '吃'), kind='phrase',
            phrases=('这个卡不能用。', '钱不够。', '您饿了吗？', '饭馆在宾馆旁边。', '很好吃！')),
    PageDef('diary2', 'Запись деда', 2, ('城市', '里', '干净', '高', '看见'), kind='phrase',
            phrases=('泰安是一个小城市。', '我住在一个宾馆里。', '房间很小，但是很干净。', '泰山很高！', '我看见了泰山。')),
    PageDef('drinks', 'Напитки', 2, ('饮料', '啤酒', '电话'), kind='icon'),
    PageDef('temple2', 'Храм Дай', 2, ('岱庙', '谁', '挑山工'), kind='picture'),
    # side scenes: they open only if you talk to everyone
    PageDef('menu', 'Меню', 2, ('米饭', '面条', '鸡蛋', '羊肉', '鱼', '菜'), kind='icon'),
    PageDef('party', 'День рождения', 2, ('生日', '快乐', '蛋糕', '女儿', '她', '高兴')),
    PageDef('fruit', 'Фрукты', 2, ('西瓜', '香蕉', '水果', '新鲜'), kind='icon'),
    PageDef('shop', 'Покупки', 2, ('雨伞', '熊猫', '卖', '黑')),
    PageDef('clothes', 'Одежда', 2, ('衣服', '裤子', '帽子'), kind='icon'),
    PageDef('table', 'За столом', 2, ('筷子', '碗', '盘子'), kind='icon'),
    PageDef('can', 'Можно и нельзя', 2, ('能', '太', '贵'), kind='phrase',
            phrases=('这个卡不能用。', '太远了！', '很近，也不贵。')),
    PageDef('oldmen', 'Старики', 2, ('爸爸', '工作', '喜欢', '喝', '他们', '很多'), kind='phrase',
            phrases=('我爸爸认识俄罗斯人！', '很多俄罗斯人在泰安工作。', '你喜欢喝啤酒吗？', '你喜欢喝啤酒吗？', '他们在大汶河修大桥。', '很多俄罗斯人在泰安工作。')),
    PageDef('sport', 'Двигаться', 2, ('锻炼', '身体', '踢足球', '休息')),
    PageDef('eat', 'В ресторане', 2, ('位', '菜单', '想', '一共'), kind='phrase',
            phrases=('一位？请坐！', '这是菜单。', '你想吃什么？', '一共十块。')),
    PageDef('bath', 'Ванная', 2, ('洗澡', '刷牙'), kind='icon'),
    PageDef('guest', 'Постоялец', 2, ('报纸', '次', '过', '呢'), kind='phrase',
            phrases=('今天的报纸说，明天是晴天。', '泰山？我去过三次！', '泰山？我去过三次！', '谢谢。您的卡呢？')),
    PageDef('mapman', 'Продавец карт', 2, ('张', '就', '错'), kind='phrase',
            phrases=('地图！地图！十块一张！', '有地图，你就不会走错了！', '有地图，你就不会走错了！')),
    PageDef('kids', 'Во дворе храма', 2, ('得', '真', '教', '懂', '重要'), kind='phrase',
            phrases=('你踢得真好！', '你踢得真好！', '没关系！我教你！', '你看懂了！很好！', '锻炼身体很重要！')),
    PageDef('shop2', 'В лавке', 2, ('带', '爱'), kind='phrase',
            phrases=('明天山上有雨，带上雨伞！', '熊猫五十块。很可爱吧？')),
)

for w, ic in (('房间', 'bed'), ('电梯', 'lift'), ('楼', 'building'), ('电视', 'tv'), ('空调', 'aircon'), ('冰箱', 'fridge'),
              ('米饭', 'rice'), ('面条', 'noodles'), ('鸡蛋', 'egg'), ('羊肉', 'meat'), ('鱼', 'fish'), ('菜', 'greens'),
              ('筷子', 'chopsticks'), ('碗', 'bowl'), ('盘子', 'plate'), ('啤酒', 'beer'), ('饮料', 'bottle'), ('蛋糕', 'cake'),
              ('西瓜', 'watermelon'), ('香蕉', 'banana'), ('水果', 'fruit'), ('雨伞', 'umbrella'), ('衣服', 'shirt'), ('帽子', 'hat'),
              ('熊猫', 'panda'), ('地图', 'map'), ('出租车', 'taxi'), ('电话', 'phone_old'), ('洗澡', 'shower'), ('刷牙', 'toothbrush'),
              ('公共汽车', 'bus'), ('裤子', 'trousers')):
    icon_for(w, ic)


@picture('新鲜')
def _(x: int, y: int) -> None:
    picto.icon('apple', x + 8, y + 10)
    for dx, dy in ((4, 6), (26, 8), (22, 26)):
        pyxel.pset(x + dx, y + dy, P.YELLOW)
        pyxel.pset(x + dx + 1, y + dy, P.WHITE)


@picture('都')
def _(x: int, y: int) -> None:
    for i in range(3):
        picto.icon('apple', x - 2 + i * 10, y + 10)
    pyxel.rectb(x + 1, y + 8, 30, 20, P.VERMILION)


@picture('司机')
def _(x: int, y: int) -> None:
    picto.icon('taxi', x + 8, y + 12)
    pyxel.circ(x + 16, y + 8, 3, P.PEACH)
    pyxel.rect(x + 13, y + 4, 7, 2, P.DARK_BLUE)


@picture('远')
def _(x: int, y: int) -> None:
    picto.person(x + 4, y + 30, P.DARK_BLUE)
    picto.icon('mountain', x + 20, y + 2, 0.6)
    for i in range(6):
        pyxel.pset(x + 8 + i * 3, y + 24 - i * 2, P.STONE)


@picture('近')
def _(x: int, y: int) -> None:
    picto.person(x + 10, y + 30, P.DARK_BLUE)
    picto.icon('house', x + 14, y + 12)


@picture('上车')
def _(x: int, y: int) -> None:
    picto.icon('taxi', x + 12, y + 14)
    picto.person(x + 6, y + 30, P.VERMILION, arm='out')


def _clock(h: float, m: float, sky: int) -> None:
    def draw(x: int, y: int) -> None:
        pyxel.rect(x, y, 32, 12, sky)
        picto.clock(x + 16, y + 20, 10, h, m, 'hour')
    return draw


@picture('现在')
def _(x: int, y: int) -> None:
    picto.clock(x + 16, y + 16, 13, 4, 0, 'minute')
    pyxel.circ(x + 16, y + 16, 2, P.VERMILION)
picture('下午')(_clock(4, 0, P.PEACH))
picture('早上')(_clock(7, 0, P.LIGHT_BLUE))
picture('晚上')(_clock(9, 0, P.NAVY))


@picture('今天')
def _(x: int, y: int) -> None:
    pyxel.rect(x + 6, y + 4, 20, 24, P.WHITE)
    pyxel.rect(x + 6, y + 4, 20, 6, P.VERMILION)
    pyxel.text(x + 11, y + 14, '21', P.INK)
    picto.arrow(x + 2, y + 30, x + 10, y + 26, P.JADE)


@picture('明天')
def _(x: int, y: int) -> None:
    pyxel.rect(x + 2, y + 6, 16, 20, P.GREY)
    pyxel.rect(x + 14, y + 4, 16, 22, P.WHITE)
    pyxel.rect(x + 14, y + 4, 16, 6, P.VERMILION)
    pyxel.text(x + 17, y + 14, '22', P.INK)
    picto.arrow(x + 6, y + 30, x + 24, y + 30, P.JADE)


@picture('宾馆')
def _(x: int, y: int) -> None:
    picto.icon('bed', x + 8, y + 12)
    pyxel.rect(x + 4, y + 2, 24, 8, P.LACQUER)
    pyxel.text(x + 7, y + 3, 'HTL', P.GOLD)


@picture('银行')
def _(x: int, y: int) -> None:
    pyxel.rect(x + 4, y + 12, 24, 16, P.PAPER)
    pyxel.tri(x + 2, y + 12, x + 30, y + 12, x + 16, y + 3, P.STONE)
    for cx in range(7, 28, 6):
        pyxel.rect(x + cx, y + 14, 2, 12, P.GREY)
    picto.icon('coins', x + 16, y + 16, 0.6)


@picture('饭馆')
def _(x: int, y: int) -> None:
    picto.icon('bowl', x + 8, y + 12)
    for lx in (8, 24):
        kit.canvas(pyxel)
        kit.lantern(x + lx, y, True)


@picture('商店')
def _(x: int, y: int) -> None:
    picto.icon('bag', x + 8, y + 10)
    pyxel.rect(x + 2, y + 4, 28, 5, P.JADE)


@picture('地图')
def _(x: int, y: int) -> None:
    picto.icon('map', x + 8, y + 8)


@picture('大街')
def _(x: int, y: int) -> None:
    pyxel.tri(x + 12, y + 8, x + 20, y + 8, x + 30, y + 31, P.GREY)
    pyxel.tri(x + 12, y + 8, x + 2, y + 31, x + 30, y + 31, P.GREY)
    pyxel.line(x + 16, y + 10, x + 16, y + 30, P.WHITE)
    kit.canvas(pyxel)
    kit.building(x, y + 18, 8, 12, P.MIST)
    kit.building(x + 25, y + 18, 7, 14, P.MIST)


@picture('天气')
def _(x: int, y: int) -> None:
    picto.icon('sun', x, y + 2)
    kit.canvas(pyxel)
    kit.cloud(x + 12, y + 12, 18)
    for i in range(3):
        pyxel.line(x + 14 + i * 5, y + 24, x + 13 + i * 5, y + 28, P.DARK_BLUE)


@picture('晴')
def _(x: int, y: int) -> None:
    pyxel.rect(x, y, 32, 32, P.LIGHT_BLUE)
    picto.icon('sun', x + 8, y + 8)


@picture('雨')
def _(x: int, y: int) -> None:
    pyxel.rect(x, y, 32, 32, P.MIST)
    kit.canvas(pyxel)
    kit.cloud(x + 4, y + 2, 24, P.GREY, P.STONE)
    for i in range(5):
        pyxel.line(x + 6 + i * 5, y + 16, x + 4 + i * 5, y + 26, P.DARK_BLUE)


@picture('热')
def _(x: int, y: int) -> None:
    picto.icon('sun', x + 2, y + 2)
    pyxel.rect(x + 22, y + 6, 4, 20, P.WHITE)
    pyxel.rectb(x + 22, y + 6, 4, 20, P.INK)
    pyxel.rect(x + 23, y + 10, 2, 16, P.VERMILION)


@picture('冷')
def _(x: int, y: int) -> None:
    for i in range(6):
        pyxel.pset(x + 4 + i * 4, y + 6 + (i % 3) * 5, P.LIGHT_BLUE)
    pyxel.rect(x + 22, y + 6, 4, 20, P.WHITE)
    pyxel.rectb(x + 22, y + 6, 4, 20, P.INK)
    pyxel.rect(x + 23, y + 22, 2, 4, P.DARK_BLUE)
    picto.person(x + 10, y + 30, P.LIGHT_BLUE)


@picture('卖')
def _(x: int, y: int) -> None:
    picto.person(x + 8, y + 30, P.JADE, arm='out')
    picto.icon('coins', x + 16, y + 4, 0.7)
    picto.icon('apple', x + 16, y + 16, 0.7)


@picture('贵')
def _(x: int, y: int) -> None:
    for i in range(4):
        picto.icon('coins', x + 2 + i * 5, y + 16 - i * 4, 0.7)
    picto.arrow(x + 26, y + 26, x + 26, y + 6, P.VERMILION)


@picture('爸爸')
def _(x: int, y: int) -> None:
    picto.person(x + 12, y + 30, P.NAVY)
    picto.person(x + 22, y + 30, P.YELLOW)
    pyxel.rect(x + 20, y + 22, 5, 8, P.YELLOW)
    picto.arrow(x + 4, y + 6, x + 10, y + 12, P.VERMILION)


@picture('女儿')
def _(x: int, y: int) -> None:
    picto.person(x + 10, y + 30, P.NAVY)
    pyxel.rect(x + 18, y + 22, 6, 8, P.PINK)
    pyxel.circ(x + 21, y + 19, 2, P.PEACH)
    picto.arrow(x + 28, y + 8, x + 23, y + 14, P.VERMILION)


@picture('生日')
def _(x: int, y: int) -> None:
    picto.icon('cake', x + 8, y + 10)
    pyxel.line(x + 16, y + 4, x + 16, y + 10, P.WHITE)
    pyxel.pset(x + 16, y + 3, P.YELLOW)


@picture('岁')
def _(x: int, y: int) -> None:
    pyxel.rect(x + 8, y + 20, 16, 8, P.WHITE)
    for i in range(7):
        pyxel.line(x + 9 + i * 2, y + 14, x + 9 + i * 2, y + 20, P.PINK)
        pyxel.pset(x + 9 + i * 2, y + 13, P.YELLOW)


@picture('快乐')
def _(x: int, y: int) -> None:
    pyxel.circ(x + 16, y + 16, 11, P.YELLOW)
    pyxel.circb(x + 16, y + 16, 11, P.INK)
    pyxel.pset(x + 12, y + 13, P.INK)
    pyxel.pset(x + 20, y + 13, P.INK)
    pyxel.line(x + 11, y + 19, x + 21, y + 19, P.INK)
    pyxel.line(x + 13, y + 21, x + 19, y + 21, P.INK)


@picture('高兴')
def _(x: int, y: int) -> None:
    picto.person(x + 16, y + 30, P.VERMILION, arm='wide')
    for dx in (4, 26):
        pyxel.pset(x + dx, y + 6, P.YELLOW)


@picture('老')
def _(x: int, y: int) -> None:
    picto.person(x + 12, y + 30, P.STONE, hair=P.GREY)
    pyxel.line(x + 18, y + 18, x + 20, y + 30, P.WOOD)


@picture('朋友')
def _(x: int, y: int) -> None:
    picto.person(x + 10, y + 30, P.DARK_BLUE, arm='out')
    picto.person(x + 22, y + 30, P.JADE)
    pyxel.pset(x + 16, y + 8, P.VERMILION)
    pyxel.pset(x + 15, y + 7, P.VERMILION)
    pyxel.pset(x + 17, y + 7, P.VERMILION)


@picture('认识')
def _(x: int, y: int) -> None:
    picto.person(x + 8, y + 30, P.DARK_BLUE)
    picto.person(x + 24, y + 30, P.JADE)
    picto.bubble(x + 10, y + 2, 12, 9)
    pyxel.text(x + 14, y + 3, '!', P.VERMILION)


@picture('找')
def _(x: int, y: int) -> None:
    pyxel.circb(x + 13, y + 13, 8, P.INK)
    pyxel.line(x + 19, y + 19, x + 27, y + 27, P.WOOD)
    pyxel.text(x + 11, y + 10, '?', P.VERMILION)


@picture('家人')
def _(x: int, y: int) -> None:
    picto.icon('house', x, y + 2)
    picto.person(x + 20, y + 30, P.NAVY)
    pyxel.rect(x + 25, y + 24, 4, 6, P.PINK)


@picture('爷爷')
def _(x: int, y: int) -> None:
    picto.person(x + 12, y + 30, P.STONE, hair=P.WHITE)
    pyxel.rect(x + 12, y + 16, 3, 3, P.WHITE)
    pyxel.line(x + 17, y + 18, x + 19, y + 30, P.WOOD)
    pyxel.rect(x + 22, y + 24, 5, 6, P.YELLOW)
    pyxel.circ(x + 24, y + 21, 2, P.PEACH)


@picture('百')
def _(x: int, y: int) -> None:
    for i in range(10):
        for j in range(10):
            pyxel.pset(x + 6 + i * 2, y + 6 + j * 2, P.VERMILION)


@picture('千')
def _(x: int, y: int) -> None:
    for k in range(4):
        for i in range(10):
            for j in range(10):
                if (i + j) % 2 == 0:
                    pyxel.pset(x + 2 + (k % 2) * 15 + i, y + 2 + (k // 2) * 15 + j, P.VERMILION)
    pyxel.text(x + 8, y + 26, '...', P.STONE)


@picture('每年')
def _(x: int, y: int) -> None:
    for i in range(3):
        pyxel.rect(x + 2 + i * 10, y + 8, 8, 10, P.WHITE)
        pyxel.rect(x + 2 + i * 10, y + 8, 8, 3, P.VERMILION)
        picto.icon('sun', x + i * 10 - 2, y + 16, 0.5)


@picture('岱庙')
def _(x: int, y: int) -> None:
    pyxel.rect(x + 4, y + 16, 24, 14, P.VERMILION)
    kit.canvas(pyxel)
    kit.roof(x + 2, y + 16, 28, 7, P.GOLD, P.OCHRE)
    pyxel.rect(x + 13, y + 22, 6, 8, P.INK)


@picture('谁')
def _(x: int, y: int) -> None:
    pyxel.circ(x + 16, y + 12, 6, P.GREY)
    pyxel.rect(x + 10, y + 18, 12, 12, P.GREY)
    pyxel.text(x + 14, y + 9, '?', P.VERMILION)


@picture('挑山工')
def _(x: int, y: int) -> None:
    pyxel.line(x + 2, y + 12, x + 30, y + 12, P.OCHRE)
    pyxel.rect(x + 1, y + 16, 7, 7, P.OCHRE)
    pyxel.rect(x + 24, y + 16, 7, 7, P.OCHRE)
    picto.person(x + 16, y + 30, P.OCHRE)
    picto.icon('mountain', x + 2, y + 14, 0.5)


@picture('黑')
def _(x: int, y: int) -> None:
    picto.swatch(x, y, P.INK)


@picture('锻炼')
def _(x: int, y: int) -> None:
    picto.person(x + 16, y + 30, P.VERMILION, arm='wide')
    pyxel.line(x + 8, y + 6, x + 24, y + 6, P.STONE)


@picture('身体')
def _(x: int, y: int) -> None:
    pyxel.circ(x + 16, y + 6, 4, P.PEACH)
    pyxel.rect(x + 12, y + 11, 9, 11, P.PEACH)
    pyxel.line(x + 12, y + 12, x + 7, y + 20, P.PEACH)
    pyxel.line(x + 20, y + 12, x + 25, y + 20, P.PEACH)
    pyxel.line(x + 14, y + 22, x + 13, y + 30, P.PEACH)
    pyxel.line(x + 18, y + 22, x + 19, y + 30, P.PEACH)


@picture('踢足球')
def _(x: int, y: int) -> None:
    picto.person(x + 10, y + 30, P.DARK_BLUE)
    pyxel.line(x + 11, y + 27, x + 17, y + 24, P.INK)
    picto.icon('ball', x + 16, y + 14, 0.6)


@picture('休息')
def _(x: int, y: int) -> None:
    pyxel.rect(x + 22, y + 6, 3, 24, P.WOOD)
    pyxel.circ(x + 23, y + 6, 7, P.JADE)
    picto.sitting(x + 14, y + 30, P.DARK_BLUE)
    pyxel.text(x + 4, y + 4, 'z', P.STONE)


@picture('她')
def _(x: int, y: int) -> None:
    picto.person(x + 20, y + 30, P.PINK)
    pyxel.line(x + 18, y + 16, x + 23, y + 16, P.INK)
    picto.arrow(x + 4, y + 10, x + 15, y + 16, P.VERMILION)


@sketch('taian_1958')
def _(x: int, y: int) -> None:
    kit.canvas(pyxel)
    pyxel.tri(x + 10, y + 34, x + 44, y + 6, x + 76, y + 34, P.STONE)
    pyxel.tri(x + 34, y + 16, x + 44, y + 6, x + 52, y + 14, P.WHITE)
    for bx in range(4, 76, 12):
        pyxel.rect(x + bx, y + 30, 10, 10, P.PAPER)
        pyxel.rectb(x + bx, y + 30, 10, 10, P.INK)
        pyxel.line(x + bx - 1, y + 30, x + bx + 10, y + 30, P.INK)


words.add('''
出租车 — такси
司机 — водитель
现在 — сейчас
下午 — после полудня
今天 — сегодня
明天 — завтра
晚上 — вечер
早上 — утро
宾馆 — гостиница
银行 — банк
饭馆 — ресторан
商店 — магазин
地图 — карта
街道 — улица
房间 — комната
电梯 — лифт
电视 — телевизор
空调 — кондиционер
冰箱 — холодильник
天气 — погода
米饭 — рис
面条 — лапша
鸡蛋 — яйцо
羊肉 — баранина
筷子 — палочки
盘子 — тарелка
啤酒 — пиво
饮料 — напиток
蛋糕 — торт
西瓜 — арбуз
香蕉 — банан
水果 — фрукты
新鲜 — свежий
雨伞 — зонт
衣服 — одежда
帽子 — шапка
熊猫 — панда
爸爸 — папа
女儿 — дочь
生日 — день рождения
快乐 — радостный
高兴 — рад
朋友 — друг
认识 — знать (кого-то)
家人 — семья
对不起 — извините
没关系 — ничего страшного
但是 — но
知道 — знать
可以 — можно
工作 — работать
喜欢 — нравиться
一共 — всего
服务员 — официант
信用卡 — кредитная карта
报纸 — газета
一下 — чуть-чуть (смягчает)
身体 — тело, здоровье
锻炼 — тренироваться
踢足球 — играть в футбол
重要 — важный
''')

hints.add(lambda s: s.scene == '2a' and not s.on('taxi_ready'),
          'Таксист у машины. Куда ехать? Покажите ему конверт с адресом — выберите 信 в сумке.')
hints.add(lambda s: s.scene == '2a' and not s.on('taxi_paid'),
          'Таксист назвал цену — 十五块. Отдайте ему деньги (钱).')
hints.add(lambda s: s.scene == '2b' and not s.has('keycard') and not s.on('checkin_asked'),
          'Администратор спросит, будете ли вы жить в гостинице. «Да» — повтор глагола: 住 или 要.')
hints.add(lambda s: s.scene == '2b' and not s.has('keycard') and not s.on('checkin_passport'),
          'Администратор просит паспорт (护照).')
hints.add(lambda s: not s.has('keycard') and s.on('room_price') and s.coins < 300 and not s.on('bank_done'),
          'Номер стоит 三百块 — больше, чем у меня есть. Банк (银行) рядом: на улице слева от гостиницы. Покажите кассиру карту.')
hints.add(lambda s: s.scene in ('2b', '2d') and not s.has('keycard') and s.on('room_price'),
          'Отдайте администратору деньги (钱) за номер.')
hints.add(lambda s: not s.on('know_deadline'),
          'Где искать Ли Мина? В конце улицы — храм Дай (岱庙). Спросите смотрителя; в ответ на «你找谁？» можно написать имя с конверта.')
hints.add(lambda s: s.scene != '2c' and s.on('know_deadline') and s.chapter == 2,
          'Пора отдыхать: номер 308, лифт в гостинице. Там кровать.')
hints.add(lambda s: s.scene == '2c' and s.chapter == 2,
          'Кровать справа. Перед сном можно посмотреть телевизор — там прогноз погоды.')

"""Chapter 4 · 红门 «Красные ворота» — the market street, the teahouse, the gate, the tower of immortals."""
from __future__ import annotations

import pyxel

from ...art import kit, picto
from ...art import palette as P
from ...art.pictures import icon_for, picture
from ...art.sketches import sketch
from ...core.numerals import from_hanzi, to_hanzi
from ...core.phrases import normalize
from ...core.puzzles import Haggle
from ...core.types import ActorDef, ExitDef, HotspotDef, ItemDef, PageDef, SceneDef, SceneLook, ScriptContext, SignDef, TextDef
from .. import hints, items, pages, texts, words
from ..world import register
from ._common import cycle, fig, no, pay, yes

# ---------------------------------------------------------------- items and texts

items.add(
    ItemDef('medicine', '药', 'medicine', 'Коробочка таблеток от боли в суставах.'),
    ItemDef('pancake', '煎饼', 'pancake', 'Тонкий хрустящий блин тайшаньского теста, свёрнутый в трубочку.'),
    ItemDef('stick', '登山杖', 'stick', 'Складная палка для подъёма. Выторговал сам!'),
    ItemDef('gate_ticket', '门票', 'ticket', 'Входной билет на гору Тайшань.'),
)

texts.add(
    TextDef(
        'diary_6', 'diary', 'Дневник деда · 6',
        '今天李明带我爬泰山。\n我们在红门的茶馆喝茶，吃了泰山煎饼，非常好吃。\n'
        '路上有很多挑山工。他们每天挑一百多公斤的东西上山。\n李明说："我以后也想当挑山工，因为我喜欢山。"',
        '«Сегодня Ли Мин повёл меня на Тайшань. У Красных ворот пили чай и ели тайшаньские блины — очень вкусно. '
        'По дороге много носильщиков: каждый день они несут наверх больше ста килограммов. '
        'Ли Мин сказал: „Потом я тоже хочу стать носильщиком, потому что люблю гору“».',
        chapter=4, date='一九五九年十月一号', sketch='porters_1959',
    ),
    TextDef(
        'diary_7', 'diary', 'Дневник деда · 7',
        '春节以前，李先生教我们写对联。\n他说，对联有两句：上一句和下一句字数一样，意思相对。\n'
        '我写了"山高"，李明写了"水长"。\n李先生笑了："很好！你们两个人就是一对对联。"',
        '«Перед Праздником Весны учитель Ли учил нас писать парные надписи. Он сказал: в них две строки, '
        'верхняя и нижняя, одинаковой длины и противоположные по смыслу. Я написал „гора высока“, Ли Мин — „река длинна“. '
        'Учитель засмеялся: „Прекрасно! Вы двое и есть пара надписей“».',
        chapter=4, date='一九六零年一月二十号', sketch='couplets',
    ),
    TextDef(
        'diary_8', 'diary', 'Дневник деда · 8',
        '李先生给我讲了马良的故事。\n马良有一支神笔，他画什么，什么就变成真的。\n'
        '李先生说："笔不神，心才神。你心里明白的字，笔才会写。"\n我不太明白。可是我相信他。',
        '«Учитель Ли рассказал мне историю Ма Ляна. У Ма Ляна была волшебная кисть: что он нарисует, то становится настоящим. '
        'Учитель сказал: „Волшебна не кисть, а сердце. Кисть напишет только тот знак, который понятен сердцу“. '
        'Я не очень понял. Но я ему верю».',
        chapter=4, date='一九六零年三月五号', sketch='magic_brush',
    ),
    TextDef(
        'legend_cangjie', 'book', 'Легенда о Цан Цзе',
        '仓颉造字\n很久很久以前，世界上没有字。\n黄帝有一个聪明的史官，他叫仓颉。\n'
        '有一天，仓颉在雪地上看见了鸟和动物的脚印。\n他发现：每一种动物的脚印都不一样！\n'
        '他想：如果每一个东西都有自己的样子，我们就能把它画下来。\n他画了山，画了水，画了日和月……\n这就是最早的汉字。',
        'Цан Цзе создаёт письмо. Давным-давно в мире не было письменности. У Жёлтого императора был умный летописец Цан Цзе. '
        'Однажды он увидел на снегу следы птиц и зверей и понял: у каждого зверя следы свои! Он подумал: если у каждой вещи '
        'свой облик, её можно нарисовать. Он нарисовал гору, воду, солнце и луну… Так появились первые иероглифы.',
        chapter=4,
    ),
    TextDef(
        'legend_maliang', 'book', 'Легенда о Ма Ляне',
        '神笔马良\n以前有一个孩子，叫马良。他很喜欢画画，可是他家没有钱买笔。\n'
        '有一天晚上，一个白头发的老人送给他一支笔。\n马良用这支笔画了一只鸟，鸟突然飞起来了！\n'
        '他画了一条鱼，鱼就在河里游起来了。\n马良明白了：这是一支神笔！\n'
        '他用神笔帮助村子里的人：他画水，画牛，画灯……\n他从来不为自己画。',
        'Волшебная кисть Ма Ляна. Жил мальчик Ма Лян, он любил рисовать, но семье не на что было купить кисть. '
        'Однажды ночью седой старик подарил ему кисть. Ма Лян нарисовал птицу — и птица вдруг взлетела! Нарисовал рыбу — '
        'и она поплыла по реке. Ма Лян понял: кисть волшебная. Он помогал ею односельчанам: рисовал воду, быков, фонари… '
        'И никогда не рисовал для себя.',
        chapter=4,
    ),
)

# ---------------------------------------------------------------- 4a · the market street


def market_look(s) -> SceneLook:
    return SceneLook('golden')


def market_art(s, look: SceneLook) -> None:
    c = kit.C
    kit.sky([(P.LIGHT_BLUE, 40), (P.MIST, 30), (P.WHITE, 40)])
    kit.ridge(70, 10, 30, 91, P.PERIWINKLE, peaks=[(200, 54, 140)])
    kit.ridge(96, 8, 20, 92, P.MOSS)
    for x, h in ((188, 22), (248, 26)):
        kit.pine(x, 96, h, seed=x)
    # the red gate far up the street
    kit.gate_tower(196, 96, 48, 26, P.VERMILION)
    kit.stairs(220, 150, 60, 220, 96, 22, P.GREY, P.STONE, steps=10)
    kit.ground(122, P.PEACH, P.OCHRE, seed=93, density=0.03)
    # the stick and hat stall
    c.rect(4, 80, 64, 44, P.PAPER)
    kit.banner(0, 72, 72, 10, P.VERMILION)
    for i in range(6):
        c.line(12 + i * 5, 96, 14 + i * 5, 122, P.WOOD)
    c.rect(8, 112, 34, 12, P.OCHRE)
    for i, col in enumerate((P.YELLOW, P.JADE, P.VERMILION)):
        c.elli(46 + i * 7, 88, 8, 4, col)
    # the pancake cart
    c.rect(78, 110, 50, 16, P.WOOD)
    c.circ(84, 128, 4, P.INK)
    c.circ(122, 128, 4, P.INK)
    c.elli(88, 104, 30, 8, P.INK)
    c.elli(90, 105, 26, 6, P.YELLOW)
    kit.banner(76, 80, 54, 10, P.DARK_BLUE)
    # the pharmacy
    c.rect(134, 70, 54, 54, P.WHITE)
    kit.roof(131, 70, 60, 7, P.INK)
    c.rect(142, 94, 16, 30, P.LIGHT_BLUE)
    c.rect(166, 90, 16, 14, P.LIGHT_BLUE)
    c.rect(170, 78, 8, 3, P.JADE)
    c.rect(172, 76, 3, 8, P.JADE)
    # the teahouse front
    c.rect(252, 64, 68, 60, P.OCHRE)
    kit.roof(248, 64, 76, 9, P.INK, P.STONE)
    c.rect(270, 92, 22, 32, P.INK)
    c.rect(270, 92, 22, 2, P.WOOD)
    kit.lantern(262, 74)
    kit.lantern(302, 74)
    kit.window(298, 88, 14, 12, True)
    kit.path_band([(0, 164), (160, 166), (320, 164)], 14, P.PAPER, P.OCHRE)


def market_anim(s, look: SceneLook, frame: int) -> None:
    kit.canvas(pyxel)
    for i in range(3):
        y = 100 - (frame // 3 + i * 7) % 18
        pyxel.pset(96 + i * 6 + int(pyxel.sin(frame * 4 + i * 80) * 2), y, P.MIST)
    kit.canvas(None)


async def market_enter(c: ScriptContext) -> None:
    if c.flag('ch4'):
        return
    c.set('ch4')
    await c.chapter(4)
    await c.narrate('Улица у подножия. Лавки, флажки, запах жареного теста. Вверху, над ступенями, — красная стена с воротами.')
    await c.narrate('Уже после полудня. До ночи надо быть у Средних ворот.')


def _count(answer: str) -> int | None:
    digits = ''.join(ch for ch in normalize(answer) if ch in '零一二两三四五六七八九十百')
    return from_hanzi(digits) if digits else None


CARGO = [
    {'zh': '水　十瓶', 'icon': 'bottle', 'n': 10, 'options': [6, 10, 14]},
    {'zh': '米　五公斤', 'icon': 'sack', 'n': 5, 'options': [3, 8, 5]},
    {'zh': '运动鞋　两双', 'icon': 'shoes', 'n': 2, 'options': [4, 2, 1]},
    {'zh': '书　三本', 'icon': 'book', 'n': 3, 'options': [3, 5, 2]},
]


async def porter_talk(c: ScriptContext) -> None:
    if c.flag('porter_medicine'):
        if not c.flag('cargo_done'):
            await porter_list(c)
        return
    if not c.flag('porter_met'):
        await c.say('porter', '哎哟……我的腿很疼。')
        answer = await c.ask('porter', '你是医生吗？')
        if yes(answer):
            await c.say('porter', '真的？你不像医生。哈哈！')
        else:
            await c.say('porter', '不是？没关系。')
        await c.say('porter', '我老了。以前我一天上山两次，现在一次也很累。')
        await c.say('porter', '药店就在那儿，可是我走不动了。我需要休息一下。')
        c.set('porter_met')
        return
    await c.say('porter', '我的腿很疼……药店就在那儿。')


async def porter_item(c: ScriptContext, item: str) -> bool:
    if item == 'medicine' and not c.flag('porter_medicine'):
        c.take('medicine')
        c.set('porter_medicine')
        await c.narrate('Старик запивает таблетку чаем из бутылки и растирает колено.')
        await c.say('porter', '谢谢你！吃了药，舒服多了。')
        await c.say('porter', '你是好人。我姓赵，大家都叫我老赵。')
        answer = await c.ask('porter', '你要去哪儿？')
        a = normalize(answer)
        if '中天门' in a or '李' in a or '茶馆' in a:
            await c.say('porter', '中天门？我今天也去中天门！我给李家茶馆送东西。')
        else:
            await c.say('porter', '我今天去中天门，给李家茶馆送东西。')
        await c.say('porter', '李明是我的老朋友！我们一起当了四十年挑山工。')
        await porter_list(c)
        return True
    if item == 'pancake':
        c.take('pancake')
        await c.say('porter', '煎饼！谢谢！我正饿呢。')
        return True
    if item == 'photo' or item == 'old_photo':
        await c.say('porter', '这是李明！那时候他真年轻啊！')
        return True
    return False


async def porter_list(c: ScriptContext) -> None:
    await c.say('porter', '可是我的眼睛不好，看不清楚这个单子。你帮我看看，好吗？')
    lines = ['单子'] + [r['zh'] for r in CARGO]
    ok = await c.puzzle('cargo', rows=CARGO, lines=lines, title='单子')
    if not ok:
        await c.say('porter', '没关系，你慢慢看。')
        return
    c.set('cargo_done')
    await c.say('porter', '好！都对了！十瓶水，五公斤米，两双运动鞋，三本书。')
    if c.has('suitcase'):
        await c.say('porter', '你的行李箱很重吧？我帮你拿到中天门，给李家。')
        c.take('suitcase')
        c.set('suitcase_porter')
        await c.narrate('Лао Чжао цепляет мой чемодан к коромыслу, будто он ничего не весит.')
    await c.say('porter', '我们挑山工一般一天上山一次，一次一百公斤。习惯了！')
    await c.say('porter', '你先走，我马上就来。我们在中天门见面！')
    await c.move('porter', 230)
    await c.move('porter', 222, 96)
    c.set('porter_gone')


async def pharmacist_talk(c: ScriptContext) -> None:
    if c.has('medicine') or c.flag('porter_medicine'):
        await cycle(c, 'pharm_n', 'pharmacist', ['你要注意身体！', '医院在城里，山上没有医院。', '希望你的朋友快点儿好！'])
        return
    if c.flag('med_order'):
        await c.say('pharmacist', '三十块。')
        return
    await c.say('pharmacist', '你好！你生病了吗？')
    answer = await c.ask('pharmacist', '你哪儿不舒服？感冒？发烧？头疼？')
    a = normalize(answer)
    if '腿' in a or '疼' in a:
        await c.say('pharmacist', '腿疼？这个药很好。三十块。')
        c.set('med_order')
    elif '感冒' in a or '发烧' in a:
        await c.say('pharmacist', '感冒了？多喝水，多休息。你不需要药！')
    else:
        await c.say('pharmacist', '头疼？腿疼？你说吧。')


async def pharmacist_item(c: ScriptContext, item: str) -> bool:
    if item == 'money' and c.flag('med_order') and not c.has('medicine'):
        if await pay(c, 'pharmacist', 30, item):
            c.give('medicine')
            await c.say('pharmacist', '一天吃两次。希望你的朋友快点儿好！')
            await c.say('pharmacist', '山上没有医院，你们要小心。')
        return True
    return False


async def pancake_talk(c: ScriptContext) -> None:
    if c.flag('pancake_order'):
        await c.say('pancake', f'{to_hanzi(int(c.flag("pancake_order")) * 5)}块。')
        return
    await c.say('pancake', '泰山煎饼！很有名！五块一个，又甜又香！')
    answer = await c.ask('pancake', '你要几个？')
    n = _count(answer)
    if n and 1 <= n <= 5:
        c.set('pancake_order', n)
        await c.say('pancake', f'{to_hanzi(n)}个，{to_hanzi(n * 5)}块！')
    elif no(answer):
        await c.say('pancake', '不要？你不饿吗？')
    else:
        await c.say('pancake', '一个？两个？')


async def pancake_item(c: ScriptContext, item: str) -> bool:
    n = int(c.flag('pancake_order') or 0)
    if item == 'money' and n:
        if await pay(c, 'pancake', n * 5, item):
            c.give('pancake')
            c.set('pancake_order', 0)
            await c.say('pancake', '吃饱了才能爬山！')
        return True
    return False


STICK_FLOOR = 30


async def stick_talk(c: ScriptContext) -> None:
    if c.has('stick'):
        await c.say('seller', '上山的时候小心！')
        return
    price = int(c.flag('stick_price') or 60)
    if c.flag('stick_deal'):
        await c.say('seller', f'{to_hanzi(price)}块，你给钱吧。')
        return
    await c.say('seller', '登山杖！上山的时候很有用！')
    answer = await c.ask('seller', f'你要吗？{to_hanzi(price)}块。')
    a = normalize(answer)
    if no(answer):
        await c.say('seller', '不要？好吧。')
        return
    n = _count(answer)
    if n is None:
        if '贵' in a:
            price = max(STICK_FLOOR + 10, price - 10)
            c.set('stick_price', price)
            await c.say('seller', f'太贵？那……{to_hanzi(price)}块，怎么样？')
        else:
            c.set('stick_deal')
            await c.say('seller', f'好！{to_hanzi(price)}块！')
        return
    h = Haggle(price, STICK_FLOOR, step=10)
    result = h.offer(n)
    c.set('stick_price', h.asking)
    if result == 'high':
        c.set('stick_deal')
        await c.say('seller', f'你真好！不用那么多，{to_hanzi(price)}块就行。')
    elif result == 'deal':
        c.set('stick_deal')
        c.set('stick_price', n)
        await c.say('seller', f'好吧好吧，{to_hanzi(n)}块！这已经很便宜了！')
    elif result == 'low':
        await c.say('seller', '太便宜了！不行，不行！')
    else:
        await c.say('seller', f'{to_hanzi(h.asking)}块，不能再便宜了！')


async def stick_item(c: ScriptContext, item: str) -> bool:
    if item == 'money' and c.flag('stick_deal') and not c.has('stick'):
        if await pay(c, 'seller', int(c.flag('stick_price') or 60), item):
            c.give('stick')
            await c.say('seller', '谢谢！一路平安！')
        return True
    return False


register(
    SceneDef(
        id='4a', chapter=4, title='Улица у Красных ворот', zh='红门路',
        art=market_art, anim=market_anim, look=market_look,
        path=[(8, 164), (160, 166), (312, 164)],
        entries={'bottom': 20, 'teahouse': 280, 'gate': 222},
        actors=[
            ActorDef('seller', 'Продавец палок', fig(P.DARK_BLUE, P.WHITE, 'jacket', 'cap'), 40, 150, 'right', on_talk=stick_talk, on_item=stick_item),
            ActorDef('pancake', 'Блинщица', fig(P.WHITE, P.VERMILION, 'jacket', 'bun'), 120, 142, 'left', stand_at=110,
                     on_talk=pancake_talk, on_item=pancake_item),
            ActorDef('pharmacist', 'Аптекарь', fig(P.WHITE, P.JADE, 'robe', 'short', glasses=True), 164, 146, 'left', stand_at=160,
                     on_talk=pharmacist_talk, on_item=pharmacist_item),
            ActorDef('porter', 'Старый носильщик', fig(P.STONE, P.OCHRE, 'jacket', 'straw', kind='old', pose='sit', prop='pole'), 206, 150, 'left',
                     visible=lambda s: not s.on('porter_gone'), stand_at=196, on_talk=porter_talk, on_item=porter_item),
        ],
        signs=[
            SignDef('pharmacy', '药店', 142, 72, 'lit'),
            SignDef('pancake', '泰山煎饼', 78, 80, 'banner'),
            SignDef('sticks', '登山杖', 8, 72, 'banner'),
            SignDef('teahouse', '红门茶馆', 256, 48, 'plaque'),
            SignDef('pancake_price', '五块', 80, 112, 'tag'),
        ],
        exits=[
            ExitDef('bottom', '3d', 'village', (0, 100, 10, 70), 'left', 12, 'Арка Дайцзун'),
            ExitDef('teahouse', '4b', 'door', (270, 92, 22, 32), 'up', 280, 'Чайная'),
            ExitDef('gate', '4c', 'bottom', (206, 90, 30, 40), 'up', 222, 'К воротам'),
        ],
        on_enter=market_enter,
        diary=('diary_6',),
        music='village',
    )
)

# ---------------------------------------------------------------- 4b · the teahouse


def teahouse_look(s) -> SceneLook:
    return SceneLook('golden')


def teahouse_art(s, look: SceneLook) -> None:
    c = kit.C
    c.rect(0, 0, 320, 180, P.OCHRE)
    kit.panel_wall(0, 110, P.PEACH, P.WOOD)
    for x in range(0, 320, 40):
        c.rect(x, 0, 4, 110, P.WOOD)
    kit.tiles(110, P.WOOD, P.OCHRE, 14)
    # the stage of the storyteller
    c.rect(20, 96, 80, 14, P.LACQUER)
    c.rect(38, 84, 30, 12, P.WOOD)
    kit.banner(24, 20, 72, 34, P.VERMILION)
    # the counter
    kit.counter(214, 94, 90, 26)
    for i in range(5):
        c.rect(222 + i * 16, 40, 10, 14, (P.JADE, P.PAPER, P.YELLOW, P.PAPER, P.JADE)[i])
        c.rect(222 + i * 16, 54, 10, 2, P.WOOD)
    c.rect(214, 58, 90, 3, P.WOOD)
    # the television
    c.rect(118, 18, 44, 30, P.INK)
    c.rect(121, 21, 38, 24, P.DARK_BLUE if not s.on('tv4_on') else P.LIGHT_BLUE)
    # tables with cups, people sit beside them
    for tx, tw in ((126, 26), (190, 28), (270, 18)):
        c.rect(tx, 134, tw, 5, P.LACQUER)
        c.line(tx, 134, tx + tw - 1, 134, P.ORANGE)
        c.rect(tx + 3, 139, 3, 13, P.LACQUER)
        c.rect(tx + tw - 6, 139, 3, 13, P.LACQUER)
        c.rect(tx + 4, 130, 5, 4, P.WHITE)
        c.rect(tx + tw - 9, 130, 5, 4, P.WHITE)
    # the door
    c.rect(0, 70, 14, 64, P.INK)
    kit.lantern(40, 0)
    kit.lantern(200, 0)
    kit.lantern(290, 0)


async def teahouse_enter(c: ScriptContext) -> None:
    if c.flag('teahouse_in'):
        return
    c.set('teahouse_in')
    await c.narrate('Чайная. Шумно: звенят чашки, в углу бормочет телевизор, на помосте старик с веером собирается что-то рассказывать.')


async def hostess_talk(c: ScriptContext) -> None:
    if c.flag('tray_done'):
        await cycle(c, 'host_n', 'hostess', ['你吃饱了吗？', '李家的茶比我们的好喝，哈哈！', '晚上山上冷，多喝热茶！'])
        return
    if not c.flag('tea_ordered'):
        await c.say('hostess', '欢迎！请坐！桌子和椅子都在那儿。')
        answer = await c.ask('hostess', '你想喝什么？')
        a = normalize(answer)
        if '咖啡' in a:
            await c.say('hostess', '对不起，我们没有咖啡。喝茶吧！')
        elif '茶' in a:
            await c.say('hostess', '好！一杯茶。')
        else:
            await c.say('hostess', '那……喝茶吧！我们的茶很好喝。')
        c.set('tea_ordered')
    await c.say('hostess', '哎呀，今天客人太多了！我是这儿的服务员，可是今天只有我一个人！')
    answer = await c.ask('hostess', '你能帮我送一下吗？')
    if no(answer):
        await c.say('hostess', '好吧，没关系。')
        return
    orders = [
        {'zh': '一号桌：两杯茶', 'want': {'tea': 2}},
        {'zh': '二号桌：一碗面条，一杯牛奶', 'want': {'noodles': 1, 'milk': 1}},
        {'zh': '三号桌：一瓶啤酒，一碗米饭', 'want': {'beer': 1, 'rice': 1}},
    ]
    ok = await c.puzzle('tray', orders=orders, lines=[o['zh'] for o in orders])
    if not ok:
        await c.say('hostess', '没关系，我自己来吧。')
        return
    c.set('tray_done')
    await c.say('hostess', '谢谢你帮忙！你帮了我很大的忙！今天的茶不要钱！')
    await c.say('hostess', '把杯子给我吧。')
    await c.say('hostess', '你去中天门吗？我小时候，李先生教过我写字。')
    await c.say('hostess', '春节的时候，他给我们写对联，写得非常好！')
    c.unlock('diary_7')


async def storyteller_talk(c: ScriptContext) -> None:
    step = int(c.flag('story_step') or 0)
    if step == 0:
        await c.say('storyteller', '安静！安静！我给大家讲一个故事。')
        await c.read('legend_cangjie')
        answer = await c.ask('storyteller', '仓颉看见了什么？')
        a = normalize(answer)
        if '鸟' in a or '脚' in a or '动物' in a:
            await c.say('storyteller', '对！鸟和动物的脚印！你听得很认真！')
        else:
            await c.say('storyteller', '你没听清楚？他看见了鸟和动物的脚印。')
        c.set('story_step', 1)
        return
    if step == 1:
        await c.say('storyteller', '再讲一个！这是我最喜欢的故事。')
        await c.read('legend_maliang')
        answer = await c.ask('storyteller', '马良画了一只鸟，鸟怎么了？')
        if '飞' in normalize(answer):
            await c.say('storyteller', '对！鸟飞起来了！')
        else:
            await c.say('storyteller', '鸟飞起来了！')
        c.set('story_step', 2)
        if c.has('brush'):
            await c.narrate('Сказитель замечает кисть у меня в сумке и замолкает.')
            await c.say('storyteller', '你的笔……跟马良的笔一样！')
            await c.say('storyteller', '我听说，中天门李家以前也有一支这样的笔。可是很多年以前，它不见了……')
        c.unlock('diary_8')
        return
    await cycle(c, 'st_n', 'storyteller', ['明天我讲"后羿射日"的故事，你来听吧！', '故事里有很多历史，也有很多文化。'])


async def manager_talk(c: ScriptContext) -> None:
    await cycle(c, 'mgr_n', 'manager', ['我是一个公司的经理。', '我同事都在上班，我请假了，来爬泰山！',
                                        '我最近太忙了，每天都有会议。', '我的办公室在北京，那儿没有山。', '我住在山下的饭店。'])


async def bride_talk(c: ScriptContext) -> None:
    await cycle(c, 'bride_n', 'bride', ['我们上个星期结婚了！', '我们是来旅游的。', '他送给我一个照相机！', '他不会跳舞，哈哈！'])


async def groom_talk(c: ScriptContext) -> None:
    if c.flag('photo_taken'):
        await c.say('groom', '照得真好！谢谢！')
        return
    answer = await c.ask('groom', '你能帮我们照相吗？')
    if no(answer):
        await c.say('groom', '好吧……')
        return
    c.set('photo_taken')
    await c.narrate('Фотографирую молодожёнов у окна, за которым гора.')
    await c.say('groom', '照得真好！谢谢！')


async def student_talk(c: ScriptContext) -> None:
    await cycle(c, 'stu_n', 'student4', ['我在上网，看电影。', '这儿的网太慢了！', '我的电脑没电了……'])


async def tv4(c: ScriptContext) -> None:
    c.set('tv4_on')
    await c.say('tv4', '现在是新闻节目。今天泰山的天气：晴，晚上山上有雨，还刮风。')
    await c.say('tv4', '明天是阴天。')


register(
    SceneDef(
        id='4b', chapter=4, title='Чайная у Красных ворот', zh='茶馆',
        art=teahouse_art, look=teahouse_look,
        path=[(12, 166), (308, 166)],
        entries={'door': 20},
        actors=[
            ActorDef('hostess', 'Хозяйка', fig(P.VERMILION, P.WHITE, 'dress', 'bun'), 256, 150, 'left', stand_at=244,
                     on_talk=hostess_talk),
            ActorDef('storyteller', 'Сказитель', fig(P.NAVY, P.GOLD, 'robe', 'scholar', kind='old', beard=True, prop='fan'), 54, 96, 'right',
                     stand_at=60, on_talk=storyteller_talk),
            ActorDef('manager', 'Человек в костюме', fig(P.INK, P.WHITE, 'jacket', 'short', glasses=True, pose='sit'), 116, 152, 'right',
                     stand_at=106, on_talk=manager_talk),
            ActorDef('bride', 'Молодая жена', fig(P.PINK, P.WHITE, 'dress', 'ponytail', pose='sit'), 180, 152, 'right',
                     stand_at=172, on_talk=bride_talk),
            ActorDef('groom', 'Молодой муж', fig(P.DARK_BLUE, P.WHITE, 'jacket', 'short', pose='sit'), 228, 152, 'left',
                     stand_at=236, on_talk=groom_talk),
            ActorDef('student4', 'Студент с ноутбуком', fig(P.JADE, P.WHITE, 'jacket', 'short', glasses=True, pose='sit'), 298, 152, 'left',
                     stand_at=300, on_talk=student_talk),
        ],
        hotspots=[
            HotspotDef('tv4', 'Телевизор', (118, 18, 44, 30), stand_at=140, on_click=tv4),
        ],
        signs=[
            SignDef('menu4', '茶　十块\n面条　十五\n煎饼　五块', 222, 64, 'paper'),
            SignDef('story', '说书', 44, 26, 'banner'),
        ],
        exits=[ExitDef('door', '4a', 'teahouse', (0, 70, 14, 64), 'left', 14, 'Улица')],
        on_enter=teahouse_enter,
        music='teahouse',
    )
)

# ---------------------------------------------------------------- 4c · the Red Gate


def gate_look(s) -> SceneLook:
    return SceneLook('golden')


def gate_art(s, look: SceneLook) -> None:
    c = kit.C
    kit.sky([(P.LIGHT_BLUE, 40), (P.MIST, 30), (P.WHITE, 40)])
    kit.ridge(60, 10, 30, 101, P.PERIWINKLE, peaks=[(170, 50, 150)])
    kit.ridge(88, 8, 20, 102, P.MOSS)
    kit.ground(118, P.PAPER, P.MIST, seed=103, density=0.03)
    # the long red wall with the gate
    kit.wall(0, 64, 320, 54, P.VERMILION, P.LACQUER, P.INK)
    kit.gate_tower(128, 118, 64, 54, P.VERMILION, open_=True)
    kit.stairs(160, 150, 70, 160, 118, 40, P.GREY, P.STONE, steps=6)
    # the stone arch in front
    kit.paifang(40, 150, 60, 52, P.STONE, P.PLUM, P.INK, P.LACQUER)
    # the ticket booth
    c.rect(236, 110, 44, 40, P.PAPER)
    kit.roof(232, 110, 52, 7, P.INK)
    c.rect(244, 120, 28, 14, P.LIGHT_BLUE)
    c.rect(244, 134, 28, 3, P.WOOD)
    # the path to the tower on the right
    kit.path_band([(290, 118), (320, 110)], 10, P.PAPER)
    kit.path_band([(0, 164), (160, 168), (320, 164)], 14, P.PAPER, P.OCHRE)
    for x in (12, 306):
        kit.cypress(x, 150, 34)


async def gate_enter(c: ScriptContext) -> None:
    if c.flag('gate_in'):
        return
    c.set('gate_in')
    await c.narrate('Красные ворота. Отсюда начинается настоящая тропа: шесть тысяч ступеней до вершины.')


async def ticket_talk(c: ScriptContext) -> None:
    if c.has('gate_ticket') or c.flag('redgate_ok'):
        await c.say('ticket', '一路平安！')
        return
    if c.flag('ticket_asked'):
        await c.say('ticket', '一百一十五块。')
        return
    answer = await c.ask('ticket', '你好！门票一百一十五块，学生半价。你是学生吗？')
    if yes(answer):
        await c.say('ticket', '请给我看一下你的学生证。')
        await c.narrate('Студенческого у меня нет.')
        await c.say('ticket', '没有？对不起，那不行。一百一十五块。')
    else:
        await c.say('ticket', '好，一百一十五块。')
    c.set('ticket_asked')


async def ticket_item(c: ScriptContext, item: str) -> bool:
    if item == 'money' and c.flag('ticket_asked') and not c.has('gate_ticket'):
        if await pay(c, 'ticket', 115, item):
            c.give('gate_ticket')
            await c.say('ticket', '这是你的门票。一路平安！')
        return True
    return False


async def guard_talk(c: ScriptContext) -> None:
    if c.flag('redgate_ok'):
        await cycle(c, 'guard_n', 'guard', ['天黑以前，你必须到中天门。', '今天风很大，你要多穿衣服！'])
        return
    await c.say('guard', '你的门票呢？')


async def guard_item(c: ScriptContext, item: str) -> bool:
    if item == 'gate_ticket':
        c.set('redgate_ok')
        await c.say('guard', '好，请进！')
        await c.say('guard', '上山的时候要注意，别离开大路！')
        await c.say('guard', '天黑以前，你必须到中天门。今天风很大！')
        return True
    return False


async def guide_talk(c: ScriptContext) -> None:
    await cycle(c, 'guide_n', 'guide', ['小姐，我们要二十张门票！', '大家看，这是"孔子登临处"。两千五百多年以前，孔子从这儿上山。',
                                        '孔子是中国历史上最有名的老师。', '大家跟我走，别走错了！'])


async def gate_up(c: ScriptContext) -> bool:
    if c.flag('redgate_ok'):
        await c.narrate('Прохожу через Красные ворота. Ступени, кипарисы, и дальше — вверх, вверх.')
        return True
    await c.say('guard', '你的门票呢？')
    return False


register(
    SceneDef(
        id='4c', chapter=4, title='Красные ворота', zh='红门',
        art=gate_art, look=gate_look,
        path=[(8, 164), (160, 168), (312, 164)],
        entries={'bottom': 20, 'tower': 300, 'up': 160},
        actors=[
            ActorDef('ticket', 'Кассирша', fig(P.DARK_BLUE, P.WHITE, 'uniform', 'bun'), 258, 132, 'left', stand_at=258,
                     on_talk=ticket_talk, on_item=ticket_item),
            ActorDef('guard', 'Контролёр', fig(P.NAVY, P.GOLD, 'uniform', 'police'), 196, 156, 'left', on_talk=guard_talk, on_item=guard_item),
            ActorDef('guide', 'Экскурсовод с флажком', fig(P.YELLOW, P.VERMILION, 'jacket', 'cap', prop='fan'), 108, 160, 'right',
                     on_talk=guide_talk),
        ],
        signs=[
            SignDef('gate', '红门', 146, 70, 'plaque'),
            SignDef('confucius', '孔子登临处', 38, 88, 'plaque'),
            SignDef('ticket_sign', '售票处', 238, 100, 'blue'),
        ],
        exits=[
            ExitDef('bottom', '4a', 'gate', (0, 100, 10, 70), 'left', 12, 'Улица'),
            ExitDef('up', '5a', 'bottom', (146, 80, 28, 38), 'up', 160, 'Вверх по тропе', guard=gate_up),
            ExitDef('tower', '4d', 'gate', (306, 96, 14, 40), 'right', 308, 'Башня'),
        ],
        on_enter=gate_enter,
        music='mountain',
    )
)

# ---------------------------------------------------------------- 4d · the tower of ten thousand immortals


def tower_look(s) -> SceneLook:
    return SceneLook('golden')


def tower_art(s, look: SceneLook) -> None:
    c = kit.C
    kit.sky([(P.LIGHT_BLUE, 40), (P.MIST, 30), (P.WHITE, 40)])
    kit.ridge(56, 10, 30, 111, P.PERIWINKLE, peaks=[(210, 44, 140)])
    kit.ridge(90, 8, 20, 112, P.PINE)
    for x, h in ((22, 40), (48, 30), (272, 36), (300, 44)):
        kit.pine(x, 126, h, seed=x)
    kit.ground(122, P.PAPER, P.MIST, seed=113, density=0.03)
    kit.gate_tower(150, 124, 70, 58, P.VERMILION, open_=True)
    kit.stairs(185, 160, 60, 185, 124, 36, P.GREY, P.STONE, steps=8)
    # the stone with the riddle
    kit.rock(64, 112, 52, 40, P.STONE, P.STONE, P.PLUM)
    kit.path_band([(0, 164), (160, 168), (320, 164)], 14, P.PAPER, P.OCHRE)


async def tower_enter(c: ScriptContext) -> None:
    if c.flag('tower_in'):
        return
    c.set('tower_in')
    await c.narrate('Башня Десяти тысяч бессмертных. Тропа проходит прямо под ней. У дороги — камень с двумя странными знаками.')


async def scholar_talk(c: ScriptContext) -> None:
    if c.flag('chonger_done'):
        await cycle(c, 'sch_n', 'scholar', ['风月无边！', '你是一个聪明的外国人。', '汉字很有意思，对吧？'])
        return
    if not c.flag('riddle_given'):
        await c.say('scholar', '你好！我每天都来看这块石头。')
        answer = await c.ask('scholar', '你看，石头上写的是什么？')
        if '虫' in normalize(answer):
            await c.say('scholar', '对，"虫二"。可是你知道这是什么意思吗？')
        else:
            await c.say('scholar', '是"虫二"两个字。')
        await c.say('scholar', '这是一个字谜。给"虫"和"二"加上边，你就知道了。')
        c.set('riddle_given')
        return
    answer = await c.ask('scholar', '"虫二"是哪两个字？')
    a = normalize(answer)
    if '风' in a and '月' in a:
        c.set('chonger_done')
        await c.say('scholar', '对！是"风月"！风月没有边：风月无边！')
        await c.say('scholar', '意思是：这儿非常漂亮，漂亮得没有边。')
        c.confirm('风')
        await c.narrate('Кисть в сумке шевелится: теперь она знает знак ветра — 风.')
    else:
        await c.say('scholar', '不对。再想想：给"虫"加上边，是什么字？')
        await c.say('scholar', '今天风很大，对吧？')


register(
    SceneDef(
        id='4d', chapter=4, title='Башня бессмертных', zh='万仙楼',
        art=tower_art, look=tower_look,
        path=[(8, 164), (160, 168), (312, 164)],
        entries={'gate': 20},
        actors=[
            ActorDef('scholar', 'Старый книжник', fig(P.GREY, P.NAVY, 'robe', 'scholar', kind='old', beard=True, glasses=True), 128, 160, 'left',
                     on_talk=scholar_talk),
        ],
        hotspots=[
            HotspotDef('stone', 'Камень с надписью', (64, 76, 52, 40), stand_at=96,
                       on_click=lambda c: c.narrate('На камне высечены два знака: 虫二. Насекомое и два? Странно.')),
        ],
        signs=[
            SignDef('tower', '万仙楼', 166, 64, 'plaque'),
            SignDef('riddle', '虫二', 80, 80, 'carved', vertical=True),
        ],
        exits=[ExitDef('gate', '4c', 'tower', (0, 100, 10, 70), 'left', 12, 'Красные ворота')],
        on_enter=tower_enter,
        music='mountain',
    )
)

# ---------------------------------------------------------------- pages, pictures, glossary, hints

pages.add(
    PageDef('pharmacy', 'В аптеке', 4, ('疼', '舒服', '药', '医生', '生病', '感冒'), kind='phrase',
            phrases=('我的腿很疼。', '你哪儿不舒服？', '药店就在那儿', '你是医生吗？', '你生病了吗？', '感冒？发烧？头疼？')),
    PageDef('cargo', 'Список носильщика', 4, ('瓶', '公斤', '双', '本'), kind='icon'),
    PageDef('porter4', 'Лао Чжао', 4, ('一般', '习惯', '马上', '见面', '清楚', '当'), kind='phrase',
            phrases=('我们挑山工一般一天上山一次', '习惯了！', '我马上就来。', '我们在中天门见面！', '看不清楚这个单子', '我们一起当了四十年挑山工。')),
    PageDef('bargain', 'Торг', 4, ('便宜', '怎么样', '不能', '甜', '饱'), kind='phrase',
            phrases=('这已经很便宜了！', '怎么样？', '不能再便宜了！', '又甜又香！', '吃饱了才能爬山！')),
    PageDef('teahouse4', 'В чайной', 4, ('客人', '帮忙', '杯', '碗', '瓶'), kind='phrase',
            phrases=('今天客人太多了！', '谢谢你帮忙！', '两杯茶', '一碗面条', '一瓶啤酒')),
    PageDef('office', 'Человек в костюме', 4, ('公司', '经理', '同事', '上班', '请假', '会议'), kind='phrase',
            phrases=('我是一个公司的经理。', '我是一个公司的经理。', '我同事都在上班', '我同事都在上班', '我请假了', '每天都有会议。')),
    PageDef('modern', 'Техника', 4, ('电脑', '照相机', '电视', '手机'), kind='icon'),
    PageDef('media', 'Новости и кино', 4, ('上网', '电影', '新闻', '节目', '刮风'), kind='phrase',
            phrases=('我在上网，看电影。', '我在上网，看电影。', '现在是新闻节目。', '现在是新闻节目。', '晚上山上有雨，还刮风。')),
    PageDef('couple', 'Молодожёны', 4, ('结婚', '旅游', '照相', '上个星期'), kind='phrase',
            phrases=('我们上个星期结婚了！', '我们是来旅游的。', '你能帮我们照相吗？', '我们上个星期结婚了！')),
    PageDef('legend1', 'Цан Цзе', 4, ('世界', '发现', '脚', '如果', '种', '久'), kind='phrase',
            phrases=('世界上没有字。', '他发现', '鸟和动物的脚印', '如果每一个东西都有自己的样子', '每一种动物的脚印都不一样！', '很久很久以前')),
    PageDef('legend2', 'Ма Лян', 4, ('突然', '起来', '明白', '自己', '飞', '神'), kind='phrase',
            phrases=('鸟突然飞起来了！', '鸟突然飞起来了！', '马良明白了', '他从来不为自己画。', '鸟突然飞起来了！', '这是一支神笔！')),
    PageDef('gate4', 'У ворот', 4, ('门票', '学生', '注意', '离开', '必须', '风')),
    PageDef('guide4', 'Экскурсия', 4, ('孔子', '最有名', '千', '跟'), kind='phrase',
            phrases=('孔子从这儿上山。', '孔子是中国历史上最有名的老师。', '两千五百多年以前', '大家跟我走')),
    PageDef('riddle4', 'Загадка', 4, ('字谜', '加', '边', '哪'), kind='phrase',
            phrases=('这是一个字谜。', '给"虫"和"二"加上边', '风月没有边', '"虫二"是哪两个字？')),
    PageDef('diary6', 'Носильщики', 4, ('挑', '带', '以后', '喜欢山'), kind='phrase',
            phrases=('他们每天挑一百多公斤的东西上山。', '今天李明带我爬泰山。', '我以后也想当挑山工', '因为我喜欢山。')),
    PageDef('diary7', 'Парные надписи', 4, ('对联', '句', '字数', '相对'), kind='phrase',
            phrases=('李先生教我们写对联。', '对联有两句', '字数一样', '意思相对。')),
    PageDef('diary8', 'Волшебная кисть', 4, ('变', '相信', '心', '故事', '讲'), kind='phrase',
            phrases=('什么就变成真的。', '可是我相信他。', '笔不神，心才神。', '马良的故事', '李先生给我讲了马良的故事。')),
)

for w, ic in (('瓶', 'bottle'), ('公斤', 'sack'), ('双', 'shoes'), ('本', 'book'), ('药', 'medicine'), ('煎饼', 'pancake'),
              ('电脑', 'laptop'), ('照相机', 'camera'), ('电视', 'tv'), ('手机', 'phone'), ('门票', 'ticket')):
    icon_for(w, ic)


@picture('学生')
def _(x: int, y: int) -> None:
    picto.icon('book', x + 16, y + 14)
    picto.person(x + 10, y + 30, P.DARK_BLUE)


@picture('注意')
def _(x: int, y: int) -> None:
    pyxel.tri(x + 16, y + 3, x + 3, y + 28, x + 29, y + 28, P.YELLOW)
    pyxel.trib(x + 16, y + 3, x + 3, y + 28, x + 29, y + 28, P.INK)
    pyxel.rect(x + 15, y + 11, 3, 10, P.INK)
    pyxel.rect(x + 15, y + 23, 3, 3, P.INK)


@picture('离开')
def _(x: int, y: int) -> None:
    picto.icon('house', x, y + 12)
    picto.person(x + 24, y + 30, P.DARK_BLUE)
    picto.arrow(x + 18, y + 8, x + 30, y + 8, P.VERMILION)


@picture('必须')
def _(x: int, y: int) -> None:
    picto.clock(x + 12, y + 14, 9, 6, 0, 'hour')
    picto.icon('mountain', x + 16, y + 14)
    pyxel.text(x + 3, y + 25, '!!', P.VERMILION)


@picture('风')
def _(x: int, y: int) -> None:
    for i in range(4):
        yy = y + 6 + i * 6
        pyxel.line(x + 2, yy, x + 22, yy, P.STONE)
        pyxel.circb(x + 24, yy - 2, 2, P.STONE)
    pyxel.tri(x + 26, y + 20, x + 30, y + 30, x + 22, y + 30, P.JADE)


@sketch('porters_1959')
def _(x: int, y: int) -> None:
    for i in range(3):
        bx = x + 12 + i * 24
        by = y + 36 - i * 8
        picto.person(bx, by, P.INK)
        pyxel.line(bx - 8, by - 14, bx + 8, by - 14, P.WOOD)
        pyxel.rect(bx - 10, by - 12, 4, 6, P.STONE)
        pyxel.rect(bx + 6, by - 12, 4, 6, P.STONE)
    pyxel.line(x + 2, y + 42, x + 78, y + 14, P.STONE)


@sketch('couplets')
def _(x: int, y: int) -> None:
    pyxel.rect(x + 30, y + 14, 20, 28, P.LACQUER)
    pyxel.rect(x + 20, y + 6, 6, 36, P.VERMILION)
    pyxel.rect(x + 54, y + 6, 6, 36, P.VERMILION)
    pyxel.rect(x + 26, y + 4, 28, 6, P.VERMILION)
    for i in range(4):
        pyxel.line(x + 22, y + 10 + i * 8, x + 24, y + 13 + i * 8, P.INK)
        pyxel.line(x + 56, y + 10 + i * 8, x + 58, y + 13 + i * 8, P.INK)


@sketch('magic_brush')
def _(x: int, y: int) -> None:
    pyxel.line(x + 20, y + 36, x + 40, y + 12, P.WOOD)
    pyxel.tri(x + 18, y + 38, x + 22, y + 34, x + 16, y + 42, P.INK)
    for i in range(5):
        pyxel.pset(x + 46 + i * 5, y + 10 + (i % 2) * 4, P.GOLD)
    pyxel.line(x + 50, y + 26, x + 56, y + 22, P.INK)
    pyxel.line(x + 56, y + 22, x + 62, y + 26, P.INK)


words.add('''
红门 — Красные ворота
红门路 — улица у Красных ворот
茶馆 — чайная
药店 — аптека
医生 — врач
医院 — больница
生病 — заболеть
感冒 — простуда
发烧 — температура, жар
舒服 — удобно, хорошо (самочувствие)
不舒服 — нездоровится
单子 — список
公斤 — килограмм
运动鞋 — кроссовки
一般 — обычно
习惯 — привыкнуть
马上 — сейчас же
见面 — встретиться
清楚 — ясно, отчётливо
挑山工 — носильщик на горе
煎饼 — блин цзяньбин
便宜 — дешёвый
不能 — нельзя, не может
怎么样 — как? как насчёт?
登山杖 — палка для горных походов
客人 — гость
帮忙 — помочь
服务员 — официант
公司 — компания
经理 — менеджер
同事 — коллега
上班 — ходить на работу
请假 — отпроситься
会议 — совещание
办公室 — офис
最近 — в последнее время
电脑 — компьютер
照相机 — фотоаппарат
上网 — сидеть в интернете
电影 — кино
新闻 — новости
节目 — передача
刮风 — дует ветер
结婚 — жениться, выйти замуж
旅游 — путешествовать
照相 — фотографировать
上个星期 — на прошлой неделе
世界 — мир
发现 — обнаружить
如果 — если
突然 — вдруг
起来 — (вверх, начать)
明白 — понимать
自己 — сам
门票 — входной билет
学生 — студент, ученик
注意 — внимание, следить
离开 — покидать
必须 — обязательно, нужно
孔子 — Конфуций
最有名 — самый знаменитый
字谜 — загадка о знаке
风月 — ветер и луна (красота природы)
风月无边 — красоте нет края
万仙楼 — Башня десяти тысяч бессмертных
对联 — парная надпись
字数 — число знаков
相对 — противоположный
相信 — верить
故事 — история, сказка
喜欢山 — любить гору
''')

hints.add(lambda s: s.scene == '4a' and not s.on('porter_met'),
          'На ступенях отдыхает старый носильщик. Поговорите с ним.')
hints.add(lambda s: s.on('porter_met') and not s.on('med_order') and not s.has('medicine') and not s.on('porter_medicine'),
          'У носильщика болит нога (腿疼). Зайдите в аптеку (药店) и скажите, что болит: «腿疼».')
hints.add(lambda s: s.on('med_order') and not s.has('medicine') and not s.on('porter_medicine'),
          'Аптекарь назвал цену — 三十块. Отдайте ему деньги (钱).')
hints.add(lambda s: s.has('medicine'),
          'Отдайте лекарство (药) старому носильщику.')
hints.add(lambda s: s.on('porter_medicine') and not s.on('cargo_done'),
          'Носильщик плохо видит свой список. Поговорите с ним и сосчитайте для каждой строки нужную груду: число и счётное слово.')
hints.add(lambda s: s.chapter == 4 and not s.has('gate_ticket') and not s.on('redgate_ok'),
          'Чтобы пройти через Красные ворота, нужен билет. Касса (售票处) — справа от ворот.')
hints.add(lambda s: s.has('gate_ticket') and not s.on('redgate_ok'),
          'Покажите билет (门票) контролёру у ворот.')
hints.add(lambda s: s.scene == '4d' and s.on('riddle_given') and not s.on('chonger_done'),
          'Загадка 虫二: если обвести знаки рамкой, получатся два других. Подсказка — погода по телевизору в чайной и девятый месяц.')
hints.add(lambda s: s.scene == '4b' and not s.on('tray_done'),
          'Хозяйке нужна помощь с заказами. Читайте заказ и кладите на поднос нужное: 杯 — чашка, 碗 — миска, 瓶 — бутылка.')
hints.add(lambda s: s.chapter == 4 and s.on('redgate_ok'),
          'Путь открыт: вверх через Красные ворота.')

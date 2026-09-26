"""Chapter 7 · 天街 «Небесная улица» — the South Gate of Heaven, the night street, the Azure Clouds temple, the moon peak."""
from __future__ import annotations

import pyxel

from ...art import kit, picto
from ...art import palette as P
from ...art.pictures import icon_for, picture
from ...art.sketches import sketch
from ...core.magic import SpellEntry
from ...core.phrases import normalize
from ...core.talisman import TalismanDef
from ...core.talisman import register as register_talisman
from ...core.types import ActorDef, ExitDef, HotspotDef, ItemDef, PageDef, SceneDef, SceneLook, ScriptContext, SignDef, TextDef
from .. import hints, items, pages, spells, texts, words
from ..world import register
from ._common import cycle, edit_talisman, fig, no, pay, yes

items.add(
    ItemDef('scroll', '画龙点睛', 'scroll', 'Свиток от Лиса: четыре знака и рисунок дракона без глаз.'),
    ItemDef('noodles7', '面条', 'noodles', 'Миска горячей лапши.'),
)

register_talisman(
    TalismanDef('south_gate', '门天南', {'南天门': 'fixed'}),
)

spells.add(
    SpellEntry('画龙点睛', 'idiom', 'Нарисовать дракону зрачки — последний штрих, оживляющий всё', 'dragon'),
)

texts.add(
    TextDef(
        'diary_14', 'diary', 'Дневник деда · 14',
        '我们终于到了山顶。\n可是云太多了，我们没有看见日出。\n李明说："明年秋分，我们再来！"\n我说："一定！"',
        '«Мы наконец дошли до вершины. Но облаков было слишком много, и восхода мы не увидели. '
        'Ли Мин сказал: „На следующее равноденствие придём снова!“ Я ответил: „Обязательно!“».',
        chapter=7, date='一九六零年九月二十三号', sketch='clouds_1960',
    ),
    TextDef(
        'diary_15', 'diary', 'Дневник деда · 15',
        '明天我就要回国了。\n我想把笔还给李明，他不要。\n他说："笔在你那儿，你就会回来。"\n我会回来的。',
        '«Завтра я возвращаюсь домой. Хотел вернуть кисть Ли Мину — он не взял. Сказал: „Пока кисть у тебя, ты вернёшься“. Я вернусь».',
        chapter=7, date='一九六零年十月八号', sketch='magic_brush',
    ),
    TextDef(
        'couplets', 'stone', 'Парные надписи', '日出东方　月落西山\n天上有云　地下有水\n山高　水长',
        'Солнце встаёт на востоке — луна садится за западные горы. На небе облака — на земле вода. Гора высока — река длинна.',
        chapter=7,
    ),
    TextDef(
        'poem_libai', 'book', 'Ли Бо. «Думы тихой ночью»', '静夜思\n床前明月光，\n疑是地上霜。\n举头望明月，\n低头思故乡。',
        'Перед кроватью — лунный свет, как будто иней на земле. Подниму голову — гляжу на яркую луну, опущу — думаю о родном доме.',
        chapter=7,
    ),
    TextDef(
        'poem_dufu', 'stone', 'Ду Фу. «Глядя на гору»', '望岳\n会当凌绝顶，\n一览众山小。',
        'Непременно поднимусь на самую вершину — и одним взглядом охвачу все горы: какими маленькими они покажутся.',
        chapter=7,
    ),
)

# ---------------------------------------------------------------- 7a · the South Gate of Heaven


def sgate_look(s) -> SceneLook:
    return SceneLook('night', lantern=True)


def sgate_art(s, look: SceneLook) -> None:
    c = kit.C
    kit.sky([(P.LIGHT_BLUE, 40), (P.MIST, 30), (P.WHITE, 40)])
    kit.stars(191, 90, 70)
    kit.moon(270, 26, 8)
    kit.cloud_sea(128, 192)
    kit.stairs(160, 180, 110, 160, 120, 60, P.GREY, P.STONE, steps=8)
    kit.gate_tower(110, 122, 100, 62, P.VERMILION, open_=True, light=True)
    # the board with its scattered glyphs
    c.rect(134, 44, 52, 16, P.LACQUER)
    c.rectb(134, 44, 52, 16, P.GOLD)
    kit.path_band([(0, 166), (160, 170), (320, 166)], 12, P.PAPER, P.STONE)


async def sgate_enter(c: ScriptContext) -> None:
    if c.flag('ch7'):
        return
    c.set('ch7')
    await c.chapter(7)
    await c.narrate('Последняя ступень. Южные небесные ворота. Внизу, под звёздами, — море облаков.')
    await c.narrate('Ветер сорвал знаки с доски над воротами, и кто-то прибил их как попало.')
    c.unlock('diary_14')


async def board(c: ScriptContext) -> None:
    if c.flag('sgate_fixed'):
        await c.narrate('Над воротами снова: 南天门.')
        return
    out = await edit_talisman(c, 'south_gate')
    if out == 'fixed':
        c.set('sgate_fixed')
        await c.narrate('Знаки встают на свои места. Доска вспыхивает золотом.')
        await c.say('keeper7', '南天门！对了！')


async def keeper7_talk(c: ScriptContext) -> None:
    if c.flag('sgate_pass'):
        await cycle(c, 'k7_n', 'keeper7', ['天街上有很多小店。', '为了看日出，很多人晚上上山。', '李明？他过去了，去日观峰了。'])
        return
    if not c.flag('sgate_fixed'):
        await c.say('keeper7', '风太大了，把牌子上的字都刮乱了！')
        await c.say('keeper7', '"门天南"？这是什么意思？')
        return
    answer = await c.ask('keeper7', '这么晚了，你要做什么？')
    a = normalize(answer)
    if '日出' in a or '看' in a:
        c.set('sgate_pass')
        await c.say('keeper7', '看日出？好！为了看日出，很多人晚上上山。')
        await c.say('keeper7', '天街上有很多小店，你可以休息一下。')
    elif '李' in a:
        c.set('sgate_pass')
        await c.say('keeper7', '李明？他刚才过去了。他每年都来看日出。')
    else:
        await c.say('keeper7', '你要做什么？')


async def sgate_through(c: ScriptContext) -> bool:
    if c.flag('sgate_pass'):
        return True
    await c.say('keeper7', '等一下！你要做什么？')
    return False


register(
    SceneDef(
        id='7a', chapter=7, title='Южные небесные ворота', zh='南天门',
        art=sgate_art, look=sgate_look,
        path=[(8, 166), (160, 170), (312, 166)],
        entries={'bottom': 160, 'street': 300},
        actors=[
            ActorDef('keeper7', 'Привратник', fig(P.NAVY, P.GOLD, 'uniform', 'cap', kind='old'), 212, 160, 'left', on_talk=keeper7_talk),
        ],
        hotspots=[
            HotspotDef('board', 'Доска над воротами', (134, 44, 52, 16), stand_at=160, on_click=board, cursor='hand'),
        ],
        signs=[SignDef('board', '门天南', 138, 44, 'plaque', talisman='south_gate')],
        exits=[
            ExitDef('bottom', '6c', 'top', (120, 170, 80, 10), 'down', 160, 'Вниз'),
            ExitDef('street', '7b', 'gate', (310, 100, 10, 70), 'right', 312, 'Небесная улица', guard=sgate_through),
        ],
        on_enter=sgate_enter,
        music='night',
    )
)

# ---------------------------------------------------------------- 7b · the Heavenly Street


def street_look(s) -> SceneLook:
    return SceneLook('night', lantern=True)


def street7_art(s, look: SceneLook) -> None:
    c = kit.C
    kit.sky([(P.LIGHT_BLUE, 40), (P.MIST, 30), (P.WHITE, 40)])
    kit.stars(201, 80, 60)
    kit.cloud_sea(118, 202)
    # shops along the cliff edge
    for x, w, col in ((0, 70, P.PAPER), (76, 80, P.OCHRE), (164, 70, P.PAPER), (240, 80, P.OCHRE)):
        c.rect(x, 70, w, 56, col)
        kit.roof(x - 2, 70, w + 4, 8, P.INK, P.STONE)
        kit.window(x + 8, 84, 14, 12, True)
    for lx in (30, 110, 200, 280):
        kit.lantern(lx, 78, True)
    # the fox's riddle lanterns
    for i in range(4):
        kit.lantern(252 + i * 16, 96, True, P.ORANGE)
        c.line(252 + i * 16, 106, 252 + i * 16, 112, P.PAPER)
    kit.railing(0, 319, 130, P.STONE, 10)
    kit.path_band([(0, 166), (160, 168), (320, 166)], 12, P.PAPER, P.STONE)


def street7_anim(s, look: SceneLook, frame: int) -> None:
    if s.on('fox_done'):
        return
    kit.canvas(pyxel)
    # the fox's tail peeks out from under the robe
    x = 296 + int(pyxel.sin(frame * 8) * 2)
    pyxel.tri(x, 158, x + 8, 150, x + 10, 160, P.ORANGE)
    pyxel.pset(x + 9, 151, P.WHITE)
    kit.canvas(None)


async def street7_enter(c: ScriptContext) -> None:
    if c.flag('street7_in'):
        return
    c.set('street7_in')
    await c.narrate('Небесная улица. Лавки над обрывом, фонари, запах лапши. Внизу — облака, как море.')


LOST_OWNERS = [
    {'id': 'girl7', 'zh': '我的伞是红色的，很小。', 'traits': '红小伞'},
    {'id': 'grandpa7', 'zh': '我的帽子是黑色的。', 'traits': '黑帽'},
    {'id': 'woman7', 'zh': '我的裙子是蓝色的，很短。', 'traits': '蓝短裙'},
    {'id': 'student7', 'zh': '我的笔记本是绿色的。', 'traits': '绿本'},
]
LOST_THINGS = [
    {'id': 't1', 'traits': '红大伞'}, {'id': 't2', 'traits': '红小伞'}, {'id': 't3', 'traits': '黑帽'},
    {'id': 't4', 'traits': '蓝长裙'}, {'id': 't5', 'traits': '蓝短裙'}, {'id': 't6', 'traits': '绿本'},
    {'id': 't7', 'traits': '红本'}, {'id': 't8', 'traits': '白瓶'}, {'id': 't9', 'traits': '白帽'},
]


async def lost_talk(c: ScriptContext) -> None:
    if c.flag('lost_done'):
        await cycle(c, 'lf_n', 'lostfound', ['你帮我解决了一个大问题！', '山上买东西不方便，丢了东西大家都很着急。'])
        return
    await c.say('lostfound', '这里是失物招领。晚上人太多了，大家都在找东西。')
    await c.say('girl7', '我的伞是红色的，很小。')
    await c.narrate('Девочка всхлипывает.')
    await c.say('grandpa7', '我的帽子是黑色的。')
    await c.say('woman7', '我的裙子是蓝色的，很短。')
    await c.say('student7', '我的笔记本是绿色的。')
    answer = await c.ask('lostfound', '你能帮我检查一下这些东西吗？')
    if no(answer):
        await c.say('lostfound', '好吧……')
        return
    ok = await c.puzzle('lost', owners=LOST_OWNERS, things=LOST_THINGS, lines=[o['zh'] for o in LOST_OWNERS])
    if not ok:
        await c.say('lostfound', '没关系，你慢慢看。')
        return
    c.set('lost_done')
    await c.say('girl7', '我的小伞！谢谢你！')
    await c.say('lostfound', '你帮我解决了一个大问题！大家都很满意！')
    await c.say('student7', '我的笔记本！我所有的作业都在里面！')


async def girl7_talk(c: ScriptContext) -> None:
    if c.flag('lost_done'):
        await c.say('girl7', '谢谢你！我不哭了！')
    else:
        await c.say('girl7', '我的伞没有了……')
        await c.narrate('Девочка плачет.')


async def grandpa7_talk(c: ScriptContext) -> None:
    await cycle(c, 'gp7_n', 'grandpa7', ['冬天山上很冷，夏天很舒服。', '我每年都来。这是我的第二十次！', '我们一起等日出吧。'])


async def woman7_talk(c: ScriptContext) -> None:
    await cycle(c, 'w7_n', 'woman7', ['我跟朋友在聊天，裙子就不见了。', '这儿的衬衫和皮鞋都很贵。', '山上没有超市，东西都是挑山工挑上来的。'])


async def student7_talk(c: ScriptContext) -> None:
    await cycle(c, 's7_n', 'student7', ['我对历史很感兴趣。', '关于泰山的故事，我知道很多！', '明天我要回学校，考试快结束了。'])


async def cook_talk(c: ScriptContext) -> None:
    if c.flag('noodle_order'):
        await c.say('cook', '十五元。')
        return
    await c.say('cook', '热面条！一碗十五元！')
    await c.say('cook', '山上什么东西都比较贵，因为都是挑山工挑上来的。')
    answer = await c.ask('cook', '你要一碗吗？')
    if yes(answer) or '要' in normalize(answer):
        c.set('noodle_order')
        await c.say('cook', '好！十五元。')
    else:
        await c.say('cook', '不饿？好吧。')


async def cook_item(c: ScriptContext, item: str) -> bool:
    if item == 'money' and c.flag('noodle_order'):
        if await pay(c, 'cook', 15, item):
            c.set('noodle_order', False)
            c.give('noodles7')
            await c.say('cook', '慢慢吃！小心，很热！')
        return True
    return False


async def musician_talk(c: ScriptContext) -> None:
    await cycle(c, 'mus_n', 'musician', ['我在这儿唱歌，大家听音乐，就不冷了。', '多么美的夜晚啊！', '你也来唱一句吧！'])


RIDDLES = [
    ('一口咬掉牛尾巴。', '告'),
    ('二人土上坐。', '坐'),
]


async def fox_talk(c: ScriptContext) -> None:
    if c.flag('fox_done'):
        await cycle(c, 'fox_n', 'fox', ['嘻嘻，你真聪明。', '龙没有眼睛，就不能飞……', '天快亮了，我要回去了。'])
        return
    step = int(c.flag('fox_step') or 0)
    if step == 0:
        await c.say('fox', '嘻嘻，这么晚还有客人！我这儿卖字谜。')
        answer = await c.ask('fox', '你对字谜感兴趣吗？')
        if no(answer):
            await c.say('fox', '真的吗？我不相信。')
            return
        await c.say('fox', '好！根据这句话，猜一个字。')
    riddle, glyph = RIDDLES[min(step, len(RIDDLES) - 1)]
    answer = await c.ask('fox', riddle)
    if glyph in normalize(answer):
        await c.say('fox', f'对！是"{glyph}"！')
        step += 1
        c.set('fox_step', step)
        if step >= len(RIDDLES):
            c.set('fox_done')
            await c.say('fox', '你是第一个都猜对的人！这个给你。')
            c.give('scroll')
            await c.narrate('Лис протягивает свиток: четыре знака и дракон без зрачков. Из-под халата мелькает рыжий хвост.')
            await c.say('fox', '碧霞祠里有一条龙，它没有眼睛。你去看看吧！')
        else:
            await c.say('fox', '再来一个！')
    else:
        c.set('fox_step', step)
        await c.say('fox', '嘻嘻，不对！再想想。')


register(
    SceneDef(
        id='7b', chapter=7, title='Небесная улица', zh='天街',
        art=street7_art, anim=street7_anim, look=street_look,
        path=[(8, 166), (160, 168), (312, 166)],
        entries={'gate': 20, 'temple': 300},
        actors=[
            ActorDef('lostfound', 'Бюро находок', fig(P.DARK_BLUE, P.WHITE, 'uniform', 'bun'), 30, 150, 'right', on_talk=lost_talk),
            ActorDef('girl7', 'Плачущая девочка', fig(P.YELLOW, P.VERMILION, 'dress', 'twinbuns', kind='child'), 58, 162, 'left',
                     on_talk=girl7_talk, tags=('人', '孩子')),
            ActorDef('grandpa7', 'Старик в тулупе', fig(P.WOOD, P.OCHRE, 'robe', 'bald', kind='old'), 84, 160, 'left', on_talk=grandpa7_talk),
            ActorDef('woman7', 'Модница', fig(P.PINK, P.WHITE, 'jacket', 'ponytail'), 108, 160, 'left', on_talk=woman7_talk),
            ActorDef('student7', 'Студент', fig(P.JADE, P.WHITE, 'jacket', 'short', glasses=True), 130, 160, 'left', on_talk=student7_talk),
            ActorDef('cook', 'Повар лапшичной', fig(P.WHITE, P.WHITE, 'jacket', 'cap'), 196, 150, 'left', on_talk=cook_talk, on_item=cook_item),
            ActorDef('musician', 'Уличный музыкант', fig(P.NAVY, P.GOLD, 'jacket', 'short', pose='sit'), 232, 158, 'right', on_talk=musician_talk),
            ActorDef('fox', 'Продавец загадок', fig(P.ORANGE, P.WHITE, 'robe', 'scholar', prop='fan'), 286, 156, 'left', on_talk=fox_talk),
        ],
        signs=[
            SignDef('street', '天街', 146, 40, 'plaque'),
            SignDef('lost', '失物招领', 4, 62, 'blue'),
            SignDef('noodles', '面条　十五元', 170, 58, 'banner'),
            SignDef('riddles', '字谜', 262, 58, 'lit'),
        ],
        exits=[
            ExitDef('gate', '7a', 'street', (0, 100, 10, 70), 'left', 12, 'Южные ворота'),
            ExitDef('temple', '7c', 'street', (310, 100, 10, 70), 'right', 312, 'Храм Лазоревых облаков'),
        ],
        on_enter=street7_enter,
        music='night',
    )
)

# ---------------------------------------------------------------- 7c · the Temple of Azure Clouds


def bixia_look(s) -> SceneLook:
    return SceneLook('predawn' if s.on('dragon_flew') else 'night', lantern=True)


def bixia_art(s, look: SceneLook) -> None:
    c = kit.C
    kit.sky([(P.LIGHT_BLUE, 40), (P.MIST, 30), (P.WHITE, 40)])
    kit.stars(211, 60, 60)
    if not s.on('dragon_flew'):
        for i in range(5):
            kit.cloud(20 + i * 64, 30 + (i % 2) * 12, 60, P.MIST, P.STONE)
    c.rect(60, 64, 200, 62, P.VERMILION)
    kit.roof(50, 64, 220, 14, P.GOLD, P.OCHRE, ridge_col=P.OCHRE)
    for px in (70, 110, 210, 250):
        kit.pillar(px, 126, 50, P.VERMILION, P.LACQUER)
    # the painted dragon on the wall between the pillars
    if not s.on('dragon_flew'):
        for i in range(16):
            x = 124 + i * 5
            y = 92 + int(pyxel.sin(i * 45) * 6)
            c.circ(x, y, 3, P.JADE)
        c.circ(206, 88, 5, P.JADE)
        c.circb(206, 87, 2, P.WHITE)
    else:
        c.rect(120, 80, 90, 26, P.LACQUER)
    kit.ground(126, P.GREY, P.STONE, seed=213, density=0.02)
    kit.path_band([(0, 166), (160, 168), (320, 166)], 12, P.PAPER, P.STONE)


async def bixia_enter(c: ScriptContext) -> None:
    if c.flag('bixia_in'):
        return
    c.set('bixia_in')
    await c.narrate('Храм Лазоревых облаков. Золотая черепица, на колоннах — парные надписи. На стене нарисован дракон — без зрачков.')


COUPLETS = [
    ('日出东方 — 月落？山', [{'zh': '东'}, {'zh': '西'}, {'zh': '南'}, {'zh': '北'}], 1),
    ('天上有云 — ？下有水', [{'zh': '人'}, {'zh': '山'}, {'zh': '地'}, {'zh': '门'}], 2),
    ('山高 — 水？', [{'zh': '长'}, {'zh': '大'}, {'zh': '短'}, {'zh': '小'}], 0),
]


async def temple_keeper_talk(c: ScriptContext) -> None:
    if not c.flag('couplets_done'):
        await c.say('tkeeper', '风太大了，对联下联的字都被刮掉了。')
        answer = await c.ask('tkeeper', '你能帮我把对联写完吗？')
        if no(answer):
            await c.say('tkeeper', '好吧。')
            return
        await c.read('couplets')
        for prompt, options, right in COUPLETS:
            idx = await c.puzzle('choose', prompt=f'Какой знак пропал? {prompt}', options=options)
            if idx is None:
                return
            if idx != right:
                await c.say('tkeeper', '不对。上联和下联，意思要相对。')
                return
        c.set('couplets_done')
        await c.say('tkeeper', '完成了！上联下联都对！你的汉语水平真高！')
        await c.say('tkeeper', '"山高水长"……有一个老人每年都说这四个字。他叫李明。')
        await c.say('tkeeper', '他刚才经过这儿，去日观峰了。日出以前，他一定在那儿。')
        return
    if not c.flag('dragon_flew'):
        await c.say('tkeeper', '你看这条龙。以前的人说：给它画上眼睛，它就会飞走。')
        await c.say('tkeeper', '可是没有人敢画。今天的云太多了，看不见日出……')
        return
    await cycle(c, 'tk_n', 'tkeeper', ['龙飞走了，云也少了！', '快去日观峰吧！', '你给了我们一个机会：今天能看见日出！'])


async def dragon(c: ScriptContext) -> None:
    if c.flag('dragon_flew'):
        await c.narrate('На стене — пустое место, где был дракон.')
        return
    await c.narrate('Дракон нарисован во всю стену: чешуя, когти, усы. Только глаза пустые.')


async def dragon_spell(c: ScriptContext, spell) -> bool:
    if c.flag('dragon_flew') or spell.power != 'full':
        return False
    if spell.is_special('画龙点睛') or spell.acts('点', '睛'):
        c.set('dragon_flew')
        await c.event('dragon')
        await c.narrate('Кисть ставит две точки. Дракон моргает — и срывается со стены.')
        await c.narrate('Он проносится над храмом, закручивая облака за собой, и уносит их на запад. Небо на востоке чистое.')
        await c.say('tkeeper', '龙飞走了！云也少了！今天能看见日出了！')
        return True
    return False


async def bixia_up(c: ScriptContext) -> bool:
    if c.flag('couplets_done'):
        return True
    await c.say('tkeeper', '等一下，年轻人！你能帮我一个忙吗？')
    return False


register(
    SceneDef(
        id='7c', chapter=7, title='Храм Лазоревых облаков', zh='碧霞祠',
        art=bixia_art, look=bixia_look,
        path=[(8, 166), (160, 168), (312, 166)],
        entries={'street': 20, 'peak': 300, 'moon': 160},
        actors=[
            ActorDef('tkeeper', 'Смотритель храма', fig(P.GREY, P.NAVY, 'robe', 'scholar', kind='old', beard=True), 92, 160, 'right',
                     on_talk=temple_keeper_talk),
        ],
        hotspots=[
            HotspotDef('dragon', 'Нарисованный дракон', (118, 78, 94, 30), stand_at=160, on_click=dragon, on_spell=dragon_spell, tags=('龙',)),
        ],
        signs=[
            SignDef('bixia', '碧霞祠', 138, 48, 'plaque'),
            SignDef('upper1', '日出东方', 64, 70, 'banner', vertical=True),
            SignDef('lower1', '月落西山', 254, 70, 'banner', vertical=True, visible=lambda s: s.on('couplets_done')),
        ],
        exits=[
            ExitDef('street', '7b', 'temple', (0, 100, 10, 70), 'left', 12, 'Небесная улица'),
            ExitDef('moon', '7d', 'temple', (150, 128, 30, 20), 'down', 160, 'Пик Луны'),
            ExitDef('peak', '8a', 'bottom', (310, 100, 10, 70), 'right', 312, 'К вершине', guard=bixia_up),
        ],
        on_enter=bixia_enter,
        on_spell=dragon_spell,
        music='temple',
    )
)

# ---------------------------------------------------------------- 7d · the Moon-viewing peak


def moon_look(s) -> SceneLook:
    return SceneLook('night', lantern=True)


def moon_art(s, look: SceneLook) -> None:
    kit.sky([(P.LIGHT_BLUE, 40), (P.MIST, 30), (P.WHITE, 40)])
    kit.stars(221, 120, 90)
    kit.moon(230, 40, 16)
    kit.cloud_sea(120, 222)
    kit.cliff(40, 110, 240, 70, P.STONE, P.GREY, P.PLUM, seed=223)
    kit.path_band([(0, 166), (160, 162), (320, 166)], 12, P.PAPER, P.STONE)


async def poet_talk(c: ScriptContext) -> None:
    if not c.flag('poem_read'):
        c.set('poem_read')
        await c.say('poet', '你看，月亮多么美！我给你读一首诗。')
        await c.read('poem_libai')
        await c.say('poet', '这是李白的诗。一千多年过去了，月亮还是这个月亮。')
        answer = await c.ask('poet', '你想你的家吗？')
        if no(answer):
            await c.say('poet', '哈哈，你心里一定有一个人。')
        else:
            await c.say('poet', '我也是。月亮下面，大家都想家。')
        return
    await cycle(c, 'poet_n', 'poet', ['杜甫也写过泰山：一览众山小。', '日出以前，最冷，也最美。'])


register(
    SceneDef(
        id='7d', chapter=7, title='Пик созерцания луны', zh='月观峰',
        art=moon_art, look=moon_look,
        path=[(8, 166), (160, 162), (312, 166)],
        entries={'temple': 20},
        actors=[
            ActorDef('poet', 'Поэт', fig(P.PAPER, P.NAVY, 'robe', 'topknot', beard=True, prop='book'), 160, 158, 'right', on_talk=poet_talk),
        ],
        hotspots=[
            HotspotDef('rock', 'Скала с надписью', (40, 110, 60, 40), stand_at=70, on_click=lambda c: c.read('poem_dufu')),
        ],
        signs=[SignDef('moon', '月观峰', 14, 40, 'carved', vertical=True)],
        exits=[ExitDef('temple', '7c', 'moon', (0, 100, 10, 70), 'left', 12, 'Храм')],
        music='night',
    )
)

# ---------------------------------------------------------------- pages, pictures, glossary, hints

pages.add(
    PageDef('sgate', 'Южные ворота', 7, ('为了', '过去', '刮乱', '小店'), kind='phrase',
            phrases=('为了看日出，很多人晚上上山。', '李明？他过去了', '把牌子上的字都刮乱了！', '天街上有很多小店')),
    PageDef('lostfound', 'Бюро находок', 7, ('裙子', '笔记本', '短', '检查', '解决', '满意'), kind='phrase',
            phrases=('我的裙子是蓝色的，很短。', '我的笔记本是绿色的。', '我的裙子是蓝色的，很短。', '你能帮我检查一下这些东西吗？',
                     '你帮我解决了一个大问题！', '大家都很满意！')),
    PageDef('clothes7', 'Одежда', 7, ('衬衫', '皮鞋', '裙子', '大衣'), kind='icon'),
    PageDef('street7', 'Небесная улица', 7, ('元', '音乐', '多么', '聊天', '超市', '方便'), kind='phrase',
            phrases=('一碗十五元！', '大家听音乐，就不冷了。', '多么美的夜晚啊！', '我跟朋友在聊天', '山上没有超市', '山上买东西不方便')),
    PageDef('seasons', 'Времена года', 7, ('春', '夏', '秋', '冬'), kind='picture'),
    PageDef('student7', 'Студент', 7, ('感兴趣', '关于', '结束', '哭'), kind='phrase',
            phrases=('我对历史很感兴趣。', '关于泰山的故事，我知道很多！', '考试快结束了。', '我不哭了！')),
    PageDef('fox', 'Лис', 7, ('根据', '猜', '相信', '眼睛'), kind='phrase',
            phrases=('根据这句话，猜一个字。', '根据这句话，猜一个字。', '我不相信。', '龙没有眼睛，就不能飞……')),
    PageDef('couplets7', 'Парные надписи', 7, ('东', '西', '地', '长', '上联', '下联'), kind='phrase',
            phrases=('日出东方', '月落西山', '地下有水', '山高水长', '上联下联都对！', '上联下联都对！')),
    PageDef('temple7', 'Смотритель', 7, ('完成', '水平', '机会', '敢'), kind='phrase',
            phrases=('完成了！', '你的汉语水平真高！', '你给了我们一个机会', '可是没有人敢画。')),
    PageDef('dragon', 'Дракон', 7, ('画', '龙', '点', '睛'), kind='phrase',
            phrases=('画龙点睛', '画龙点睛', '画龙点睛', '画龙点睛')),
    PageDef('poem7', 'Ли Бо', 7, ('月光', '低头', '故乡', '想家'), kind='phrase',
            phrases=('床前明月光', '低头思故乡。', '低头思故乡。', '大家都想家。')),
    PageDef('diary14', 'Облака 1960 года', 7, ('山顶', '没有看见', '明年', '再来'), kind='phrase',
            phrases=('我们终于到了山顶。', '我们没有看见日出。', '明年秋分，我们再来！', '明年秋分，我们再来！')),
    PageDef('diary15', 'Кисть остаётся', 7, ('还给', '回国', '会回来'), kind='phrase',
            phrases=('我想把笔还给李明', '明天我就要回国了。', '我会回来的。')),
)

for w, ic in (('衬衫', 'shirt'), ('皮鞋', 'shoes'), ('裙子', 'dress'), ('大衣', 'coat')):
    icon_for(w, ic)


def _season(ground: int, sky: int, extra: str) -> None:
    def draw(x: int, y: int) -> None:
        pyxel.rect(x, y, 32, 20, sky)
        pyxel.rect(x, y + 20, 32, 12, ground)
        picto.icon('tree', x + 8, y + 8)
        if extra == 'snow':
            for dx, dy in ((4, 4), (14, 10), (24, 6), (8, 16), (28, 14)):
                pyxel.pset(x + dx, y + dy, P.WHITE)
        elif extra == 'sun':
            pyxel.circ(x + 26, y + 5, 3, P.YELLOW)
        elif extra == 'leaves':
            for dx in (4, 12, 22, 28):
                pyxel.pset(x + dx, y + 24, P.ORANGE)
        elif extra == 'flowers':
            for dx in (4, 12, 22, 28):
                pyxel.pset(x + dx, y + 24, P.PINK)
    return draw


picture('春')(_season(P.JADE, P.LIGHT_BLUE, 'flowers'))
picture('夏')(_season(P.MOSS, P.LIGHT_BLUE, 'sun'))
picture('秋')(_season(P.OCHRE, P.PEACH, 'leaves'))
picture('冬')(_season(P.WHITE, P.GREY, 'snow'))


@sketch('clouds_1960')
def _(x: int, y: int) -> None:
    for i in range(4):
        pyxel.elli(x + 2 + i * 20, y + 14 + (i % 2) * 4, 26, 10, P.STONE)
    picto.person(x + 30, y + 42, P.INK)
    picto.person(x + 42, y + 42, P.INK)
    pyxel.line(x + 2, y + 42, x + 78, y + 42, P.INK)


words.add('''
南天门 — Южные небесные ворота
为了 — ради, чтобы
过去 — пройти; прошлое
刮乱 — растрепать ветром
小店 — лавочка
天街 — Небесная улица
失物招领 — бюро находок
裙子 — юбка
笔记本 — тетрадь, записная книжка
短 — короткий
检查 — проверить
解决 — решить
满意 — довольный
衬衫 — рубашка
皮鞋 — кожаные туфли
元 — юань
音乐 — музыка
多么 — как (же)!
聊天 — болтать
超市 — супермаркет
方便 — удобно
感兴趣 — интересоваться
关于 — о, про
结束 — закончиться
哭 — плакать
根据 — согласно, по
猜 — угадывать
上联 — верхняя строка парной надписи
下联 — нижняя строка
完成 — завершить
水平 — уровень
机会 — возможность, шанс
敢 — осмелиться
画龙点睛 — нарисовать дракону зрачки (последний штрих)
碧霞祠 — Храм Лазоревых облаков
月观峰 — Пик созерцания луны
月光 — лунный свет
低头 — опустить голову
故乡 — родные края
想家 — скучать по дому
山顶 — вершина
没有看见 — не увидели
明年 — в следующем году
再来 — прийти снова
还给 — вернуть
回国 — вернуться на родину
会回来 — вернётся
''')

hints.add(lambda s: s.scene == '7a' and not s.on('sgate_fixed'),
          'Ветер перепутал знаки на доске: 门天南. Как называются эти ворота? Поменяйте знаки местами.')
hints.add(lambda s: s.scene == '7a' and s.on('sgate_fixed') and not s.on('sgate_pass'),
          'Привратник спрашивает, зачем вы здесь ночью. Ответьте: 我要看日出.')
hints.add(lambda s: s.scene == '7b' and not s.on('lost_done'),
          'В бюро находок все описывают свои вещи: цвет, размер, что это. Помогите найти каждую.')
hints.add(lambda s: s.scene == '7b' and s.on('lost_done') and not s.on('fox_done'),
          'Продавец загадок в оранжевом халате (и с хвостом?). Отгадывайте знак по описанию: 一口咬掉牛尾巴 — 口 и 牛 без хвоста.')
hints.add(lambda s: s.scene == '7c' and not s.on('couplets_done'),
          'Парные надписи: нижняя строка отвечает верхней — день и ночь, восток и запад, небо и земля. Вспомните запись деда: 山高 — 水长.')
hints.add(lambda s: s.scene == '7c' and s.on('couplets_done') and not s.on('dragon_flew'),
          'Дракон без глаз и свиток Лиса: 画龙点睛. Напишите эти четыре знака кистью и направьте на дракона.')

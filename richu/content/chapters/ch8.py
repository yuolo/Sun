"""Chapter 8 · 日出 «Восход» — the Jade Emperor peak, the Sun-viewing peak, the letter, the sunrise."""
from __future__ import annotations

import pyxel

from ...art import kit, picto
from ...art import palette as P
from ...art.pictures import picture
from ...art.sketches import sketch
from ...core.magic import SpellEntry
from ...core.phrases import normalize
from ...core.types import ActorDef, ExitDef, HotspotDef, PageDef, SceneDef, SceneLook, ScriptContext, SignDef, TextDef
from .. import hints, pages, spells, texts, words
from ..world import register
from ._common import cycle, fig

spells.add(
    SpellEntry('风吹云开', 'idiom', 'Ветер дует — облака расходятся', 'clouds_open'),
)

texts.add(
    TextDef(
        'letter_grandpa', 'letter', 'Письмо деда',
        '亲爱的李明：\n你好！六十年过去了，你还好吗？\n我有一件事，一直想告诉你。\n'
        '一九六零年，国家要求我们回国，我没有选择。我不同意，可是我不能留下。\n'
        '回国以后，我遇到了我的妻子，有了孩子。有一年，我差一点儿就回来了，可是……\n'
        '其他的事，我都忘了；可是泰山，我没有忘。每年秋分，我都看着东方。\n'
        '你教我的字，影响了我的一生。我不但学会了写字，而且学会了等。\n'
        '我的汉语水平不高，这些句子写得不好，请你别笑我。\n我写这封信，主要是想说：谢谢你，我的朋友。\n'
        '这支笔，我一直没有还给你。我让我的家人把它带回泰山。\n你的朋友　小安',
        '«Дорогой Ли Мин! Здравствуй! Прошло шестьдесят лет — как ты? Я всё хотел сказать тебе одну вещь. '
        'В 1960-м страна потребовала, чтобы мы вернулись, у меня не было выбора. Я был против, но остаться не мог. '
        'Дома я встретил жену, у нас появились дети. Однажды я чуть было не приехал, но… Остальное я забыл, но Тайшань — нет. '
        'Каждое равноденствие я смотрю на восток. Знаки, которым ты меня учил, изменили мою жизнь: я научился не только писать, но и ждать. '
        'Мой китайский так себе, фразы корявые — не смейся. Пишу это письмо, чтобы сказать главное: спасибо, мой друг. '
        'Кисть я так и не вернул. Прошу моих родных отнести её на Тайшань. Твой друг Сяо Ань».',
        chapter=8,
    ),
    TextDef(
        'diary_16', 'diary', 'Дневник деда · 16',
        '十年了。今天是秋分。\n我在莫斯科，看着东方。\n李明，你在山上吗？你看见日出了吗？',
        '«Десять лет. Сегодня равноденствие. Я в Москве и смотрю на восток. Ли Мин, ты на горе? Ты видишь восход?»',
        chapter=8, date='一九七零年九月二十三号', sketch='moscow_window',
    ),
    TextDef(
        'diary_17', 'diary', 'Дневник деда · 17',
        '我老了，不能去泰山了。\n我把笔、信和日记放在一个盒子里。\n也许有一天，有人会带它们回去。',
        '«Я стар, до Тайшаня мне уже не добраться. Я положил кисть, письмо и дневник в коробку. Может быть, однажды кто-то отвезёт их обратно».',
        chapter=8, date='二零一九年九月二十三号', sketch='the_box',
    ),
    TextDef(
        'email_xiaoyue', 'letter', 'Письмо от Сяоюэ',
        '小安的家人，你好！\n这是我给你写的第一封电子邮件。\n爷爷很好。他每天打扫茶馆，还给客人讲小安的故事。\n'
        '王奶奶坐了一辆出租车上山看爷爷，他们聊了一个下午！\n'
        '我决定去俄罗斯留学！我每天去图书馆学习俄语，还买了一本很大的词典。我的俄语水平提高了很多。\n'
        '明年九月，飞机起飞以前，我一定给你打电话。\n听说莫斯科的地铁很漂亮，我也想骑自行车看看你的城市。\n'
        '爷爷把泰山的水放在一个小瓶子里，让我带给你。\n秋分见！\n小月',
        '«Здравствуй! Это моё первое письмо тебе по электронной почте. Дедушка в порядке: каждый день прибирает чайную и рассказывает гостям историю Сяо Аня. '
        'Бабушка Ван приехала на такси к нему в гости, они проговорили целый день! Я решила учиться в России! Каждый день хожу в библиотеку учить русский, '
        'купила огромный словарь, мой русский стал намного лучше. В сентябре перед вылетом обязательно позвоню. Говорят, в Москве красивое метро — '
        'хочу проехаться по твоему городу на велосипеде. Дедушка налил воды с Тайшаня в маленький флакон, чтобы я привезла её тебе. До равноденствия! Сяоюэ».',
        chapter=8,
    ),
)

# ---------------------------------------------------------------- 8a · the Jade Emperor peak


def jade_look(s) -> SceneLook:
    return SceneLook('predawn', lantern=True)


def jade_art(s, look: SceneLook) -> None:
    c = kit.C
    kit.sky([(P.LIGHT_BLUE, 40), (P.MIST, 30), (P.WHITE, 40)])
    kit.stars(231, 60, 40)
    kit.cloud_sea(126, 232)
    kit.cliff(0, 112, 320, 68, P.STONE, P.GREY, P.PLUM, seed=233)
    # the little temple on the summit
    kit.wall(180, 86, 120, 40, P.VERMILION, P.LACQUER, P.INK)
    kit.roof(200, 72, 80, 10, P.INK, P.STONE)
    c.rect(214, 82, 52, 44, P.VERMILION)
    kit.door(232, 96, 16, 30, P.LACQUER, P.GOLD)
    # the wordless stele
    kit.stele(80, 150, 22, 60, P.STONE, P.GREY, P.PLUM)
    kit.path_band([(0, 166), (160, 168), (320, 166)], 12, P.PAPER, P.STONE)


async def jade_enter(c: ScriptContext) -> None:
    if c.flag('ch8'):
        return
    c.set('ch8')
    await c.chapter(8)
    await c.narrate('Нефритовая вершина. Выше Тайшаня только небо. Восток чуть светлеет. У безымянной стелы кто-то ждёт — знакомая седая борода.')


RECIPES = [
    {'a': '人', 'b': '木', 'layout': 'lr', 'result': '休'},
    {'a': '木', 'b': '木', 'layout': 'lr', 'result': '林'},
    {'a': '日', 'b': '月', 'layout': 'lr', 'result': '明'},
    {'a': '日', 'b': '一', 'layout': 'tb', 'result': '旦'},
    {'a': '十', 'b': '口', 'layout': 'tb', 'result': '古'},
    {'a': '人', 'b': '人', 'layout': 'lr', 'result': '从'},
]
TARGETS = [
    {'hint': '一个人在树旁边休息。', 'result': '休'},
    {'hint': '两棵树在一起。', 'result': '林'},
    {'hint': '日和月在一起，天就亮了。', 'result': '明'},
    {'hint': '太阳从地上出来的时候。', 'result': '旦'},
]


async def scholar8_talk(c: ScriptContext) -> None:
    if c.flag('compose_done'):
        await cycle(c, 'sch8_n', 'scholar8', ['古人说：风吹云开，日就出来了。', '快去日观峰吧！日出快到了。', '字是人造的。人心里有什么，就能写出什么。'])
        return
    if not c.flag('scholar8_met'):
        c.set('scholar8_met')
        await c.say('scholar8', '我们又见面了！聪明的外国人！')
        await c.say('scholar8', '你知道吗？仓颉造字的时候，也是这样：把两个字放在一起，就有了新的字。')
    ok = await c.puzzle('compose', parts='人木日月一十口', recipes=RECIPES, targets=TARGETS, lines=[t['hint'] for t in TARGETS])
    if not ok:
        await c.say('scholar8', '没关系，慢慢想。')
        return
    c.set('compose_done')
    c.confirm('休林明旦')
    await c.say('scholar8', '你会造字了！')
    await c.say('scholar8', '"旦"，就是早上，太阳刚出来的时候。')
    await c.say('scholar8', '古人说：风吹云开，日就出来了。今天的日出，就在你的笔下。')


async def stele8(c: ScriptContext) -> None:
    await c.narrate('Безымянная стела: высокий камень, на котором нет ни одного знака.')
    await c.say('scholar8', '这是无字碑。两千多年了，上面没有一个字。')
    await c.say('scholar8', '有人说，不写字，是因为要说的话太多了。')


async def jade_down(c: ScriptContext) -> bool:
    if c.flag('compose_done'):
        return True
    await c.say('scholar8', '等一下！我教你一件事。')
    return False


register(
    SceneDef(
        id='8a', chapter=8, title='Нефритовая вершина', zh='玉皇顶',
        art=jade_art, look=jade_look,
        path=[(8, 166), (160, 168), (312, 166)],
        entries={'bottom': 20, 'sun': 300},
        actors=[
            ActorDef('scholar8', 'Старый книжник', fig(P.GREY, P.NAVY, 'robe', 'scholar', kind='old', beard=True, glasses=True), 128, 160, 'left',
                     on_talk=scholar8_talk),
        ],
        hotspots=[HotspotDef('stele', 'Безымянная стела', (76, 84, 30, 66), stand_at=100, on_click=stele8)],
        signs=[
            SignDef('jade', '玉皇顶', 216, 58, 'plaque'),
            SignDef('wordless', '无字碑', 50, 70, 'carved', vertical=True),
        ],
        exits=[
            ExitDef('bottom', '7c', 'peak', (0, 100, 10, 70), 'left', 12, 'Храм Лазоревых облаков'),
            ExitDef('sun', '8b', 'jade', (310, 100, 10, 70), 'right', 312, 'Пик созерцания солнца', guard=jade_down),
        ],
        on_enter=jade_enter,
        music='temple',
    )
)

# ---------------------------------------------------------------- 8b · the Sun-viewing peak


def sun_look(s) -> SceneLook:
    if s.on('sunrise'):
        return SceneLook('dawn')
    return SceneLook('predawn', lantern=True)


def sun_art(s, look: SceneLook) -> None:
    c = kit.C
    # the eastern sky warms towards the horizon (painted for the pre-dawn palette)
    kit.sky([(P.LIGHT_BLUE, 44), (P.PERIWINKLE, 22), (P.PEACH, 22), (P.YELLOW, 40)])
    if s.on('sunrise'):
        kit.sun(250, 92, 14)
    elif s.on('clouds_open'):
        c.rect(200, 100, 110, 3, P.ORANGE)
        c.rect(220, 97, 70, 3, P.YELLOW)
    kit.cloud_sea(104, 242)
    kit.cliff(0, 120, 190, 60, P.STONE, P.GREY, P.PLUM, seed=243)
    kit.rock(150, 134, 40, 18, P.STONE, P.GREY, P.PLUM)
    kit.railing(0, 150, 126, P.STONE, 10)
    kit.path_band([(0, 166), (190, 166)], 12, P.PAPER, P.STONE)


def sun_front(s, look: SceneLook) -> None:
    if s.on('clouds_open'):
        return
    for i in range(6):
        kit.cloud(150 + i * 30, 70 + (i % 3) * 10, 70, P.STONE, P.PLUM)


def sun_anim(s, look: SceneLook, frame: int) -> None:
    if not s.on('sunrise'):
        return
    kit.canvas(pyxel)
    for i in range(8):
        a = frame * 0.5 + i * 45
        x0 = 250 + pyxel.cos(a) * 18
        y0 = 92 + pyxel.sin(a) * 18
        x1 = 250 + pyxel.cos(a) * 24
        y1 = 92 + pyxel.sin(a) * 24
        pyxel.line(x0, y0, x1, y1, P.YELLOW)
    kit.canvas(None)


async def sun_enter(c: ScriptContext) -> None:
    if c.flag('sun_in'):
        return
    c.set('sun_in')
    await c.narrate('Пик созерцания солнца. Край скалы, перила, дальше — только облака. На камне у края сидит старик в ватной куртке, укутанный до ушей.')


async def liming_talk(c: ScriptContext) -> None:
    if c.flag('sunrise'):
        await cycle(c, 'lm_n', 'liming', ['小安，你看见了吗？', '这支笔，现在是你的了。', '秋分见，孩子。'])
        return
    if not c.flag('lm_met'):
        await c.say('liming', '你好。你也来看日出？')
        await c.say('liming', '我每年都来。我在等一个人。')
        answer = await c.ask('liming', '你是谁？')
        a = normalize(answer)
        if '小安' in a or '爷爷' in a or '俄' in a:
            await c.say('liming', '小安……？你是小安的家人？！')
            await c.narrate('Старик поднимается. Руки дрожат.')
            c.set('lm_met')
        else:
            await c.say('liming', '我不认识你……可是你的笔，那是我爸爸的笔！')
            c.set('lm_met')
        return
    if not c.flag('letter_given'):
        await c.say('liming', '小安……他好吗？他在哪儿？')
        await c.narrate('У меня для него письмо. Письмо, которое дед так и не отправил.')
        return
    await clouds_line(c)


async def clouds_line(c: ScriptContext) -> None:
    if c.flag('clouds_open'):
        await c.say('liming', '云开了！你看，东边天上的一角红了！')
        return
    await c.say('liming', '可是你看，云太多了。一层一层的云……')
    await c.say('liming', '六十年前也是这样。今年又看不见日出了吗？')


async def liming_item(c: ScriptContext, item: str) -> bool:
    if item == 'letter' and c.flag('lm_met') and not c.flag('letter_given'):
        c.take('letter')
        c.set('letter_given')
        await c.say('liming', '这是……小安的信？')
        await c.say('liming', '我的眼睛不好，看不清楚。你给我读，好吗？')
        await c.narrate('Читаю вслух. Медленно, по слогам, как учил дед. Ли Мин слушает, закрыв глаза.')
        await c.read('letter_grandpa')
        await c.narrate('Старик плачет, не пряча лица.')
        await c.say('liming', '他没有忘记我……我也没有忘记他。')
        await c.say('liming', '我花了六十年，等这个日出。')
        await clouds_line(c)
        return True
    if item == 'old_photo':
        await c.say('liming', '一九五九年！小王也在！她现在是王奶奶了。')
        return True
    if item == 'photo':
        await c.say('liming', '这是我们……在山顶。那天有很多云。')
        return True
    if item == 'drawing':
        await c.say('liming', '大桥！谁画的？画得真好！')
        return True
    if item == 'brush':
        await c.say('liming', '我爸爸的笔……它回来了。')
        return True
    return False


async def sky_spell(c: ScriptContext, spell) -> bool:
    if spell.power != 'full' or not c.flag('letter_given'):
        return False
    if not c.flag('clouds_open') and (spell.is_special('风吹云开') or spell.is_thing('风') or spell.says(noun='云', verb='开')):
        c.set('clouds_open')
        await c.event('clouds_open')
        await c.narrate('Ветер поднимается снизу, из долины. Облака расходятся, как занавес. Край неба на востоке розовеет.')
        await c.say('liming', '云开了！你看，东边天上的一角红了！')
        return True
    if c.flag('clouds_open') and not c.flag('sunrise') and (spell.says(noun='日', verb='出') or spell.is_thing('旦') or spell.is_special('日出')):
        await sunrise(c)
        return True
    return False


async def sunrise(c: ScriptContext) -> None:
    c.set('sunrise')
    await c.event('sunrise')
    await c.narrate('Из-за края облаков поднимается солнце. Сначала красная полоска, потом полукруг, потом — весь диск.')
    await c.narrate('Равноденствие. День и ночь равны. Над Тайшанем восход.')
    await c.say('liming', '日出了……')
    await c.say('liming', '小安，你看见了吗？我们终于一起看到了日出。')
    await c.say('liming', '谢谢你，孩子。')
    await c.say('liming', '这支笔，现在是你的了。你心里明白的字，它都会写。')
    answer = await c.ask('liming', '你想给小安写一句话吗？')
    line = normalize(answer)
    if line:
        c.state.inscription = line
        await c.say('liming', '好。他会看见的。')
    await c.narrate('Несколько месяцев спустя.')
    c.unlock('diary_16')
    c.unlock('diary_17')
    await c.read('diary_16')
    await c.read('diary_17')
    await c.read('email_xiaoyue')
    await c.finish()


register(
    SceneDef(
        id='8b', chapter=8, title='Пик созерцания солнца', zh='日观峰',
        art=sun_art, front=sun_front, anim=sun_anim, look=sun_look,
        path=[(8, 166), (180, 166)],
        entries={'jade': 20},
        actors=[
            ActorDef('liming', 'Ли Мин', fig(P.NAVY, P.STONE, 'jacket', 'cap', kind='old', beard=True, pose='sit'), 170, 134, 'right',
                     stand_at=150, on_talk=liming_talk, on_item=liming_item),
        ],
        hotspots=[
            HotspotDef('sky', 'Восток', (200, 40, 120, 70), stand_at=180, on_spell=sky_spell, tags=('天', '云', '日'),
                       on_click=lambda c: c.narrate('Восток. Над облаками светлеет полоса неба.')),
        ],
        signs=[SignDef('sunpeak', '日观峰', 14, 40, 'carved', vertical=True)],
        exits=[ExitDef('jade', '8a', 'sun', (0, 100, 10, 70), 'left', 12, 'Нефритовая вершина')],
        on_enter=sun_enter,
        on_spell=sky_spell,
        music='dawn',
    )
)

# ---------------------------------------------------------------- pages, pictures, glossary, hints

pages.add(
    PageDef('compose8', 'Новые знаки', 8, ('休', '林', '明', '旦')),
    PageDef('stele8', 'Безымянная стела', 8, ('无字碑', '造字', '放'), kind='phrase',
            phrases=('这是无字碑。', '仓颉造字的时候', '把两个字放在一起')),
    PageDef('sky8', 'Совет книжника', 8, ('风吹云开', '古人', '日出'), kind='phrase',
            phrases=('古人说：风吹云开，日就出来了。', '古人说：风吹云开，日就出来了。', '今天的日出，就在你的笔下。')),
    PageDef('letter8', 'Письмо деда', 8, ('国家', '要求', '选择', '同意', '遇到', '影响'), kind='phrase',
            phrases=('国家要求我们回国', '国家要求我们回国', '我没有选择。', '我不同意', '我遇到了我的妻子', '影响了我的一生。')),
    PageDef('letter8b', 'Главное', 8, ('件', '差', '其他', '不但', '句子', '主要'), kind='phrase',
            phrases=('我有一件事', '我差一点儿就回来了', '其他的事，我都忘了', '我不但学会了写字', '这些句子写得不好', '主要是想说')),
    PageDef('liming8', 'Ли Мин', 8, ('花', '终于', '一起', '心里', '一层一层', '一角'), kind='phrase',
            phrases=('我花了六十年，等这个日出。', '我们终于一起看到了日出。', '我们终于一起看到了日出。', '你心里明白的字，它都会写。',
                     '一层一层的云……', '东边天上的一角红了！')),
    PageDef('email8', 'Письмо Сяоюэ', 8, ('电子邮件', '打扫', '留学', '图书馆', '词典', '提高'), kind='phrase',
            phrases=('这是我给你写的第一封电子邮件。', '他每天打扫茶馆', '我决定去俄罗斯留学！', '我每天去图书馆学习俄语', '还买了一本很大的词典', '我的俄语水平提高了很多。')),
    PageDef('email8b', 'Москва', 8, ('起飞', '地铁', '自行车', '瓶子', '辆'), kind='phrase',
            phrases=('飞机起飞以前', '听说莫斯科的地铁很漂亮', '我也想骑自行车', '放在一个小瓶子里', '王奶奶坐了一辆出租车上山')),
)


@picture('休')
def _(x: int, y: int) -> None:
    picto.icon('tree', x + 14, y + 8)
    picto.person(x + 10, y + 30, P.DARK_BLUE)


@picture('林')
def _(x: int, y: int) -> None:
    picto.icon('tree', x, y + 8)
    picto.icon('tree', x + 16, y + 8)


@picture('明')
def _(x: int, y: int) -> None:
    pyxel.rect(x, y, 32, 32, P.LAMP)
    pyxel.circ(x + 10, y + 16, 7, P.ORANGE)
    pyxel.circ(x + 23, y + 14, 6, P.WHITE)
    pyxel.circ(x + 26, y + 12, 5, P.LAMP)


@picture('旦')
def _(x: int, y: int) -> None:
    pyxel.rect(x, y, 32, 32, P.PEACH)
    pyxel.circ(x + 16, y + 18, 8, P.VERMILION)
    pyxel.rect(x, y + 20, 32, 12, P.STONE)
    pyxel.line(x, y + 20, x + 31, y + 20, P.INK)


@sketch('moscow_window')
def _(x: int, y: int) -> None:
    pyxel.rectb(x + 20, y + 6, 40, 32, P.INK)
    pyxel.line(x + 40, y + 6, x + 40, y + 37, P.INK)
    pyxel.line(x + 20, y + 22, x + 59, y + 22, P.INK)
    pyxel.circb(x + 50, y + 14, 4, P.VERMILION)
    picto.person(x + 30, y + 42, P.INK)


@sketch('the_box')
def _(x: int, y: int) -> None:
    pyxel.rect(x + 20, y + 18, 40, 20, P.WOOD)
    pyxel.rectb(x + 20, y + 18, 40, 20, P.INK)
    pyxel.line(x + 26, y + 16, x + 50, y + 8, P.WOOD)
    pyxel.rect(x + 30, y + 22, 10, 12, P.PAPER)
    pyxel.rect(x + 44, y + 22, 10, 12, P.VERMILION)


words.add('''
玉皇顶 — Нефритовая вершина
无字碑 — безымянная стела
造字 — создавать иероглифы
古人 — древние люди
风吹云开 — ветер дует — облака расходятся
一层一层 — слой за слоем
一角 — уголок
日出 — восход
日观峰 — Пик созерцания солнца
国家 — государство, страна
要求 — требовать
选择 — выбор
同意 — соглашаться
遇到 — встретить
影响 — влиять
一件事 — одно дело
差一点儿 — чуть было не
其他 — остальное, другие
不但 — не только
句子 — предложение
主要 — главным образом
花 — тратить (время, деньги); цветок
一起 — вместе
心里 — в душе
电子邮件 — электронное письмо
打扫 — убирать
留学 — учиться за границей
图书馆 — библиотека
词典 — словарь
提高 — повышать
起飞 — взлетать
地铁 — метро
自行车 — велосипед
瓶子 — бутылочка
辆 — (счётное слово для машин)
莫斯科 — Москва
亲爱的 — дорогой
''')

hints.add(lambda s: s.scene == '8a' and not s.on('compose_done'),
          'Книжник учит составлять знаки: человек у дерева — 人 и 木 рядом; два дерева — 木 и 木; солнце и луна — 日 и 月; солнце над горизонтом — 日 над 一.')
hints.add(lambda s: s.scene == '8b' and not s.on('lm_met'),
          'Старик на камне — Ли Мин. Поговорите с ним. Кто вы? Внук Сяо Аня: можно ответить «小安» или «我爷爷是小安».')
hints.add(lambda s: s.scene == '8b' and s.on('lm_met') and not s.on('letter_given'),
          'Отдайте Ли Мину письмо деда (信).')
hints.add(lambda s: s.scene == '8b' and s.on('letter_given') and not s.on('clouds_open'),
          'Облака закрывают восток. Кисть: 风吹云开 — «ветер дует, облака расходятся». Направьте её на восток.')
hints.add(lambda s: s.scene == '8b' and s.on('clouds_open') and not s.on('sunrise'),
          'Небо чистое. Остался последний знак: солнце над горизонтом — 旦. Или напишите 日出.')

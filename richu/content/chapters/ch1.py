"""Chapter 1 · 路上 «В пути» — Jinan airport, the railway station, the train to Tai'an."""
from __future__ import annotations

import pyxel

from ...art import kit, picto
from ...art import palette as P
from ...art.pictures import icon_for, picture
from ...art.sketches import sketch
from ...core.phrases import normalize
from ...core.types import ActorDef, ExitDef, HotspotDef, ItemDef, PageDef, SceneDef, SceneLook, ScriptContext, SignDef, TextDef
from .. import hints, items, pages, texts, words
from ..world import register
from ._common import OFFICER, STAFF, cycle, fig, has_all, no, pay, yes

# ---------------------------------------------------------------- items and texts

items.add(
    ItemDef('passport', '护照', 'passport', 'Паспорт с китайской визой.'),
    ItemDef('suitcase', '行李箱', 'suitcase', 'Мой красный чемодан. Тяжёлый.'),
    ItemDef('phone', '手机', 'phone', 'Экран чёрный. Сел ещё в самолёте.'),
    ItemDef('money', '钱', 'money', 'Юани, обменянные дома. Хватит на дорогу, если не шиковать.'),
    ItemDef('ticket', '票', 'ticket', 'Билет на поезд. Знаки, цифры, номер.'),
    ItemDef('coffee', '咖啡', 'coffee', 'Горячий, сладкий, в бумажном стаканчике.'),
    ItemDef('tea', '茶', 'tea', 'Зелёный чай в стаканчике.'),
    ItemDef('milk', '牛奶', 'milk', 'Бутылочка холодного.'),
    ItemDef('bread', '面包', 'bread', 'Мягкая булочка.'),
    ItemDef('water_cup', '水', 'water_glass', 'Стакан воды.'),
    ItemDef('apple', '苹果', 'apple', 'Красное, блестящее. Подарок бабушки с вокзала.'),
)

texts.add(
    TextDef('ticket', 'sign', 'Билет', '泰安\n十点二十\n八号', 'Тайань, 10:20, место номер восемь.', chapter=1),
    TextDef(
        'diary_1', 'diary', 'Дневник деда · 1', '我叫安德烈。我是俄罗斯人。\n我不会说中文。',
        '«Меня зовут Андрей. Я русский. Я не умею говорить по-китайски». Первая запись — в поезде, этой же дорогой, шестьдесят с лишним лет назад.',
        chapter=1, date='一九五八年九月二十号', sketch='train_1958',
    ),
)

# ---------------------------------------------------------------- pages

pages.add(
    PageDef('greet', 'Приветствия', 1, ('你好', '谢谢', '再见', '请')),
    PageDef('who', 'Кто я', 1, ('我', '人', '中国', '俄罗斯', '外')),
    PageDef('airport', 'В аэропорту', 1, ('护照', '行李箱', '手机', '飞机', '洗手间', '机场'), kind='icon'),
    PageDef('this', 'Это моё', 1, ('这', '是', '的', '不', '在'), kind='phrase',
            phrases=('这是我的！', '你是俄罗斯人吗？', '不是你的！', '我不会说中文。', '出口在那儿。')),
    PageDef('num1', 'Счёт I', 1, ('一', '二', '三', '四', '五')),
    PageDef('num2', 'Счёт II', 1, ('六', '七', '八', '九', '十')),
    PageDef('station', 'Вокзал', 1, ('火车', '站', '进', '出口', '票')),
    PageDef('cafe', 'Буфет', 1, ('咖啡', '茶', '牛奶', '面包', '苹果', '水'), kind='icon'),
    PageDef('money', 'Деньги и время', 1, ('块', '两', '钱', '点', '分', '号')),
    PageDef('questions', 'Вопросы', 1, ('吗', '什么', '哪', '几'), kind='phrase',
            phrases=('你是俄罗斯人吗？', '你叫什么名字？', '你要去哪儿？', '几点的火车？')),
    PageDef('actions', 'Действия', 1, ('去', '来', '看', '买', '给', '要')),
    PageDef('train', 'В поезде', 1, ('学生', '名字', '叫', '坐', '说')),
    PageDef('window', 'За окном', 1, ('黄', '河', '山', '北', '南', '京')),
    PageDef('talk', 'Разговор', 1, ('没', '了', '也', '会', '那', '儿'), kind='phrase',
            phrases=('手机没电了！', '泰安站到了。', '你也不会说中文！', '我不会说中文。', '那是泰山！', '你要去哪儿？')),
    PageDef('have', 'Есть', 1, ('有', '给', '在'), kind='phrase',
            phrases=('你有手机吗？', '请给我你的护照。', '火车在那儿。')),
    PageDef('words1', 'Слова', 1, ('红', '电', '中文', '欢迎', '到')),
)

for w, ic in (('护照', 'passport'), ('行李箱', 'suitcase'), ('手机', 'phone'), ('飞机', 'plane'), ('洗手间', 'wc'), ('咖啡', 'coffee'),
              ('机场', 'plane'), ('茶', 'tea'), ('牛奶', 'milk'), ('面包', 'bread'), ('苹果', 'apple'), ('水', 'water_glass'), ('火车', 'train'), ('票', 'ticket')):
    icon_for(w, ic)


@picture('你好')
def _(x: int, y: int) -> None:
    picto.person(x + 9, y + 29, P.DARK_BLUE, arm='up')
    picto.person(x + 23, y + 29, P.VERMILION, arm='up')


@picture('谢谢')
def _(x: int, y: int) -> None:
    picto.person(x + 8, y + 29, P.JADE, arm='out')
    picto.person(x + 20, y + 29, P.DARK_BLUE, arm='bow')
    pyxel.pset(x + 13, y + 16, P.YELLOW)


@picture('再见')
def _(x: int, y: int) -> None:
    picto.door(x + 2, y + 11)
    picto.person(x + 22, y + 29, P.DARK_BLUE, arm='up')
    picto.arrow(x + 26, y + 6, x + 31, y + 6, P.VERMILION)


@picture('请')
def _(x: int, y: int) -> None:
    picto.person(x + 9, y + 29, P.VERMILION, arm='out')
    picto.sitting(x + 24, y + 29, P.MIST)


@picture('我')
def _(x: int, y: int) -> None:
    picto.person(x + 16, y + 29, P.DARK_BLUE, arm='self')
    picto.arrow(x + 27, y + 8, x + 19, y + 15, P.VERMILION)


@picture('人')
def _(x: int, y: int) -> None:
    picto.person(x + 16, y + 29, P.JADE)


@picture('中国')
def _(x: int, y: int) -> None:
    picto.flag(x + 4, y + 5, 'cn')


@picture('俄罗斯')
def _(x: int, y: int) -> None:
    picto.flag(x + 4, y + 5, 'ru')


@picture('外')
def _(x: int, y: int) -> None:
    pyxel.rectb(x + 2, y + 10, 14, 20, P.STONE)
    picto.person(x + 24, y + 29, P.OCHRE)
    picto.icon('plane', x + 16, y - 2)


def _num(n: int):
    def draw(x: int, y: int) -> None:
        picto.dots(n, x + 6, y + 10)
    return draw


for _i, _g in enumerate('一二三四五六七八九十', 1):
    picture(_g)(_num(_i))


@picture('站')
def _(x: int, y: int) -> None:
    pyxel.rect(x, y + 24, 32, 8, P.STONE)
    pyxel.line(x + 24, y + 6, x + 24, y + 24, P.INK)
    pyxel.rect(x + 18, y + 4, 12, 6, P.DARK_BLUE)
    picto.person(x + 10, y + 26, P.VERMILION)


@picture('进')
def _(x: int, y: int) -> None:
    picto.door(x + 18, y + 8)
    picto.arrow(x + 2, y + 18, x + 16, y + 18, P.JADE)


@picture('出口')
def _(x: int, y: int) -> None:
    pyxel.rect(x + 2, y + 2, 28, 10, P.JADE)
    picto.arrow(x + 8, y + 7, x + 24, y + 7, P.WHITE)
    picto.door(x + 4, y + 13)
    picto.arrow(x + 18, y + 22, x + 30, y + 22, P.VERMILION)


@picture('块')
def _(x: int, y: int) -> None:
    picto.icon('coins', x + 8, y + 8)


@picture('两')
def _(x: int, y: int) -> None:
    picto.icon('coins', x, y + 8)
    picto.icon('coins', x + 14, y + 8)


@picture('钱')
def _(x: int, y: int) -> None:
    picto.icon('money', x + 8, y + 4)
    picto.icon('money', x + 8, y + 12)


@picture('点')
def _(x: int, y: int) -> None:
    picto.clock(x + 16, y + 16, 13, 10, 0, 'hour')


@picture('分')
def _(x: int, y: int) -> None:
    picto.clock(x + 16, y + 16, 13, 10, 20, 'minute')


@picture('号')
def _(x: int, y: int) -> None:
    pyxel.rect(x + 6, y + 8, 20, 14, P.WHITE)
    pyxel.rectb(x + 6, y + 8, 20, 14, P.INK)
    pyxel.text(x + 11, y + 12, 'No8', P.INK)


@picture('去')
def _(x: int, y: int) -> None:
    picto.icon('house', x, y + 10)
    picto.person(x + 22, y + 29, P.DARK_BLUE)
    picto.arrow(x + 18, y + 6, x + 30, y + 6, P.VERMILION)


@picture('来')
def _(x: int, y: int) -> None:
    picto.icon('house', x + 16, y + 10)
    picto.person(x + 8, y + 29, P.DARK_BLUE)
    picto.arrow(x + 4, y + 6, x + 16, y + 6, P.JADE)


@picture('看')
def _(x: int, y: int) -> None:
    picto.eye(x + 12, y + 16)
    for i in range(3):
        pyxel.pset(x + 22 + i * 3, y + 16, P.STONE)


@picture('买')
def _(x: int, y: int) -> None:
    picto.icon('bag', x + 2, y + 8)
    picto.icon('coins', x + 16, y + 10)


@picture('给')
def _(x: int, y: int) -> None:
    picto.person(x + 7, y + 29, P.DARK_BLUE, arm='out')
    picto.person(x + 25, y + 29, P.VERMILION)
    picto.icon('apple', x + 9, y + 6)
    picto.arrow(x + 10, y + 4, x + 22, y + 4, P.JADE)


@picture('要')
def _(x: int, y: int) -> None:
    picto.person(x + 8, y + 29, P.JADE, arm='out')
    picto.icon('apple', x + 16, y + 10)


@picture('学生')
def _(x: int, y: int) -> None:
    picto.person(x + 12, y + 29, P.JADE)
    picto.icon('diary', x + 16, y + 10)


@picture('名字')
def _(x: int, y: int) -> None:
    pyxel.rect(x + 3, y + 9, 26, 14, P.WHITE)
    pyxel.rectb(x + 3, y + 9, 26, 14, P.VERMILION)
    pyxel.rect(x + 3, y + 9, 26, 4, P.VERMILION)
    pyxel.line(x + 7, y + 17, x + 24, y + 17, P.INK)
    pyxel.line(x + 7, y + 20, x + 18, y + 20, P.INK)


@picture('叫')
def _(x: int, y: int) -> None:
    picto.person(x + 9, y + 29, P.DARK_BLUE)
    for i in range(3):
        pyxel.circb(x + 14, y + 15, 3 + i * 3, P.VERMILION)


@picture('坐')
def _(x: int, y: int) -> None:
    picto.sitting(x + 16, y + 29, P.DARK_BLUE)


@picture('说')
def _(x: int, y: int) -> None:
    picto.person(x + 8, y + 29, P.DARK_BLUE)
    picto.bubble(x + 12, y + 2, 18, 10)
    pyxel.line(x + 15, y + 6, x + 26, y + 6, P.STONE)


@picture('黄')
def _(x: int, y: int) -> None:
    picto.swatch(x, y, P.YELLOW)


@picture('红')
def _(x: int, y: int) -> None:
    picto.swatch(x, y, P.VERMILION)


@picture('河')
def _(x: int, y: int) -> None:
    pyxel.rect(x, y, 32, 32, P.MOSS)
    for i in range(32):
        cx = x + 16 + round(pyxel.sin(i * 12) * 6)
        pyxel.line(cx - 4, y + i, cx + 4, y + i, P.TEAL)


@picture('山')
def _(x: int, y: int) -> None:
    picto.icon('mountain', x + 8, y + 8, 1.8)


@picture('北')
def _(x: int, y: int) -> None:
    picto.compass(x, y, 'N')


@picture('南')
def _(x: int, y: int) -> None:
    picto.compass(x, y, 'S')


@picture('京')
def _(x: int, y: int) -> None:
    pyxel.rect(x + 4, y + 16, 24, 14, P.VERMILION)
    pyxel.rect(x + 13, y + 22, 6, 8, P.INK)
    kit.canvas(pyxel)
    kit.roof(x + 6, y + 15, 20, 5, P.INK, P.STONE)
    pyxel.rect(x + 11, y + 6, 10, 6, P.VERMILION)
    kit.roof(x + 9, y + 6, 14, 4, P.INK, P.STONE)


@picture('电')
def _(x: int, y: int) -> None:
    pyxel.tri(x + 18, y + 2, x + 8, y + 18, x + 16, y + 18, P.YELLOW)
    pyxel.tri(x + 16, y + 14, x + 24, y + 14, x + 12, y + 30, P.YELLOW)


@picture('中文')
def _(x: int, y: int) -> None:
    pyxel.rect(x + 4, y + 4, 24, 24, P.PAPER)
    pyxel.rectb(x + 4, y + 4, 24, 24, P.STONE)
    from ...engine import text

    text.draw(x + 10, y + 9, '字', P.INK)
    picto.icon('brush', x + 16, y - 2)


@picture('欢迎')
def _(x: int, y: int) -> None:
    pyxel.rect(x + 2, y + 2, 28, 7, P.VERMILION)
    picto.person(x + 16, y + 30, P.JADE, arm='wide')


@picture('到')
def _(x: int, y: int) -> None:
    pyxel.line(x + 24, y + 4, x + 24, y + 26, P.INK)
    pyxel.tri(x + 24, y + 4, x + 30, y + 8, x + 24, y + 12, P.VERMILION)
    picto.arrow(x + 2, y + 22, x + 20, y + 22, P.JADE)


@picture('饿')
def _(x: int, y: int) -> None:
    pyxel.elli(x + 6, y + 14, 20, 10, P.WHITE)
    pyxel.ellib(x + 6, y + 14, 20, 10, P.INK)
    pyxel.line(x + 6, y + 18, x + 25, y + 18, P.STONE)
    pyxel.text(x + 10, y + 4, '...', P.STONE)


@sketch('train_1958')
def _(x: int, y: int) -> None:
    pyxel.rect(x, y + 34, 80, 10, P.PEACH)
    pyxel.line(x, y + 38, x + 80, y + 38, P.INK)
    pyxel.rect(x + 10, y + 20, 34, 14, P.INK)
    pyxel.rect(x + 36, y + 12, 8, 10, P.INK)
    pyxel.rect(x + 46, y + 22, 24, 12, P.INK)
    for cx in (16, 28, 40, 52, 64):
        pyxel.circb(x + cx, y + 35, 3, P.INK)
    for i in range(4):
        pyxel.circb(x + 38 - i * 6, y + 8 - i * 2, 2 + i, P.STONE)


words.add('''
你好 — здравствуй
谢谢 — спасибо
再见 — до свидания
中国 — Китай
护照 — паспорт
飞机 — самолёт
手机 — мобильный телефон
洗手间 — туалет
火车站 — вокзал
火车 — поезд
出租车 — такси
咖啡 — кофе
牛奶 — молоко
面包 — хлеб
苹果 — яблоко
水果 — фрукты
名字 — имя
学生 — ученик, студент
什么 — что
哪儿 — где, куда
多少 — сколько
欢迎 — добро пожаловать
北京 — Пекин
汉语 — китайский язык
没有 — нет, не иметь
一点儿 — немного
看见 — увидеть
''')

# ---------------------------------------------------------------- hints

hints.add(lambda s: s.scene == '1a' and not s.on('passport_ok') and 'passport' in s.inventory and not s.on('officer_met'),
          'Пограничник за стойкой ждёт. Подойдите к нему.')
hints.add(lambda s: s.scene == '1a' and not s.on('passport_ok'),
          'Пограничник протягивает руку к документам. Выберите паспорт (护照) в сумке внизу и покажите ему. На вопрос отвечайте его же словами: «да» по-китайски — это повторённый глагол, 是.')
hints.add(lambda s: s.scene == '1a' and 'suitcase' not in s.inventory,
          'Мой чемодан — красный, как в квартире деда. Остальные чужие.')
hints.add(lambda s: s.scene == '1b' and 'ticket' not in s.inventory and not s.on('price_asked'),
          'Касса слева, над ней 买票. Спросят, куда едете: на конверте написано 泰山.')
hints.add(lambda s: s.scene == '1b' and 'ticket' not in s.inventory,
          'Кассирша назвала цену. Выберите 钱 в сумке и отдайте ей.')
hints.add(lambda s: s.scene == '1b' and not s.on('gate_ok'),
          'С билетом — к проходу 进站 справа. Покажите билет.')
hints.add(lambda s: s.scene == '1c' and not s.on('seated'),
          'Какое место в билете? Откройте дневник → «Тексты» → «Билет» и сравните с табличками над креслами.')
hints.add(lambda s: s.scene == '1c' and not s.on('arrived'),
          'Поговорите с соседкой. Можно показать ей дневник деда.')

# ---------------------------------------------------------------- 1a · airport


def airport_art(s, look: SceneLook) -> None:
    c = kit.C
    c.rect(0, 0, 320, 180, P.GREY)
    # glass wall with the apron outside
    c.rect(0, 10, 320, 62, P.LIGHT_BLUE)
    c.rect(0, 52, 320, 20, P.STONE)
    kit.cloud(40, 18, 40, P.WHITE, P.MIST)
    kit.cloud(220, 24, 30, P.WHITE, P.MIST)
    # a plane at the gate
    c.rect(150, 40, 80, 10, P.WHITE)
    c.tri(226, 40, 246, 40, 236, 24, P.WHITE)
    c.tri(232, 40, 242, 40, 238, 26, P.VERMILION)
    c.elli(144, 40, 14, 10, P.WHITE)
    c.tri(180, 50, 210, 50, 190, 58, P.WHITE)
    for wx in range(158, 222, 6):
        c.rect(wx, 43, 3, 2, P.DARK_BLUE)
    for x in range(0, 320, 40):
        c.rect(x, 10, 2, 62, P.PAPER)
    c.rect(0, 10, 320, 2, P.PAPER)
    c.rect(0, 70, 320, 3, P.PAPER)
    c.rect(0, 0, 320, 10, P.PAPER)
    for x in range(10, 320, 30):
        c.rect(x, 3, 12, 2, P.LAMP)
    # back wall
    kit.panel_wall(73, 118, P.MIST, P.GREY)
    kit.tiles(118, P.PAPER, P.MIST, 16)
    # passport booth
    c.rect(34, 96, 58, 26, P.DARK_BLUE)
    c.rect(38, 100, 50, 18, P.LIGHT_BLUE)
    c.rect(34, 90, 58, 6, P.NAVY)
    # baggage belt
    c.rect(146, 128, 124, 12, P.INK)
    c.rect(146, 126, 124, 3, P.STONE)
    for x in range(148, 268, 6):
        c.pset(x, 133, P.GREY)
    c.rect(146, 140, 124, 6, P.STONE)
    if 'suitcase' not in s.inventory:
        c.rect(158, 116, 18, 12, P.VERMILION)
        c.rect(158, 116, 18, 2, P.LACQUER)
        c.rect(164, 113, 6, 3, P.INK)
    if not s.on('black_taken'):
        c.rect(190, 114, 20, 14, P.INK)
        c.rect(197, 111, 6, 3, P.STONE)
    if not s.on('blue_taken'):
        c.rect(228, 118, 14, 10, P.DARK_BLUE)
        c.rect(233, 115, 4, 3, P.INK)
    # exit doorway
    c.rect(296, 76, 24, 70, P.INK)
    c.rect(300, 80, 20, 66, P.LIGHT_BLUE)
    kit.plant_pot(270, 150)
    kit.plant_pot(116, 150)


def airport_front(s, look: SceneLook) -> None:
    c = kit.C
    c.rect(30, 132, 66, 20, P.DARK_BLUE)
    c.rect(28, 128, 70, 5, P.MIST)
    c.rect(36, 138, 54, 2, P.NAVY)


async def airport_enter(c: ScriptContext) -> None:
    if c.flag('ch1'):
        return
    c.set('ch1')
    c.state.coins = 200
    await c.chapter(1)
    for it in ('passport', 'phone', 'money'):
        c.give(it)
    await c.narrate('Аэропорт Цзинаня. Вокруг — только знаки. Ни одной понятной буквы.')
    await c.narrate('Телефон сел ещё в самолёте. Чемодан где-то на ленте. Сначала — паспортный контроль.')
    await c.say('officer', '你好！')


async def officer_talk(c: ScriptContext) -> None:
    if c.flag('passport_ok'):
        await cycle(c, 'officer_n', 'officer', ['欢迎来中国！', '再见！'])
        return
    if not c.flag('officer_met'):
        c.set('officer_met')
        await c.say('officer', '你好！请给我你的护照。')
        await c.narrate('Пограничник кивает на мои документы и протягивает руку.')
        return
    await c.say('officer', '护照！请给我你的护照。')


async def officer_item(c: ScriptContext, item: str) -> bool:
    if c.flag('passport_ok'):
        await c.say('officer', '欢迎来中国！')
        return True
    if item == 'phone':
        await c.say('officer', '手机？不是护照。')
        return True
    if item != 'passport':
        await c.say('officer', '这不是护照。')
        return True
    c.set('officer_met')
    await c.say('officer', '谢谢。')
    await c.narrate('Он листает паспорт, смотрит на визу, потом на меня.')
    while True:
        answer = await c.ask('officer', '你是俄罗斯人吗？')
        if yes(answer) or has_all(answer, '俄罗斯'):
            break
        if no(answer):
            await c.say('officer', '不是？')
            await c.narrate('Он поднимает бровь и стучит пальцем по паспорту.')
            await c.say('officer', '你是俄罗斯人！')
            break
        if not answer:
            return True
        await c.narrate('Он ждёт. Кажется, ответ может быть совсем коротким — его же словом.')
    await c.say('officer', '好！欢迎来中国！')
    c.sfx('stamp')
    await c.narrate('Щёлк — штамп. Пограничник возвращает паспорт и машет рукой: проходите.')
    c.set('passport_ok')
    return True


async def traveler_talk(c: ScriptContext) -> None:
    await cycle(c, 'traveler_n', 'traveler', ['你好。', '这是我的行李箱。'])


async def girl_talk(c: ScriptContext) -> None:
    await cycle(c, 'girl_n', 'girl', ['你好！', '我的行李箱是小的。'])


async def staff_talk(c: ScriptContext) -> None:
    n = int(c.flag('staff_n') or 0)
    if n % 2 == 0:
        await c.say('staff', '你好！出口在那儿。')
        await c.event('point-exit')
    else:
        await c.say('staff', '洗手间在这儿。')
        await c.event('point-wc')
    c.set('staff_n', n + 1)


async def belt_guard(c: ScriptContext) -> bool:
    if c.flag('passport_ok'):
        return True
    await c.say('officer', '你好！护照！')
    await c.narrate('Сначала паспортный контроль.')
    return False


async def red_case(c: ScriptContext) -> None:
    if not await belt_guard(c):
        return
    await c.narrate('Мой красный чемодан! Цел.')
    c.give('suitcase')


async def black_case(c: ScriptContext) -> None:
    if not await belt_guard(c):
        return
    await c.say('traveler', '这是我的！不是你的！')
    await c.narrate('Мужчина вежливо, но твёрдо забирает чёрный чемодан.')
    c.set('black_taken')
    c.set('traveler_gone')


async def blue_case(c: ScriptContext) -> None:
    if not await belt_guard(c):
        return
    await c.say('girl', '这是我的！')
    await c.narrate('Девушка подхватывает синий чемоданчик и улыбается.')
    c.set('blue_taken')


async def airport_exit(c: ScriptContext) -> bool:
    if not c.flag('passport_ok'):
        await c.say('officer', '你好！护照！')
        return False
    if 'suitcase' not in c.state.inventory:
        await c.narrate('Без чемодана? Там запасная одежда и тёплая куртка. Надо забрать его с ленты.')
        return False
    await c.narrate('Автобус от аэропорта до вокзала. За окном — поля, заводы, бесконечные стройки.')
    return True


register(
    SceneDef(
        id='1a', chapter=1, title='Аэропорт Цзинаня', zh='机场',
        art=airport_art, front=airport_front, look=lambda s: SceneLook('day'),
        path=[(14, 162), (160, 164), (296, 160)],
        entries={'gate': 110},
        actors=[
            ActorDef('officer', 'Пограничник', OFFICER, 62, 140, 'right', stand_at=106,
                     on_talk=officer_talk, on_item=officer_item),
            ActorDef('traveler', 'Мужчина с чёрным чемоданом', fig(P.STONE, P.INK, 'jacket', 'short', glasses=True), 214, 162, 'left',
                     visible=lambda s: not s.on('traveler_gone'), on_talk=traveler_talk),
            ActorDef('girl', 'Девушка', fig(P.PINK, P.WHITE, 'dress', 'ponytail'), 252, 163, 'left',
                     visible=lambda s: not s.on('blue_taken'), on_talk=girl_talk),
            ActorDef('staff', 'Сотрудница аэропорта', STAFF, 284, 161, 'left', stand_at=262, on_talk=staff_talk),
        ],
        hotspots=[
            HotspotDef('red', 'Красный чемодан', (156, 110, 22, 18), stand_at=166, on_click=red_case,
                       visible=lambda s: 'suitcase' not in s.inventory, cursor='hand'),
            HotspotDef('black', 'Чёрный чемодан', (188, 108, 24, 20), stand_at=198, on_click=black_case,
                       visible=lambda s: not s.on('black_taken'), cursor='hand'),
            HotspotDef('blue', 'Синий чемодан', (226, 112, 18, 16), stand_at=234, on_click=blue_case,
                       visible=lambda s: not s.on('blue_taken'), cursor='hand'),
        ],
        signs=[
            SignDef('welcome', '欢迎', 130, 14, 'banner'),
            SignDef('airport', '机场', 6, 14, 'blue'),
            SignDef('foreign', '外国人', 43, 76, 'blue'),
            SignDef('wc', '洗手间', 100, 80, 'blue'),
            SignDef('exit', '出口', 280, 60, 'lit'),
        ],
        exits=[ExitDef('out', '1b', 'door', (298, 80, 22, 70), 'right', 300, 'Выход', guard=airport_exit)],
        marks={'exit': (300, 70), 'wc': (112, 76)},
        on_enter=airport_enter,
        music='travel',
    )
)

# ---------------------------------------------------------------- 1b · station

MENU = {'咖啡': ('coffee', 20), '茶': ('tea', 10), '牛奶': ('milk', 8), '面包': ('bread', 6), '苹果': ('apple', 3), '水': ('water_cup', 2)}


def station_art(s, look: SceneLook) -> None:
    c = kit.C
    c.rect(0, 0, 320, 180, P.MIST)
    # high windows and roof trusses
    for x in range(0, 320, 64):
        c.rect(x + 8, 6, 48, 28, P.LIGHT_BLUE)
        c.line(x + 32, 6, x + 32, 34, P.PAPER)
        c.tri(x, 4, x + 32, 0, x + 64, 4, P.GREY)
    c.rect(0, 0, 320, 4, P.STONE)
    kit.panel_wall(34, 122, P.PAPER, P.GREY)
    kit.tiles(122, P.GREY, P.STONE, 14)
    # ticket window
    c.rect(16, 80, 70, 44, P.OCHRE)
    c.rect(22, 98, 56, 24, P.LIGHT_BLUE)
    c.rect(16, 76, 70, 4, P.WOOD)
    # departure board frame
    c.rect(98, 22, 108, 50, P.INK)
    c.rect(96, 20, 112, 3, P.STONE)
    # benches
    for bx in (126, 170):
        c.rect(bx, 140, 36, 4, P.OCHRE)
        c.rect(bx + 2, 144, 2, 8, P.INK)
        c.rect(bx + 32, 144, 2, 8, P.INK)
    # café counter
    c.rect(214, 108, 52, 4, P.PAPER)
    c.rect(214, 112, 52, 16, P.JADE)
    c.rect(210, 4, 88, 4, P.WOOD)
    # gate with turnstiles
    c.rect(282, 84, 38, 60, P.STONE)
    c.rect(286, 92, 30, 52, P.INK)
    for tx in (288, 302):
        c.rect(tx, 124, 4, 18, P.GREY)
        c.line(tx + 4, 130, tx + 10, 130, P.VERMILION)


def station_front(s, look: SceneLook) -> None:
    c = kit.C
    c.rect(14, 122, 74, 30, P.OCHRE)
    c.rect(12, 120, 78, 3, P.WOOD)
    c.rect(212, 128, 56, 22, P.JADE)
    c.rect(210, 126, 60, 3, P.PAPER)


async def station_enter(c: ScriptContext) -> None:
    if c.flag('station_in'):
        return
    c.set('station_in')
    await c.narrate('Вокзал. Над кассами табло, у буфета очередь, у прохода на перрон — турникеты.')


async def clerk_talk(c: ScriptContext) -> None:
    if c.has('ticket'):
        await cycle(c, 'clerk_n', 'clerk', ['十点二十。', '再见！'])
        return
    if c.flag('price_asked'):
        await c.say('clerk', '去泰安，五十块。')
        return
    answer = await c.ask('clerk', '你好！你要去哪儿？')
    a = normalize(answer)
    if '泰山' in a or '泰安' in a:
        if '泰山' in a:
            await c.say('clerk', '泰山？去泰安！')
        await c.say('clerk', '几点的火车？十点二十分的。')
        await c.say('clerk', '去泰安，五十块。')
        c.set('price_asked')
        return
    if a:
        await c.say('clerk', '你去哪儿？北京？南京？泰安？')
        await c.narrate('Она показывает на табло. Куда мне? На конверте деда было написано…')


async def clerk_item(c: ScriptContext, item: str) -> bool:
    if c.has('ticket'):
        await c.say('clerk', '你有票了。')
        return True
    if item == 'letter':
        await c.say('clerk', '泰山？去泰安！五十块。')
        c.set('price_asked')
        return True
    if item == 'phone':
        await c.say('clerk', '手机没电了？给我钱。')
        return True
    if item == 'money' and c.flag('price_asked'):
        if await pay(c, 'clerk', 50, item):
            await c.say('clerk', '好！这是你的票。')
            c.give('ticket')
            c.unlock('ticket')
            await c.read('ticket')
        return True
    if item == 'money':
        await c.say('clerk', '你去哪儿？')
        return True
    return False


async def waitress_talk(c: ScriptContext) -> None:
    pending = c.flag('cafe_order')
    if pending:
        await c.say('waitress', f'{pending}，{_price_text(pending)}。')
        return
    answer = await c.ask('waitress', '你好！你要什么？')
    a = normalize(answer)
    for name in MENU:
        if name in a:
            c.set('cafe_order', name)
            await c.say('waitress', f'{name}？{_price_text(name)}。')
            return
    if a:
        await c.say('waitress', '咖啡？茶？牛奶？面包？苹果？水？')


def _price_text(name: str) -> str:
    from ...core.numerals import to_hanzi

    price = MENU[name][1]
    return ('两' if price == 2 else to_hanzi(price)) + '块'


async def waitress_item(c: ScriptContext, item: str) -> bool:
    pending = c.flag('cafe_order')
    if item == 'money' and pending:
        it, price = MENU[pending]
        if await pay(c, 'waitress', price, item):
            await c.say('waitress', '谢谢！给你。')
            c.give(it)
            c.set('cafe_order', '')
        return True
    if item == 'money':
        await c.say('waitress', '你要什么？')
        return True
    return False


async def kid_talk(c: ScriptContext) -> None:
    if c.flag('kid_fed'):
        await cycle(c, 'kid_n', 'kid', ['谢谢！', '再见！'])
        return
    if not c.flag('kid_met'):
        c.set('kid_met')
        answer = await c.ask('kid', '你好！你是哪国人？')
        if '俄罗斯' in normalize(answer):
            await c.say('kid', '俄罗斯！')
            await c.say('granny', '你好！你去哪儿？')
        else:
            await c.say('granny', '你好！')
        return
    await c.say('kid', '我饿了。我要面包！')
    await c.narrate('Мальчик смотрит на буфет и тянет бабушку за рукав.')


async def kid_item(c: ScriptContext, item: str) -> bool:
    if c.flag('kid_fed'):
        await c.say('kid', '谢谢！')
        return True
    if item == 'bread':
        c.take('bread')
        c.set('kid_fed')
        await c.say('kid', '面包！谢谢！')
        await c.say('granny', '谢谢你！这是苹果，给你。')
        c.give('apple')
        return True
    if item in ('coffee', 'tea', 'milk', 'water_cup'):
        await c.say('kid', '不要。我要面包！')
        return True
    return False


async def granny_talk(c: ScriptContext) -> None:
    if c.flag('kid_fed'):
        await c.say('granny', '谢谢你！再见！')
        return
    answer = await c.ask('granny', '你去哪儿？')
    a = normalize(answer)
    if '泰' in a:
        await c.say('granny', '泰山！好！')
    elif a:
        await c.say('granny', '好。')


async def gate_talk(c: ScriptContext) -> None:
    if c.flag('gate_ok'):
        await c.say('gatekeeper', '请进！')
        return
    await c.say('gatekeeper', '你好！票？')


async def gate_item(c: ScriptContext, item: str) -> bool:
    if item == 'ticket':
        await c.say('gatekeeper', '泰安，十点二十分。火车在那儿。请进！')
        c.set('gate_ok')
        return True
    await c.say('gatekeeper', '票！')
    return True


async def gate_guard(c: ScriptContext) -> bool:
    if c.flag('gate_ok'):
        return True
    await c.say('gatekeeper', '票！')
    return False


register(
    SceneDef(
        id='1b', chapter=1, title='Вокзал', zh='火车站',
        art=station_art, front=station_front, look=lambda s: SceneLook('day'),
        path=[(10, 164), (160, 166), (304, 162)],
        entries={'door': 20},
        actors=[
            ActorDef('clerk', 'Кассирша', fig(P.VERMILION, P.WHITE, 'uniform', 'bun'), 50, 136, 'right', stand_at=96,
                     on_talk=clerk_talk, on_item=clerk_item),
            ActorDef('granny', 'Бабушка', fig(P.PLUM, P.PAPER, 'jacket', 'bun', kind='old', pose='sit'), 136, 146, 'right', stand_at=118,
                     on_talk=granny_talk),
            ActorDef('kid', 'Мальчик', fig(P.YELLOW, P.VERMILION, 'jacket', 'short', kind='child'), 158, 158, 'left', stand_at=178,
                     on_talk=kid_talk, on_item=kid_item),
            ActorDef('waitress', 'Буфетчица', fig(P.JADE, P.WHITE, 'jacket', 'ponytail'), 240, 132, 'left', stand_at=228,
                     on_talk=waitress_talk, on_item=waitress_item),
            ActorDef('gatekeeper', 'Контролёр', STAFF, 296, 160, 'left', stand_at=274, on_talk=gate_talk, on_item=gate_item),
        ],
        signs=[
            SignDef('buy', '买票', 38, 84, 'plaque'),
            SignDef('board', '北京　九点\n泰安　十点二十\n南京　十一点', 101, 25, 'screen'),
            SignDef('menu', '咖啡　二十块\n茶　　十块\n牛奶　八块\n面包　六块\n苹果　三块\n水　　两块', 212, 8, 'board'),
            SignDef('in', '进站', 285, 70, 'lit'),
            SignDef('out', '出站', 4, 70, 'lit'),
        ],
        exits=[ExitDef('platform', '1c', 'door', (284, 90, 36, 60), 'right', 300, 'На перрон', guard=gate_guard)],
        on_enter=station_enter,
        music='travel',
    )
)

# ---------------------------------------------------------------- 1c · train

SEATS = '一二三四五六七八'
SEAT_X = [22 + i * 38 for i in range(8)]


def train_art(s, look: SceneLook) -> None:
    c = kit.C
    c.rect(0, 0, 320, 180, P.PAPER)
    c.rect(0, 0, 320, 16, P.GREY)
    for x in range(0, 320, 20):
        c.rect(x + 4, 6, 12, 3, P.LAMP)
    # windows (the view is drawn in anim)
    for wx in range(8, 320, 78):
        c.rect(wx, 20, 66, 46, P.INK)
    c.rect(0, 66, 320, 4, P.GREY)
    kit.panel_wall(70, 150, P.PAPER, P.GREY)
    # seats: backs facing the aisle
    for i, x in enumerate(SEAT_X):
        c.rect(x - 10, 96, 22, 40, P.DARK_BLUE)
        c.rect(x - 10, 96, 22, 6, P.WHITE)
        c.rect(x - 10, 134, 26, 6, P.DARK_BLUE)
    kit.tiles(150, P.GREY, P.STONE, 20)
    c.rect(306, 70, 14, 80, P.STONE)


def train_anim(s, look: SceneLook, frame: int) -> None:
    """The landscape rolls past the windows."""
    view = 'mountain' if s.on('saw_taishan') else 'river' if s.on('saw_river') and not s.on('river_passed') else 'fields'
    for wx in range(8, 320, 78):
        pyxel.clip(wx + 2, 22, 62, 42)
        pyxel.rect(wx + 2, 22, 62, 42, P.LIGHT_BLUE)
        off = frame * 2
        if view == 'river':
            pyxel.rect(wx + 2, 44, 62, 20, P.OCHRE)
            for i in range(6):
                lx = wx + 2 + (i * 17 - off) % 70
                pyxel.line(lx, 50 + i % 3 * 4, lx + 6, 50 + i % 3 * 4, P.YELLOW)
            for i in range(0, 80, 10):
                gx = wx + 2 + (i - off * 2) % 80
                pyxel.line(gx, 22, gx, 44, P.STONE)
            pyxel.line(wx + 2, 40, wx + 64, 40, P.STONE)
        else:
            if view == 'mountain':
                for k in range(3):
                    mx = wx + 30 + k * 30 - (off // 4) % 60
                    pyxel.tri(mx - 20, 50, mx + 20, 50, mx, 26 - k * 3, P.STONE if k != 1 else P.PERIWINKLE)
            pyxel.rect(wx + 2, 50, 62, 14, P.MOSS)
            for i in range(5):
                tx = wx + 2 + (i * 23 - off) % 80
                pyxel.rect(tx, 42, 2, 8, P.WOOD)
                pyxel.circ(tx + 1, 40, 4, P.JADE)
            for i in range(3):
                px = wx + 2 + (i * 31 - off * 2) % 90
                pyxel.line(px, 30, px, 50, P.INK)
        pyxel.clip()


async def train_enter(c: ScriptContext) -> None:
    if c.flag('train_in'):
        return
    c.set('train_in')
    await c.narrate('Поезд до Тайаня. Вагон полон: кто спит, кто ест лапшу. Над креслами таблички с номерами.')
    await c.narrate('В билете есть номер места. Какой?')
    await c.read('ticket')


def seat_click(n: int):
    async def click(c: ScriptContext) -> None:
        if c.flag('seated'):
            await c.narrate('Моё место — у окна, рядом со студенткой.')
            return
        if n == 8:
            c.set('seated')
            await c.move('player', SEAT_X[7] - 4)
            await c.narrate('Место восемь. Сажусь у окна. Соседка откладывает книгу.')
            await c.say('student', '你好！')
            return
        if n in (2, 4, 5, 7):
            await c.say(f'p{n}' if n != 7 else 'student', '这是我的。')
            return
        answer = await c.ask('conductor', '你好！你是几号？')
        if '八' in normalize(answer):
            await c.say('conductor', '八号在那儿。')
            await c.event('point-seat8')
        else:
            await c.say('conductor', '你的票？')
    return click


STUDENT_LINES = [
    '你好！你是哪国人？',
    '你坐飞机来中国的吗？',
    '我是学生。我叫小红。你叫什么名字？',
    'diary',
    'phone',
    'river',
    'taishan',
    'arrive',
]


async def student_talk(c: ScriptContext) -> None:
    if not c.flag('seated'):
        await c.say('student', '你好！')
        return
    step = int(c.flag('student_step') or 0)
    kind = STUDENT_LINES[min(step, len(STUDENT_LINES) - 1)]
    if kind == '你好！你是哪国人？':
        answer = await c.ask('student', kind)
        if '俄罗斯' in normalize(answer):
            await c.say('student', '俄罗斯！好！')
    elif kind == '你坐飞机来中国的吗？':
        answer = await c.ask('student', kind)
        if yes(answer) or '飞机' in normalize(answer):
            await c.say('student', '我也坐飞机！')
        elif no(answer):
            await c.say('student', '不是？……火车？')
    elif kind.startswith('我是学生'):
        answer = await c.ask('student', kind)
        if '安' in normalize(answer):
            await c.say('student', '安？好名字！')
        elif answer:
            await c.say('student', '好名字！')
    elif kind == 'diary':
        await c.narrate('Она кивает на тетрадь деда у меня на коленях.')
        await c.say('student', '这是什么？')
        return  # the story goes on when the diary is shown
    elif kind == 'phone':
        await c.say('student', '你有手机吗？')
        await c.narrate('Показываю ей чёрный экран телефона.')
        await c.say('student', '手机没电了！')
        await c.narrate('Она смеётся и что-то быстро печатает в своём телефоне. Мне не показывает — дед бы одобрил.')
    elif kind == 'river':
        c.set('saw_river')
        await c.say('student', '看！黄河！')
        await c.event('river')
        await c.narrate('За окном широкая мутно-жёлтая река. Поезд идёт по длинному мосту.')
        c.set('river_passed')
    elif kind == 'taishan':
        c.set('saw_taishan')
        await c.say('student', '那是泰山！')
        await c.narrate('На горизонте поднимается гора. Выше соседних, темнее, в облачной шапке.')
    else:
        c.set('arrived')
        await c.say('speaker', '泰安站到了。')
        await c.say('student', '泰安到了！再见！')
        return
    c.set('student_step', step + 1)


async def student_item(c: ScriptContext, item: str) -> bool:
    step = int(c.flag('student_step') or 0)
    if item == 'diary' and STUDENT_LINES[min(step, len(STUDENT_LINES) - 1)] == 'diary':
        await c.say('student', '日记？一九五八年！')
        await c.narrate('Она осторожно открывает тетрадь и читает вслух первую строчку, водя пальцем по знакам.')
        await c.say('student', '我叫安德烈。我是俄罗斯人。我不会说中文。')
        c.unlock('diary_1')
        await c.say('student', '你也不会说中文！')
        await c.narrate('Она смеётся, и я смеюсь вместе с ней. Ну да, я тоже не умею.')
        c.set('student_step', step + 1)
        return True
    if item == 'diary':
        await c.say('student', '日记？')
        return True
    if item == 'apple':
        await c.say('student', '苹果？不要，谢谢！')
        return True
    return False


async def train_exit(c: ScriptContext) -> bool:
    if not c.flag('arrived'):
        await c.narrate('Поезд ещё идёт. Выходить некуда.')
        return False
    await c.narrate('Перрон Тайаня. Воздух пахнет жареными каштанами и дождём.')
    return True


register(
    SceneDef(
        id='1c', chapter=1, title='Поезд до Тайаня', zh='火车',
        art=train_art, anim=train_anim, look=lambda s: SceneLook('day'),
        path=[(8, 166), (300, 166)],
        entries={'door': 290},
        actors=[
            ActorDef('student', 'Студентка', fig(P.JADE, P.WHITE, 'jacket', 'long', pose='sit', prop='book'), SEAT_X[6], 140, 'right',
                     stand_at=SEAT_X[6] + 14, on_talk=student_talk, on_item=student_item),
            ActorDef('p2', 'Пассажир', fig(P.STONE, P.INK, 'jacket', 'cap', pose='sit'), SEAT_X[1], 140, 'right'),
            ActorDef('p4', 'Пассажирка', fig(P.ROSE, P.WHITE, 'dress', 'bun', pose='sit'), SEAT_X[3], 140, 'right'),
            ActorDef('p5', 'Старик', fig(P.WOOD, P.OCHRE, 'jacket', 'bald', kind='old', pose='sit', beard=True), SEAT_X[4], 140, 'right'),
            ActorDef('conductor', 'Проводница', STAFF, 60, 166, 'right'),
        ],
        hotspots=[HotspotDef(f'seat{i + 1}', f'Кресло {i + 1}', (x - 10, 96, 22, 40), stand_at=x, on_click=seat_click(i + 1), cursor='hand')
                  for i, x in enumerate(SEAT_X)],
        signs=[SignDef(f'n{i + 1}', f'{g}号', x - 13, 80, 'tag') for i, (g, x) in enumerate(zip(SEATS, SEAT_X))],
        exits=[ExitDef('out', '2a', 'station', (306, 70, 14, 80), 'right', 300, 'Выход', guard=train_exit)],
        marks={'speaker': (160, 18), 'seat8': (SEAT_X[7], 90)},
        on_enter=train_enter,
        music='train',
    )
)

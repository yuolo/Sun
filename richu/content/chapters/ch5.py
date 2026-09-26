"""Chapter 5 · 中天门 «Средние ворота» — the Doumu nunnery, the Stone Sutra valley, the Horse-turning ridge, Zhongtianmen."""
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
from ._common import cycle, edit_talisman, fig, no, yes

# ---------------------------------------------------------------- items, texts, talismans, spells

items.add(
    ItemDef('fu', '符', 'talisman', 'Чистая жёлтая бумага для талисманов. Монахиня сказала: на горе написанное сбывается.'),
    ItemDef('incense', '香', 'incense', 'Три палочки благовоний.'),
    ItemDef('coat', '大衣', 'coat', 'Старая ватная куртка Ли Мина. Тёплая и пахнет чаем.'),
)

register_talisman(
    TalismanDef('doumu_gate', '门不开', {'门开': 'open', '开门': 'open', '门大开': 'open'}),
    TalismanDef('stream', '水大', {'水小': 'low', '水不大': 'low', '小水': 'low'}),
    TalismanDef('signpost', '中天门下红门上', {'中天门上红门下': 'fixed'}),
)

spells.add(
    SpellEntry('水落石出', 'idiom', 'Вода спадает — камни видны (всё тайное становится явным)', 'water_down'),
)

texts.add(
    TextDef(
        'diary_9', 'diary', 'Дневник деда · 9',
        '今天我和李明一起挑东西上中天门。\n我只挑了三十公斤，就累得走不动了。\n'
        '李明挑了六十公斤，还一边走一边唱歌。\n我问他："你不累吗？"\n他说："累。可是唱歌的时候，就不累了。"',
        '«Сегодня мы с Ли Мином несли грузы к Средним воротам. Я взял всего тридцать килограммов — и выбился из сил. '
        'Ли Мин нёс шестьдесят и ещё пел на ходу. Я спросил: „Ты не устал?“ Он ответил: „Устал. Но когда поёшь — не устаёшь“».',
        chapter=5, date='一九六零年四月十号', sketch='porters_1959',
    ),
    TextDef(
        'diary_10', 'diary', 'Дневник деда · 10',
        '今天是中秋节。李家在中天门开了一个小茶馆。\n晚上我们在茶馆外面看月亮，吃月饼。\n'
        '李明的妈妈说："月亮最圆的时候，家人都要在一起。"\n我想起了我的妈妈。',
        '«Сегодня Праздник середины осени. Семья Ли открыла у Средних ворот маленькую чайную. Вечером мы смотрели на луну и ели лунные пряники. '
        'Мама Ли Мина сказала: „Когда луна круглее всего, семья должна быть вместе“. Я вспомнил свою маму».',
        chapter=5, date='一九五九年九月十七号', sketch='moon_festival',
    ),
    TextDef(
        'diary_11', 'diary', 'Дневник деда · 11',
        '今天我们收到了回国的通知。\n还有三个月，我们就要离开中国了。\n我不想走。桥还没有修完。\n'
        '李明说："秋分的时候，我们一起上山看日出吧。"',
        '«Сегодня пришёл приказ о возвращении. Через три месяца мы уезжаем из Китая. Я не хочу уезжать. Мост ещё не достроен. '
        'Ли Мин сказал: „На осеннее равноденствие поднимемся вместе на гору встречать рассвет“».',
        chapter=5, date='一九六零年六月二号', sketch='sunrise_promise',
    ),
    TextDef(
        'sutra', 'stone', 'Каменная сутра', '如是我闻',
        '«Так я слышал» — первые слова Алмазной сутры, высеченные в камне больше тысячи лет назад.',
        chapter=5,
    ),
    TextDef(
        'bell_poem', 'stone', 'Надпись у колоколов', '雨后云开月出来',
        '«После дождя облака расходятся, и выходит луна».',
        chapter=5,
    ),
)

# ---------------------------------------------------------------- 5a · the Doumu nunnery


def doumu_look(s) -> SceneLook:
    return SceneLook('sunset')


def doumu_art(s, look: SceneLook) -> None:
    c = kit.C
    kit.sky([(P.LIGHT_BLUE, 40), (P.MIST, 30), (P.WHITE, 40)])
    kit.ridge(56, 10, 30, 121, P.PERIWINKLE, peaks=[(250, 40, 120)])
    kit.ridge(84, 8, 20, 122, P.PINE)
    kit.ground(120, P.PAPER, P.MIST, seed=123, density=0.03)
    # the courtyard wall and the gate
    kit.wall(80, 70, 180, 50, P.YELLOW, P.OCHRE, P.INK)
    kit.roof(150, 62, 60, 10, P.INK, P.STONE)
    open_ = s.on('doumu_open')
    kit.door(162, 78, 36, 42, P.LACQUER, P.GOLD, open_=open_)
    if open_:
        c.rect(166, 90, 28, 30, P.PAPER)
        c.rect(174, 96, 12, 14, P.OCHRE)
    else:
        c.rect(157, 89, 46, 20, P.YELLOW)
        c.rectb(157, 89, 46, 20, P.OCHRE)
    # an old pine over the wall and the incense burner
    kit.pine(60, 124, 50, seed=5, lean=4)
    c.rect(236, 132, 16, 12, P.OCHRE)
    c.rect(234, 130, 20, 3, P.WOOD)
    # the stream beside the path
    kit.water(150, 8, P.TEAL, P.MINT, seed=124, x0=0, x1=320)
    kit.path_band([(0, 164), (160, 166), (320, 160)], 12, P.PAPER, P.STONE)


def doumu_anim(s, look: SceneLook, frame: int) -> None:
    kit.canvas(pyxel)
    for i in range(3):
        x = 240 + i * 4 + int(pyxel.sin(frame * 6 + i * 60) * 2)
        y = 126 - (frame // 3 + i * 7) % 20
        pyxel.pset(x, y, P.MIST)
    kit.canvas(None)


async def doumu_enter(c: ScriptContext) -> None:
    if c.flag('ch5'):
        return
    c.set('ch5')
    await c.chapter(5)
    await c.narrate('Солнце клонится к западу. Обитель Доуму: жёлтая стена, ворота на запоре. На створках — жёлтая бумажка с красными знаками.')


async def pilgrim_talk(c: ScriptContext) -> None:
    if c.flag('doumu_open'):
        await cycle(c, 'pil_n', 'pilgrim5', ['门开了！真奇怪！', '你认为字真的能开门吗？', '谢谢你！'])
        return
    await c.say('pilgrim5', '你好！这个门今天不开。')
    await c.say('pilgrim5', '你看，门上写着"门不开"。山上写的字都是真的！')
    await c.say('pilgrim5', '以前有一个人把"不"字去掉了，门就开了。')
    await c.say('pilgrim5', '其实，我也想进去，可是我没有办法。')
    await c.say('pilgrim5', '我的手表没电了……天快黑了吧？')


async def gate_talisman(c: ScriptContext) -> None:
    if c.flag('doumu_open'):
        await c.narrate('Бумажка на воротах: 门开. Ворота открыты.')
        return
    out = await edit_talisman(c, 'doumu_gate')
    if out == 'open':
        c.set('doumu_open')
        await c.event('gate_open')
        await c.narrate('Бумажка вспыхивает. Засов сам отодвигается, створки расходятся.')
        await c.say('pilgrim5', '门开了！真奇怪！')


async def nun_talk(c: ScriptContext) -> None:
    if c.flag('nun_done'):
        await cycle(c, 'nun_n', 'nun', ['山上写的字，都是真的。你要小心写。', '你应该在天黑以前到中天门。'])
        return
    if not c.flag('nun_met'):
        await c.narrate('Монахиня прикладывает палец к губам: обет молчания. Берёт кисть и пишет на листке.')
        await c.say('nun', '我不说话，我写字。')
        answer = await c.ask('nun', '你找谁？')
        a = normalize(answer)
        if '李' in a:
            await c.say('nun', '李明是我的老朋友。他刚才经过这儿，上山了。')
            c.set('nun_met')
        else:
            await c.say('nun', '我不明白。你写清楚一点儿。')
            return
    await c.say('nun', '天黑了，你有灯吗？')
    await c.narrate('Она ждёт. Может, показать ей лампу?')


async def nun_item(c: ScriptContext, item: str) -> bool:
    if item == 'lamp' and c.flag('nun_met') and not c.flag('nun_done'):
        await c.narrate('Монахиня кивает и снова пишет.')
        await c.say('nun', '好。这张纸给你。')
        c.give('fu')
        await c.say('nun', '山上写的字，都是真的。你要小心写。')
        await c.say('nun', '这儿的环境很安静，我在这儿住了三十年。')
        await c.say('nun', '你应该在天黑以前到中天门。')
        c.set('nun_done')
        return True
    if item == 'brush':
        await c.say('nun', '李家的笔！')
        return True
    return False


async def burner(c: ScriptContext) -> None:
    if not c.has('incense') and not c.flag('incense_taken'):
        c.set('incense_taken')
        c.give('incense')
        await c.narrate('У курильницы — пучок палочек для паломников. Беру три.')
    else:
        await c.narrate('Благовония тлеют. Дым поднимается ровной нитью: ветра нет.')


async def doumu_up(c: ScriptContext) -> bool:
    if c.flag('nun_done'):
        return True
    await c.narrate('Из-за ворот доносится колокольчик — будто кто-то зовёт. Надо заглянуть в обитель.')
    return False


register(
    SceneDef(
        id='5a', chapter=5, title='Обитель Доуму', zh='斗母宫',
        art=doumu_art, anim=doumu_anim, look=doumu_look,
        path=[(8, 166), (160, 166), (312, 160)],
        entries={'bottom': 20, 'valley': 300},
        actors=[
            ActorDef('pilgrim5', 'Паломница', fig(P.DARK_BLUE, P.WHITE, 'jacket', 'bun', kind='old', hair=P.GREY), 120, 160, 'right',
                     on_talk=pilgrim_talk),
            ActorDef('nun', 'Молчаливая монахиня', fig(P.GREY, P.STONE, 'robe', 'hood'), 180, 118, 'left',
                     visible=lambda s: s.on('doumu_open'), stand_at=180, on_talk=nun_talk, on_item=nun_item),
        ],
        hotspots=[
            HotspotDef('talisman', 'Бумажка на воротах', (157, 89, 46, 20), stand_at=180, on_click=gate_talisman,
                       visible=lambda s: not s.on('doumu_open'), cursor='hand'),
            HotspotDef('burner', 'Курильница', (232, 124, 24, 22), stand_at=244, on_click=burner),
        ],
        signs=[
            SignDef('doumu', '斗母宫', 158, 48, 'plaque'),
            SignDef('gate_fu', '门不开', 158, 90, 'carved', talisman='doumu_gate', visible=lambda s: not s.on('doumu_open')),
        ],
        exits=[
            ExitDef('bottom', '4c', 'up', (0, 100, 10, 70), 'left', 12, 'Красные ворота'),
            ExitDef('valley', '5b', 'bottom', (310, 100, 10, 64), 'right', 312, 'Вверх по тропе', guard=doumu_up),
        ],
        on_enter=doumu_enter,
        music='temple',
    )
)

# ---------------------------------------------------------------- 5b · the Stone Sutra valley


def valley_look(s) -> SceneLook:
    return SceneLook('sunset')


def valley_art(s, look: SceneLook) -> None:
    c = kit.C
    kit.sky([(P.LIGHT_BLUE, 40), (P.MIST, 30), (P.WHITE, 40)])
    kit.ridge(50, 10, 30, 131, P.PERIWINKLE, peaks=[(120, 40, 100)])
    kit.ridge(80, 8, 20, 132, P.PINE)
    # the great sloping rock with carved glyphs
    kit.poly([(20, 128), (70, 70), (200, 64), (240, 128)], P.GREY)
    kit.poly([(30, 124), (76, 76), (196, 70), (230, 124)], P.STONE)
    kit.ground(128, P.MOSS, P.JADE, seed=133, density=0.04)
    # the stream
    low = s.on('stream_low')
    kit.water(140, 14, P.TEAL, P.MINT, seed=134, x0=236, x1=300)
    if low:
        for sx in (240, 256, 272, 288):
            c.elli(sx, 144, 10, 6, P.STONE)
            c.line(sx + 1, 144, sx + 8, 144, P.GREY)
    else:
        kit.water(128, 36, P.TEAL, P.MINT, seed=135, x0=232, x1=304)
    # the stone with the painted talisman
    kit.rock(210, 116, 24, 18, P.STONE, P.GREY, P.PLUM)
    kit.path_band([(0, 166), (230, 166)], 12, P.PAPER, P.STONE)
    kit.path_band([(300, 160), (320, 158)], 12, P.PAPER, P.STONE)
    for x in (300, 314):
        kit.pine(x, 130, 26, seed=x)


def valley_anim(s, look: SceneLook, frame: int) -> None:
    kit.canvas(pyxel)
    if s.on('stream_low'):
        kit.water_anim(140, 12, frame, x0=236, x1=300)
    else:
        kit.water_anim(128, 34, frame, x0=232, x1=304)
    # water calligraphy fading on the rock
    t = frame % 240
    if t < 180:
        pyxel.dither(1 - t / 180)
        pyxel.text(128, 110, '山 水', P.NAVY)
        pyxel.dither(1.0)
    kit.canvas(None)


async def valley_enter(c: ScriptContext) -> None:
    if c.flag('valley_in'):
        return
    c.set('valley_in')
    await c.narrate('Долина каменной сутры. На огромной покатой скале высечены знаки — каждый размером с человека.')
    await c.narrate('Дальше тропу пересекает ручей. Вода бурлит — не перейти.')


async def calligrapher_talk(c: ScriptContext) -> None:
    await cycle(c, 'cal_n', 'calligrapher', [
        '我每天在这儿写字，用水写。一会儿，字就没有了。',
        '这是一个很安静的地方。',
        '写字的时候，我的心很安静。',
        '一千多年以前，有人在这块大石头上刻了很多字。',
        '你看最大的字："如是我闻"。',
    ])


async def students_talk(c: ScriptContext) -> None:
    if c.flag('stream_low'):
        await cycle(c, 'stu5_n', 'student5', ['水小了！真奇怪！', '你是怎么做到的？', '我们一起上山吧！'])
        return
    await c.say('student5', '我们是大学生，这个周末来爬山。')
    await c.say('student5', '可是水太大了，我们过不去。河中间有石头，可是看不见。')
    await c.say('student5', '我们决定等水小一点儿再走。')


async def stream_stone(c: ScriptContext) -> None:
    if c.flag('stream_low'):
        await c.narrate('На камне теперь написано: 水小.')
        return
    await c.narrate('На камне у ручья кто-то вывел краской два знака. Краска ещё свежая. В кустах мелькает рыжий хвост.')
    out = await edit_talisman(c, 'stream')
    if out == 'low':
        await lower_stream(c)


async def lower_stream(c: ScriptContext) -> None:
    c.set('stream_low')
    await c.event('stream_low')
    await c.narrate('Шум воды стихает. Ручей мелеет на глазах, из воды поднимаются плоские камни — как ступени.')
    await c.say('student5', '水小了！真奇怪！')


async def stream_spell(c: ScriptContext, spell) -> bool:
    if c.flag('stream_low') or spell.power != 'full':
        return False
    if spell.is_special('水落石出') or spell.says(noun='水', adj='小') or spell.says(adj='小'):
        await lower_stream(c)
        return True
    return False


async def valley_cross(c: ScriptContext) -> bool:
    if c.flag('stream_low'):
        await c.narrate('Перепрыгиваю с камня на камень.')
        return True
    await c.narrate('Ручей слишком бурный. Перейти нельзя.')
    return False


register(
    SceneDef(
        id='5b', chapter=5, title='Долина каменной сутры', zh='经石峪',
        art=valley_art, anim=valley_anim, look=valley_look,
        path=[(8, 166), (220, 166)],
        entries={'bottom': 20, 'ridge': 220},
        actors=[
            ActorDef('calligrapher', 'Старик с кистью-шваброй', fig(P.WHITE, P.GREY, 'jacket', 'cap', kind='old', prop='broom'), 110, 160, 'right',
                     on_talk=calligrapher_talk),
            ActorDef('student5', 'Студенты', fig(P.VERMILION, P.WHITE, 'jacket', 'ponytail', prop='bag'), 196, 162, 'right',
                     on_talk=students_talk),
        ],
        hotspots=[
            HotspotDef('rock', 'Скала со знаками', (70, 70, 120, 50), stand_at=120,
                       on_click=lambda c: c.read('sutra')),
            HotspotDef('stone', 'Камень у ручья', (208, 100, 28, 18), stand_at=214, on_click=stream_stone, cursor='hand'),
            HotspotDef('stream', 'Ручей', (232, 126, 72, 38), stand_at=224, on_spell=stream_spell, tags=('水', '河'),
                       on_click=lambda c: c.narrate('Холодная горная вода несётся по камням.')),
        ],
        signs=[
            SignDef('valley', '经石峪', 10, 40, 'plaque'),
            SignDef('sutra', '如是\n我闻', 100, 78, 'carved', vertical=True),
            SignDef('stream_fu', '水大', 212, 104, 'carved', talisman='stream'),
        ],
        exits=[
            ExitDef('bottom', '5a', 'valley', (0, 100, 10, 70), 'left', 12, 'Обитель'),
            ExitDef('ridge', '5c', 'bottom', (300, 100, 20, 64), 'right', 220, 'Через ручей', guard=valley_cross),
        ],
        on_enter=valley_enter,
        music='mountain',
    )
)

# ---------------------------------------------------------------- 5c · the Horse-turning ridge


def ridge_look(s) -> SceneLook:
    return SceneLook('sunset')


def ridge_art(s, look: SceneLook) -> None:
    c = kit.C
    kit.sky([(P.LIGHT_BLUE, 40), (P.MIST, 30), (P.WHITE, 40)])
    kit.sun(60, 70, 12)
    kit.ridge(78, 10, 30, 141, P.PERIWINKLE)
    kit.slope([(0, 150), (120, 130), (220, 110), (320, 90)], P.MOSS)
    kit.path_band([(0, 164), (150, 150), (320, 120)], 12, P.PAPER, P.STONE)
    kit.paifang(200, 124, 56, 40, P.STONE, P.PLUM, P.INK, P.LACQUER)
    # the signpost
    c.rect(94, 110, 3, 40, P.WOOD)
    for x, h in ((20, 30), (270, 40), (300, 34)):
        kit.pine(x, 150 if x < 100 else 116, h, seed=x)


async def ridge_enter(c: ScriptContext) -> None:
    if c.flag('ridge_in'):
        return
    c.set('ridge_in')
    c.unlock('diary_9')
    await c.narrate('Хребет, где поворачивают коней. Солнце садится. У указателя растерянно топчется старик.')


async def groom_talk(c: ScriptContext) -> None:
    step = int(c.flag('groom_step') or 0)
    if step == 0:
        answer = await c.ask('horseman', '你要骑马吗？')
        if yes(answer):
            await c.say('horseman', '对不起，马不上山。')
        else:
            await c.say('horseman', '对，马不上山。')
        await c.say('horseman', '到这儿，马就要回去了。所以这儿叫"回马岭"。')
        await c.say('horseman', '上面的路太难走了，马不愿意走。')
        c.set('groom_step', 1)
        return
    await cycle(c, 'groom_n', 'horseman', ['我的马累了，我们回去了。', '你一个人上山？路上小心！'])


async def lost_talk(c: ScriptContext) -> None:
    if c.flag('signpost_fixed'):
        await cycle(c, 'lost_n', 'lost', ['中天门在上面！你终于帮我找到路了！', '谢谢你！我们一起走吧！'])
        return
    await c.say('lost', '牌子上写着"中天门下"……可是我是从下面来的！')
    await c.say('lost', '我走了一个小时，又回到这儿了！我很生气！')


async def signpost(c: ScriptContext) -> None:
    if c.flag('signpost_fixed'):
        await c.narrate('Указатель: 中天门上，红门下. Всё верно.')
        return
    await c.narrate('Указатель будто перевернули: стрелка «вниз» у Средних ворот. На столбе — следы когтей.')
    out = await edit_talisman(c, 'signpost')
    if out == 'fixed':
        c.set('signpost_fixed')
        await c.narrate('Знаки меняются местами — и стрелки сами поворачиваются.')
        await c.say('lost', '中天门在上面！你终于帮我找到路了！')


register(
    SceneDef(
        id='5c', chapter=5, title='Хребет Хуэйма', zh='回马岭',
        art=ridge_art, look=ridge_look,
        path=[(8, 164), (150, 150), (312, 122)],
        entries={'bottom': 20, 'top': 300},
        actors=[
            ActorDef('horseman', 'Конюх', fig(P.WOOD, P.OCHRE, 'jacket', 'straw'), 46, 160, 'right', on_talk=groom_talk),
            ActorDef('lost', 'Заблудившийся старик', fig(P.GREY, P.WHITE, 'jacket', 'cap', kind='old', prop='staff'), 124, 154, 'left',
                     on_talk=lost_talk),
        ],
        hotspots=[
            HotspotDef('signpost', 'Указатель', (80, 92, 98, 24), stand_at=110, on_click=signpost, cursor='hand'),
            HotspotDef('horse', 'Лошадь', (8, 132, 26, 24), stand_at=40,
                       on_click=lambda c: c.narrate('Невысокая гнедая лошадка. Устала и тянется к траве.')),
        ],
        signs=[
            SignDef('ridge', '回马岭', 210, 86, 'plaque'),
            SignDef('post', '中天门下红门上', 80, 96, 'board', talisman='signpost'),
        ],
        exits=[
            ExitDef('bottom', '5b', 'ridge', (0, 100, 10, 70), 'left', 12, 'Долина'),
            ExitDef('top', '5d', 'bottom', (296, 80, 24, 44), 'right', 306, 'Средние ворота'),
        ],
        on_enter=ridge_enter,
        music='mountain',
    )
)

# ---------------------------------------------------------------- 5d · Zhongtianmen


def zt_look(s) -> SceneLook:
    return SceneLook('night' if s.on('bells_done') else 'dusk', lantern=s.on('bells_done'))


def zt_art(s, look: SceneLook) -> None:
    c = kit.C
    kit.sky([(P.LIGHT_BLUE, 40), (P.MIST, 30), (P.WHITE, 40)])
    if s.on('bells_done'):
        kit.stars(151, 60, 70)
        kit.moon(260, 30, 9)
    kit.ridge(46, 10, 30, 151, P.PERIWINKLE, peaks=[(200, 30, 90)])
    kit.ground(118, P.PAPER, P.MIST, seed=153, density=0.03)
    # the gate of Zhongtianmen
    kit.paifang(10, 128, 64, 56, P.STONE, P.PLUM, P.INK, P.LACQUER)
    # the Li family teahouse
    c.rect(112, 70, 96, 50, P.OCHRE)
    kit.roof(106, 70, 108, 10, P.INK, P.STONE)
    c.rect(150, 88, 22, 32, P.INK)
    kit.window(122, 84, 18, 14, s.on('bells_done'))
    kit.window(182, 84, 18, 14, s.on('bells_done'))
    kit.lantern(116, 80, s.on('bells_done'))
    kit.lantern(204, 80, s.on('bells_done'))
    # the bells on a frame
    c.rect(236, 84, 70, 4, P.WOOD)
    c.rect(238, 88, 3, 36, P.WOOD)
    c.rect(300, 88, 3, 36, P.WOOD)
    for i in range(3):
        bx = 252 + i * 18
        c.tri(bx - 6, 106, bx + 6, 106, bx, 90, P.OCHRE)
        c.rect(bx - 5, 96, 11, 10, P.OCHRE)
    # the closed cable-car station
    c.rect(270, 128, 46, 22, P.GREY)
    c.rect(276, 134, 16, 12, P.DARK_BLUE)
    kit.path_band([(0, 164), (160, 166), (320, 164)], 12, P.PAPER, P.STONE)


async def zt_enter(c: ScriptContext) -> None:
    if c.flag('zt_in'):
        return
    c.set('zt_in')
    await c.narrate('Средние небесные ворота. Каменная арка, домик с фонарями — и вывеска. Та самая, с конверта: 李家茶馆.')


async def xiaoyue_talk(c: ScriptContext) -> None:
    if c.flag('coat_given'):
        await cycle(c, 'xy_n', 'xiaoyue', ['十八盘很难走，你要慢慢走。', '爷爷一定在山顶等日出。你一定能找到他！', '晚上冷，别感冒了！'])
        return
    if not c.flag('xy_met'):
        await c.say('xiaoyue', '欢迎！你要喝茶吗？天快黑了，山上很冷。')
        answer = await c.ask('xiaoyue', '你从哪儿来？')
        if '俄' in normalize(answer):
            await c.say('xiaoyue', '俄罗斯？！我爷爷有一个俄罗斯朋友……')
        else:
            await c.say('xiaoyue', '欢迎你！')
        await c.say('xiaoyue', '我叫李小月。这是我家的茶馆。')
        c.set('xy_met')
        return
    await c.say('xiaoyue', '你有什么事吗？')


async def xiaoyue_item(c: ScriptContext, item: str) -> bool:
    if item in ('letter', 'envelope') and not c.flag('letter_read'):
        c.set('letter_read')
        await c.narrate('Сяоюэ читает адрес на конверте и прижимает ладонь ко рту.')
        await c.say('xiaoyue', '"李明收"……这是给我爷爷的信！')
        await c.say('xiaoyue', '你是小安的家人？')
        await c.say('xiaoyue', '爷爷常常说起他的俄罗斯朋友小安。他说，小安会回来的。')
        await c.say('xiaoyue', '他等了六十多年……')
        await c.narrate('Она вытирает глаза.')
        await c.say('xiaoyue', '对不起，我很难过，也很高兴。')
        await c.say('xiaoyue', '可是爷爷已经上山了。他每年秋分都去山顶看日出。')
        await c.say('xiaoyue', '我给爷爷打电话……喂？喂？……他没有接。')
        await c.say('xiaoyue', '索道晚上不开，你必须走上去。')
        c.unlock('diary_11')
        if c.flag('cargo_done'):
            c.set('zhao_arrived')
            await c.narrate('За спиной кто-то кряхтит: Лао Чжао с коромыслом добрался до чайной.')
        return True
    if item in ('photo', 'old_photo'):
        await c.say('xiaoyue', '这是爷爷！他那时候真年轻！')
        return True
    if item == 'drawing':
        await c.say('xiaoyue', '大桥！画得真好！')
        return True
    return False


async def xiaoyue_coat(c: ScriptContext) -> None:
    if c.flag('coat_given'):
        return
    c.set('coat_given')
    await c.say('xiaoyue', '晚上山上很冷。穿上爷爷的旧大衣吧！')
    c.give('coat')
    await c.say('xiaoyue', '十八盘很难走，你要慢慢走。')


async def monk_talk(c: ScriptContext) -> None:
    if c.flag('bells_done'):
        await cycle(c, 'monk_n', 'monk', ['钟声很好听吧？', '天黑了，上山要小心。', '月亮出来了。'])
        return
    await c.say('monk', '天快黑了，我要敲钟。')
    await c.say('monk', '你帮我敲吧。你看，石头上写着敲钟的顺序。')
    await c.read('bell_poem')
    ok = await c.puzzle('bells', bells='风雨日云月', chant='雨云月', lines=['雨后云开月出来'])
    if not ok:
        await c.say('monk', '没关系，你再看看石头上的字。')
        return
    c.set('bells_done')
    await c.event('night')
    await c.narrate('Последний удар тает в воздухе. Облака расходятся, над горой встаёт луна. Ночь.')
    await c.say('monk', '钟声很好听吧？月亮出来了。')
    if c.flag('letter_read'):
        await xiaoyue_coat(c)


async def zhao_talk(c: ScriptContext) -> None:
    if not c.flag('zhao_arrived'):
        return
    if c.flag('suitcase_porter') and not c.flag('suitcase_back'):
        c.set('suitcase_back')
        await c.say('zhao', '我终于到了！你的行李箱在这儿。')
        await c.say('zhao', '行李箱太重了，放在茶馆吧。明天我给你拿到山顶。')
        return
    await cycle(c, 'zhao_n', 'zhao', ['我们挑山工，走路要走"之"字。', '十八盘很难走，可是我走了四十年！', '今天晚上我也上山。我们一会儿见！'])


async def family_talk(c: ScriptContext) -> None:
    await cycle(c, 'fam_n', 'father5', ['我们打算明天早上坐索道上去。', '我儿子参加了学校的比赛，得了第一名！', '这个季节爬山最好：不冷也不热。',
                                         '我们是北方人。北京的公园没有这么大的山！'])


async def kid5_talk(c: ScriptContext) -> None:
    await cycle(c, 'kid5_n', 'kid5', ['我喜欢体育！我会游泳，也会打篮球！', '我渴了！妈妈，我要喝水！', '晚上的月亮真大！',
                                       '我个子很矮，可是我跑得很快！', '我的帽子是蓝的，我哥哥的是绿的。'])


async def zt_up(c: ScriptContext) -> bool:
    if not c.flag('letter_read'):
        await c.narrate('Сначала — в чайную семьи Ли. Письмо адресовано сюда.')
        return False
    if not c.flag('bells_done'):
        await c.narrate('Ещё сумерки. Монах у колоколов машет рукой — просит помочь с вечерним звоном.')
        return False
    if not c.flag('coat_given'):
        await xiaoyue_coat(c)
    await c.narrate('Ночь. Лампа бабушки Ван, куртка Ли Мина, кисть деда. Вверх — к Восемнадцати поворотам.')
    return True


register(
    SceneDef(
        id='5d', chapter=5, title='Средние небесные ворота', zh='中天门',
        art=zt_art, look=zt_look,
        path=[(8, 164), (160, 166), (312, 164)],
        entries={'bottom': 20, 'top': 40},
        actors=[
            ActorDef('xiaoyue', 'Сяоюэ', fig(P.JADE, P.WHITE, 'jacket', 'ponytail'), 162, 150, 'left', on_talk=xiaoyue_talk, on_item=xiaoyue_item),
            ActorDef('monk', 'Монах у колоколов', fig(P.OCHRE, P.WOOD, 'robe', 'bald'), 240, 150, 'right', on_talk=monk_talk),
            ActorDef('zhao', 'Лао Чжао', fig(P.STONE, P.OCHRE, 'jacket', 'straw', kind='old', prop='pole'), 100, 160, 'right',
                     visible=lambda s: s.on('zhao_arrived'), on_talk=zhao_talk),
            ActorDef('father5', 'Отец семейства', fig(P.NAVY, P.WHITE, 'jacket', 'short'), 204, 160, 'left', on_talk=family_talk),
            ActorDef('kid5', 'Мальчик в кепке', fig(P.YELLOW, P.DARK_BLUE, 'jacket', 'cap', kind='child'), 218, 164, 'left', on_talk=kid5_talk,
                     tags=('人', '孩子')),
        ],
        hotspots=[
            HotspotDef('cablecar', 'Канатная дорога', (270, 124, 46, 26), stand_at=280,
                       on_click=lambda c: c.narrate('Станция канатной дороги. На двери: 晚上不开. Ночью не работает.')),
        ],
        signs=[
            SignDef('zt', '中天门', 26, 74, 'plaque'),
            SignDef('teahouse', '李家茶馆', 134, 54, 'plaque'),
            SignDef('cable', '索道', 280, 112, 'blue'),
            SignDef('closed', '晚上不开', 256, 152, 'tag'),
        ],
        exits=[
            ExitDef('bottom', '5c', 'top', (0, 100, 10, 70), 'left', 12, 'Хребет'),
            ExitDef('up', '6a', 'bottom', (26, 76, 32, 50), 'up', 42, 'К Восемнадцати поворотам', guard=zt_up),
        ],
        on_enter=zt_enter,
        diary=('diary_10',),
        music='teahouse',
    )
)


# ---------------------------------------------------------------- pages, pictures, glossary, hints

pages.add(
    PageDef('doumu', 'Обитель', 5, ('其实', '办法', '真奇怪', '认为', '去掉'), kind='phrase',
            phrases=('其实，我也想进去', '可是我没有办法。', '门开了！真奇怪！', '你认为字真的能开门吗？', '以前有一个人把"不"字去掉了')),
    PageDef('nun', 'Монахиня', 5, ('刚才', '经过', '应该', '环境', '小心'), kind='phrase',
            phrases=('他刚才经过这儿，上山了。', '他刚才经过这儿，上山了。', '你应该在天黑以前到中天门。', '这儿的环境很安静', '你要小心写。')),
    PageDef('valley', 'Каменная сутра', 5, ('一会儿', '刻', '周末', '决定', '大学生'), kind='phrase',
            phrases=('一会儿，字就没有了。', '有人在这块大石头上刻了很多字。', '这个周末来爬山。', '我们决定等水小一点儿再走。', '我们是大学生')),
    PageDef('horse', 'Конюх', 5, ('骑', '马', '愿意', '难走'), kind='phrase',
            phrases=('你要骑马吗？', '马不上山。', '马不愿意走。', '上面的路太难走了')),
    PageDef('lost', 'Заблудившийся', 5, ('生气', '终于', '找到', '又'), kind='phrase',
            phrases=('我很生气！', '你终于帮我找到路了！', '你终于帮我找到路了！', '又回到这儿了！')),
    PageDef('xiaoyue', 'Сяоюэ', 5, ('难过', '说起', '等', '已经', '索道'), kind='phrase',
            phrases=('我很难过，也很高兴。', '爷爷常常说起他的俄罗斯朋友小安。', '他等了六十多年……', '可是爷爷已经上山了。', '索道晚上不开')),
    PageDef('family5', 'Семья у ворот', 5, ('打算', '参加', '比赛', '季节', '体育', '渴'), kind='phrase',
            phrases=('我们打算明天早上坐索道上去。', '我儿子参加了学校的比赛', '我儿子参加了学校的比赛', '这个季节爬山最好', '我喜欢体育！', '我渴了！')),
    PageDef('sport5', 'Спорт', 5, ('游泳', '打篮球', '踢足球', '跑步'), kind='picture'),
    PageDef('night5', 'Вечер', 5, ('月亮', '钟', '旧', '大衣'), kind='picture'),
    PageDef('diary9', 'Грузы', 5, ('一边', '只', '走不动', '累'), kind='phrase',
            phrases=('还一边走一边唱歌。', '我只挑了三十公斤', '就累得走不动了。', '你不累吗？')),
    PageDef('diary10', 'Праздник луны', 5, ('中秋节', '月饼', '外面', '想起'), kind='phrase',
            phrases=('今天是中秋节。', '吃月饼。', '晚上我们在茶馆外面看月亮', '我想起了我的妈妈。')),
    PageDef('diary11', 'Приказ', 5, ('收到', '通知', '完', '秋分'), kind='phrase',
            phrases=('今天我们收到了回国的通知。', '今天我们收到了回国的通知。', '桥还没有修完。', '秋分的时候，我们一起上山看日出吧。')),
)

for w, ic in (('大衣', 'coat'), ('钟', 'bell'), ('月亮', 'moon'), ('马', 'horse'), ('符', 'talisman')):
    icon_for(w, ic)


@picture('旧')
def _(x: int, y: int) -> None:
    picto.icon('coat', x + 8, y + 8)
    for dx, dy in ((10, 14), (20, 22), (14, 26)):
        pyxel.pset(x + dx, y + dy, P.STONE)
        pyxel.pset(x + dx + 1, y + dy, P.STONE)
    pyxel.line(x + 22, y + 10, x + 26, y + 14, P.PAPER)


@picture('游泳')
def _(x: int, y: int) -> None:
    pyxel.rect(x, y + 16, 32, 16, P.LIGHT_BLUE)
    pyxel.circ(x + 12, y + 14, 3, P.PEACH)
    pyxel.line(x + 14, y + 16, x + 24, y + 18, P.VERMILION)
    for i in range(4):
        pyxel.line(x + 2 + i * 8, y + 22, x + 6 + i * 8, y + 22, P.WHITE)


@picture('打篮球')
def _(x: int, y: int) -> None:
    picto.person(x + 10, y + 30, P.VERMILION, arm='up')
    pyxel.circ(x + 20, y + 8, 4, P.ORANGE)
    pyxel.rect(x + 24, y + 4, 6, 1, P.VERMILION)


@picture('踢足球')
def _(x: int, y: int) -> None:
    picto.person(x + 12, y + 30, P.DARK_BLUE)
    pyxel.circ(x + 22, y + 27, 3, P.WHITE)
    pyxel.circb(x + 22, y + 27, 3, P.INK)


@picture('跑步')
def _(x: int, y: int) -> None:
    picto.person(x + 16, y + 30, P.JADE, arm='out')
    for i in range(3):
        pyxel.line(x + 2, y + 14 + i * 5, x + 8, y + 14 + i * 5, P.STONE)


@sketch('moon_festival')
def _(x: int, y: int) -> None:
    pyxel.circb(x + 60, y + 12, 8, P.INK)
    for i in range(3):
        picto.person(x + 14 + i * 12, y + 40, P.INK)
    pyxel.circ(x + 40, y + 36, 3, P.OCHRE)


@sketch('sunrise_promise')
def _(x: int, y: int) -> None:
    pyxel.tri(x + 4, y + 40, x + 40, y + 6, x + 76, y + 40, P.STONE)
    pyxel.circb(x + 40, y + 6, 5, P.VERMILION)
    for i in range(5):
        pyxel.line(x + 40, y + 6, x + 22 + i * 9, y - 2, P.VERMILION)
    picto.person(x + 34, y + 40, P.INK)
    picto.person(x + 46, y + 40, P.INK)


words.add('''
斗母宫 — обитель Доуму
其实 — на самом деле
办法 — способ, выход
真奇怪 — как странно
奇怪 — странный
认为 — считать, полагать
去掉 — убрать
刚才 — только что
经过 — проходить мимо
应该 — следует, должен
环境 — окружающая среда, обстановка
小心 — осторожно
经石峪 — Долина каменной сутры
一会儿 — немного погодя
周末 — выходные
决定 — решить
大学生 — студент
如是我闻 — «так я слышал»
回马岭 — хребет Хуэйма («поверни коня»)
骑马 — ехать верхом
愿意 — хотеть, соглашаться
难走 — трудно идти
生气 — сердиться
终于 — наконец
找到 — найти
难过 — грустно
说起 — упоминать, рассказывать о
索道 — канатная дорога
打算 — собираться, планировать
参加 — участвовать
比赛 — соревнование
季节 — время года
体育 — физкультура, спорт
游泳 — плавать
打篮球 — играть в баскетбол
踢足球 — играть в футбол
月亮 — луна
大衣 — пальто, куртка
一边 — одновременно, на ходу
走不动 — не в силах идти
中秋节 — Праздник середины осени
月饼 — лунный пряник
外面 — снаружи
想起 — вспомнить
收到 — получить
通知 — извещение
秋分 — осеннее равноденствие
李家茶馆 — чайная семьи Ли
晚上不开 — вечером закрыто
水落石出 — вода спадает — камни видны
''')

hints.add(lambda s: s.scene == '5a' and not s.on('doumu_open'),
          'Бумажка на воротах: 门不开 — «ворота не открываются». На горе написанное сбывается. Нажмите на бумажку и уберите лишний знак.')
hints.add(lambda s: s.on('doumu_open') and not s.on('nun_met'),
          'Монахиня молчит, но пишет. Её вопрос — «кого ты ищешь?». Напишите имя с конверта.')
hints.add(lambda s: s.on('nun_met') and not s.on('nun_done'),
          'Монахиня спрашивает, есть ли у вас лампа (灯). Покажите её — выберите в сумке.')
hints.add(lambda s: s.scene == '5b' and not s.on('stream_low'),
          'Кто-то написал на камне у ручья 水大 — «воды много». Перепишите: напишите 小 поверх 大. Или попробуйте идиому 水落石出.')
hints.add(lambda s: s.scene == '5c' and not s.on('signpost_fixed'),
          'Указатель перепутан: 中天门下 — «Средние ворота внизу». Поменяйте местами 上 и 下.')
hints.add(lambda s: s.scene == '5d' and not s.on('letter_read'),
          'Вывеска 李家茶馆 — адрес с конверта. Покажите письмо (信) девушке у чайной.')
hints.add(lambda s: s.scene == '5d' and s.on('letter_read') and not s.on('bells_done'),
          'Монах просит позвонить в колокола в том порядке, в каком знаки стоят в надписи 雨后云开月出来.')
hints.add(lambda s: s.scene == '5d' and s.on('bells_done'),
          'Пора наверх: к Восемнадцати поворотам, через арку 中天门.')

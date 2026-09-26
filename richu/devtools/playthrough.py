"""Scripted playthroughs used by tests and by the screenshot tool."""
from __future__ import annotations

from ..content import pages as PG
from ..core import journal
from ..core.headless import HeadlessGame


def solve_open_pages(g: HeadlessGame, chapter: int) -> list[str]:
    done = []
    for p in PG.PAGES:
        if p.chapter == chapter and journal.page_status(g.state, p) == 'open':
            g.solve_page(p.id)
            done.append(p.id)
    return done


def play_prologue(g: HeadlessGame) -> None:
    g.start('0a', 'start')
    assert g.state.chapter == 0
    g.click('box')
    assert all(it in g.state.inventory for it in ('letter', 'diary', 'photo', 'brush'))
    assert 'envelope' in g.state.texts
    assert g.exit('door')
    assert g.state.scene == '1a'


def play_chapter1(g: HeadlessGame) -> None:
    s = g.state
    assert s.chapter == 1 and s.coins == 200
    g.talk('officer')
    g.answer('是')
    assert g.use('passport', 'officer')
    assert s.on('passport_ok')
    g.click('black')
    assert s.on('black_taken')
    g.click('red')
    assert 'suitcase' in s.inventory
    g.talk('staff')
    assert g.exit('out') and s.scene == '1b'

    g.answer('泰山').talk('clerk')
    assert s.on('price_asked')
    assert g.use('money', 'clerk')
    assert 'ticket' in s.inventory and s.coins == 150
    g.answer('面包').talk('waitress')
    g.use('money', 'waitress')
    assert 'bread' in s.inventory
    g.answer('我是俄罗斯人').talk('kid')
    g.talk('kid')
    g.use('bread', 'kid')
    assert 'apple' in s.inventory
    assert not g.exit('platform')
    g.use('ticket', 'gatekeeper')
    assert g.exit('platform') and s.scene == '1c'

    g.click('seat8')
    assert s.on('seated')
    g.answer('我是俄罗斯人').talk('student')
    g.answer('是').talk('student')
    g.answer('小安').talk('student')
    g.talk('student')
    g.use('diary', 'student')
    assert 'diary_1' in s.texts
    for _ in range(4):
        g.talk('student')
    assert s.on('arrived')


def play_chapter2(g: HeadlessGame, sleep: bool = False) -> None:
    """The city: taxi, hotel, bank, the street's side scenes, the Dai Temple."""
    s = g.state
    assert g.exit('out') and s.scene == '2a'
    assert s.chapter == 2 and 'card' in s.inventory
    g.answer('我要西瓜').talk('fruit')
    g.use('money', 'fruit')
    g.talk('mapman')
    g.use('money', 'mapman')
    assert 'map' in s.inventory
    g.talk('mapman')
    g.answer('好', '泰山', '不知道').talk('driver')
    assert s.on('taxi_ready')
    g.use('money', 'driver')
    assert g.exit('taxi') and s.scene == '2b'
    g.talk('guest')
    g.talk('guest')
    g.talk('guest')
    g.answer('住').talk('clerk2')
    g.answer('一个晚上')
    g.use('passport', 'clerk2')
    assert s.on('room_price')
    g.use('card', 'clerk2')
    g.use('money', 'clerk2')
    assert s.on('need_bank') and 'keycard' not in s.inventory
    assert g.exit('street') and s.scene == '2d'
    g.answer('钱').talk('banker')
    g.use('passport', 'banker')
    g.use('card', 'banker')
    assert s.on('bank_done') and s.coins > 1000
    g.answer('一').talk('waiter')
    g.answer('面条', '茶').talk('waiter')
    g.use('money', 'waiter')
    assert s.on('dinner_done')
    g.talk('father')
    g.answer('吃').talk('mother')
    assert 'cake' in s.inventory
    g.answer('你好').talk('daughter')
    g.answer('生日快乐').talk('daughter')
    assert s.on('sang_birthday')
    g.answer('我是俄罗斯人').talk('oldman1')
    g.answer('喜欢').talk('oldman2')
    g.answer('雨伞', '黑').talk('shopkeeper')
    g.use('money', 'shopkeeper')
    assert 'umbrella' in s.inventory
    g.answer('熊猫').talk('shopkeeper')
    g.answer('你好').talk('shopkeeper')
    assert g.exit('temple') and s.scene == '2e'
    g.answer('李明').talk('keeper')
    assert s.on('know_deadline')
    g.plan('ancient', True)
    g.click('stele')
    g.talk('exerciser')
    g.talk('exerciser')
    g.talk('exerciser')
    g.answer('会').talk('footballer')
    g.answer('不').talk('footballer')
    g.use('photo', 'keeper')
    g.talk('keeper')
    g.talk('keeper')
    g.talk('keeper')
    assert g.exit('street') and g.exit('hotel') and s.scene == '2b'
    g.use('money', 'clerk2')
    assert 'keycard' in s.inventory
    assert g.exit('elevator') and s.scene == '2c'
    assert 'diary_2' in s.texts
    g.click('tv')
    g.click('ac')
    g.click('fridge')
    g.click('bath')
    g.click('window')
    if sleep:
        g.click('bed')


def play_chapter3(g: HeadlessGame, climb: bool = False) -> None:
    """The bridge, the village, the school, the arch of Daizong."""
    s = g.state
    assert s.scene == '3a' and s.chapter == 3
    assert 'diary_3' in s.texts
    g.read('diary_3')
    g.click('plaque')
    g.answer('是', '他是我爷爷').talk('fisher')
    assert s.on('fisher_story')
    g.talk('boy')
    g.answer('能').talk('boy')
    assert s.on('xl_school')
    g.click('pencil')
    assert 'pencil' in s.inventory
    g.answer('七条').talk('fisher')
    assert 'bucket' in s.inventory
    g.click('catch')
    assert g.use('bucket', 'river') and 'water' in s.inventory
    assert g.exit('village') and s.scene == '3b'
    g.answer('能').talk('aunt')
    assert s.on('aunt_asked')
    g.answer('我是俄罗斯人').talk('grandma')
    assert s.on('grandma_met')
    assert g.use('water', 'grandma') and s.on('gw_water')
    g.talk('aunt')
    assert 'firewood' in s.inventory
    assert g.use('firewood', 'grandma') and s.on('need_fire')
    g.answer('没有').talk('son')
    g.talk('son')
    g.talk('son')
    g.talk('son')
    g.talk('mother')
    g.click('tree')
    assert not g.exit('road')
    assert g.exit('school') and s.scene == '3c'
    g.answer('不是', '我是俄罗斯人').talk('teacher')
    g.talk('teacher')
    assert s.on('lesson1')
    g.answer('六十', '七天').talk('teacher')
    assert s.on('math_done')
    g.plan('face', True).talk('teacher')
    assert s.on('face_done')
    g.answer('红').talk('xiaohong')
    g.answer('喜欢').talk('pangpang')
    g.talk('teacher')
    assert s.on('exam_started')
    g.use('pencil', 'xiaolong')
    g.talk('teacher')
    g.talk('xiaolong')
    assert 'drawing' in s.inventory
    g.click('blackboard')
    assert g.exit('door') and s.scene == '3b'
    g.solve_page('elements')
    assert s.confirmed.get('火')
    g.use('brush', 'stove')
    assert s.on('brush_awake')
    g.answer('是')
    g.cast('火', 'stove')
    assert s.on('tea_done') and 'lamp' in s.inventory and 'old_photo' in s.inventory
    assert 'diary_4' in s.texts
    g.read('diary_4')
    assert g.exit('road') and s.scene == '3d'
    assert 'diary_5' in s.texts
    g.read('diary_5')
    g.talk('husband')
    g.answer('往前走').talk('wife')
    assert s.on('tourists_ok')
    g.answer('上山').talk('ranger')
    assert s.on('ranger_ok')
    if climb:
        assert g.exit('up')


def play_chapter4(g: HeadlessGame, climb: bool = False) -> None:
    """The market street, the teahouse, the Red Gate, the tower of immortals."""
    s = g.state
    assert s.scene == '4a' and s.chapter == 4
    g.read('diary_6')
    g.answer('不是').talk('porter')
    assert s.on('porter_met')
    g.answer('腿疼').talk('pharmacist')
    assert s.on('med_order')
    g.use('money', 'pharmacist')
    assert 'medicine' in s.inventory
    had_suitcase = 'suitcase' in s.inventory
    g.plan('cargo', True).answer('中天门')
    g.use('medicine', 'porter')
    assert s.on('cargo_done') and s.on('porter_gone')
    assert not had_suitcase or 'suitcase' not in s.inventory
    g.answer('一个').talk('pancake')
    g.use('money', 'pancake')
    assert 'pancake' in s.inventory
    g.answer('太贵了').talk('seller')
    g.answer('四十').talk('seller')
    g.use('money', 'seller')
    assert 'stick' in s.inventory
    assert g.exit('teahouse') and s.scene == '4b'
    g.click('tv4')
    g.plan('tray', True).answer('茶', '能').talk('hostess')
    assert s.on('tray_done') and 'diary_7' in s.texts
    g.read('diary_7')
    g.answer('鸟').talk('storyteller')
    g.answer('飞').talk('storyteller')
    assert 'diary_8' in s.texts
    g.read('diary_8')
    for _ in range(4):
        g.talk('manager')
    for _ in range(3):
        g.talk('bride')
        g.talk('student4')
    g.answer('好').talk('groom')
    assert g.exit('door') and s.scene == '4a'
    assert g.exit('gate') and s.scene == '4c'
    assert not g.exit('up')
    g.answer('不是').talk('ticket')
    g.use('money', 'ticket')
    assert 'gate_ticket' in s.inventory
    g.use('gate_ticket', 'guard')
    assert s.on('redgate_ok')
    for _ in range(3):
        g.talk('guide')
    assert g.exit('tower') and s.scene == '4d'
    g.answer('虫二').talk('scholar')
    g.answer('风月').talk('scholar')
    assert s.on('chonger_done') and s.confirmed.get('风')
    assert g.exit('gate') and s.scene == '4c'
    if climb:
        assert g.exit('up')


def play_chapter5(g: HeadlessGame, climb: bool = False) -> None:
    """The nunnery's talisman, the stream, the flipped signpost, the Li family teahouse, the bells."""
    s = g.state
    assert s.scene == '5a' and s.chapter == 5
    g.talk('pilgrim5')
    assert not g.exit('valley')
    g.plan('talisman', '门开').click('talisman')
    assert s.on('doumu_open')
    g.answer('李明').talk('nun')
    assert s.on('nun_met')
    g.use('lamp', 'nun')
    assert s.on('nun_done') and 'fu' in s.inventory
    g.click('burner')
    assert g.exit('valley') and s.scene == '5b'
    g.click('rock')
    for _ in range(4):
        g.talk('calligrapher')
    g.talk('student5')
    assert not g.exit('ridge')
    g.plan('talisman', '水小').click('stone')
    assert s.on('stream_low')
    assert g.exit('ridge') and s.scene == '5c'
    g.read('diary_9')
    g.answer('不要').talk('horseman')
    g.talk('horseman')
    g.talk('lost')
    g.plan('talisman', '中天门上红门下').click('signpost')
    assert s.on('signpost_fixed')
    g.talk('lost')
    g.click('horse')
    assert g.exit('top') and s.scene == '5d'
    g.read('diary_10')
    assert not g.exit('up')
    g.answer('我是俄罗斯人').talk('xiaoyue')
    g.use('letter', 'xiaoyue')
    assert s.on('letter_read') and 'diary_11' in s.texts
    g.read('diary_11')
    g.talk('zhao')
    g.plan('bells', True).talk('monk')
    assert s.on('bells_done') and 'coat' in s.inventory
    for _ in range(3):
        g.talk('father5')
        g.talk('kid5')
    g.click('cablecar')
    g.talk('xiaoyue')
    if climb:
        assert g.exit('up')

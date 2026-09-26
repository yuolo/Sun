from richu.core import magic, puzzles, talisman
from richu.core.numerals import from_hanzi, to_hanzi, year_hanzi
from richu.core.state import GameState, dumps, loads
from richu.core.types import GlyphDef, tone_of

LEX = {
    '火': GlyphDef('火', 'huǒ', 'огонь', 1, 'n', 'nature', magic='elem:fire'),
    '门': GlyphDef('门', 'mén', 'дверь', 1, 'n', 'place'),
    '鱼': GlyphDef('鱼', 'yú', 'рыба', 1, 'n', 'animal', magic='mw:条'),
    '开': GlyphDef('开', 'kāi', 'открывать', 1, 'v', 'action', magic='verb:open'),
    '大': GlyphDef('大', 'dà', 'большой', 1, 'a', 'quality', magic='adj:size+'),
    '小': GlyphDef('小', 'xiǎo', 'маленький', 1, 'a', 'quality', magic='adj:size-'),
    '水': GlyphDef('水', 'shuǐ', 'вода', 1, 'n', 'nature', magic='elem:water'),
    '不': GlyphDef('不', 'bù', 'не', 1, 'adv', 'grammar'),
    '很': GlyphDef('很', 'hěn', 'очень', 1, 'adv', 'grammar'),
    '三': GlyphDef('三', 'sān', 'три', 1, 'num', 'number', magic='num:3'),
    '条': GlyphDef('条', 'tiáo', 'счётное (длинное)', 1, 'm', 'grammar'),
    '本': GlyphDef('本', 'běn', 'счётное (книги)', 1, 'm', 'grammar'),
    '的': GlyphDef('的', 'de', 'частица', 1, 'part', 'grammar'),
    '山': GlyphDef('山', 'shān', 'гора', 1, 'n', 'nature'),
}
SPECIALS = {
    '火山': magic.SpellEntry('火山', 'n', 'вулкан', 'volcano'),
    '水落石出': magic.SpellEntry('水落石出', 'idiom', 'вода спала — камни видны', 'reveal'),
}


def m(text):
    return magic.parse(text, LEX.get, SPECIALS)


def test_magic_grammar():
    assert m('火').kind == 'thing' and m('火').noun == '火'
    t = m('三条鱼')
    assert t.kind == 'thing' and t.count == 3 and t.mw_ok
    assert m('三本鱼').mw_ok is False
    assert m('大火').adj == '大'
    q = m('很大')
    assert q.kind == 'quality' and q.degree == 'very'
    a = m('开门')
    assert a.kind == 'action' and a.verb == '开' and a.obj == '门'
    st = m('门开')
    assert st.kind == 'statement' and st.noun == '门' and st.verb == '开'
    neg = m('门不开')
    assert neg.kind == 'statement' and neg.neg
    assert m('水小').adj == '小'
    assert m('火山').special == '火山' and m('火山').kind == 'thing'
    assert m('水落石出').kind == 'special'


def test_magic_explains_failures():
    for bad in ('火门', '的', '三', '不火', '大小', ''):
        assert isinstance(m(bad), str), bad


def test_spell_power_depends_on_understanding():
    confirmed = {'门': True, '开': True}
    s = magic.cast('门开', confirmed, LEX.get, SPECIALS)
    assert s.power == 'full' and s.acts('开', on='门')
    s2 = magic.cast('开门', {'开': True}, LEX.get, SPECIALS)
    assert s2.power == 'shadow' and s2.acts('开', on='门')
    s3 = magic.cast('门不开', confirmed | {'不': True}, LEX.get, SPECIALS)
    assert not s3.acts('开', on='门') and s3.acts('开', on='门', neg=True)
    s4 = magic.cast('火门', confirmed, LEX.get, SPECIALS)
    assert s4.power == 'fizzle' and s4.reason
    s5 = magic.cast('小', {'小': True}, LEX.get, SPECIALS)
    assert s5.says(adj='小') and not s5.says(adj='大')


def test_talisman_edits():
    t = talisman.TalismanDef('gate', '门不开', {'门开': 'open'})
    s = GameState()
    assert talisman.current(s, t) == '门不开'
    new = talisman.remove('门不开', 1)
    assert new == '门开'
    assert talisman.apply(s, t, new) == 'open' and talisman.outcome(s, t) == 'open'
    assert talisman.swap('门天南', 0, 2) == '南天门'
    assert talisman.replace('水大', 1, '小') == '水小'
    assert talisman.insert('门开', 1, '不') == '门不开'


def test_puzzles():
    order = puzzles.Order('茶', 2, '小')
    cups = [puzzles.Cup('茶', '小'), puzzles.Cup('茶', '小')]
    assert puzzles.check_order(cups, order) is None
    assert puzzles.check_order(cups[:1], order) == 'count'
    assert puzzles.check_order([puzzles.Cup('水', '小')] * 2, order) == 'drink'
    assert puzzles.ring(0, '雨', '雨云月') == (1, 'progress')
    assert puzzles.ring(2, '月', '雨云月') == (3, 'solved')
    assert puzzles.ring(1, '山', '雨云月') == (0, 'wrong')
    h = puzzles.Haggle(20, 12, step=3)
    assert h.offer(10) == 'low'
    assert h.offer(15) == 'counter' and h.asking == 17
    assert h.offer(15) == 'deal'
    assert puzzles.check_list({'伞': 3, '鞋': 2}, {'伞': 3, '鞋': 2}) == []
    assert puzzles.check_list({'伞': 3}, {'伞': 2, '书': 1}) == ['书', '伞']
    assert puzzles.within_budget({'面': 8, '茶': 3}, {'面': 1, '茶': 1}, 12)
    assert not puzzles.within_budget({'面': 8, '茶': 3}, {'面': 2}, 12)
    assert puzzles.couplet_ok('天高', '地低', {'天': '地', '高': '低'})
    assert not puzzles.couplet_ok('天高', '地高', {'天': '地', '高': '低'})
    things = [puzzles.Thing('a', frozenset('红小伞')), puzzles.Thing('b', frozenset('黑大伞'))]
    assert puzzles.match_all({'girl': frozenset('红伞')}, things, {'girl': 'a'})
    assert puzzles.walk(list('左上右'), list('左上')) == (2, False)
    assert puzzles.walk(list('左上右'), list('左右')) == (1, False)


def test_numerals():
    assert [to_hanzi(n) for n in (0, 7, 10, 12, 20, 35, 99)] == ['零', '七', '十', '十二', '二十', '三十五', '九十九']
    for n in range(100):
        assert from_hanzi(to_hanzi(n)) == n
    assert from_hanzi('两') == 2 and from_hanzi('山') is None
    assert year_hanzi(1958) == '一九五八'


def test_state_roundtrip():
    s = GameState(scene='1b', coins=7)
    s.flags['x'] = 1
    s.inventory.append('lamp')
    s2 = loads(dumps(s))
    assert s2 is not None and s2.scene == '1b' and s2.coins == 7 and s2.flags == {'x': 1} and s2.inventory == ['lamp']
    assert loads('{"scene": 5}') is None and loads('garbage') is None


def test_tones():
    assert [tone_of(p) for p in ('mā', 'má', 'mǎ', 'mà', 'ma')] == [1, 2, 3, 4, 0]


def test_fonts_cover_every_character_in_the_game():
    """The pixel font and the brush glyphs include every hanzi the game can show."""
    import os
    import re

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    used: set[str] = set()
    for dirpath, _, files in os.walk(os.path.join(root, 'richu')):
        for f in files:
            if f.endswith('.py') and f not in ('hanzi_meta.py', 'hsk.py'):
                used |= set(re.findall(r'[㐀-鿿]', open(os.path.join(dirpath, f), encoding='utf-8').read()))
    bdf = open(os.path.join(root, 'richu', 'assets', 'fonts', 'px12.bdf'), encoding='ascii').read()
    in_font = {chr(int(m)) for m in re.findall(r'^ENCODING (\d+)$', bdf, re.M)}
    missing = sorted(used - in_font)
    assert not missing, f'run scripts/build_fonts.py: missing {"".join(missing)}'
    import json

    brush = json.load(open(os.path.join(root, 'richu', 'assets', 'fonts', 'brush.json'), encoding='utf-8'))['chars']
    from richu.content import lexicon

    assert not sorted(set(lexicon.LEXICON) - set(brush)), 'run scripts/build_fonts.py: brush glyphs are out of date'

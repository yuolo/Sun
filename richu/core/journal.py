"""The journal: glyphs met, guesses, confirmation pages, texts, grammar."""
from __future__ import annotations

from ..content import grammar as G
from ..content import lexicon as L
from ..content import pages as P
from ..content import texts as T
from .phrases import glyphs_of, is_han
from .state import GameState, LogLine
from .types import GlyphDef, GrammarDef, PageDef, TextDef

MAX_GUESS = 24


def see(s: GameState, text: str) -> list[str]:
    """Registers every lexicon glyph of a text as seen. Returns the new ones."""
    fresh = []
    for ch in text:
        if is_han(ch) and L.known(ch) and ch not in s.seen:
            s.seen[ch] = len(s.seen) + 1
            fresh.append(ch)
    return fresh


def seen_glyphs(s: GameState) -> list[str]:
    return sorted(s.seen, key=lambda g: s.seen[g])


def set_guess(s: GameState, g: str, text: str) -> None:
    t = ' '.join(text.split())[:MAX_GUESS]
    if t:
        s.guesses[g] = t
    else:
        s.guesses.pop(g, None)


def confirm(s: GameState, glyphs: str | list[str]) -> list[str]:
    fresh = []
    for g in glyphs:
        if not L.known(g):
            continue
        see(s, g)
        if not s.confirmed.get(g):
            s.confirmed[g] = True
            fresh.append(g)
    return fresh


def is_confirmed(s: GameState, g: str) -> bool:
    return bool(s.confirmed.get(g))


def record_line(s: GameState, who: str, text: str, scene: str) -> None:
    if not any(l.who == who and l.text == text for l in s.log):
        s.log.append(LogLine(who, text, scene))


def contexts(s: GameState, g: str, limit: int = 6) -> list[str]:
    """Lines the player heard or read that contain the glyph (newest first)."""
    out: list[str] = []
    for line in reversed(s.log):
        if g in line.text and line.text not in out:
            out.append(line.text)
            if len(out) >= limit:
                break
    return out


# ---------------------------------------------------------------- pages


def page_chars(page: PageDef) -> list[str]:
    """Every glyph a page confirms (a slot may hold a whole word: 飞机, 行李箱)."""
    out: list[str] = []
    for w in page.glyphs:
        for ch in w:
            if ch not in out:
                out.append(ch)
    return out


def page_status(s: GameState, page: PageDef) -> str:
    """locked (not every glyph met yet) · open · done."""
    if s.pages.get(page.id):
        return 'done'
    return 'open' if all(ch in s.seen for ch in page_chars(page)) else 'locked'


def missing_count(s: GameState, page: PageDef) -> int:
    return sum(1 for ch in page_chars(page) if ch not in s.seen)


def open_pages(s: GameState) -> list[PageDef]:
    return [p for p in P.PAGES if page_status(s, p) == 'open']


def placements(s: GameState, page: PageDef) -> list[str | None]:
    saved = s.placements.get(page.id) or []
    out: list[str | None] = []
    for i in range(len(page.glyphs)):
        g = saved[i] if i < len(saved) else None
        out.append(g if g in page.glyphs else None)
    return out


def place(s: GameState, page: PageDef, slot: int, glyph: str | None) -> list[str | None]:
    """Puts a glyph into a slot (or clears it). A glyph lives in one slot at most."""
    p = placements(s, page)
    if not 0 <= slot < len(p):
        return p
    if glyph is not None:
        if glyph not in page.glyphs:
            return p
        if glyph in p:
            p[p.index(glyph)] = None
    p[slot] = glyph
    s.placements[page.id] = p
    return p


def check_page(page: PageDef, placed: list[str | None]) -> tuple[bool, bool, int]:
    """(filled, correct, wrong count)."""
    filled = all(g is not None for g in placed)
    wrong = sum(1 for i, g in enumerate(page.glyphs) if placed[i] != g)
    return filled, filled and wrong == 0, wrong


def submit_page(s: GameState, page: PageDef) -> tuple[bool, list[str]]:
    """Validates a page. On success its glyphs become confirmed."""
    filled, correct, _ = check_page(page, placements(s, page))
    if not correct:
        return False, []
    s.pages[page.id] = True
    s.placements.pop(page.id, None)
    return True, confirm(s, page_chars(page))


def _hash(text: str) -> int:
    h = 2166136261
    for ch in text:
        h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
    return h


def pool_order(page: PageDef) -> list[str]:
    """Deterministic shuffle of a page's glyphs, never equal to the answer order."""
    out = list(page.glyphs)
    seed = _hash(page.id) or 1
    for i in range(len(out) - 1, 0, -1):
        seed = (seed * 1664525 + 1013904223) & 0xFFFFFFFF
        j = seed % (i + 1)
        out[i], out[j] = out[j], out[i]
    if out == list(page.glyphs) and len(out) > 1:
        out.append(out.pop(0))
    return out


# ---------------------------------------------------------------- texts, grammar, progress


def unlock_text(s: GameState, text_id: str) -> bool:
    if text_id in T.TEXTS and text_id not in s.texts:
        s.texts.append(text_id)
        return True
    return False


def text_glyphs(t: TextDef) -> list[str]:
    return [g for g in glyphs_of(t.zh) if L.known(g)]


def text_progress(s: GameState, t: TextDef) -> tuple[int, int]:
    gs = text_glyphs(t)
    return sum(1 for g in gs if s.confirmed.get(g)), len(gs)


def understood(s: GameState, t: TextDef) -> bool:
    done, total = text_progress(s, t)
    return done == total


def grammar_unlocked(s: GameState) -> list[GrammarDef]:
    return [g for g in G.GRAMMAR if all(s.confirmed.get(c) for c in g.requires)]


def glyph(ch: str) -> GlyphDef | None:
    return L.get(ch)


def progress(s: GameState) -> tuple[int, int, int]:
    """(seen, confirmed, total in lexicon)."""
    return len(s.seen), sum(1 for v in s.confirmed.values() if v), len(L.LEXICON)


# ---------------------------------------------------------------- HSK words


def corpus(s: GameState) -> str:
    """Everything the player has heard or can read."""
    parts = [line.text for line in s.log]
    parts += [T.TEXTS[t].zh for t in s.texts if t in T.TEXTS]
    return '\n'.join(parts)


def met_words(s: GameState) -> list[str]:
    """HSK 1–3 words that appeared in something the player heard or read, in list order."""
    from ..content import hsk

    text = corpus(s)
    return [w for w in hsk.WORDS if w in text]


def word_understood(s: GameState, word: str) -> bool:
    return all(s.confirmed.get(ch) for ch in word)

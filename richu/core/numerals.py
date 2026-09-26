"""Numbers in hanzi: 0–99 is all the game needs (prices, counts, years spoken digit by digit)."""
from __future__ import annotations

DIGITS = '零一二三四五六七八九'


def to_hanzi(n: int) -> str:
    if not 0 <= n <= 99:
        raise ValueError(n)
    if n < 10:
        return DIGITS[n]
    tens, ones = divmod(n, 10)
    head = '' if tens == 1 else DIGITS[tens]
    return head + '十' + (DIGITS[ones] if ones else '')


def from_hanzi(s: str) -> int | None:
    """Parses 0–99 written in hanzi (两 counts as 2). Returns None if it is not a number."""
    s = s.replace('两', '二')
    if not s or any(ch not in DIGITS + '十' for ch in s):
        return None
    if '十' not in s:
        return DIGITS.index(s) if len(s) == 1 else None
    head, _, tail = s.partition('十')
    if len(head) > 1 or len(tail) > 1 or '十' in tail:
        return None
    tens = DIGITS.index(head) if head else 1
    ones = DIGITS.index(tail) if tail else 0
    if tens == 0:
        return None
    return tens * 10 + ones


def year_hanzi(year: int) -> str:
    """1958 → 一九五八 (years are read digit by digit)."""
    return ''.join(DIGITS[int(d)] for d in str(year))

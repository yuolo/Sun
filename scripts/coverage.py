#!/usr/bin/env python3
"""How much of HSK 1–3 the game's texts cover so far.

    python scripts/coverage.py [--missing]

Collects every Chinese string in the chapter modules and texts, then reports
covered HSK words and characters, and (with --missing) the words still absent,
grouped by level — the to-do list for writing the next chapters.
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HAN = re.compile(r'[㐀-鿿]+')
CYR = re.compile(r'[А-Яа-яЁё]')


def corpus() -> str:
    root = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'richu', 'content')
    parts = []
    for dirpath, _, files in os.walk(root):
        for f in files:
            if f.endswith('.py') and f not in ('hanzi_meta.py', 'hsk.py', 'radicals.py') and 'lexicon' not in dirpath:
                src = open(os.path.join(dirpath, f), encoding='utf-8').read()
                # Chinese shown as language: string literals with hanzi and without Cyrillic
                # (Russian hints, narration and glossaries don't count)
                for m in re.finditer(r"'([^'\n]*)'|\"([^\"\n]*)\"", src):
                    lit = m.group(1) or m.group(2) or ''
                    if HAN.search(lit) and not CYR.search(lit):
                        parts.append(lit)
    return '\n'.join(parts)


def main() -> None:
    from richu.content import hsk, lexicon

    text = corpus()
    chars = set(''.join(HAN.findall(text)))
    covered = [w for w in hsk.WORDS if w in text]
    print(f'HSK 1–3 words: {len(covered)}/{len(hsk.WORDS)}')
    for level in (1, 2, 3):
        ws = hsk.HSK[level]
        print(f'  HSK{level}: {sum(1 for w in ws if w in text)}/{len(ws)}')
    print(f'characters in texts: {len(chars)}; HSK characters covered: {len(chars & hsk.CHARS)}/{len(hsk.CHARS)}')
    print(f'lexicon: {len(lexicon.LEXICON)}; in texts but not in lexicon: {"".join(sorted(chars - set(lexicon.LEXICON)))}')
    if '--missing' in sys.argv:
        for level in (1, 2, 3):
            miss = [w for w in hsk.HSK[level] if w not in text]
            print(f'\nmissing HSK{level} ({len(miss)}):')
            print(' '.join(miss))


if __name__ == '__main__':
    main()

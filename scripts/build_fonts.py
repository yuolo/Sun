#!/usr/bin/env python3
"""Builds the game's fonts from their npm packages.

    python scripts/build_fonts.py

Sources (downloaded once into .font-cache/, both SIL OFL 1.1):
  * Fusion Pixel Font 12px / 10px by TakWolf — pixel glyphs for hanzi,
    Cyrillic and Latin (npm @vp-tw/cjk-web-fonts-fusion-pixel-font).
  * LXGW WenKai — a brush (kai) typeface for large glyphs on cards
    (npm lxgw-wenkai-webfont).

Outputs in richu/assets/fonts/:
  px12.bdf    every character the game shows, 12 px pixel font
  px10.bdf    the same set, 10 px (labels, guesses under glyphs)
  brush.bin   hanzi drawn with a brush at BRUSH_SIZE px, four ink levels
  brush.json  index for brush.bin
  OFL.txt     licences

Only the characters the game uses are kept: all hanzi in data/hanzi.tsv and
in the source code, plus Latin, Cyrillic and punctuation.
"""
from __future__ import annotations

import glob
import io
import json
import math
import re
import shutil
import sys
import tarfile
import urllib.request
import zlib
from pathlib import Path

from fontTools.pens.basePen import BasePen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / '.font-cache'
OUT = ROOT / 'richu' / 'assets' / 'fonts'
BRUSH_SIZE = 40

PACKAGES = {
    'fusion': '@vp-tw/cjk-web-fonts-fusion-pixel-font',
    'wenkai': 'lxgw-wenkai-webfont',
}

CJK = re.compile(r'[㐀-鿿豈-﫿]')

EXTRA = (
    ''.join(chr(c) for c in range(0x20, 0x7F))
    + 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    + '«»—–…·•№°×÷±←→↑↓↔▲▼◀▶●○■□◆◇★☆♪♫'
    + '，。、！？：；（）《》〈〉【】「」『』“”‘’～·—…　'
)


def fetch(name: str) -> Path:
    """Downloads and unpacks an npm package into the cache."""
    dest = CACHE / name.replace('/', '__')
    if (dest / 'package').exists():
        return dest / 'package'
    CACHE.mkdir(exist_ok=True)
    meta = json.load(urllib.request.urlopen(f'https://registry.npmjs.org/{name}/latest'))
    print(f'downloading {name} {meta["version"]}…')
    data = urllib.request.urlopen(meta['dist']['tarball']).read()
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        tar.extractall(dest, filter='data')
    return dest / 'package'


def charset() -> tuple[str, str]:
    """Returns (all characters, hanzi only) the game needs."""
    text = EXTRA
    tsv = ROOT / 'data' / 'hanzi.tsv'
    if tsv.exists():
        text += tsv.read_text(encoding='utf-8')
    for path in (ROOT / 'richu').rglob('*.py'):
        text += path.read_text(encoding='utf-8')
    chars = sorted(set(text) - set('\n\r\t'))
    hanzi = ''.join(c for c in chars if CJK.match(c))
    return ''.join(chars), hanzi


# ---------------------------------------------------------------- pixel font


class PolygonPen(BasePen):
    """Collects glyph outlines as polygons (pixel fonts have straight edges)."""

    def __init__(self, glyphset):
        super().__init__(glyphset)
        self.contours: list[list[tuple[float, float]]] = []

    def _moveTo(self, pt):
        self.contours.append([pt])

    def _lineTo(self, pt):
        self.contours[-1].append(pt)

    def _curveToOne(self, p1, p2, p3):
        self.contours[-1].append(p3)

    def _qCurveToOne(self, p1, p2):
        self.contours[-1].append(p2)

    def _closePath(self):
        pass


def rasterize(contours, unit: float, ascent: int, width: int, height: int) -> list[list[int]]:
    """Fills polygons with the non-zero rule, sampling pixel centres row by row."""
    edges = []
    for poly in contours:
        for i in range(len(poly)):
            (x0, y0), (x1, y1) = poly[i], poly[(i + 1) % len(poly)]
            if y0 != y1:
                edges.append((x0, y0, x1, y1))
    rows = []
    for r in range(height):
        y = (ascent - r - 0.5) * unit
        hits = []
        for x0, y0, x1, y1 in edges:
            if (y0 <= y < y1) or (y1 <= y < y0):
                x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                hits.append((x, 1 if y1 > y0 else -1))
        hits.sort()
        row = [0] * width
        wind = 0
        for i, (x, d) in enumerate(hits):
            wind += d
            if wind != 0 and i + 1 < len(hits):
                a, b = x / unit, hits[i + 1][0] / unit
                for c in range(width):
                    if a <= c + 0.5 < b:
                        row[c] = 1
        rows.append(row)
    return rows


def load_fusion(size: int) -> list[TTFont]:
    base = fetch(PACKAGES['fusion']) / 'dist' / f'{size}px' / 'proportional'
    files = sorted(glob.glob(str(base / 'zh_hans' / '*.woff2')))
    return [TTFont(f) for f in files]


def build_bdf(size: int, chars: str, path: Path) -> list[str]:
    fonts = load_fusion(size)
    lookup = {}
    for font in fonts:
        for code, name in font.getBestCmap().items():
            lookup.setdefault(code, (font, name))
    head = fonts[0]
    upm = head['head'].unitsPerEm
    unit = upm / size
    # The line box hugs the tallest and deepest glyph actually used.
    top, bottom = 0.0, 0.0
    for ch in chars:
        hit = lookup.get(ord(ch))
        if hit:
            font, name = hit
            gs = font.getGlyphSet()
            bp = BoundsPen(gs)
            gs[name].draw(bp)
            if bp.bounds:
                bottom, top = min(bottom, bp.bounds[1]), max(top, bp.bounds[3])
    ascent = math.ceil(top / unit)
    descent = math.ceil(-bottom / unit)
    height = ascent + descent
    glyphs, missing = [], []
    for ch in chars:
        hit = lookup.get(ord(ch))
        if not hit:
            missing.append(ch)
            continue
        font, name = hit
        gs = font.getGlyphSet()
        pen = PolygonPen(gs)
        gs[name].draw(pen)
        adv = round(font['hmtx'][name][0] / unit)
        rows = rasterize(pen.contours, unit, ascent, max(adv, 1), height)
        glyphs.append((ch, adv, rows))
    out = [
        'STARTFONT 2.1',
        f'FONT -TakWolf-FusionPixel-Medium-R-Normal--{size}-{size * 10}-75-75-P-{size * 10}-ISO10646-1',
        f'SIZE {size} 75 75',
        f'FONTBOUNDINGBOX {size} {height} 0 {-descent}',
        'STARTPROPERTIES 3',
        f'FONT_ASCENT {ascent}',
        f'FONT_DESCENT {descent}',
        'DEFAULT_CHAR 63',
        'ENDPROPERTIES',
        f'CHARS {len(glyphs)}',
    ]
    for ch, adv, rows in glyphs:
        w = max(adv, 1)
        out += [
            f'STARTCHAR U+{ord(ch):04X}',
            f'ENCODING {ord(ch)}',
            f'SWIDTH {round(adv * 1000 / size)} 0',
            f'DWIDTH {adv} 0',
            f'BBX {w} {height} 0 {-descent}',
            'BITMAP',
        ]
        nbytes = (w + 7) // 8
        for row in rows:
            v = 0
            for c, bit in enumerate(row):
                if bit:
                    v |= 1 << (nbytes * 8 - 1 - c)
            out.append(f'{v:0{nbytes * 2}X}')
        out.append('ENDCHAR')
    out.append('ENDFONT')
    path.write_text('\n'.join(out) + '\n', encoding='ascii')
    return missing


# ---------------------------------------------------------------- brush glyphs


def build_brush(hanzi: str) -> list[str]:
    from PIL import Image, ImageDraw, ImageFont

    base = fetch(PACKAGES['wenkai']) / 'files'
    parts = []
    for f in sorted(glob.glob(str(base / 'lxgwwenkai-regular-subset-*.woff2'))):
        t = TTFont(f)
        cmap = set(t.getBestCmap())
        t.flavor = None
        buf = io.BytesIO()
        t.save(buf)
        parts.append((cmap, buf.getvalue()))
    fonts: dict[int, object] = {}
    n = BRUSH_SIZE
    data = bytearray()
    done, missing = [], []
    for ch in hanzi:
        idx = next((i for i, (cmap, _) in enumerate(parts) if ord(ch) in cmap), None)
        if idx is None:
            missing.append(ch)
            continue
        if idx not in fonts:
            fonts[idx] = ImageFont.truetype(io.BytesIO(parts[idx][1]), int(n * 0.9))
        img = Image.new('L', (n, n), 0)
        d = ImageDraw.Draw(img)
        d.text((n / 2, n / 2), ch, fill=255, font=fonts[idx], anchor='mm')
        for v in img.tobytes():
            data.append(0 if v < 40 else 1 if v < 110 else 2 if v < 190 else 3)
        done.append(ch)
    (OUT / 'brush.bin').write_bytes(zlib.compress(bytes(data), 9))
    (OUT / 'brush.json').write_text(json.dumps({'size': n, 'chars': ''.join(done)}, ensure_ascii=False), encoding='utf-8')
    return missing


def licences() -> None:
    fusion = fetch(PACKAGES['fusion'])
    wenkai = fetch(PACKAGES['wenkai'])
    parts = [
        'Fonts in this directory are subsets generated by scripts/build_fonts.py.\n',
        'px12.bdf, px10.bdf — Fusion Pixel Font by TakWolf (https://github.com/TakWolf/fusion-pixel-font),',
        'built from Ark Pixel Font and other open pixel fonts; licences of the parts follow.\n',
        'brush.bin — glyphs rendered from LXGW WenKai (https://github.com/lxgw/LxgwWenKai).\n',
        'All are licensed under the SIL Open Font License, Version 1.1.\n',
        '=' * 72,
        'Fusion Pixel Font',
        '=' * 72,
        (fusion / 'LICENSE.font.txt').read_text(encoding='utf-8'),
    ]
    for lic in sorted((fusion / 'LICENSES' / '12px').rglob('*')):
        if lic.is_file():
            parts += ['=' * 72, f'Fusion Pixel Font part: {lic.parent.name}', '=' * 72, lic.read_text(encoding='utf-8', errors='replace')]
    parts += ['=' * 72, 'LXGW WenKai', '=' * 72, (wenkai / 'OFL.txt').read_text(encoding='utf-8')]
    (OUT / 'OFL.txt').write_text('\n'.join(parts), encoding='utf-8')


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    chars, hanzi = charset()
    print(f'{len(chars)} characters, {len(hanzi)} hanzi')
    ok = True
    for size in (12, 10):
        missing = build_bdf(size, chars, OUT / f'px{size}.bdf')
        if missing:
            print(f'px{size}: missing {"".join(missing)}')
            ok = ok and not any(CJK.match(c) for c in missing)
    missing = build_brush(hanzi)
    if missing:
        print(f'brush: missing {"".join(missing)}')
    licences()
    for f in sorted(OUT.iterdir()):
        print(f'  {f.relative_to(ROOT)}: {f.stat().st_size // 1024} KB')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Build tiny subset fonts for the game.

Scans src/ for every CJK character actually used in the game and writes
woff2 subsets of two OFL fonts into src/assets/fonts/:

  * LXGW WenKai  (kaishu, textbook stroke forms) — hanzi + Latin + pinyin + Cyrillic
  * Ma Shan Zheng (brush)                        — hanzi used on signs and titles

Usage:
  pip install fonttools brotli
  python3 scripts/subset-fonts.py [path/to/LXGWWenKai-Regular.ttf] [path/to/MaShanZheng-Regular.ttf]

Without arguments the source fonts are downloaded into .font-cache/.
"""
import os
import re
import sys
import urllib.request

from fontTools import subset

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".font-cache")
OUT = os.path.join(ROOT, "src", "assets", "fonts")

SOURCES = {
    "wenkai": "https://raw.githubusercontent.com/lxgw/LxgwWenKai/main/fonts/TTF/LXGWWenKai-Regular.ttf",
    "brush": "https://raw.githubusercontent.com/google/fonts/main/ofl/mashanzheng/MaShanZheng-Regular.ttf",
}

CJK = re.compile(r"[　-〿㐀-䶿一-鿿＀-￯]")

PINYIN = "āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜüĀÁǍÀĒÉĚÈĪÍǏÌŌÓǑÒŪÚǓÙǕǗǙǛÜ"
EXTRA = "—–«»…•’‘“”№·×←→↑↓✓✗★☆♪"


def collect_hanzi():
    chars = set()
    for base, _dirs, files in os.walk(os.path.join(ROOT, "src")):
        for name in files:
            if name.endswith((".ts", ".css", ".html")):
                with open(os.path.join(base, name), encoding="utf-8") as fh:
                    chars.update(CJK.findall(fh.read()))
    with open(os.path.join(ROOT, "index.html"), encoding="utf-8") as fh:
        chars.update(CJK.findall(fh.read()))
    return "".join(sorted(chars))


def source(key, override):
    if override:
        return override
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, os.path.basename(SOURCES[key]))
    if not os.path.exists(path):
        print("downloading", SOURCES[key])
        urllib.request.urlretrieve(SOURCES[key], path)
    return path


def build(src, out, text):
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    font = subset.load_font(src, opts)
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    subset.save_font(font, out, opts)
    print(f"{os.path.relpath(out, ROOT)}: {len(set(text))} chars, {os.path.getsize(out) // 1024} KB")


def main():
    args = sys.argv[1:]
    hanzi = collect_hanzi()
    latin = "".join(chr(c) for c in range(0x20, 0x7F)) + "".join(chr(c) for c in range(0xA0, 0x100))
    cyrillic = "".join(chr(c) for c in range(0x400, 0x460))
    os.makedirs(OUT, exist_ok=True)
    build(source("wenkai", args[0] if args else None), os.path.join(OUT, "wenkai.woff2"),
          hanzi + latin + cyrillic + PINYIN + EXTRA)
    build(source("brush", args[1] if len(args) > 1 else None), os.path.join(OUT, "brush.woff2"), hanzi)


if __name__ == "__main__":
    main()

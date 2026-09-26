#!/usr/bin/env python3
"""Builds the game for the browser: build/richu.pyxapp and build/site/index.html.

    python scripts/build_web.py

Stages only the package (no tests, docs or caches) with a tiny startup
script, packs it with ``pyxel package`` and wraps it with ``pyxel app2html``.
The page loads Pyxel's web runtime (Pyodide) from a CDN.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, 'build')
APP = os.path.join(BUILD, 'richu')


def main() -> None:
    shutil.rmtree(BUILD, ignore_errors=True)
    os.makedirs(APP)
    shutil.copytree(
        os.path.join(ROOT, 'richu'), os.path.join(APP, 'richu'),
        ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'devtools'),
    )
    with open(os.path.join(APP, 'main.py'), 'w', encoding='utf-8') as f:
        f.write('from richu.game import main\n\nmain()\n')
    subprocess.run(['pyxel', 'package', APP, os.path.join(APP, 'main.py')], cwd=BUILD, check=True)
    pyxapp = os.path.join(BUILD, 'richu.pyxapp')
    if not os.path.exists(pyxapp):
        sys.exit('pyxel package did not produce richu.pyxapp')
    subprocess.run(['pyxel', 'app2html', pyxapp], cwd=BUILD, check=True)
    site = os.path.join(BUILD, 'site')
    os.makedirs(site)
    shutil.copy(os.path.join(BUILD, 'richu.html'), os.path.join(site, 'index.html'))
    size = os.path.getsize(os.path.join(site, 'index.html')) // 1024
    print(f'build/richu.pyxapp and build/site/index.html ({size} KB)')


if __name__ == '__main__':
    main()

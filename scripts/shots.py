#!/usr/bin/env python3
"""Screenshots of game screens in headless mode.

    python scripts/shots.py [out_dir]          # title screen and more as they appear
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from richu import platform  # noqa: E402
from richu.engine import app  # noqa: E402
from richu.engine.driver import Driver  # noqa: E402


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else 'shots'
    os.makedirs(out, exist_ok=True)
    platform.use_memory_storage()
    app.init(headless=True)
    d = Driver()
    from richu.ui.title import TitleScreen

    app.APP.push(TitleScreen())
    d.step(2)
    d.move(160, 120)
    d.shot(os.path.join(out, 'title'))
    print('saved to', out)


if __name__ == '__main__':
    main()

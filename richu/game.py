"""Entry point: ``python -m richu``."""
from __future__ import annotations

import sys

from .engine import app


def main(argv: list[str] | None = None) -> None:
    args = sys.argv[1:] if argv is None else argv
    app.init(headless='--headless' in args)
    from .ui.menus import TitleScreen
    from .ui.session import SESSION

    SESSION.boot()
    app.APP.push(TitleScreen())
    app.run()


if __name__ == '__main__':
    main()

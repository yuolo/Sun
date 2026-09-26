"""Differences between the desktop and the browser (Pyodide) builds.

* Saves: ``localStorage`` in the browser, a JSON file in Pyxel's user data
  directory on the desktop, memory in tests.
* Voice: the browser's ``speechSynthesis`` (zh-CN); none on the desktop.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any

IS_WEB = sys.platform == 'emscripten'

_memory: dict[str, str] | None = None


def use_memory_storage() -> None:
    """Tests and headless runs keep saves in memory."""
    global _memory
    _memory = {}


def _data_dir() -> str:
    import pyxel

    return pyxel.user_data_dir('richu', 'richu')


def storage_get(key: str) -> str | None:
    if _memory is not None:
        return _memory.get(key)
    try:
        if IS_WEB:
            import js  # type: ignore[import-not-found]

            return js.window.localStorage.getItem(key)
        path = os.path.join(_data_dir(), f'{key}.json')
        if os.path.exists(path):
            with open(path, encoding='utf-8') as f:
                return f.read()
    except Exception:
        pass
    return None


def storage_set(key: str, value: str) -> None:
    if _memory is not None:
        _memory[key] = value
        return
    try:
        if IS_WEB:
            import js  # type: ignore[import-not-found]

            js.window.localStorage.setItem(key, value)
            return
        path = os.path.join(_data_dir(), f'{key}.json')
        tmp = path + '.tmp'
        with open(tmp, 'w', encoding='utf-8') as f:
            f.write(value)
        os.replace(tmp, path)
    except Exception:
        pass


def storage_del(key: str) -> None:
    if _memory is not None:
        _memory.pop(key, None)
        return
    try:
        if IS_WEB:
            import js  # type: ignore[import-not-found]

            js.window.localStorage.removeItem(key)
            return
        path = os.path.join(_data_dir(), f'{key}.json')
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass


def load_json(key: str) -> Any:
    raw = storage_get(key)
    if not raw:
        return None
    try:
        return json.loads(raw)
    except ValueError:
        return None


def save_json(key: str, value: Any) -> None:
    storage_set(key, json.dumps(value, ensure_ascii=False, separators=(',', ':')))


# ---------------------------------------------------------------- voice


def can_speak() -> bool:
    if not IS_WEB:
        return False
    try:
        import js  # type: ignore[import-not-found]

        return bool(getattr(js.window, 'speechSynthesis', None))
    except Exception:
        return False


def speak(text: str, rate: float = 0.8) -> None:
    """Reads Chinese text aloud in the browser; silently does nothing elsewhere."""
    if not IS_WEB:
        return
    try:
        import js  # type: ignore[import-not-found]

        synth = js.window.speechSynthesis
        synth.cancel()
        utter = js.SpeechSynthesisUtterance.new(text)
        utter.lang = 'zh-CN'
        utter.rate = rate
        voices = [v for v in synth.getVoices() if str(v.lang).lower().startswith('zh')]
        if voices:
            utter.voice = voices[0]
        synth.speak(utter)
    except Exception:
        pass

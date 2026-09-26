"""Runs a coroutine that never waits (for the headless context)."""
from __future__ import annotations

from ..engine.tasks import run_sync as run  # noqa: F401

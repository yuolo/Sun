"""Coroutine scripts without asyncio.

Scene scripts are ``async def`` functions that ``await`` futures: a speech
bubble that closes on click, a walk that ends on arrival, a dialog that
returns an answer. The game loop calls :meth:`Scheduler.step` once per frame;
each task runs until it awaits a future that is not done yet.

In tests the headless context resolves every future at once, so
:func:`run_sync` finishes a script in a single call.
"""
from __future__ import annotations

from collections.abc import Coroutine
from typing import Any, Generic, TypeVar

T = TypeVar('T')
_UNSET: Any = object()


class Future(Generic[T]):
    """A value that will be set later (by the UI, a timer or another task)."""

    __slots__ = ('done', 'value')

    def __init__(self, value: Any = _UNSET) -> None:
        self.done = value is not _UNSET
        self.value: Any = None if value is _UNSET else value

    def set(self, value: Any = None) -> None:
        if not self.done:
            self.done = True
            self.value = value

    def __await__(self):
        if not self.done:
            yield self
        return self.value


def resolved(value: Any = None) -> Future:
    return Future(value)


class Task:
    """Runs one coroutine step by step."""

    def __init__(self, coro: Coroutine[Any, Any, Any], name: str = '') -> None:
        self.coro = coro
        self.name = name
        self.waiting: Future | None = None
        self.finished = False
        self.result: Any = None
        self.done = Future()

    def step(self) -> None:
        while not self.finished:
            if self.waiting is not None and not self.waiting.done:
                return
            try:
                fut = self.coro.send(None)
            except StopIteration as stop:
                self.finished = True
                self.result = stop.value
                self.done.set(stop.value)
                return
            if not isinstance(fut, Future):
                raise TypeError(f'script {self.name!r} awaited {fut!r}; only Future is supported')
            self.waiting = fut

    def cancel(self) -> None:
        if not self.finished:
            self.coro.close()
            self.finished = True
            self.done.set(None)


class Scheduler:
    """Steps all running scripts and counts down timers once per frame."""

    def __init__(self) -> None:
        self.tasks: list[Task] = []
        self.timers: list[list[Any]] = []

    def spawn(self, coro: Coroutine[Any, Any, Any], name: str = '') -> Task:
        task = Task(coro, name)
        self.tasks.append(task)
        task.step()
        if task.finished:
            self.tasks.remove(task)
        return task

    def sleep(self, frames: int) -> Future:
        fut: Future = Future()
        if frames <= 0:
            fut.set()
        else:
            self.timers.append([frames, fut])
        return fut

    @property
    def busy(self) -> bool:
        return bool(self.tasks)

    def step(self) -> None:
        for timer in self.timers:
            timer[0] -= 1
            if timer[0] <= 0:
                timer[1].set()
        self.timers = [t for t in self.timers if not t[1].done]
        for task in list(self.tasks):
            task.step()
            if task.finished and task in self.tasks:
                self.tasks.remove(task)

    def cancel_all(self) -> None:
        for task in self.tasks:
            task.cancel()
        self.tasks.clear()
        self.timers.clear()


def run_sync(coro: Coroutine[Any, Any, T]) -> T:
    """Runs a coroutine that never waits (headless scripts). Raises if it blocks."""
    task = Task(coro, 'sync')
    task.step()
    if not task.finished:
        task.cancel()
        raise RuntimeError('script blocked on a future in synchronous mode')
    return task.result

from richu.engine.tasks import Future, Scheduler, run_sync


def test_run_sync_returns_value():
    async def script():
        a = await Future(2)
        return a + 1

    assert run_sync(script()) == 3


def test_scheduler_waits_for_futures_and_timers():
    sched = Scheduler()
    gate: Future = Future()
    log = []

    async def script():
        log.append('start')
        v = await gate
        log.append(v)
        await sched.sleep(2)
        log.append('end')

    task = sched.spawn(script())
    assert log == ['start'] and not task.finished
    sched.step()
    assert log == ['start']
    gate.set('open')
    sched.step()
    assert log == ['start', 'open']
    sched.step()
    sched.step()
    assert log[-1] == 'end' and task.finished and not sched.busy


def test_run_sync_raises_when_blocked():
    async def script():
        await Future()

    try:
        run_sync(script())
    except RuntimeError:
        return
    raise AssertionError('expected RuntimeError')

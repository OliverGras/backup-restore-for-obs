"""Running tasks in the background.

Skipped where Qt can't be loaded (e.g. a server without graphics libraries).
"""

import time
from collections.abc import Callable

import pytest

pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)

from PySide6.QtCore import QCoreApplication, QEvent, QThread  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from obs_backup.gui.tasks import LatestCall, TaskRunner  # noqa: E402


@pytest.fixture
def app() -> QApplication:
    existing = QApplication.instance()
    return existing if isinstance(existing, QApplication) else QApplication([])


def _wait_until(done: Callable[[], bool], app: QApplication) -> None:
    deadline = time.monotonic() + 10
    while not done():
        assert time.monotonic() < deadline, "task did not finish"
        app.processEvents()


def _fail(_progress: object) -> None:
    raise OSError("disk full")


def test_failed_task_reports_to_its_caller(app: QApplication) -> None:
    runner = TaskRunner()
    shown: list[BaseException] = []
    told: list[BaseException] = []
    runner.failed.connect(shown.append)
    assert runner.run("x", _fail, on_done=lambda _: None, on_error=told.append)
    _wait_until(lambda: not runner.busy, app)
    assert shown == told and [str(e) for e in told] == ["disk full"]
    assert isinstance(told[0], OSError)  # so the window can word known errors itself


def test_finished_task_reports_its_result(app: QApplication) -> None:
    runner = TaskRunner()
    results: list[object] = []
    runner.run("x", lambda progress: 42, on_done=results.append)
    _wait_until(lambda: not runner.busy, app)
    assert results == [42]


def test_finished_task_frees_its_thread(app: QApplication) -> None:
    runner = TaskRunner()
    for _ in range(3):
        runner.run("x", lambda progress: None, on_done=lambda _: None)
        _wait_until(lambda: not runner.busy, app)
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    assert runner.findChildren(QThread) == []


def test_latest_call_delivers_only_the_newest_result(app: QApplication) -> None:
    calls = LatestCall()
    try:
        results: list[int] = []
        calls.call(lambda: 1, results.append)
        calls.call(lambda: 2, results.append)
        _wait_until(lambda: bool(results), app)

        calls.call(lambda: 3, results.append)
        calls.cancel()
        calls.call(lambda: 4, results.append)  # runs after 3, so 3 has been dropped by then
        _wait_until(lambda: results[-1] == 4, app)
        assert results == [2, 4]
    finally:
        calls.stop()

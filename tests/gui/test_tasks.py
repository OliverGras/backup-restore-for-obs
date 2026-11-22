"""Running tasks in the background.

Skipped where Qt can't be loaded (e.g. a server without graphics libraries).
"""

import time
from collections.abc import Callable

import pytest

pytest.importorskip("PySide6.QtWidgets", exc_type=ImportError)

from PySide6.QtWidgets import QApplication  # noqa: E402

from obs_backup.gui.tasks import TaskRunner  # noqa: E402


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
    shown: list[str] = []
    told: list[str] = []
    runner.failed.connect(shown.append)
    assert runner.run("x", _fail, on_done=lambda _: None, on_error=told.append)
    _wait_until(lambda: not runner.busy, app)
    assert shown == told == ["disk full"]


def test_finished_task_reports_its_result(app: QApplication) -> None:
    runner = TaskRunner()
    results: list[object] = []
    runner.run("x", lambda progress: 42, on_done=results.append)
    _wait_until(lambda: not runner.busy, app)
    assert results == [42]

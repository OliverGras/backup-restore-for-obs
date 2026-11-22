"""Run long operations in background threads.

- ``TaskRunner``: backup and restore, one at a time; the window waits for them.
- ``LatestCall``: quick lookups (counting media) that must not freeze the window;
  only the newest result counts.
"""

import traceback
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QCoreApplication, QObject, QThread, Signal, Slot

from obs_backup.backup import Progress

Task = Callable[[Progress], Any]


class Worker(QObject):
    """Runs one task in the thread it is moved to."""

    progress = Signal(int, int, str)
    finished = Signal(object)
    failed = Signal(object)  # the exception

    def __init__(self, fn: Task) -> None:
        super().__init__()
        self._fn = fn

    @Slot()
    def run(self) -> None:
        try:
            result = self._fn(self.progress.emit)
        except Exception as e:  # shown to the user
            traceback.print_exc()
            self.failed.emit(e)
        else:
            self.finished.emit(result)


class TaskRunner(QObject):
    """Runs one task at a time and reports its progress in the GUI thread."""

    started = Signal(str)  # status message
    progress = Signal(int, int, str)  # done, total, current item
    ended = Signal()
    failed = Signal(object)  # the exception the task raised

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._thread: QThread | None = None
        self._worker: Worker | None = None
        self._on_done: Callable[[Any], None] | None = None
        self._on_error: Callable[[BaseException], None] | None = None

    @property
    def busy(self) -> bool:
        return self._thread is not None

    def run(
        self,
        message: str,
        fn: Task,
        on_done: Callable[[Any], None],
        on_error: Callable[[BaseException], None] | None = None,
    ) -> bool:
        """Start ``fn(progress)`` in the background.

        Afterwards ``on_done(result)`` runs, or, if ``fn`` raised, ``on_error(exception)``
        (after ``failed`` was emitted, which shows the error).
        """
        if self.busy:
            return False
        thread = QThread(self)
        worker = Worker(fn)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        # Slots of this object run in the GUI thread (queued connections).
        worker.progress.connect(self._on_progress)
        worker.finished.connect(self._on_finished)
        worker.failed.connect(self._on_failed)
        self._thread, self._worker = thread, worker
        self._on_done, self._on_error = on_done, on_error
        self.started.emit(message)
        thread.start()
        return True

    @Slot(int, int, str)
    def _on_progress(self, done: int, total: int, current: str) -> None:
        self.progress.emit(done, total, current)

    @Slot(object)
    def _on_finished(self, result: object) -> None:
        on_done = self._on_done
        self._stop()
        if on_done:
            on_done(result)

    @Slot(object)
    def _on_failed(self, error: BaseException) -> None:
        on_error = self._on_error
        self._stop()
        self.failed.emit(error)
        if on_error:
            on_error(error)

    def _stop(self) -> None:
        if self._thread is not None:
            self._thread.quit()
            self._thread.wait()
            self._thread.deleteLater()  # a child of this runner; not needed again
        self._thread = self._worker = self._on_done = self._on_error = None
        self.ended.emit()


class _CallWorker(QObject):
    done = Signal(int, object)  # call number, result

    def __init__(self, latest: Callable[[], int]) -> None:
        super().__init__()
        self._latest = latest

    @Slot(int, object)
    def run(self, number: int, fn: Callable[[], Any]) -> None:
        if number != self._latest():
            return  # a newer call came in while this one waited
        try:
            result = fn()
        except Exception:  # a lookup only; the GUI keeps its previous text
            traceback.print_exc()
            return
        self.done.emit(number, result)


class LatestCall(QObject):
    """Runs functions in one background thread and hands their results to the GUI thread.

    Only the result of the newest call is delivered: earlier calls, and calls made
    before ``cancel``, are dropped. ``stop`` must run before the app quits (it also
    runs on ``aboutToQuit``).
    """

    _request = Signal(int, object)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._number = 0
        self._on_done: Callable[[Any], None] | None = None
        self._thread = QThread(self)
        self._worker = _CallWorker(lambda: self._number)
        self._worker.moveToThread(self._thread)
        self._request.connect(self._worker.run)
        self._worker.done.connect(self._deliver)
        self._thread.start()
        if (app := QCoreApplication.instance()) is not None:
            app.aboutToQuit.connect(self.stop)

    def call(self, fn: Callable[[], Any], on_done: Callable[[Any], None]) -> None:
        """Run ``fn()`` in the background, then ``on_done(result)`` if no newer call came."""
        self._number += 1
        self._on_done = on_done
        self._request.emit(self._number, fn)

    def cancel(self) -> None:
        """Drop the result of the pending call."""
        self._number += 1
        self._on_done = None

    @Slot(int, object)
    def _deliver(self, number: int, result: object) -> None:
        if number == self._number and self._on_done is not None:
            on_done, self._on_done = self._on_done, None
            on_done(result)

    def stop(self) -> None:
        """Wait for the running call to end and stop the thread."""
        self.cancel()
        self._thread.quit()
        self._thread.wait()

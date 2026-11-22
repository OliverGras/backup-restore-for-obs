"""Run long operations (backup, restore) in a background thread."""

from __future__ import annotations

import traceback
from collections.abc import Callable
from typing import Any

from PySide6.QtCore import QObject, QThread, Signal, Slot

from obs_backup.backup import Progress

Task = Callable[[Progress], Any]


class Worker(QObject):
    """Runs one task in the thread it is moved to."""

    progress = Signal(int, int, str)
    finished = Signal(object)
    failed = Signal(str)

    def __init__(self, fn: Task) -> None:
        super().__init__()
        self._fn = fn

    @Slot()
    def run(self) -> None:
        try:
            result = self._fn(self.progress.emit)
        except Exception as e:  # shown to the user
            traceback.print_exc()
            self.failed.emit(str(e) or type(e).__name__)
        else:
            self.finished.emit(result)


class TaskRunner(QObject):
    """Runs one task at a time and reports its progress in the GUI thread."""

    started = Signal(str)  # status message
    progress = Signal(int, int, str)  # done, total, current item
    ended = Signal()
    failed = Signal(str)  # error message

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._thread: QThread | None = None
        self._worker: Worker | None = None
        self._on_done: Callable[[Any], None] | None = None

    @property
    def busy(self) -> bool:
        return self._thread is not None

    def run(self, message: str, fn: Task, on_done: Callable[[Any], None]) -> bool:
        """Start ``fn(progress)`` in the background; ``on_done(result)`` runs afterwards."""
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
        self._thread, self._worker, self._on_done = thread, worker, on_done
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

    @Slot(str)
    def _on_failed(self, error: str) -> None:
        self._stop()
        self.failed.emit(error)

    def _stop(self) -> None:
        if self._thread is not None:
            self._thread.quit()
            self._thread.wait()
        self._thread = self._worker = self._on_done = None
        self.ended.emit()

"""Dialog listing the app's own license and the bundled third-party licenses."""

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices, QFontDatabase
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QListWidget,
    QSplitter,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from obs_backup.i18n import tr
from obs_backup.legal import license_documents


class LicensesDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(tr("licenses_title"))
        self.resize(860, 600)
        self._docs = license_documents()

        self._list = QListWidget()
        self._list.addItems([name for name, _ in self._docs])
        self._text = QTextBrowser()
        # Only web links open (in the browser); links to repo files mean nothing here.
        self._text.setOpenLinks(False)
        self._text.anchorClicked.connect(self._open_link)

        splitter = QSplitter()
        splitter.addWidget(self._list)
        splitter.addWidget(self._text)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([240, 620])
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(splitter, 1)
        layout.addWidget(buttons)

        self._list.currentRowChanged.connect(self._show)
        self._list.setCurrentRow(0)

    @staticmethod
    def _open_link(url: QUrl) -> None:
        if url.scheme() in ("http", "https"):
            QDesktopServices.openUrl(url)

    def _show(self, row: int) -> None:
        if not 0 <= row < len(self._docs):
            return
        path = self._docs[row][1]
        content = path.read_text(encoding="utf-8", errors="replace")
        if path.suffix == ".md":
            self._text.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.GeneralFont))
            self._text.setLineWrapMode(QTextBrowser.LineWrapMode.WidgetWidth)
            self._text.setMarkdown(content)
        else:
            self._text.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
            self._text.setLineWrapMode(QTextBrowser.LineWrapMode.NoWrap)
            self._text.setPlainText(content)

from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QPainter, QColor, QFont
from PySide2.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy

from common.models import SyncStatus
from client.i18n import sync_status_label


class StatusIndicator(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        self._dot = _DotWidget(self)
        self._dot.setFixedSize(12, 12)
        self._label = QLabel(self)
        self._label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(self._dot)
        layout.addWidget(self._label)
        layout.addStretch()

    def set_status(self, status: SyncStatus) -> None:
        colors = {
            SyncStatus.SYNCED: QColor("#4CAF50"),
            SyncStatus.SYNCING: QColor("#2196F3"),
            SyncStatus.NOT_SYNCED: QColor("#9E9E9E"),
            SyncStatus.ERROR: QColor("#F44336"),
        }
        self._dot.set_color(colors.get(status, QColor("#9E9E9E")))
        self._label.setText(sync_status_label(status.value))


class _DotWidget(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._color = QColor("#9E9E9E")

    def set_color(self, color: QColor) -> None:
        self._color = color
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setBrush(self._color)
        p.setPen(Qt.NoPen)
        r = self.rect().adjusted(1, 1, -1, -1)
        p.drawEllipse(r)

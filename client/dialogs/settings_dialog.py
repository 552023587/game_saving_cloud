from PySide2.QtCore import Signal, QSettings
from PySide2.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QSpinBox,
    QDialogButtonBox, QVBoxLayout, QLabel
)

from client.i18n import tr


class SettingsDialog(QDialog):
    server_changed = Signal(str, int)

    def __init__(self, current_host: str, current_port: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("dialog.settings.title"))
        self.setMinimumWidth(320)

        layout = QVBoxLayout(self)

        label = QLabel(tr("dialog.settings.description"))
        label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(label)

        form = QFormLayout()
        self._host_edit = QLineEdit(current_host)
        self._host_edit.setPlaceholderText(tr("dialog.settings.host_placeholder"))
        form.addRow(tr("dialog.settings.host_label"), self._host_edit)

        self._port_spin = QSpinBox()
        self._port_spin.setRange(1, 65535)
        self._port_spin.setValue(current_port)
        form.addRow(tr("dialog.settings.port_label"), self._port_spin)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        host = self._host_edit.text().strip()
        port = self._port_spin.value()
        if not host:
            return
        s = QSettings("GameSaveCloud", "Client")
        s.setValue("server/host", host)
        s.setValue("server/port", port)

        self.server_changed.emit(host, port)
        super().accept()

    @staticmethod
    def load_server_address() -> tuple:
        s = QSettings("GameSaveCloud", "Client")
        return (
            s.value("server/host", "127.0.0.1"),
            int(s.value("server/port", 3000)),
        )

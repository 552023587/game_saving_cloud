from typing import Optional

from PySide2.QtCore import Qt
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton,
    QDialogButtonBox, QVBoxLayout, QLabel, QHBoxLayout,
    QFileDialog
)

from client.i18n import tr


class AddGameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("dialog.add_game.title"))
        self.setMinimumWidth(400)
        self._icon_path: Optional[str] = None

        layout = QVBoxLayout(self)

        label = QLabel(tr("dialog.add_game.description"))
        label.setStyleSheet("font-weight: bold; font-size: 12px;")
        layout.addWidget(label)

        form = QFormLayout()
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText(tr("dialog.add_game.name_placeholder"))
        form.addRow(tr("dialog.add_game.name_label"), self._name_edit)

        path_layout = QHBoxLayout()
        self._path_edit = QLineEdit()
        self._path_edit.setPlaceholderText(tr("dialog.add_game.path_placeholder"))
        browse_btn = QPushButton(tr("dialog.add_game.browse"))
        browse_btn.clicked.connect(self._browse_path)
        path_layout.addWidget(self._path_edit)
        path_layout.addWidget(browse_btn)
        form.addRow(tr("dialog.add_game.path_label"), path_layout)

        layout.addLayout(form)

        icon_layout = QHBoxLayout()
        self._icon_preview = QLabel()
        self._icon_preview.setFixedSize(100, 200)
        self._icon_preview.setAlignment(Qt.AlignCenter)
        self._icon_preview.setStyleSheet("background-color: #171a21; border: 1px solid #2a3f56;")
        self._icon_preview.setText(tr("dialog.add_game.icon_preview"))
        icon_btn_layout = QVBoxLayout()
        choose_icon_btn = QPushButton(tr("dialog.add_game.choose_icon"))
        choose_icon_btn.clicked.connect(self._browse_icon)
        clear_icon_btn = QPushButton(tr("dialog.add_game.clear_icon"))
        clear_icon_btn.clicked.connect(self._clear_icon)
        icon_btn_layout.addWidget(choose_icon_btn)
        icon_btn_layout.addWidget(clear_icon_btn)
        icon_btn_layout.addStretch()
        icon_layout.addWidget(self._icon_preview)
        icon_layout.addLayout(icon_btn_layout)
        layout.addLayout(icon_layout)

        self._error_label = QLabel()
        self._error_label.setStyleSheet("color: #FF6B6B;")
        self._error_label.setVisible(False)
        layout.addWidget(self._error_label)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse_path(self):
        path = QFileDialog.getExistingDirectory(self, tr("dialog.add_game.browse_path_title"))
        if path:
            self._path_edit.setText(path)

    def _browse_icon(self):
        path, _ = QFileDialog.getOpenFileName(
            self, tr("dialog.add_game.browse_icon_title"), "",
            tr("dialog.change_icon.filter")
        )
        if path:
            self._icon_path = path
            pix = QPixmap(path)
            scaled = pix.scaled(100, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self._icon_preview.setPixmap(scaled)

    def _clear_icon(self):
        self._icon_path = None
        self._icon_preview.setPixmap(QPixmap())
        self._icon_preview.setText(tr("dialog.add_game.icon_preview"))

    def _validate_and_accept(self):
        name = self._name_edit.text().strip()
        if not name:
            self._error_label.setText(tr("dialog.add_game.validation_required"))
            self._error_label.setVisible(True)
            return
        self._error_label.setVisible(False)
        super().accept()

    def get_game_data(self) -> tuple:
        return (
            self._name_edit.text().strip(),
            self._path_edit.text().strip(),
            self._icon_path,
        )

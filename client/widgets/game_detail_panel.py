from typing import Optional

from PySide2.QtCore import Signal, Qt
from PySide2.QtGui import QPixmap, QFont
from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QPushButton, QSizePolicy, QFormLayout
)

from common.models import SyncStatus
from client.widgets.status_indicator import StatusIndicator
from client.i18n import tr


class GameDetailPanel(QWidget):
    upload_requested = Signal(int)
    download_requested = Signal(int)
    refresh_requested = Signal(int)
    icon_change_requested = Signal(int)
    path_change_requested = Signal(int, str)
    delete_requested = Signal(int)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        self._name_label = QLabel(tr("detail.default_title"))
        name_font = QFont()
        name_font.setPointSize(20)
        name_font.setBold(True)
        self._name_label.setFont(name_font)
        layout.addWidget(self._name_label)

        self._icon_label = QLabel()
        self._icon_label.setFixedSize(100, 200)
        self._icon_label.setAlignment(Qt.AlignCenter)
        self._icon_label.setStyleSheet("background-color: #171a21; border: 1px solid #2a3f56;")
        self._icon_label.setText(tr("detail.no_icon"))
        layout.addWidget(self._icon_label)

        self._status_indicator = StatusIndicator(self)
        layout.addWidget(self._status_indicator)

        form = QFormLayout()
        path_row = QHBoxLayout()
        self._local_path_label = QLabel("-")
        self._local_path_label.setWordWrap(True)
        path_row.addWidget(self._local_path_label, 1)
        self._change_path_btn = QPushButton(tr("detail.change_path"))
        self._change_path_btn.clicked.connect(self._on_change_path)
        path_row.addWidget(self._change_path_btn)
        self._local_path_form_label = QLabel(tr("detail.local_path"))
        form.addRow(self._local_path_form_label, path_row)
        self._server_name_label = QLabel("-")
        self._game_name_form_label = QLabel(tr("detail.game_name"))
        form.addRow(self._game_name_form_label, self._server_name_label)
        self._last_save_time_label = QLabel(tr("detail.no_saves"))
        self._last_sync_form_label = QLabel(tr("detail.last_sync"))
        form.addRow(self._last_sync_form_label, self._last_save_time_label)
        layout.addLayout(form)

        saves_group = QGroupBox(tr("detail.save_operations"))
        saves_layout = QVBoxLayout(saves_group)

        saves_btn_layout = QHBoxLayout()
        self._upload_btn = QPushButton(tr("detail.upload"))
        self._upload_btn.clicked.connect(self._on_upload)
        self._download_btn = QPushButton(tr("detail.download"))
        self._download_btn.clicked.connect(self._on_download)
        saves_btn_layout.addWidget(self._upload_btn)
        saves_btn_layout.addWidget(self._download_btn)
        saves_layout.addLayout(saves_btn_layout)

        layout.addWidget(saves_group)

        bottom_btn_layout = QHBoxLayout()
        self._change_icon_btn = QPushButton(tr("detail.change_icon"))
        self._change_icon_btn.clicked.connect(self._on_change_icon)
        self._delete_btn = QPushButton(tr("detail.delete_game"))
        self._delete_btn.setStyleSheet("QPushButton { background-color: #8B0000; } QPushButton:hover { background-color: #B22222; }")
        self._delete_btn.clicked.connect(self._on_delete_game)
        bottom_btn_layout.addWidget(self._change_icon_btn)
        bottom_btn_layout.addWidget(self._delete_btn)
        bottom_btn_layout.addStretch()
        layout.addLayout(bottom_btn_layout)

        self._status_msg = QLabel()
        self._status_msg.setStyleSheet("color: #8f98a0;")
        layout.addWidget(self._status_msg)

        layout.addStretch()
        self._current_game_id: Optional[int] = None

    def show_game(self, game_data: dict) -> None:
        self._current_game_id = game_data.get("id")
        self._name_label.setText(game_data.get("name", tr("detail.unknown_name")))
        self._local_path_label.setText(game_data.get("local_save_path", "-"))
        self._server_name_label.setText(game_data.get("name", "-"))
        lst = game_data.get("last_save_time")
        if lst:
            t = lst[:19].replace("T", " ")
            self._last_save_time_label.setText(t)
        else:
            self._last_save_time_label.setText(tr("detail.no_saves"))
        status_str = game_data.get("sync_status", "not_synced")
        try:
            status = SyncStatus(status_str)
        except ValueError:
            status = SyncStatus.NOT_SYNCED
        self._status_indicator.set_status(status)
        if game_data.get("icon_url"):
            self._icon_label.setText(tr("detail.loading"))
        else:
            self._icon_label.setText(tr("detail.no_icon"))

    def set_icon(self, pixmap: QPixmap) -> None:
        scaled = pixmap.scaled(100, 200, Qt.KeepAspectRatioByExpanding,
                               Qt.SmoothTransformation)
        self._icon_label.setPixmap(scaled)

    def clear(self) -> None:
        self._current_game_id = None
        self._name_label.setText(tr("detail.default_title"))
        self._icon_label.setText(tr("detail.no_icon"))
        self._icon_label.setPixmap(QPixmap())
        self._local_path_label.setText("-")
        self._server_name_label.setText("-")
        self._last_save_time_label.setText(tr("detail.no_saves"))
        self._status_indicator.set_status(SyncStatus.NOT_SYNCED)
        self._status_msg.setText("")

    def set_status_message(self, msg: str) -> None:
        self._status_msg.setText(msg)

    def retranslate(self):
        self._change_path_btn.setText(tr("detail.change_path"))
        self._upload_btn.setText(tr("detail.upload"))
        self._download_btn.setText(tr("detail.download"))
        self._change_icon_btn.setText(tr("detail.change_icon"))
        self._delete_btn.setText(tr("detail.delete_game"))
        self._local_path_form_label.setText(tr("detail.local_path"))
        self._game_name_form_label.setText(tr("detail.game_name"))
        self._last_sync_form_label.setText(tr("detail.last_sync"))
        for child in self.children():
            if isinstance(child, QGroupBox):
                child.setTitle(tr("detail.save_operations"))
                break

    def _on_upload(self):
        if self._current_game_id is not None:
            self.upload_requested.emit(self._current_game_id)

    def _on_download(self):
        if self._current_game_id is not None:
            self.download_requested.emit(self._current_game_id)

    def _on_change_path(self):
        if self._current_game_id is None:
            return
        from PySide2.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(self, tr("detail.change_path_title"))
        if path:
            self._local_path_label.setText(path)
            self.path_change_requested.emit(self._current_game_id, path)

    def _on_delete_game(self):
        if self._current_game_id is None:
            return
        from PySide2.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, tr("dialog.confirm_delete.title"),
            tr("dialog.confirm_delete.message"),
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.delete_requested.emit(self._current_game_id)

    def _on_change_icon(self):
        if self._current_game_id is not None:
            self.icon_change_requested.emit(self._current_game_id)

from PySide2.QtCore import Qt, QSettings
from PySide2.QtGui import QPixmap
from PySide2.QtWidgets import (
    QMainWindow, QSplitter, QMenuBar, QStatusBar,
    QMessageBox, QAction, QActionGroup
)

from client.widgets.game_list_view import GameListView
from client.widgets.game_detail_panel import GameDetailPanel
from client.widgets.game_list_model import GameListModel
from client.models.game_item import GameItem
from client.network.api_client import ApiClient
from client.dialogs.settings_dialog import SettingsDialog
from client.dialogs.add_game_dialog import AddGameDialog
from client.i18n import tr, set_locale, get_locale
from common.models import SyncStatus


class MainWindow(QMainWindow):
    def __init__(self, api: ApiClient):
        super().__init__()
        self._api = api
        self._game_items: list[GameItem] = []
        self._retry_count = 0
        self._max_retries = 10
        from PySide2.QtCore import QTimer
        self._retry_timer = QTimer(self)
        self._retry_timer.setSingleShot(True)
        self._retry_timer.timeout.connect(self._retry_connect)
        self.setWindowTitle(tr("app.window_title"))
        self.resize(1200, 760)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #1b2838; }
            QWidget { color: #c6d4df; font-size: 17px; }
            QMenuBar { background-color: #171a21; padding: 2px; }
            QMenuBar::item:selected { background-color: #2a475e; }
            QMenu { background-color: #171a21; border: 1px solid #2a475e; }
            QMenu::item:selected { background-color: #2a475e; }
            QPushButton {
                background-color: #2a475e; color: #c6d4df;
                border: none; border-radius: 2px; padding: 6px 18px;
            }
            QPushButton:hover { background-color: #3d6c8e; }
            QPushButton:pressed { background-color: #1b2838; }
            QGroupBox {
                border: 1px solid #2a3f56; border-radius: 4px;
                margin-top: 10px; padding-top: 14px;
                color: #66c0f4; font-weight: bold;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; }
            QLineEdit, QSpinBox {
                background-color: #171a21; color: #c6d4df;
                border: 1px solid #2a3f56; border-radius: 2px; padding: 4px;
            }
            QListView { background-color: #1b2838; border: none; outline: none; }
            QListWidget { background-color: #1b2838; border: 1px solid #2a3f56; }
            QSplitter::handle { background-color: #2a3f56; width: 1px; }
            QStatusBar { background-color: #171a21; color: #8f98a0; }
            QLabel { background: transparent; }
            QDialog { background-color: #1b2838; }
        """)
        menubar = self.menuBar()
        file_menu = menubar.addMenu(tr("menu.file"))
        add_action = QAction(tr("menu.file.add_game"), self)
        add_action.triggered.connect(self._on_add_game)
        file_menu.addAction(add_action)
        file_menu.addSeparator()
        exit_action = QAction(tr("menu.file.exit"), self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        self._lang_menu = menubar.addMenu(tr("menu.language"))
        self._lang_group = QActionGroup(self)
        self._lang_group.setExclusive(True)
        self._lang_action_zh = QAction(tr("menu.language.zh_CN"), self)
        self._lang_action_zh.setCheckable(True)
        self._lang_action_zh.setData("zh_CN")
        self._lang_action_en = QAction(tr("menu.language.en_US"), self)
        self._lang_action_en.setCheckable(True)
        self._lang_action_en.setData("en_US")
        self._lang_group.addAction(self._lang_action_zh)
        self._lang_group.addAction(self._lang_action_en)
        self._lang_menu.addAction(self._lang_action_zh)
        self._lang_menu.addAction(self._lang_action_en)
        current_locale = get_locale()
        if current_locale == "en_US":
            self._lang_action_en.setChecked(True)
        else:
            self._lang_action_zh.setChecked(True)
        self._lang_group.triggered.connect(self._on_language_changed)

        settings_menu = menubar.addMenu(tr("menu.settings"))
        config_action = QAction(tr("menu.settings.server_config"), self)
        config_action.triggered.connect(self._open_settings)
        settings_menu.addAction(config_action)

        splitter = QSplitter(Qt.Horizontal, self)
        self._game_list_view = GameListView(self)
        self._detail_panel = GameDetailPanel(self)
        splitter.addWidget(self._game_list_view)
        splitter.addWidget(self._detail_panel)
        splitter.setSizes([310, 790])
        self.setCentralWidget(splitter)

        self._status_bar = QStatusBar()
        self._status_bar.showMessage(tr("status.disconnected"))
        self.setStatusBar(self._status_bar)

    def _connect_signals(self):
        api = self._api
        api.games_loaded.connect(self._on_games_loaded)
        api.game_created.connect(self._on_game_created)
        api.game_loaded.connect(self._on_game_loaded)
        api.game_deleted.connect(self._on_game_deleted)
        api.icon_loaded.connect(self._on_icon_loaded)
        api.save_upload_completed.connect(self._on_save_upload_completed)
        api.save_downloaded.connect(self._on_save_downloaded)
        api.health_checked.connect(self._on_health_checked)
        api.error_occurred.connect(self._on_error)

        self._game_list_view.game_selected.connect(self._on_game_selected)
        self._game_list_view.add_game_requested.connect(self._on_add_game)
        self._game_list_view.refresh_requested.connect(self._refresh_games)

        self._detail_panel.upload_requested.connect(self._on_upload_save)
        self._detail_panel.download_requested.connect(self._on_download_save)
        self._detail_panel.icon_change_requested.connect(self._on_change_icon)
        self._detail_panel.path_change_requested.connect(self._on_change_save_path)
        self._detail_panel.delete_requested.connect(self._api.delete_game)

    def _refresh_games(self):
        self._api.list_games()

    def _on_games_loaded(self, games: list[dict]):
        items = []
        for g in games:
            status_str = g.get("sync_status", "not_synced")
            try:
                status = SyncStatus(status_str)
            except ValueError:
                status = SyncStatus.NOT_SYNCED
            item = GameItem(
                id=g["id"],
                name=g["name"],
                local_save_path=g.get("local_save_path", ""),
                sync_status=status,
                latest_save_hash=g.get("latest_save_hash"),
                last_save_time=g.get("last_save_time"),
            )
            items.append(item)
        self._game_items = items
        self._game_list_view.model().set_games(items)
        for item in items:
            self._api.download_icon(item.id)

    def _on_game_created(self, data: dict):
        self._refresh_games()
        icon_path = getattr(self, '_pending_icon', None)
        if icon_path and data.get("id"):
            self._api.upload_icon(data["id"], icon_path)
            self._pending_icon = None

    def _on_game_loaded(self, data: dict):
        pass

    def _on_game_deleted(self, game_id: int):
        self._refresh_games()
        self._detail_panel.clear()

    def _on_icon_loaded(self, game_id: int, pixmap: QPixmap):
        model = self._game_list_view.model()
        model.update_game_icon(game_id, pixmap)
        if self._game_list_view.selected_game_id() == game_id:
            self._detail_panel.set_icon(pixmap)

    def _on_save_upload_completed(self, game_id: int):
        self._api.list_games()
        self._detail_panel.set_status_message(tr("detail.upload_success"))

    def _on_save_downloaded(self, game_id: int):
        self._detail_panel.set_status_message(tr("detail.download_complete"))
        self._api.list_games()

    def _on_health_checked(self, ok: bool):
        if ok:
            self._retry_count = 0
            self._status_bar.showMessage(tr("status.connected"))
        else:
            self._retry_count += 1
            if self._retry_count <= self._max_retries:
                self._status_bar.showMessage(
                    tr("status.retrying", seconds=3,
                       retry_count=self._retry_count, max_retries=self._max_retries))
                self._retry_timer.start(3000)
            else:
                self._status_bar.showMessage(tr("status.max_retries"))

    def _on_error(self, message: str, status: int):
        self._status_bar.showMessage(tr("status.error_prefix", message=message))
        QMessageBox.warning(self, tr("error.dialog_title"),
                            f"{message}\n(HTTP {status})")

    def _on_add_game(self):
        dlg = AddGameDialog(self)
        if dlg.exec_():
            name, local_path, icon_path = dlg.get_game_data()
            self._pending_icon = icon_path
            self._api.create_game(name, local_path)

    def _on_game_selected(self, game_id: int):
        model = self._game_list_view.model()
        item = model.get_game_by_id(game_id)
        if item:
            self._detail_panel.show_game({
                "id": item.id,
                "name": item.name,
                "local_save_path": item.local_save_path,
                "sync_status": item.sync_status.value,
                "latest_save_hash": item.latest_save_hash,
                "last_save_time": item.last_save_time,
            })
            if item.icon_pixmap:
                self._detail_panel.set_icon(item.icon_pixmap)

    def _on_upload_save(self, game_id: int):
        import tempfile
        import shutil
        import os
        model = self._game_list_view.model()
        item = model.get_game_by_id(game_id)
        if not item or not item.local_save_path:
            QMessageBox.warning(self, tr("error.dialog_title"),
                                tr("error.no_save_path"))
            return
        src = item.local_save_path
        if not os.path.isdir(src):
            QMessageBox.warning(self, tr("error.dialog_title"),
                                tr("error.path_not_exist", path=src))
            return
        tmp_dir = tempfile.mkdtemp()
        zip_base = os.path.join(tmp_dir, "save")
        try:
            zip_path = shutil.make_archive(zip_base, "zip", src)
            zip_size = os.path.getsize(zip_path)
            max_size = 100 * 1024 * 1024
            if zip_size > max_size:
                import shutil as _shutil
                _shutil.rmtree(tmp_dir)
                QMessageBox.warning(self, tr("error.upload_failed"),
                                    tr("error.file_too_large"))
                return
            self._api.upload_game_save(game_id, zip_path)
            self._detail_panel.set_status_message(tr("detail.uploading"))
        except Exception as e:
            QMessageBox.warning(self, tr("error.dialog_title"),
                                tr("error.pack_failed", error=e))

    def _on_download_save(self, game_id: int):
        model = self._game_list_view.model()
        item = model.get_game_by_id(game_id)
        if not item or not item.local_save_path:
            QMessageBox.warning(self, tr("error.dialog_title"),
                                tr("error.no_save_path"))
            return
        import os, shutil, time
        src = item.local_save_path
        if os.path.isdir(src) and os.listdir(src):
            game_name = item.name.replace("/", "_").replace("\\", "_")
            today = time.strftime('%Y%m%d')
            today_prefix = f"{game_name}_backup_{today}"
            parent_dir = os.path.dirname(src)
            existing = [f for f in os.listdir(parent_dir) if f.startswith(today_prefix)]
            if existing:
                self._detail_panel.set_status_message(tr("detail.backup_skip"))
            else:
                backup_name = f"{today_prefix}_{time.strftime('%H%M%S')}"
                backup_path = os.path.join(parent_dir, backup_name)
                try:
                    shutil.make_archive(backup_path, "zip", src)
                    self._detail_panel.set_status_message(
                        tr("detail.backup_created", backup_name=backup_name))
                except Exception as e:
                    QMessageBox.warning(self, tr("error.dialog_title"),
                                        tr("error.backup_failed", error=e))
                    return
        else:
            self._detail_panel.set_status_message(tr("detail.downloading"))
        self._api.download_game_save(game_id, item.local_save_path)

    def _on_change_save_path(self, game_id: int, new_path: str):
        self._api.update_game(game_id, local_save_path=new_path)
        model = self._game_list_view.model()
        item = model.get_game_by_id(game_id)
        if item:
            item.local_save_path = new_path
        self._detail_panel.set_status_message(tr("detail.path_updated"))

    def _on_change_icon(self, game_id: int):
        from PySide2.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self, tr("dialog.change_icon.title"), "",
            tr("dialog.change_icon.filter")
        )
        if path:
            self._api.upload_icon(game_id, path)

    def _open_settings(self):
        host, port = SettingsDialog.load_server_address()
        dlg = SettingsDialog(host, port, self)
        dlg.server_changed.connect(self._on_server_changed)
        dlg.exec_()

    def _on_language_changed(self, action):
        locale = action.data()
        if locale == get_locale():
            return
        s = QSettings("GameSaveCloud", "Client")
        s.setValue("i18n/locale", locale)
        set_locale(locale)
        self._retranslate_ui()

    def _retranslate_ui(self):
        self.setWindowTitle(tr("app.window_title"))
        actions = self.menuBar().actions()
        file_menu = actions[0].menu()
        file_menu.setTitle(tr("menu.file"))
        file_menu.actions()[0].setText(tr("menu.file.add_game"))
        file_menu.actions()[2].setText(tr("menu.file.exit"))
        self._lang_menu.setTitle(tr("menu.language"))
        self._lang_action_zh.setText(tr("menu.language.zh_CN"))
        self._lang_action_en.setText(tr("menu.language.en_US"))
        settings_menu = actions[2].menu()
        settings_menu.setTitle(tr("menu.settings"))
        settings_menu.actions()[0].setText(tr("menu.settings.server_config"))
        self._game_list_view.retranslate()
        self._game_list_view.repaint()
        self._detail_panel.retranslate()
        gid = self._game_list_view.selected_game_id()
        if gid is not None:
            self._on_game_selected(gid)

    def _on_server_changed(self, host: str, port: int):
        self._retry_count = 0
        self._api.set_server(host, port)
        self._status_bar.showMessage(
            tr("status.server_config_done", host=host, port=port))
        self._api.health_check()

    def connect_to_server(self):
        self._retry_count = 0
        host, port = SettingsDialog.load_server_address()
        self._api.set_server(host, port)
        self._status_bar.showMessage(
            tr("status.connecting", host=host, port=port))
        self._api.health_check()
        self._api.list_games()

    def _retry_connect(self):
        self._api.health_check()

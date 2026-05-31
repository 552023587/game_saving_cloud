import os
import sys

from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication

from client.network.api_client import ApiClient
from client.widgets.main_window import MainWindow


def _icon_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, "icon.png")
    return os.path.join(os.path.dirname(__file__), "..", "..", "icon.png")


class GameSaveApplication:
    def __init__(self, argv: list[str]):
        self._app = QApplication(argv)
        self._app.setApplicationName("GameSaveCloud")
        self._app.setOrganizationName("GameSaveCloud")

        from client.i18n import set_locale
        from PySide2.QtCore import QSettings
        s = QSettings("GameSaveCloud", "Client")
        locale = s.value("i18n/locale", "zh_CN")
        set_locale(locale)

        icon = _icon_path()
        if os.path.exists(icon):
            self._app.setWindowIcon(QIcon(icon))
        self._api = ApiClient()
        self._window = MainWindow(self._api)

    def run(self) -> int:
        self._window.show()
        self._window.connect_to_server()
        return self._app.exec_()

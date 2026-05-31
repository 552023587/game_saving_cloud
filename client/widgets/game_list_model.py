from typing import Any, Optional

from PySide2.QtCore import Qt, QAbstractListModel, QModelIndex
from PySide2.QtGui import QPixmap

from client.models.game_item import GameItem
from common.models import SyncStatus


class GameListModel(QAbstractListModel):
    IconRole = Qt.UserRole + 1
    StatusRole = Qt.UserRole + 2
    GameIdRole = Qt.UserRole + 3
    GameItemRole = Qt.UserRole + 4

    def __init__(self, parent=None):
        super().__init__(parent)
        self._games: list[GameItem] = []

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._games)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid() or index.row() >= len(self._games):
            return None
        game = self._games[index.row()]
        if role == Qt.DisplayRole:
            return game.name
        elif role == Qt.DecorationRole:
            return game.icon_pixmap
        elif role == self.IconRole:
            return game.icon_pixmap
        elif role == self.StatusRole:
            return game.sync_status
        elif role == self.GameIdRole:
            return game.id
        elif role == self.GameItemRole:
            return game
        return None

    def set_games(self, games: list[GameItem]) -> None:
        self.beginResetModel()
        self._games = games
        self.endResetModel()

    def update_game_status(self, game_id: int, status: SyncStatus) -> None:
        for i, g in enumerate(self._games):
            if g.id == game_id:
                g.sync_status = status
                idx = self.index(i)
                self.dataChanged.emit(idx, idx, [self.StatusRole])
                return

    def update_game_icon(self, game_id: int, pixmap: QPixmap) -> None:
        for i, g in enumerate(self._games):
            if g.id == game_id:
                g.icon_pixmap = pixmap
                g.icon_loading = False
                idx = self.index(i)
                self.dataChanged.emit(idx, idx, [Qt.DecorationRole, self.IconRole])
                return

    def get_game(self, index: int) -> Optional[GameItem]:
        if 0 <= index < len(self._games):
            return self._games[index]
        return None

    def get_game_by_id(self, game_id: int) -> Optional[GameItem]:
        for g in self._games:
            if g.id == game_id:
                return g
        return None

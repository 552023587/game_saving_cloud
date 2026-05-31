from typing import Optional

from PySide2.QtCore import Signal, QSize, Qt
from PySide2.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListView, QPushButton
)

from client.widgets.game_list_model import GameListModel
from client.widgets.game_list_delegate import GameListDelegate
from client.i18n import tr


class GameListView(QWidget):
    game_selected = Signal(int)
    add_game_requested = Signal()
    refresh_requested = Signal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._model = GameListModel(self)
        self._delegate = GameListDelegate(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        self._list_view = QListView()
        self._list_view.setModel(self._model)
        self._list_view.setItemDelegate(self._delegate)
        self._list_view.setSelectionMode(QListView.SingleSelection)
        self._list_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._list_view.setViewMode(QListView.ListMode)
        self._list_view.setWrapping(False)
        self._list_view.setUniformItemSizes(True)

        self._list_view.selectionModel().selectionChanged.connect(self._on_selection)
        self._list_view.doubleClicked.connect(self._on_double_click)

        btn_layout = QHBoxLayout()
        self._add_btn = QPushButton(tr("view.add_game"))
        self._add_btn.clicked.connect(self.add_game_requested.emit)
        self._refresh_btn = QPushButton(tr("view.refresh"))
        self._refresh_btn.clicked.connect(self.refresh_requested.emit)
        btn_layout.addWidget(self._add_btn)
        btn_layout.addWidget(self._refresh_btn)

        layout.addWidget(self._list_view)
        layout.addLayout(btn_layout)

    def set_model(self, model: GameListModel) -> None:
        self._model = model
        self._list_view.setModel(model)

    def model(self) -> GameListModel:
        return self._model

    def selected_game_id(self) -> Optional[int]:
        idx = self._list_view.currentIndex()
        if idx.isValid():
            return idx.data(GameListModel.GameIdRole)
        return None

    def _on_selection(self):
        gid = self.selected_game_id()
        if gid is not None:
            self.game_selected.emit(gid)

    def _on_double_click(self, index):
        gid = index.data(GameListModel.GameIdRole)
        if gid is not None:
            self.game_selected.emit(gid)

    def retranslate(self):
        self._add_btn.setText(tr("view.add_game"))
        self._refresh_btn.setText(tr("view.refresh"))

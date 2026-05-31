from PySide2.QtCore import Qt, QSize, QRectF
from PySide2.QtGui import (
    QPainter, QColor, QFont, QPen, QBrush, QFontMetrics
)
from PySide2.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QStyle

from common.models import SyncStatus
from client.i18n import tr, sync_status_label


class GameListDelegate(QStyledItemDelegate):
    ICON_W, ICON_H = 80, 120
    ITEM_W, ITEM_H = 280, 134

    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        r = option.rect
        if option.state & QStyle.State_Selected:
            painter.fillRect(r, QColor("#2a475e"))
        elif option.state & QStyle.State_MouseOver:
            painter.fillRect(r, QColor("#213447"))

        # Icon area
        ix, iy = r.left() + 8, r.top() + 7
        pixmap = index.data(self._icon_role())
        if pixmap:
            scaled = pixmap.scaled(self.ICON_W, self.ICON_H, Qt.KeepAspectRatioByExpanding,
                                   Qt.SmoothTransformation)
            sx = ix + (self.ICON_W - scaled.width()) // 2
            sy = iy + (self.ICON_H - scaled.height()) // 2
            painter.drawPixmap(sx, sy, scaled)
        else:
            painter.setPen(QPen(QColor("#2a3f56"), 1))
            painter.setBrush(QBrush(QColor("#171a21")))
            painter.drawRect(QRectF(ix, iy, self.ICON_W, self.ICON_H))
            painter.setPen(QColor("#555"))
            f = QFont()
            f.setPointSize(9)
            painter.setFont(f)
            painter.drawText(QRectF(ix, iy, self.ICON_W, self.ICON_H),
                             Qt.AlignCenter, tr("detail.no_icon"))

        # Text area
        tx = ix + self.ICON_W + 10
        tw = r.right() - tx - 8
        name = index.data(Qt.DisplayRole) or tr("detail.unknown_name")
        status = index.data(self._status_role()) or SyncStatus.NOT_SYNCED

        # Game name
        name_font = QFont()
        name_font.setPointSize(12)
        name_font.setBold(True)
        painter.setFont(name_font)
        painter.setPen(QColor("#c6d4df"))
        fm = QFontMetrics(name_font)
        name_elided = fm.elidedText(name, Qt.ElideRight, tw)
        painter.drawText(QRectF(tx, iy, tw, fm.height() + 2),
                         Qt.AlignLeft | Qt.AlignVCenter, name_elided)

        # Status dot + label
        sy = iy + fm.height() + 12
        colors = {
            SyncStatus.SYNCED: QColor("#4CAF50"),
            SyncStatus.SYNCING: QColor("#2196F3"),
            SyncStatus.NOT_SYNCED: QColor("#9E9E9E"),
            SyncStatus.ERROR: QColor("#F44336"),
        }
        color = colors.get(status, QColor("#9E9E9E"))
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(tx, sy + 3, 8, 8))
        painter.setPen(QColor("#8f98a0"))
        sf = QFont()
        sf.setPointSize(9)
        painter.setFont(sf)
        painter.drawText(QRectF(tx + 14, sy, tw - 14, 18),
                         Qt.AlignLeft | Qt.AlignVCenter,
                         sync_status_label(status.value))

        painter.restore()

    def sizeHint(self, option: QStyleOptionViewItem, index) -> QSize:
        return QSize(self.ITEM_W, self.ITEM_H)

    @staticmethod
    def _icon_role():
        from client.widgets.game_list_model import GameListModel
        return GameListModel.IconRole

    @staticmethod
    def _status_role():
        from client.widgets.game_list_model import GameListModel
        return GameListModel.StatusRole

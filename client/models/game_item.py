from dataclasses import dataclass, field
from typing import Optional

from PySide2.QtGui import QPixmap

from common.models import SyncStatus


@dataclass
class GameItem:
    id: int
    name: str
    local_save_path: str = ""
    sync_status: SyncStatus = SyncStatus.NOT_SYNCED
    icon_pixmap: Optional[QPixmap] = None
    latest_save_hash: Optional[str] = None
    last_save_time: Optional[str] = None
    icon_loading: bool = False

from enum import Enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class SyncStatus(str, Enum):
    SYNCED = "synced"
    SYNCING = "syncing"
    NOT_SYNCED = "not_synced"
    ERROR = "error"


class GameCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    local_save_path: str = Field(default="", max_length=1024)


class GameUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    local_save_path: Optional[str] = Field(None, max_length=1024)


class GameResponse(BaseModel):
    id: int
    name: str
    local_save_path: str
    icon_url: Optional[str] = None
    sync_status: SyncStatus = SyncStatus.NOT_SYNCED
    latest_save_hash: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class GameListResponse(BaseModel):
    games: list[GameResponse]
    total: int


class SaveCreate(BaseModel):
    version: str = Field(default="1.0", max_length=50)


class SaveResponse(BaseModel):
    id: int
    game_id: int
    version: str
    file_name: str
    file_hash: str
    file_size: int
    sync_status: SyncStatus
    created_at: datetime
    updated_at: datetime


class SaveListResponse(BaseModel):
    saves: list[SaveResponse]
    total: int


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

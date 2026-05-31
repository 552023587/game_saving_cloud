from typing import Optional

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from server.models import Game, GameSave
from server.services.storage import StorageService


class SaveService:
    def __init__(self, db: AsyncSession, storage: StorageService):
        self._db = db
        self._storage = storage

    async def create_save(self, game_id: int, file_name: str, content: bytes, version: str = "1.0") -> Optional[GameSave]:
        game = await self._db.get(Game, game_id)
        if game is None:
            return None
        file_hash = StorageService.sha256_hash(content)
        file_size = len(content)
        gsave = GameSave(
            game_id=game_id, version=version, file_name=file_name,
            file_path="", file_hash=file_hash, file_size=file_size,
            sync_status="synced"
        )
        self._db.add(gsave)
        await self._db.flush()
        path = await self._storage.save_save_file(game_id, gsave.id, file_name, content)
        gsave.file_path = path
        await self._db.commit()
        await self._db.refresh(gsave)
        return gsave

    async def get_save(self, save_id: int) -> Optional[GameSave]:
        return await self._db.get(GameSave, save_id)

    async def list_saves(self, game_id: int, offset: int = 0, limit: int = 20) -> tuple[list[GameSave], int]:
        stmt = (
            select(GameSave)
            .where(GameSave.game_id == game_id)
            .order_by(GameSave.created_at.desc())
        )
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self._db.execute(count_stmt)).scalar() or 0
        stmt = stmt.offset(offset).limit(limit)
        result = await self._db.execute(stmt)
        return list(result.scalars().all()), total

    async def delete_save(self, save_id: int) -> bool:
        gsave = await self._db.get(GameSave, save_id)
        if gsave is None:
            return False
        await self._storage.delete_save_file(gsave.game_id, save_id)
        await self._db.execute(delete(GameSave).where(GameSave.id == save_id))
        await self._db.commit()
        return True

    async def get_latest_save(self, game_id: int) -> Optional[GameSave]:
        stmt = (
            select(GameSave)
            .where(GameSave.game_id == game_id)
            .order_by(GameSave.created_at.desc())
            .limit(1)
        )
        result = await self._db.execute(stmt)
        return result.scalar_one_or_none()

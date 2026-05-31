from typing import Optional

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from server.models import Game, GameSave
from server.services.storage import StorageService


class GameService:
    def __init__(self, db: AsyncSession, storage: StorageService):
        self._db = db
        self._storage = storage

    async def create_game(self, name: str, local_save_path: str = "") -> Game:
        game = Game(name=name, local_save_path=local_save_path)
        self._db.add(game)
        await self._db.commit()
        await self._db.refresh(game)
        return game

    async def get_game(self, game_id: int) -> Optional[Game]:
        return await self._db.get(Game, game_id)

    async def list_games(self, q: str = "", offset: int = 0, limit: int = 50) -> tuple[list[Game], int]:
        stmt = select(Game)
        if q:
            stmt = stmt.where(Game.name.ilike(f"%{q}%"))
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = (await self._db.execute(count_stmt)).scalar() or 0
        stmt = stmt.offset(offset).limit(limit).order_by(Game.name)
        result = await self._db.execute(stmt)
        return list(result.scalars().all()), total

    async def update_game(self, game_id: int, name: Optional[str] = None, local_save_path: Optional[str] = None) -> Optional[Game]:
        game = await self._db.get(Game, game_id)
        if game is None:
            return None
        if name is not None:
            game.name = name
        if local_save_path is not None:
            game.local_save_path = local_save_path
        await self._db.commit()
        await self._db.refresh(game)
        return game

    async def delete_game(self, game_id: int) -> bool:
        game = await self._db.get(Game, game_id)
        if game is None:
            return False
        await self._storage.delete_icon(game_id)
        await self._db.execute(delete(Game).where(Game.id == game_id))
        await self._db.commit()
        return True

    async def set_icon(self, game_id: int, content: bytes) -> Optional[Game]:
        game = await self._db.get(Game, game_id)
        if game is None:
            return None
        path = await self._storage.save_icon(game_id, content)
        game.icon_path = path
        await self._db.commit()
        await self._db.refresh(game)
        return game

    async def get_latest_save_hash(self, game_id: int) -> Optional[str]:
        stmt = (
            select(GameSave.file_hash)
            .where(GameSave.game_id == game_id)
            .order_by(GameSave.created_at.desc())
            .limit(1)
        )
        result = await self._db.execute(stmt)
        row = result.scalar_one_or_none()
        return row

    async def get_latest_save_time(self, game_id: int) -> Optional[str]:
        stmt = (
            select(GameSave.created_at)
            .where(GameSave.game_id == game_id)
            .order_by(GameSave.created_at.desc())
            .limit(1)
        )
        result = await self._db.execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        local = row.replace(tzinfo=None)
        from datetime import timezone, timedelta
        local = local + timedelta(hours=8)
        return local.strftime('%Y-%m-%d %H:%M:%S')

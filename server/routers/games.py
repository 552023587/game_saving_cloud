from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from server.database import get_db
from server.services.game_service import GameService
from server.services.storage import StorageService

router = APIRouter(prefix="/api/games", tags=["games"])


def make_game_service(db: AsyncSession = Depends(get_db)) -> GameService:
    return GameService(db, StorageService())


@router.post("", status_code=201)
async def create_game(
    data: dict,
    db: AsyncSession = Depends(get_db),
):
    svc = GameService(db, StorageService())
    game = await svc.create_game(
        name=data.get("name", ""),
        local_save_path=data.get("local_save_path", ""),
    )
    return _game_to_response(game, None)


@router.get("")
async def list_games(
    q: str = "",
    offset: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    svc = GameService(db, StorageService())
    games, total = await svc.list_games(q=q, offset=offset, limit=limit)
    items = []
    for g in games:
        h = await svc.get_latest_save_hash(g.id)
        t = await svc.get_latest_save_time(g.id)
        items.append(_game_to_response(g, h, t))
    return {"games": items, "total": total}


@router.get("/{game_id}")
async def get_game(game_id: int, db: AsyncSession = Depends(get_db)):
    svc = GameService(db, StorageService())
    game = await svc.get_game(game_id)
    if game is None:
        raise HTTPException(404, "Game not found")
    h = await svc.get_latest_save_hash(game.id)
    t = await svc.get_latest_save_time(game.id)
    return _game_to_response(game, h, t)


@router.put("/{game_id}")
async def update_game(
    game_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db),
):
    svc = GameService(db, StorageService())
    game = await svc.update_game(
        game_id,
        name=data.get("name"),
        local_save_path=data.get("local_save_path"),
    )
    if game is None:
        raise HTTPException(404, "Game not found")
    h = await svc.get_latest_save_hash(game.id)
    t = await svc.get_latest_save_time(game.id)
    return _game_to_response(game, h, t)


@router.delete("/{game_id}", status_code=204)
async def delete_game(game_id: int, db: AsyncSession = Depends(get_db)):
    svc = GameService(db, StorageService())
    deleted = await svc.delete_game(game_id)
    if not deleted:
        raise HTTPException(404, "Game not found")


@router.put("/{game_id}/icon")
async def upload_icon(
    game_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    svc = GameService(db, StorageService())
    content = await file.read()
    game = await svc.set_icon(game_id, content)
    if game is None:
        raise HTTPException(404, "Game not found")
    h = await svc.get_latest_save_hash(game.id)
    t = await svc.get_latest_save_time(game.id)
    return _game_to_response(game, h, t)


@router.get("/{game_id}/icon")
async def get_icon(game_id: int, db: AsyncSession = Depends(get_db)):
    from fastapi.responses import FileResponse
    svc = GameService(db, StorageService())
    game = await svc.get_game(game_id)
    if game is None:
        raise HTTPException(404, "Game not found")
    storage = StorageService()
    path = await storage.get_icon_path(game_id)
    if path is None:
        raise HTTPException(404, "No icon for this game")
    return FileResponse(path, media_type="image/png")


@router.put("/{game_id}/save")
async def upload_game_save(
    game_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    svc = GameService(db, StorageService())
    game = await svc.get_game(game_id)
    if game is None:
        raise HTTPException(404, "Game not found")
    storage = StorageService()
    content = await file.read()
    zip_hash = StorageService.sha256_hash(content)
    storage.save_game_save(game_id, content)
    # Delete old individual saves and create one representing the zip
    from server.models import GameSave
    from sqlalchemy import delete as sa_delete
    await db.execute(sa_delete(GameSave).where(GameSave.game_id == game_id))
    gsave = GameSave(
        game_id=game_id, version="zip", file_name="save.zip",
        file_path="", file_hash=zip_hash, file_size=len(content),
        sync_status="synced"
    )
    db.add(gsave)
    await db.commit()
    await db.refresh(gsave)
    return {
        "game_id": game_id,
        "file_name": "save.zip",
        "file_hash": zip_hash,
        "file_size": len(content),
        "sync_status": "synced",
    }


@router.get("/{game_id}/save/download")
async def download_game_save(game_id: int, db: AsyncSession = Depends(get_db)):
    from fastapi.responses import FileResponse
    svc = GameService(db, StorageService())
    game = await svc.get_game(game_id)
    if game is None:
        raise HTTPException(404, "Game not found")
    storage = StorageService()
    path = storage.get_game_save_path(game_id)
    if path is None:
        raise HTTPException(404, "No save file for this game")
    return FileResponse(path, media_type="application/zip", filename="save.zip")


def _game_to_response(game, latest_save_hash: str | None, last_save_time: str | None = None) -> dict:
    from common.models import SyncStatus
    status = SyncStatus.SYNCED if latest_save_hash else SyncStatus.NOT_SYNCED
    return {
        "id": game.id,
        "name": game.name,
        "local_save_path": game.local_save_path,
        "icon_url": f"/api/games/{game.id}/icon" if game.icon_path else None,
        "sync_status": status.value,
        "latest_save_hash": latest_save_hash,
        "last_save_time": last_save_time,
        "created_at": game.created_at.isoformat(),
        "updated_at": game.updated_at.isoformat(),
    }

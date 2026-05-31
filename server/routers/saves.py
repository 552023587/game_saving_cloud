from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from server.database import get_db
from server.services.save_service import SaveService
from server.services.storage import StorageService

router = APIRouter(tags=["saves"])


def make_save_service(db: AsyncSession = Depends(get_db)) -> SaveService:
    return SaveService(db, StorageService())


@router.post("/api/games/{game_id}/saves", status_code=201)
async def create_save(
    game_id: int,
    file: UploadFile = File(...),
    version: str = Form("1.0"),
    db: AsyncSession = Depends(get_db),
):
    svc = SaveService(db, StorageService())
    content = await file.read()
    gsave = await svc.create_save(game_id, file.filename or "save.dat", content, version)
    if gsave is None:
        raise HTTPException(404, "Game not found")
    return _save_to_response(gsave)


@router.get("/api/games/{game_id}/saves")
async def list_saves(
    game_id: int,
    offset: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    svc = SaveService(db, StorageService())
    saves, total = await svc.list_saves(game_id, offset=offset, limit=limit)
    return {"saves": [_save_to_response(s) for s in saves], "total": total}


@router.get("/api/saves/{save_id}")
async def get_save(save_id: int, db: AsyncSession = Depends(get_db)):
    svc = SaveService(db, StorageService())
    gsave = await svc.get_save(save_id)
    if gsave is None:
        raise HTTPException(404, "Save not found")
    return _save_to_response(gsave)


@router.get("/api/saves/{save_id}/download")
async def download_save(save_id: int, db: AsyncSession = Depends(get_db)):
    svc = SaveService(db, StorageService())
    gsave = await svc.get_save(save_id)
    if gsave is None:
        raise HTTPException(404, "Save not found")
    storage = StorageService()
    path = await storage.get_save_file_path(gsave.game_id, save_id)
    if path is None:
        raise HTTPException(404, "Save file not found on disk")
    return FileResponse(path, filename=gsave.file_name, media_type="application/octet-stream")


@router.delete("/api/saves/{save_id}", status_code=204)
async def delete_save(save_id: int, db: AsyncSession = Depends(get_db)):
    svc = SaveService(db, StorageService())
    deleted = await svc.delete_save(save_id)
    if not deleted:
        raise HTTPException(404, "Save not found")


def _save_to_response(gsave) -> dict:
    return {
        "id": gsave.id,
        "game_id": gsave.game_id,
        "version": gsave.version,
        "file_name": gsave.file_name,
        "file_hash": gsave.file_hash,
        "file_size": gsave.file_size,
        "sync_status": gsave.sync_status,
        "created_at": gsave.created_at.isoformat(),
        "updated_at": gsave.updated_at.isoformat(),
    }

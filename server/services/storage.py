import hashlib
import shutil
from pathlib import Path
from typing import Optional

from PIL import Image
import io

from server.config import settings


class StorageService:
    def __init__(self) -> None:
        self._root = settings.storage_root_path.resolve()
        self._icons_dir = self._root / "icons"
        self._saves_dir = self._root / "saves"
        self._icons_dir.mkdir(parents=True, exist_ok=True)
        self._saves_dir.mkdir(parents=True, exist_ok=True)

    async def save_icon(self, game_id: int, content: bytes) -> str:
        img = Image.open(io.BytesIO(content))
        img = img.convert("RGBA")
        img.thumbnail((200, 200), Image.LANCZOS)
        canvas = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
        x = (200 - img.width) // 2
        y = (200 - img.height) // 2
        canvas.paste(img, (x, y))
        path = self._icons_dir / f"{game_id}.png"
        canvas.save(path, "PNG")
        return str(path)

    async def get_icon_path(self, game_id: int) -> Optional[Path]:
        path = self._icons_dir / f"{game_id}.png"
        return path if path.exists() else None

    async def delete_icon(self, game_id: int) -> None:
        path = self._icons_dir / f"{game_id}.png"
        if path.exists():
            path.unlink()

    async def save_save_file(self, game_id: int, save_id: int, file_name: str, content: bytes) -> str:
        game_dir = self._saves_dir / str(game_id)
        game_dir.mkdir(parents=True, exist_ok=True)
        path = game_dir / f"{save_id}_{file_name}"
        path.write_bytes(content)
        return str(path)

    async def get_save_file_path(self, game_id: int, save_id: int) -> Optional[Path]:
        game_dir = self._saves_dir / str(game_id)
        if not game_dir.exists():
            return None
        for f in game_dir.iterdir():
            if f.name.startswith(f"{save_id}_"):
                return f
        return None

    async def delete_save_file(self, game_id: int, save_id: int) -> None:
        game_dir = self._saves_dir / str(game_id)
        if not game_dir.exists():
            return
        for f in game_dir.iterdir():
            if f.name.startswith(f"{save_id}_"):
                f.unlink()
                break
        if game_dir.exists() and not any(game_dir.iterdir()):
            shutil.rmtree(game_dir)

    def save_game_save(self, game_id: int, content: bytes) -> str:
        game_dir = self._saves_dir / str(game_id)
        game_dir.mkdir(parents=True, exist_ok=True)
        path = game_dir / "save.zip"
        path.write_bytes(content)
        return str(path)

    def get_game_save_path(self, game_id: int) -> Optional[Path]:
        path = self._saves_dir / str(game_id) / "save.zip"
        return path if path.exists() else None

    @staticmethod
    def sha256_hash(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

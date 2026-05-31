from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 3000
    database_url: str = "sqlite+aiosqlite:///./server/data/game_saves.db"
    storage_root: str = "./server/storage"
    max_upload_size_mb: int = 500
    log_level: str = "INFO"

    model_config = {"env_prefix": "GSC_", "extra": "ignore"}

    @property
    def storage_root_path(self) -> Path:
        return Path(self.storage_root)


settings = Settings()

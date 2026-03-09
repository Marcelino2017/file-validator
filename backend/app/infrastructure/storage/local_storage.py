from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import uuid

from app.config import settings
from app.domain.interfaces import FileStorage


class LocalDiskStorage(FileStorage):
    def __init__(self) -> None:
        self._base_dir = Path(settings.upload_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, filename: str, content: bytes) -> tuple[str, str]:
        extension = Path(filename).suffix.lower()
        target_name = f"{uuid.uuid4().hex}{extension}"
        target_path = self._base_dir / target_name
        target_path.write_bytes(content)

        file_hash = sha256(content).hexdigest()
        return str(target_path), file_hash

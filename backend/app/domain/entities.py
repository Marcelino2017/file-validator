from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Enterprise:
    name: str
    nit: str
    id: int | None = None
    created_at: datetime | None = None


@dataclass(slots=True)
class User:
    first_name: str
    last_name: str
    cedula: str
    hashed_password: str
    enterprise_id: int
    id: int | None = None
    created_at: datetime | None = None


@dataclass(slots=True)
class Profile:
    user_id: int
    enterprise_name: str
    nit: str


@dataclass(slots=True)
class PDFDocument:
    filename: str
    mime_type: str
    storage_path: str
    sha256: str
    user_id: int
    enterprise_id: int
    id: int | None = None
    created_at: datetime | None = None

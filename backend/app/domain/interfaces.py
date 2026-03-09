from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities import Enterprise, PDFDocument, User


class EnterpriseRepository(ABC):
    @abstractmethod
    def get_by_nit(self, nit: str) -> Enterprise | None:
        raise NotImplementedError

    @abstractmethod
    def create(self, enterprise: Enterprise) -> Enterprise:
        raise NotImplementedError


class UserRepository(ABC):
    @abstractmethod
    def get_by_cedula(self, cedula: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def create(self, user: User) -> User:
        raise NotImplementedError


class PDFRepository(ABC):
    @abstractmethod
    def create(self, document: PDFDocument) -> PDFDocument:
        raise NotImplementedError


class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, plain_password: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        raise NotImplementedError


class TokenProvider(ABC):
    @abstractmethod
    def create_access_token(self, subject: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_subject(self, token: str) -> str:
        raise NotImplementedError


class FileStorage(ABC):
    @abstractmethod
    def save(self, filename: str, content: bytes) -> tuple[str, str]:
        """Returns (storage_path, sha256)."""
        raise NotImplementedError


class FileValidator(ABC):
    @abstractmethod
    def validate(self, filename: str, mime_type: str, content: bytes) -> None:
        raise NotImplementedError


class FileValidatorFactory(ABC):
    @abstractmethod
    def for_file(self, filename: str, mime_type: str) -> FileValidator:
        raise NotImplementedError

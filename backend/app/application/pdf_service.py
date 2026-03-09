from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
import re

from pypdf import PdfReader

from app.application.exceptions import NotFoundError, ValidationError
from app.domain.entities import PDFDocument
from app.domain.interfaces import (
    FileStorage,
    FileValidatorFactory,
    PDFRepository,
    UserRepository,
)


@dataclass(slots=True)
class ValidateAndUploadPDFInput:
    filename: str
    mime_type: str
    content: bytes
    user_id: int


class ValidateAndUploadPDF:
    def __init__(
        self,
        user_repo: UserRepository,
        pdf_repo: PDFRepository,
        file_storage: FileStorage,
        validator_factory: FileValidatorFactory,
    ) -> None:
        self._user_repo = user_repo
        self._pdf_repo = pdf_repo
        self._file_storage = file_storage
        self._validator_factory = validator_factory

    def execute(self, payload: ValidateAndUploadPDFInput) -> PDFDocument:
        user = self._user_repo.get_by_id(payload.user_id)
        if not user:
            raise NotFoundError("Usuario no encontrado")

        validator = self._validator_factory.for_file(
            filename=payload.filename,
            mime_type=payload.mime_type,
        )
        validator.validate(payload.filename, payload.mime_type, payload.content)

        if not self._pdf_contains_user_cedula(payload.content, user.cedula):
            raise ValidationError(
                "El PDF no contiene la cédula del usuario autenticado"
            )

        storage_path, sha256_hash = self._file_storage.save(
            filename=payload.filename,
            content=payload.content,
        )
        document = PDFDocument(
            filename=payload.filename,
            mime_type=payload.mime_type,
            storage_path=storage_path,
            sha256=sha256_hash,
            user_id=payload.user_id,
            enterprise_id=user.enterprise_id,
        )
        return self._pdf_repo.create(document)

    def _pdf_contains_user_cedula(self, content: bytes, cedula: str) -> bool:
        try:
            reader = PdfReader(BytesIO(content))
        except Exception as exc:
            raise ValidationError("No fue posible leer el contenido del PDF") from exc

        extracted_text = "\n".join((page.extract_text() or "") for page in reader.pages)
        normalized_text_digits = re.sub(r"\D", "", extracted_text)
        normalized_cedula = re.sub(r"\D", "", cedula)
        return bool(normalized_cedula) and normalized_cedula in normalized_text_digits

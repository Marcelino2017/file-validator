from __future__ import annotations

from pathlib import Path

from app.application.exceptions import ValidationError
from app.domain.interfaces import FileValidator, FileValidatorFactory


class PDFFileValidator(FileValidator):
    ALLOWED_MIME_TYPES = {"application/pdf"}
    SIGNATURE = b"%PDF"

    def validate(self, filename: str, mime_type: str, content: bytes) -> None:
        extension = Path(filename).suffix.lower()
        if extension != ".pdf":
            raise ValidationError("Solo se permiten archivos PDF")
        if mime_type not in self.ALLOWED_MIME_TYPES:
            raise ValidationError("Tipo MIME inválido para PDF")
        if not content.startswith(self.SIGNATURE):
            raise ValidationError("El archivo no tiene encabezado PDF válido")


class UnsupportedFileValidator(FileValidator):
    def validate(self, filename: str, mime_type: str, content: bytes) -> None:
        raise ValidationError("Formato de archivo no soportado")


class SimpleFileValidatorFactory(FileValidatorFactory):
    def __init__(self) -> None:
        self._pdf_validator = PDFFileValidator()
        self._unsupported_validator = UnsupportedFileValidator()

    def for_file(self, filename: str, mime_type: str) -> FileValidator:
        extension = Path(filename).suffix.lower()
        if extension == ".pdf" or mime_type == "application/pdf":
            return self._pdf_validator
        return self._unsupported_validator

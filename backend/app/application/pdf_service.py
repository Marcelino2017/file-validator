from __future__ import annotations

import logging
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
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

logger = logging.getLogger(__name__)


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

    # ------------------------------------------------------------------
    # Cedula detection pipeline
    # ------------------------------------------------------------------

    def _pdf_contains_user_cedula(self, content: bytes, cedula: str) -> bool:
        normalized_cedula = self._normalize_digits(cedula)
        if not normalized_cedula:
            return False

        # Layer 1: pypdf native text extraction
        pypdf_text = self._extract_text_pypdf(content)
        logger.info("pypdf extracted %d chars", len(pypdf_text))
        if self._contains_cedula_variant(pypdf_text, normalized_cedula):
            return True

        # Layer 2: pdfplumber (better at complex layouts / embedded fonts)
        plumber_text = self._extract_text_pdfplumber(content)
        logger.info("pdfplumber extracted %d chars", len(plumber_text))
        if self._contains_cedula_variant(plumber_text, normalized_cedula):
            return True

        # Layer 3: PyMuPDF built-in text extraction (works on some PDFs the others miss)
        fitz_text = self._extract_text_fitz(content)
        logger.info("fitz extracted %d chars", len(fitz_text))
        if self._contains_cedula_variant(fitz_text, normalized_cedula):
            return True

        # Layer 4: OCR on embedded images (photos/scans pasted inside the PDF)
        embedded_ocr_text = self._extract_text_from_embedded_images(content)
        logger.info("Embedded images OCR extracted %d chars", len(embedded_ocr_text))
        if self._contains_cedula_variant(embedded_ocr_text, normalized_cedula, from_ocr=True):
            return True

        # Layer 5: Full-page OCR (for fully scanned / image-based PDFs)
        ocr_text = self._extract_text_ocr(content)
        logger.info("Full-page OCR extracted %d chars", len(ocr_text))
        return self._contains_cedula_variant(ocr_text, normalized_cedula, from_ocr=True)

    # ------------------------------------------------------------------
    # Cedula matching helpers
    # ------------------------------------------------------------------

    def _contains_cedula_variant(
        self,
        text: str,
        normalized_cedula: str,
        from_ocr: bool = False,
    ) -> bool:
        if not text.strip():
            return False

        normalized_text_digits = self._normalize_digits(text, from_ocr=from_ocr)
        if normalized_cedula in normalized_text_digits:
            return True

        cedula_pattern = self._build_cedula_pattern(normalized_cedula)
        candidate_text = text if not from_ocr else self._normalize_ocr_text(text)
        return bool(cedula_pattern.search(candidate_text))

    def _build_cedula_pattern(self, normalized_cedula: str) -> re.Pattern[str]:
        digits_pattern = r"[\s\.\-_/,:;]*".join(re.escape(ch) for ch in normalized_cedula)
        prefix_pattern = r"(?:c\s*\.?\s*c\s*\.?\s*)?(?:n\s*\.?\s*o\s*\.?\s*)?"
        return re.compile(
            rf"(?<!\d){prefix_pattern}{digits_pattern}(?!\d)",
            flags=re.IGNORECASE,
        )

    def _normalize_digits(self, value: str, from_ocr: bool = False) -> str:
        normalized = value
        if from_ocr:
            normalized = self._normalize_ocr_text(normalized)
        return re.sub(r"\D", "", normalized)

    def _normalize_ocr_text(self, value: str) -> str:
        return value.translate(
            str.maketrans(
                {
                    "O": "0",
                    "o": "0",
                    "Q": "0",
                    "D": "0",
                    "I": "1",
                    "l": "1",
                    "L": "1",
                    "|": "1",
                    "!": "1",
                    "S": "5",
                    "s": "5",
                    "$": "5",
                    "B": "8",
                    "Z": "2",
                    "z": "2",
                    "G": "6",
                    "g": "9",
                }
            )
        )

    # ------------------------------------------------------------------
    # Text extraction: Layer 1 – pypdf
    # ------------------------------------------------------------------

    def _extract_text_pypdf(self, content: bytes) -> str:
        try:
            reader = PdfReader(BytesIO(content))
        except Exception as exc:
            raise ValidationError("No fue posible leer el contenido del PDF") from exc

        return "\n".join((page.extract_text() or "") for page in reader.pages)

    # ------------------------------------------------------------------
    # Text extraction: Layer 2 – pdfplumber
    # ------------------------------------------------------------------

    def _extract_text_pdfplumber(self, content: bytes) -> str:
        try:
            import pdfplumber
        except ImportError:
            logger.warning("pdfplumber not installed, skipping layer 2")
            return ""

        try:
            with pdfplumber.open(BytesIO(content)) as pdf:
                return "\n".join(
                    (page.extract_text() or "") for page in pdf.pages
                )
        except Exception:
            logger.warning("pdfplumber failed to parse PDF", exc_info=True)
            return ""

    # ------------------------------------------------------------------
    # Text extraction: Layer 3 – PyMuPDF (fitz) native text
    # ------------------------------------------------------------------

    def _extract_text_fitz(self, content: bytes) -> str:
        try:
            import fitz
        except ImportError:
            logger.warning("PyMuPDF not installed, skipping layer 3")
            return ""

        try:
            doc = fitz.open(stream=content, filetype="pdf")
            try:
                return "\n".join(page.get_text() for page in doc)
            finally:
                doc.close()
        except Exception:
            logger.warning("fitz text extraction failed", exc_info=True)
            return ""

    # ------------------------------------------------------------------
    # Text extraction: Layer 4 – OCR on embedded images
    # ------------------------------------------------------------------

    def _extract_text_from_embedded_images(self, content: bytes) -> str:
        try:
            import fitz
            import cv2
            import numpy as np
            import pytesseract
            from pytesseract import TesseractNotFoundError
        except ImportError:
            logger.warning("OCR libs not installed, skipping embedded image OCR")
            return ""

        self._configure_tesseract(pytesseract)
        MIN_IMAGE_SIZE = 80

        text_parts: list[str] = []
        document = fitz.open(stream=content, filetype="pdf")
        try:
            seen_xrefs: set[int] = set()
            for page in document:
                for img_info in page.get_images(full=True):
                    xref = img_info[0]
                    if xref in seen_xrefs:
                        continue
                    seen_xrefs.add(xref)

                    try:
                        base_image = document.extract_image(xref)
                    except Exception:
                        continue
                    if not base_image or not base_image.get("image"):
                        continue

                    image_bytes = base_image["image"]
                    img_array = np.frombuffer(image_bytes, dtype=np.uint8)
                    image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    if image is None:
                        continue
                    h, w = image.shape[:2]
                    if h < MIN_IMAGE_SIZE or w < MIN_IMAGE_SIZE:
                        continue

                    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                    preprocessed = self._preprocess_for_ocr(gray, cv2)

                    for img in preprocessed:
                        text = self._run_tesseract(
                            img, pytesseract, TesseractNotFoundError,
                        )
                        if text:
                            text_parts.append(text)
        except Exception:
            logger.warning("Embedded image extraction failed", exc_info=True)
        finally:
            document.close()

        return "\n".join(text_parts)

    # ------------------------------------------------------------------
    # Text extraction: Layer 5 – Full-page OCR (scanned PDFs)
    # ------------------------------------------------------------------

    def _extract_text_ocr(self, content: bytes) -> str:
        try:
            import fitz
            import cv2
            import numpy as np
            import pytesseract
            from pytesseract import TesseractNotFoundError
        except ImportError as exc:
            raise ValidationError(
                "No fue posible cargar el motor OCR para PDF escaneado"
            ) from exc

        self._configure_tesseract(pytesseract)

        text_parts: list[str] = []
        document = fitz.open(stream=content, filetype="pdf")
        try:
            for page in document:
                page_rect = page.rect
                clips = [
                    None,
                    fitz.Rect(
                        page_rect.x0,
                        page_rect.y0,
                        page_rect.x1,
                        page_rect.y0 + page_rect.height / 2,
                    ),
                    fitz.Rect(
                        page_rect.x0,
                        page_rect.y0 + page_rect.height / 2,
                        page_rect.x1,
                        page_rect.y1,
                    ),
                ]
                for zoom in (2, 3, 4):
                    matrix = fitz.Matrix(zoom, zoom)
                    for clip in clips:
                        pixmap = page.get_pixmap(
                            matrix=matrix, alpha=False, clip=clip,
                        )
                        image = np.frombuffer(
                            pixmap.samples, dtype=np.uint8,
                        ).reshape(pixmap.height, pixmap.width, pixmap.n)

                        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
                        preprocessed = self._preprocess_for_ocr(gray, cv2)

                        for img in preprocessed:
                            text = self._run_tesseract(
                                img, pytesseract, TesseractNotFoundError,
                            )
                            if text:
                                text_parts.append(text)
        finally:
            document.close()

        return "\n".join(text_parts)

    def _configure_tesseract(self, pytesseract) -> None:  # type: ignore[no-untyped-def]
        candidates = (
            Path("C:/Program Files/Tesseract-OCR/tesseract.exe"),
            Path("C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"),
            Path("C:/Users/Public/Apps/Tesseract-OCR/tesseract.exe"),
        )
        for candidate in candidates:
            if candidate.exists():
                pytesseract.pytesseract.tesseract_cmd = str(candidate)
                return

    @staticmethod
    def _preprocess_for_ocr(gray, cv2):  # type: ignore[no-untyped-def]
        """Return multiple preprocessed versions to maximise OCR accuracy."""
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        _, otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        adaptive = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2,
        )
        bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
        _, bilateral_otsu = cv2.threshold(
            bilateral, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU,
        )
        return (gray, blurred, otsu, adaptive, bilateral_otsu)

    @staticmethod
    def _run_tesseract(image, pytesseract, TesseractNotFoundError) -> str:  # type: ignore[no-untyped-def]
        """Run Tesseract with full-text recognition (no whitelist restriction)."""
        lang = "spa+eng"
        configs = [
            "--oem 3 --psm 3",
            "--oem 3 --psm 6",
            "--oem 3 --psm 4",
        ]
        parts: list[str] = []
        for config in configs:
            try:
                extracted = pytesseract.image_to_string(
                    image, lang=lang, config=config,
                )
            except Exception:
                try:
                    extracted = pytesseract.image_to_string(
                        image, lang="eng", config=config,
                    )
                except TesseractNotFoundError as exc:
                    raise ValidationError(
                        "Tesseract OCR no está instalado en el sistema"
                    ) from exc
            if extracted and extracted.strip():
                parts.append(extracted)
        return "\n".join(parts)

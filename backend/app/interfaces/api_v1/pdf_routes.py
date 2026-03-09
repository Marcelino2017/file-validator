from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.application.exceptions import NotFoundError, ValidationError
from app.application.pdf_service import ValidateAndUploadPDF, ValidateAndUploadPDFInput
from app.domain.entities import User
from app.interfaces.dependencies import (
    get_current_user,
    get_upload_pdf_use_case,
)
from app.interfaces.schemas.pdf import PDFUploadResponse


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload-pdf", response_model=PDFUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    use_case: ValidateAndUploadPDF = Depends(get_upload_pdf_use_case),
) -> PDFUploadResponse:
    try:
        content = await file.read()
        result = use_case.execute(
            ValidateAndUploadPDFInput(
                filename=file.filename or "archivo.pdf",
                mime_type=file.content_type or "application/octet-stream",
                content=content,
                user_id=current_user.id or 0,
            )
        )
    except (ValidationError, NotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return PDFUploadResponse(
        id=result.id or 0,
        filename=result.filename,
        mime_type=result.mime_type,
        sha256=result.sha256,
        storage_path=result.storage_path,
    )

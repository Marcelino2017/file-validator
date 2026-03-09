from pydantic import BaseModel


class PDFUploadResponse(BaseModel):
    id: int
    filename: str
    mime_type: str
    sha256: str
    storage_path: str

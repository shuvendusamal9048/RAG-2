from datetime import datetime

from pydantic import BaseModel


class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    file_size: int
    sha256: str
    status: str
    created_at: datetime
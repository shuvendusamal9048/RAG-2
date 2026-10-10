from pydantic import BaseModel


class IngestionResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str
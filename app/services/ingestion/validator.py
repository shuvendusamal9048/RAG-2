from pathlib import Path

from fastapi import UploadFile

from app.core.exceptions import AppException

ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


async def validate_uploaded_file(file: UploadFile) -> bytes:
    filename = Path(file.filename or "").name

    if not filename:
        raise AppException(
            message="Filename is required",
            code="INVALID_FILENAME",
            status_code=400,
        )

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise AppException(
            message="Only PDF files are allowed",
            code="INVALID_FILE_TYPE",
            status_code=400,
        )

    content = await file.read()

    if not content:
        raise AppException(
            message="Uploaded file is empty",
            code="EMPTY_FILE",
            status_code=400,
        )

    if len(content) > MAX_FILE_SIZE:
        raise AppException(
            message="File size exceeds the 10 MB limit",
            code="FILE_TOO_LARGE",
            status_code=413,
        )

    return content
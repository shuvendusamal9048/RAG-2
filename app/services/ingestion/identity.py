import hashlib


def generate_document_id(filename: str) -> str:
    normalized_filename = filename.strip().lower()

    return hashlib.sha256(
        normalized_filename.encode("utf-8")
    ).hexdigest()[:16]
import hashlib


def calculate_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def calculate_chunk_sha256(text: str) -> str:
    normalized_text = text.strip()

    return hashlib.sha256(
        normalized_text.encode("utf-8")
    ).hexdigest()
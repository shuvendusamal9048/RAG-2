from app.services.ingestion.hasher import (
    calculate_chunk_sha256,
    calculate_sha256,
)


def test_file_sha256_same_content():
    content = b"hello world"

    hash_1 = calculate_sha256(content)
    hash_2 = calculate_sha256(content)

    assert hash_1 == hash_2


def test_file_sha256_different_content():
    hash_1 = calculate_sha256(b"hello world")
    hash_2 = calculate_sha256(b"hello python")

    assert hash_1 != hash_2


def test_chunk_sha256_same_text():
    text = "Employee leave policy"

    hash_1 = calculate_chunk_sha256(text)
    hash_2 = calculate_chunk_sha256(text)

    assert hash_1 == hash_2


def test_chunk_sha256_different_text():
    hash_1 = calculate_chunk_sha256(
        "Employee receives 12 leaves."
    )

    hash_2 = calculate_chunk_sha256(
        "Employee receives 15 leaves."
    )

    assert hash_1 != hash_2


def test_chunk_sha256_ignores_outer_whitespace():
    hash_1 = calculate_chunk_sha256(
        "Employee leave policy"
    )

    hash_2 = calculate_chunk_sha256(
        "   Employee leave policy   "
    )

    assert hash_1 == hash_2
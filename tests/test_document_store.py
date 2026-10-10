from pathlib import Path

from app.storage.document_store import DocumentStore
from datetime import datetime, timezone

from app.schemas.metadata import DocumentMetadata

def test_document_store_initializes(tmp_path):
    store = DocumentStore(base_dir=tmp_path)

    store.initialize()

    assert store.original_dir.exists()
    assert store.extracted_dir.exists()
    assert store.chunks_dir.exists()
    assert store.metadata_dir.exists()

def test_save_original_file(tmp_path):
    source_file = tmp_path / "sample.pdf"
    source_file.write_bytes(b"fake pdf content")

    store = DocumentStore(base_dir=tmp_path / "storage")

    saved_file = store.save_original(
        source_path=source_file,
        filename="sample.pdf",
    )

    assert saved_file.exists()
    assert saved_file.name == "sample.pdf"
    assert saved_file.read_bytes() == b"fake pdf content"

def test_save_metadata(tmp_path):
    store = DocumentStore(base_dir=tmp_path)

    metadata = DocumentMetadata(
        document_id="test-document-123",
        filename="sample.pdf",
        file_size=1024,
        sha256="abc123",
        status="processed",
        created_at=datetime.now(timezone.utc),
    )

    metadata_path = store.save_metadata(metadata)

    assert metadata_path.exists()
    assert metadata_path.name == "test-document-123.json"

    content = metadata_path.read_text(encoding="utf-8")

    assert "sample.pdf" in content
    assert "abc123" in content
    assert "processed" in content
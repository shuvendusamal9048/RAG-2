from app.storage.chunk_store import ChunkStore


def test_chunk_store_initializes(tmp_path):
    store = ChunkStore(
        base_dir=tmp_path
    )

    store.initialize()

    assert store.chunks_dir.exists()


def test_save_and_get_chunks(tmp_path):
    store = ChunkStore(
        base_dir=tmp_path
    )

    chunks = [
        {
            "chunk_id": "doc-1-p1-c0",
            "page_number": 1,
            "chunk_index": 0,
            "sha256": "abc123",
        },
        {
            "chunk_id": "doc-1-p1-c1",
            "page_number": 1,
            "chunk_index": 1,
            "sha256": "def456",
        },
    ]

    saved_path = store.save_chunks(
        document_id="doc-1",
        chunks=chunks,
    )

    assert saved_path.exists()

    loaded_chunks = store.get_chunks(
        document_id="doc-1"
    )

    assert loaded_chunks == chunks


def test_get_chunks_for_unknown_document(tmp_path):
    store = ChunkStore(
        base_dir=tmp_path
    )

    chunks = store.get_chunks(
        document_id="unknown-document"
    )

    assert chunks == []
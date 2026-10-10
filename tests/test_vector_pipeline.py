from app.services.embeddings.embedder import EmbeddingService
from app.services.ingestion.vector_pipeline import update_vector_store
from app.storage.vector_store import VectorStore


class FakeEmbeddingService(EmbeddingService):
    def __init__(self):
        pass

    def embed_texts(self, texts):
        embeddings = []

        for text in texts:
            if "leave" in text.lower():
                embeddings.append([1.0, 0.0, 0.0])
            else:
                embeddings.append([0.0, 1.0, 0.0])

        return embeddings


def test_update_vector_store_adds_new_chunks(tmp_path):
    vector_store = VectorStore(
        base_dir=tmp_path,
        dimension=3,
    )

    embedding_service = FakeEmbeddingService()

    added_chunks = [
        {
            "chunk_id": "chunk-1",
            "document_id": "doc-1",
            "page_number": 1,
            "chunk_index": 0,
            "sha256": "hash-1",
            "text": "Employee leave policy",
        },
        {
            "chunk_id": "chunk-2",
            "document_id": "doc-1",
            "page_number": 1,
            "chunk_index": 1,
            "sha256": "hash-2",
            "text": "Employee salary policy",
        },
    ]

    result = update_vector_store(
        changed_chunks=[],
        added_chunks=added_chunks,
        removed_chunks=[],
        vector_store=vector_store,
        embedding_service=embedding_service,
    )

    assert result["embedded"] == 2
    assert result["added"] == 2

    results = vector_store.search(
        embedding=[1.0, 0.0, 0.0],
        top_k=5,
    )

    assert len(results) == 2
    assert results[0]["chunk_id"] == "chunk-1"


def test_update_vector_store_removes_chunks(tmp_path):
    vector_store = VectorStore(
        base_dir=tmp_path,
        dimension=3,
    )

    embedding_service = FakeEmbeddingService()

    chunks = [
        {
            "chunk_id": "chunk-1",
            "document_id": "doc-1",
            "page_number": 1,
            "chunk_index": 0,
            "sha256": "hash-1",
            "text": "Employee leave policy",
        },
        {
            "chunk_id": "chunk-2",
            "document_id": "doc-1",
            "page_number": 1,
            "chunk_index": 1,
            "sha256": "hash-2",
            "text": "Employee salary policy",
        },
    ]

    update_vector_store(
        changed_chunks=[],
        added_chunks=chunks,
        removed_chunks=[],
        vector_store=vector_store,
        embedding_service=embedding_service,
    )

    result = update_vector_store(
        changed_chunks=[],
        added_chunks=[],
        removed_chunks=[chunks[0]],
        vector_store=vector_store,
        embedding_service=embedding_service,
    )

    assert result["embedded"] == 0
    assert result["removed"] == 1

    results = vector_store.search(
        embedding=[1.0, 0.0, 0.0],
        top_k=5,
    )

    assert len(results) == 1
    assert results[0]["chunk_id"] == "chunk-2"


def test_update_vector_store_changes_chunk(tmp_path):
    vector_store = VectorStore(
        base_dir=tmp_path,
        dimension=3,
    )

    embedding_service = FakeEmbeddingService()

    old_chunk = {
        "chunk_id": "chunk-1",
        "document_id": "doc-1",
        "page_number": 1,
        "chunk_index": 0,
        "sha256": "old-hash",
        "text": "Employee leave policy",
    }

    update_vector_store(
        changed_chunks=[],
        added_chunks=[old_chunk],
        removed_chunks=[],
        vector_store=vector_store,
        embedding_service=embedding_service,
    )

    new_chunk = {
        "chunk_id": "chunk-1",
        "document_id": "doc-1",
        "page_number": 1,
        "chunk_index": 0,
        "sha256": "new-hash",
        "text": "Employee salary policy",
    }

    result = update_vector_store(
        changed_chunks=[new_chunk],
        added_chunks=[],
        removed_chunks=[],
        vector_store=vector_store,
        embedding_service=embedding_service,
    )

    assert result["embedded"] == 1
    assert result["changed"] == 1

    results = vector_store.search(
        embedding=[0.0, 1.0, 0.0],
        top_k=5,
    )

    assert len(results) == 1
    assert results[0]["chunk_id"] == "chunk-1"
    assert results[0]["sha256"] == "new-hash"
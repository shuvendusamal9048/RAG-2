import numpy as np

from app.storage.vector_store import VectorStore


def test_vector_store_initializes(tmp_path):
    store = VectorStore(
        base_dir=tmp_path,
        dimension=3,
    )

    store.initialize()

    assert store.vector_dir.exists()


def test_add_and_search(tmp_path):
    store = VectorStore(
        base_dir=tmp_path,
        dimension=3,
    )

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
        [0.0, 0.0, 1.0],
    ]

    metadata = [
        {
            "chunk_id": "chunk-1",
            "document_id": "doc-1",
            "text": "Employee leave policy",
        },
        {
            "chunk_id": "chunk-2",
            "document_id": "doc-1",
            "text": "Employee salary policy",
        },
        {
            "chunk_id": "chunk-3",
            "document_id": "doc-2",
            "text": "Office timing policy",
        },
    ]

    store.add(
        embeddings=embeddings,
        metadata=metadata,
    )

    results = store.search(
        embedding=[1.0, 0.0, 0.0],
        top_k=2,
    )

    assert len(results) == 2

    assert results[0]["chunk_id"] == "chunk-1"

    assert results[0]["score"] > 0.9


def test_search_empty_store(tmp_path):
    store = VectorStore(
        base_dir=tmp_path,
        dimension=3,
    )

    results = store.search(
        embedding=[1.0, 0.0, 0.0],
        top_k=5,
    )

    assert results == []


def test_remove(tmp_path):
    store = VectorStore(
        base_dir=tmp_path,
        dimension=3,
    )

    embeddings = [
        [1.0, 0.0, 0.0],
        [0.0, 1.0, 0.0],
    ]

    metadata = [
        {
            "chunk_id": "chunk-1",
            "document_id": "doc-1",
            "text": "Leave policy",
        },
        {
            "chunk_id": "chunk-2",
            "document_id": "doc-1",
            "text": "Salary policy",
        },
    ]

    store.add(
        embeddings=embeddings,
        metadata=metadata,
    )

    store.remove(
        {"chunk-1"}
    )

    results = store.search(
        embedding=[1.0, 0.0, 0.0],
        top_k=5,
    )

    assert len(results) == 1

    assert results[0]["chunk_id"] == "chunk-2"


def test_remove_unknown_chunk(tmp_path):
    store = VectorStore(
        base_dir=tmp_path,
        dimension=3,
    )

    embeddings = [
        [1.0, 0.0, 0.0],
    ]

    metadata = [
        {
            "chunk_id": "chunk-1",
            "document_id": "doc-1",
            "text": "Leave policy",
        }
    ]

    store.add(
        embeddings=embeddings,
        metadata=metadata,
    )

    store.remove(
        {"unknown-chunk"}
    )

    results = store.search(
        embedding=[1.0, 0.0, 0.0],
        top_k=5,
    )

    assert len(results) == 1
    assert results[0]["chunk_id"] == "chunk-1"
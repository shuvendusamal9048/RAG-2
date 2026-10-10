from app.storage.bm25_store import BM25Store


def test_bm25_store_initializes(tmp_path):
    store = BM25Store(
        base_dir=tmp_path
    )

    store.initialize()

    assert store.bm25_dir.exists()


def test_add_and_search(tmp_path):
    store = BM25Store(
        base_dir=tmp_path
    )

    chunks = [
        {
            "chunk_id": "chunk-1",
            "document_id": "doc-1",
            "page_number": 1,
            "chunk_index": 0,
            "sha256": "hash-1",
            "text": (
                "Employees receive annual leave "
                "according to company policy."
            ),
        },
        {
            "chunk_id": "chunk-2",
            "document_id": "doc-1",
            "page_number": 2,
            "chunk_index": 0,
            "sha256": "hash-2",
            "text": (
                "Employees receive salary "
                "at the end of every month."
            ),
        },
        {
            "chunk_id": "chunk-3",
            "document_id": "doc-2",
            "page_number": 1,
            "chunk_index": 0,
            "sha256": "hash-3",
            "text": (
                "Office working hours are "
                "nine to six."
            ),
        },
    ]

    store.add(chunks)

    results = store.search(
        query="annual leave",
        top_k=2,
    )

    assert len(results) == 2

    assert results[0]["chunk_id"] == "chunk-1"

    assert results[0]["score"] > 0


def test_bm25_empty_store(tmp_path):
    store = BM25Store(
        base_dir=tmp_path
    )

    results = store.search(
        query="annual leave",
        top_k=5,
    )

    assert results == []


def test_bm25_remove(tmp_path):
    store = BM25Store(
        base_dir=tmp_path
    )

    chunks = [
        {
            "chunk_id": "chunk-1",
            "document_id": "doc-1",
            "page_number": 1,
            "chunk_index": 0,
            "sha256": "hash-1",
            "text": "Annual leave policy",
        },
        {
            "chunk_id": "chunk-2",
            "document_id": "doc-1",
            "page_number": 2,
            "chunk_index": 0,
            "sha256": "hash-2",
            "text": "Salary policy",
        },
    ]

    store.add(chunks)

    store.remove(
        {"chunk-1"}
    )

    results = store.search(
        query="annual leave",
        top_k=5,
    )

    assert len(results) == 1

    assert results[0]["chunk_id"] == "chunk-2"


def test_bm25_does_not_duplicate_chunks(tmp_path):
    store = BM25Store(
        base_dir=tmp_path
    )

    chunk = {
        "chunk_id": "chunk-1",
        "document_id": "doc-1",
        "page_number": 1,
        "chunk_index": 0,
        "sha256": "hash-1",
        "text": "Annual leave policy",
    }

    store.add([chunk])
    store.add([chunk])

    corpus = store._load_corpus()

    assert len(corpus) == 1
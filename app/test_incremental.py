from app.services.ingestion.incremental import compare_chunks


def test_compare_chunks():
    old_chunks = [
        {
            "chunk_id": "doc-1-p1-c0",
            "page_number": 1,
            "chunk_index": 0,
            "sha256": "hash-a",
        },
        {
            "chunk_id": "doc-1-p1-c1",
            "page_number": 1,
            "chunk_index": 1,
            "sha256": "hash-b",
        },
        {
            "chunk_id": "doc-1-p1-c2",
            "page_number": 1,
            "chunk_index": 2,
            "sha256": "hash-c",
        },
    ]

    new_chunks = [
        {
            "chunk_id": "doc-1-p1-c0",
            "page_number": 1,
            "chunk_index": 0,
            "sha256": "hash-a",
        },
        {
            "chunk_id": "doc-1-p1-c1",
            "page_number": 1,
            "chunk_index": 1,
            "sha256": "hash-new",
        },
        {
            "chunk_id": "doc-1-p1-c3",
            "page_number": 1,
            "chunk_index": 3,
            "sha256": "hash-d",
        },
    ]

    result = compare_chunks(
        old_chunks=old_chunks,
        new_chunks=new_chunks,
    )

    assert len(result.unchanged) == 1
    assert result.unchanged[0]["chunk_id"] == "doc-1-p1-c0"

    assert len(result.changed) == 1
    assert result.changed[0]["chunk_id"] == "doc-1-p1-c1"

    assert len(result.added) == 1
    assert result.added[0]["chunk_id"] == "doc-1-p1-c3"

    assert len(result.removed) == 1
    assert result.removed[0]["chunk_id"] == "doc-1-p1-c2"


def test_compare_identical_chunks():
    chunks = [
        {
            "chunk_id": "doc-1-p1-c0",
            "page_number": 1,
            "chunk_index": 0,
            "sha256": "hash-a",
        }
    ]

    result = compare_chunks(
        old_chunks=chunks,
        new_chunks=chunks,
    )

    assert len(result.unchanged) == 1
    assert result.changed == []
    assert result.added == []
    assert result.removed == []


def test_compare_empty_old_chunks():
    new_chunks = [
        {
            "chunk_id": "doc-1-p1-c0",
            "page_number": 1,
            "chunk_index": 0,
            "sha256": "hash-a",
        }
    ]

    result = compare_chunks(
        old_chunks=[],
        new_chunks=new_chunks,
    )

    assert result.unchanged == []
    assert result.changed == []
    assert len(result.added) == 1
    assert result.removed == []


def test_compare_empty_new_chunks():
    old_chunks = [
        {
            "chunk_id": "doc-1-p1-c0",
            "page_number": 1,
            "chunk_index": 0,
            "sha256": "hash-a",
        }
    ]

    result = compare_chunks(
        old_chunks=old_chunks,
        new_chunks=[],
    )

    assert result.unchanged == []
    assert result.changed == []
    assert result.added == []
    assert len(result.removed) == 1
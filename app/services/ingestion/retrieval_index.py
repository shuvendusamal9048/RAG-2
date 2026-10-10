from app.services.embeddings.embedder import EmbeddingService
from app.services.ingestion.vector_pipeline import (
    update_vector_store,
)
from app.storage.bm25_store import BM25Store
from app.storage.vector_store import VectorStore


def update_retrieval_indexes(
    changed_chunks: list[dict],
    added_chunks: list[dict],
    removed_chunks: list[dict],
    vector_store: VectorStore | None = None,
    bm25_store: BM25Store | None = None,
    embedding_service: EmbeddingService | None = None,
) -> dict:
    vector_store = (
        vector_store
        or VectorStore()
    )

    bm25_store = (
        bm25_store
        or BM25Store()
    )

    # ---------------------------------------------------------
    # Vector index
    # ---------------------------------------------------------
    vector_result = update_vector_store(
        changed_chunks=changed_chunks,
        added_chunks=added_chunks,
        removed_chunks=removed_chunks,
        vector_store=vector_store,
        embedding_service=embedding_service,
    )

    # ---------------------------------------------------------
    # BM25 index
    # ---------------------------------------------------------

    # Remove old versions of changed chunks.
    changed_chunk_ids = {
        chunk["chunk_id"]
        for chunk in changed_chunks
    }

    removed_chunk_ids = {
        chunk["chunk_id"]
        for chunk in removed_chunks
    }

    bm25_store.remove(
        changed_chunk_ids
        | removed_chunk_ids
    )

    # Add current changed + newly added chunks.
    chunks_to_add = (
        changed_chunks
        + added_chunks
    )

    bm25_store.add(
        chunks_to_add
    )

    return {
        "embedded": vector_result["embedded"],
        "vector_removed": vector_result["removed"],
        "bm25_added": len(chunks_to_add),
        "bm25_removed": (
            len(changed_chunks)
            + len(removed_chunks)
        ),
        "changed": len(changed_chunks),
        "added": len(added_chunks),
        "removed": len(removed_chunks),
    }
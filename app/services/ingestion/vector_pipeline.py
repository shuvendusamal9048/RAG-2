from app.services.embeddings.embedder import EmbeddingService
from app.storage.vector_store import VectorStore


def update_vector_store(
    changed_chunks: list[dict],
    added_chunks: list[dict],
    removed_chunks: list[dict],
    vector_store: VectorStore | None = None,
    embedding_service: EmbeddingService | None = None,
) -> dict:
    vector_store = vector_store or VectorStore()
    embedding_service = (
        embedding_service
        or EmbeddingService()
    )

    # ---------------------------------------------------------
    # 1. Remove deleted chunks
    # ---------------------------------------------------------
    removed_chunk_ids = {
        chunk["chunk_id"]
        for chunk in removed_chunks
    }

    vector_store.remove(
        removed_chunk_ids
    )

    # ---------------------------------------------------------
    # 2. Remove old vectors for changed chunks
    # ---------------------------------------------------------
    changed_chunk_ids = {
        chunk["chunk_id"]
        for chunk in changed_chunks
    }

    vector_store.remove(
        changed_chunk_ids
    )

    # ---------------------------------------------------------
    # 3. Changed + added chunks need new embeddings
    # ---------------------------------------------------------
    chunks_to_embed = (
        changed_chunks
        + added_chunks
    )

    if not chunks_to_embed:
        return {
            "embedded": 0,
            "removed": len(removed_chunks),
            "changed": len(changed_chunks),
            "added": len(added_chunks),
        }

    # ---------------------------------------------------------
    # 4. Generate embeddings only for required chunks
    # ---------------------------------------------------------
    texts = [
        chunk["text"]
        for chunk in chunks_to_embed
    ]

    embeddings = embedding_service.embed_texts(
        texts
    )

    # ---------------------------------------------------------
    # 5. Store vectors + metadata
    # ---------------------------------------------------------
    metadata = [
        {
            "chunk_id": chunk["chunk_id"],
            "document_id": chunk.get(
                "document_id"
            ),
            "page_number": chunk["page_number"],
            "chunk_index": chunk["chunk_index"],
            "sha256": chunk["sha256"],
            "text": chunk["text"],
        }
        for chunk in chunks_to_embed
    ]

    vector_store.add(
        embeddings=embeddings,
        metadata=metadata,
    )

    return {
        "embedded": len(chunks_to_embed),
        "removed": len(removed_chunks),
        "changed": len(changed_chunks),
        "added": len(added_chunks),
    }
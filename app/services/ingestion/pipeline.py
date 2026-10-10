from pathlib import Path

from app.services.embeddings.embedder import EmbeddingService
from app.services.ingestion.chunker import chunk_text
from app.services.ingestion.cleaner import clean_text
from app.services.ingestion.extractor import extract_pdf_pages
from app.services.ingestion.hasher import calculate_chunk_sha256
from app.services.ingestion.incremental import compare_chunks
from app.services.ingestion.retrieval_index import (
    update_retrieval_indexes,
)
from app.storage.bm25_store import BM25Store
from app.storage.chunk_store import ChunkStore
from app.storage.vector_store import VectorStore


def process_document(
    document_id: str,
    pdf_path: Path,
    chunk_store: ChunkStore | None = None,
    vector_store: VectorStore | None = None,
    embedding_service: EmbeddingService | None = None,
    bm25_store: BM25Store | None = None,
) -> dict:
   
    chunk_store = (
        chunk_store
        or ChunkStore()
    )

    bm25_store = (
    bm25_store
    or BM25Store()
)

    vector_store = (
        vector_store
        or VectorStore()
    )

    vector_store = (
        vector_store
        or VectorStore()
    )

    # ---------------------------------------------------------
    # 1. Extract PDF pages
    # ---------------------------------------------------------
    pages = extract_pdf_pages(
        pdf_path
    )

    new_chunks = []

    # ---------------------------------------------------------
    # 2. Clean and chunk every page
    # ---------------------------------------------------------
    for page in pages:
        page_number = page["page_number"]

        cleaned_text = clean_text(
            page["text"]
        )

        chunks = chunk_text(
            text=cleaned_text,
            page_number=page_number,
        )

        # -----------------------------------------------------
        # 3. Create chunk metadata + SHA-256
        # -----------------------------------------------------
        for chunk in chunks:
            chunk_id = (
                f"{document_id}"
                f"-p{chunk.page_number}"
                f"-c{chunk.chunk_index}"
            )

            chunk_hash = calculate_chunk_sha256(
                chunk.text
            )

            new_chunks.append(
                {
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "page_number": chunk.page_number,
                    "chunk_index": chunk.chunk_index,
                    "sha256": chunk_hash,
                    "text": chunk.text,
                }
            )

    # ---------------------------------------------------------
    # 4. Load previous chunks
    # ---------------------------------------------------------
    old_chunks = chunk_store.get_chunks(
        document_id=document_id
    )

    # ---------------------------------------------------------
    # 5. Compare old vs new
    # ---------------------------------------------------------
    result = compare_chunks(
        old_chunks=old_chunks,
        new_chunks=new_chunks,
    )

    # ---------------------------------------------------------
    # 6. Update vector store
    #
    # Only changed/new chunks are embedded.
    # Unchanged chunks keep their existing vectors.
    # Removed chunks are deleted.
    # ---------------------------------------------------------
    retrieval_result = update_retrieval_indexes(
    changed_chunks=result.changed,
    added_chunks=result.added,
    removed_chunks=result.removed,
    vector_store=vector_store,
    bm25_store=bm25_store,
    embedding_service=embedding_service,
)
    # ---------------------------------------------------------
    # 7. Save latest chunk metadata
    # ---------------------------------------------------------
    chunk_store.save_chunks(
        document_id=document_id,
        chunks=new_chunks,
    )

    # ---------------------------------------------------------
    # 8. Return complete processing information
    # ---------------------------------------------------------
    return {
        "document_id": document_id,
        "total_chunks": len(new_chunks),
        "unchanged": len(result.unchanged),
        "changed": len(result.changed),
        "added": len(result.added),
        "removed": len(result.removed),
       "embedded": retrieval_result["embedded"],
    }
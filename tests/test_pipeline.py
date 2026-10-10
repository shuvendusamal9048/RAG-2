from pathlib import Path

import fitz

from app.services.ingestion.pipeline import process_document
from app.storage.chunk_store import ChunkStore


def create_test_pdf(path: Path, text: str) -> None:
    document = fitz.open()

    page = document.new_page()

    page.insert_text(
        (50, 50),
        text,
    )

    document.save(path)
    document.close()


def test_process_document(tmp_path):
    document_id = "test-document"

    pdf_path = tmp_path / "sample.pdf"

    create_test_pdf(
        pdf_path,
        "Employee leave policy. "
        "Employees receive annual leave.",
    )

    chunk_store = ChunkStore(
        base_dir=tmp_path / "storage"
    )

    result = process_document(
        document_id=document_id,
        pdf_path=pdf_path,
        chunk_store=chunk_store,
    )

    assert result["document_id"] == document_id
    assert result["total_chunks"] >= 1

    assert result["added"] >= 1
    assert result["unchanged"] == 0
    assert result["changed"] == 0
    assert result["removed"] == 0

    saved_chunks = chunk_store.get_chunks(
        document_id=document_id
    )

    assert len(saved_chunks) == result["total_chunks"]

    assert saved_chunks[0]["chunk_id"].startswith(
        document_id
    )

    assert saved_chunks[0]["sha256"]
    assert saved_chunks[0]["text"]


def test_process_same_document_twice(tmp_path):
    document_id = "test-document"

    pdf_path = tmp_path / "sample.pdf"

    create_test_pdf(
        pdf_path,
        "Employee leave policy. "
        "Employees receive annual leave.",
    )

    chunk_store = ChunkStore(
        base_dir=tmp_path / "storage"
    )

    first_result = process_document(
        document_id=document_id,
        pdf_path=pdf_path,
        chunk_store=chunk_store,
    )

    second_result = process_document(
        document_id=document_id,
        pdf_path=pdf_path,
        chunk_store=chunk_store,
    )

    assert first_result["added"] >= 1

    assert second_result["added"] == 0
    assert second_result["changed"] == 0
    assert second_result["removed"] == 0

    assert (
        second_result["unchanged"]
        == second_result["total_chunks"]
    )

def test_process_document_detects_changed_chunk(tmp_path):
    document_id = "test-document"

    pdf_path = tmp_path / "sample.pdf"

    chunk_store = ChunkStore(
        base_dir=tmp_path / "storage"
    )

    # First version
    create_test_pdf(
        pdf_path,
        "Employee leave policy. "
        "Employees receive annual leave.",
    )

    first_result = process_document(
        document_id=document_id,
        pdf_path=pdf_path,
        chunk_store=chunk_store,
    )

    assert first_result["added"] >= 1

    old_chunks = chunk_store.get_chunks(
        document_id=document_id
    )

    assert len(old_chunks) >= 1

    # Second version with changed content
    create_test_pdf(
        pdf_path,
        "Employee leave policy. "
        "Employees receive fifteen annual leave days.",
    )

    second_result = process_document(
        document_id=document_id,
        pdf_path=pdf_path,
        chunk_store=chunk_store,
    )

    assert second_result["changed"] >= 1
    assert second_result["added"] == 0

def test_incremental_processing_only_embeds_changed_chunks(
    tmp_path,
):
    from app.services.embeddings.embedder import EmbeddingService
    from app.storage.vector_store import VectorStore


    class CountingEmbeddingService(
        EmbeddingService
    ):
        def __init__(self):
            self.embedded_texts = []

        def embed_texts(self, texts):
            self.embedded_texts.extend(texts)

            return [
                [1.0] * 384
                for _ in texts
            ]


    document_id = "test-document"

    pdf_path = tmp_path / "sample.pdf"

    chunk_store = ChunkStore(
        base_dir=tmp_path / "storage"
    )

    vector_store = VectorStore(
        base_dir=tmp_path / "storage",
        dimension=384,
    )

    embedding_service = CountingEmbeddingService()

    # ---------------------------------------------------------
    # Version 1
    # ---------------------------------------------------------
    create_test_pdf(
        pdf_path,
        "Employee leave policy. "
        "Employees receive annual leave.",
    )

    first_result = process_document(
        document_id=document_id,
        pdf_path=pdf_path,
        chunk_store=chunk_store,
        vector_store=vector_store,
        embedding_service=embedding_service,
    )

    assert first_result["embedded"] >= 1

    first_embedded_count = len(
        embedding_service.embedded_texts
    )

    assert first_embedded_count == (
        first_result["embedded"]
    )

    # ---------------------------------------------------------
    # Version 2
    # ---------------------------------------------------------
    create_test_pdf(
        pdf_path,
        "Employee leave policy. "
        "Employees receive fifteen annual leave days.",
    )

    second_result = process_document(
        document_id=document_id,
        pdf_path=pdf_path,
        chunk_store=chunk_store,
        vector_store=vector_store,
        embedding_service=embedding_service,
    )

    assert second_result["changed"] >= 1

    # Only changed + added chunks should be embedded.
    assert second_result["embedded"] == (
        second_result["changed"]
        + second_result["added"]
    )

    # The second processing should not embed
    # unchanged chunks.
    assert len(
        embedding_service.embedded_texts
    ) == (
        first_embedded_count
        + second_result["embedded"]
    )
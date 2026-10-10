from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, File, UploadFile

from app.schemas.ingestion import IngestionResponse
from app.schemas.metadata import DocumentMetadata
from app.services.ingestion.hasher import calculate_sha256
from app.services.ingestion.identity import generate_document_id
from app.services.ingestion.pipeline import process_document
from app.services.ingestion.validator import validate_uploaded_file
from app.storage.chunk_store import ChunkStore
from app.storage.document_store import DocumentStore
from app.storage.metadata_store import MetadataStore


router = APIRouter(
    prefix="/ingestion",
    tags=["Ingestion"],
)


@router.post(
    "/documents",
    response_model=IngestionResponse,
)
async def ingest_document(
    file: UploadFile = File(...),
):
    store = DocumentStore()
    metadata_store = MetadataStore()
    chunk_store = ChunkStore()

    filename = Path(
        file.filename or "unknown.pdf"
    ).name

    content = await validate_uploaded_file(file)

    # ---------------------------------------------------------
    # 1. Calculate file-level SHA-256
    # ---------------------------------------------------------
    file_hash = calculate_sha256(content)

    # ---------------------------------------------------------
    # 2. Check whether this exact PDF already exists
    # ---------------------------------------------------------
    existing_document = metadata_store.find_by_sha256(
        file_hash
    )

    if existing_document:
        return IngestionResponse(
            document_id=existing_document["document_id"],
            filename=existing_document["filename"],
            status="skipped",
            message=(
                "Document already exists. "
                "No processing required."
            ),
        )

    # ---------------------------------------------------------
    # 3. Generate stable document ID
    # ---------------------------------------------------------
    document_id = generate_document_id(
        filename
    )

    # ---------------------------------------------------------
    # 4. Store this PDF version
    # ---------------------------------------------------------
    versioned_filename = (
        f"{document_id}_"
        f"{file_hash[:12]}_"
        f"{filename}"
    )

    temporary_path = (
        store.base_dir
        / f"temp_{versioned_filename}"
    )

    temporary_path.write_bytes(content)

    saved_path = store.save_original(
        source_path=temporary_path,
        filename=versioned_filename,
    )

    temporary_path.unlink(
        missing_ok=True
    )

    # ---------------------------------------------------------
    # 5. Run extraction → cleaning → chunking →
    #    chunk-level comparison
    # ---------------------------------------------------------
    processing_result = process_document(
        document_id=document_id,
        pdf_path=saved_path,
        chunk_store=chunk_store,
    )

    # ---------------------------------------------------------
    # 6. Save current document metadata
    # ---------------------------------------------------------
    metadata = DocumentMetadata(
        document_id=document_id,
        filename=filename,
        file_size=len(content),
        sha256=file_hash,
        status="processed",
        created_at=datetime.now(timezone.utc),
    )

    store.save_metadata(
        metadata
    )

    # ---------------------------------------------------------
    # 7. Return ingestion result
    # ---------------------------------------------------------
    return IngestionResponse(
        document_id=document_id,
        filename=filename,
        status="processed",
        message=(
            "Document processed successfully. "
            f"Chunks: {processing_result['total_chunks']}, "
            f"unchanged: {processing_result['unchanged']}, "
            f"changed: {processing_result['changed']}, "
            f"added: {processing_result['added']}, "
            f"removed: {processing_result['removed']}."
        ),
    )
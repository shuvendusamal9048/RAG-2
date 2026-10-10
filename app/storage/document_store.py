import json
import shutil
from pathlib import Path

from app.core.config import get_settings


class DocumentStore:
    def __init__(self, base_dir: Path | None = None):
        settings = get_settings()

        self.base_dir = (
            base_dir
            if base_dir is not None
            else Path(settings.document_dir)
        )

        self.original_dir = self.base_dir / "original"
        self.extracted_dir = self.base_dir / "extracted"
        self.chunks_dir = self.base_dir / "chunks"
        self.metadata_dir = self.base_dir / "metadata"

    def initialize(self) -> None:
        directories = [
            self.original_dir,
            self.extracted_dir,
            self.chunks_dir,
            self.metadata_dir,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def save_original(
    self,
    source_path: Path,
    filename: str,
) -> Path:
        self.initialize()

        destination = self.original_dir / filename

        shutil.copy2(
            source_path,
            destination,
        )

        return destination

    def save_metadata(self, metadata) -> Path:
        self.initialize()

        metadata_path = self.metadata_dir / f"{metadata.document_id}.json"

        with metadata_path.open("w", encoding="utf-8") as file:
            json.dump(
                metadata.model_dump(mode="json"),
                file,
                indent=2,
            )

        return metadata_path
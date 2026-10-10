import json
from pathlib import Path

from app.core.config import get_settings


class MetadataStore:
    def __init__(self, base_dir: Path | None = None):
        settings = get_settings()

        self.base_dir = (
            base_dir
            if base_dir is not None
            else Path(settings.document_dir)
        )

        self.metadata_dir = self.base_dir / "metadata"

    def find_by_sha256(self, sha256: str) -> dict | None:
        if not self.metadata_dir.exists():
            return None

        for metadata_file in self.metadata_dir.glob("*.json"):
            with metadata_file.open("r", encoding="utf-8") as file:
                metadata = json.load(file)

            if metadata.get("sha256") == sha256:
                return metadata

        return None
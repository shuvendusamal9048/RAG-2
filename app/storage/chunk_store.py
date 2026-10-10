import json
from pathlib import Path

from app.core.config import get_settings


class ChunkStore:
    def __init__(self, base_dir: Path | None = None):
        settings = get_settings()

        self.base_dir = (
            base_dir
            if base_dir is not None
            else Path(settings.document_dir)
        )

        self.chunks_dir = self.base_dir / "chunks"

    def initialize(self) -> None:
        self.chunks_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def save_chunks(
        self,
        document_id: str,
        chunks: list[dict],
    ) -> Path:
        self.initialize()

        chunks_path = (
            self.chunks_dir
            / f"{document_id}.json"
        )

        data = {
            "document_id": document_id,
            "chunks": chunks,
        }

        with chunks_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
            )

        return chunks_path

    def get_chunks(
        self,
        document_id: str,
    ) -> list[dict]:
        chunks_path = (
            self.chunks_dir
            / f"{document_id}.json"
        )

        if not chunks_path.exists():
            return []

        with chunks_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        return data.get("chunks", [])
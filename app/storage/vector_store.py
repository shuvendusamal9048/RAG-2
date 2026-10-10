import json
from pathlib import Path

import faiss
import numpy as np

from app.core.config import get_settings


class VectorStore:
    def __init__(
        self,
        base_dir: Path | None = None,
        dimension: int = 384,
    ):
        settings = get_settings()

        self.base_dir = (
            base_dir
            if base_dir is not None
            else Path(settings.document_dir)
        )

        self.vector_dir = (
            self.base_dir
            / "indexes"
            / "vector"
        )

        self.index_path = (
            self.vector_dir
            / "index.faiss"
        )

        self.metadata_path = (
            self.vector_dir
            / "metadata.json"
        )

        self.dimension = dimension

    def initialize(self) -> None:
        self.vector_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _create_index(self):
        return faiss.IndexFlatIP(
            self.dimension
        )

    def _load_index(self):
        self.initialize()

        if not self.index_path.exists():
            return self._create_index()

        return faiss.read_index(
            str(self.index_path)
        )

    def _load_metadata(self) -> list[dict]:
        self.initialize()

        if not self.metadata_path.exists():
            return []

        with self.metadata_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def _save(
        self,
        index,
        metadata: list[dict],
    ) -> None:
        self.initialize()

        faiss.write_index(
            index,
            str(self.index_path),
        )

        with self.metadata_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                metadata,
                file,
                indent=2,
                ensure_ascii=False,
            )

    def add(
        self,
        embeddings: list[list[float]],
        metadata: list[dict],
    ) -> None:
        if not embeddings:
            return

        if len(embeddings) != len(metadata):
            raise ValueError(
                "Embeddings and metadata "
                "must have the same length"
            )

        index = self._load_index()
        stored_metadata = self._load_metadata()

        vectors = np.asarray(
            embeddings,
            dtype="float32",
        )

        index.add(vectors)

        stored_metadata.extend(metadata)

        self._save(
            index,
            stored_metadata,
        )

    def search(
        self,
        embedding: list[float],
        top_k: int = 5,
    ) -> list[dict]:
        index = self._load_index()
        metadata = self._load_metadata()

        if index.ntotal == 0:
            return []

        query_vector = np.asarray(
            [embedding],
            dtype="float32",
        )

        scores, indices = index.search(
            query_vector,
            min(top_k, index.ntotal),
        )

        results = []

        for score, index_position in zip(
            scores[0],
            indices[0],
        ):
            if index_position < 0:
                continue

            item = metadata[
                int(index_position)
            ].copy()

            item["score"] = float(score)

            results.append(item)

        return results

    def remove(
        self,
        chunk_ids: set[str],
    ) -> None:
        if not chunk_ids:
            return

        metadata = self._load_metadata()

        if not metadata:
            return

        keep_indices = [
            index
            for index, item in enumerate(metadata)
            if item["chunk_id"] not in chunk_ids
        ]

        if len(keep_indices) == len(metadata):
            return

        old_index = self._load_index()

        vectors = []

        for index_position in keep_indices:
            vector = old_index.reconstruct(
                index_position
            )

            vectors.append(vector)

        new_index = self._create_index()

        if vectors:
            new_index.add(
                np.asarray(
                    vectors,
                    dtype="float32",
                )
            )

        new_metadata = [
            metadata[index]
            for index in keep_indices
        ]

        self._save(
            new_index,
            new_metadata,
        )
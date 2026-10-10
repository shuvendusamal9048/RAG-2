import json
from pathlib import Path

from rank_bm25 import BM25Okapi

from app.core.config import get_settings


class BM25Store:
    def __init__(
        self,
        base_dir: Path | None = None,
    ):
        settings = get_settings()

        self.base_dir = (
            base_dir
            if base_dir is not None
            else Path(settings.document_dir)
        )

        self.bm25_dir = (
            self.base_dir
            / "indexes"
            / "bm25"
        )

        self.corpus_path = (
            self.bm25_dir
            / "corpus.json"
        )

    def initialize(self) -> None:
        self.bm25_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def _load_corpus(self) -> list[dict]:
        self.initialize()

        if not self.corpus_path.exists():
            return []

        with self.corpus_path.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def _save_corpus(
        self,
        corpus: list[dict],
    ) -> None:
        self.initialize()

        with self.corpus_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                corpus,
                file,
                indent=2,
                ensure_ascii=False,
            )

    def add(
        self,
        chunks: list[dict],
    ) -> None:
        if not chunks:
            return

        corpus = self._load_corpus()

        existing_ids = {
            item["chunk_id"]
            for item in corpus
        }

        for chunk in chunks:
            if chunk["chunk_id"] in existing_ids:
                continue

            corpus.append(chunk)

        self._save_corpus(corpus)

    def remove(
        self,
        chunk_ids: set[str],
    ) -> None:
        if not chunk_ids:
            return

        corpus = self._load_corpus()

        filtered_corpus = [
            item
            for item in corpus
            if item["chunk_id"] not in chunk_ids
        ]

        self._save_corpus(
            filtered_corpus
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:
        corpus = self._load_corpus()

        if not corpus:
            return []

        tokenized_corpus = [
            item["text"].lower().split()
            for item in corpus
        ]

        bm25 = BM25Okapi(
            tokenized_corpus
        )

        query_tokens = (
            query.lower().split()
        )

        scores = bm25.get_scores(
            query_tokens
        )

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda index: scores[index],
            reverse=True,
        )

        results = []

        for index in ranked_indices[:top_k]:
            item = corpus[index].copy()

            item["score"] = float(
                scores[index]
            )

            results.append(item)

        return results
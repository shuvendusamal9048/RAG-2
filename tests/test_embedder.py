from app.services.embeddings.embedder import EmbeddingService


def test_embed_text():
    service = EmbeddingService()

    embedding = service.embed_text(
        "Employee leave policy"
    )

    assert isinstance(embedding, list)
    assert len(embedding) > 0
    assert all(
        isinstance(value, float)
        for value in embedding
    )


def test_embed_texts():
    service = EmbeddingService()

    embeddings = service.embed_texts(
        [
            "Employee leave policy",
            "Annual leave information",
        ]
    )

    assert len(embeddings) == 2
    assert len(embeddings[0]) > 0
    assert len(embeddings[0]) == len(embeddings[1])


def test_empty_text():
    service = EmbeddingService()

    try:
        service.embed_text("")
        assert False
    except ValueError as exc:
        assert "empty" in str(exc).lower()


def test_empty_texts():
    service = EmbeddingService()

    embeddings = service.embed_texts([])

    assert embeddings == []
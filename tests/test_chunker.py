from app.services.ingestion.chunker import chunk_text


def test_chunk_text():
    text = "A" * 2500

    chunks = chunk_text(
        text=text,
        page_number=3,
        chunk_size=1000,
        chunk_overlap=100,
    )

    assert len(chunks) == 3

    assert chunks[0].page_number == 3
    assert chunks[0].chunk_index == 0

    assert chunks[1].chunk_index == 1
    assert chunks[2].chunk_index == 2

    assert len(chunks[0].text) == 1000
    assert len(chunks[1].text) == 1000
    assert len(chunks[2].text) == 700


def test_chunk_empty_text():
    chunks = chunk_text(
        text="",
        page_number=1,
    )

    assert chunks == []


def test_chunk_overlap():
    text = "0123456789"

    chunks = chunk_text(
        text=text,
        page_number=1,
        chunk_size=6,
        chunk_overlap=2,
    )

    assert chunks[0].text == "012345"
    assert chunks[1].text == "456789"


def test_invalid_chunk_size():
    try:
        chunk_text(
            text="hello",
            page_number=1,
            chunk_size=0,
        )
        assert False
    except ValueError as exc:
        assert "chunk_size" in str(exc)


def test_invalid_overlap():
    try:
        chunk_text(
            text="hello",
            page_number=1,
            chunk_size=100,
            chunk_overlap=100,
        )
        assert False
    except ValueError as exc:
        assert "chunk_overlap" in str(exc)

def test_chunk_prefers_sentence_boundary():
    text = (
        "This is the first sentence. "
        "This is the second sentence. "
        "This is the third sentence."
    )

    chunks = chunk_text(
        text=text,
        page_number=1,
        chunk_size=40,
        chunk_overlap=5,
    )

    assert chunks[0].text.endswith(".")


def test_chunk_prefers_word_boundary():
    text = "This is a long sentence containing many words."

    chunks = chunk_text(
        text=text,
        page_number=1,
        chunk_size=20,
        chunk_overlap=5,
    )

    for chunk in chunks:
        assert not chunk.text.endswith(" ")
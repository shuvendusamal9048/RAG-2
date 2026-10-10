from dataclasses import dataclass


@dataclass
class Chunk:
    page_number: int
    chunk_index: int
    text: str


def _find_best_split(text: str, start: int, max_end: int) -> int:
    """
    Find the best natural boundary before max_end.

    Priority:
    1. Paragraph boundary
    2. Sentence boundary
    3. Word boundary
    4. Hard character boundary
    """

    if max_end >= len(text):
        return len(text)

    candidate = text[start:max_end]

    # 1. Prefer paragraph boundary
    paragraph_position = candidate.rfind("\n\n")

    if paragraph_position > 0:
        return start + paragraph_position + 2

    # 2. Prefer sentence boundary
    sentence_positions = [
        candidate.rfind(". "),
        candidate.rfind("? "),
        candidate.rfind("! "),
    ]

    best_sentence_position = max(sentence_positions)

    if best_sentence_position > 0:
        return start + best_sentence_position + 2

    # 3. Prefer word boundary
    word_position = candidate.rfind(" ")

    if word_position > 0:
        return start + word_position + 1

    # 4. Hard boundary
    return max_end


def chunk_text(
    text: str,
    page_number: int,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> list[Chunk]:

    if not text.strip():
        return []

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative")

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size"
        )

    chunks = []

    start = 0
    chunk_index = 0

    while start < len(text):
        max_end = min(
            start + chunk_size,
            len(text),
        )

        end = _find_best_split(
            text=text,
            start=start,
            max_end=max_end,
        )

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(
                Chunk(
                    page_number=page_number,
                    chunk_index=chunk_index,
                    text=chunk,
                )
            )

            chunk_index += 1

        if end >= len(text):
            break

        next_start = end - chunk_overlap

        if next_start <= start:
            next_start = end

        start = next_start

    return chunks
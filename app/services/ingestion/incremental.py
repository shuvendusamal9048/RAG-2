from dataclasses import dataclass


@dataclass
class IncrementalResult:
    unchanged: list[dict]
    changed: list[dict]
    added: list[dict]
    removed: list[dict]


def compare_chunks(
    old_chunks: list[dict],
    new_chunks: list[dict],
) -> IncrementalResult:
    old_by_id = {
        chunk["chunk_id"]: chunk
        for chunk in old_chunks
    }

    new_by_id = {
        chunk["chunk_id"]: chunk
        for chunk in new_chunks
    }

    unchanged = []
    changed = []
    added = []
    removed = []

    for chunk_id, new_chunk in new_by_id.items():
        old_chunk = old_by_id.get(chunk_id)

        if old_chunk is None:
            added.append(new_chunk)
            continue

        if old_chunk["sha256"] == new_chunk["sha256"]:
            unchanged.append(new_chunk)
        else:
            changed.append(new_chunk)

    for chunk_id, old_chunk in old_by_id.items():
        if chunk_id not in new_by_id:
            removed.append(old_chunk)

    return IncrementalResult(
        unchanged=unchanged,
        changed=changed,
        added=added,
        removed=removed,
    )
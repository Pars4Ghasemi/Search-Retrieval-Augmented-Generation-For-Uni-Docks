"""Split long sections into smaller, overlapping chunks for search."""

from app.loaders import Section

CHUNK_SIZE = 800  # characters
CHUNK_OVERLAP = 150  # characters shared between neighbouring chunks

# Try to split on the biggest natural boundary first, then fall back to smaller ones.
_SEPARATORS = ["\n\n", "\n", ". ", " "]


def _split(text: str, size: int, separators: list[str]) -> list[str]:
    if len(text) <= size:
        return [text]
    if not separators:
        return [text[i : i + size] for i in range(0, len(text), size)]

    sep, rest = separators[0], separators[1:]
    parts = text.split(sep)
    if sep == ". ":
        # Keep the full stop on every sentence except the last (which already has its own).
        parts = [p + "." for p in parts[:-1]] + parts[-1:]
    pieces = []
    for part in parts:
        if len(part) > size:
            pieces.extend(_split(part, size, rest))
        elif part:
            pieces.append(part)
    return pieces


def _merge(pieces: list[str], size: int, overlap: int) -> list[str]:
    chunks, current = [], ""
    for piece in pieces:
        candidate = f"{current} {piece}".strip() if current else piece
        if len(candidate) <= size:
            current = candidate
            continue
        if current:
            chunks.append(current.strip())
            tail = current[-overlap:] if overlap else ""
            # Start the overlap on a word boundary.
            tail = tail[tail.find(" ") + 1 :] if " " in tail else tail
            current = f"{tail} {piece}".strip()
            if len(current) > size:
                current = piece
        else:
            current = piece
    if current.strip():
        chunks.append(current.strip())
    return chunks


def chunk_sections(
    sections: list[Section], size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP
) -> list[Section]:
    """Return chunks that each carry their section's metadata plus a chunk index."""
    chunks = []
    for section in sections:
        pieces = _split(section.text, size, _SEPARATORS)
        for i, text in enumerate(_merge(pieces, size, overlap)):
            chunks.append(Section(text, {**section.metadata, "chunk": i}))
    return chunks

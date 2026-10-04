
import hashlib
import io
import re

from pypdf import PdfReader
from fastapi import HTTPException

from app.config import settings


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def extract_pdf(data):
    """Extract text from each PDF page while preserving page numbers."""

    try:
        reader = PdfReader(io.BytesIO(data), strict=False)

        pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            extracted_text = page.extract_text() or ""

            extracted_text = extracted_text.strip()

            if extracted_text:
                pages.append({
                    "page": page_number,
                    "text": extracted_text
                })

        return pages, len(reader.pages)

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid PDF: {exc}"
        )


def _normalize_text(text):
    """Normalize whitespace without destroying paragraph boundaries."""

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def _find_chunk_end(text, start, size):
    """
    Find a natural chunk boundary.

    Preference:
    1. Paragraph boundary
    2. Sentence boundary
    3. Word boundary
    4. Hard character boundary as a last resort
    """

    max_end = min(start + size, len(text))

    if max_end == len(text):
        return max_end

    min_end = start + int(size * 0.65)
    window = text[min_end:max_end]

    # Prefer paragraph boundaries.
    paragraph_end = window.rfind("\n\n")

    if paragraph_end >= 0:
        return min_end + paragraph_end + 2

    # Next prefer sentence boundaries.
    sentence_matches = list(
        re.finditer(r"(?<=[.!?])\s+", window)
    )

    if sentence_matches:
        return min_end + sentence_matches[-1].end()

    # Otherwise, split at the last available whitespace.
    whitespace_end = max(
        window.rfind(" "),
        window.rfind("\n")
    )

    if whitespace_end >= 0:
        return min_end + whitespace_end + 1

    return max_end


def _find_next_start(text, end, overlap, previous_start):
    """Calculate the next chunk start without splitting a word."""

    next_start = max(previous_start + 1, end - overlap)

    # If overlap begins in the middle of a word,
    # move forward to the next word boundary.
    while (
        next_start < end
        and next_start > 0
        and not text[next_start - 1].isspace()
        and not text[next_start].isspace()
    ):
        next_start += 1

    # Skip whitespace at the beginning.
    while next_start < len(text) and text[next_start].isspace():
        next_start += 1

    return next_start


def chunk_pages(pages, size=None, overlap=None):
    """
    Split PDF pages into overlapping chunks.

    Each chunk retains its original PDF page number.
    Chunk boundaries prefer paragraphs and sentences.
    """

    size = settings.chunk_size if size is None else size

    overlap = (
        settings.chunk_overlap
        if overlap is None
        else overlap
    )

    if size < 100 or overlap < 0 or overlap >= size:
        raise ValueError(
            "Require size >= 100 and 0 <= overlap < size"
        )

    result = []

    for page in pages:

        text = _normalize_text(page.get("text", ""))

        if not text:
            continue

        start = 0

        while start < len(text):

            end = _find_chunk_end(text, start, size)

            part = text[start:end].strip()

            if part:
                result.append({
                    "page": page["page"],
                    "text": part
                })

            if end >= len(text):
                break

            next_start = _find_next_start(
                text,
                end,
                overlap,
                start
            )

            if next_start <= start:
                break

            start = next_start

    return result

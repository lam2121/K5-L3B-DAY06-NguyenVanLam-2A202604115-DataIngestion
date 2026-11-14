"""Implement fixed-size and structure-aware chunking."""
import re
from .models import Chunk, DocumentPage


def fixed_size(page: DocumentPage, size: int, overlap: int) -> list[Chunk]:
    """Split text into overlapping windows and retain page metadata."""
    text = page.text.strip()
    if not text:
        return []

    step = size - overlap
    if step <= 0:
        step = size

    chunks: list[Chunk] = []
    chunk_idx = 0
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + size, text_len)
        chunk_text = text[start:end].strip()

        if chunk_text:
            meta = dict(page.metadata)
            meta["chunk_type"] = "fixed_size"
            meta["char_length"] = len(chunk_text)

            chunks.append(
                Chunk(
                    chunk_id=f"{page.document_id}-p{page.page}-fix{chunk_idx:03d}",
                    document_id=page.document_id,
                    source=page.source,
                    page=page.page,
                    text=chunk_text,
                    metadata=meta
                )
            )
            chunk_idx += 1

        if end >= text_len:
            break
        start += step

    return chunks


def by_paragraph(page: DocumentPage, max_size: int) -> list[Chunk]:
    """Group paragraphs, split oversized paragraphs, and retain metadata."""
    text = page.text.strip()
    if not text:
        return []

    # Split into paragraphs by double newlines or single newlines followed by capital/header
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paragraphs:
        paragraphs = [text]

    chunks: list[Chunk] = []
    chunk_idx = 0
    current_parts: list[str] = []
    current_length = 0

    def flush_current():
        nonlocal chunk_idx, current_parts, current_length
        if not current_parts:
            return
        chunk_text = "\n\n".join(current_parts).strip()
        if chunk_text:
            meta = dict(page.metadata)
            meta["chunk_type"] = "by_paragraph"
            meta["char_length"] = len(chunk_text)
            chunks.append(
                Chunk(
                    chunk_id=f"{page.document_id}-p{page.page}-para{chunk_idx:03d}",
                    document_id=page.document_id,
                    source=page.source,
                    page=page.page,
                    text=chunk_text,
                    metadata=meta
                )
            )
            chunk_idx += 1
        current_parts = []
        current_length = 0

    for para in paragraphs:
        # If single paragraph exceeds max_size, split by sentences
        if len(para) > max_size:
            flush_current()
            sentences = re.split(r"(?<=[.!?])\s+", para)
            sub_parts: list[str] = []
            sub_len = 0
            for sent in sentences:
                sent = sent.strip()
                if not sent:
                    continue
                if sub_len + len(sent) + 1 > max_size and sub_parts:
                    sub_text = " ".join(sub_parts).strip()
                    meta = dict(page.metadata)
                    meta["chunk_type"] = "by_paragraph"
                    meta["char_length"] = len(sub_text)
                    chunks.append(
                        Chunk(
                            chunk_id=f"{page.document_id}-p{page.page}-para{chunk_idx:03d}",
                            document_id=page.document_id,
                            source=page.source,
                            page=page.page,
                            text=sub_text,
                            metadata=meta
                        )
                    )
                    chunk_idx += 1
                    sub_parts = [sent]
                    sub_len = len(sent)
                else:
                    sub_parts.append(sent)
                    sub_len += len(sent) + 1
            if sub_parts:
                sub_text = " ".join(sub_parts).strip()
                meta = dict(page.metadata)
                meta["chunk_type"] = "by_paragraph"
                meta["char_length"] = len(sub_text)
                chunks.append(
                    Chunk(
                        chunk_id=f"{page.document_id}-p{page.page}-para{chunk_idx:03d}",
                        document_id=page.document_id,
                        source=page.source,
                        page=page.page,
                        text=sub_text,
                        metadata=meta
                    )
                )
                chunk_idx += 1
        else:
            # Check if adding this paragraph exceeds max_size
            added_len = len(para) + (2 if current_parts else 0)
            if current_length + added_len > max_size and current_parts:
                flush_current()
            current_parts.append(para)
            current_length += added_len

    flush_current()
    return chunks

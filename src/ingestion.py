"""Read and normalize source data."""
import json
import logging
import re
import unicodedata
from pathlib import Path
from .models import DocumentPage

logger = logging.getLogger(__name__)

CHAPTER_RANGES = [
    (11, 16, 0, "Preface"),
    (17, 42, 1, "Exploring College"),
    (43, 82, 2, "Knowing Yourself as a Learner"),
    (83, 124, 3, "Managing Your Time and Priorities"),
    (125, 160, 4, "Planning Your Academic Pathways"),
    (161, 200, 5, "Reading and Notetaking"),
    (201, 230, 6, "Studying, Memory, and Test Taking"),
    (231, 264, 7, "Thinking"),
    (265, 292, 8, "Communicating"),
    (293, 328, 9, "Understanding Civility and Cultural Competence"),
    (329, 374, 10, "Understanding Financial literacy"),
    (375, 412, 11, "Engaging in a Healthy Lifestyle"),
    (413, 456, 12, "Planning for Your Future"),
    (457, 464, 13, "Appendix: Answer Key"),
    (465, 465, 14, "Index")
]


def get_chapter_metadata(page_num: int) -> dict[str, int | str]:
    for start_p, end_p, ch_num, ch_title in CHAPTER_RANGES:
        if start_p <= page_num <= end_p:
            return {"chapter": ch_num, "chapter_title": ch_title}
    return {"chapter": -1, "chapter_title": "Front Matter"}


def normalize_text(text: str) -> str:
    """Normalize Unicode and whitespace while preserving paragraph breaks."""
    if not text:
        return ""
    # Unicode NFC normalization
    text = unicodedata.normalize("NFC", text)
    # Normalize Windows line breaks
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Replace non-breaking spaces and tabs with standard space
    text = re.sub(r"[\t\u00a0\u200b]", " ", text)
    # Collapse multiple horizontal spaces on the same line
    text = re.sub(r"[ ]{2,}", " ", text)
    # Collapse more than two consecutive newlines into two
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_pdf(path: Path, document_id: str, source: str, start_page: int | None = None, end_page: int | None = None) -> list[DocumentPage]:
    """Extract each physical page; keep page number, source, and chapter metadata.

    Detect and record pages with minimal/no text.
    """
    import pypdf

    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")

    reader = pypdf.PdfReader(str(path))
    total_pages = len(reader.pages)
    pages: list[DocumentPage] = []

    s_page = start_page if start_page is not None else 1
    e_page = end_page if end_page is not None else total_pages

    empty_pages = []

    for page_idx in range(s_page - 1, min(e_page, total_pages)):
        page_num = page_idx + 1
        raw_text = reader.pages[page_idx].extract_text() or ""
        norm_text = normalize_text(raw_text)

        if len(norm_text) < 50:
            empty_pages.append(page_num)

        meta = get_chapter_metadata(page_num)

        pages.append(
            DocumentPage(
                document_id=document_id,
                source=source,
                page=page_num,
                text=norm_text,
                metadata=meta
            )
        )

    if empty_pages:
        logger.info("Found %d blank/minimal text pages: %s", len(empty_pages), empty_pages[:10])

    return pages

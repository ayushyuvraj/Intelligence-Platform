"""
Section text extractor for Income Tax Acts.

Builds a page-level index at startup and extracts section text on demand.
- 1961 Act: scanned from Income_Tax_Act_1961.pdf (880 pages)
- 2025 Act: individual section PDFs in data/pdfs/Income Tax Act 2025/
"""
import re
import glob
from pathlib import Path
from functools import lru_cache
from typing import Optional

import PyPDF2

DATA_DIR = Path(__file__).parent.parent.parent / "data"
PDF_1961 = DATA_DIR / "pdfs" / "Income_Tax_Act_1961.pdf"
PDF_2025_DIR = DATA_DIR / "pdfs" / "Income Tax Act 2025"

# Matches section declarations like:
#   139. Return of income.
#   4[80C.  Deduction in ...
#   115BAC. Tax on income ...
_SEC_RE = re.compile(r'\n\s*(?:\d+\[)?(\d+[A-Z]{0,3})\.\s+[A-Z\[]')


# ─── 1961 Act ────────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _build_index_1961() -> dict[str, int]:
    """Returns {section_number: first_page_index} for the 1961 Act PDF."""
    index: dict[str, int] = {}
    if not PDF_1961.exists():
        return index
    with open(PDF_1961, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for i, page in enumerate(reader.pages):
            if i < 20:  # skip table of contents
                continue
            text = page.extract_text() or ""
            for sec in _SEC_RE.findall(text):
                if sec not in index:
                    index[sec] = i
    return index


def get_section_text_1961(section: str) -> Optional[str]:
    """
    Extract the text of a section from the 1961 Act PDF.
    Returns up to ~3 pages of text starting from the section's first page.
    """
    section = _normalise(section)
    index = _build_index_1961()
    start_page = index.get(section)
    if start_page is None:
        return None

    # Determine the next section's page to know where to stop
    all_pages = sorted(index.values())
    next_pages = [p for p in all_pages if p > start_page]
    end_page = next_pages[0] if next_pages else start_page + 3
    end_page = min(end_page, start_page + 5)  # cap at 5 pages

    with open(PDF_1961, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        chunks = []
        for i in range(start_page, end_page):
            chunks.append(reader.pages[i].extract_text() or "")

    raw = "\n".join(chunks)
    return _clean_text(raw)


def get_all_sections_1961() -> list[str]:
    """Return list of all indexed section numbers in the 1961 Act."""
    return sorted(_build_index_1961().keys(), key=_sort_key)


# ─── 2025 Act ────────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _list_2025_section_files() -> dict[str, Path]:
    """Returns {section_number: pdf_path} for all individual section PDFs."""
    mapping: dict[str, Path] = {}
    if not PDF_2025_DIR.exists():
        return mapping
    for path in PDF_2025_DIR.glob("Section-*_*.pdf"):
        # e.g. Section-123_2026-04-01_05-11-32_e2f4a7_en.pdf
        m = re.match(r"Section-(\d+[A-Z]{0,3})_", path.name)
        if m:
            mapping[m.group(1)] = path
    return mapping


def get_section_text_2025(section: str) -> Optional[str]:
    """Extract text of a section from its individual 2025 Act PDF."""
    section = _normalise(section)
    files = _list_2025_section_files()
    pdf_path = files.get(section)
    if pdf_path is None:
        return None
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        chunks = [page.extract_text() or "" for page in reader.pages]
    return _clean_text("\n".join(chunks))


def get_all_sections_2025() -> list[str]:
    """Return list of all available section numbers in the 2025 Act."""
    return sorted(_list_2025_section_files().keys(), key=_sort_key)


# ─── Shared ───────────────────────────────────────────────────────────────────

def _normalise(sec: str) -> str:
    """Strip whitespace, remove 'Section'/'Sec' prefix, uppercase."""
    sec = sec.strip()
    sec = re.sub(r'^[Ss]ection\s*', '', sec)
    sec = re.sub(r'^[Ss]ec\.\s*', '', sec)
    return sec.upper().strip()


def _clean_text(text: str) -> str:
    """Remove PDF artefacts: page numbers, footnote markers, excess whitespace."""
    lines = text.splitlines()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # Skip bare page-number lines (e.g. "330" or "330 ")
        if re.fullmatch(r'\d{1,4}', stripped):
            continue
        # Skip lines that are only asterisks/footnote markers
        if re.fullmatch(r'[\*\d\[\] ]+', stripped):
            continue
        # Remove inline footnote markers like 1[ or 2[
        stripped = re.sub(r'\b\d{1,2}\[', '', stripped)
        # Normalise multiple spaces
        stripped = re.sub(r'  +', ' ', stripped)
        if stripped:
            cleaned.append(stripped)
    return "\n".join(cleaned).strip()


def _sort_key(sec: str):
    """Sort section numbers numerically then alphabetically: 1, 2, 10, 80, 80A, 80C ..."""
    m = re.match(r'^(\d+)([A-Z]*)', sec)
    if m:
        return (int(m.group(1)), m.group(2))
    return (0, sec)


# ─── Warm-up ─────────────────────────────────────────────────────────────────

def warm_up():
    """Pre-build both indexes at startup so first request is fast."""
    try:
        n1961 = len(_build_index_1961())
        n2025 = len(_list_2025_section_files())
        print(f"[OK] Section extractor: 1961={n1961} sections, 2025={n2025} sections")
    except Exception as e:
        print(f"[WARN] Section extractor warm-up failed: {e}")

from pathlib import Path

from pypdf import PdfReader


def load_pdf(pdf_path: str | Path) -> list[dict]:
    """
    Extract text from a PDF page by page.

    Returns:
        A list of dictionaries containing page number and extracted text.
    """
    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    reader = PdfReader(pdf_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        pages.append(
            {
                "page_number": page_number,
                "text": text,
            }
        )

    return pages
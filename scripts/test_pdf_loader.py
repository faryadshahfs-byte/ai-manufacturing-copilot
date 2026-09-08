import logging
from pathlib import Path

from app.ingestion.pdf_loader import load_pdf

logging.disable(logging.CRITICAL)

PDF_PATH = Path("data/raw/danfoss_vlt_fc302_operating_guide.pdf")

pages = load_pdf(PDF_PATH)

non_empty_pages = [
    page for page in pages
    if page["text"].strip()
]

empty_pages = [
    page for page in pages
    if not page["text"].strip()
]

total_characters = sum(
    len(page["text"])
    for page in pages
)

print("=" * 60)
print("PDF EXTRACTION QUALITY REPORT")
print("=" * 60)

print(f"Total pages: {len(pages)}")
print(f"Pages with text: {len(non_empty_pages)}")
print(f"Empty pages: {len(empty_pages)}")
print(f"Total characters: {total_characters}")

print("\nEmpty page numbers:")

if empty_pages:
    print([page["page_number"] for page in empty_pages])
else:
    print("None")

print("\nFirst 3 non-empty pages:")

for page in non_empty_pages[:3]:
    print("\n" + "=" * 60)
    print(f"PAGE {page['page_number']}")
    print("=" * 60)
    print(page["text"][:500])
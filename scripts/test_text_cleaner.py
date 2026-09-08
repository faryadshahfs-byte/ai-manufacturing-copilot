import logging
import sys
from pathlib import Path

from app.ingestion.pdf_loader import load_pdf
from app.ingestion.text_cleaner import clean_text


logging.disable(logging.CRITICAL)

PDF_PATH = Path("data/raw/danfoss_vlt_fc302_operating_guide.pdf")

pages = load_pdf(PDF_PATH)

print("=" * 60)
print("TEXT CLEANING TEST")
print("=" * 60)

for page in pages[4:7]:
    cleaned = clean_text(page["text"])

    print("\n" + "=" * 60)
    print(f"PAGE {page['page_number']}")
    print("=" * 60)
    print(cleaned[:1500])

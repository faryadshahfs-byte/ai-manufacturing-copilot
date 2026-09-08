from pathlib import Path

from app.ingestion.pdf_loader import load_pdf
from app.ingestion.text_cleaner import clean_text


PDF_PATH = Path("data/raw/danfoss_vlt_fc302_operating_guide.pdf")

pages = load_pdf(PDF_PATH)

print("=" * 70)
print("DOCUMENT STRUCTURE INSPECTION")
print("=" * 70)

for page in pages:
    page_number = page["page_number"]

    if page_number < 9 or page_number > 130:
        continue

    text = clean_text(page["text"])

    lines = text.splitlines()

    print(f"\nPAGE {page_number}")
    print("-" * 70)

    for line in lines:
        stripped = line.strip()

        if not stripped:
            continue

        # Show likely numbered headings only
        if (
            len(stripped) < 120
            and any(
                stripped.startswith(f"{i} ")
                or stripped.startswith(f"{i}.")
                for i in range(1, 11)
            )
        ):
            print(stripped)

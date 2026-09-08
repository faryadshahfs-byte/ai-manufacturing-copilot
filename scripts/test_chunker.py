from pathlib import Path

from app.ingestion.pdf_loader import load_pdf
from app.ingestion.text_cleaner import clean_text
from app.ingestion.chunker import chunk_pages


PDF_PATH = Path("data/raw/danfoss_vlt_fc302_operating_guide.pdf")


pages = load_pdf(PDF_PATH)

cleaned_pages = [
    {
        "page_number": page["page_number"],
        "text": clean_text(page["text"]),
    }
    for page in pages
]


chunks = chunk_pages(
    cleaned_pages,
    source=PDF_PATH.name,
    chunk_size=1200,
    chunk_overlap=200,
)


print("=" * 70)
print("ENGINEERING-AWARE CHUNKING TEST")
print("=" * 70)

print(f"Pages: {len(cleaned_pages)}")
print(f"Chunks: {len(chunks)}")

print("\nFirst 5 chunks:")

for chunk in chunks[:5]:
    print("\n" + "=" * 70)
    print(f"Chunk ID:    {chunk['chunk_id']}")
    print(f"Source:      {chunk['source']}")
    print(f"Page:        {chunk['page_number']}")
    print(f"Section:     {chunk['section']}")
    print(f"Subsection:  {chunk['subsection']}")
    print("=" * 70)
    print(chunk["text"][:1000])

import json
from pathlib import Path
from collections import Counter

from app.ingestion.pdf_loader import load_pdf
from app.ingestion.text_cleaner import clean_text
from app.ingestion.chunker import chunk_pages


PDF_PATH = Path("data/raw/danfoss_vlt_fc302_operating_guide.pdf")
OUTPUT_PATH = Path("data/knowledge_base/knowledge_base.json")


def build_knowledge_base():
    print("=" * 70)
    print("BUILDING KNOWLEDGE BASE")
    print("=" * 70)

    print(f"Source: {PDF_PATH}")

    # ---------------------------------------------------------
    # 1. Load PDF
    # ---------------------------------------------------------
    print("\n[1/4] Loading PDF...")

    pages = load_pdf(PDF_PATH)

    print(f"Pages: {len(pages)}")

    # ---------------------------------------------------------
    # 2. Clean extracted text
    # ---------------------------------------------------------
    print("\n[2/4] Cleaning text...")

    cleaned_pages = []

    for page in pages:
        cleaned_text = clean_text(page.get("text", ""))

        cleaned_pages.append(
            {
                "page_number": page["page_number"],
                "text": cleaned_text,
            }
        )

    pages_with_text = sum(
        1 for page in cleaned_pages if page["text"].strip()
    )

    print(f"Pages containing text: {pages_with_text}")

    # ---------------------------------------------------------
    # 3. Create chunks
    # ---------------------------------------------------------
    print("\n[3/4] Creating chunks...")

    chunks = chunk_pages(
        cleaned_pages,
        chunk_size=1200,
        overlap=200,
    )

    print(f"Chunks created: {len(chunks)}")

    # ---------------------------------------------------------
    # 4. Validate and save
    # ---------------------------------------------------------
    print("\n[4/4] Validating and saving...")

    empty_chunks = [
        chunk
        for chunk in chunks
        if not chunk.get("text", "").strip()
    ]

    missing_section_chunks = [
        chunk
        for chunk in chunks
        if not chunk.get("section")
    ]

    print(f"Empty chunks: {len(empty_chunks)}")
    print(
        f"Chunks without section metadata: "
        f"{len(missing_section_chunks)}"
    )

    # Section distribution
    section_counts = Counter(
        chunk.get("section")
        for chunk in chunks
    )

    print("\nSection distribution:")

    for section, count in section_counts.items():
        print(f"  {section}: {count}")

    # ---------------------------------------------------------
    # Check suspicious numeric subsections
    # ---------------------------------------------------------
    suspicious_subsections = [
        chunk
        for chunk in chunks
        if chunk.get("subsection")
        and (
            chunk["subsection"].startswith("0.")
            or chunk["subsection"].startswith("00.")
        )
    ]

    print(
        f"\nSuspicious numeric subsections: "
        f"{len(suspicious_subsections)}"
    )

    for chunk in suspicious_subsections[:20]:
        print(
            f"  {chunk['chunk_id']} | "
            f"page {chunk['page_start']} | "
            f"{chunk['subsection']}"
        )

    # ---------------------------------------------------------
    # Hard validation
    # ---------------------------------------------------------
    if empty_chunks:
        raise ValueError(
            f"Knowledge base contains {len(empty_chunks)} "
            f"empty chunks."
        )

    if missing_section_chunks:
        raise ValueError(
            f"{len(missing_section_chunks)} chunks "
            f"are missing section metadata."
        )

    if suspicious_subsections:
        raise ValueError(
            "Suspicious numeric subsections detected. "
            "Chunk hierarchy is still incorrect."
        )

    # ---------------------------------------------------------
    # Save output
    # ---------------------------------------------------------
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    knowledge_base = {
        "source": str(PDF_PATH),
        "pages": len(pages),
        "pages_with_text": pages_with_text,
        "chunk_count": len(chunks),
        "chunk_size": 1200,
        "chunk_overlap": 200,
        "chunks": chunks,
    }

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            knowledge_base,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print("\nKnowledge base saved:")
    print(OUTPUT_PATH)

    print("\n" + "=" * 70)
    print("KNOWLEDGE BASE BUILD COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    build_knowledge_base()

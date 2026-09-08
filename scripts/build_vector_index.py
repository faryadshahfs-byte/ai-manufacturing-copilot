import json
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer


KB_PATH = Path("data/knowledge_base/knowledge_base.json")
INDEX_PATH = Path("data/knowledge_base/faiss.index")
META_PATH = Path("data/knowledge_base/faiss_metadata.json")

MODEL_NAME = "all-MiniLM-L6-v2"


def build_vector_index():
    print("=" * 70)
    print("BUILDING SEMANTIC VECTOR INDEX")
    print("=" * 70)

    if not KB_PATH.exists():
        raise FileNotFoundError(
            f"Knowledge base not found: {KB_PATH}"
        )

    with KB_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    chunks = data["chunks"]

    if not chunks:
        raise ValueError("Knowledge base contains no chunks.")

    print(f"Chunks: {len(chunks)}")
    print(f"Embedding model: {MODEL_NAME}")

    print("\n[1/3] Loading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    print("[2/3] Creating embeddings...")

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    print(f"Embedding shape: {embeddings.shape}")

    print("[3/3] Building FAISS index...")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    INDEX_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    faiss.write_index(
        index,
        str(INDEX_PATH),
    )

    metadata = {
        "model_name": MODEL_NAME,
        "dimension": dimension,
        "chunk_count": len(chunks),
        "chunks": chunks,
    }

    with META_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metadata,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print("\nVector index saved:")
    print(INDEX_PATH)

    print("Metadata saved:")
    print(META_PATH)

    print("\n" + "=" * 70)
    print("VECTOR INDEX BUILD COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    build_vector_index()

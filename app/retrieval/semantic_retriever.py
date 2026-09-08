import json
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer


INDEX_PATH = Path("data/knowledge_base/faiss.index")
META_PATH = Path("data/knowledge_base/faiss_metadata.json")


class SemanticRetriever:
    def __init__(self):
        if not INDEX_PATH.exists():
            raise FileNotFoundError(
                f"FAISS index not found: {INDEX_PATH}"
            )

        if not META_PATH.exists():
            raise FileNotFoundError(
                f"FAISS metadata not found: {META_PATH}"
            )

        self.index = faiss.read_index(
            str(INDEX_PATH)
        )

        with META_PATH.open(
            "r",
            encoding="utf-8",
        ) as file:
            metadata = json.load(file)

        self.model_name = metadata["model_name"]
        self.chunks = metadata["chunks"]

        self.model = SentenceTransformer(
            self.model_name
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:

        if not query.strip():
            return []

        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True,
        )

        scores, indices = self.index.search(
            query_embedding,
            top_k,
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0],
        ):

            if index < 0:
                continue

            chunk = self.chunks[index]

            results.append(
                {
                    "score": float(score),
                    "chunk": chunk,
                }
            )

        return results

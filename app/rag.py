from app.llm.client import LLMClient
from app.llm.prompt import build_prompt
from app.retrieval.hybrid_retriever import HybridRetriever


class RAGService:

    def __init__(self):
        self.retriever = HybridRetriever()
        self.llm = LLMClient()

    def ask(
        self,
        query: str,
        top_k: int = 5,
    ) -> dict:

        if not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        retrieved = self.retriever.retrieve(
            query,
            top_k=top_k,
        )

        if not retrieved:
            return {
                "answer": (
                    "No relevant documentation "
                    "was found for this question."
                ),
                "sources": [],
            }

        prompt = build_prompt(
            query,
            retrieved,
        )

        answer = self.llm.generate(prompt)

        sources = []

        for item in retrieved:

            chunk = item["chunk"]

            sources.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "source": chunk.get("source"),
                    "page_start": chunk.get("page_start"),
                    "page_end": chunk.get("page_end"),
                    "section": chunk.get("section"),
                    "subsection": chunk.get("subsection"),
                    "subsubsection": chunk.get(
                        "subsubsection"
                    ),
                    "keyword_rank": item.get(
                        "keyword_rank"
                    ),
                    "semantic_rank": item.get(
                        "semantic_rank"
                    ),
                    "rrf_score": item.get(
                        "rrf_score"
                    ),
                }
            )

        return {
            "query": query,
            "answer": answer,
            "sources": sources,
        }

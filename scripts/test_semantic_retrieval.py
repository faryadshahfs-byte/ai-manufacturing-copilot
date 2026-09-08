from app.retrieval.semantic_retriever import SemanticRetriever

retriever = SemanticRetriever()

results = retriever.retrieve(
    "The drive reports Warning 1 because the 10 V supply is overloaded",
    top_k=5,
)

for rank, result in enumerate(results, start=1):
    chunk = result["chunk"]

    print(
        f"{rank}. "
        f"{result['score']:.4f} | "
        f"{chunk['chunk_id']} | "
        f"{chunk.get('subsection')}"
    )

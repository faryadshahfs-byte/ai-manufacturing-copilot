from app.retrieval.hybrid_retriever import HybridRetriever

retriever = HybridRetriever()

queries = [
    "What is the cause and troubleshooting procedure for Warning 1, 10 Volts Low?",
    "How do I remove dust buildup from the heat sink?",
    "What does an alarm indicate and what happens after an alarm?",
    "What safety precautions should be followed before servicing the drive?",
    "What should be checked during maintenance to help prevent breakdown?",
]

for query in queries:
    print("\n" + "=" * 70)
    print(query)
    print("=" * 70)

    results = retriever.retrieve(
        query,
        top_k=5,
    )

    for rank, result in enumerate(results, start=1):
        chunk = result["chunk"]

        print(
            f"{rank}. "
            f"{chunk['chunk_id']} | "
            f"RRF={result['rrf_score']:.5f} | "
            f"K={result['keyword_rank']} | "
            f"S={result['semantic_rank']} | "
            f"{chunk.get('subsection')}"
        )

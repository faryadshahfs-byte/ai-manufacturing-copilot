from scripts.retrieval_eval import EVALUATION_QUERIES
from app.retrieval.semantic_retriever import SemanticRetriever


def chunk_matches_expected(chunk, evaluation):
    text = " ".join(
        [
            chunk.get("text", ""),
            chunk.get("section") or "",
            chunk.get("subsection") or "",
            chunk.get("subsubsection") or "",
        ]
    ).lower()

    expected = [
        value.lower()
        for value in evaluation.get(
            "expected_chunk_contains",
            [],
        )
    ]

    return any(
        phrase in text
        for phrase in expected
    )


def main():
    retriever = SemanticRetriever()

    recall_at_1 = []
    recall_at_3 = []
    reciprocal_ranks = []

    print("=" * 70)
    print("SEMANTIC RETRIEVAL EVALUATION")
    print("=" * 70)

    for evaluation in EVALUATION_QUERIES:
        query = evaluation["query"]

        results = retriever.retrieve(
            query,
            top_k=5,
        )

        first_rank = 0

        for rank, result in enumerate(
            results,
            start=1,
        ):
            if chunk_matches_expected(
                result["chunk"],
                evaluation,
            ):
                first_rank = rank
                break

        r1 = 1 if first_rank == 1 else 0
        r3 = 1 if 1 <= first_rank <= 3 else 0

        rr = (
            1.0 / first_rank
            if first_rank
            else 0.0
        )

        recall_at_1.append(r1)
        recall_at_3.append(r3)
        reciprocal_ranks.append(rr)

        print("\n" + "-" * 70)
        print(
            f"{evaluation['id']}: {query}"
        )

        print(
            "Relevant rank: "
            f"{first_rank if first_rank else 'NOT FOUND'}"
        )

        print(
            f"Recall@1: {r1}"
        )

        print(
            f"Recall@3: {r3}"
        )

        print(
            f"MRR contribution: {rr:.3f}"
        )

        print("\nTop results:")

        for rank, result in enumerate(
            results,
            start=1,
        ):
            chunk = result["chunk"]

            print(
                f"{rank}. "
                f"{result['score']:.4f} | "
                f"{chunk['chunk_id']} | "
                f"{chunk.get('subsection')}"
            )

    avg_r1 = sum(recall_at_1) / len(
        recall_at_1
    )

    avg_r3 = sum(recall_at_3) / len(
        recall_at_3
    )

    avg_mrr = sum(reciprocal_ranks) / len(
        reciprocal_ranks
    )

    print("\n" + "=" * 70)
    print("SEMANTIC EVALUATION SUMMARY")
    print("=" * 70)

    print(
        f"Recall@1: "
        f"{avg_r1 * 100:.2f}%"
    )

    print(
        f"Recall@3: "
        f"{avg_r3 * 100:.2f}%"
    )

    print(
        f"MRR: "
        f"{avg_mrr:.3f}"
    )

    print("=" * 70)


if __name__ == "__main__":
    main()

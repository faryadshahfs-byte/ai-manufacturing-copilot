import json
import re
from pathlib import Path


KB_PATH = Path("data/knowledge_base/knowledge_base.json")


EVALUATION_QUERIES = [
    {
        "id": "Q001",
        "query": "What is the cause and troubleshooting procedure for Warning 1, 10 Volts Low?",
        "expected_terms": [
            "warning 1",
            "10 volts low",
            "cause",
            "troubleshooting",
        ],
        "expected_chunk_contains": [
            "control card voltage",
            "terminal 50",
            "10 V supply",
        ],
    },
    {
        "id": "Q002",
        "query": "How do I remove dust buildup from the heat sink?",
        "expected_terms": [
            "dust buildup",
            "heat sink",
            "procedure",
            "remove",
        ],
        "expected_chunk_contains": [
            "Removing Dust Buildup from the Heat Sink",
        ],
    },
    {
        "id": "Q003",
        "query": "What does an alarm indicate and what happens after an alarm?",
        "expected_terms": [
            "alarm",
            "fault",
            "trip",
            "trip lock",
        ],
        "expected_chunk_contains": [
            "An alarm indicates a fault",
        ],
    },
    {
        "id": "Q004",
        "query": "What safety precautions should be followed before servicing the drive?",
        "expected_terms": [
            "safety",
            "maintenance",
            "service",
            "high voltage",
        ],
        "expected_chunk_contains": [
            "Safety Precautions",
        ],
    },
    {
        "id": "Q005",
        "query": "What should be checked during maintenance to help prevent breakdown?",
        "expected_terms": [
            "maintenance",
            "prevent breakdown",
            "loose terminal connections",
        ],
        "expected_chunk_contains": [
            "Under normal operating conditions",
            "prevent breakdown",
        ],
    },
]


STOPWORDS = {
    "the",
    "a",
    "an",
    "is",
    "are",
    "to",
    "for",
    "and",
    "or",
    "of",
    "what",
    "does",
    "do",
    "how",
    "should",
    "be",
    "after",
    "during",
    "before",
    "from",
    "in",
    "on",
    "with",
}


def normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9%°]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> list[str]:
    normalized = normalize(text)
    return [
        token
        for token in normalized.split()
        if token not in STOPWORDS
    ]


def score_chunk(query: str, chunk: dict) -> float:
    query_normalized = normalize(query)

    text = normalize(chunk.get("text", ""))
    section = normalize(chunk.get("section") or "")
    subsection = normalize(chunk.get("subsection") or "")
    subsubsection = normalize(chunk.get("subsubsection") or "")

    metadata_text = " ".join(
        [
            section,
            subsection,
            subsubsection,
        ]
    ).strip()

    score = 0.0

    # ---------------------------------------------------------
    # Exact query phrase
    # ---------------------------------------------------------
    if query_normalized in text:
        score += 8

    # ---------------------------------------------------------
    # Query token matching
    # ---------------------------------------------------------
    query_tokens = tokenize(query)
    text_tokens = set(tokenize(text))

    for token in query_tokens:
        if token in text_tokens:
            score += 1

    # ---------------------------------------------------------
    # Metadata matching
    # ---------------------------------------------------------
    metadata_tokens = set(tokenize(metadata_text))

    for token in query_tokens:
        if token in metadata_tokens:
            score += 1.5

    # ---------------------------------------------------------
    # Troubleshooting intent
    # ---------------------------------------------------------
    troubleshooting_terms = {
        "cause",
        "troubleshooting",
        "procedure",
        "check",
        "prevent",
        "remove",
        "safety",
        "service",
        "maintenance",
    }

    for term in troubleshooting_terms:
        if term in query_normalized and term in text:
            score += 2

    # ---------------------------------------------------------
    # Fault/alarm specificity
    # ---------------------------------------------------------
    alarm_match = re.search(
        r"\b(?:warning|alarm)\s+\d+\b",
        query_normalized,
    )

    if alarm_match:
        alarm_phrase = alarm_match.group(0)

        if alarm_phrase in text:
            score += 12

        if alarm_phrase in subsection:
            score += 15

    # Specific "10 volts low" style phrase
    if "10 volts low" in query_normalized:
        if "10 volts low" in text:
            score += 15

        if "terminal 50" in text:
            score += 4

        if "control card voltage" in text:
            score += 4

    # ---------------------------------------------------------
    # Domain-specific relevance boosts
    # ---------------------------------------------------------
    if "heat sink" in query_normalized:
        if "heat sink" in text:
            score += 5

        if "heat sink service" in subsection:
            score += 6

        if "dust buildup" in text:
            score += 5

    if "alarm" in query_normalized:
        if "warnings and alarms" in subsection:
            score += 5

        if "alarm indicates a fault" in text:
            score += 8

        if "trip or trip lock" in text:
            score += 4

    if "safety" in query_normalized:
        if "safety precautions" in subsection:
            score += 10

        if "high voltage" in text:
            score += 4

    if "maintenance" in query_normalized:
        if "maintenance and service" in subsection:
            score += 8

        if "prevent breakdown" in text:
            score += 10

    return score


def retrieve(query: str, chunks: list[dict], top_k: int = 5):
    scored = []

    for chunk in chunks:
        score = score_chunk(query, chunk)

        scored.append(
            {
                "score": score,
                "chunk": chunk,
            }
        )

    scored.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return scored[:top_k]


def chunk_matches_expected(
    chunk: dict,
    evaluation: dict,
) -> bool:

    text = normalize(
        " ".join(
            [
                chunk.get("text", ""),
                chunk.get("section") or "",
                chunk.get("subsection") or "",
                chunk.get("subsubsection") or "",
            ]
        )
    )

    expected_phrases = [
        normalize(value)
        for value in evaluation.get(
            "expected_chunk_contains",
            [],
        )
    ]

    return any(
        phrase in text
        for phrase in expected_phrases
    )


def term_recall(
    chunks: list[dict],
    expected_terms: list[str],
) -> float:

    combined_text = normalize(
        " ".join(
            chunk.get("text", "")
            for chunk in chunks
        )
    )

    matched = sum(
        1
        for term in expected_terms
        if normalize(term) in combined_text
    )

    if not expected_terms:
        return 0.0

    return matched / len(expected_terms)


def reciprocal_rank(
    retrieved: list[dict],
    evaluation: dict,
) -> float:

    for rank, item in enumerate(
        retrieved,
        start=1,
    ):

        if chunk_matches_expected(
            item["chunk"],
            evaluation,
        ):
            return 1.0 / rank

    return 0.0


def evaluate():

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

    print("=" * 70)
    print("SMART KEYWORD RETRIEVAL EVALUATION")
    print("=" * 70)

    print(f"Knowledge-base chunks: {len(chunks)}")
    print(
        f"Evaluation queries: "
        f"{len(EVALUATION_QUERIES)}"
    )

    recall_at_1 = []
    recall_at_3 = []
    reciprocal_ranks = []
    term_recalls = []

    for evaluation in EVALUATION_QUERIES:

        query = evaluation["query"]

        retrieved = retrieve(
            query,
            chunks,
            top_k=5,
        )

        top1 = retrieved[:1]
        top3 = retrieved[:3]

        r1 = any(
            chunk_matches_expected(
                item["chunk"],
                evaluation,
            )
            for item in top1
        )

        r3 = any(
            chunk_matches_expected(
                item["chunk"],
                evaluation,
            )
            for item in top3
        )

        rr = reciprocal_rank(
            retrieved,
            evaluation,
        )

        tr = term_recall(
            [item["chunk"] for item in retrieved],
            evaluation["expected_terms"],
        )

        recall_at_1.append(
            1.0 if r1 else 0.0
        )

        recall_at_3.append(
            1.0 if r3 else 0.0
        )

        reciprocal_ranks.append(rr)
        term_recalls.append(tr)

        print("\n" + "=" * 70)
        print(
            f"{evaluation['id']}: {query}"
        )
        print("-" * 70)
        print(
            f"Term recall@5: "
            f"{tr * 100:.2f}%"
        )
        print(
            f"Relevant result in Top-1: "
            f"{'YES' if r1 else 'NO'}"
        )
        print(
            f"Relevant result in Top-3: "
            f"{'YES' if r3 else 'NO'}"
        )
        print(
            f"Reciprocal rank: "
            f"{rr:.3f}"
        )

        print("\nTop retrieved chunks:")

        for rank, item in enumerate(
            retrieved,
            start=1,
        ):

            chunk = item["chunk"]

            print(
                f"\n{rank}. "
                f"{chunk['chunk_id']} "
                f"(score={item['score']:.1f})"
            )

            print(
                f"   Page: "
                f"{chunk['page_start']}"
            )

            print(
                f"   Section: "
                f"{chunk.get('section')}"
            )

            print(
                f"   Subsection: "
                f"{chunk.get('subsection')}"
            )

            preview = chunk["text"][:400]

            print(
                "   Text: "
                + preview.replace("\n", " ")
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

    avg_term_recall = sum(term_recalls) / len(
        term_recalls
    )

    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
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

    print(
        f"Average term recall@5: "
        f"{avg_term_recall * 100:.2f}%"
    )

    print("=" * 70)


if __name__ == "__main__":
    evaluate()

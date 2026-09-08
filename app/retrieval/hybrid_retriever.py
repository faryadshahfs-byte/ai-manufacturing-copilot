from __future__ import annotations

import json
import re
from pathlib import Path

from app.retrieval.semantic_retriever import SemanticRetriever


KB_PATH = Path("data/knowledge_base/knowledge_base.json")


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
    """
    Domain-aware keyword score.

    This mirrors the validated keyword retrieval logic used
    in scripts/retrieval_eval.py.
    """
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

    # Exact query phrase
    if query_normalized in text:
        score += 8

    # Query token matching
    query_tokens = tokenize(query)
    text_tokens = set(tokenize(text))

    for token in query_tokens:
        if token in text_tokens:
            score += 1

    # Metadata matching
    metadata_tokens = set(tokenize(metadata_text))

    for token in query_tokens:
        if token in metadata_tokens:
            score += 1.5

    # Troubleshooting intent
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

    # Fault/alarm specificity
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

    # 10 Volts Low specificity
    if "10 volts low" in query_normalized:
        if "10 volts low" in text:
            score += 15

        if "terminal 50" in text:
            score += 4

        if "control card voltage" in text:
            score += 4

    # Heat sink
    if "heat sink" in query_normalized:
        if "heat sink" in text:
            score += 5

        if "heat sink service" in subsection:
            score += 6

        if "dust buildup" in text:
            score += 5

    # Alarm
    if "alarm" in query_normalized:
        if "warnings and alarms" in subsection:
            score += 5

        if "alarm indicates a fault" in text:
            score += 8

        if "trip or trip lock" in text:
            score += 4

    # Safety
    if "safety" in query_normalized:
        if "safety precautions" in subsection:
            score += 10

        if "high voltage" in text:
            score += 4

    # Maintenance
    if "maintenance" in query_normalized:
        if "maintenance and service" in subsection:
            score += 8

        if "prevent breakdown" in text:
            score += 10

    return score


class HybridRetriever:
    """
    Hybrid retrieval using:

    1. Domain-aware keyword retrieval
    2. Semantic retrieval
    3. Weighted Reciprocal Rank Fusion
    4. Small quality adjustment for heading-only chunks
    """

    def __init__(
        self,
        rrf_k: int = 60,
        keyword_weight: float = 4.0,
        semantic_weight: float = 1.0,
    ):
        if not KB_PATH.exists():
            raise FileNotFoundError(
                f"Knowledge base not found: {KB_PATH}"
            )

        with KB_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)

        self.chunks = data["chunks"]
        self.semantic = SemanticRetriever()

        self.rrf_k = rrf_k
        self.keyword_weight = keyword_weight
        self.semantic_weight = semantic_weight

    @staticmethod
    def _quality_adjustment(chunk: dict) -> float:
        """
        Prevent heading-only chunks from outranking useful content.
        """
        text = (chunk.get("text") or "").strip()

        # Very short chunks are usually structural headings.
        if len(text) < 120:
            return -0.005

        return 0.0

    def _keyword_retrieve(
        self,
        query: str,
        top_k: int,
    ) -> list[dict]:

        scored = []

        for chunk in self.chunks:
            score = score_chunk(query, chunk)

            scored.append(
                {
                    "score": score,
                    "chunk": chunk,
                }
            )

        scored.sort(
            key=lambda item: (
                item["score"],
                len(item["chunk"].get("text", "")),
            ),
            reverse=True,
        )

        return scored[:top_k]

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict]:

        if not query.strip():
            return []

        candidate_k = max(20, top_k * 4)

        keyword_results = self._keyword_retrieve(
            query,
            candidate_k,
        )

        semantic_results = self.semantic.retrieve(
            query,
            top_k=candidate_k,
        )

        fused = {}

        # -----------------------------
        # Keyword results
        # -----------------------------
        for rank, item in enumerate(
            keyword_results,
            start=1,
        ):
            chunk = item["chunk"]
            chunk_id = chunk["chunk_id"]

            if chunk_id not in fused:
                fused[chunk_id] = {
                    "chunk": chunk,
                    "keyword_rank": None,
                    "semantic_rank": None,
                    "rrf_score": 0.0,
                }

            fused[chunk_id]["keyword_rank"] = rank

            fused[chunk_id]["rrf_score"] += (
                self.keyword_weight
                / (self.rrf_k + rank)
            )

        # -----------------------------
        # Semantic results
        # -----------------------------
        for rank, item in enumerate(
            semantic_results,
            start=1,
        ):
            chunk = item["chunk"]
            chunk_id = chunk["chunk_id"]

            if chunk_id not in fused:
                fused[chunk_id] = {
                    "chunk": chunk,
                    "keyword_rank": None,
                    "semantic_rank": None,
                    "rrf_score": 0.0,
                }

            fused[chunk_id]["semantic_rank"] = rank

            fused[chunk_id]["rrf_score"] += (
                self.semantic_weight
                / (self.rrf_k + rank)
            )

        # -----------------------------
        # Quality adjustment
        # -----------------------------
        for item in fused.values():
            adjustment = self._quality_adjustment(
                item["chunk"]
            )

            item["quality_adjustment"] = adjustment

            item["final_score"] = (
                item["rrf_score"]
                + adjustment
            )

        ranked = sorted(
            fused.values(),
            key=lambda item: item["final_score"],
            reverse=True,
        )

        return ranked[:top_k]

from app.rag import RAGService


def main():

    service = RAGService()

    query = (
        "What is the cause and troubleshooting "
        "procedure for Warning 1, 10 Volts Low?"
    )

    result = service.ask(
        query,
        top_k=5,
    )

    print("=" * 70)
    print("RAG ANSWER")
    print("=" * 70)

    print(result["answer"])

    print("\n" + "=" * 70)
    print("SOURCES")
    print("=" * 70)

    for source in result["sources"]:

        print(
            f"{source['chunk_id']} | "
            f"Pages {source['page_start']}"
            f"-{source['page_end']} | "
            f"{source['section']} | "
            f"{source['subsection']} | "
            f"RRF={source['rrf_score']:.5f}"
        )


if __name__ == "__main__":
    main()

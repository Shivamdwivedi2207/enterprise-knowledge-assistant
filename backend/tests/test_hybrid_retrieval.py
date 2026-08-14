from app.services.retrieval_service import RetrievalService


OWNER_ID = "296c8dd6-adca-4c29-83cf-f6a5951b9e21"

retrieval_service = RetrievalService()

results = retrieval_service.retrieve(
    query="What tools and frameworks does Shivam know?",
    owner_id=OWNER_ID,
    top_k=5,
    initial_fetch=20,
    rerank_candidates=12,
    max_chunks_per_document=3,
)

print("=" * 70)
print("HYBRID RETRIEVAL WITH RERANKING")
print("=" * 70)
print(f"Results found: {len(results)}")

for index, result in enumerate(
    results,
    start=1,
):
    print("\n" + "=" * 70)
    print("Rank:", index)
    print("File:", result.get("filename"))
    print("Chunk:", result.get("chunk_index"))
    print("Document ID:", result.get("document_id"))
    print("Reranker score:", result.get("reranker_score"))
    print("RRF score:", result.get("rrf_score"))
    print(
        "Retrieval sources:",
        result.get("retrieval_sources"),
    )
    print("Distance:", result.get("distance"))
    print("BM25 score:", result.get("bm25_score"))
    print("\nText:")
    print(
        result.get(
            "text",
            "",
        )[:500]
    )
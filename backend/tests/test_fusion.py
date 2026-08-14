from app.services.fusion_service import FusionService


semantic_results = [
    {
        "id": "chunk-1",
        "text": "FastAPI backend development",
        "filename": "resume.pdf",
        "chunk_index": 1,
        "document_id": "doc-1",
        "distance": 0.20,
    },
    {
        "id": "chunk-2",
        "text": "Machine learning project",
        "filename": "resume.pdf",
        "chunk_index": 2,
        "document_id": "doc-1",
        "distance": 0.30,
    },
]

keyword_results = [
    {
        "id": "chunk-1",
        "text": "FastAPI backend development",
        "filename": "resume.pdf",
        "chunk_index": 1,
        "document_id": "doc-1",
        "bm25_score": 2.8,
    },
    {
        "id": "chunk-3",
        "text": "FastAPI authentication system",
        "filename": "project.pdf",
        "chunk_index": 0,
        "document_id": "doc-2",
        "bm25_score": 2.1,
    },
]


results = FusionService.reciprocal_rank_fusion(
    semantic_results=semantic_results,
    keyword_results=keyword_results,
    top_k=5,
)

for result in results:
    print("=" * 70)
    print("ID:", result.get("id"))
    print("File:", result.get("filename"))
    print("RRF score:", result.get("rrf_score"))
    print(
        "Sources:",
        result.get("retrieval_sources"),
    )
    print("Text:", result.get("text"))
from app.services.reranker_service import RerankerService


reranker = RerankerService()

query = "What tools and frameworks does Shivam know?"

candidates = [
    {
        "id": "chunk-1",
        "filename": "resume.pdf",
        "chunk_index": 1,
        "document_id": "doc-1",
        "text": (
            "Frameworks: TensorFlow and Scikit-learn. "
            "Tools: Git, GitHub, Jupyter Notebook, "
            "Streamlit and FastAPI."
        ),
    },
    {
        "id": "chunk-2",
        "filename": "registration.pdf",
        "chunk_index": 0,
        "document_id": "doc-2",
        "text": (
            "Registration form for semester seven. "
            "The student is enrolled in B.Tech CSE AI and ML."
        ),
    },
    {
        "id": "chunk-3",
        "filename": "resume.pdf",
        "chunk_index": 3,
        "document_id": "doc-1",
        "text": (
            "Education: B.Tech in Computer Science Engineering "
            "with specialization in Artificial Intelligence "
            "and Machine Learning."
        ),
    },
]

results = reranker.rerank(
    query=query,
    candidates=candidates,
    top_k=3,
)

print("=" * 70)
print("CROSS-ENCODER RERANKING RESULTS")
print("=" * 70)

for index, result in enumerate(
    results,
    start=1,
):
    print("\n" + "=" * 70)
    print("Rank:", index)
    print("File:", result["filename"])
    print("Chunk:", result["chunk_index"])
    print("Reranker score:", result["reranker_score"])
    print("Text:", result["text"])
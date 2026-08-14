from app.services.embedding_service import EmbeddingService

embedding_service = EmbeddingService()

embedding = embedding_service.embed_query(
    "What is Artificial Intelligence?"
)

print(f"Embedding Dimension: {len(embedding)}")
print(embedding[:10])
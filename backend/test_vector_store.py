from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService

embedding_service = EmbeddingService()
vector_store = VectorStoreService()

text = "Artificial Intelligence is transforming healthcare."

embedding = embedding_service.embed_query(text)

vector_store.add_documents(
    ids=["test-1"],
    documents=[text],
    embeddings=[embedding],
    metadatas=[
        {
            "document_id": "demo",
            "chunk_index": 0,
        }
    ],
)

print("Stored Successfully!")

result = vector_store.similarity_search(
    embedding,
    n_results=1,
)

print(result["documents"][0][0])
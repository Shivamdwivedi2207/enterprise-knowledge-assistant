from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService


class RetrievalService:
    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreService()

    def retrieve(
        self,
        query: str,
        owner_id: str,
        top_k: int = 5,
    ) -> list[str]:
        """
        Retrieve the most relevant chunks for a user's query.
        """

        query_embedding = self.embedding_service.embed_query(query)

        results = self.vector_store.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"owner_id": owner_id},
        )

        documents = results.get("documents", [])

        if not documents:
            return []

        return documents[0]
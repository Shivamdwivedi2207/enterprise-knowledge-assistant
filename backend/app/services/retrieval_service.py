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
    ):
        """
        Retrieve relevant chunks along with their metadata.
        """

        query_embedding = self.embedding_service.embed_query(query)

        results = self.vector_store.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where={"owner_id": owner_id},
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        retrieved_chunks = []

        for doc, meta in zip(documents, metadatas):
            retrieved_chunks.append(
                {
                    "text": doc,
                    "filename": meta.get("filename", "Unknown"),
                    "chunk_index": meta.get("chunk_index", -1),
                    "document_id": meta.get("document_id"),
                }
            )

        return retrieved_chunks
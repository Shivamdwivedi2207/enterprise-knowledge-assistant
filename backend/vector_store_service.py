from chromadb import PersistentClient


class VectorStoreService:
    def __init__(self):
        self.client = PersistentClient(
            path="storage/chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="documents"
        )

    def add_documents(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
    ) -> None:
        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def similarity_search(
        self,
        query_embedding: list[float],
        n_results: int = 5,
    ):
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )

    def delete_document(self, document_id: str):
        self.collection.delete(
            where={"document_id": document_id}
        )
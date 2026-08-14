from chromadb import PersistentClient

from app.core.config import settings


class VectorRepository:

    def __init__(self):
        self.client = PersistentClient(
            path=settings.CHROMA_DB_PATH
        )

        self.collection = self.client.get_collection(
            settings.CHROMA_COLLECTION_NAME
        )

    def get_chunk(
        self,
        document_id: str,
        chunk_index: int,
    ):
        result = self.collection.get(
            where={
                "$and": [
                    {
                        "document_id": document_id,
                    },
                    {
                        "chunk_index": chunk_index,
                    },
                ]
            }
        )

        if not result["documents"]:
            return None

        return {
            "text": result["documents"][0],
            "metadata": result["metadatas"][0],
        }
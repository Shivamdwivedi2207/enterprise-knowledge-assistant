from chromadb import PersistentClient


class VectorStore:

    def __init__(self):
        self.client = PersistentClient(
            path="storage/chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="documents"
        )
from chromadb import PersistentClient

from app.core.config import settings


class VectorStoreService:
    """
    Service responsible for all ChromaDB operations.

    ChromaDB is used as the single source of truth for:
    - document chunks
    - embeddings
    - document metadata
    - BM25 index construction
    """

    def __init__(self) -> None:
        self.client = PersistentClient(
            path=settings.CHROMA_DB_PATH,
        )

        self.collection = self.client.get_or_create_collection(
            name="documents",
        )

    def add_documents(
        self,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
    ) -> None:
        """
        Add document chunks, embeddings and metadata
        to the ChromaDB collection.
        """

        if not ids:
            return

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def similarity_search(
        self,
        query_embedding: list[float],
        owner_id: str,
        n_results: int = 10,
    ) -> dict:
        """
        Perform semantic similarity search.

        Search is restricted to documents belonging
        to the authenticated user.
        """

        if not query_embedding:
            return {
                "ids": [[]],
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
            }

        available_chunks = self.count_owner_chunks(
            owner_id=owner_id,
        )

        if available_chunks == 0:
            return {
                "ids": [[]],
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]],
            }

        safe_n_results = min(
            n_results,
            available_chunks,
        )

        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=safe_n_results,
            where={
                "owner_id": owner_id,
            },
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

    def get_owner_chunks(
        self,
        owner_id: str,
    ) -> list[dict]:
        """
        Return all chunks belonging to one user.

        This method is used to build the user's BM25
        keyword-search index from existing ChromaDB data.
        """

        result = self.collection.get(
            where={
                "owner_id": owner_id,
            },
            include=[
                "documents",
                "metadatas",
            ],
        )

        ids = result.get("ids") or []
        documents = result.get("documents") or []
        metadatas = result.get("metadatas") or []

        chunks: list[dict] = []

        for chunk_id, document, metadata in zip(
            ids,
            documents,
            metadatas,
        ):
            metadata = metadata or {}

            chunks.append(
                {
                    "id": str(chunk_id),
                    "text": document or "",
                    "filename": metadata.get(
                        "filename",
                        "Unknown",
                    ),
                    "chunk_index": metadata.get(
                        "chunk_index",
                        -1,
                    ),
                    "document_id": metadata.get(
                        "document_id",
                    ),
                    "owner_id": metadata.get(
                        "owner_id",
                    ),
                }
            )

        return chunks

    def get_chunk(
        self,
        document_id: str,
        chunk_index: int,
        owner_id: str | None = None,
    ) -> dict | None:
        """
        Return one specific document chunk.

        This can be used by the source-preview endpoint.
        """

        conditions: list[dict] = [
            {
                "document_id": document_id,
            },
            {
                "chunk_index": chunk_index,
            },
        ]

        if owner_id:
            conditions.append(
                {
                    "owner_id": owner_id,
                }
            )

        result = self.collection.get(
            where={
                "$and": conditions,
            },
            include=[
                "documents",
                "metadatas",
            ],
        )

        ids = result.get("ids") or []
        documents = result.get("documents") or []
        metadatas = result.get("metadatas") or []

        if not ids or not documents:
            return None

        metadata = (
            metadatas[0]
            if metadatas
            else {}
        ) or {}

        return {
            "id": str(ids[0]),
            "text": documents[0] or "",
            "filename": metadata.get(
                "filename",
                "Unknown",
            ),
            "chunk_index": metadata.get(
                "chunk_index",
                chunk_index,
            ),
            "document_id": metadata.get(
                "document_id",
                document_id,
            ),
            "owner_id": metadata.get(
                "owner_id",
            ),
        }

    def count_owner_chunks(
        self,
        owner_id: str,
    ) -> int:
        """
        Return the number of chunks belonging to a user.
        """

        result = self.collection.get(
            where={
                "owner_id": owner_id,
            },
            include=[],
        )

        ids = result.get("ids") or []

        return len(ids)

    def delete_document(
        self,
        document_id: str,
        owner_id: str | None = None,
    ) -> None:
        """
        Delete every chunk belonging to one document.

        When owner_id is supplied, deletion is restricted
        to that user's document.
        """

        if owner_id:
            self.collection.delete(
                where={
                    "$and": [
                        {
                            "document_id": document_id,
                        },
                        {
                            "owner_id": owner_id,
                        },
                    ]
                }
            )

            return

        self.collection.delete(
            where={
                "document_id": document_id,
            }
        )
from app.repositories.vector_repository import VectorRepository


class SourceService:

    def __init__(self):
        self.repository = VectorRepository()

    def get_chunk(
        self,
        document_id: str,
        chunk_index: int,
    ):
        result = self.repository.get_chunk(
            document_id=document_id,
            chunk_index=chunk_index,
        )

        if result is None:
            return None

        return {
            "filename": result["metadata"]["filename"],
            "chunk_index": result["metadata"]["chunk_index"],
            "text": result["text"],
        }
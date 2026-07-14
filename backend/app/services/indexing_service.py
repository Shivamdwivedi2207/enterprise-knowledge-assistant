from pathlib import Path
from uuid import uuid4

from app.database.models.document import Document
from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService
from app.utils.pdf import PDFProcessor
from app.utils.text_splitter import TextSplitter


class IndexingService:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.text_splitter = TextSplitter()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreService()

    def index_document(self, document: Document) -> None:
        """
        Complete indexing pipeline:
        PDF -> Text -> Chunks -> Embeddings -> ChromaDB
        """

        pdf_path = Path("storage/uploads") / document.stored_filename

        # Extract text
        text = self.pdf_processor.extract_text(str(pdf_path))

        if not text.strip():
            raise ValueError("No text found in PDF.")

        # Split into chunks
        chunks = self.text_splitter.split(text)

        # Generate embeddings
        embeddings = self.embedding_service.embed_documents(chunks)

        ids = []
        metadatas = []

        for index, _ in enumerate(chunks):
            ids.append(str(uuid4()))

            metadatas.append(
                {
                    "document_id": str(document.id),
                    "owner_id": str(document.owner_id),
                    "chunk_index": index,
                    "filename": document.filename,
                }
            )

        # Store in ChromaDB
        self.vector_store.add_documents(
            ids=ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )
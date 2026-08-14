from pathlib import Path
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database.models.document import Document
from app.database.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.services.indexing_service import IndexingService
from app.services.vector_store_service import VectorStoreService


class DocumentService:
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    UPLOAD_DIRECTORY = Path("storage/uploads")

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = DocumentRepository(db)
        self.vector_store = VectorStoreService()

        self.UPLOAD_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

    async def upload_document(
        self,
        file: UploadFile,
        current_user: User,
    ) -> Document:
        """
        Validate, save and index an uploaded PDF.
        """

        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed.",
            )

        content = await file.read()

        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded PDF is empty.",
            )

        if len(content) > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 10 MB.",
            )

        original_filename = file.filename or "document.pdf"
        extension = Path(original_filename).suffix.lower()

        if extension != ".pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed.",
            )

        stored_filename = f"{uuid4()}{extension}"

        file_path = (
            self.UPLOAD_DIRECTORY
            / stored_filename
        )

        document: Document | None = None

        try:
            with file_path.open("wb") as buffer:
                buffer.write(content)

            document = Document(
                filename=original_filename,
                stored_filename=stored_filename,
                content_type=file.content_type,
                file_size=len(content),
                owner_id=current_user.id,
            )

            self.repository.add(document)
            self.repository.commit()
            self.repository.refresh(document)

            IndexingService().index_document(
                document
            )

            return document

        except HTTPException:
            self.db.rollback()

            if file_path.exists():
                file_path.unlink()

            raise

        except Exception as error:
            self.db.rollback()

            if document is not None:
                try:
                    self.vector_store.delete_document(
                        document_id=str(document.id),
                        owner_id=str(current_user.id),
                    )
                except Exception:
                    pass

            if file_path.exists():
                file_path.unlink()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "The document could not be uploaded "
                    "and indexed."
                ),
            ) from error

        finally:
            await file.close()

    def delete_document(
        self,
        document_id: UUID,
        current_user: User,
    ) -> None:
        """
        Delete the document from:

        1. ChromaDB
        2. Local file storage
        3. PostgreSQL
        """

        document = self.repository.get_by_id(
            document_id
        )

        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )

        if document.owner_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied.",
            )

        file_path = (
            self.UPLOAD_DIRECTORY
            / document.stored_filename
        )

        try:
            # Remove indexed chunks first.
            self.vector_store.delete_document(
                document_id=str(document.id),
                owner_id=str(current_user.id),
            )

            # Remove local PDF.
            if file_path.exists():
                file_path.unlink()

            # Remove PostgreSQL metadata.
            self.repository.delete(document)

        except HTTPException:
            raise

        except Exception as error:
            self.db.rollback()

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=(
                    "The document could not be deleted "
                    "completely."
                ),
            ) from error
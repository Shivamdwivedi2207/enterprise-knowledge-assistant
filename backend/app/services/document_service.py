from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database.models.document import Document
from app.database.models.user import User
from app.repositories.document_repository import DocumentRepository
from app.services.indexing_service import IndexingService

class DocumentService:
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    UPLOAD_DIRECTORY = Path("storage/uploads")

    def __init__(self, db: Session):
        self.repository = DocumentRepository(db)
        self.UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

    async def upload_document(
        self,
        file: UploadFile,
        current_user: User,
    ) -> Document:

        # Validate content type
        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are allowed.",
            )

        # Read file
        content = await file.read()

        # Validate size
        if len(content) > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 10 MB.",
            )

        # Generate unique filename
        extension = Path(file.filename).suffix
        stored_filename = f"{uuid4()}{extension}"

        # Save file
        file_path = self.UPLOAD_DIRECTORY / stored_filename

        with open(file_path, "wb") as buffer:
            buffer.write(content)

        # Save metadata
        document = Document(
            filename=file.filename,
            stored_filename=stored_filename,
            content_type=file.content_type,
            file_size=len(content),
            owner_id=current_user.id,
        )

        self.repository.add(document)
        self.repository.commit()
        self.repository.refresh(document)

        # Automatically index the document
        IndexingService().index_document(document)

        return document
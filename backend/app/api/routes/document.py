from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.models.user import User
from app.database.session import get_db
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.schemas.document_schema import DocumentResponse
from app.services.document_service import DocumentService


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DocumentService(db)

    return await service.upload_document(
        file=file,
        current_user=current_user,
    )


@router.get(
    "",
    response_model=list[DocumentResponse],
)
def get_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repository = DocumentRepository(db)

    return repository.get_by_owner(
        current_user.id
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_200_OK,
)
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = DocumentService(db)

    service.delete_document(
        document_id=document_id,
        current_user=current_user,
    )

    return {
        "message": (
            "Document and its indexed chunks "
            "were deleted successfully."
        )
    }
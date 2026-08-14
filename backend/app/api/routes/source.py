from fastapi import APIRouter, HTTPException

from app.schemas.source import SourcePreviewResponse
from app.services.source_service import SourceService

router = APIRouter(
    prefix="/sources",
    tags=["Sources"],
)

service = SourceService()


@router.get(
    "/{document_id}/{chunk_index}",
    response_model=SourcePreviewResponse,
)
def get_source_preview(
    document_id: str,
    chunk_index: int,
):
    result = service.get_chunk(
        document_id=document_id,
        chunk_index=chunk_index,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Chunk not found",
        )

    return SourcePreviewResponse(**result)
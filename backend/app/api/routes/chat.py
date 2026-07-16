from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.database.models.user import User
from app.database.session import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.graph_service import GraphService

router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)

service = GraphService()


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    result = service.ask(
        db=db,
        question=request.question,
        owner_id=str(current_user.id),
    )

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
    )

@router.post("/stream")
def stream_chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    generator = service.ask_stream(
        question=request.question,
        owner_id=str(current_user.id),
    )

    return StreamingResponse(
        generator,
        media_type="text/plain",
    )
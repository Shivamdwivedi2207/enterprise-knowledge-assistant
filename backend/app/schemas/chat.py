from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SourceResponse(BaseModel):
    filename: str
    chunk_index: int
    document_id: str


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]


class ChatHistoryResponse(BaseModel):
    id: UUID
    question: str
    answer: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
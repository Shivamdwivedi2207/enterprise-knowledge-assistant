from pydantic import BaseModel, Field


class SourceResponse(BaseModel):
    filename: str
    chunk_index: int


class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceResponse]
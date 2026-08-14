from pydantic import BaseModel


class SourcePreviewResponse(BaseModel):
    filename: str
    chunk_index: int
    text: str
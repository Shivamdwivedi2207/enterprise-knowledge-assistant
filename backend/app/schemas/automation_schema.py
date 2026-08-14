from typing import Any

from pydantic import BaseModel, Field


class AutomationRequest(BaseModel):
    """
    Data sent by the frontend to an n8n workflow.
    """

    action: str = Field(
        ...,
        min_length=1,
        max_length=100,
        examples=["test_workflow"],
    )

    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        examples=["Hello from FastAPI"],
    )

    data: dict[str, Any] = Field(
        default_factory=dict,
    )


class AutomationResponse(BaseModel):
    """
    Response returned after the n8n workflow executes.
    """

    success: bool
    message: str
    workflow_response: dict[str, Any] | list[Any] | str | None
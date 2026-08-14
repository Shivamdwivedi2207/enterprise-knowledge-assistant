from pydantic import BaseModel, Field

from app.schemas.agent_schema import AgentDecision


class AgentPlan(BaseModel):
    """
    Represents one or more actions that should be executed
    for a single user request.

    Existing AgentDecision remains unchanged and is reused
    for each individual action.
    """

    actions: list[AgentDecision] = Field(
        default_factory=list,
        description=(
            "Ordered list of actions required to satisfy "
            "the user's request."
        ),
    )

    reasoning_summary: str = Field(
        default="",
        description=(
            "Short explanation of why these actions "
            "were selected. This is for logging only."
        ),
    )
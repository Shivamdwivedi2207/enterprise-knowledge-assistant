from typing import Any, TypedDict


class GraphState(TypedDict):
    question: str
    owner_id: str
    history: str
    context: str
    answer: str
    sources: list[dict[str, Any]]
from typing import TypedDict


class GraphState(TypedDict):
    question: str
    owner_id: str
    context: str
    answer: str
from sqlalchemy.orm import Session

from app.graph.graph import graph
from app.repositories.chat_history_repository import ChatHistoryRepository


class GraphService:

    def __init__(self):
        self.repository = ChatHistoryRepository()

    def ask(
        self,
        db: Session,
        question: str,
        owner_id: str,
    ) -> str:

        state = {
        "question": question,
        "owner_id": owner_id,
        "history": "",
        "context": "",
        "answer": "",
        "sources": [],
    }

        result = graph.invoke(state)

        answer = result["answer"]

        sources = result["sources"]

        self.repository.create(
            db=db,
            owner_id=owner_id,
            question=question,
            answer=answer,
        )

        return {
            "answer": answer,
            "sources": sources,
        }
    
    def ask_stream(
        self,
        question: str,
        owner_id: str,
    ):
        """
        Stream the answer token by token.
        """

        state = {
            "question": question,
            "owner_id": owner_id,
            "history": "",
            "context": "",
            "answer": "",
            "sources": [],
        }

        result = graph.invoke(state)

        answer = result["answer"]

        for word in answer.split():
            yield word + " "
from uuid import UUID

from sqlalchemy.orm import Session

from app.database.models.chat_history import ChatHistory


class ChatHistoryRepository:

    def create(
        self,
        db: Session,
        owner_id: str,
        question: str,
        answer: str,
    ) -> ChatHistory:
        chat = ChatHistory(
            owner_id=UUID(str(owner_id)),
            question=question,
            answer=answer,
        )

        db.add(chat)
        db.commit()
        db.refresh(chat)

        return chat

    def get_history(
        self,
        db: Session,
        owner_id: str,
        limit: int = 10,
    ) -> list[ChatHistory]:
        """
        Return the user's most recent chat records.

        Results are returned newest first. The history node
        reverses them before building the conversation text.
        """

        return (
            db.query(ChatHistory)
            .filter(
                ChatHistory.owner_id
                == UUID(str(owner_id))
            )
            .order_by(
                ChatHistory.created_at.desc()
            )
            .limit(limit)
            .all()
        )
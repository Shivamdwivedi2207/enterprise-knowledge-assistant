from sqlalchemy.orm import Session

from app.database.models.chat_session import ChatSession


class ChatSessionRepository:

    def create(
        self,
        db: Session,
        owner_id: str,
        title: str = "New Chat",
    ):
        session = ChatSession(
            owner_id=owner_id,
            title=title,
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return session

    def get_all(
        self,
        db: Session,
        owner_id: str,
    ):
        return (
            db.query(ChatSession)
            .filter(ChatSession.owner_id == owner_id)
            .order_by(ChatSession.updated_at.desc())
            .all()
        )

    def get_by_id(
        self,
        db: Session,
        session_id: str,
    ):
        return (
            db.query(ChatSession)
            .filter(ChatSession.id == session_id)
            .first()
        )

    def delete(
        self,
        db: Session,
        session: ChatSession,
    ):
        db.delete(session)
        db.commit()
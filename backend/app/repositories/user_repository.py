from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: UUID) -> User | None:
        return self.db.scalar(
            select(User).where(User.id == user_id)
        )

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(
            select(User).where(User.email == email)
        )

    def add(self, user: User) -> None:
        self.db.add(user)

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, user: User) -> None:
        self.db.refresh(user)
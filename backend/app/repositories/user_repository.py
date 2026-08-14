from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models.user import User


class UserRepository:
    def __init__(
        self,
        db: Session,
    ):
        self.db = db

    # =====================================================
    # Get User by ID
    # =====================================================

    def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:
        return self.db.scalar(
            select(User).where(
                User.id == user_id
            )
        )

    # =====================================================
    # Get User by Email
    # =====================================================

    def get_by_email(
        self,
        email: str,
    ) -> User | None:
        return self.db.scalar(
            select(User).where(
                User.email == email
            )
        )

    # =====================================================
    # List Employees
    # =====================================================

    def get_employees(
        self,
    ) -> list[User]:
        """
        Return normal employee accounts only.

        Superusers/admins are excluded from the
        employee-management list.
        """

        result = self.db.scalars(
            select(User)
            .where(
                User.is_superuser.is_(False)
            )
            .order_by(
                User.created_at.desc()
            )
        )

        return list(
            result.all()
        )

    # =====================================================
    # Add User
    # =====================================================

    def add(
        self,
        user: User,
    ) -> None:
        self.db.add(
            user
        )

    # =====================================================
    # Commit
    # =====================================================

    def commit(
        self,
    ) -> None:
        self.db.commit()

    # =====================================================
    # Refresh
    # =====================================================

    def refresh(
        self,
        user: User,
    ) -> None:
        self.db.refresh(
            user
        )
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.database.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import UserRegister


class AuthService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def register(self, user_data: UserRegister) -> User:
        existing_user = self.repository.get_by_email(user_data.email)

        if existing_user:
            raise ValueError("Email already registered")

        user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
        )

        self.repository.add(user)
        self.repository.commit()
        self.repository.refresh(user)

        return user

    def login(self, email: str, password: str) -> str:
        user = self.repository.get_by_email(email)

        if user is None:
            raise ValueError("Invalid email or password")

        if not verify_password(password, user.hashed_password):
            raise ValueError("Invalid email or password")

        return create_access_token(str(user.id))
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.database.models.user import User
from app.schemas.auth_schema import (
    TokenResponse,
    UserLogin,
    UserRegister,
)


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, user_data: UserRegister) -> User:
        existing_user = self.db.scalar(
            select(User).where(User.email == user_data.email)
        )

        if existing_user:
            raise ValueError("Email already registered")

        user = User(
            full_name=user_data.full_name,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def login(self, login_data: UserLogin) -> TokenResponse:
        user = self.db.scalar(
            select(User).where(User.email == login_data.email)
        )

        if not user:
            raise ValueError("Invalid email or password")

        if not verify_password(
            login_data.password,
            user.hashed_password,
        ):
            raise ValueError("Invalid email or password")

        token = create_access_token(str(user.id))

        return TokenResponse(
            access_token=token,
        )
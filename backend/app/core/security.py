from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.models.user import User
from app.database.session import get_db
from app.repositories.user_repository import UserRepository


password_hash = PasswordHash.recommended()


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/swagger-login"
)


# =========================================================
# JWT
# =========================================================

def decode_access_token(
    token: str,
) -> str:
    """
    Decode JWT and return the authenticated user's ID.
    """

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[
                settings.ALGORITHM,
            ],
        )

        subject = payload.get(
            "sub"
        )

        if subject is None:
            raise HTTPException(
                status_code=(
                    status.HTTP_401_UNAUTHORIZED
                ),
                detail="Invalid token",
                headers={
                    "WWW-Authenticate": "Bearer",
                },
            )

        return str(
            subject
        )

    except JWTError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=(
                "Invalid or expired token"
            ),
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from error


# =========================================================
# Current User
# =========================================================

def get_current_user(
    token: str = Depends(
        oauth2_scheme
    ),
    db: Session = Depends(
        get_db
    ),
) -> User:
    """
    Return the currently authenticated active user.
    """

    user_id = decode_access_token(
        token
    )

    repository = UserRepository(
        db
    )

    user = repository.get_by_id(
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail="User not found",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    if not user.is_active:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "This user account is inactive."
            ),
        )

    return user


# =========================================================
# Admin / Superuser
# =========================================================

def get_current_admin(
    current_user: User = Depends(
        get_current_user
    ),
) -> User:
    """
    Allow access only to enterprise administrators.

    In this project:
        is_superuser = True  -> Admin
        is_superuser = False -> Employee
    """

    if not current_user.is_superuser:
        raise HTTPException(
            status_code=(
                status.HTTP_403_FORBIDDEN
            ),
            detail=(
                "Administrator access required."
            ),
        )

    return current_user


# =========================================================
# Password Utilities
# =========================================================

def hash_password(
    password: str,
) -> str:
    return password_hash.hash(
        password
    )


def verify_password(
    password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        password,
        hashed_password,
    )


# =========================================================
# Access Token
# =========================================================

def create_access_token(
    subject: str,
) -> str:
    expire = (
        datetime.now(
            timezone.utc
        )
        + timedelta(
            minutes=(
                settings
                .ACCESS_TOKEN_EXPIRE_MINUTES
            )
        )
    )

    payload = {
        "sub": subject,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=(
            settings.ALGORITHM
        ),
    )
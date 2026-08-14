from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.auth_schema import (
    TokenResponse,
    UserLogin,
)
from app.services.auth_service import AuthService


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# =========================================================
# Login — React Frontend
# =========================================================

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request: UserLogin,
    db: Session = Depends(get_db),
):
    """
    JSON login endpoint used by the React frontend.

    Public registration is intentionally disabled.
    Employee accounts are created by administrators.
    """

    service = AuthService(db)

    try:
        access_token = service.login(
            email=request.email,
            password=request.password,
        )

        return TokenResponse(
            access_token=access_token,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=str(error),
        ) from error


# =========================================================
# Login — Swagger OAuth2
# =========================================================

@router.post(
    "/swagger-login",
    response_model=TokenResponse,
)
def swagger_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Form-data login endpoint used by Swagger OAuth2.

    Enter the user's email address in the
    Swagger username field.
    """

    service = AuthService(db)

    try:
        access_token = service.login(
            email=form_data.username,
            password=form_data.password,
        )

        return TokenResponse(
            access_token=access_token,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_401_UNAUTHORIZED
            ),
            detail=str(error),
            headers={
                "WWW-Authenticate": "Bearer",
            },
        ) from error
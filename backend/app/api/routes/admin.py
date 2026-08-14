from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.core.security import (
    get_current_admin,
)
from app.database.models.user import User
from app.database.session import get_db
from app.repositories.user_repository import (
    UserRepository,
)
from app.schemas.auth_schema import (
    EmployeeCreate,
    EmployeeStatusUpdate,
    UserResponse,
)
from app.services.auth_service import (
    AuthService,
)


router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
)


# =========================================================
# Create Employee
# =========================================================

@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(
        get_db
    ),
    current_admin: User = Depends(
        get_current_admin
    ),
) -> User:
    """
    Create a new enterprise employee account.

    Only administrators can access this endpoint.
    """

    service = AuthService(
        db
    )

    try:
        return service.create_employee(
            employee
        )

    except ValueError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=str(error),
        ) from error


# =========================================================
# List Employees
# =========================================================

@router.get(
    "/users",
    response_model=list[UserResponse],
)
def list_employees(
    db: Session = Depends(
        get_db
    ),
    current_admin: User = Depends(
        get_current_admin
    ),
) -> list[User]:
    """
    Return all normal employee accounts.

    Admin accounts are intentionally excluded.
    """

    repository = UserRepository(
        db
    )

    return repository.get_employees()


# =========================================================
# Activate / Deactivate Employee
# =========================================================

@router.patch(
    "/users/{user_id}/status",
    response_model=UserResponse,
)
def update_employee_status(
    user_id: UUID,
    request: EmployeeStatusUpdate,
    db: Session = Depends(
        get_db
    ),
    current_admin: User = Depends(
        get_current_admin
    ),
) -> User:
    """
    Activate or deactivate an employee account.

    Deactivation is preferred over permanent deletion
    because the employee may own documents or chat history.
    """

    repository = UserRepository(
        db
    )

    user = repository.get_by_id(
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=(
                status.HTTP_404_NOT_FOUND
            ),
            detail="Employee not found.",
        )

    if user.is_superuser:
        raise HTTPException(
            status_code=(
                status.HTTP_400_BAD_REQUEST
            ),
            detail=(
                "Admin accounts cannot be modified "
                "through the employee endpoint."
            ),
        )

    user.is_active = (
        request.is_active
    )

    repository.commit()

    repository.refresh(
        user
    )

    return user
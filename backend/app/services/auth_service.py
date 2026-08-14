from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.database.models.user import User
from app.repositories.user_repository import (
    UserRepository,
)
from app.schemas.auth_schema import (
    EmployeeCreate,
    UserRegister,
)


class AuthService:
    def __init__(
        self,
        db: Session,
    ) -> None:
        self.repository = UserRepository(
            db
        )

    # =====================================================
    # Internal user creation helper
    # =====================================================

    def _create_user(
        self,
        full_name: str,
        email: str,
        password: str,
        *,
        is_superuser: bool = False,
    ) -> User:
        """
        Create a user account.

        This internal method is shared by public development
        registration and admin employee provisioning.
        """

        existing_user = (
            self.repository.get_by_email(
                email
            )
        )

        if existing_user:
            raise ValueError(
                "Email already registered"
            )

        user = User(
            full_name=full_name,
            email=email,
            hashed_password=(
                hash_password(
                    password
                )
            ),
            is_active=True,
            is_verified=False,
            is_superuser=(
                is_superuser
            ),
        )

        self.repository.add(
            user
        )

        self.repository.commit()

        self.repository.refresh(
            user
        )

        return user

    # =====================================================
    # Existing registration
    # =====================================================

    def register(
        self,
        user_data: UserRegister,
    ) -> User:
        """
        Temporary development registration.

        This will later be removed from public access after
        administrator employee provisioning is verified.
        """

        return self._create_user(
            full_name=(
                user_data.full_name
            ),
            email=str(
                user_data.email
            ),
            password=(
                user_data.password
            ),
            is_superuser=False,
        )

    # =====================================================
    # Admin creates employee
    # =====================================================

    def create_employee(
        self,
        employee_data: EmployeeCreate,
    ) -> User:
        """
        Create a normal enterprise employee account.

        This method must only be called from an endpoint
        protected by get_current_admin().
        """

        return self._create_user(
            full_name=(
                employee_data.full_name
            ),
            email=str(
                employee_data.email
            ),
            password=(
                employee_data.password
            ),
            is_superuser=False,
        )

    # =====================================================
    # Login
    # =====================================================

    def login(
        self,
        email: str,
        password: str,
    ) -> str:
        user = (
            self.repository.get_by_email(
                email
            )
        )

        if user is None:
            raise ValueError(
                "Invalid email or password"
            )

        if not verify_password(
            password,
            user.hashed_password,
        ):
            raise ValueError(
                "Invalid email or password"
            )

        if not user.is_active:
            raise ValueError(
                "This account is inactive"
            )

        return create_access_token(
            str(user.id)
        )
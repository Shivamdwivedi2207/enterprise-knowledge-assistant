from __future__ import annotations

import uuid

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


# =========================================================
# Registration / Employee Creation
# =========================================================

class UserRegister(BaseModel):
    """
    Temporary development registration schema.

    This can remain available until public registration
    is disabled after the admin flow is fully tested.
    """

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )


class EmployeeCreate(BaseModel):
    """
    Request used by an administrator to create
    a new employee account.
    """

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )


class EmployeeStatusUpdate(BaseModel):
    """
    Request used by an administrator to activate
    or deactivate an employee account.
    """

    is_active: bool


# =========================================================
# Login
# =========================================================

class UserLogin(BaseModel):
    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
    )


# =========================================================
# User Response
# =========================================================

class UserResponse(BaseModel):
    id: uuid.UUID

    full_name: str

    email: EmailStr

    is_active: bool

    is_verified: bool

    is_superuser: bool

    model_config = ConfigDict(
        from_attributes=True
    )


# =========================================================
# Token
# =========================================================

class TokenResponse(BaseModel):
    access_token: str

    token_type: str = "bearer"
from datetime import timedelta
from typing import Any

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.core import security
from app.core.config import settings
from app.models.user import UserCreate, UserPublic, UserRegister
from app.schemas.auth import LoginPayload, LoginResponse, RefreshResponse

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(session: SessionDep, payload: LoginPayload) -> Any:
    user = crud.authenticate(session=session, username=payload.username, password=payload.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return LoginResponse(
        access_token=security.create_access_token(user.id, expires_delta=access_token_expires),
        token_type="Bearer",
    )


@router.post("/logout", dependencies=[CurrentUser])
def logout() -> Any:
    """jwt token doesn't need to be invalidated"""
    pass


@router.get("/codes", response_model=list[str], dependencies=[CurrentUser])
def get_codes() -> Any:
    """access codes is not necessary."""
    return []


@router.post("/refresh", response_model=RefreshResponse)
def refresh(current_user: CurrentUser) -> Any:
    """
    vben need to set ' enableRefreshToken: true' in preferences.ts of your app.
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return RefreshResponse(data=security.create_access_token(current_user.id, expires_delta=access_token_expires))


@router.post("/register", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    Create new user without the need to be logged in.
    """
    user = crud.get_user_by_username_or_email(session=session, username=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email or username already exists in the system",
        )
    user_create = UserCreate.model_validate(user_in)
    user = crud.create_user(session=session, user_create=user_create)
    return user

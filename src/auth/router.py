from typing import Annotated

from fastapi import APIRouter, Depends, Response
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.exceptions import UserIsNotActive, WrongCredentials
from src.auth.schema import LoginSchema, TokenInfo
from src.auth.services import AuthService
from src.auth.utils import (
    create_access_token,
    create_refresh_token,
    get_current_active_profile,
    get_current_profile_by_refresh,
    validate_password,
)
from src.core.exceptions import NotFoundException
from src.database import get_db
from src.profile.models import Profile
from src.profile.schemas import ProfileSchema

http_bearer = HTTPBearer(auto_error=False)
router = APIRouter(dependencies=[Depends(http_bearer)])


@router.post("/login", response_model=TokenInfo)
async def auth_user_issue_jwt(
        login: LoginSchema,
        response: Response,
        db: Annotated[AsyncSession, Depends(get_db)],
):
    auth_service: AuthService = AuthService(db)
    profile: Profile = await auth_service.get_by_login(login.login)
    if not profile:
        raise NotFoundException("Profile not found")

    if not validate_password(
        password=login.password,
        hashed_password=profile.password,
    ):
        raise WrongCredentials()

    if not profile.is_active:
        raise UserIsNotActive()

    access_token = await create_access_token(profile)
    refresh_token = await create_refresh_token(profile)

    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenInfo)
async def refresh_token(
    profile: Profile = Depends(get_current_profile_by_refresh),
):
    access_token = await create_access_token(profile)
    refresh_token = await create_refresh_token(profile)
    return TokenInfo(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get("/profile/me/")
async def auth_user_check_self_info(
    profile: ProfileSchema = Depends(get_current_active_profile),
):
    return {
        "login": profile.login,
        "email": profile.email,
    }
